import unittest
from agents.planner_agent import PlannerAgent
from models.schemas import TripInput, TravelMode
from engine.orchestrator import orchestrator

class TestAgents(unittest.TestCase):
    def test_planner_agent_pareto_generation(self):
        planner = PlannerAgent()
        trip_in = TripInput(
            origin="Delhi",
            destination="Jaipur",
            budget=18000.0,
            start_date="2026-10-01",
            end_date="2026-10-02",
            travel_mode=TravelMode.driving,
            party_size=2
        )
        plan = planner.generate_plan(trip_in)

        # Assert plan structure
        self.assertTrue(plan.plan_id.startswith("PLAN-"))
        self.assertIn("balanced", plan.options)
        self.assertIn("fastest", plan.options)
        self.assertIn("cheapest", plan.options)
        self.assertIn("scenic", plan.options)

        # Assert cheapest is <= balanced
        cheapest_cost = plan.options["cheapest"].total_cost
        scenic_cost = plan.options["scenic"].total_cost
        self.assertLessEqual(cheapest_cost, scenic_cost)

        # Assert agent trace logged communications
        self.assertGreater(len(plan.agent_trace), 15)
        senders = {t["sender"] for t in plan.agent_trace}
        self.assertIn("PlannerAgent", senders)
        self.assertIn("RouteAgent", senders)
        self.assertIn("SpotAgent", senders)
        self.assertIn("WeatherAgent", senders)
        self.assertIn("BudgetAgent", senders)
        self.assertIn("SchedulerAgent", senders)

        # Assert day weather is populated
        day0_weather = plan.options["balanced"].days[0].weather
        self.assertIsNotNone(day0_weather)
        self.assertGreater(day0_weather.temperature_celsius, 0)
        self.assertGreater(len(day0_weather.clothing_packing_advice), 0)

    def test_orchestrator_refinement(self):
        trip_in = TripInput(origin="Delhi", destination="Jaipur", budget=12000.0)
        plan = orchestrator.generate_trip(trip_in)
        self.assertIsNotNone(plan)

        # Refine trip with higher budget and party size 3
        refined = orchestrator.refine_trip(plan.plan_id, {"budget": 20000.0, "party_size": 3})
        self.assertEqual(refined.input_params.budget, 20000.0)
        self.assertEqual(refined.input_params.party_size, 3)

if __name__ == "__main__":
    unittest.main()
