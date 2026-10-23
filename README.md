# Network Troubleshooting Toolkit

A beginner-friendly terminal-based Python tool for basic network diagnostics: DNS lookup, one specified TCP port check, ping, response timing, and CSV reports.

## Requirements
- Python 3.10+ (Python 3.11 recommended)
- Linux/Ubuntu/WSL2, macOS, or Windows
- No third-party packages required

## Run on Ubuntu / WSL2
From the extracted project folder:
```bash
python3 --version
python3 src/main.py
```

## Run on Windows
Open PowerShell in the project folder:
```powershell
py --version
py src/main.py
```

## Menu
1. DNS lookup for a hostname such as `example.com`
2. TCP connection check for one hostname/IP and one port, e.g. `example.com` and `443`
3. Ping test
4. Run all checks and save the results
5. Exit

CSV reports are written to `reports/`. They include timestamp, check type, target, status, response time in milliseconds, details, and resolved IP.

## Project structure
```text
network-troubleshooting-toolkit/
├── src/main.py
├── src/diagnostics.py
├── tests/test_diagnostics.py
├── reports/.gitkeep
├── requirements.txt
├── .gitignore
└── README.md
```

## Concepts demonstrated
Python modules, exceptions, DNS resolution (`socket.getaddrinfo`), TCP connections (`socket.create_connection`), response timing (`time.perf_counter`), safe subprocess execution, CSV writing, and unit tests.

## Limitations and responsible use
A failed connection does not necessarily mean a server is down; a firewall, DNS issue, or network restriction may block it. Ping can be blocked even when TCP works. This is a basic diagnostic tool, not continuous monitoring or a full security scanner. Only test systems and ports you own or are authorized to troubleshoot.
