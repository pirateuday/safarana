from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from agents.planner_agent import PlannerAgent
from models.schemas import TripInput, TripPlan, BookingRequest, BookingResponse
from engine.optimizer import ParetoOptimizer
from tools.cache import cache_db
from tools.routing_tools import get_city_catalog

# Active in-memory plan cache for quick retrieval & refinement
PLAN_REGISTRY: Dict[str, TripPlan] = {}

class TripOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()

    def generate_trip(self, trip_input: TripInput) -> TripPlan:
        # Run multi-agent planning pipeline
        plan = self.planner.generate_plan(trip_input)

        # Calculate comparative Pareto score matrix
        score_matrix = ParetoOptimizer.calculate_scores(plan.options, trip_input.budget)
        for opt_key, scores in score_matrix.items():
            if opt_key in plan.options:
                plan.options[opt_key].score = scores["composite"]

        # Cache plan
        PLAN_REGISTRY[plan.plan_id] = plan
        return plan

    def get_trip(self, plan_id: str) -> Optional[TripPlan]:
        return PLAN_REGISTRY.get(plan_id)

    def refine_trip(self, plan_id: str, updates: Dict[str, Any]) -> TripPlan:
        existing = self.get_trip(plan_id)
        current_input = existing.input_params if existing else TripInput()

        # Apply updates onto input
        input_data = current_input.model_dump()
        for k, v in updates.items():
            if v is not None and k in input_data:
                input_data[k] = v

        refined_input = TripInput(**input_data)

        # Log interactive user refinement
        self.planner.log_step(
            recipient="Planner",
            action="user_refinement_request",
            payload=updates,
            notes=f"User requested itinerary refinement: {', '.join([f'{k}={v}' for k, v in updates.items() if v is not None])}"
        )

        new_plan = self.generate_trip(refined_input)
        return new_plan

    def book_item(self, req: BookingRequest) -> BookingResponse:
        return self.planner.food_stay_agent.book_item(
            item_type=req.item_type,
            item_id=req.item_id,
            date_or_time=req.date_or_time,
            guests=req.guests,
            user_name=req.user_name,
            plan_id=req.plan_id
        )

    def get_available_cities(self) -> List[Dict[str, Any]]:
        """Returns catalog of curated Indian cities for manual origin/destination selection."""
        return get_city_catalog()

    def get_preset_trips(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "delhi-jaipur",
                "title": "Delhi to Jaipur Royal Corridor",
                "origin": "Delhi",
                "destination": "Jaipur",
                "budget": 16000.0,
                "days": 3,
                "mode": "driving",
                "interests": ["heritage", "food", "scenic"],
                "food_pref": "roadside_dhaba",
                "stay_pref": "standard_hotel",
                "party_size": 2,
                "highlights": "Old Rao Dhaba parathas, Neemrana Fort, Amber Palace, Nahargarh Sunset"
            },
            {
                "id": "mumbai-goa",
                "title": "Mumbai to Goa Coastal Expressway",
                "origin": "Mumbai",
                "destination": "Goa",
                "budget": 28000.0,
                "days": 4,
                "mode": "driving",
                "interests": ["nature", "relaxation", "food"],
                "food_pref": "local_cuisine",
                "stay_pref": "boutique_resort",
                "party_size": 2,
                "highlights": "Lonavala Ghats, Kolhapur Misal stop, Aguada Fort, Anjuna Beach"
            },
            {
                "id": "bangalore-coorg",
                "title": "Bangalore to Coorg Coffee Trails",
                "origin": "Bangalore",
                "destination": "Coorg",
                "budget": 14000.0,
                "days": 3,
                "mode": "driving",
                "interests": ["nature", "scenic", "heritage"],
                "food_pref": "all",
                "stay_pref": "standard_hotel",
                "party_size": 2,
                "highlights": "Mysore Royal Palace, Abbey Falls, Coffee Plantations, Kushalnagar"
            },
            {
                "id": "delhi-agra",
                "title": "Delhi to Agra Taj Weekend",
                "origin": "Delhi",
                "destination": "Agra",
                "budget": 12000.0,
                "days": 2,
                "mode": "driving",
                "interests": ["heritage", "food", "shopping"],
                "food_pref": "vegetarian",
                "stay_pref": "standard_hotel",
                "party_size": 2,
                "highlights": "Taj Mahal sunrise, Fatehpur Sikri, Mathura peda stop, Vrindavan temples"
            },
            {
                "id": "chandigarh-manali",
                "title": "Chandigarh to Manali Himalayan Drive",
                "origin": "Chandigarh",
                "destination": "Manali",
                "budget": 18000.0,
                "days": 3,
                "mode": "driving",
                "interests": ["nature", "scenic", "adventure"],
                "food_pref": "local_cuisine",
                "stay_pref": "boutique_resort",
                "party_size": 2,
                "highlights": "Hadimba Temple, Solang Valley, Old Manali cafes, Kullu panorama"
            },
            {
                "id": "delhi-rishikesh",
                "title": "Delhi to Rishikesh Ganga Spiritual Trail",
                "origin": "Delhi",
                "destination": "Rishikesh",
                "budget": 12000.0,
                "days": 2,
                "mode": "driving",
                "interests": ["religious", "heritage", "nature"],
                "food_pref": "cafe",
                "stay_pref": "standard_hotel",
                "party_size": 2,
                "highlights": "Har Ki Pauri Ganga Aarti, Laxman Jhula, Triveni Ghat, ashram visit"
            },
            {
                "id": "jaipur-udaipur",
                "title": "Jaipur to Udaipur Royal Lakes Circuit",
                "origin": "Jaipur",
                "destination": "Udaipur",
                "budget": 16000.0,
                "days": 3,
                "mode": "driving",
                "interests": ["heritage", "scenic", "relaxation"],
                "food_pref": "vegetarian",
                "stay_pref": "boutique_resort",
                "party_size": 2,
                "highlights": "City Palace, Lake Pichola boat, Chittorgarh Fort, Mewar thali"
            },
            {
                "id": "bangalore-ooty",
                "title": "Bangalore to Ooty Blue Mountains",
                "origin": "Bangalore",
                "destination": "Ooty",
                "budget": 20000.0,
                "days": 3,
                "mode": "driving",
                "interests": ["nature", "scenic", "heritage"],
                "food_pref": "local_cuisine",
                "stay_pref": "boutique_resort",
                "party_size": 2,
                "highlights": "Botanical Gardens, Doddabetta Peak, Bandipur reserve, Mysore Palace"
            },
            {
                "id": "chennai-pondicherry",
                "title": "Chennai to Pondicherry ECR Coastal Drive",
                "origin": "Chennai",
                "destination": "Pondicherry",
                "budget": 14000.0,
                "days": 2,
                "mode": "driving",
                "interests": ["heritage", "scenic", "relaxation"],
                "food_pref": "local_cuisine",
                "stay_pref": "standard_hotel",
                "party_size": 2,
                "highlights": "Mahabalipuram Shore Temple, Auroville Matrimandir, White Town French villas, ECR seafood"
            },
            {
                "id": "kolkata-darjeeling",
                "title": "Kolkata to Darjeeling Himalayan Sunrise",
                "origin": "Kolkata",
                "destination": "Darjeeling",
                "budget": 22000.0,
                "days": 4,
                "mode": "train",
                "interests": ["scenic", "nature", "heritage"],
                "food_pref": "local_cuisine",
                "stay_pref": "boutique_resort",
                "party_size": 2,
                "highlights": "Tiger Hill Kanchenjunga sunrise, Batasia Loop toy train, Happy Valley Tea Estate, Glenary's"
            },
            {
                "id": "pune-mahabaleshwar",
                "title": "Pune to Mahabaleshwar Western Ghats Vista",
                "origin": "Pune",
                "destination": "Mahabaleshwar",
                "budget": 13000.0,
                "days": 2,
                "mode": "driving",
                "interests": ["scenic", "nature", "food"],
                "food_pref": "roadside_dhaba",
                "stay_pref": "standard_hotel",
                "party_size": 2,
                "highlights": "Arthur's Seat canyon view, Mapro Garden strawberry farm, Table Land plateau, Wai dhabas"
            }
        ]

    def export_icalendar(self, plan_id: str, variant_type: str = "balanced") -> str:
        """Generates standard RFC 5545 iCalendar (.ics) format for Google/Apple Calendar integration."""
        plan = self.get_trip(plan_id)
        if not plan:
            raise ValueError(f"Trip plan '{plan_id}' not found")

        variant = plan.options.get(variant_type, plan.options.get("balanced"))
        if not variant:
            raise ValueError(f"Variant '{variant_type}' not found for plan '{plan_id}'")

        now_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//SmartRoute AI Multi-Agent Trip Planner//NONSGML v1.0//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:SmartRoute: {plan.input_params.origin} to {plan.input_params.destination} ({variant.variant_title})",
            f"X-WR-CALDESC:AI-optimized {len(variant.days)}-day itinerary with traffic delay buffers and operating window alignment.",
        ]

        event_counter = 1
        for day in variant.days:
            clean_date = day.date.replace("-", "")

            # Schedule activities
            for act in day.activities:
                start_clean = act.start_time.replace(":", "") + "00"
                end_clean = act.end_time.replace(":", "") + "00"
                uid = f"EVENT-{plan_id}-{clean_date}-{event_counter:03d}@smartroute.ai"
                event_counter += 1

                lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{now_str}",
                    f"DTSTART:{clean_date}T{start_clean}",
                    f"DTEND:{clean_date}T{end_clean}",
                    f"SUMMARY:{act.place.name}",
                    f"DESCRIPTION:Sightseeing visit ({act.duration_mins} mins). Status: {act.opening_status_note}. Fee: INR {act.cost:.0f}. {act.place.description}",
                    f"LOCATION:{act.place.name}, {act.place.location}",
                    "STATUS:CONFIRMED",
                    "END:VEVENT"
                ])

            # Schedule meals
            for meal in day.meals:
                times = meal.time_slot.split(" - ")
                start_clean = (times[0].strip().replace(":", "") + "00") if times else "130000"
                end_clean = (times[1].strip().replace(":", "") + "00") if len(times) > 1 else "140000"
                uid = f"MEAL-{plan_id}-{clean_date}-{event_counter:03d}@smartroute.ai"
                event_counter += 1

                lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{now_str}",
                    f"DTSTART:{clean_date}T{start_clean}",
                    f"DTEND:{clean_date}T{end_clean}",
                    f"SUMMARY:{meal.meal_type.title()} at {meal.restaurant.name}",
                    f"DESCRIPTION:Cuisine: {meal.restaurant.cuisine_type}. Specialty: {meal.restaurant.specialty}. Est cost: INR {meal.estimated_cost:.0f}.",
                    f"LOCATION:{meal.restaurant.name}, {meal.restaurant.location}",
                    "STATUS:CONFIRMED",
                    "END:VEVENT"
                ])

            # Schedule overnight stay check-in
            if day.overnight_stay:
                uid = f"STAY-{plan_id}-{clean_date}-{event_counter:03d}@smartroute.ai"
                event_counter += 1
                lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{now_str}",
                    f"DTSTART:{clean_date}T190000",
                    f"DTEND:{clean_date}T220000",
                    f"SUMMARY:Overnight Stay: {day.overnight_stay.hotel.name}",
                    f"DESCRIPTION:Hotel check-in ({day.overnight_stay.hotel.tier}). Rating: {day.overnight_stay.hotel.rating}/5. Price: INR {day.overnight_stay.total_cost:.0f}.",
                    f"LOCATION:{day.overnight_stay.hotel.name}, {day.overnight_stay.hotel.location}",
                    "STATUS:CONFIRMED",
                    "END:VEVENT"
                ])

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)

orchestrator = TripOrchestrator()
