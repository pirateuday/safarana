import unittest
from tools.registry import registry
from tools.routing_tools import get_route, get_coordinates, haversine_distance
from tools.places_tools import search_places, get_opening_hours
from tools.hospitality_tools import search_hotels, search_restaurants, book_hotel, book_restaurant
from models.schemas import Coordinates

class TestTools(unittest.TestCase):
    def test_registry_populated(self):
        tools = registry.list_tools()
        self.assertGreaterEqual(len(tools), 7)
        tool_names = [t["name"] for t in tools]
        self.assertIn("get_route", tool_names)
        self.assertIn("search_places", tool_names)
        self.assertIn("search_hotels", tool_names)
        self.assertIn("book_hotel", tool_names)

    def test_routing_delhi_jaipur(self):
        route = get_route("Delhi", "Jaipur", "driving")
        self.assertIn("total_distance_km", route)
        self.assertGreater(route["total_distance_km"], 200.0)
        self.assertGreater(route["buffered_travel_time_hours"], route["base_travel_time_hours"])
        self.assertGreaterEqual(len(route["corridor_stops"]), 1)

    def test_places_and_opening_hours(self):
        spots = search_places("Jaipur", "heritage")
        self.assertGreaterEqual(len(spots), 1)
        amber = next((s for s in spots if "Amber" in s["name"]), spots[0])
        self.assertIn("opening_time", amber)
        self.assertIn("closing_time", amber)

        hours = get_opening_hours(amber["id"])
        self.assertEqual(hours["opening_time"], amber["opening_time"])

    def test_hospitality_and_booking(self):
        hotels = search_hotels("Jaipur", "standard_hotel", party_size=2)
        self.assertGreater(len(hotels), 0)
        hotel = hotels[0]

        res = book_hotel(hotel["id"], date="2026-10-01", guests=2, user_name="Test Traveler")
        self.assertEqual(res["status"], "CONFIRMED")
        self.assertTrue(res["confirmation_code"].startswith("CONF-"))

        dining = search_restaurants("Delhi-Jaipur Highway", cuisine_pref="roadside_dhaba")
        self.assertGreater(len(dining), 0)
        self.assertTrue(dining[0]["is_dhaba"])

    def test_new_corridor_places(self):
        # Curated (non-generic) spots for each newly added corridor
        cases = {
            "Manali": "Solang Valley",
            "Agra": "Fatehpur Sikri",
            "Udaipur": "City Palace",
            "Ooty": "Botanical Gardens",
            "Rishikesh": "Laxman Jhula",
            "Haridwar": "Mansa Devi",
            "Pondicherry": "Promenade Beach",
            "Darjeeling": "Tiger Hill",
            "Mahabaleshwar": "Arthur's Seat",
        }
        for loc, expect in cases.items():
            spots = search_places(loc, "scenic")
            names = " | ".join(s["name"] for s in spots)
            self.assertIn(expect, names, f"Expected curated spot '{expect}' for {loc}, got: {names}")
            # Curated spot must carry real geocodes, not the generic Delhi fallback (28.0 / 28.02)
            curated = next(s for s in spots if expect in s["name"])
            self.assertNotIn(curated["lat"], (28.0, 28.02))

    def test_new_corridor_hotels_and_dining(self):
        hotel_cases = {
            "Manali": "Whispering Pines",
            "Agra": "Orchid",
            "Udaipur": "Mewar Haveli",
            "Ooty": "Sterling",
            "Pondicherry": "Maison Perumal",
            "Darjeeling": "Windamere",
            "Mahabaleshwar": "Le Méridien",
        }
        for loc, expect in hotel_cases.items():
            hotels = search_hotels(loc, "boutique_resort", party_size=2)
            names = " | ".join(h["name"] for h in hotels)
            self.assertIn(expect, names, f"Expected curated hotel '{expect}' for {loc}, got: {names}")

        highway_dhabas = search_restaurants("Manali Highway Corridor", cuisine_pref="roadside_dhaba")
        self.assertTrue(any(r["is_dhaba"] for r in highway_dhabas))
        rishikesh_dhabas = search_restaurants("Rishikesh Highway Corridor", cuisine_pref="roadside_dhaba")
        self.assertTrue(any(r["is_dhaba"] for r in rishikesh_dhabas))
        ecr_dhabas = search_restaurants("Chennai-Pondicherry Highway Corridor", cuisine_pref="roadside_dhaba")
        self.assertTrue(any(r["is_dhaba"] for r in ecr_dhabas))

    def test_new_corridor_routing(self):
        route = get_route("Jaipur", "Udaipur", "driving")
        self.assertIn("Chittorgarh", route["corridor_stops"])

        pdy_route = get_route("Chennai", "Pondicherry", "driving")
        self.assertIn("Mahabalipuram", pdy_route["corridor_stops"])

        djl_route = get_route("Kolkata", "Darjeeling", "driving")
        self.assertIn("Siliguri", djl_route["corridor_stops"])

        mhb_route = get_route("Pune", "Mahabaleshwar", "driving")
        self.assertIn("Wai", mhb_route["corridor_stops"])

        coords = get_coordinates("Chittorgarh")
        self.assertAlmostEqual(coords.lat, 24.8797, delta=0.05)

if __name__ == "__main__":
    unittest.main()
