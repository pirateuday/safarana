import unittest
from engine.constraints import ConstraintEngine
from models.schemas import DayItinerary, Activity, Place, Coordinates

class TestConstraints(unittest.TestCase):
    def test_budget_violation_detection(self):
        # Create day exceeding budget
        day1 = DayItinerary(
            day_number=1,
            date="2026-10-01",
            title="Day 1",
            total_day_cost=15000.0,
            day_cost_breakdown={"transport": 5000, "stay": 7000, "food": 2000, "activities": 1000}
        )

        feasibility = ConstraintEngine.evaluate_itinerary([day1], budget_limit=10000.0)
        self.assertFalse(feasibility.passed)
        self.assertFalse(feasibility.budget_ok)
        self.assertGreater(len(feasibility.issues), 0)
        self.assertTrue(any("Budget Violation" in issue for issue in feasibility.issues))

    def test_budget_pass_when_under_limit(self):
        day1 = DayItinerary(
            day_number=1,
            date="2026-10-01",
            title="Day 1",
            total_day_cost=6000.0,
            day_cost_breakdown={"transport": 2000, "stay": 2500, "food": 1000, "activities": 500}
        )
        feasibility = ConstraintEngine.evaluate_itinerary([day1], budget_limit=10000.0)
        self.assertTrue(feasibility.passed)
        self.assertTrue(feasibility.budget_ok)

    def test_opening_hours_violation(self):
        place = Place(
            id="P1", name="Night Club Monument", location="City", coords=Coordinates(lat=28.0, lon=77.0),
            category="monument", opening_time="18:00", closing_time="23:00"
        )
        # Scheduled at 10:00 AM (closed)
        act = Activity(
            activity_id="A1", place=place, start_time="10:00", end_time="11:30",
            duration_mins=90, buffer_mins=25, is_open=False, opening_status_note="Closed"
        )
        day1 = DayItinerary(
            day_number=1, date="2026-10-01", title="Day 1",
            activities=[act], total_day_cost=1000.0
        )
        feasibility = ConstraintEngine.evaluate_itinerary([day1], budget_limit=5000.0)
        self.assertFalse(feasibility.passed)
        self.assertFalse(feasibility.opening_hours_ok)

if __name__ == "__main__":
    unittest.main()
