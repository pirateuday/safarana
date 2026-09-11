from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import Hotel, Restaurant, Stay, Meal, BookingResponse

class FoodStayAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FoodStayAgent",
            role="Hospitality & Dining Specialist",
            description="Finds curated highway dhabas, local culinary spots, and accommodations within budget tier; executes bookings."
        )

    def select_accommodations(self, location: str, stay_tier: str, party_size: int = 2) -> List[Hotel]:
        self.log_step(
            recipient="Planner",
            action="search_hotels",
            payload={"location": location, "tier": stay_tier, "party_size": party_size},
            notes=f"Searching hotels in {location} for {party_size} guests with preference '{stay_tier}'."
        )

        results = self.execute_tool("search_hotels", location=location, budget_tier=stay_tier, party_size=party_size)
        hotels = [
            Hotel(
                id=h["id"],
                name=h["name"],
                location=h["location"],
                tier=h.get("tier", stay_tier),
                price_per_night=h["price_per_night"],
                rating=h.get("rating", 4.3),
                amenities=h.get("amenities", []),
                image_url=h.get("image_url")
            )
            for h in results
        ]

        self.log_step(
            recipient="Planner",
            action="hotels_retrieved",
            payload={"count": len(hotels), "options": [h.name for h in hotels]},
            notes=f"Found {len(hotels)} accommodations. Top match: {hotels[0].name if hotels else 'N/A'}."
        )
        return hotels

    def select_dining_options(self, location: str, food_pref: str, is_highway: bool = False) -> List[Restaurant]:
        search_loc = f"{location} Highway Corridor" if is_highway else location
        self.log_step(
            recipient="Planner",
            action="search_dining",
            payload={"location": search_loc, "preference": food_pref, "is_highway": is_highway},
            notes=f"Looking up {'highway dhabas' if is_highway else 'local restaurants'} for '{food_pref}'."
        )

        results = self.execute_tool("search_restaurants", location=search_loc, cuisine_pref=food_pref)
        restaurants = [
            Restaurant(
                id=r["id"],
                name=r["name"],
                location=r["location"],
                cuisine_type=r.get("cuisine_type", "local"),
                avg_cost_per_person=r["avg_cost_per_person"],
                rating=r.get("rating", 4.4),
                specialty=r.get("specialty", ""),
                is_dhaba=r.get("is_dhaba", False),
                image_url=r.get("image_url")
            )
            for r in results
        ]
        return restaurants

    def book_item(self, item_type: str, item_id: str, date_or_time: str, guests: int, user_name: str = "Traveler", plan_id: str = "") -> BookingResponse:
        self.log_step(
            recipient="Planner",
            action=f"execute_booking_{item_type}",
            payload={"item_id": item_id, "time": date_or_time, "guests": guests, "user": user_name},
            notes=f"Executing confirmed reservation for {item_type} ID: {item_id}."
        )

        if item_type == "hotel":
            res = self.execute_tool("book_hotel", hotel_id=item_id, date=date_or_time, guests=guests, user_name=user_name, plan_id=plan_id)
        else:
            res = self.execute_tool("book_restaurant", restaurant_id=item_id, time_slot=date_or_time, guests=guests, user_name=user_name, plan_id=plan_id)

        response = BookingResponse(
            booking_id=res["booking_id"],
            status=res["status"],
            item_name=res["item_name"],
            item_type=res["item_type"],
            confirmation_code=res["confirmation_code"],
            amount=res["amount"],
            details=res.get("details", {})
        )

        self.log_step(
            recipient="User",
            action="booking_confirmed",
            payload={"booking_id": response.booking_id, "code": response.confirmation_code},
            notes=f"Confirmed reservation for {response.item_name}. Reference code: {response.confirmation_code}."
        )
        return response
