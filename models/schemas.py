from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class TravelMode(str, Enum):
    driving = "driving"
    train = "train"
    bus = "bus"
    flight = "flight"
    shared_cab = "shared_cab"

class TransportOption(BaseModel):
    mode: str # "driving", "train", "bus", "shared_cab"
    title: str
    description: str
    base_duration_hours: float
    buffered_duration_hours: float
    delay_buffer_ratio: float
    station_buffer_hours: float = 0.0
    ticket_cost_per_person: float = 0.0
    tickets_total: float = 0.0
    local_shared_transit_cost: float = 0.0
    total_cost: float = 0.0
    departure_hub: str = ""
    arrival_hub: str = ""
    local_vehicle_type: str = ""
    train_number: Optional[str] = None
    train_name: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    available_trains: List[Dict[str, Any]] = Field(default_factory=list)
    flight_number: Optional[str] = None
    airline: Optional[str] = None
    airline_code: Optional[str] = None
    aircraft: Optional[str] = None
    cabin_class: Optional[str] = None
    baggage_allowance: Optional[str] = None
    available_flights: List[Dict[str, Any]] = Field(default_factory=list)
    fare_source: str = "calibrated_model"
    fare_currency: str = "₹"
    fare_breakdown: Dict[str, Any] = Field(default_factory=dict)
    seat_status: List[Dict[str, Any]] = Field(default_factory=list)
    coach_position: Optional[str] = None
    route_stops: List[Dict[str, Any]] = Field(default_factory=list)
    live_status: Optional[Dict[str, Any]] = None
    live_delay_mins: int = 0
    live_status_text: str = "Scheduled"

class InterestType(str, Enum):
    heritage = "heritage"
    nature = "nature"
    food = "food"
    adventure = "adventure"
    religious = "religious"
    shopping = "shopping"
    relaxation = "relaxation"
    scenic = "scenic"

class StayPreference(str, Enum):
    budget_hostel = "budget_hostel"
    standard_hotel = "standard_hotel"
    boutique_resort = "boutique_resort"
    dharmashala = "dharmashala"
    luxury = "luxury"

class FoodPreference(str, Enum):
    roadside_dhaba = "roadside_dhaba"
    vegetarian = "vegetarian"
    local_cuisine = "local_cuisine"
    cafe = "cafe"
    fine_dining = "fine_dining"
    all = "all"

class Coordinates(BaseModel):
    lat: float
    lon: float

class Place(BaseModel):
    id: str
    name: str
    location: str
    coords: Coordinates
    category: str
    interests: List[str] = Field(default_factory=list)
    genre: Optional[str] = None
    source: str = "curated"
    user_selected: bool = False
    typical_duration_mins: int = 90
    entry_fee_per_person: float = 0.0
    rating: float = 4.5
    opening_time: str = "09:00"
    closing_time: str = "18:00"
    closed_days: List[str] = Field(default_factory=list)
    description: str = ""
    image_url: Optional[str] = None

class Hotel(BaseModel):
    id: str
    name: str
    location: str
    coords: Optional[Coordinates] = None
    tier: str = "standard_hotel"
    price_per_night: float
    rating: float = 4.3
    amenities: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    source: str = "curated" # "staying_api" | "google_places" | "osm" | "curated"
    address: Optional[str] = None
    user_selected: bool = False

class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    coords: Optional[Coordinates] = None
    cuisine_type: str
    avg_cost_per_person: float
    rating: float = 4.4
    specialty: str = ""
    is_dhaba: bool = False
    image_url: Optional[str] = None
    source: str = "curated" # "google_places" | "osm" | "curated"
    address: Optional[str] = None
    user_selected: bool = False

class Activity(BaseModel):
    activity_id: str
    place: Place
    start_time: str
    end_time: str
    duration_mins: int
    transit_from_prev_mins: int = 0
    buffer_mins: int = 25
    cost: float = 0.0
    is_open: bool = True
    opening_status_note: str = "Open"
    booked: bool = False

class Meal(BaseModel):
    meal_type: str # "breakfast", "lunch", "dinner", "tea_snack"
    restaurant: Restaurant
    time_slot: str
    estimated_cost: float
    booked: bool = False
    booking_id: Optional[str] = None

class Stay(BaseModel):
    hotel: Hotel
    check_in_date: str
    nights: int = 1
    total_cost: float
    booked: bool = False
    booking_id: Optional[str] = None

class DayWeather(BaseModel):
    temperature_celsius: float
    condition: str
    icon: str
    clothing_packing_advice: List[str] = Field(default_factory=list)
    risk_alert: Optional[str] = None

class DayItinerary(BaseModel):
    day_number: int
    date: str
    title: str
    activities: List[Activity] = Field(default_factory=list)
    meals: List[Meal] = Field(default_factory=list)
    overnight_stay: Optional[Stay] = None
    weather: Optional[DayWeather] = None
    transit_distance_km: float = 0.0
    transit_time_hours: float = 0.0
    transit_mode: str = "driving"
    transit_details: Optional[Dict[str, Any]] = None
    day_cost_breakdown: Dict[str, float] = Field(default_factory=dict)
    total_day_cost: float = 0.0
    feasibility_passed: bool = True
    feasibility_notes: List[str] = Field(default_factory=list)

class StopoverInput(BaseModel):
    location: str
    stay_days: Optional[int] = None # None or 0 = "Not Sure / AI Optimal"
    travel_mode: Optional[str] = None # Optional mode for this leg
    selected_places: List[str] = Field(default_factory=list)
    selected_flight: Optional[str] = None
    selected_hotel_id: Optional[str] = None
    selected_restaurant_ids: List[str] = Field(default_factory=list)

class RouteLeg(BaseModel):
    from_place: str
    to_place: str
    distance_km: float
    duration_hours: float
    buffered_duration_hours: float = 0.0
    estimated_transit_cost: float = 0.0
    geometry: List[Coordinates] = Field(default_factory=list)
    selected_mode: str = "driving"
    available_modes: List[TransportOption] = Field(default_factory=list)
    ticket_cost: float = 0.0
    local_transit_cost: float = 0.0
    departure_hub: str = ""
    arrival_hub: str = ""
    local_vehicle_type: str = ""
    train_number: Optional[str] = None
    train_name: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    available_trains: List[Dict[str, Any]] = Field(default_factory=list)
    flight_number: Optional[str] = None
    airline: Optional[str] = None
    airline_code: Optional[str] = None
    aircraft: Optional[str] = None
    cabin_class: Optional[str] = None
    baggage_allowance: Optional[str] = None
    available_flights: List[Dict[str, Any]] = Field(default_factory=list)
    fare_source: str = "calibrated_model"
    fare_currency: str = "₹"
    fare_breakdown: Dict[str, Any] = Field(default_factory=dict)
    seat_status: List[Dict[str, Any]] = Field(default_factory=list)
    coach_position: Optional[str] = None
    route_stops: List[Dict[str, Any]] = Field(default_factory=list)
    live_status: Optional[Dict[str, Any]] = None
    live_delay_mins: int = 0
    live_status_text: str = "Scheduled"

class RouteOption(BaseModel):
    origin: str
    destination: str
    waypoints: List[str] = Field(default_factory=list)
    legs: List[RouteLeg] = Field(default_factory=list)
    total_distance_km: float
    base_travel_time_hours: float
    buffered_travel_time_hours: float
    estimated_transit_cost: float
    corridor_geometry: List[Coordinates] = Field(default_factory=list)
    selected_mode: str = "driving"
    fare_source: str = "calibrated_model"

class TripInput(BaseModel):
    origin: str = "Delhi"
    destination: str = "Jaipur"
    stopovers: List[StopoverInput] = Field(default_factory=list)
    selected_places: List[str] = Field(default_factory=list)
    places_by_city: Dict[str, List[str]] = Field(default_factory=dict)
    budget: float = 15000.0
    start_date: str = "2026-10-01"
    end_date: str = "2026-10-03"
    travel_mode: TravelMode = TravelMode.driving
    leg_modes: Dict[str, str] = Field(default_factory=dict) # e.g. {"0": "train", "1": "bus"}
    return_travel_mode: Optional[str] = None
    selected_trains: Dict[str, str] = Field(default_factory=dict) # e.g. {"0": "12015"}
    return_train_number: Optional[str] = None
    selected_flights: Dict[str, str] = Field(default_factory=dict) # e.g. {"0": "6E-2381", "return": "AI-492"}
    return_flight_number: Optional[str] = None
    selected_hotel_id: Optional[str] = None
    selected_hotels_by_city: Dict[str, str] = Field(default_factory=dict) # e.g. {"Jaipur": "HTL-JPR-02"}
    selected_restaurant_ids: List[str] = Field(default_factory=list)
    selected_dining_by_city: Dict[str, List[str]] = Field(default_factory=dict) # e.g. {"Jaipur": ["RES-JPR-01"]}
    interests: List[str] = Field(default_factory=lambda: ["heritage", "food", "scenic"])
    food_preference: FoodPreference = FoodPreference.all
    stay_preference: StayPreference = StayPreference.standard_hotel
    party_size: int = 2
    start_time_of_day: str = "07:30"
    buffer_factor: float = 0.18
    google_maps_api_key: Optional[str] = None

class FeasibilityCheck(BaseModel):
    passed: bool = True
    budget_ok: bool = True
    budget_spent: float = 0.0
    budget_limit: float = 0.0
    time_ok: bool = True
    opening_hours_ok: bool = True
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class ItineraryVariant(BaseModel):
    variant_type: str # "balanced", "fastest", "cheapest", "scenic"
    variant_title: str
    tagline: str
    score: float
    total_cost: float
    total_distance_km: float
    total_spots_visited: int
    days: List[DayItinerary] = Field(default_factory=list)
    feasibility: FeasibilityCheck
    highlights: List[str] = Field(default_factory=list)
    cost_summary: Dict[str, float] = Field(default_factory=dict)
    corridor_geometry: List[Coordinates] = Field(default_factory=list)

class TripPlan(BaseModel):
    plan_id: str
    input_params: TripInput
    options: Dict[str, ItineraryVariant]
    route: Optional[RouteOption] = None
    recommended_option: str = "balanced"
    agent_trace: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str

class BookingRequest(BaseModel):
    plan_id: str
    variant_type: str
    item_type: str # "hotel" | "restaurant"
    item_id: str
    date_or_time: str
    guests: int = 1
    user_name: str = "Traveler"
    user_contact: str = ""

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    item_name: str
    item_type: str
    confirmation_code: str
    amount: float
    details: Dict[str, Any] = Field(default_factory=dict)
