"""Tests for CSV report generation."""
import csv
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import main  # noqa: E402


class ReportTests(unittest.TestCase):
    def test_save_report_writes_expected_columns_and_data(self):
        results = [{
            "check_type": "DNS",
            "target": "example.com",
            "status": "PASS",
            "response_time_ms": 12.5,
            "details": "Resolved successfully",
            "resolved_ip": "192.0.2.1",
        }]

        with patch.object(main, "REPORT_DIR", ROOT / "reports_test_tmp"):
            report_path = main.save_report(results)

            try:
                with report_path.open(newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)

                self.assertEqual(
                    reader.fieldnames,
                    main.FIELDS,
                )
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["check_type"], "DNS")
                self.assertEqual(rows[0]["target"], "example.com")
                self.assertEqual(rows[0]["status"], "PASS")
                self.assertEqual(rows[0]["response_time_ms"], "12.5")
                self.assertEqual(rows[0]["resolved_ip"], "192.0.2.1")

                timestamp = datetime.fromisoformat(rows[0]["timestamp"])
                self.assertIsNotNone(timestamp.tzinfo)
            finally:
                report_path.unlink(missing_ok=True)
                report_path.parent.rmdir()


if __name__ == "__main__":
    unittest.main()
