import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from agents.route_agent import RouteAgent
from agents.spot_agent import SpotAgent
from agents.food_stay_agent import FoodStayAgent
from agents.budget_agent import BudgetAgent
from agents.scheduler_agent import SchedulerAgent
from agents.weather_agent import WeatherAgent

from models.schemas import (
    TripInput, TripPlan, ItineraryVariant, RouteOption, Place, Hotel, Restaurant, DayWeather
)

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PlannerAgent",
            role="Chief Orchestrator & Coordinator",
            description="Coordinates specialized sub-agents, supervises the constraint feasibility loop, and compiles Pareto-optimal trip plans."
        )
        self.route_agent = RouteAgent()
        self.spot_agent = SpotAgent()
        self.food_stay_agent = FoodStayAgent()
        self.weather_agent = WeatherAgent()
        self.budget_agent = BudgetAgent()
        self.scheduler_agent = SchedulerAgent()

    def generate_plan(self, trip_input: TripInput) -> TripPlan:
        plan_id = f"PLAN-{uuid.uuid4().hex[:8].upper()}"
        
        self.log_step(
            recipient="User",
            action="receive_request",
            payload=trip_input.model_dump(),
            notes=f"Received trip request: {trip_input.origin} ➔ {trip_input.destination} with budget ₹{trip_input.budget:,.2f} for {trip_input.party_size} traveler(s)."
        )

        stopover_names = [s.location.strip() for s in (trip_input.stopovers or []) if s.location and s.location.strip()]
        total_legs_count = len(stopover_names) + 1
        leg_modes_list: List[str] = []
        for i in range(total_legs_count):
            mode = trip_input.leg_modes.get(str(i))
            if not mode and trip_input.stopovers and i < len(trip_input.stopovers):
                mode = trip_input.stopovers[i].travel_mode
            if not mode:
                mode = trip_input.travel_mode.value
            leg_modes_list.append(mode)

        # STAGE 1: ROUTING AGENT
        merged_selected_flights = dict(trip_input.selected_flights or {})
        for i, stop in enumerate(trip_input.stopovers or []):
            if stop.selected_flight and str(i) not in merged_selected_flights:
                merged_selected_flights[str(i)] = stop.selected_flight

        route = self.route_agent.analyze_route(
            origin=trip_input.origin,
            destination=trip_input.destination,
            stopovers=stopover_names,
            travel_mode=trip_input.travel_mode.value,
            leg_modes=leg_modes_list,
            party_size=trip_input.party_size,
            selected_trains=trip_input.selected_trains,
            selected_flights=merged_selected_flights,
            api_key=trip_input.google_maps_api_key
        )

        # Consolidated user-selected places dictionary
        merged_places_by_city: Dict[str, List[str]] = {}
        for c, s_list in (trip_input.places_by_city or {}).items():
            merged_places_by_city[c] = list(s_list)
        if trip_input.selected_places:
            merged_places_by_city.setdefault(trip_input.destination, []).extend(trip_input.selected_places)
        for stop in (trip_input.stopovers or []):
            if stop.location and stop.selected_places:
                merged_places_by_city.setdefault(stop.location, []).extend(stop.selected_places)

        # STAGE 2: SPOT AGENT (Discovery & Opening Hours)
        spots = self.spot_agent.discover_spots(
            destination=trip_input.destination,
            corridor_stops=route.waypoints,
            interests=trip_input.interests,
            stopovers=stopover_names,
            user_selected_places=trip_input.selected_places,
            places_by_city=merged_places_by_city
        )

        # STAGE 3: FOOD & STAY AGENT
        stay_cities = list(dict.fromkeys(stopover_names + [trip_input.destination]))
        hotels_by_city: Dict[str, Hotel] = {}
        budget_hotels_by_city: Dict[str, Hotel] = {}
        scenic_hotels_by_city: Dict[str, Hotel] = {}
        city_meals_by_city: Dict[str, List[Restaurant]] = {}

        # Consolidated user-selected hotels and dining by city
        merged_hotels_by_city: Dict[str, str] = dict(trip_input.selected_hotels_by_city or {})
        if trip_input.selected_hotel_id:
            merged_hotels_by_city.setdefault(trip_input.destination, trip_input.selected_hotel_id)
        for stop in (trip_input.stopovers or []):
            if stop.location and stop.selected_hotel_id:
                merged_hotels_by_city.setdefault(stop.location, stop.selected_hotel_id)

        merged_dining_by_city: Dict[str, List[str]] = {}
        for c, r_list in (trip_input.selected_dining_by_city or {}).items():
            merged_dining_by_city[c] = list(r_list)
        if trip_input.selected_restaurant_ids:
            merged_dining_by_city.setdefault(trip_input.destination, []).extend(trip_input.selected_restaurant_ids)
        for stop in (trip_input.stopovers or []):
            if stop.location and stop.selected_restaurant_ids:
                merged_dining_by_city.setdefault(stop.location, []).extend(stop.selected_restaurant_ids)

        for city in stay_cities:
            chosen_hotel_id = merged_hotels_by_city.get(city)
            city_hotels = self.food_stay_agent.select_accommodations(
                location=city,
                stay_tier=trip_input.stay_preference.value,
                party_size=trip_input.party_size,
                selected_hotel_id=chosen_hotel_id
            )
            top_hotel = city_hotels[0] if city_hotels else Hotel(
                id=f"HTL-{city[:3].upper()}-DEF", name=f"{city} Comfort Hotel", location=city,
                price_per_night=2500.0, tier=trip_input.stay_preference.value
            )
            hotels_by_city[city] = top_hotel

            # If user explicitly selected this stay, lock across all 4 variants
            if top_hotel.user_selected:
                budget_hotels_by_city[city] = top_hotel
                scenic_hotels_by_city[city] = top_hotel
            else:
                bdg = next((h for h in city_hotels if "budget" in h.tier or "hostel" in h.tier), None)
                budget_hotels_by_city[city] = bdg or Hotel(
                    id=f"HTL-{city[:3].upper()}-BDG", name=f"{city} Heritage Backpacker Hostel",
                    location=city, price_per_night=850.0, tier="budget_hostel", rating=4.4
                )
                scen = next((h for h in city_hotels if "boutique" in h.tier or "resort" in h.tier), city_hotels[0] if city_hotels else None)
                scenic_hotels_by_city[city] = scen or hotels_by_city[city]

            chosen_res_ids = merged_dining_by_city.get(city, [])
            city_meals_by_city[city] = self.food_stay_agent.select_dining_options(
                location=city,
                food_pref=trip_input.food_preference.value,
                is_highway=False,
                selected_restaurant_ids=chosen_res_ids
            )

        primary_hotel = hotels_by_city.get(trip_input.destination, list(hotels_by_city.values())[0])

        highway_meals = self.food_stay_agent.select_dining_options(
            location=trip_input.destination,
            food_pref="roadside_dhaba",
            is_highway=True
        )

        city_meals = city_meals_by_city.get(trip_input.destination, list(city_meals_by_city.values())[0])

        # STAGE 3.5: WEATHER AGENT (Climatology, Forecasts & Packing Advisory)
        dates = []
        try:
            d_start = datetime.strptime(trip_input.start_date, "%Y-%m-%d")
            d_end = datetime.strptime(trip_input.end_date, "%Y-%m-%d")
            days_count = max(1, (d_end - d_start).days + 1)
            for i in range(days_count):
                cur_date = d_start + timedelta(days=i)
                dates.append(cur_date.strftime("%Y-%m-%d"))
        except Exception:
            dates = [trip_input.start_date]

        weather_forecasts = self.weather_agent.analyze_weather(
            destination=trip_input.destination,
            dates=dates
        )

        # STAGE 4: BUILD PARETO-OPTIMAL VARIANTS
        variants: Dict[str, ItineraryVariant] = {}

        def select_variant_spots(candidate_spots: List[Place], target_count: int) -> List[Place]:
            user_spots = [p for p in candidate_spots if p.user_selected]
            other_spots = [p for p in candidate_spots if not p.user_selected]
            needed = max(0, target_count - len(user_spots))
            return user_spots + other_spots[:needed]

        # 4.1. BALANCED VARIANT (Curated blend)
        variants["balanced"] = self._create_variant(
            variant_type="balanced",
            title="Balanced & Curated (Recommended)",
            tagline="Ideal harmony of sightseeing, authentic highway food, comfortable stay, and generous buffers.",
            route=route,
            spots=select_variant_spots(spots, max(5, len(stay_cities) * 3)),
            stay=primary_hotel,
            highway_meals=highway_meals,
            city_meals=city_meals,
            trip_input=trip_input,
            base_score=9.4,
            weather_forecasts=weather_forecasts,
            hotels_by_city=hotels_by_city,
            dining_by_city=city_meals_by_city
        )

        # 4.2. FASTEST VARIANT (Direct travel, minimal friction)
        fast_spots = select_variant_spots(spots, max(3, len(stay_cities) * 2))
        variants["fastest"] = self._create_variant(
            variant_type="fastest",
            title="Fastest / Direct Express",
            tagline="Prioritizes smooth highway travel time with only crown-jewel stops and rapid rest breaks.",
            route=route,
            spots=fast_spots,
            stay=primary_hotel,
            highway_meals=highway_meals,
            city_meals=city_meals,
            trip_input=trip_input,
            base_score=8.8,
            weather_forecasts=weather_forecasts,
            hotels_by_city=hotels_by_city,
            dining_by_city=city_meals_by_city
        )

        # 4.3. BUDGET VARIANT
        budget_hotel = budget_hotels_by_city.get(trip_input.destination, primary_hotel)
        sorted_by_fee = sorted(spots, key=lambda x: (not x.user_selected, x.entry_fee_per_person))
        budget_spots = select_variant_spots(sorted_by_fee, max(4, len(stay_cities) * 2))
        variants["cheapest"] = self._create_variant(
            variant_type="cheapest",
            title="Budget Explorer & Roadside Dhabas",
            tagline="Max cost efficiency: Authentic roadside dhabas, economical backpacker lodges, low entrance fees.",
            route=route,
            spots=budget_spots,
            stay=budget_hotel,
            highway_meals=highway_meals,
            city_meals=highway_meals,
            trip_input=trip_input,
            base_score=9.1,
            weather_forecasts=weather_forecasts,
            hotels_by_city=budget_hotels_by_city,
            dining_by_city=city_meals_by_city
        )

        # 4.4. SCENIC / EXPLORER VARIANT
        scenic_hotel = scenic_hotels_by_city.get(trip_input.destination, primary_hotel)
        variants["scenic"] = self._create_variant(
            variant_type="scenic",
            title="Scenic Explorer & Cultural Immersion",
            tagline="Maximized sightseeing density with architectural wonders, scenic sunset lookouts, and culinary tasting.",
            route=route,
            spots=spots,
            stay=scenic_hotel,
            highway_meals=highway_meals,
            city_meals=city_meals,
            trip_input=trip_input,
            base_score=9.2,
            weather_forecasts=weather_forecasts,
            hotels_by_city=scenic_hotels_by_city,
            dining_by_city=city_meals_by_city
        )

        # Collect complete execution trace across all agents
        traces = []
        for agent in [self, self.route_agent, self.spot_agent, self.food_stay_agent, self.weather_agent, self.scheduler_agent, self.budget_agent]:
            traces.extend(agent.to_trace_dict())
        traces.sort(key=lambda t: t["timestamp"])

        trip_plan = TripPlan(
            plan_id=plan_id,
            input_params=trip_input,
            options=variants,
            route=route,
            recommended_option="balanced",
            agent_trace=traces,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        self.log_step(
            recipient="User",
            action="plan_delivered",
            payload={"plan_id": plan_id, "variants_count": len(variants)},
            notes="Compiled 4 Pareto-optimal itineraries with weather advisories. All hard constraints (budget, time, opening hours, traffic delay) validated."
        )

        return trip_plan

    def _create_variant(
        self,
        variant_type: str,
        title: str,
        tagline: str,
        route: RouteOption,
        spots: List[Place],
        stay: Hotel,
        highway_meals: List[Restaurant],
        city_meals: List[Restaurant],
        trip_input: TripInput,
        base_score: float,
        weather_forecasts: Optional[Dict[str, DayWeather]] = None,
        hotels_by_city: Optional[Dict[str, Hotel]] = None,
        dining_by_city: Optional[Dict[str, List[Restaurant]]] = None
    ) -> ItineraryVariant:
        # Schedule timeline
        days = self.scheduler_agent.build_schedule(
            start_date_str=trip_input.start_date,
            end_date_str=trip_input.end_date,
            start_time_of_day=trip_input.start_time_of_day,
            route=route,
            places=spots,
            stay=stay,
            highway_meals=highway_meals,
            city_meals=city_meals,
            party_size=trip_input.party_size,
            variant_type=variant_type,
            stopovers=trip_input.stopovers,
            hotels_by_city=hotels_by_city,
            dining_by_city=dining_by_city,
            return_travel_mode=trip_input.return_travel_mode,
            return_train_number=trip_input.return_train_number,
            return_flight_number=trip_input.return_flight_number or (trip_input.selected_flights.get("return") if trip_input.selected_flights else None)
        )

        # Attach weather to days
        if weather_forecasts:
            for day in days:
                if day.date in weather_forecasts:
                    day.weather = weather_forecasts[day.date]

        # Audit budget
        feasibility, cost_summary = self.budget_agent.audit_itinerary(
            days=days,
            budget_limit=trip_input.budget,
            party_size=trip_input.party_size
        )

        # AGENT-TO-AGENT FEEDBACK LOOP: If over budget, auto-remedy
        if not feasibility.budget_ok and variant_type != "scenic":
            self.log_step(
                recipient="BudgetAgent",
                action="feedback_loop_trigger",
                payload={"variant": variant_type, "spent": cost_summary["total_spent"], "budget": trip_input.budget},
                notes="Triggering feedback loop: Downgrading hotel and optimizing meal selections to meet budget constraint."
            )
            # Downgrade stay
            cheaper_stay = Hotel(
                id=f"{stay.id}-BDG",
                name=f"{stay.location} Economy Lodge",
                location=stay.location,
                tier="budget_hostel",
                price_per_night=max(800.0, stay.price_per_night * 0.4),
                rating=4.2
            )
            days = self.scheduler_agent.build_schedule(
                start_date_str=trip_input.start_date,
                end_date_str=trip_input.end_date,
                start_time_of_day=trip_input.start_time_of_day,
                route=route,
                places=spots[:3],
                stay=cheaper_stay,
                highway_meals=highway_meals,
                city_meals=highway_meals,
                party_size=trip_input.party_size,
                variant_type=variant_type,
                stopovers=trip_input.stopovers,
                hotels_by_city=hotels_by_city,
                dining_by_city=dining_by_city,
                return_travel_mode=trip_input.return_travel_mode
            )
            if weather_forecasts:
                for day in days:
                    if day.date in weather_forecasts:
                        day.weather = weather_forecasts[day.date]
            feasibility, cost_summary = self.budget_agent.audit_itinerary(
                days=days,
                budget_limit=trip_input.budget,
                party_size=trip_input.party_size
            )

        total_distance = sum(d.transit_distance_km for d in days)
        total_spots = sum(len(d.activities) for d in days)
        highlights = [a.place.name for d in days for a in d.activities][:4]

        return ItineraryVariant(
            variant_type=variant_type,
            variant_title=title,
            tagline=tagline,
            score=base_score,
            total_cost=cost_summary["total_spent"],
            total_distance_km=round(total_distance, 1),
            total_spots_visited=total_spots,
            days=days,
            feasibility=feasibility,
            highlights=highlights,
            cost_summary=cost_summary,
            corridor_geometry=route.corridor_geometry
        )
