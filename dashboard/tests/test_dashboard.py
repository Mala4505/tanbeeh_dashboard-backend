from django.test import TestCase

class DashboardTest(TestCase):
    def test_bootstrap_endpoint(self):
        resp = self.client.get("/api/dashboard/bootstrap/?role=prefect&days=7")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        for key in ["daily", "weekly", "rooms", "flagged", "meta"]:
            self.assertIn(key, body)
