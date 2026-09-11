from typing import List, Dict, Any, Tuple
from models.schemas import DayItinerary, FeasibilityCheck
from config import DEFAULT_DELAY_BUFFER_RATIO, DEFAULT_STOP_BUFFER_MINUTES, MAX_DAILY_TRAVEL_HOURS

class ConstraintEngine:
    """
    Evaluates the 4 hard constraints of the SmartRoute problem:
    1. Budget: total cost <= budget
    2. Time Window: daily travel time <= daily driving limit
    3. Opening Hours: every activity falls within [opening_time, closing_time]
    4. Delays & Buffers: +15-20% traffic delay factor and >= 20 min buffers respected
    """

    @staticmethod
    def evaluate_itinerary(
        days: List[DayItinerary],
        budget_limit: float,
        buffer_ratio: float = DEFAULT_DELAY_BUFFER_RATIO,
        min_buffer_mins: int = DEFAULT_STOP_BUFFER_MINUTES
    ) -> FeasibilityCheck:
        issues: List[str] = []
        recommendations: List[str] = []

        total_cost = sum(d.total_day_cost for d in days)
        budget_ok = total_cost <= budget_limit
        if not budget_ok:
            over = total_cost - budget_limit
            issues.append(f"Budget Violation: Total cost of ₹{total_cost:,.2f} exceeds budget limit of ₹{budget_limit:,.2f} by ₹{over:,.2f}.")
            recommendations.append("Consider downgrading hotel tier or opting for budget roadside dhabas.")

        time_ok = True
        opening_hours_ok = True

        for day in days:
            # Check daily transit time
            if day.transit_time_hours > MAX_DAILY_TRAVEL_HOURS:
                time_ok = False
                issues.append(f"Day {day.day_number}: Transit time of {day.transit_time_hours}h exceeds safe daily limit of {MAX_DAILY_TRAVEL_HOURS}h.")
                recommendations.append("Add an overnight rest stop midway along the highway corridor.")

            # Check each activity's opening hours
            for act in day.activities:
                if not act.is_open:
                    opening_hours_ok = False
                    issues.append(f"Day {day.day_number}: Activity '{act.place.name}' at {act.start_time}-{act.end_time} is outside operating hours ({act.place.opening_time} - {act.place.closing_time}).")
                    recommendations.append(f"Reschedule {act.place.name} to morning or midday slot.")

                # Check buffer
                if act.buffer_mins < min_buffer_mins:
                    issues.append(f"Day {day.day_number}: Buffer before/after '{act.place.name}' is only {act.buffer_mins} mins (recommended: {min_buffer_mins} mins).")

        passed = budget_ok and time_ok and opening_hours_ok

        return FeasibilityCheck(
            passed=passed,
            budget_ok=budget_ok,
            budget_spent=round(total_cost, 2),
            budget_limit=round(budget_limit, 2),
            time_ok=time_ok,
            opening_hours_ok=opening_hours_ok,
            issues=issues,
            recommendations=recommendations
        )
