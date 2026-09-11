import unittest
from fastapi.testclient import TestClient
from app import app

class TestLiveE2E(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_presets(self):
        r = self.client.get("/api/presets")
        self.assertEqual(r.status_code, 200)
        corridors = [p["id"] for p in r.json()["presets"]]
        self.assertIn("chennai-pondicherry", corridors)
        self.assertIn("kolkata-darjeeling", corridors)
        self.assertIn("pune-mahabaleshwar", corridors)

    def test_maps_status_and_trains(self):
        r = self.client.get("/api/maps/status")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data.get("key_configured"))

        tr = self.client.get("/api/trains/12015/details")
        self.assertEqual(tr.status_code, 200)
        self.assertTrue(tr.json()["success"])

    def test_plan_and_weather(self):
        payload = {
            "origin": "Chennai",
            "destination": "Pondicherry",
            "start_date": "2026-10-01",
            "end_date": "2026-10-02",
            "budget": 14000.0,
            "party_size": 2,
            "travel_mode": "driving",
            "interests": ["heritage", "scenic"]
        }
        r = self.client.post("/api/plan", json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("options", data)
        balanced = data["options"]["balanced"]
        self.assertGreater(len(balanced["days"]), 0)

        # Verify Weather integration
        day1 = balanced["days"][0]
        self.assertIsNotNone(day1["weather"])
        self.assertGreater(day1["weather"]["temperature_celsius"], 20.0)
        self.assertGreater(len(day1["weather"]["clothing_packing_advice"]), 0)

        # Verify Calendar .ics export
        plan_id = data["plan_id"]
        ics_res = self.client.get(f"/api/plan/{plan_id}/export/ics?variant=balanced")
        self.assertEqual(ics_res.status_code, 200)
        self.assertIn("text/calendar", ics_res.headers.get("content-type", ""))
        self.assertIn("BEGIN:VCALENDAR", ics_res.text)
        self.assertIn("END:VCALENDAR", ics_res.text)

if __name__ == "__main__":
    unittest.main()
