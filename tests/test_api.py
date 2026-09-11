import unittest
from fastapi.testclient import TestClient
from app import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_presets_endpoint(self):
        response = self.client.get("/api/presets")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("presets", data)
        self.assertGreaterEqual(len(data["presets"]), 3)

    def test_plan_endpoint(self):
        payload = {
            "origin": "Delhi",
            "destination": "Jaipur",
            "budget": 15000.0,
            "start_date": "2026-10-01",
            "end_date": "2026-10-03",
            "travel_mode": "driving",
            "party_size": 2
        }
        response = self.client.post("/api/plan", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("plan_id", data)
        self.assertIn("options", data)
        self.assertEqual(len(data["options"]), 4)

    def test_book_endpoint(self):
        payload = {
            "plan_id": "TEST-PLAN-001",
            "variant_type": "balanced",
            "item_type": "hotel",
            "item_id": "HTL-JPR-01",
            "date_or_time": "2026-10-01",
            "guests": 2,
            "user_name": "Test Traveler",
            "user_contact": "9999999999"
        }
        response = self.client.post("/api/book", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "CONFIRMED")
        self.assertIn("confirmation_code", data)

    def test_frontend_serving(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("SmartRoute", response.text)

    def test_export_ics_endpoint(self):
        payload = {
            "origin": "Delhi",
            "destination": "Jaipur",
            "budget": 15000.0,
            "start_date": "2026-10-01",
            "end_date": "2026-10-03",
            "travel_mode": "driving",
            "party_size": 2
        }
        plan_res = self.client.post("/api/plan", json=payload)
        self.assertEqual(plan_res.status_code, 200)
        plan_id = plan_res.json()["plan_id"]

        export_res = self.client.get(f"/api/plan/{plan_id}/export/ics?variant=balanced")
        self.assertEqual(export_res.status_code, 200)
        self.assertIn("text/calendar", export_res.headers.get("content-type", ""))
        self.assertIn("BEGIN:VCALENDAR", export_res.text)
        self.assertIn("END:VCALENDAR", export_res.text)

if __name__ == "__main__":
    unittest.main()
