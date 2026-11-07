"""
Automated unit and functional tests for the Apex Federal Bank Web Portal.
"""

import json
from pathlib import Path
import tempfile
import unittest

from web.app import create_app


class TestWebPortal(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_landing_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Apex Federal Bank", resp.data)
        self.assertIn(b"Institutional Financial Management", resp.data)

    def test_atm_locator_page(self):
        resp = self.client.get("/atms")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"APX-4821", resp.data)
        self.assertIn(b"Vault Cash Stock", resp.data)

    def test_telemetry_api(self):
        resp = self.client.get("/api/v1/atm/status")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["terminal_id"], "APX-4821")
        self.assertEqual(data["status"], "ONLINE")
        self.assertIn("cassettes", data)

    def test_login_flow(self):
        # 1. Successful Login
        resp = self.client.post("/login", data={
            "card_number": "4532-0150-1122-3341",
            "pin": "1234"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Alexander Vance", resp.data)
        self.assertIn(b"Total Liquid Net Worth", resp.data)

        # 2. Failed Login
        client2 = self.app.test_client()
        resp_fail = client2.post("/login", data={
            "card_number": "4532-0150-1122-3341",
            "pin": "9998"
        }, follow_redirects=True)
        self.assertEqual(resp_fail.status_code, 200)
        self.assertIn(b"Invalid PIN", resp_fail.data)

    def test_dashboard_requires_login(self):
        resp = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers["Location"])

    def test_authenticated_transfer(self):
        # Log in first
        self.client.post("/login", data={
            "card_number": "4532-0150-1122-3341",
            "pin": "1234"
        })

        # Execute transfer of $100 from Checking to Savings
        resp = self.client.post("/transfer", data={
            "source_account": "ACT-1001-CHK",
            "target_account": "ACT-1002-SAV",
            "amount": "100.00"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Successfully transferred $100.00", resp.data)

    def test_card_freeze_toggle(self):
        self.client.post("/login", data={
            "card_number": "4532-0150-1122-3341",
            "pin": "1234"
        })

        # Toggle freeze
        resp = self.client.post("/cards/toggle-freeze", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"frozen", resp.data)

        # Toggle unfreeze
        resp2 = self.client.post("/cards/toggle-freeze", follow_redirects=True)
        self.assertEqual(resp2.status_code, 200)
        self.assertIn(b"unfrozen and active", resp2.data)

    def test_statement_download_csv(self):
        self.client.post("/login", data={
            "card_number": "4532-0150-1122-3341",
            "pin": "1234"
        })

        resp = self.client.get("/statement/download-csv")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "text/csv")
        self.assertIn(b"Transaction ID,Date/Time", resp.data)


if __name__ == "__main__":
    unittest.main()
