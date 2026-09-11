import unittest
from tools.hospitality_tools import (
    get_city_hotels,
    get_city_restaurants,
    search_hotels,
    search_restaurants,
    fetch_hotels_from_staying_api,
    fetch_hotels_from_google_places,
    fetch_restaurants_from_google_places,
    CURATED_HOTELS,
    CURATED_RESTAURANTS
)


class TestHospitalityAPI(unittest.TestCase):

    def test_curated_catalogs_exist(self):
        """Verify curated Indian hotels and restaurants databases are populated."""
        self.assertGreaterEqual(len(CURATED_HOTELS), 15)
        self.assertGreaterEqual(len(CURATED_RESTAURANTS), 15)

    def test_get_city_hotels_jaipur(self):
        """Verify unified hotel aggregator returns valid hotels with source badges."""
        hotels = get_city_hotels("Jaipur", max_count=10)
        self.assertGreater(len(hotels), 0)
        h0 = hotels[0]
        self.assertIn("id", h0)
        self.assertIn("name", h0)
        self.assertIn("tier", h0)
        self.assertIn("price_per_night", h0)
        self.assertIn("rating", h0)
        self.assertIn("source", h0)
        self.assertIn("address", h0)

    def test_get_city_hotels_tier_prioritization(self):
        """Verify tier filtering prioritizes selected accommodation type."""
        budget_hotels = get_city_hotels("Jaipur", stay_tier="budget_hostel")
        self.assertGreater(len(budget_hotels), 0)
        self.assertEqual(budget_hotels[0]["tier"], "budget_hostel")

        resort_hotels = get_city_hotels("Jaipur", stay_tier="boutique_resort")
        self.assertGreater(len(resort_hotels), 0)
        self.assertEqual(resort_hotels[0]["tier"], "boutique_resort")

    def test_get_city_restaurants_and_dhabas(self):
        """Verify food aggregator returns dining venues with cuisine types and dhaba flags."""
        restaurants = get_city_restaurants("Jaipur", max_count=10)
        self.assertGreater(len(restaurants), 0)
        r0 = restaurants[0]
        self.assertIn("id", r0)
        self.assertIn("name", r0)
        self.assertIn("cuisine_type", r0)
        self.assertIn("avg_cost_per_person", r0)
        self.assertIn("source", r0)

        # Test roadside dhaba discovery along corridor
        hwy_dhabas = get_city_restaurants("Delhi-Jaipur Highway", is_highway=True)
        self.assertGreater(len(hwy_dhabas), 0)
        self.assertTrue(any(r.get("is_dhaba") for r in hwy_dhabas))

    def test_regional_corridor_hospitality(self):
        """Verify authentic stays and food in newly supported corridors."""
        udaipur_stays = get_city_hotels("Udaipur")
        self.assertTrue(any("Mewar" in s["name"] or "Zostel" in s["name"] or "Lake" in s["name"] for s in udaipur_stays))

        darjeeling_food = get_city_restaurants("Darjeeling")
        self.assertTrue(any("Glenary" in r["name"] or "Keventers" in r["name"] or "Siliguri" in r["name"] for r in darjeeling_food))

    def test_staying_api_graceful_fallback(self):
        """Verify that StayingAPI handles missing or invalid keys gracefully without throwing exceptions."""
        result = fetch_hotels_from_staying_api("Jaipur", key="invalid_test_key_123")
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
