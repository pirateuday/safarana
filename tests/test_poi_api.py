import unittest
from fastapi.testclient import TestClient
from app import app
from tools.poi_tools import (
    parse_osm_opening_hours,
    determine_genre_and_category,
    get_city_spots
)
from models.schemas import TripInput, StopoverInput
from engine.orchestrator import orchestrator

class TestPOIExtractionAndUserSpots(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_osm_opening_hours_parser(self):
        # Case 1: Standard daily range
        res1 = parse_osm_opening_hours('Mo-Su 09:00-18:30')
        self.assertEqual(res1['opening_time'], '09:00')
        self.assertEqual(res1['closing_time'], '18:30')
        self.assertFalse(res1['is_24_7'])
        self.assertEqual(res1['closed_days'], [])

        # Case 2: 24/7 open
        res2 = parse_osm_opening_hours('24/7')
        self.assertEqual(res2['opening_time'], '00:00')
        self.assertEqual(res2['closing_time'], '23:59')
        self.assertTrue(res2['is_24_7'])

        # Case 3: Closed on Mondays
        res3 = parse_osm_opening_hours('Tu-Su 09:30-17:00; Mo off')
        self.assertEqual(res3['opening_time'], '09:30')
        self.assertEqual(res3['closing_time'], '17:00')
        self.assertIn('Monday', res3['closed_days'])

        # Case 4: None or empty string
        res4 = parse_osm_opening_hours(None)
        self.assertEqual(res4['opening_time'], '09:00')
        self.assertEqual(res4['closing_time'], '18:00')

    def test_genre_and_category_classification(self):
        # Fort / Castle
        genre, cat = determine_genre_and_category({'historic': 'fort'}, 'Nahargarh Fort')
        self.assertIn('Fort', genre)
        self.assertEqual(cat, 'heritage')

        # Temple / Spiritual
        genre, cat = determine_genre_and_category({'amenity': 'place_of_worship', 'religion': 'hindu'}, 'Birla Mandir')
        self.assertIn('Spiritual', genre)
        self.assertEqual(cat, 'spiritual')

        # Museum
        genre, cat = determine_genre_and_category({'tourism': 'museum'}, 'Albert Hall')
        self.assertIn('Museum', genre)
        self.assertEqual(cat, 'museum')

        # Viewpoint
        genre, cat = determine_genre_and_category({'tourism': 'viewpoint'}, 'Sunset Point')
        self.assertIn('Viewpoint', genre)
        self.assertEqual(cat, 'viewpoint')

    def test_get_city_spots_catalog(self):
        spots = get_city_spots('Jaipur', max_count=10)
        self.assertGreaterEqual(len(spots), 3)
        for s in spots:
            self.assertIn('name', s)
            self.assertIn('genre', s)
            self.assertIn('category', s)
            self.assertIn('source', s)
            self.assertIn('opening_time', s)
            self.assertIn('closing_time', s)
            self.assertIn('entry_fee_per_person', s)

        # Genre filtering
        fort_spots = get_city_spots('Jaipur', genre_filter='fort', max_count=10)
        self.assertTrue(all('fort' in s['genre'].lower() or 'fort' in s['category'].lower() for s in fort_spots))

    def test_api_spots_endpoint(self):
        # Test basic city spots fetch
        res = self.client.get('/api/spots?city=Jaipur')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['city'], 'Jaipur')
        self.assertIn('spots', data)
        self.assertGreater(data['count'], 0)

        # Test genre filter query param
        res_genre = self.client.get('/api/spots?city=Jaipur&genre=fort')
        self.assertEqual(res_genre.status_code, 200)
        data_genre = res_genre.json()
        self.assertIn('spots', data_genre)
        self.assertTrue(all('fort' in s['genre'].lower() or 'fort' in s['category'].lower() for s in data_genre['spots']))

    def test_e2e_planning_with_user_selected_spots(self):
        # Plan a trip with user-selected spots for Destination (Jaipur) and Stopover (Neemrana)
        trip_input = TripInput(
            origin='Delhi',
            destination='Jaipur',
            stopovers=[
                StopoverInput(
                    location='Neemrana',
                    stay_days=1,
                    selected_places=['Neemrana Fort-Palace (En Route)']
                )
            ],
            selected_places=['Hawa Mahal (Palace of Winds)', 'Nahargarh Fort Sunset Viewpoint'],
            budget=18000.0,
            start_date='2026-10-01',
            end_date='2026-10-03',
            party_size=2
        )

        plan = orchestrator.generate_trip(trip_input)
        self.assertIsNotNone(plan)
        self.assertIn('balanced', plan.options)

        variant = plan.options['balanced']
        all_activities = [act for day in variant.days for act in day.activities]
        activity_place_names = [act.place.name for act in all_activities]

        # Verify that the user-selected destination places are scheduled
        self.assertTrue(any('Hawa Mahal' in name for name in activity_place_names))
        self.assertTrue(any('Nahargarh' in name for name in activity_place_names))

        # Verify that user_selected attribute is preserved on scheduled places
        user_selected_acts = [act for act in all_activities if act.place.user_selected]
        self.assertGreaterEqual(len(user_selected_acts), 2)
        user_selected_names = [act.place.name for act in user_selected_acts]
        self.assertTrue(any('Hawa Mahal' in name or 'Nahargarh' in name for name in user_selected_names))

        # Verify stopover place is scheduled on the stopover day (Day 1)
        day_1_places = [act.place.name for act in variant.days[0].activities]
        self.assertTrue(any('Neemrana' in name for name in day_1_places))

if __name__ == '__main__':
    unittest.main()
