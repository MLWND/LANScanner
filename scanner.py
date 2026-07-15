#!/usr/bin/env python3
"""Local network scanner — discover devices on your subnet via ping + ARP."""

import subprocess
import re
import sys
import ipaddress
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_local_network():
    """Return (network_obj, local_ip) for the primary LAN interface."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()

    # Get subnet from interface listing (Windows)
    if platform.system() == "Windows":
        raw = subprocess.check_output(
            ["netsh", "interface", "ip", "show", "config"]
        )
        output = raw.decode("gbk", errors="replace")
        for line in output.splitlines():
            if "Subnet Prefix" in line or "子网前缀" in line:
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)/(\d+)", line)
                if match:
                    network = ipaddress.ip_network(
                        f"{match.group(1)}/{match.group(2)}", strict=False
                    )
                    if local_ip in network:
                        return network, local_ip
    # Fallback: assume /24
    return ipaddress.ip_network(f"{local_ip}/24", strict=False), local_ip


def get_scan_range(network, local_ip):
    """Return iterable of IPs to scan.

    For large networks (/16, /8), only scan the local /24 segment + gateway
    to keep runtime reasonable.
    """
    if network.prefixlen >= 24:
        return network.hosts()

    # For wider networks, scan only the /24 containing local_ip
    local_segment = ipaddress.ip_network(f"{local_ip}/24", strict=False)
    return local_segment.hosts()


# Cached once at import — ping_host is called hundreds of times per scan
_IS_WINDOWS = platform.system() == "Windows"
_PING_FLAGS = ["-n", "1", "-w", "500"] if _IS_WINDOWS else ["-c", "1", "-W", "1"]


def ping_host(ip_str):
    """Ping a single host. Return ip_str if alive, None otherwise."""
    try:
        result = subprocess.run(
            ["ping"] + _PING_FLAGS + [ip_str],
            capture_output=True, timeout=3,
        )
        if result.returncode == 0:
            return ip_str
    except subprocess.TimeoutExpired:
        pass
    return None


def ping_sweep(ips):
    """Concurrently ping hosts, return set of alive IPs."""
    alive = set()
    with ThreadPoolExecutor(max_workers=50) as pool:
        futures = [pool.submit(ping_host, str(ip)) for ip in ips]
        for future in as_completed(futures):
            result = future.result()
            if result:
                alive.add(result)
    return alive


def get_arp_table():
    """Parse arp -a, return dict of {ip: mac} for real devices only."""
    output = subprocess.check_output(["arp", "-a"], text=True)
    seen = {}
    for line in output.splitlines():
        match = re.search(
            r"(\d+\.\d+\.\d+\.\d+).*?((?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})", line
        )
        if not match:
            continue
        ip = match.group(1)
        mac = match.group(2).replace("-", ":").upper()

        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_multicast or ip_obj.is_reserved:
                continue
        except ValueError:
            continue

        if mac == "FF:FF:FF:FF:FF:FF":
            continue

        if ip not in seen:
            seen[ip] = mac
    return seen


def main():
    network, local_ip = get_local_network()
    scan_ips = list(get_scan_range(network, local_ip))
    host_count = len(scan_ips)

    print(f"Local IP: {local_ip}")
    print(f"Network: {network}")
    print(f"Scanning {host_count} hosts...")

    alive_ips = ping_sweep(scan_ips)
    arp = get_arp_table()

    devices = {}
    for ip in alive_ips:
        devices[ip] = arp.get(ip, "(unknown)")

    # Mark local machine
    if local_ip in devices and devices[local_ip] == "(unknown)":
        devices[local_ip] = "(this machine)"

    if not devices:
        print("No devices found.")
        sys.exit(0)

    sorted_devices = sorted(
        devices.items(), key=lambda x: ipaddress.ip_address(x[0])
    )

    print(f"\n{len(sorted_devices)} device(s) found:\n")
    print(f"{'IP Address':<20} {'MAC Address':<20}")
    print("-" * 40)
    for ip, mac in sorted_devices:
        print(f"{ip:<20} {mac:<20}")


if __name__ == "__main__":
    main()