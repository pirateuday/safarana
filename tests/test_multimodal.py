import unittest
from fastapi.testclient import TestClient
from app import app
from tools.routing_tools import calculate_transit_options, get_route, get_multi_stop_route
from agents.planner_agent import PlannerAgent
from models.schemas import TripInput, StopoverInput, TravelMode

class TestMultiModalTransit(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.planner = PlannerAgent()

    def test_transit_options_generation(self):
        options = calculate_transit_options("Delhi", "Jaipur", 268.0, party_size=2)
        self.assertIn("driving", options)
        self.assertIn("train", options)
        self.assertIn("bus", options)
        self.assertIn("shared_cab", options)

        train_opt = options["train"]
        self.assertGreater(train_opt["buffered_duration_hours"], 0)
        self.assertEqual(train_opt["delay_buffer_ratio"], 0.12)
        self.assertEqual(train_opt["station_buffer_hours"], 0.67)
        self.assertGreater(train_opt["local_shared_transit_cost"], 0)
        self.assertIn("Railway", train_opt["departure_hub"])
        self.assertIn("Junction", train_opt["arrival_hub"])
        self.assertIn("Auto", train_opt["local_vehicle_type"])
        self.assertEqual(train_opt["total_cost"], train_opt["tickets_total"] + train_opt["local_shared_transit_cost"])

        bus_opt = options["bus"]
        self.assertEqual(bus_opt["delay_buffer_ratio"], 0.22)
        self.assertGreater(bus_opt["local_shared_transit_cost"], 0)
        self.assertIn("ISBT", bus_opt["departure_hub"])

        drive_opt = options["driving"]
        self.assertEqual(drive_opt["ticket_cost_per_person"], 0.0)
        self.assertEqual(drive_opt["local_shared_transit_cost"], 0.0)
        self.assertEqual(drive_opt["delay_buffer_ratio"], 0.18)

    def test_party_size_scaling(self):
        opt_solo = calculate_transit_options("Delhi", "Jaipur", 268.0, party_size=1)
        opt_family = calculate_transit_options("Delhi", "Jaipur", 268.0, party_size=4)

        self.assertEqual(opt_solo["driving"]["total_cost"], opt_family["driving"]["total_cost"])
        self.assertEqual(opt_family["train"]["tickets_total"], opt_solo["train"]["tickets_total"] * 4)

    def test_per_leg_multi_modal_routing(self):
        multi_route = get_multi_stop_route(
            origin="Delhi",
            destination="Jaipur",
            stopovers=["Neemrana"],
            travel_mode="driving",
            leg_modes=["train", "bus"],
            party_size=2
        )
        self.assertEqual(len(multi_route["legs"]), 2)
        leg0 = multi_route["legs"][0]
        leg1 = multi_route["legs"][1]

        self.assertEqual(leg0["selected_mode"], "train")
        self.assertIn("Rewari", leg0["arrival_hub"])
        self.assertGreater(leg0["local_transit_cost"], 0)

        self.assertEqual(leg1["selected_mode"], "bus")
        self.assertIn("Bus", leg1["arrival_hub"])
        self.assertGreater(leg1["local_transit_cost"], 0)

    def test_scheduler_transit_details_and_local_transfers(self):
        trip_in = TripInput(
            origin="Delhi",
            destination="Jaipur",
            stopovers=[StopoverInput(location="Neemrana", travel_mode="train")],
            leg_modes={"1": "bus"},
            party_size=2
        )
        plan = self.planner.generate_plan(trip_in)
        balanced = plan.options["balanced"]

        day1 = balanced.days[0]
        self.assertEqual(day1.transit_mode, "train")
        self.assertIsNotNone(day1.transit_details)
        steps = day1.transit_details["steps"]
        self.assertGreaterEqual(len(steps), 3)
        self.assertIn("Auto", steps[0]["title"])
        self.assertIn("Train", steps[1]["title"])
        self.assertIn("Auto", steps[2]["title"])

        self.assertEqual(day1.day_cost_breakdown["transport"], day1.transit_details["total_cost"])

    def test_mode_switch_changes_timing_and_cost(self):
        trip_drive = TripInput(origin="Delhi", destination="Jaipur", travel_mode=TravelMode.driving, party_size=2)
        plan_drive = self.planner.generate_plan(trip_drive)

        trip_train = TripInput(origin="Delhi", destination="Jaipur", travel_mode=TravelMode.train, party_size=2)
        plan_train = self.planner.generate_plan(trip_train)

        d1_drive = plan_drive.options["balanced"].days[0]
        d1_train = plan_train.options["balanced"].days[0]

        self.assertNotEqual(d1_drive.day_cost_breakdown["transport"], d1_train.day_cost_breakdown["transport"])
        self.assertNotEqual(d1_drive.transit_time_hours, d1_train.transit_time_hours)
        self.assertEqual(d1_train.transit_mode, "train")
        self.assertEqual(d1_drive.transit_mode, "driving")

    def test_api_plan_endpoint_with_leg_modes(self):
        payload = {
            "origin": "Delhi",
            "destination": "Jaipur",
            "stopovers": [{"location": "Neemrana"}],
            "leg_modes": {"0": "train", "1": "bus"},
            "budget": 16000.0,
            "party_size": 2,
            "start_date": "2026-10-01",
            "end_date": "2026-10-03"
        }
        res = self.client.post("/api/plan", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("route", data)
        self.assertIsNotNone(data["route"])
        legs = data["route"]["legs"]
        self.assertEqual(len(legs), 2)
        self.assertEqual(legs[0]["selected_mode"], "train")
        self.assertEqual(legs[1]["selected_mode"], "bus")
        self.assertEqual(len(legs[0]["available_modes"]), 4)

    def test_budget_agent_itemized_transport_breakdown(self):
        trip_in = TripInput(
            origin="Delhi",
            destination="Jaipur",
            travel_mode=TravelMode.train,
            return_travel_mode="bus",
            party_size=2
        )
        plan = self.planner.generate_plan(trip_in)
        balanced = plan.options["balanced"]
        cost_sum = balanced.cost_summary

        self.assertIn("tickets", cost_sum)
        self.assertIn("local_shared_transit", cost_sum)
        self.assertIn("fuel_tolls", cost_sum)
        self.assertGreater(cost_sum["tickets"], 0)
        self.assertGreater(cost_sum["local_shared_transit"], 0)

        # Sum of sub-components matches total transport
        expected_transport = round(cost_sum["tickets"] + cost_sum["local_shared_transit"] + cost_sum["fuel_tolls"], 2)
        self.assertAlmostEqual(cost_sum["transport"], expected_transport, delta=0.5)

    def test_return_leg_mode_selection_and_steps(self):
        trip_in = TripInput(
            origin="Delhi",
            destination="Jaipur",
            travel_mode=TravelMode.driving,
            return_travel_mode="train",
            party_size=2
        )
        plan = self.planner.generate_plan(trip_in)
        balanced = plan.options["balanced"]
        last_day = balanced.days[-1]

        self.assertEqual(last_day.transit_mode, "train")
        self.assertIsNotNone(last_day.transit_details)
        self.assertEqual(last_day.transit_details["mode"], "train")
        self.assertIn("Train", last_day.title)
        self.assertTrue(any(w in last_day.transit_details["departure_hub"] for w in ["Station", "Junction", "Terminal"]))

        steps = last_day.transit_details["steps"]
        self.assertGreaterEqual(len(steps), 3)
        self.assertIn("Auto", steps[0]["title"])
        self.assertIn("Train", steps[1]["title"])
        self.assertIn("Auto", steps[2]["title"])

if __name__ == "__main__":
    unittest.main()
