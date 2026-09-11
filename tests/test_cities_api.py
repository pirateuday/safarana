import unittest
from fastapi.testclient import TestClient
from app import app
from tools.routing_tools import get_city_catalog, get_route

class TestCitiesAndCustomRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_cities_endpoint(self):
        response = self.client.get("/api/cities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cities", data)
        cities = data["cities"]
        self.assertGreaterEqual(len(cities), 20)

        # Check required fields
        for city in cities:
            self.assertIn("name", city)
            self.assertIn("category", city)
            self.assertIn("state", city)
            self.assertIn("lat", city)
            self.assertIn("lon", city)

        city_names = [c["name"] for c in cities]
        self.assertIn("Delhi", city_names)
        self.assertIn("Mumbai", city_names)
        self.assertIn("Bangalore", city_names)
        self.assertIn("Jaipur", city_names)
        self.assertIn("Goa", city_names)

    def test_plan_custom_unpaired_origin_destination(self):
        # Testing a pair that wasn't a predefined corridor (e.g. Pune to Goa)
        payload = {
            "origin": "Pune",
            "destination": "Goa",
            "budget": 20000.0,
            "start_date": "2026-11-01",
            "end_date": "2026-11-03",
            "travel_mode": "driving",
            "party_size": 2
        }
        response = self.client.post("/api/plan", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("plan_id", data)
        self.assertIn("options", data)
        self.assertIn("balanced", data["options"])
        variant = data["options"]["balanced"]
        self.assertEqual(data["input_params"]["origin"], "Pune")
        self.assertEqual(data["input_params"]["destination"], "Goa")
        self.assertGreater(variant["total_distance_km"], 100)

    def test_dynamic_corridor_interpolation(self):
        # Test routing for arbitrary pair
        route = get_route("Chandigarh", "Shimla", "driving")
        self.assertEqual(route["origin"], "Chandigarh")
        self.assertEqual(route["destination"], "Shimla")
        self.assertGreater(route["total_distance_km"], 0)
        self.assertTrue(len(route["corridor_stops"]) > 0)
