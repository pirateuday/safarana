import unittest
from engine.orchestrator import orchestrator
from models.schemas import TripInput

class TestExportCalendar(unittest.TestCase):
    def setUp(self):
        trip_in = TripInput(origin="Delhi", destination="Jaipur", budget=15000.0)
        self.plan = orchestrator.generate_trip(trip_in)

    def test_export_icalendar_structure(self):
        ics = orchestrator.export_icalendar(self.plan.plan_id, "balanced")
        self.assertIn("BEGIN:VCALENDAR", ics)
        self.assertIn("END:VCALENDAR", ics)
        self.assertIn("PRODID:-//SmartRoute AI Multi-Agent Trip Planner//NONSGML v1.0//EN", ics)
        self.assertIn("BEGIN:VEVENT", ics)
        self.assertIn("END:VEVENT", ics)
        self.assertIn("SUMMARY:", ics)
        self.assertIn("DTSTART:", ics)
        self.assertIn("DTEND:", ics)
        self.assertIn("UID:", ics)

    def test_export_invalid_plan_or_variant(self):
        with self.assertRaises(ValueError):
            orchestrator.export_icalendar("NON_EXISTENT_PLAN_ID", "balanced")

if __name__ == "__main__":
    unittest.main()
