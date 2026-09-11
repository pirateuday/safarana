import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logger = logging.getLogger("smartroute")

from models.schemas import (
    TripInput, TripPlan, BookingRequest, BookingResponse
)
from engine.orchestrator import orchestrator
from tools.cache import cache_db

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="SmartRoute — AI Multi-Agent Trip Planner",
    description="Agentic constraint-solving trip planning engine optimizing budget, time windows, opening hours, and traffic delay buffers.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RefineRequest(BaseModel):
    plan_id: str
    updates: Dict[str, Any]

@app.get("/api/cities")
def get_cities():
    """Returns curated list of Indian cities and regions for manual origin/destination selection."""
    return {"cities": orchestrator.get_available_cities()}

@app.get("/api/presets")
def get_presets():
    """Returns curated preset corridors for instant 1-click planning."""
    return {"presets": orchestrator.get_preset_trips()}

@app.get("/api/trains")
def get_trains(origin: str, destination: str, date: Optional[str] = None):
    """Retrieves live or cached trains between two cities/stations using RailRadar API with mock fallback."""
    from tools.railway_tools import get_trains_between
    try:
        trains = get_trains_between(origin, destination, travel_date=date)
        return {
            "origin": origin,
            "destination": destination,
            "date": date,
            "count": len(trains),
            "trains": trains
        }
    except Exception as e:
        logger.error(f"Error fetching trains: {e}")
        return {"origin": origin, "destination": destination, "date": date, "count": 0, "trains": []}

@app.get("/api/maps/status")
def get_maps_status():
    """Returns the live status of Google Maps API and key configuration."""
    from tools.google_maps_tools import get_google_maps_status
    return get_google_maps_status()

@app.post("/api/maps/key")
def update_maps_key(data: Dict[str, str]):
    """Updates or sets the Google Maps API key dynamically."""
    import config
    from tools.google_maps_tools import api_status_info
    key = data.get("key", "").strip()
    if key:
        config.GOOGLE_MAPS_API_KEY = key
        api_status_info["key_configured"] = True
        return {"success": True, "message": "Google Maps API Key updated successfully"}
    return {"success": False, "message": "No key provided"}

@app.get("/api/trains/{train_number}/details")
def get_train_timetable_details(train_number: str):
    """Returns actual timetable halts, coach position, classes, and seat availability for a train."""
    from tools.railway_tools import get_train_full_details
    try:
        details = get_train_full_details(train_number)
        return {"success": True, "details": details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch train details: {str(e)}")

@app.get("/api/trains/{train_number}/live")
def get_train_live_tracking(train_number: str):
    """Returns live running delay, current station location, and status for a train."""
    from tools.railway_tools import get_train_live_status
    try:
        status = get_train_live_status(train_number)
        return {"success": True, "live": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch train live status: {str(e)}")

@app.get("/api/spots")
def get_spots(city: str, genre: Optional[str] = None):
    """Retrieves list of tourist spots, genres, timings, and entry fees from OpenStreetMap / Overpass / OpenTripMap / Curated database."""
    from tools.poi_tools import get_city_spots
    try:
        spots = get_city_spots(city_name=city, genre_filter=genre)
        return {
            "city": city,
            "genre": genre,
            "count": len(spots),
            "spots": spots
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spots: {str(e)}")

@app.get("/api/flights")
def get_flights(origin: str, destination: str, date: Optional[str] = None):
    """Retrieves commercial domestic flight schedules, fares, classes, and seat availability."""
    from tools.flight_tools import get_flights_between
    try:
        flights = get_flights_between(origin, destination, travel_date=date)
        return {
            "origin": origin,
            "destination": destination,
            "date": date,
            "count": len(flights),
            "flights": flights
        }
    except Exception as e:
        logger.error(f"Error fetching flights: {e}")
        return {"origin": origin, "destination": destination, "date": date, "count": 0, "flights": []}

@app.get("/api/flights/{flight_number}")
def get_flight_info(flight_number: str, origin: Optional[str] = None, destination: Optional[str] = None):
    """Retrieves flight information and seat/fare status for a specific flight."""
    from tools.flight_tools import get_flight_details
    details = get_flight_details(flight_number, origin, destination)
    if not details:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"success": True, "flight": details}

@app.get("/api/hotels")
def get_hotels(city: str, tier: Optional[str] = None):
    """Aggregates hotels from StayingAPI, Google Places, OpenStreetMap, and Curated catalog."""
    from tools.hospitality_tools import get_city_hotels
    try:
        hotels = get_city_hotels(city_name=city, stay_tier=tier)
        return {
            "city": city,
            "tier": tier,
            "count": len(hotels),
            "hotels": hotels
        }
    except Exception as e:
        logger.error(f"Error fetching hotels for {city}: {e}")
        return {"city": city, "tier": tier, "count": 0, "hotels": []}

@app.get("/api/restaurants")
def get_restaurants(city: str, cuisine: Optional[str] = None, is_highway: bool = False):
    """Aggregates food places & dhabas from Google Places, OpenStreetMap, and Curated catalog."""
    from tools.hospitality_tools import get_city_restaurants
    try:
        restaurants = get_city_restaurants(city_name=city, cuisine_pref=cuisine or "all", is_highway=is_highway)
        return {
            "city": city,
            "cuisine": cuisine,
            "count": len(restaurants),
            "restaurants": restaurants
        }
    except Exception as e:
        logger.error(f"Error fetching restaurants for {city}: {e}")
        return {"city": city, "cuisine": cuisine, "count": 0, "restaurants": []}

@app.post("/api/plan", response_model=TripPlan)
def plan_trip(trip_input: TripInput):
    """Executes the multi-agent planning pipeline to generate 4 Pareto-optimal itineraries."""
    try:
        plan = orchestrator.generate_trip(trip_input)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning pipeline failed: {str(e)}")

@app.get("/api/plan/{plan_id}", response_model=TripPlan)
def get_trip_plan(plan_id: str):
    """Retrieves an existing cached trip plan."""
    plan = orchestrator.get_trip(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Trip plan not found")
    return plan

@app.get("/api/plan/{plan_id}/export/ics")
def export_plan_ics(plan_id: str, variant: str = "balanced"):
    """Exports the optimized itinerary as standard iCalendar (.ics) for Google/Apple Calendar."""
    try:
        ics_data = orchestrator.export_icalendar(plan_id, variant)
        filename = f"smartroute_{plan_id.lower()}_{variant}.ics"
        return Response(
            content=ics_data,
            media_type="text/calendar",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export calendar: {str(e)}")

@app.post("/api/refine", response_model=TripPlan)
def refine_trip(req: RefineRequest):
    """Interactively refines an existing plan with updated budget, dates, or preferences."""
    try:
        new_plan = orchestrator.refine_trip(req.plan_id, req.updates)
        return new_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@app.post("/api/book", response_model=BookingResponse)
def book_item(req: BookingRequest):
    """Simulates a confirmed reservation for a hotel or dining table."""
    try:
        res = orchestrator.book_item(req)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")

@app.get("/api/bookings")
def list_bookings(plan_id: Optional[str] = None):
    """Lists confirmed bookings and vouchers."""
    bookings = cache_db.list_bookings(plan_id=plan_id)
    return {"bookings": bookings}

# Mount static web frontend
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
