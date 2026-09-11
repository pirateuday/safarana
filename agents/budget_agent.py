from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent
from models.schemas import DayItinerary, FeasibilityCheck

class BudgetAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="BudgetAgent",
            role="Financial Auditor & Cost Gatekeeper",
            description="Audits and strictly validates all transportation, lodging, food, and activity fees against the trip budget."
        )

    def audit_itinerary(self, days: List[DayItinerary], budget_limit: float, party_size: int = 1) -> Tuple[FeasibilityCheck, Dict[str, float]]:
        self.log_step(
            recipient="Planner",
            action="audit_budget",
            payload={"budget_limit": budget_limit, "days": len(days), "party_size": party_size},
            notes=f"Starting itemized cost audit against hard budget cap of ₹{budget_limit:,.2f}."
        )

        total_transport = sum(d.day_cost_breakdown.get("transport", 0.0) for d in days)
        total_stays = sum(d.day_cost_breakdown.get("stay", 0.0) for d in days)
        total_food = sum(d.day_cost_breakdown.get("food", 0.0) for d in days)
        total_activities = sum(d.day_cost_breakdown.get("activities", 0.0) for d in days)
        total_buffer = sum(d.day_cost_breakdown.get("buffer", 0.0) for d in days)

        total_tickets = sum(
            float(d.transit_details.get("ticket_cost", 0.0))
            for d in days if d.transit_details
        )
        total_local_shared = sum(
            float(d.transit_details.get("local_transit_cost", 0.0))
            for d in days if d.transit_details
        )
        total_fuel_tolls = max(0.0, round(total_transport - total_tickets - total_local_shared, 2))

        total_spent = total_transport + total_stays + total_food + total_activities + total_buffer
        cost_summary = {
            "transport": round(total_transport, 2),
            "tickets": round(total_tickets, 2),
            "local_shared_transit": round(total_local_shared, 2),
            "fuel_tolls": round(total_fuel_tolls, 2),
            "stays": round(total_stays, 2),
            "food": round(total_food, 2),
            "activities": round(total_activities, 2),
            "buffer_reserve": round(total_buffer, 2),
            "total_spent": round(total_spent, 2),
            "budget_limit": round(budget_limit, 2),
            "remaining_surplus": round(budget_limit - total_spent, 2)
        }

        issues: List[str] = []
        recommendations: List[str] = []
        is_budget_ok = total_spent <= budget_limit

        if not is_budget_ok:
            deficit = total_spent - budget_limit
            issues.append(f"Projected expenditure (₹{total_spent:,.2f}) exceeds total budget (₹{budget_limit:,.2f}) by ₹{deficit:,.2f}.")

            # Compute concrete remediation advice
            if total_stays > deficit:
                recommendations.append(f"Downgrade accommodation tier (e.g. boutique to standard/hostel) to save up to ₹{min(total_stays * 0.4, deficit):,.0f}.")
            if total_activities > 500:
                recommendations.append("Swap high-ticket commercial experiences for scenic free viewpoints or monuments with nominal fees.")
            if total_food > 1000:
                recommendations.append("Prioritize authentic highway dhabas and local street-food specialties over fine-dining venues.")

            self.log_step(
                recipient="Planner",
                action="budget_rejected",
                payload={"deficit": deficit, "recommendations": recommendations},
                status="VIOLATION",
                notes=f"Over budget by ₹{deficit:,.2f}. Feedback sent to Planner for auto-remedy."
            )
        else:
            self.log_step(
                recipient="Planner",
                action="budget_approved",
                payload={"total_spent": total_spent, "surplus": budget_limit - total_spent},
                status="SUCCESS",
                notes=f"Itinerary satisfies budget constraint with a healthy surplus of ₹{budget_limit - total_spent:,.2f}."
            )

        feasibility = FeasibilityCheck(
            passed=is_budget_ok,
            budget_ok=is_budget_ok,
            budget_spent=round(total_spent, 2),
            budget_limit=round(budget_limit, 2),
            time_ok=True,
            opening_hours_ok=True,
            issues=issues,
            recommendations=recommendations
        )

        return feasibility, cost_summary
