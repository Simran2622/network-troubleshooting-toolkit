"""Interactive CLI for the Network Troubleshooting Toolkit."""
import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnostics import dns_lookup, ping_check, tcp_port_check  # noqa: E402

REPORT_DIR = ROOT / "reports"
FIELDS = ["timestamp", "check_type", "target", "status", "response_time_ms", "details", "resolved_ip"]


def save_report(results):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"network_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for item in results:
            writer.writerow({"timestamp": timestamp, **item})
    return path


def display_and_save(results):
    for item in results:
        print(f"\n[{item['status']}] {item['check_type']} — {item['target']}")
        if item["response_time_ms"] != "":
            print(f"  Response time: {item['response_time_ms']} ms")
        print(f"  Details: {item['details']}")
        if item["resolved_ip"]:
            print(f"  IP: {item['resolved_ip']}")
    report = save_report(results)
    passed = sum(item["status"] == "PASS" for item in results)
    print(f"\nSummary: {len(results)} checks | {passed} passed | {len(results)-passed} failed")
    print(f"CSV report saved to: {report.relative_to(ROOT)}")


def ask_port():
    while True:
        raw = input("TCP port (1-65535, default 443): ").strip()
        if not raw:
            return 443
        try:
            port = int(raw)
            if 1 <= port <= 65535:
                return port
        except ValueError:
            pass
        print("Enter a whole number from 1 to 65535.")


def main():
    print("=" * 46 + "\n   NETWORK TROUBLESHOOTING TOOLKIT\n" + "=" * 46)
    while True:
        print("\n1. DNS lookup\n2. TCP port connectivity check\n3. Ping test\n4. Run all checks\n5. Exit")
        choice = input("\nChoose an option (1-5): ").strip()
        if choice == "1":
            display_and_save([dns_lookup(input("Hostname (e.g. example.com): ").strip())])
        elif choice == "2":
            host = input("Hostname or IP address: ").strip()
            display_and_save([tcp_port_check(host, ask_port())])
        elif choice == "3":
            display_and_save([ping_check(input("Hostname or IP address: ").strip())])
        elif choice == "4":
            host = input("Hostname (e.g. example.com): ").strip()
            port = ask_port()
            display_and_save([dns_lookup(host), tcp_port_check(host, port), ping_check(host)])
        elif choice == "5":
            print("Goodbye! Troubleshoot responsibly.")
            break
        else:
            print("Invalid choice. Choose 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting safely.")
