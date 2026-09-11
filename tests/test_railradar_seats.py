import unittest
from tools.railway_tools import (
    generate_seat_status,
    get_train_full_details,
    get_train_live_status,
    get_trains_between,
    _infer_train_classes
)

class TestRailRadarSeatsAndRoutes(unittest.TestCase):

    def test_seat_status_generation(self):
        classes = ["1A", "2A", "3A", "SL"]
        seats = generate_seat_status(classes, "12958", distance_km=300.0)
        self.assertEqual(len(seats), 4)

        class_codes = [s["class_code"] for s in seats]
        self.assertIn("1A", class_codes)
        self.assertIn("2A", class_codes)
        self.assertIn("3A", class_codes)
        self.assertIn("SL", class_codes)

        for s in seats:
            self.assertIn("status", s)
            self.assertIn("status_code", s)
            self.assertIn("fare", s)
            self.assertIn("badge", s)
            self.assertGreater(s["fare"], 0)

    def test_infer_classes(self):
        self.assertEqual(_infer_train_classes("12015"), ["EC", "CC"])
        self.assertEqual(_infer_train_classes("20978"), ["EC", "CC"])
        self.assertEqual(_infer_train_classes("12958"), ["1A", "2A", "3A"])
        self.assertEqual(_infer_train_classes("14311"), ["1A", "2A", "3A", "SL"])

    def test_train_full_details(self):
        details = get_train_full_details("12015")
        self.assertIsNotNone(details)
        self.assertEqual(details["train_number"], "12015")
        self.assertIn("route_stops", details)
        self.assertGreater(len(details["route_stops"]), 0)
        self.assertIn("seat_status", details)
        self.assertGreater(len(details["seat_status"]), 0)
        self.assertIn("coach_position", details)

        first_stop = details["route_stops"][0]
        self.assertIn("station_name", first_stop)
        self.assertIn("station_code", first_stop)
        self.assertIn("departure", first_stop)

    def test_train_live_status(self):
        live = get_train_live_status("12015")
        self.assertIsNotNone(live)
        self.assertEqual(live["train_number"], "12015")
        self.assertIn("status", live)
        self.assertIn("delay_minutes", live)

    def test_get_trains_between_enriches_seats(self):
        trains = get_trains_between("Delhi", "Jaipur")
        self.assertGreater(len(trains), 0)
        t = trains[0]
        self.assertIn("seat_status", t)
        self.assertGreater(len(t["seat_status"]), 0)
        self.assertIn("route_stops", t)
        self.assertIn("coach_position", t)
        self.assertIn("live_status", t)

if __name__ == "__main__":
    unittest.main()
