import unittest
from tools.flight_tools import (
    INDIAN_AIRPORTS,
    get_airport_for_city,
    get_flights_between,
    calculate_flight_transit,
    get_flight_details,
    book_flight,
)
from tools.cache import cache_db


class TestFlightTools(unittest.TestCase):

    def test_indian_airports_registry(self):
        """Ensure commercial airport registry is populated with major hubs."""
        self.assertIn("DEL", INDIAN_AIRPORTS)
        self.assertIn("BOM", INDIAN_AIRPORTS)
        self.assertIn("BLR", INDIAN_AIRPORTS)
        self.assertIn("JAI", INDIAN_AIRPORTS)
        self.assertIn("IXB", INDIAN_AIRPORTS)
        self.assertIn("DED", INDIAN_AIRPORTS)
        self.assertIn("CJB", INDIAN_AIRPORTS)

    def test_get_airport_for_city_direct_and_gateways(self):
        """Test direct airport lookup and regional hill station gateway mappings."""
        # Direct hub lookup
        delhi_apt = get_airport_for_city("Delhi")
        self.assertIsNotNone(delhi_apt)
        self.assertEqual(delhi_apt["code"], "DEL")

        mumbai_apt = get_airport_for_city("Mumbai")
        self.assertIsNotNone(mumbai_apt)
        self.assertEqual(mumbai_apt["code"], "BOM")

        jaipur_apt = get_airport_for_city("Jaipur")
        self.assertIsNotNone(jaipur_apt)
        self.assertEqual(jaipur_apt["code"], "JAI")

        # Regional gateways
        darjeeling_apt = get_airport_for_city("Darjeeling")
        self.assertIsNotNone(darjeeling_apt)
        self.assertEqual(darjeeling_apt["code"], "IXB")  # Bagdogra

        rishikesh_apt = get_airport_for_city("Rishikesh")
        self.assertIsNotNone(rishikesh_apt)
        self.assertEqual(rishikesh_apt["code"], "DED")  # Dehradun

        ooty_apt = get_airport_for_city("Ooty")
        self.assertIsNotNone(ooty_apt)
        self.assertEqual(ooty_apt["code"], "CJB")  # Coimbatore

        # Non-airport locality
        invalid_apt = get_airport_for_city("NonExistentTown12345")
        self.assertIsNone(invalid_apt)

    def test_get_flights_between_metro_and_regional(self):
        """Test commercial flight schedules between pairs."""
        flights = get_flights_between("Delhi", "Mumbai")
        self.assertGreaterEqual(len(flights), 2)
        f0 = flights[0]
        self.assertIn("flight_number", f0)
        self.assertIn("airline", f0)
        self.assertIn("departure_time", f0)
        self.assertIn("arrival_time", f0)
        self.assertIn("seat_status", f0)
        self.assertGreater(len(f0["seat_status"]), 0)
        self.assertIn("fare_breakdown", f0)
        self.assertGreater(f0["fare_breakdown"]["ticket_per_person"], 2000.0)

        # Same city flight should return empty
        same = get_flights_between("Delhi", "Delhi")
        self.assertEqual(len(same), 0)

    def test_calculate_flight_transit(self):
        """Test door-to-door transit time calculation including security and airport transfer buffers."""
        transit = calculate_flight_transit("Delhi", "Mumbai", dist_km=1400.0, party_size=2)
        self.assertIsNotNone(transit)
        self.assertEqual(transit["mode"], "flight")
        self.assertGreater(transit["buffered_duration_hours"], transit["base_duration_hours"])
        # Buffer should include check-in/security (1.75h) + deboarding/baggage (0.5h) + feeder cabs (1.5h)
        self.assertGreaterEqual(transit["station_buffer_hours"], 1.5)
        self.assertIn("fare_breakdown", transit)
        self.assertEqual(transit["fare_breakdown"]["party_size"], 2)
        self.assertGreater(transit["total_cost"], transit["ticket_cost_per_person"])

    def test_calculate_flight_transit_with_selected_flight(self):
        """Test custom selection of a specific flight number."""
        flights = get_flights_between("Delhi", "Jaipur")
        if flights:
            target_flight = flights[-1]["flight_number"]
            transit = calculate_flight_transit("Delhi", "Jaipur", dist_km=280.0, selected_flight_number=target_flight)
            self.assertIsNotNone(transit)
            self.assertEqual(transit["flight_number"], target_flight)

    def test_book_flight(self):
        """Test end-to-end flight booking and confirmation."""
        flights = get_flights_between("Delhi", "Mumbai")
        self.assertTrue(len(flights) > 0)
        fn = flights[0]["flight_number"]

        booking = book_flight(
            flight_number=fn,
            date="2026-10-15",
            guests=2,
            user_name="Aarav Sharma",
            cabin_class="Economy"
        )
        self.assertEqual(booking["status"], "CONFIRMED")
        self.assertEqual(booking["item_type"], "flight")
        self.assertTrue(booking["confirmation_code"].isalnum())
        self.assertIn("seats_assigned", booking["details"])
        self.assertGreater(booking["amount"], 0)


if __name__ == "__main__":
    unittest.main()
