import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = str(BASE_DIR / "smartroute_cache.db")

# Google Maps API Key (provided by user, with env override)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyBD9Cks3UYTRbIOUafiGCCMRImc1VTBPOs")
GOOGLE_PLACES_KEY = os.getenv("GOOGLE_PLACES_KEY", GOOGLE_MAPS_API_KEY)
STAYING_API_KEY = os.getenv("STAYING_API_KEY", "")
FLIGHT_API_KEY = os.getenv("FLIGHT_API_KEY", "")
ORS_API_KEY = os.getenv("ORS_API_KEY", "")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# OSRM Public Routing URL (Free, no key required)
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")

# Planning & Constraint Defaults
DEFAULT_DELAY_BUFFER_RATIO = 0.18    # +18% travel time for traffic and unexpected slowdowns
DEFAULT_STOP_BUFFER_MINUTES = 25     # 25 mins buffer between sequential scheduled activities
MAX_DAILY_TRAVEL_HOURS = 8.0         # Realistic driving limit per day
DEFAULT_CURRENCY = "₹"               # Default Indian Rupee display (or adaptable)
