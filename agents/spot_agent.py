from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import Place, Coordinates

class SpotAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SpotAgent",
            role="Attraction & Experience Specialist",
            description="Discovers tourist spots, viewpoints, and cultural attractions, verifying operating hours and duration constraints."
        )

    def discover_spots(self, destination: str, corridor_stops: List[str], interests: List[str], stopovers: Optional[List[str]] = None) -> List[Place]:
        active_stopovers = [s.strip() for s in (stopovers or []) if s and s.strip()]
        self.log_step(
            recipient="Planner",
            action="initiate_discovery",
            payload={"destination": destination, "stopovers": active_stopovers, "interests": interests, "corridor_stops": corridor_stops},
            notes=f"Searching top attractions in {destination} and intermediate stopovers {active_stopovers} matching interests: {', '.join(interests)}."
        )

        all_raw_places: List[Dict[str, Any]] = []
        seen_ids = set()

        # 1. Search in user-selected intermediate stopovers
        for stop in active_stopovers:
            for interest in interests[:2]:
                found_stop = self.execute_tool("search_places", location=stop, interest=interest, max_results=2)
                for p in found_stop:
                    if p["id"] not in seen_ids:
                        seen_ids.add(p["id"])
                        all_raw_places.append(p)
            # Fallback if no interest match found
            if not any(stop.lower() in p["location"].lower() for p in all_raw_places):
                found_generic = self.execute_tool("search_places", location=stop, interest=None, max_results=2)
                for p in found_generic:
                    if p["id"] not in seen_ids:
                        seen_ids.add(p["id"])
                        all_raw_places.append(p)

        # 2. Search in main destination
        for interest in interests:
            found = self.execute_tool("search_places", location=destination, interest=interest, max_results=4)
            for p in found:
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    all_raw_places.append(p)

        # 3. Search key intermediate corridor stops (if space permits)
        for stop in corridor_stops[:2]:
            if stop.lower() not in [s.lower() for s in active_stopovers]:
                found_corridor = self.execute_tool("search_places", location=stop, interest=None, max_results=1)
                for p in found_corridor:
                    if p["id"] not in seen_ids:
                        seen_ids.add(p["id"])
                        all_raw_places.append(p)

        # Build Place models and verify operating hours
        places: List[Place] = []
        for p in all_raw_places:
            hours = self.execute_tool("get_opening_hours", place_id_or_name=p["id"])
            p_lat = p.get("lat")
            p_lon = p.get("lon")
            if p_lat is None or p_lon is None:
                from tools.routing_tools import get_coordinates
                loc_c = get_coordinates(p.get("location", destination))
                p_lat, p_lon = loc_c.lat, loc_c.lon
            place_obj = Place(
                id=p["id"],
                name=p["name"],
                location=p["location"],
                coords=Coordinates(lat=p_lat, lon=p_lon),
                category=p.get("category", "attraction"),
                interests=p.get("interests", []),
                typical_duration_mins=p.get("typical_duration_mins", 90),
                entry_fee_per_person=p.get("entry_fee_per_person", 0.0),
                rating=p.get("rating", 4.5),
                opening_time=hours.get("opening_time", "09:00"),
                closing_time=hours.get("closing_time", "18:00"),
                closed_days=hours.get("closed_days", []),
                description=p.get("description", "")
            )
            places.append(place_obj)

        self.log_step(
            recipient="Planner",
            action="spots_discovered",
            payload={"total_spots": len(places), "spot_names": [p.name for p in places]},
            notes=f"Retrieved {len(places)} verified attractions with full opening hours and entry fee data."
        )

        return places

    def check_schedule_feasibility(self, place: Place, visit_time: str) -> Dict[str, Any]:
        """Checks whether visit_time ('HH:MM') falls strictly within opening hours."""
        is_open = True
        reason = "Open"

        if place.opening_time and place.closing_time:
            if visit_time < place.opening_time:
                is_open = False
                reason = f"Opens later at {place.opening_time} (scheduled for {visit_time})"
            elif visit_time >= place.closing_time:
                is_open = False
                reason = f"Closes at {place.closing_time} (scheduled for {visit_time})"

        return {"is_open": is_open, "reason": reason}
