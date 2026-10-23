"""Basic tests for input validation and DNS result formatting."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from diagnostics import dns_lookup, tcp_port_check  # noqa: E402


class DiagnosticsTests(unittest.TestCase):
    def test_empty_hostname_fails(self):
        self.assertEqual(dns_lookup(" ")["status"], "FAIL")
        self.assertEqual(tcp_port_check("", 443)["status"], "FAIL")

    def test_invalid_ports_fail(self):
        self.assertEqual(tcp_port_check("localhost", 0)["status"], "FAIL")
        self.assertEqual(tcp_port_check("localhost", 65536)["status"], "FAIL")

    @patch("diagnostics.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("192.0.2.1", 0))])
    def test_dns_success(self, _mock):
        result = dns_lookup("example.test")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("192.0.2.1", result["resolved_ip"])


if __name__ == "__main__":
    unittest.main()
