from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from models.schemas import (
    DayItinerary, Activity, Meal, Stay, Place, Hotel, Restaurant, RouteOption, StopoverInput
)
from config import DEFAULT_DELAY_BUFFER_RATIO, DEFAULT_STOP_BUFFER_MINUTES
from tools.routing_tools import get_route

class SchedulerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SchedulerAgent",
            role="Timeline & Dispatch Engineer",
            description="Constructs clock-time itineraries factoring in traffic delay models, inter-activity buffers, and attraction opening windows."
        )

    def _mins_to_time_str(self, minutes_since_midnight: int) -> str:
        hours = (minutes_since_midnight // 60) % 24
        mins = minutes_since_midnight % 60
        return f"{hours:02d}:{mins:02d}"

    def _time_str_to_mins(self, time_str: str) -> int:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    def _allocate_days(self, num_days: int, stopovers: List[StopoverInput], destination: str) -> Tuple[List[str], List[str]]:
        """Allocates each day of the trip to a specific city/stop within total num_days deadline."""
        valid_stopovers = [s for s in stopovers if s.location and s.location.strip()]
        notes = []

        if not valid_stopovers:
            return [destination] * num_days, notes

        manual_stops = [s for s in valid_stopovers if s.stay_days is not None and s.stay_days > 0]
        auto_stops = [s for s in valid_stopovers if s.stay_days is None or s.stay_days <= 0]

        allocations: Dict[str, int] = {}
        total_manual = sum(s.stay_days for s in manual_stops)

        # Cap if manual days exceed available days (keeping at least 1 day for destination)
        if num_days > 1 and total_manual >= num_days:
            max_for_stops = max(1, num_days - 1)
            notes.append(f"Requested {total_manual} days across stopovers exceeds trip deadline ({num_days} days). Auto-adjusted stays to fit deadline.")
            running = 0
            for s in manual_stops[:-1]:
                scaled = max(1, int(s.stay_days * (max_for_stops / total_manual)))
                allocations[s.location] = scaled
                running += scaled
            last_manual = manual_stops[-1]
            allocations[last_manual.location] = max(1, max_for_stops - running)
            allocations[destination] = 1
            for s in auto_stops:
                allocations[s.location] = 0
        else:
            for s in manual_stops:
                allocations[s.location] = s.stay_days
            remaining = num_days - total_manual

            # Distribute remaining days across auto_stops and destination
            if not auto_stops:
                allocations[destination] = max(1, remaining)
            else:
                if remaining <= len(auto_stops) + 1:
                    for s in auto_stops:
                        allocations[s.location] = 1 if remaining > 1 else 0
                        if allocations[s.location] > 0:
                            remaining -= 1
                    allocations[destination] = max(1, remaining)
                else:
                    for s in auto_stops:
                        alloc = min(2, max(1, remaining // (len(auto_stops) + 1)))
                        allocations[s.location] = alloc
                        remaining -= alloc
                    allocations[destination] = max(1, remaining)

        # Build day-by-day city sequence
        day_cities: List[str] = []
        for s in valid_stopovers:
            count = allocations.get(s.location, 0)
            day_cities.extend([s.location] * count)
        dest_count = allocations.get(destination, max(1, num_days - len(day_cities)))
        day_cities.extend([destination] * dest_count)

        if len(day_cities) < num_days:
            day_cities.extend([destination] * (num_days - len(day_cities)))
        elif len(day_cities) > num_days:
            day_cities = day_cities[:num_days]

        return day_cities, notes

    def _find_leg_for_pair(self, from_c: str, to_c: str, route: RouteOption, party_size: int, default_mode: str, selected_train: Optional[str] = None) -> Dict[str, Any]:
        """Finds matching route leg or dynamically computes transit options for city pair."""
        f_norm = from_c.strip().lower()
        t_norm = to_c.strip().lower()
        for leg in route.legs:
            if leg.from_place.strip().lower() == f_norm and leg.to_place.strip().lower() == t_norm:
                return {
                    "mode": leg.selected_mode,
                    "distance_km": leg.distance_km,
                    "duration_hours": leg.buffered_duration_hours,
                    "cost": leg.estimated_transit_cost,
                    "ticket_cost": leg.ticket_cost,
                    "local_transit_cost": leg.local_transit_cost,
                    "departure_hub": leg.departure_hub,
                    "arrival_hub": leg.arrival_hub,
                    "local_vehicle_type": leg.local_vehicle_type,
                    "train_number": leg.train_number,
                    "train_name": leg.train_name,
                    "departure_time": leg.departure_time,
                    "arrival_time": leg.arrival_time,
                    "available_trains": leg.available_trains,
                    "fare_source": getattr(leg, "fare_source", "calibrated_model"),
                    "fare_currency": getattr(leg, "fare_currency", "₹"),
                    "fare_breakdown": getattr(leg, "fare_breakdown", {}),
                    "seat_status": getattr(leg, "seat_status", []),
                    "coach_position": getattr(leg, "coach_position", ""),
                    "route_stops": getattr(leg, "route_stops", []),
                    "live_status": getattr(leg, "live_status", {}),
                    "live_delay_mins": getattr(leg, "live_delay_mins", 0),
                    "live_status_text": getattr(leg, "live_status_text", "Scheduled")
                }
        # Fallback if not directly in route.legs (e.g. return leg)
        rt = get_route(from_c, to_c, travel_mode=default_mode, party_size=party_size, selected_train_number=selected_train)
        return {
            "mode": default_mode,
            "distance_km": rt["total_distance_km"],
            "duration_hours": rt["buffered_travel_time_hours"],
            "cost": rt["estimated_transit_cost"],
            "ticket_cost": rt.get("ticket_cost", 0.0),
            "local_transit_cost": rt.get("local_transit_cost", 0.0),
            "departure_hub": rt.get("departure_hub", ""),
            "arrival_hub": rt.get("arrival_hub", ""),
            "local_vehicle_type": rt.get("local_vehicle_type", ""),
            "train_number": rt.get("train_number"),
            "train_name": rt.get("train_name"),
            "departure_time": rt.get("departure_time"),
            "arrival_time": rt.get("arrival_time"),
            "available_trains": rt.get("available_trains", []),
            "fare_source": rt.get("fare_source", "calibrated_model"),
            "fare_currency": rt.get("fare_currency", "₹"),
            "fare_breakdown": rt.get("fare_breakdown", {}),
            "seat_status": rt.get("seat_status", []),
            "coach_position": rt.get("coach_position", ""),
            "route_stops": rt.get("route_stops", []),
            "live_status": rt.get("live_status", {}),
            "live_delay_mins": rt.get("live_delay_mins", 0),
            "live_status_text": rt.get("live_status_text", "Scheduled")
        }

    def build_schedule(
        self,
        start_date_str: str,
        end_date_str: str,
        start_time_of_day: str,
        route: RouteOption,
        places: List[Place],
        stay: Hotel,
        highway_meals: List[Restaurant],
        city_meals: List[Restaurant],
        party_size: int = 1,
        variant_type: str = "balanced",
        stopovers: Optional[List[StopoverInput]] = None,
        hotels_by_city: Optional[Dict[str, Hotel]] = None,
        dining_by_city: Optional[Dict[str, List[Restaurant]]] = None,
        return_travel_mode: Optional[str] = None,
        return_train_number: Optional[str] = None
    ) -> List[DayItinerary]:
        self.log_step(
            recipient="Planner",
            action="build_schedule",
            payload={"variant": variant_type, "spots_count": len(places), "party_size": party_size},
            notes=f"Generating {variant_type} timeline with multi-modal transit legs, local shared vehicle feeders, and opening window validations."
        )

        try:
            d_start = datetime.strptime(start_date_str, "%Y-%m-%d")
            d_end = datetime.strptime(end_date_str, "%Y-%m-%d")
            num_days = max(1, (d_end - d_start).days + 1)
        except Exception:
            num_days = 2
            d_start = datetime.now()

        effective_stopovers = stopovers or []
        day_cities, alloc_notes = self._allocate_days(num_days, effective_stopovers, route.destination)

        # Distribute places according to their location
        places_per_day: List[List[Place]] = [[] for _ in range(num_days)]
        city_places: Dict[str, List[Place]] = {}
        for p in places:
            matched_city = None
            for c in day_cities:
                if c.lower() in p.location.lower() or p.location.lower() in c.lower():
                    matched_city = c
                    break
            if not matched_city:
                matched_city = route.destination
            city_places.setdefault(matched_city, []).append(p)

        for c_name, c_spots in city_places.items():
            matching_day_indices = [idx for idx, c in enumerate(day_cities) if c.lower() == c_name.lower()]
            if not matching_day_indices:
                matching_day_indices = [0]
            # Prioritize user-selected spots first
            sorted_c_spots = sorted(c_spots, key=lambda s: not s.user_selected)
            for i, p in enumerate(sorted_c_spots):
                target_day = matching_day_indices[i % len(matching_day_indices)]
                places_per_day[target_day].append(p)

        days: List[DayItinerary] = []

        for day_num in range(1, num_days + 1):
            curr_date = (d_start + timedelta(days=day_num - 1)).strftime("%Y-%m-%d")
            active_city = day_cities[day_num - 1]
            prev_city = day_cities[day_num - 2] if day_num > 1 else route.origin
            day_places = places_per_day[day_num - 1]
            activities: List[Activity] = []
            meals: List[Meal] = []
            feasibility_notes: List[str] = list(alloc_notes) if day_num == 1 else []

            is_start_day = (day_num == 1)
            is_return_day = (day_num == num_days and num_days > 1)
            is_transition_day = (day_num > 1 and active_city.lower() != prev_city.lower())

            current_time_mins = self._time_str_to_mins(start_time_of_day if is_start_day else "08:30")
            day_transit_km = 0.0
            day_transit_hours = 0.0
            day_transit_cost = 350.0
            transit_mode = "local"
            transit_details = None
            leg_info = None

            # 1. Start Day: Depart from Origin to active_city
            if is_start_day:
                leg_info = self._find_leg_for_pair(route.origin, active_city, route, party_size, route.selected_mode)
                transit_mode = leg_info["mode"]
                day_transit_km = leg_info["distance_km"]
                day_transit_hours = leg_info["duration_hours"]
                day_transit_cost = leg_info["cost"]
                dep_hub = leg_info["departure_hub"] or f"{route.origin} Station"
                arr_hub = leg_info["arrival_hub"] or f"{active_city} Station"
                local_veh = leg_info["local_vehicle_type"] or "Shared Auto"

                if transit_mode == "train":
                    t_num = leg_info.get("train_number") or ""
                    t_name = leg_info.get("train_name") or "Intercity Express Train"
                    train_label = f"🚆 {t_num} {t_name}".strip() if t_num else f"🚆 {t_name}"

                    if leg_info.get("departure_time") and leg_info.get("arrival_time"):
                        train_dep = leg_info["departure_time"]
                        train_arr = leg_info["arrival_time"]
                        dep_mins = self._time_str_to_mins(train_dep)
                        arr_mins = self._time_str_to_mins(train_arr)
                        feeder_start = self._mins_to_time_str(max(300, dep_mins - 45))
                        dep_station = self._mins_to_time_str(max(330, dep_mins - 10))

                        # If train runs across midday (11:30 - 14:30), add onboard lunch
                        if dep_mins <= 780 and arr_mins >= 750:
                            lunch_dep = self._mins_to_time_str(max(dep_mins + 45, min(780, (dep_mins + arr_mins) // 2)))
                            meals.append(Meal(
                                meal_type="lunch",
                                restaurant=highway_meals[0] if highway_meals else Restaurant(
                                    id=f"PANTRY-{active_city[:3]}", name="IRCTC Pantry Car / Railway Catering",
                                    location=f"Aboard {train_label}", cuisine_type="local_cuisine", avg_cost_per_person=180.0, rating=4.3
                                ),
                                time_slot=f"{lunch_dep} - {self._mins_to_time_str(self._time_str_to_mins(lunch_dep) + 35)}",
                                estimated_cost=180.0 * party_size
                            ))

                        t_hotel = self._mins_to_time_str(arr_mins + 35)
                        current_time_mins = arr_mins + 35
                    else:
                        feeder_start = self._mins_to_time_str(current_time_mins)
                        current_time_mins += 35
                        dep_station = self._mins_to_time_str(current_time_mins)
                        train_dep = dep_station
                        rail_mins = max(45, int((day_transit_hours - 1.0) * 60))
                        half_rail = rail_mins // 2
                        current_time_mins += half_rail
                        lunch_time = self._mins_to_time_str(current_time_mins)
                        meals.append(Meal(
                            meal_type="lunch",
                            restaurant=highway_meals[0] if highway_meals else Restaurant(
                                id=f"PANTRY-{active_city[:3]}", name=f"Railway Catering / Station Kitchen",
                                location=dep_hub, cuisine_type="local_cuisine", avg_cost_per_person=180.0, rating=4.3
                            ),
                            time_slot=f"{lunch_time} - {self._mins_to_time_str(current_time_mins + 35)}",
                            estimated_cost=180.0 * party_size
                        ))
                        current_time_mins += 35 + DEFAULT_STOP_BUFFER_MINUTES
                        current_time_mins += max(30, rail_mins - half_rail)
                        train_arr = self._mins_to_time_str(current_time_mins)
                        current_time_mins += 35
                        t_hotel = self._mins_to_time_str(current_time_mins)

                    transit_details = {
                        "mode": "train",
                        "mode_title": train_label,
                        "from_place": route.origin,
                        "to_place": active_city,
                        "distance_km": day_transit_km,
                        "duration_hours": day_transit_hours,
                        "total_cost": day_transit_cost,
                        "ticket_cost": leg_info["ticket_cost"],
                        "local_transit_cost": leg_info["local_transit_cost"],
                        "departure_hub": dep_hub,
                        "arrival_hub": arr_hub,
                        "local_vehicle_type": local_veh,
                        "train_number": leg_info.get("train_number"),
                        "train_name": leg_info.get("train_name"),
                        "departure_time": leg_info.get("departure_time"),
                        "arrival_time": leg_info.get("arrival_time"),
                        "available_trains": leg_info.get("available_trains", []),
                        "steps": [
                            {"title": f"Local Shared Auto / Metro to {dep_hub}", "time": f"{feeder_start} - {dep_station}", "cost": 140.0, "vehicle": "Shared Auto"},
                            {"title": f"Express Train ({train_label}): {dep_hub} ➔ {arr_hub}", "time": f"{train_dep} - {train_arr}", "cost": leg_info["ticket_cost"], "vehicle": train_label},
                            {"title": f"Local Shared Auto from {arr_hub} to Stay", "time": f"{train_arr} - {t_hotel}", "cost": 160.0, "vehicle": "Shared Auto"}
                        ]
                    }
                elif transit_mode == "bus":
                    t_start = self._mins_to_time_str(current_time_mins)
                    current_time_mins += 25
                    t_stand = self._mins_to_time_str(current_time_mins)
                    bus_mins = max(40, int((day_transit_hours - 0.8) * 60))
                    half_bus = bus_mins // 2
                    current_time_mins += half_bus
                    lunch_time = self._mins_to_time_str(current_time_mins)
                    meals.append(Meal(
                        meal_type="lunch",
                        restaurant=highway_meals[0] if highway_meals else Restaurant(
                            id=f"BUS-DHB-{active_city[:3]}", name="Highway Express Rest Stop Dhaba",
                            location="Interstate Corridor", cuisine_type="roadside_dhaba", avg_cost_per_person=200.0, rating=4.4, is_dhaba=True
                        ),
                        time_slot=f"{lunch_time} - {self._mins_to_time_str(current_time_mins + 40)}",
                        estimated_cost=200.0 * party_size
                    ))
                    current_time_mins += 40 + DEFAULT_STOP_BUFFER_MINUTES
                    current_time_mins += max(30, bus_mins - half_bus)
                    t_arr = self._mins_to_time_str(current_time_mins)
                    current_time_mins += 25
                    t_hotel = self._mins_to_time_str(current_time_mins)

                    transit_details = {
                        "mode": "bus",
                        "mode_title": "Highway Express Bus",
                        "from_place": route.origin,
                        "to_place": active_city,
                        "distance_km": day_transit_km,
                        "duration_hours": day_transit_hours,
                        "total_cost": day_transit_cost,
                        "ticket_cost": leg_info["ticket_cost"],
                        "local_transit_cost": leg_info["local_transit_cost"],
                        "departure_hub": dep_hub,
                        "arrival_hub": arr_hub,
                        "local_vehicle_type": local_veh,
                        "steps": [
                            {"title": f"Shared Auto / Metro Feeder to {dep_hub}", "time": f"{t_start} - {t_stand}", "cost": 90.0, "vehicle": "Shared Auto"},
                            {"title": f"Highway Express Bus: {dep_hub} ➔ {arr_hub}", "time": f"{t_stand} - {t_arr}", "cost": leg_info["ticket_cost"], "vehicle": "Express Bus"},
                            {"title": f"Shared Auto from {arr_hub} to Stay", "time": f"{t_arr} - {t_hotel}", "cost": 110.0, "vehicle": "Shared Auto"}
                        ]
                    }
                elif transit_mode == "shared_cab":
                    t_start = self._mins_to_time_str(current_time_mins)
                    drive_mins = int(day_transit_hours * 60)
                    half_drive = max(30, drive_mins // 2)
                    current_time_mins += half_drive
                    lunch_time = self._mins_to_time_str(current_time_mins)
                    meals.append(Meal(
                        meal_type="lunch",
                        restaurant=highway_meals[0] if highway_meals else Restaurant(
                            id=f"DHB-CAB-{active_city[:3]}", name="Highway Shared Cab Midway Rest",
                            location="NH Highway", cuisine_type="roadside_dhaba", avg_cost_per_person=220.0, rating=4.5, is_dhaba=True
                        ),
                        time_slot=f"{lunch_time} - {self._mins_to_time_str(current_time_mins + 45)}",
                        estimated_cost=220.0 * party_size
                    ))
                    current_time_mins += 45 + DEFAULT_STOP_BUFFER_MINUTES
                    current_time_mins += max(30, drive_mins - half_drive)
                    t_end = self._mins_to_time_str(current_time_mins)

                    transit_details = {
                        "mode": "shared_cab",
                        "mode_title": "Shared Outstation Cab / Shuttle",
                        "from_place": route.origin,
                        "to_place": active_city,
                        "distance_km": day_transit_km,
                        "duration_hours": day_transit_hours,
                        "total_cost": day_transit_cost,
                        "ticket_cost": leg_info["ticket_cost"],
                        "local_transit_cost": leg_info["local_transit_cost"],
                        "departure_hub": dep_hub,
                        "arrival_hub": arr_hub,
                        "local_vehicle_type": local_veh,
                        "steps": [
                            {"title": f"Shared Cab Doorstep Feeder Pickup ({dep_hub})", "time": f"{t_start}", "cost": leg_info["local_transit_cost"], "vehicle": "Shared Cab"},
                            {"title": f"Shared Highway Drive: {dep_hub} ➔ {arr_hub}", "time": f"{t_start} - {t_end}", "cost": leg_info["ticket_cost"], "vehicle": "Shared Outstation Cab"}
                        ]
                    }
                else: # driving
                    t_start = self._mins_to_time_str(current_time_mins)
                    buffered_transit_mins = int(day_transit_hours * 60)
                    drive_leg_1 = max(30, buffered_transit_mins // 2)
                    current_time_mins += drive_leg_1
                    lunch_time = self._mins_to_time_str(current_time_mins)

                    highway_dhaba = highway_meals[0] if highway_meals else Restaurant(
                        id="DHB-MID", name=f"Midway Grand Dhaba ({route.origin} to {active_city})", location="National Highway",
                        cuisine_type="roadside_dhaba", avg_cost_per_person=220.0, rating=4.5, is_dhaba=True
                    )
                    meals.append(Meal(
                        meal_type="lunch",
                        restaurant=highway_dhaba,
                        time_slot=f"{lunch_time} - {self._mins_to_time_str(current_time_mins + 45)}",
                        estimated_cost=highway_dhaba.avg_cost_per_person * party_size
                    ))
                    current_time_mins += 45 + DEFAULT_STOP_BUFFER_MINUTES
                    current_time_mins += max(30, buffered_transit_mins - drive_leg_1)
                    t_end = self._mins_to_time_str(current_time_mins)

                    transit_details = {
                        "mode": "driving",
                        "mode_title": "Self-Drive / Personal Car",
                        "from_place": route.origin,
                        "to_place": active_city,
                        "distance_km": day_transit_km,
                        "duration_hours": day_transit_hours,
                        "total_cost": day_transit_cost,
                        "ticket_cost": 0.0,
                        "local_transit_cost": 0.0,
                        "departure_hub": f"{route.origin} (Doorstep)",
                        "arrival_hub": f"{active_city} (Direct)",
                        "local_vehicle_type": "Private / Rental Vehicle",
                        "steps": [
                            {"title": f"Highway Drive via NH Corridor with +18% Traffic Buffer", "time": f"{t_start} - {t_end}", "cost": day_transit_cost, "vehicle": "Personal Car"}
                        ]
                    }

            # 2. Inter-City Transition Day (Moving from stopover to next stopover/destination)
            elif is_transition_day:
                leg_info = self._find_leg_for_pair(prev_city, active_city, route, party_size, route.selected_mode)
                transit_mode = leg_info["mode"]
                day_transit_km = leg_info["distance_km"]
                day_transit_hours = leg_info["duration_hours"]
                day_transit_cost = leg_info["cost"]
                dep_hub = leg_info["departure_hub"] or f"{prev_city} Station"
                arr_hub = leg_info["arrival_hub"] or f"{active_city} Station"
                local_veh = leg_info["local_vehicle_type"] or "Shared Auto"

                if transit_mode == "train":
                    t_num = leg_info.get("train_number") or ""
                    t_name = leg_info.get("train_name") or "Intercity Express Train"
                    train_label = f"🚆 {t_num} {t_name}".strip() if t_num else f"🚆 {t_name}"

                    if leg_info.get("departure_time") and leg_info.get("arrival_time"):
                        train_dep = leg_info["departure_time"]
                        train_arr = leg_info["arrival_time"]
                        dep_mins = self._time_str_to_mins(train_dep)
                        arr_mins = self._time_str_to_mins(train_arr)
                        feeder_start = self._mins_to_time_str(max(300, dep_mins - 45))
                        dep_station = self._mins_to_time_str(max(330, dep_mins - 10))
                        t_hotel = self._mins_to_time_str(arr_mins + 30)
                        current_time_mins = arr_mins + 30
                    else:
                        feeder_start = self._mins_to_time_str(current_time_mins)
                        current_time_mins += 30
                        dep_station = self._mins_to_time_str(current_time_mins)
                        train_dep = dep_station
                        rail_mins = max(40, int((day_transit_hours - 1.0) * 60))
                        current_time_mins += rail_mins
                        train_arr = self._mins_to_time_str(current_time_mins)
                        current_time_mins += 30
                        t_hotel = self._mins_to_time_str(current_time_mins)

                    transit_details = {
                        "mode": "train",
                        "mode_title": train_label,
                        "from_place": prev_city,
                        "to_place": active_city,
                        "distance_km": day_transit_km,
                        "duration_hours": day_transit_hours,
                        "total_cost": day_transit_cost,
                        "ticket_cost": leg_info["ticket_cost"],
                        "local_transit_cost": leg_info["local_transit_cost"],
                        "departure_hub": dep_hub,
                        "arrival_hub": arr_hub,
                        "local_vehicle_type": local_veh,
                        "train_number": leg_info.get("train_number"),
                        "train_name": leg_info.get("train_name"),
                        "departure_time": leg_info.get("departure_time"),
                        "arrival_time": leg_info.get("arrival_time"),
                        "available_trains": leg_info.get("available_trains", []),
                        "steps": [
                            {"title": f"Local Shared Auto to {dep_hub}", "time": f"{feeder_start} - {dep_station}", "cost": 140.0, "vehicle": "Shared Auto"},
                            {"title": f"Express Train ({train_label}): {dep_hub} ➔ {arr_hub}", "time": f"{train_dep} - {train_arr}", "cost": leg_info["ticket_cost"], "vehicle": train_label},
                            {"title": f"Local Shared Auto from {arr_hub} to Stay", "time": f"{train_arr} - {t_hotel}", "cost": 160.0, "vehicle": "Shared Auto"}
                        ]
                    }
                elif transit_mode == "bus":
                    t_start = self._mins_to_time_str(current_time_mins)
                    current_time_mins += 25
                    t_stand = self._mins_to_time_str(current_time_mins)
                    bus_mins = max(35, int((day_transit_hours - 0.8) * 60))
                    current_time_mins += bus_mins
                    t_arr = self._mins_to_time_str(current_time_mins)
                    current_time_mins += 25
                    t_hotel = self._mins_to_time_str(current_time_mins)

                    transit_details = {
                        "mode": "bus",
                        "mode_title": "Highway Express Bus",
                        "from_place": prev_city,
                        "to_place": active_city,
                        "distance_km": day_transit_km,
                        "duration_hours": day_transit_hours,
                        "total_cost": day_transit_cost,
                        "ticket_cost": leg_info["ticket_cost"],
                        "local_transit_cost": leg_info["local_transit_cost"],
                        "departure_hub": dep_hub,
                        "arrival_hub": arr_hub,
                        "local_vehicle_type": local_veh,
                        "steps": [
                            {"title": f"Shared Auto to {dep_hub}", "time": f"{t_start} - {t_stand}", "cost": 90.0, "vehicle": "Shared Auto"},
                            {"title": f"Highway Express Bus: {dep_hub} ➔ {arr_hub}", "time": f"{t_stand} - {t_arr}", "cost": leg_info["ticket_cost"], "vehicle": "Express Bus"},
                            {"title": f"Shared Auto from {arr_hub} to Stay", "time": f"{t_arr} - {t_hotel}", "cost": 110.0, "vehicle": "Shared Auto"}
                        ]
                    }
                else: # driving or shared_cab
                    drive_leg = max(30, int(day_transit_hours * 60) // 2)
                    current_time_mins += drive_leg
                    lunch_time = self._mins_to_time_str(current_time_mins)

                    lunch_dhaba = highway_meals[day_num % len(highway_meals)] if highway_meals else Restaurant(
                        id=f"DHB-LEG-{day_num}", name=f"{prev_city} to {active_city} Highway Treat", location="Interstate Corridor",
                        cuisine_type="roadside_dhaba", avg_cost_per_person=240.0, rating=4.4, is_dhaba=True
                    )
                    meals.append(Meal(
                        meal_type="lunch",
                        restaurant=lunch_dhaba,
                        time_slot=f"{lunch_time} - {self._mins_to_time_str(current_time_mins + 45)}",
                        estimated_cost=lunch_dhaba.avg_cost_per_person * party_size
                    ))
                    current_time_mins += 45 + DEFAULT_STOP_BUFFER_MINUTES
                    current_time_mins += max(30, int(day_transit_hours * 60) - drive_leg)

                    transit_details = {
                        "mode": transit_mode,
                        "mode_title": "Self-Drive Car" if transit_mode == "driving" else "Shared Outstation Cab",
                        "from_place": prev_city,
                        "to_place": active_city,
                        "distance_km": day_transit_km,
                        "duration_hours": day_transit_hours,
                        "total_cost": day_transit_cost,
                        "ticket_cost": leg_info.get("ticket_cost", 0.0),
                        "local_transit_cost": leg_info.get("local_transit_cost", 0.0),
                        "departure_hub": dep_hub,
                        "arrival_hub": arr_hub,
                        "local_vehicle_type": local_veh,
                        "steps": [
                            {"title": f"Drive from {prev_city} to {active_city} via Interstate Highway", "time": f"{start_time_of_day} departure", "cost": day_transit_cost, "vehicle": "Car / Cab"}
                        ]
                    }

            # 3. Final Day Return
            elif is_return_day:
                ret_mode = return_travel_mode or route.selected_mode
                leg_info = self._find_leg_for_pair(active_city, route.origin, route, party_size, ret_mode, selected_train=return_train_number)
                transit_mode = leg_info["mode"]
                day_transit_km = leg_info["distance_km"]
                day_transit_hours = leg_info["duration_hours"]
                day_transit_cost = leg_info["cost"]
                dep_hub = leg_info["departure_hub"] or f"{active_city} Station"
                arr_hub = leg_info["arrival_hub"] or f"{route.origin} Station"
                if transit_mode == "train":
                    if not any(w in dep_hub for w in ["Station", "Junction", "Terminal"]):
                        dep_hub = f"{dep_hub} Railway Station"
                    if not any(w in arr_hub for w in ["Station", "Junction", "Terminal"]):
                        arr_hub = f"{arr_hub} Railway Station"
                local_veh = leg_info["local_vehicle_type"] or "Shared Auto"

                if transit_mode == "train":
                    t_num = leg_info.get("train_number") or ""
                    t_name = leg_info.get("train_name") or "Return Express Train"
                    train_label = f"🚆 {t_num} {t_name}".strip() if t_num else f"🚆 {t_name}"
                    train_dep = leg_info.get("departure_time") or "15:15"
                    train_arr = leg_info.get("arrival_time") or "19:45"
                    dep_mins = self._time_str_to_mins(train_dep)
                    feeder_start = self._mins_to_time_str(max(300, dep_mins - 45))
                    dep_hub_reach = self._mins_to_time_str(max(330, dep_mins - 10))

                    return_steps = [
                        {"title": f"Local Shared Auto / E-Rickshaw to {dep_hub}", "time": f"{feeder_start} - {dep_hub_reach}", "cost": 140.0, "vehicle": "Shared Auto"},
                        {"title": f"Return Express Train ({train_label}): {dep_hub} ➔ {arr_hub}", "time": f"{train_dep} - {train_arr}", "cost": leg_info.get("ticket_cost", 0.0), "vehicle": train_label},
                        {"title": f"Local Shared Auto from {arr_hub} to Home ({route.origin})", "time": f"{train_arr} Arrival", "cost": 160.0, "vehicle": "Shared Auto"}
                    ]
                elif transit_mode == "bus":
                    return_steps = [
                        {"title": f"Local Feeder / Shared Auto to {dep_hub}", "time": "14:30 - 14:55", "cost": 90.0, "vehicle": "Shared Auto"},
                        {"title": f"Return Highway Express Bus: {dep_hub} ➔ {arr_hub}", "time": "15:00 Departure", "cost": leg_info.get("ticket_cost", 0.0), "vehicle": "Express Bus"},
                        {"title": f"Shared Auto from {arr_hub} to Home ({route.origin})", "time": "Final Drop", "cost": 110.0, "vehicle": "Shared Auto"}
                    ]
                elif transit_mode == "shared_cab":
                    return_steps = [
                        {"title": f"Shared Cab Doorstep Feeder Pickup at Hotel in {active_city}", "time": "14:30 Pickup", "cost": leg_info.get("local_transit_cost", 80.0), "vehicle": "Shared Cab"},
                        {"title": f"Return Shared Cab Highway Transit to {route.origin}", "time": "Direct Drop", "cost": leg_info.get("ticket_cost", day_transit_cost), "vehicle": "Shared Outstation Cab"}
                    ]
                else:
                    return_steps = [
                        {"title": f"Return Drive from {active_city} to {route.origin} via Highway", "time": "14:30 Departure", "cost": day_transit_cost, "vehicle": "Self-Drive Car"}
                    ]

                transit_details = {
                    "mode": transit_mode,
                    "mode_title": f"Return via {train_label if transit_mode == 'train' else transit_mode.title()}",
                    "from_place": active_city,
                    "to_place": route.origin,
                    "distance_km": day_transit_km,
                    "duration_hours": day_transit_hours,
                    "total_cost": day_transit_cost,
                    "ticket_cost": leg_info.get("ticket_cost", 0.0),
                    "local_transit_cost": leg_info.get("local_transit_cost", 0.0),
                    "departure_hub": dep_hub,
                    "arrival_hub": arr_hub,
                    "local_vehicle_type": local_veh,
                    "train_number": leg_info.get("train_number"),
                    "train_name": leg_info.get("train_name"),
                    "departure_time": leg_info.get("departure_time"),
                    "arrival_time": leg_info.get("arrival_time"),
                    "available_trains": leg_info.get("available_trains", []),
                    "steps": return_steps
                }

            # 4. Standard local day
            else:
                day_transit_km = 25.0
                day_transit_hours = 1.0
                day_transit_cost = 350.0
                transit_mode = "local"
                transit_details = {
                    "mode": "local",
                    "mode_title": "Local City Transit (Shared Autos / E-Rickshaws)",
                    "from_place": active_city,
                    "to_place": active_city,
                    "distance_km": 25.0,
                    "duration_hours": 1.0,
                    "total_cost": 350.0,
                    "ticket_cost": 0.0,
                    "local_transit_cost": 350.0,
                    "local_vehicle_type": "Shared Auto / E-Rickshaw",
                    "steps": [
                        {"title": f"Local Auto / E-Rickshaw Hops across {active_city}", "time": "Throughout Day", "cost": 350.0, "vehicle": "Shared Auto"}
                    ]
                }

            if transit_details and leg_info:
                transit_details["fare_source"] = leg_info.get("fare_source", "calibrated_model")
                transit_details["fare_currency"] = leg_info.get("fare_currency", "₹")
                transit_details["fare_breakdown"] = leg_info.get("fare_breakdown", {})
                transit_details["seat_status"] = leg_info.get("seat_status", [])
                transit_details["coach_position"] = leg_info.get("coach_position", "")
                transit_details["route_stops"] = leg_info.get("route_stops", [])
                transit_details["live_status"] = leg_info.get("live_status", {})
                transit_details["live_delay_mins"] = leg_info.get("live_delay_mins", 0)
                transit_details["live_status_text"] = leg_info.get("live_status_text", "Scheduled")

            # Schedule sightseeing spots for this day in active_city (user-selected first)
            sorted_day_places = sorted(day_places, key=lambda p: not p.user_selected)
            for idx, p in enumerate(sorted_day_places):
                place_open_mins = self._time_str_to_mins(p.opening_time)
                place_close_mins = self._time_str_to_mins(p.closing_time)

                if current_time_mins < place_open_mins:
                    wait_mins = place_open_mins - current_time_mins
                    feasibility_notes.append(f"Early arrival at {p.name}. Paused {wait_mins} mins for opening at {p.opening_time}.")
                    current_time_mins = place_open_mins

                start_str = self._mins_to_time_str(current_time_mins)
                end_mins = current_time_mins + p.typical_duration_mins
                end_str = self._mins_to_time_str(end_mins)

                is_open = end_mins <= place_close_mins
                base_note = "Open & Validated" if is_open else f"Warning: Exceeds closing time {p.closing_time}"
                status_note = f"⭐ User Selected • {base_note}" if p.user_selected else base_note
                if not is_open:
                    feasibility_notes.append(f"{p.name} closes at {p.closing_time}. Visit window trimmed to match.")

                activities.append(Activity(
                    activity_id=f"ACT-D{day_num}-{idx+1}",
                    place=p,
                    start_time=start_str,
                    end_time=end_str,
                    duration_mins=p.typical_duration_mins,
                    transit_from_prev_mins=20,
                    buffer_mins=DEFAULT_STOP_BUFFER_MINUTES,
                    cost=p.entry_fee_per_person * party_size,
                    is_open=is_open,
                    opening_status_note=status_note
                ))
                current_time_mins = end_mins + DEFAULT_STOP_BUFFER_MINUTES

            # Schedule dinner meal in active_city
            dinner_time = max(current_time_mins, self._time_str_to_mins("20:00"))
            available_city_meals = (dining_by_city.get(active_city) if dining_by_city and active_city in dining_by_city else city_meals) or city_meals
            city_venue = available_city_meals[day_num % len(available_city_meals)] if available_city_meals else Restaurant(
                id=f"RES-{active_city[:3].upper()}", name=f"{active_city} Local Heritage Kitchen", location=active_city,
                cuisine_type="local_cuisine", avg_cost_per_person=350.0, rating=4.5
            )
            meals.append(Meal(
                meal_type="dinner",
                restaurant=city_venue,
                time_slot=f"{self._mins_to_time_str(dinner_time)} - {self._mins_to_time_str(dinner_time + 60)}",
                estimated_cost=city_venue.avg_cost_per_person * party_size
            ))

            # Overnight Stay in active_city
            overnight = None
            stay_cost = 0.0
            if day_num < num_days:
                hotel_for_day = (hotels_by_city.get(active_city) if hotels_by_city and active_city in hotels_by_city else stay) or stay
                stay_cost = hotel_for_day.price_per_night
                overnight = Stay(
                    hotel=hotel_for_day,
                    check_in_date=curr_date,
                    nights=1,
                    total_cost=stay_cost
                )

            # Day Cost Breakdown
            activities_cost = sum(a.cost for a in activities)
            food_cost = sum(m.estimated_cost for m in meals)
            buffer_cost = round((day_transit_cost + activities_cost + food_cost + stay_cost) * 0.05, 2)
            total_day = round(day_transit_cost + activities_cost + food_cost + stay_cost + buffer_cost, 2)

            # Informative Day Title reflecting transport mode
            if is_start_day:
                mode_icon = "🚆" if transit_mode == "train" else "🚌" if transit_mode == "bus" else "🛺" if transit_mode == "shared_cab" else "🚗"
                title = f"Day 1: Depart {route.origin} via {transit_mode.title()} {mode_icon} ➔ Arrive & Explore {active_city}"
            elif is_transition_day:
                mode_icon = "🚆" if transit_mode == "train" else "🚌" if transit_mode == "bus" else "🛺" if transit_mode == "shared_cab" else "🚗"
                title = f"Day {day_num}: {transit_mode.title()} Transit {mode_icon} from {prev_city} ➔ Explore {active_city}"
            elif is_return_day:
                mode_icon = "🚆" if transit_mode == "train" else "🚌" if transit_mode == "bus" else "🛺" if transit_mode == "shared_cab" else "🚗"
                title = f"Day {day_num}: Final Sights in {active_city} & Return Journey via {transit_mode.title()} {mode_icon} to {route.origin}"
            else:
                title = f"Day {day_num}: In-Depth Sights & Experiences in {active_city}"

            day_itinerary = DayItinerary(
                day_number=day_num,
                date=curr_date,
                title=title,
                activities=activities,
                meals=meals,
                overnight_stay=overnight,
                transit_distance_km=round(day_transit_km, 1),
                transit_time_hours=round(day_transit_hours, 2),
                transit_mode=transit_mode,
                transit_details=transit_details,
                day_cost_breakdown={
                    "transport": round(day_transit_cost, 2),
                    "activities": round(activities_cost, 2),
                    "food": round(food_cost, 2),
                    "stay": round(stay_cost, 2),
                    "buffer": round(buffer_cost, 2)
                },
                total_day_cost=total_day,
                feasibility_passed=len([n for n in feasibility_notes if "Warning" in n]) == 0,
                feasibility_notes=feasibility_notes
            )
            days.append(day_itinerary)

        self.log_step(
            recipient="Planner",
            action="schedule_complete",
            payload={"days_scheduled": len(days), "total_activities": sum(len(d.activities) for d in days)},
            notes=f"Successfully built timeline for {len(days)} days covering {', '.join(set(day_cities))} with opening hour synchronizations."
        )

        return days
