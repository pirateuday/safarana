import unittest
from models.schemas import TripInput, StopoverInput
from engine.orchestrator import orchestrator


class TestDiningReplacement(unittest.TestCase):
    """Verify user-selected dining replaces predefined meals in the day plan."""

    def _build_trip(self, selected_restaurant_ids=None, selected_dining_slots_by_city=None,
                    selected_dining_days_by_city=None):
        return TripInput(
            origin='Delhi',
            destination='Jaipur',
            stopovers=[
                StopoverInput(
                    location='Neemrana',
                    stay_days=1
                )
            ],
            budget=18000.0,
            start_date='2026-10-01',
            end_date='2026-10-03',
            party_size=2,
            selected_restaurant_ids=selected_restaurant_ids or [],
            selected_dining_slots_by_city=selected_dining_slots_by_city or {},
            selected_dining_days_by_city=selected_dining_days_by_city or {}
        )

    def test_selected_dining_replaces_predefined_meals_across_days(self):
        trip = self._build_trip(selected_restaurant_ids=['RES-JPR-01', 'RES-JPR-02'])
        plan = orchestrator.generate_trip(trip)
        self.assertIsNotNone(plan)
        self.assertIn('balanced', plan.options)

        variant = plan.options['balanced']
        # Every day carries an active_city echo for the frontend live patch
        for day in variant.days:
            self.assertTrue(day.active_city)

        flagged = [
            meal for day in variant.days for meal in day.meals
            if meal.restaurant.user_selected
        ]

        # Both user-selected restaurants must appear as meals (distributed across Jaipur days)
        self.assertGreaterEqual(len(flagged), 2)
        flagged_names = {meal.restaurant.name for meal in flagged}
        self.assertTrue(any('Rawat' in name for name in flagged_names))
        self.assertTrue(any('LMB' in name or 'Mishthan' in name for name in flagged_names))

        # Replaced meals land in the on-city dinner slot
        self.assertTrue(any(meal.meal_type == 'dinner' for meal in flagged))

        # No cross-city leakage: the stopover day (no selection) keeps its predefined dining
        non_flagged = [
            meal for day in variant.days for meal in day.meals
            if not meal.restaurant.user_selected
        ]
        self.assertGreater(len(non_flagged), 0)

    def test_selected_dining_per_slot_override(self):
        trip = self._build_trip(
            selected_restaurant_ids=['RES-JPR-01'],
            selected_dining_slots_by_city={'Jaipur': {'RES-JPR-01': ['dinner']}}
        )
        plan = orchestrator.generate_trip(trip)
        self.assertIsNotNone(plan)

        variant = plan.options['balanced']
        flagged = [
            meal for day in variant.days for meal in day.meals
            if meal.restaurant.user_selected
        ]

        # Dinner-only configuration: every flagged meal must be a dinner slot
        self.assertGreaterEqual(len(flagged), 1)
        self.assertTrue(all(meal.meal_type == 'dinner' for meal in flagged))
        self.assertTrue(all('Rawat' in meal.restaurant.name for meal in flagged))

        # Lunch slots must stay predefined (not overridden by the dinner-only pick)
        flagged_lunch = [
            meal for day in variant.days for meal in day.meals
            if meal.meal_type == 'lunch' and meal.restaurant.user_selected
        ]
        self.assertEqual(len(flagged_lunch), 0)

    def test_selected_dining_per_date_override(self):
        # Two city-wide picks rotate across Jaipur days by default, but LMB (RES-JPR-02)
        # is pinned to the second Jaipur day (2026-10-02) for dinner only.
        trip = self._build_trip(
            selected_restaurant_ids=['RES-JPR-01', 'RES-JPR-02'],
            selected_dining_slots_by_city={
                'Jaipur': {'RES-JPR-01': ['dinner'], 'RES-JPR-02': ['dinner']}
            },
            selected_dining_days_by_city={
                'Jaipur': {'RES-JPR-02': {'2026-10-02': ['dinner']}}
            }
        )
        plan = orchestrator.generate_trip(trip)
        self.assertIsNotNone(plan)

        variant = plan.options['balanced']
        by_date = {}
        for day in variant.days:
            if (day.active_city or '').lower().startswith('jaipur'):
                for meal in day.meals:
                    if meal.meal_type == 'dinner' and meal.restaurant.user_selected:
                        by_date[day.date] = meal.restaurant.name

        # The pinned date must host the pin's restaurant (LMB / Mishthan)
        self.assertIn('2026-10-02', by_date)
        self.assertTrue(any('LMB' in n or 'Mishthan' in n for n in [by_date['2026-10-02']]))

        # Any other Jaipur dinner day stays on the rotating pick (Rawat)
        for date, name in by_date.items():
            if date == '2026-10-02':
                continue
            self.assertTrue('Rawat' in name)


if __name__ == '__main__':
    unittest.main()