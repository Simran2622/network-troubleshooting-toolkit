"""Core network diagnostic functions."""
import platform
import socket
import subprocess
import time


def dns_lookup(hostname):
    target = hostname.strip()
    if not target:
        return result("DNS", hostname, "FAIL", "", "Hostname cannot be empty.")
    started = time.perf_counter()
    try:
        records = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
        ips = sorted({item[4][0] for item in records})
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        return result("DNS", target, "PASS", elapsed, "Resolved to: " + ", ".join(ips), ", ".join(ips))
    except (socket.gaierror, OSError) as exc:
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        return result("DNS", target, "FAIL", elapsed, f"DNS resolution failed: {exc}")


def tcp_port_check(hostname, port, timeout=3.0):
    target = hostname.strip()
    if not target:
        return result("TCP", f"{hostname}:{port}", "FAIL", "", "Hostname cannot be empty.")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        return result("TCP", f"{target}:{port}", "FAIL", "", "Port must be an integer from 1 to 65535.")
    started = time.perf_counter()
    try:
        with socket.create_connection((target, port), timeout=timeout) as conn:
            remote_ip = conn.getpeername()[0]
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        return result("TCP", f"{target}:{port}", "PASS", elapsed,
                      f"TCP connection successful (timeout {timeout:g}s).", remote_ip)
    except (socket.gaierror, socket.timeout, TimeoutError, OSError) as exc:
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        return result("TCP", f"{target}:{port}", "FAIL", elapsed, f"TCP connection failed: {exc}")


def ping_check(hostname, count=2, timeout_seconds=4):
    target = hostname.strip()
    if not target:
        return result("PING", hostname, "FAIL", "", "Hostname or IP cannot be empty.")
    if platform.system().lower() == "windows":
        command = ["ping", "-n", str(count), "-w", str(timeout_seconds * 1000), target]
    else:
        command = ["ping", "-c", str(count), "-W", str(timeout_seconds), target]
    started = time.perf_counter()
    try:
        proc = subprocess.run(command, capture_output=True, text=True,
                              timeout=count * timeout_seconds + 3, check=False)
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        output = (proc.stdout + "\n" + proc.stderr).strip()
        details = output.splitlines()[-1][:240] if output else "No output from ping command."
        return result("PING", target, "PASS" if proc.returncode == 0 else "FAIL",
                      elapsed, details)
    except FileNotFoundError:
        return result("PING", target, "FAIL", "", "ping command not found; DNS/TCP checks can still be used.")
    except subprocess.TimeoutExpired:
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        return result("PING", target, "FAIL", elapsed, "Ping command timed out.")


def result(check_type, target, status, response_time_ms, details, resolved_ip=""):
    return {"check_type": check_type, "target": target, "status": status,
            "response_time_ms": response_time_ms, "details": details, "resolved_ip": resolved_ip}
