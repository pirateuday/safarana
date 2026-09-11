import unittest
from models.schemas import TripInput, StopoverInput
from engine.orchestrator import orchestrator
from tools.routing_tools import get_multi_stop_route
from agents.scheduler_agent import SchedulerAgent

class TestStopovers(unittest.TestCase):
    def test_multi_stop_routing(self):
        route = get_multi_stop_route('Delhi', 'Jaipur', stopovers=['Neemrana'])
        self.assertEqual(route['origin'], 'Delhi')
        self.assertEqual(route['destination'], 'Jaipur')
        self.assertIn('Neemrana', route['corridor_stops'])
        self.assertEqual(len(route['legs']), 2)
        self.assertEqual(route['legs'][0]['from_place'], 'Delhi')
        self.assertEqual(route['legs'][0]['to_place'], 'Neemrana')
        self.assertEqual(route['legs'][1]['from_place'], 'Neemrana')
        self.assertEqual(route['legs'][1]['to_place'], 'Jaipur')
        self.assertGreater(route['total_distance_km'], 150)

    def test_day_allocation_manual_duration(self):
        scheduler = SchedulerAgent()
        stopovers = [StopoverInput(location='Neemrana', stay_days=2)]
        day_cities, notes = scheduler._allocate_days(4, stopovers, 'Jaipur')
        self.assertEqual(len(day_cities), 4)
        self.assertEqual(day_cities.count('Neemrana'), 2)
        self.assertEqual(day_cities.count('Jaipur'), 2)
        self.assertEqual(day_cities, ['Neemrana', 'Neemrana', 'Jaipur', 'Jaipur'])

    def test_day_allocation_not_sure_ai(self):
        scheduler = SchedulerAgent()
        stopovers = [StopoverInput(location='Neemrana', stay_days=None)]
        day_cities, notes = scheduler._allocate_days(3, stopovers, 'Jaipur')
        self.assertEqual(len(day_cities), 3)
        self.assertEqual(day_cities.count('Neemrana'), 1)
        self.assertEqual(day_cities.count('Jaipur'), 2)

    def test_day_allocation_deadline_capping(self):
        scheduler = SchedulerAgent()
        stopovers = [StopoverInput(location='Neemrana', stay_days=3)]
        day_cities, notes = scheduler._allocate_days(3, stopovers, 'Jaipur')
        self.assertEqual(len(day_cities), 3)
        self.assertLessEqual(day_cities.count('Neemrana'), 2)
        self.assertGreaterEqual(day_cities.count('Jaipur'), 1)
        self.assertTrue(any('exceeds trip deadline' in n for n in notes))

    def test_e2e_plan_with_stopovers(self):
        inp = TripInput(
            origin='Delhi',
            destination='Jaipur',
            stopovers=[StopoverInput(location='Neemrana', stay_days=1)],
            start_date='2026-10-01',
            end_date='2026-10-03',
            budget=20000.0,
            party_size=2
        )
        plan = orchestrator.generate_trip(inp)
        self.assertIsNotNone(plan.plan_id)
        variant = plan.options['balanced']
        self.assertEqual(len(variant.days), 3)
        self.assertIn('Neemrana', variant.days[0].title)
        self.assertIsNotNone(variant.days[0].overnight_stay)
        self.assertIn('Neemrana', variant.days[0].overnight_stay.hotel.location)
        self.assertIn('Jaipur', variant.days[1].title)
        self.assertIsNotNone(variant.days[1].overnight_stay)
        self.assertIn('Jaipur', variant.days[1].overnight_stay.hotel.location)

if __name__ == '__main__':
    unittest.main()
