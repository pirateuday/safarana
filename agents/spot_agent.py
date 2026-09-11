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

    def discover_spots(
        self,
        destination: str,
        corridor_stops: List[str],
        interests: List[str],
        stopovers: Optional[List[str]] = None,
        user_selected_places: Optional[List[str]] = None,
        places_by_city: Optional[Dict[str, List[str]]] = None
    ) -> List[Place]:
        active_stopovers = [s.strip() for s in (stopovers or []) if s and s.strip()]
        user_selected_list = [p.strip() for p in (user_selected_places or []) if p and p.strip()]
        city_places_dict = places_by_city or {}

        # Aggregate set of user-selected place names/ids for lookup
        user_selected_set = {p.lower() for p in user_selected_list}
        for spots in city_places_dict.values():
            for sp in spots:
                if sp and sp.strip():
                    user_selected_set.add(sp.strip().lower())

        self.log_step(
            recipient="Planner",
            action="initiate_discovery",
            payload={
                "destination": destination,
                "stopovers": active_stopovers,
                "interests": interests,
                "corridor_stops": corridor_stops,
                "user_selected_count": len(user_selected_set)
            },
            notes=f"Searching top attractions in {destination} and intermediate stopovers {active_stopovers} matching interests: {', '.join(interests)}. Prioritizing {len(user_selected_set)} user-selected places."
        )

        all_raw_places: List[Dict[str, Any]] = []
        seen_ids = set()

        # 0. First, explicitly load all user-selected spots by city
        from tools.poi_tools import get_city_spots
        for city, requested_names in city_places_dict.items():
            if not requested_names:
                continue
            city_spots = get_city_spots(city_name=city, max_count=30)
            for sp in city_spots:
                sp_name = sp.get("name", "").strip().lower()
                sp_id = sp.get("id", "").strip().lower()
                if any(req.strip().lower() in sp_name or sp_name in req.strip().lower() or req.strip().lower() == sp_id for req in requested_names):
                    if sp["id"] not in seen_ids:
                        sp["user_selected"] = True
                        seen_ids.add(sp["id"])
                        all_raw_places.append(sp)

        # Also search user_selected_list in destination or stopovers if not already added
        if user_selected_list:
            for city in [destination] + active_stopovers:
                city_spots = get_city_spots(city_name=city, max_count=30)
                for sp in city_spots:
                    sp_name = sp.get("name", "").strip().lower()
                    sp_id = sp.get("id", "").strip().lower()
                    if any(req.strip().lower() in sp_name or sp_name in req.strip().lower() or req.strip().lower() == sp_id for req in user_selected_list):
                        if sp["id"] not in seen_ids:
                            sp["user_selected"] = True
                            seen_ids.add(sp["id"])
                            all_raw_places.append(sp)

        # 1. Search in user-selected intermediate stopovers
        for stop in active_stopovers:
            for interest in interests[:2]:
                found_stop = self.execute_tool("search_places", location=stop, interest=interest, max_results=3)
                for p in found_stop:
                    if p["id"] not in seen_ids:
                        seen_ids.add(p["id"])
                        all_raw_places.append(p)
            # Fallback if no interest match found
            if not any(stop.lower() in p.get("location", "").lower() for p in all_raw_places):
                found_generic = self.execute_tool("search_places", location=stop, interest=None, max_results=3)
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
                found_corridor = self.execute_tool("search_places", location=stop, interest=None, max_results=2)
                for p in found_corridor:
                    if p["id"] not in seen_ids:
                        seen_ids.add(p["id"])
                        all_raw_places.append(p)

        # Build Place models and verify operating hours
        places: List[Place] = []
        for p in all_raw_places:
            p_name_lower = p.get("name", "").strip().lower()
            p_id_lower = p.get("id", "").strip().lower()
            is_user_chosen = (
                p.get("user_selected", False) or
                p_name_lower in user_selected_set or
                p_id_lower in user_selected_set or
                any(u in p_name_lower or p_name_lower in u for u in user_selected_set)
            )

            # Use opening hours from p if available, otherwise check get_opening_hours
            op_time = p.get("opening_time")
            cl_time = p.get("closing_time")
            cl_days = p.get("closed_days", [])
            if not op_time or not cl_time:
                hours = self.execute_tool("get_opening_hours", place_id_or_name=p["id"])
                op_time = hours.get("opening_time", "09:00")
                cl_time = hours.get("closing_time", "18:00")
                cl_days = hours.get("closed_days", [])

            p_lat = p.get("lat")
            p_lon = p.get("lon")
            if p_lat is None or p_lon is None:
                from tools.routing_tools import get_coordinates
                loc_c = get_coordinates(p.get("location", destination))
                p_lat, p_lon = loc_c.lat, loc_c.lon

            place_obj = Place(
                id=p["id"],
                name=p["name"],
                location=p.get("location", destination),
                coords=Coordinates(lat=p_lat, lon=p_lon),
                category=p.get("category", "attraction"),
                genre=p.get("genre") or "🏛️ Heritage & Monument",
                source=p.get("source", "curated"),
                user_selected=is_user_chosen,
                interests=p.get("interests", []),
                typical_duration_mins=p.get("typical_duration_mins", 90),
                entry_fee_per_person=p.get("entry_fee_per_person", 0.0),
                rating=p.get("rating", 4.5),
                opening_time=op_time or "09:00",
                closing_time=cl_time or "18:00",
                closed_days=cl_days or [],
                description=p.get("description", "")
            )
            places.append(place_obj)

        # Prioritize user-selected places so they appear first
        places.sort(key=lambda x: not x.user_selected)

        self.log_step(
            recipient="Planner",
            action="spots_discovered",
            payload={
                "total_spots": len(places),
                "user_selected_count": sum(1 for p in places if p.user_selected),
                "spot_names": [p.name for p in places]
            },
            notes=f"Retrieved {len(places)} verified attractions ({sum(1 for p in places if p.user_selected)} selected by user) with full opening hours and entry fee data."
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
