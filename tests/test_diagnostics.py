"""Tests for network diagnostic functions."""
import socket
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from diagnostics import dns_lookup, ping_check, tcp_port_check  # noqa: E402


class DiagnosticsTests(unittest.TestCase):
    def test_empty_hostname_fails(self):
        self.assertEqual(dns_lookup(" ")["status"], "FAIL")
        self.assertEqual(tcp_port_check("", 443)["status"], "FAIL")
        self.assertEqual(ping_check(" ")["status"], "FAIL")

    def test_invalid_ports_fail(self):
        for port in (0, 65536, "443", None):
            with self.subTest(port=port):
                self.assertEqual(tcp_port_check("localhost", port)["status"], "FAIL")

    @patch(
        "diagnostics.socket.getaddrinfo",
        return_value=[(2, 1, 6, "", ("192.0.2.1", 0))],
    )
    def test_dns_success(self, _mock):
        result = dns_lookup("example.test")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("192.0.2.1", result["resolved_ip"])
        self.assertIsInstance(result["response_time_ms"], (int, float))

    @patch("diagnostics.socket.getaddrinfo", side_effect=socket.gaierror("not found"))
    def test_dns_failure(self, _mock):
        result = dns_lookup("missing.invalid")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("DNS resolution failed", result["details"])

    @patch("diagnostics.socket.create_connection")
    def test_tcp_success(self, mock_connect):
        connection = MagicMock()
        connection.getpeername.return_value = ("192.0.2.10", 443)
        mock_connect.return_value.__enter__.return_value = connection

        result = tcp_port_check("example.test", 443)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["resolved_ip"], "192.0.2.10")
        mock_connect.assert_called_once()

    @patch("diagnostics.socket.create_connection", side_effect=ConnectionRefusedError("refused"))
    def test_tcp_failure(self, _mock):
        result = tcp_port_check("127.0.0.1", 443)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("TCP connection failed", result["details"])

    @patch("diagnostics.subprocess.run")
    def test_ping_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Reply from host", stderr=""
        )
        result = ping_check("example.test")
        self.assertEqual(result["status"], "PASS")
        mock_run.assert_called_once()

    @patch("diagnostics.subprocess.run")
    def test_ping_failure(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="Request timed out"
        )
        result = ping_check("example.test")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("Request timed out", result["details"])

    @patch("diagnostics.subprocess.run", side_effect=subprocess.TimeoutExpired("ping", 11))
    def test_ping_timeout(self, _mock):
        result = ping_check("example.test")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("timed out", result["details"])


if __name__ == "__main__":
    unittest.main()

