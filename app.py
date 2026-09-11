import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
