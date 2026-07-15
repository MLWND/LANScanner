# LANScanner

[![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](#)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](#)
[![macOS](https://img.shields.io/badge/macOS-000000?style=flat-square&logo=apple&logoColor=white)](#)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

A zero-dependency local network scanner that discovers active devices on your LAN, displaying their IP and MAC addresses.

## Features

- **Auto-detect** local IP and subnet — no configuration needed
- **Concurrent ping sweep** — 50-thread pool scans a /24 in seconds
- **ARP resolution** — maps IPs to MAC addresses with filtering
- **Cross-platform** — Windows (primary), Linux, and macOS
- **Zero dependencies** — Python standard library only

## Quick Start

```bash
python scanner.py
```

That's it. No install, no config, no third-party packages.

## Example Output

```
Local IP: 10.228.92.71
Network: 10.228.92.0/24
Scanning 254 hosts...

8 device(s) found:

IP Address           MAC Address
----------------------------------------
10.228.92.21         54:16:51:56:8D:89
10.228.92.71         (this machine)
10.228.92.153        54:16:51:56:8D:89
```

## How It Works

```
1. Network Detection
   UDP connect → local IP
   netsh / ip route → subnet prefix
        │
2. Ping Sweep (concurrent)
   50 threads ICMP-ping all hosts
   Alive hosts populate OS ARP cache
        │
3. ARP Table Read + Filter
   Parse arp -a output
   Filter: multicast, broadcast, duplicate, reserved
        │
4. Output
   Merge alive IPs with ARP data
   Sort by IP, mark local machine
```

### Scan Scope

| Subnet Size | Behavior |
|-------------|----------|
| /24 or smaller | Scan all hosts |
| /16, /8 (large) | Scan only the local /24 segment (254 hosts) |

Large subnets are scoped down to keep runtime reasonable.

## Requirements

| Item | Detail |
|------|--------|
| Python | >= 3.6 |
| Platform | Windows (primary), Linux, macOS |
| Dependencies | None (stdlib only) |
| Permissions | Ability to run `ping` and `arp` commands |

## Known Limitations

| Limitation | Cause | Impact |
|------------|-------|--------|
| Some hosts don't respond | Firewall / OS blocks ICMP | These devices won't appear |
| MAC shows "(unknown)" | ARP cache not yet populated | Recently discovered devices may lack MAC |
| VPN / multi-interface | UDP connect picks primary route | May scan VPN subnet instead of physical LAN |
| Large subnet truncation | /16+ scans limited to /24 | Devices outside local segment won't be found |

## License

MIT
