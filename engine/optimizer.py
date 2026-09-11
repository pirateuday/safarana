from typing import Dict, List, Any
from models.schemas import ItineraryVariant

class ParetoOptimizer:
    """
    Evaluates multi-objective trade-offs across Cost, Sightseeing, Comfort, and Transit.
    """

    @staticmethod
    def calculate_scores(variants: Dict[str, ItineraryVariant], budget_cap: float) -> Dict[str, Dict[str, float]]:
        scores: Dict[str, Dict[str, float]] = {}

        for key, variant in variants.items():
            # 1. Cost Score (Lower cost relative to budget yields higher score)
            cost_ratio = variant.total_cost / max(1.0, budget_cap)
            cost_score = round(max(0.0, min(10.0, (1.0 - cost_ratio * 0.7) * 10)), 1)

            # 2. Sightseeing Score (More spots visited yields higher score)
            spots = variant.total_spots_visited
            sightseeing_score = round(min(10.0, (spots / 6.0) * 10), 1)

            # 3. Comfort / Leisure Score (Buffer quality, hotel tier)
            has_boutique = any(
                d.overnight_stay and "boutique" in d.overnight_stay.hotel.tier
                for d in variant.days
            )
            has_hostel = any(
                d.overnight_stay and "hostel" in d.overnight_stay.hotel.tier
                for d in variant.days
            )
            if key == "balanced":
                comfort_score = 9.2
            elif key == "scenic":
                comfort_score = 9.5 if has_boutique else 8.5
            elif key == "cheapest":
                comfort_score = 7.0 if has_hostel else 7.8
            else: # fastest
                comfort_score = 8.0

            # 4. Route Transit Efficiency (Distance vs transit time)
            transit_hours = sum(d.transit_time_hours for d in variant.days)
            speed_score = round(max(5.0, min(10.0, 10.0 - (transit_hours / 3.0))), 1)

            # Aggregate weighted overall
            composite = round((cost_score * 0.25) + (sightseeing_score * 0.3) + (comfort_score * 0.25) + (speed_score * 0.2), 1)

            scores[key] = {
                "composite": composite,
                "cost_score": cost_score,
                "sightseeing_score": sightseeing_score,
                "comfort_score": comfort_score,
                "transit_score": speed_score
            }

        return scores
