# LANScanner

[![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](#)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](#)
[![macOS](https://img.shields.io/badge/macOS-000000?style=flat-square&logo=apple&logoColor=white)](#)
[![Zero Dependencies](https://img.shields.io/badge/依赖-零-brightgreen?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

零依赖的本地网络扫描器，发现局域网内的活跃设备并显示其 IP 与 MAC 地址。

## 功能

- **自动检测**本机 IP 与子网，无需配置
- **并发 Ping 扫描** — 50 线程池数秒完成 /24 网段扫描
- **ARP 解析** — IP-MAC 映射，自动过滤无效条目
- **跨平台** — Windows（主要支持）、Linux、macOS
- **零依赖** — 仅使用 Python 标准库

## 快速开始

```bash
python scanner.py
```

无需安装、无需配置、无第三方包。

## 输出示例

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

## 工作原理

```
1. 网络检测
   UDP connect → 本机 IP
   netsh / ip route → 子网前缀
        │
2. Ping Sweep（并发）
   50 线程并发 ICMP Ping 所有目标主机
   存活主机触发系统 ARP 表更新
        │
3. ARP 表读取 + 过滤
   解析 arp -a 输出
   过滤：多播、广播、重复 IP、保留地址
        │
4. 输出
   合并存活 IP 与 ARP 数据
   按 IP 排序，标记本机
```

### 扫描范围

| 子网大小 | 行为 |
|----------|------|
| /24 及更小 | 扫描全部主机 |
| /16、/8 等大子网 | 仅扫描本机所在 /24 段（254 台主机） |

大子网全扫描耗时过长，自动缩减范围以保证可用性。

## 运行环境

| 项目 | 要求 |
|------|------|
| Python | >= 3.6 |
| 操作系统 | Windows（主要支持）、Linux、macOS |
| 依赖 | 仅标准库，无第三方包 |
| 权限 | 需能执行 `ping` 和 `arp` 命令 |

## 已知限制

| 限制 | 原因 | 影响 |
|------|------|------|
| 部分主机 Ping 不响应 | 防火墙/系统策略禁止 ICMP | 这些设备不会出现在结果中 |
| MAC 显示 (unknown) | ARP 表中尚无该 IP 条目 | 刚发现的设备可能缺少 MAC |
| VPN / 多接口环境 | UDP connect 选择主出口接口 | 可能扫描 VPN 子网而非物理 LAN |
| 大子网截断 | /16+ 仅扫描 /24 段 | 同网段外的设备不会被发现 |

## License

MIT
