import unittest
from fastapi.testclient import TestClient
from app import app
from tools.railway_tools import (
    get_trains_between,
    get_train_route_geometry,
    get_train_live_status,
    resolve_station_code
)
from tools.routing_tools import get_route, calculate_transit_options
from agents.planner_agent import PlannerAgent
from models.schemas import TripInput, StopoverInput

class TestRailwayAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.planner = PlannerAgent()

    def test_station_code_resolution(self):
        self.assertEqual(resolve_station_code("Delhi"), "NDLS")
        self.assertEqual(resolve_station_code("New Delhi"), "NDLS")
        self.assertEqual(resolve_station_code("Jaipur"), "JP")
        self.assertEqual(resolve_station_code("Mumbai"), "CSMT")
        self.assertEqual(resolve_station_code("Pune"), "PUNE")
        self.assertEqual(resolve_station_code("Bangalore"), "SBC")
        self.assertEqual(resolve_station_code("Chennai"), "MAS")

    def test_get_trains_between_cities(self):
        trains = get_trains_between("Delhi", "Jaipur")
        self.assertIsInstance(trains, list)
        self.assertGreater(len(trains), 0)
        first = trains[0]
        self.assertIn("number", first)
        self.assertIn("name", first)
        self.assertIn("departure", first)
        self.assertIn("arrival", first)
        self.assertIn("duration", first)
        self.assertIn("source", first)

    def test_get_trains_fallback_for_unmapped_pair(self):
        trains = get_trains_between("UnknownVillageA", "UnknownVillageB")
        self.assertIsInstance(trains, list)
        self.assertGreater(len(trains), 0)
        self.assertEqual(trains[0]["source"], "synthetic_fallback")

    def test_train_route_geometry(self):
        coords = get_train_route_geometry("12015")
        self.assertIsInstance(coords, list)

    def test_train_live_status(self):
        status = get_train_live_status("12015")
        self.assertIsInstance(status, dict)
        self.assertIn("train_number", status)
        self.assertIn("delay_mins", status)

    def test_api_trains_endpoint(self):
        res = self.client.get("/api/trains?origin=Delhi&destination=Jaipur")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["origin"], "Delhi")
        self.assertEqual(data["destination"], "Jaipur")
        self.assertGreater(data["count"], 0)
        self.assertEqual(len(data["trains"]), data["count"])

    def test_routing_with_selected_train(self):
        route = get_route("Delhi", "Jaipur", travel_mode="train", selected_train_number="12015")
        self.assertEqual(route["selected_mode"], "train")
        self.assertEqual(route["train_number"], "12015")
        self.assertIn("Shatabdi", route["train_name"])
        self.assertIsNotNone(route.get("departure_time"))
        self.assertIsNotNone(route.get("arrival_time"))
        self.assertGreater(len(route.get("available_trains", [])), 0)

    def test_end_to_end_planner_with_train_mode(self):
        trip_input = TripInput(
            origin="Delhi",
            destination="Jaipur",
            budget=20000.0,
            start_date="2026-10-01",
            end_date="2026-10-03",
            travel_mode="train",
            leg_modes={"0": "train"},
            selected_trains={"0": "12015"},
            return_travel_mode="train",
            return_train_number="12958",
            party_size=2
        )
        plan = self.planner.generate_plan(trip_input)
        self.assertIsNotNone(plan)
        self.assertIn("balanced", plan.options)

        balanced = plan.options["balanced"]
        # Check Day 1 transit
        day1 = balanced.days[0]
        self.assertEqual(day1.transit_mode, "train")
        self.assertIsNotNone(day1.transit_details)
        self.assertEqual(day1.transit_details.get("train_number"), "12015")
        self.assertIn("12015", day1.transit_details.get("mode_title", ""))

        # Check return day transit
        return_day = balanced.days[-1]
        self.assertEqual(return_day.transit_mode, "train")
        self.assertIsNotNone(return_day.transit_details)
        self.assertIn("train_number", return_day.transit_details)

if __name__ == "__main__":
    unittest.main()
