import math
import requests
from typing import List, Dict, Tuple, Optional, Any
from tools.registry import tool
from tools.cache import cache_db
from config import OSRM_BASE_URL, DEFAULT_DELAY_BUFFER_RATIO
from models.schemas import Coordinates, RouteOption, RouteLeg, TransportOption
from tools.google_maps_tools import (
    get_google_directions,
    calculate_transport_fare,
    decode_polyline,
    get_google_maps_status
)
from tools.railway_tools import (
    get_trains_between,
    get_train_route_geometry,
    get_train_live_status,
    get_train_full_details
)
from tools.flight_tools import (
    calculate_flight_transit,
    get_flights_between,
    get_flight_details
)

# Curated High-Reliability Geocodes for Instant Response & Offline Fallback
KNOWN_CITIES: Dict[str, Tuple[float, float]] = {
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "jaipur": (26.9124, 75.7873),
    "agra": (27.1767, 78.0081),
    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "goa": (15.2993, 74.1240),
    "panaji": (15.4909, 73.8278),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "mysore": (12.2958, 76.6394),
    "mysuru": (12.2958, 76.6394),
    "coorg": (12.3375, 75.8069),
    "ooty": (11.4102, 76.6950),
    "udaipur": (24.5854, 73.7125),
    "chandigarh": (30.7333, 76.7794),
    "shimla": (31.1048, 77.1734),
    "manali": (32.2432, 77.1892),
    "rishikesh": (30.0869, 78.2676),
    "haridwar": (29.9457, 78.1642),
    "varanasi": (25.3176, 82.9739),
    "ahmedabad": (23.0225, 72.5714),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "gurgaon": (28.4595, 77.0266),
    "gurugram": (28.4595, 77.0266),
    "neemrana": (27.9888, 76.3883),
    "behror": (27.8872, 76.2808),
    "shahpura": (27.3917, 75.9614),
    "faridabad": (28.4089, 77.3178),
    "palwal": (28.1498, 77.3257),
    "mathura": (27.4924, 77.6737),
    "vrindavan": (27.5793, 77.6853),
    "fatehpur sikri": (27.0911, 77.6673),
    "bilaspur": (31.3308, 76.7568),
    "mandi": (31.7087, 76.9312),
    "kullu": (31.9592, 77.1089),
    "roorkee": (29.8543, 77.8883),
    "nayidwar": (29.9741, 78.1397),
    "ajmer": (26.4499, 74.6399),
    "beawar": (26.1012, 74.3202),
    "chittorgarh": (24.8797, 74.6259),
    "nanjangud": (12.1216, 76.6841),
    "bandipur": (11.6424, 76.5363),
    "mudumalai": (11.5710, 76.6292),
    "lonavala": (18.7557, 73.4091),
    "khandala": (18.7614, 73.3742),
    "satara": (17.6805, 73.9926),
    "kolhapur": (16.7050, 74.2433),
    "belgaum": (15.8497, 74.4977),
    "pondicherry": (11.9416, 79.8083),
    "puducherry": (11.9416, 79.8083),
    "mahabalipuram": (12.6269, 80.1927),
    "mamallapuram": (12.6269, 80.1927),
    "kalpakkam": (12.5023, 80.1557),
    "marakkanam": (12.1974, 79.9547),
    "darjeeling": (27.0410, 88.2663),
    "siliguri": (26.7271, 88.3953),
    "kurseong": (26.8817, 88.2778),
    "malda": (25.0108, 88.1411),
    "mahabaleshwar": (17.9307, 73.6477),
    "panchgani": (17.9237, 73.8016),
    "wai": (17.9472, 73.8920),
    "shirwal": (18.1362, 73.9856),
}

CITY_CATALOG: List[Dict[str, Any]] = [
    # Metros & Major Hubs
    {"name": "Delhi", "category": "Metros & Hubs", "state": "Delhi NCR", "lat": 28.6139, "lon": 77.2090, "popular_origin": True},
    {"name": "Mumbai", "category": "Metros & Hubs", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "popular_origin": True},
    {"name": "Bangalore", "category": "Metros & Hubs", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "popular_origin": True},
    {"name": "Kolkata", "category": "Metros & Hubs", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639, "popular_origin": True},
    {"name": "Chennai", "category": "Metros & Hubs", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707, "popular_origin": True},
    {"name": "Hyderabad", "category": "Metros & Hubs", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "popular_origin": True},
    {"name": "Pune", "category": "Metros & Hubs", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567, "popular_origin": True},
    {"name": "Ahmedabad", "category": "Metros & Hubs", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714, "popular_origin": True},
    {"name": "Chandigarh", "category": "Metros & Hubs", "state": "Punjab / Haryana", "lat": 30.7333, "lon": 76.7794, "popular_origin": True},

    # Heritage & Culture
    {"name": "Jaipur", "category": "Heritage & Culture", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873, "popular_dest": True},
    {"name": "Agra", "category": "Heritage & Culture", "state": "Uttar Pradesh", "lat": 27.1767, "lon": 78.0081, "popular_dest": True},
    {"name": "Udaipur", "category": "Heritage & Culture", "state": "Rajasthan", "lat": 24.5854, "lon": 73.7125, "popular_dest": True},
    {"name": "Mysore", "category": "Heritage & Culture", "state": "Karnataka", "lat": 12.2958, "lon": 76.6394, "popular_dest": True},
    {"name": "Varanasi", "category": "Heritage & Culture", "state": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739, "popular_dest": True},
    {"name": "Ajmer", "category": "Heritage & Culture", "state": "Rajasthan", "lat": 26.4499, "lon": 74.6399, "popular_dest": False},
    {"name": "Chittorgarh", "category": "Heritage & Culture", "state": "Rajasthan", "lat": 24.8797, "lon": 74.6259, "popular_dest": False},
    {"name": "Fatehpur Sikri", "category": "Heritage & Culture", "state": "Uttar Pradesh", "lat": 27.0911, "lon": 77.6673, "popular_dest": False},

    # Hill Stations & Nature
    {"name": "Manali", "category": "Hill Stations & Nature", "state": "Himachal Pradesh", "lat": 32.2432, "lon": 77.1892, "popular_dest": True},
    {"name": "Shimla", "category": "Hill Stations & Nature", "state": "Himachal Pradesh", "lat": 31.1048, "lon": 77.1734, "popular_dest": True},
    {"name": "Ooty", "category": "Hill Stations & Nature", "state": "Tamil Nadu", "lat": 11.4102, "lon": 76.6950, "popular_dest": True},
    {"name": "Coorg", "category": "Hill Stations & Nature", "state": "Karnataka", "lat": 12.3375, "lon": 75.8069, "popular_dest": True},
    {"name": "Darjeeling", "category": "Hill Stations & Nature", "state": "West Bengal", "lat": 27.0410, "lon": 88.2663, "popular_dest": True},
    {"name": "Mahabaleshwar", "category": "Hill Stations & Nature", "state": "Maharashtra", "lat": 17.9307, "lon": 73.6477, "popular_dest": True},
    {"name": "Kullu", "category": "Hill Stations & Nature", "state": "Himachal Pradesh", "lat": 31.9592, "lon": 77.1089, "popular_dest": False},
    {"name": "Panchgani", "category": "Hill Stations & Nature", "state": "Maharashtra", "lat": 17.9237, "lon": 73.8016, "popular_dest": False},

    # Coastal & Beaches
    {"name": "Goa", "category": "Coastal & Beaches", "state": "Goa", "lat": 15.2993, "lon": 74.1240, "popular_dest": True},
    {"name": "Pondicherry", "category": "Coastal & Beaches", "state": "Puducherry", "lat": 11.9416, "lon": 79.8083, "popular_dest": True},
    {"name": "Mahabalipuram", "category": "Coastal & Beaches", "state": "Tamil Nadu", "lat": 12.6269, "lon": 80.1927, "popular_dest": False},

    # Spiritual & Pilgrimage
    {"name": "Rishikesh", "category": "Spiritual & Pilgrimage", "state": "Uttarakhand", "lat": 30.0869, "lon": 78.2676, "popular_dest": True},
    {"name": "Haridwar", "category": "Spiritual & Pilgrimage", "state": "Uttarakhand", "lat": 29.9457, "lon": 78.1642, "popular_dest": True},
    {"name": "Mathura", "category": "Spiritual & Pilgrimage", "state": "Uttar Pradesh", "lat": 27.4924, "lon": 77.6737, "popular_dest": False},
    {"name": "Vrindavan", "category": "Spiritual & Pilgrimage", "state": "Uttar Pradesh", "lat": 27.5793, "lon": 77.6853, "popular_dest": False},
]

def get_city_catalog() -> List[Dict[str, Any]]:
    """Returns the list of curated cities for manual origin/destination selection."""
    return CITY_CATALOG

def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """Calculates great-circle distance between two points in kilometers."""
    R = 6371.0
    dlat = math.radians(coord2.lat - coord1.lat)
    dlon = math.radians(coord2.lon - coord1.lon)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(coord1.lat)) * math.cos(math.radians(coord2.lat)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@tool(name="get_coordinates", description="Get latitude and longitude for a city or place name.")
def get_coordinates(place_name: str) -> Coordinates:
    clean_name = place_name.strip().lower()
    if clean_name in KNOWN_CITIES:
        lat, lon = KNOWN_CITIES[clean_name]
        return Coordinates(lat=lat, lon=lon)

    # Check cache
    cached = cache_db.get("geocode", clean_name)
    if cached:
        return Coordinates(lat=cached["lat"], lon=cached["lon"])

    # Query Nominatim API with timeout & user-agent
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "SmartRoute-AITripPlanner/1.0"}
        params = {"q": place_name, "format": "json", "limit": 1}
        resp = requests.get(url, params=params, headers=headers, timeout=3.0)
        if resp.status_code == 200 and resp.json():
            item = resp.json()[0]
            lat = float(item["lat"])
            lon = float(item["lon"])
            cache_db.set("geocode", clean_name, {"lat": lat, "lon": lon})
            return Coordinates(lat=lat, lon=lon)
    except Exception:
        pass

    # Default fallback: approximate coordinates near Delhi or center
    return Coordinates(lat=28.6139, lon=77.2090)

def get_transport_hubs(city: str) -> Dict[str, str]:
    """Provides realistic railway stations, bus stands, and cab stands for Indian cities."""
    c = city.strip().title()
    rail_hubs = {
        "Delhi": "New Delhi Railway Station (NDLS)",
        "New Delhi": "New Delhi Railway Station (NDLS)",
        "Jaipur": "Jaipur Junction (JP)",
        "Agra": "Agra Cantt Railway Station (AGC)",
        "Mumbai": "CSMT / Dadar Terminus",
        "Pune": "Pune Junction (PUNE)",
        "Bangalore": "KSR Bengaluru City Junction (SBC)",
        "Bengaluru": "KSR Bengaluru City Junction (SBC)",
        "Mysore": "Mysuru Junction (MYS)",
        "Mysuru": "Mysuru Junction (MYS)",
        "Varanasi": "Varanasi Junction (BSB)",
        "Chandigarh": "Chandigarh Junction (CDG)",
        "Goa": "Madgaon Junction (MAO)",
        "Panaji": "Karmali / Thivim Railway Station",
        "Chennai": "Chennai Central (MAS)",
        "Hyderabad": "Secunderabad Junction (SC)",
        "Ahmedabad": "Ahmedabad Junction (ADI)",
        "Kolkata": "Howrah Junction (HWH)",
        "Haridwar": "Haridwar Junction (HW)",
        "Rishikesh": "Yog Nagari Rishikesh (YNRK)",
        "Udaipur": "Udaipur City Railway Station (UDZ)",
        "Neemrana": "Rewari / Bawal Junction",
        "Behror": "Narnaul / Rewari Station",
        "Mathura": "Mathura Junction (MTJ)",
        "Shimla": "Shimla Railway Station (SML)",
        "Manali": "Joginder Nagar / Chandigarh Hub",
        "Ooty": "Udagamandalam / Mettupalayam (MTP)",
        "Coorg": "Mysuru Junction (Rail-Head for Coorg)"
    }
    bus_hubs = {
        "Delhi": "Kashmere Gate ISBT / Sarai Kale Khan",
        "New Delhi": "Kashmere Gate ISBT",
        "Jaipur": "Sindhi Camp Central Bus Stand",
        "Agra": "Idgah Inter-State Bus Stand",
        "Mumbai": "Mumbai Central MSRTC Stand",
        "Pune": "Shivajinagar Bus Stand",
        "Bangalore": "Majestic Kempegowda Bus Station",
        "Bengaluru": "Majestic Kempegowda Bus Station",
        "Mysore": "KSRTC Central Suburb Bus Stand",
        "Mysuru": "KSRTC Central Suburb Bus Stand",
        "Varanasi": "Varanasi Cantt Bus Depot",
        "Chandigarh": "ISBT Sector 43 Chandigarh",
        "Goa": "Panaji KSRTC / Kadamba Bus Stand",
        "Panaji": "Panaji Kadamba Bus Terminal",
        "Chennai": "CMBT Koyambedu Bus Terminus",
        "Hyderabad": "MGBS Mahatma Gandhi Bus Station",
        "Ahmedabad": "Gita Mandir Central Bus Stand",
        "Kolkata": "Esplanade Central Bus Terminus",
        "Haridwar": "Haridwar Roadways Bus Stand",
        "Rishikesh": "Rishikesh Sanyukta Yatra Bus Stand",
        "Udaipur": "Udaipur Central Bus Stand (Udiapole)",
        "Neemrana": "Neemrana Highway Bus Bay",
        "Behror": "Behror Midway Bus Bay",
        "Mathura": "Mathura ISBT Stand",
        "Shimla": "ISBT Tutikandi Shimla",
        "Manali": "Private / HRTC Bus Stand Manali",
        "Ooty": "Ooty Central Bus Stand",
        "Coorg": "Madikeri KSRTC Bus Stand"
    }
    return {
        "rail": rail_hubs.get(c, f"{c} Railway Junction"),
        "bus": bus_hubs.get(c, f"{c} Central Bus Stand (ISBT)"),
        "cab": f"{c} City Hub / Shared Stand"
    }

def calculate_transit_options(
    origin: str,
    destination: str,
    dist_km: float,
    party_size: int = 1,
    selected_train_number: Optional[str] = None,
    selected_flight_number: Optional[str] = None,
    google_data: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    """Calculates comparative travel options for Driving, Train, Bus, and Shared Cab with Google Maps API fares, RailRadar seat availability, and local shared vehicles."""
    orig_hubs = get_transport_hubs(origin)
    dest_hubs = get_transport_hubs(destination)
    effective_dist = max(15.0, dist_km)
    party_size = max(1, party_size)

    # 1. Driving (Personal / Self-Drive Car)
    car_speed = 55.0
    car_base_hours = round(effective_dist / car_speed, 2)
    car_delay_ratio = 0.18
    car_buffered_hours = round(car_base_hours * (1.0 + car_delay_ratio), 2)
    if google_data and google_data.get("mode") == "driving":
        if google_data.get("duration_hours"):
            car_base_hours = google_data["duration_hours"]
        if google_data.get("traffic_duration_hours"):
            car_buffered_hours = google_data["traffic_duration_hours"]

    car_fare_calc = calculate_transport_fare(effective_dist, "driving", party_size=party_size)
    car_total_cost = car_fare_calc["total_cost"]

    # 2. Train (Express Intercity Rail via RailRadar API / high-fidelity fallback)
    train_speed = 72.0
    train_base_hours = round(effective_dist / train_speed, 2)
    train_delay_ratio = 0.12
    station_buffer_hours = 0.67 # 40 mins station arrival, platform security & boarding
    train_local_transfer_hours = 0.83 # 25 mins each side

    # Query live train API / mock fallback
    trains_list = get_trains_between(origin, destination)
    primary_train = None
    if selected_train_number and trains_list:
        for tr in trains_list:
            if tr.get("train_number") == str(selected_train_number):
                primary_train = tr
                break
    if not primary_train and trains_list:
        primary_train = trains_list[0]

    train_num = primary_train.get("train_number") if primary_train else "12015"
    train_nm = primary_train.get("train_name") if primary_train else "Intercity Express Train"
    dep_tm = primary_train.get("departure_time") if primary_train else "06:10"
    arr_tm = primary_train.get("arrival_time") if primary_train else "10:35"
    dep_hub_str = primary_train.get("from_station") if primary_train else orig_hubs["rail"]
    arr_hub_str = primary_train.get("to_station") if primary_train else dest_hubs["rail"]
    if dep_hub_str and "railway" not in dep_hub_str.lower():
        if "station" in dep_hub_str.lower():
            dep_hub_str = dep_hub_str.replace("Station", "Railway Station")
        elif "jn" in dep_hub_str.lower():
            dep_hub_str = dep_hub_str.replace("Jn", "Junction Railway Station")
        else:
            dep_hub_str = f"{dep_hub_str} Railway Station"
    if arr_hub_str and "railway" not in arr_hub_str.lower():
        if "station" in arr_hub_str.lower():
            arr_hub_str = arr_hub_str.replace("Station", "Railway Station")
        elif "jn" in arr_hub_str.lower():
            arr_hub_str = arr_hub_str.replace("Jn", "Junction Railway Station")
        else:
            arr_hub_str = f"{arr_hub_str} Railway Station"

    if primary_train and primary_train.get("duration_hours"):
        train_base_hours = float(primary_train["duration_hours"])

    train_buffered_hours = round((train_base_hours * (1.0 + train_delay_ratio)) + station_buffer_hours + train_local_transfer_hours, 2)

    # Google Maps Transit Fare evaluation if available
    g_fare_obj = google_data.get("transit_fare") if (google_data and google_data.get("mode") == "transit") else None
    primary_classes = primary_train.get("classes", ["CC"]) if primary_train else ["CC"]
    primary_class = primary_classes[0] if primary_classes else "CC"

    train_fare_calc = calculate_transport_fare(effective_dist, "train", party_size=party_size, google_fare_obj=g_fare_obj, train_class=primary_class)
    ticket_per_person_train = train_fare_calc["ticket_cost_per_person"]
    train_tickets_total = train_fare_calc["tickets_total"]
    train_local_transit_cost = train_fare_calc["local_shared_transit_cost"]
    train_total_cost = train_fare_calc["total_cost"]

    # 3. Bus (Highway Express Bus)
    bus_speed = 48.0
    bus_base_hours = round(effective_dist / bus_speed, 2)
    bus_delay_ratio = 0.22
    bus_terminal_buffer = 0.42 # 25 mins terminal check-in & boarding
    bus_local_transfer_hours = 0.8 # 24 mins each side
    bus_buffered_hours = round((bus_base_hours * (1.0 + bus_delay_ratio)) + bus_terminal_buffer + bus_local_transfer_hours, 2)

    bus_fare_calc = calculate_transport_fare(effective_dist, "bus", party_size=party_size)
    ticket_per_person_bus = bus_fare_calc["ticket_cost_per_person"]
    bus_tickets_total = bus_fare_calc["tickets_total"]
    bus_local_transit_cost = bus_fare_calc["local_shared_transit_cost"]
    bus_total_cost = bus_fare_calc["total_cost"]

    # 4. Shared Cab (Outstation Shared Taxi / Shuttle)
    cab_speed = 60.0
    cab_base_hours = round(effective_dist / cab_speed, 2)
    cab_delay_ratio = 0.15
    cab_pickup_buffer = 0.25 # 15 mins
    cab_buffered_hours = round((cab_base_hours * (1.0 + cab_delay_ratio)) + cab_pickup_buffer, 2)

    cab_fare_calc = calculate_transport_fare(effective_dist, "shared_cab", party_size=party_size)
    ticket_per_person_cab = cab_fare_calc["ticket_cost_per_person"]
    cab_tickets_total = cab_fare_calc["tickets_total"]
    cab_local_pickup = cab_fare_calc["local_shared_transit_cost"]
    cab_total_cost = cab_fare_calc["total_cost"]

    # Train rich metadata
    train_seat_status = primary_train.get("seat_status", []) if primary_train else []
    train_coach_pos = primary_train.get("coach_position", "") if primary_train else ""
    train_route_stops = primary_train.get("route_stops", []) if primary_train else []
    train_live = primary_train.get("live_status", {}) if primary_train else {}

    options = {
        "driving": {
            "mode": "driving",
            "title": "Self-Drive / Personal Car",
            "description": f"Direct highway drive via NH corridor. Door-to-door flexibility with fuel & toll costs.",
            "base_duration_hours": car_base_hours,
            "buffered_duration_hours": car_buffered_hours,
            "delay_buffer_ratio": car_delay_ratio,
            "station_buffer_hours": 0.0,
            "ticket_cost_per_person": 0.0,
            "tickets_total": car_total_cost,
            "local_shared_transit_cost": 0.0,
            "total_cost": car_total_cost,
            "departure_hub": f"{origin} (Doorstep)",
            "arrival_hub": f"{destination} (Direct)",
            "local_vehicle_type": "Private / Rental Vehicle",
            "fare_source": car_fare_calc["fare_source"],
            "fare_currency": car_fare_calc["fare_currency"],
            "fare_breakdown": car_fare_calc["fare_breakdown"],
            "seat_status": [],
            "coach_position": "",
            "route_stops": [],
            "live_status": {},
            "live_delay_mins": 0,
            "live_status_text": "Normal Highway Traffic"
        },
        "train": {
            "mode": "train",
            "title": f"{train_nm} ({train_num})" if primary_train else "Intercity Express Train",
            "description": f"Rail transit via {train_nm} ({train_num}) from {dep_hub_str} to {arr_hub_str}. Dep: {dep_tm}, Arr: {arr_tm}.",
            "base_duration_hours": train_base_hours,
            "buffered_duration_hours": train_buffered_hours,
            "delay_buffer_ratio": train_delay_ratio,
            "station_buffer_hours": station_buffer_hours,
            "ticket_cost_per_person": ticket_per_person_train,
            "tickets_total": train_tickets_total,
            "local_shared_transit_cost": train_local_transit_cost,
            "total_cost": train_total_cost,
            "departure_hub": dep_hub_str,
            "arrival_hub": arr_hub_str,
            "local_vehicle_type": "Shared Auto-Rickshaw / E-Rickshaw",
            "train_number": train_num,
            "train_name": train_nm,
            "departure_time": dep_tm,
            "arrival_time": arr_tm,
            "available_trains": trains_list,
            "fare_source": train_fare_calc["fare_source"],
            "fare_currency": train_fare_calc["fare_currency"],
            "fare_breakdown": train_fare_calc["fare_breakdown"],
            "seat_status": train_seat_status,
            "coach_position": train_coach_pos,
            "route_stops": train_route_stops,
            "live_status": train_live,
            "live_delay_mins": int(train_live.get("delay_minutes", 0)),
            "live_status_text": train_live.get("status", "On Time")
        },
        "bus": {
            "mode": "bus",
            "title": "Highway Express Bus",
            "description": f"Express interstate bus from {orig_hubs['bus']} to {dest_hubs['bus']} with local shared feeder autos.",
            "base_duration_hours": bus_base_hours,
            "buffered_duration_hours": bus_buffered_hours,
            "delay_buffer_ratio": bus_delay_ratio,
            "station_buffer_hours": bus_terminal_buffer,
            "ticket_cost_per_person": ticket_per_person_bus,
            "tickets_total": bus_tickets_total,
            "local_shared_transit_cost": bus_local_transit_cost,
            "total_cost": bus_total_cost,
            "departure_hub": orig_hubs["bus"],
            "arrival_hub": dest_hubs["bus"],
            "local_vehicle_type": "Shared Auto / Metro Feeder",
            "fare_source": bus_fare_calc["fare_source"],
            "fare_currency": bus_fare_calc["fare_currency"],
            "fare_breakdown": bus_fare_calc["fare_breakdown"],
            "seat_status": [],
            "coach_position": "",
            "route_stops": [],
            "live_status": {},
            "live_delay_mins": 0,
            "live_status_text": "Scheduled Inter-State Bus"
        },
        "shared_cab": {
            "mode": "shared_cab",
            "title": "Shared Outstation Cab",
            "description": f"Shared outstation taxi with shared local feeder pickup in {origin} and drop in {destination}.",
            "base_duration_hours": cab_base_hours,
            "buffered_duration_hours": cab_buffered_hours,
            "delay_buffer_ratio": cab_delay_ratio,
            "station_buffer_hours": cab_pickup_buffer,
            "ticket_cost_per_person": ticket_per_person_cab,
            "tickets_total": cab_tickets_total,
            "local_shared_transit_cost": cab_local_pickup,
            "total_cost": cab_total_cost,
            "departure_hub": orig_hubs["cab"],
            "arrival_hub": dest_hubs["cab"],
            "local_vehicle_type": "Shared Taxi Feeder",
            "fare_source": cab_fare_calc["fare_source"],
            "fare_currency": cab_fare_calc["fare_currency"],
            "fare_breakdown": cab_fare_calc["fare_breakdown"],
            "seat_status": [],
            "coach_position": "",
            "route_stops": [],
            "live_status": {},
            "live_delay_mins": 0,
            "live_status_text": "Shared Outstation Seat"
        }
    }

    # 5. Flight (Commercial domestic flight where airport connectivity exists)
    flight_opt = calculate_flight_transit(origin, destination, effective_dist, party_size=party_size, selected_flight_number=selected_flight_number)
    if flight_opt:
        options["flight"] = flight_opt

    return options

@tool(name="get_route", description="Fetch driving or travel route distance, time, and corridor waypoints between origin and destination.")
def get_route(
    origin: str,
    destination: str,
    travel_mode: str = "driving",
    party_size: int = 1,
    selected_train_number: Optional[str] = None,
    selected_flight_number: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    cache_key = f"{origin.lower()}_to_{destination.lower()}_{travel_mode}_p{party_size}_{selected_train_number or 'def'}_{selected_flight_number or 'def'}"
    cached = cache_db.get("route", cache_key)
    if cached:
        if travel_mode == "train" and cached.get("departure_hub") and not any(w in cached["departure_hub"] for w in ["Station", "Junction", "Terminal"]):
            pass
        elif "fare_breakdown" in cached and "seat_status" in cached:
            return cached

    coord_a = get_coordinates(origin)
    coord_b = get_coordinates(destination)

    # 1. Attempt Google Maps Directions / Routes API
    g_data = get_google_directions(origin, destination, travel_mode=travel_mode, api_key=api_key)
    geometry_coords: List[Dict[str, float]] = []
    dist_km = 0.0
    duration_hours = 0.0

    if g_data and g_data.get("distance_km", 0) > 0:
        dist_km = g_data["distance_km"]
        duration_hours = g_data["duration_hours"]
        if g_data.get("geometry"):
            geometry_coords = g_data["geometry"]

    # 2. Fallback to live OSRM routing if Google Maps did not supply distance
    if dist_km <= 0:
        try:
            osrm_url = f"{OSRM_BASE_URL}/route/v1/driving/{coord_a.lon},{coord_a.lat};{coord_b.lon},{coord_b.lat}?overview=full&geometries=geojson"
            resp = requests.get(osrm_url, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("routes"):
                    primary = data["routes"][0]
                    dist_km = round(primary["distance"] / 1000.0, 1)
                    duration_hours = round(primary["duration"] / 3600.0, 2)
                    raw_coords = primary["geometry"]["coordinates"]
                    step = max(1, len(raw_coords) // 50)
                    geometry_coords = [{"lat": round(pt[1], 4), "lon": round(pt[0], 4)} for pt in raw_coords[::step]]
                    if raw_coords:
                        geometry_coords.append({"lat": round(raw_coords[-1][1], 4), "lon": round(raw_coords[-1][0], 4)})
        except Exception:
            pass

    # 3. Fallback to geodesic model if OSRM failed or returned 0
    if dist_km <= 0:
        crow_dist = haversine_distance(coord_a, coord_b)
        dist_km = round(crow_dist * 1.28, 1)
        steps = 15
        geometry_coords = []
        for i in range(steps + 1):
            t = i / steps
            geometry_coords.append({
                "lat": round(coord_a.lat + (coord_b.lat - coord_a.lat) * t, 4),
                "lon": round(coord_a.lon + (coord_b.lon - coord_a.lon) * t, 4)
            })

    # Calculate comparative transit options across all modes
    transit_options = calculate_transit_options(
        origin, destination, dist_km,
        party_size=party_size,
        selected_train_number=selected_train_number,
        selected_flight_number=selected_flight_number,
        google_data=g_data,
        api_key=api_key
    )
    chosen_opt = transit_options.get(travel_mode, transit_options["driving"])

    # If train mode is chosen, check if live railway track geometry is available
    if travel_mode == "train" and chosen_opt.get("train_number"):
        rail_geom = get_train_route_geometry(chosen_opt["train_number"])
        if rail_geom and len(rail_geom) > 1:
            geometry_coords = rail_geom

    # Determine intermediate corridor stops
    corridor_stops = _infer_corridor_stops(origin, destination)

    result = {
        "origin": origin.title(),
        "destination": destination.title(),
        "origin_coords": {"lat": coord_a.lat, "lon": coord_a.lon},
        "dest_coords": {"lat": coord_b.lat, "lon": coord_b.lon},
        "total_distance_km": dist_km,
        "base_travel_time_hours": chosen_opt["base_duration_hours"],
        "buffered_travel_time_hours": chosen_opt["buffered_duration_hours"],
        "delay_buffer_ratio": chosen_opt["delay_buffer_ratio"],
        "estimated_transit_cost": chosen_opt["total_cost"],
        "travel_mode": travel_mode,
        "selected_mode": travel_mode,
        "ticket_cost": chosen_opt["tickets_total"],
        "local_transit_cost": chosen_opt["local_shared_transit_cost"],
        "departure_hub": chosen_opt["departure_hub"],
        "arrival_hub": chosen_opt["arrival_hub"],
        "local_vehicle_type": chosen_opt["local_vehicle_type"],
        "train_number": chosen_opt.get("train_number"),
        "train_name": chosen_opt.get("train_name"),
        "departure_time": chosen_opt.get("departure_time"),
        "arrival_time": chosen_opt.get("arrival_time"),
        "available_trains": chosen_opt.get("available_trains", []),
        "flight_number": chosen_opt.get("flight_number"),
        "airline": chosen_opt.get("airline"),
        "airline_code": chosen_opt.get("airline_code"),
        "aircraft": chosen_opt.get("aircraft"),
        "cabin_class": chosen_opt.get("cabin_class"),
        "baggage_allowance": chosen_opt.get("baggage_policy"),
        "available_flights": chosen_opt.get("available_flights", []),
        "available_modes": list(transit_options.values()),
        "corridor_stops": corridor_stops,
        "geometry": geometry_coords,
        "fare_source": chosen_opt.get("fare_source", "calibrated_model"),
        "fare_currency": chosen_opt.get("fare_currency", "₹"),
        "fare_breakdown": chosen_opt.get("fare_breakdown", {}),
        "seat_status": chosen_opt.get("seat_status", []),
        "coach_position": chosen_opt.get("coach_position", ""),
        "route_stops": chosen_opt.get("route_stops", []),
        "live_status": chosen_opt.get("live_status", {}),
        "live_delay_mins": chosen_opt.get("live_delay_mins", 0),
        "live_status_text": chosen_opt.get("live_status_text", "Scheduled")
    }

    cache_db.set("route", cache_key, result)
    return result

@tool(name="get_multi_stop_route", description="Fetch travel route covering origin, intermediate stopovers, and final destination with per-leg multi-modal transit choices.")
def get_multi_stop_route(
    origin: str,
    destination: str,
    stopovers: Optional[List[str]] = None,
    travel_mode: str = "driving",
    leg_modes: Optional[List[str]] = None,
    party_size: int = 1,
    selected_trains: Optional[Dict[str, str]] = None,
    selected_flights: Optional[Dict[str, str]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    stopovers = [s.strip() for s in (stopovers or []) if s and s.strip()]
    if not stopovers:
        direct_mode = leg_modes[0] if (leg_modes and len(leg_modes) > 0 and leg_modes[0]) else travel_mode
        direct_train = (selected_trains.get("0") or selected_trains.get(f"{origin}->{destination}")) if selected_trains else None
        direct_flight = (selected_flights.get("0") or selected_flights.get(f"{origin}->{destination}") or selected_flights.get(destination)) if selected_flights else None
        direct = get_route(
            origin, destination, travel_mode=direct_mode, party_size=party_size,
            selected_train_number=direct_train, selected_flight_number=direct_flight, api_key=api_key
        )
        direct["legs"] = [{
            "from_place": direct["origin"],
            "to_place": direct["destination"],
            "distance_km": direct["total_distance_km"],
            "duration_hours": direct["base_travel_time_hours"],
            "buffered_duration_hours": direct["buffered_travel_time_hours"],
            "estimated_transit_cost": direct["estimated_transit_cost"],
            "geometry": direct.get("geometry", []),
            "selected_mode": direct["selected_mode"],
            "available_modes": direct.get("available_modes", []),
            "ticket_cost": direct.get("ticket_cost", 0.0),
            "local_transit_cost": direct.get("local_transit_cost", 0.0),
            "departure_hub": direct.get("departure_hub", ""),
            "arrival_hub": direct.get("arrival_hub", ""),
            "local_vehicle_type": direct.get("local_vehicle_type", ""),
            "train_number": direct.get("train_number"),
            "train_name": direct.get("train_name"),
            "departure_time": direct.get("departure_time"),
            "arrival_time": direct.get("arrival_time"),
            "available_trains": direct.get("available_trains", []),
            "flight_number": direct.get("flight_number"),
            "airline": direct.get("airline"),
            "airline_code": direct.get("airline_code"),
            "aircraft": direct.get("aircraft"),
            "cabin_class": direct.get("cabin_class"),
            "baggage_allowance": direct.get("baggage_allowance"),
            "available_flights": direct.get("available_flights", []),
            "fare_source": direct.get("fare_source", "calibrated_model"),
            "fare_currency": direct.get("fare_currency", "₹"),
            "fare_breakdown": direct.get("fare_breakdown", {}),
            "seat_status": direct.get("seat_status", []),
            "coach_position": direct.get("coach_position", ""),
            "route_stops": direct.get("route_stops", []),
            "live_status": direct.get("live_status", {}),
            "live_delay_mins": direct.get("live_delay_mins", 0),
            "live_status_text": direct.get("live_status_text", "Scheduled")
        }]
        return direct

    points = [origin.strip()] + stopovers + [destination.strip()]
    legs = []
    total_dist = 0.0
    total_base_time = 0.0
    total_buf_time = 0.0
    total_cost = 0.0
    all_geometry: List[Dict[str, float]] = []
    all_corridor_stops: List[str] = list(stopovers)

    for i in range(len(points) - 1):
        p_from = points[i]
        p_to = points[i+1]
        leg_mode = leg_modes[i] if (leg_modes and i < len(leg_modes) and leg_modes[i]) else travel_mode
        leg_train = (selected_trains.get(str(i)) or selected_trains.get(f"{p_from}->{p_to}")) if selected_trains else None
        leg_flight = (selected_flights.get(str(i)) or selected_flights.get(f"{p_from}->{p_to}") or selected_flights.get(p_to)) if selected_flights else None
        leg_data = get_route(p_from, p_to, travel_mode=leg_mode, party_size=party_size, selected_train_number=leg_train, selected_flight_number=leg_flight, api_key=api_key)
        legs.append({
            "from_place": p_from.title(),
            "to_place": p_to.title(),
            "distance_km": leg_data["total_distance_km"],
            "duration_hours": leg_data["base_travel_time_hours"],
            "buffered_duration_hours": leg_data["buffered_travel_time_hours"],
            "estimated_transit_cost": leg_data["estimated_transit_cost"],
            "geometry": leg_data.get("geometry", []),
            "selected_mode": leg_mode,
            "available_modes": leg_data.get("available_modes", []),
            "ticket_cost": leg_data.get("ticket_cost", 0.0),
            "local_transit_cost": leg_data.get("local_transit_cost", 0.0),
            "departure_hub": leg_data.get("departure_hub", ""),
            "arrival_hub": leg_data.get("arrival_hub", ""),
            "local_vehicle_type": leg_data.get("local_vehicle_type", ""),
            "train_number": leg_data.get("train_number"),
            "train_name": leg_data.get("train_name"),
            "departure_time": leg_data.get("departure_time"),
            "arrival_time": leg_data.get("arrival_time"),
            "available_trains": leg_data.get("available_trains", []),
            "flight_number": leg_data.get("flight_number"),
            "airline": leg_data.get("airline"),
            "airline_code": leg_data.get("airline_code"),
            "aircraft": leg_data.get("aircraft"),
            "cabin_class": leg_data.get("cabin_class"),
            "baggage_allowance": leg_data.get("baggage_allowance"),
            "available_flights": leg_data.get("available_flights", []),
            "fare_source": leg_data.get("fare_source", "calibrated_model"),
            "fare_currency": leg_data.get("fare_currency", "₹"),
            "fare_breakdown": leg_data.get("fare_breakdown", {}),
            "seat_status": leg_data.get("seat_status", []),
            "coach_position": leg_data.get("coach_position", ""),
            "route_stops": leg_data.get("route_stops", []),
            "live_status": leg_data.get("live_status", {}),
            "live_delay_mins": leg_data.get("live_delay_mins", 0),
            "live_status_text": leg_data.get("live_status_text", "Scheduled")
        })
        total_dist += leg_data["total_distance_km"]
        total_base_time += leg_data["base_travel_time_hours"]
        total_buf_time += leg_data["buffered_travel_time_hours"]
        total_cost += leg_data["estimated_transit_cost"]

        leg_geom = leg_data.get("geometry", [])
        if all_geometry and leg_geom:
            all_geometry.extend(leg_geom[1:])
        else:
            all_geometry.extend(leg_geom)

        for c_stop in leg_data.get("corridor_stops", []):
            if c_stop not in all_corridor_stops and c_stop.lower() not in [p.lower() for p in points]:
                all_corridor_stops.append(c_stop)

    orig_coords = get_coordinates(origin)
    dest_coords = get_coordinates(destination)

    return {
        "origin": origin.title(),
        "destination": destination.title(),
        "origin_coords": {"lat": orig_coords.lat, "lon": orig_coords.lon},
        "dest_coords": {"lat": dest_coords.lat, "lon": dest_coords.lon},
        "total_distance_km": round(total_dist, 1),
        "base_travel_time_hours": round(total_base_time, 2),
        "buffered_travel_time_hours": round(total_buf_time, 2),
        "delay_buffer_ratio": DEFAULT_DELAY_BUFFER_RATIO,
        "estimated_transit_cost": round(total_cost, 0),
        "travel_mode": travel_mode,
        "selected_mode": travel_mode,
        "corridor_stops": all_corridor_stops,
        "geometry": all_geometry,
        "legs": legs,
        "fare_source": legs[0].get("fare_source", "calibrated_model") if legs else "calibrated_model"
    }

def _infer_corridor_stops(origin: str, destination: str) -> List[str]:
    """Identifies realistic highway stop candidates along standard travel corridors."""
    pair = f"{origin.lower()}-{destination.lower()}"
    reverse_pair = f"{destination.lower()}-{origin.lower()}"

    known_corridors = {
        "delhi-jaipur": ["Gurgaon", "Neemrana", "Behror", "Shahpura"],
        "jaipur-delhi": ["Shahpura", "Behror", "Neemrana", "Gurgaon"],
        "delhi-agra": ["Faridabad", "Palwal", "Mathura", "Vrindavan"],
        "agra-delhi": ["Vrindavan", "Mathura", "Palwal", "Faridabad"],
        "mumbai-pune": ["Navi Mumbai", "Lonavala", "Khandala"],
        "pune-mumbai": ["Khandala", "Lonavala", "Navi Mumbai"],
        "mumbai-goa": ["Pune", "Satara", "Kolhapur", "Belgaum"],
        "goa-mumbai": ["Belgaum", "Kolhapur", "Satara", "Pune"],
        "bangalore-coorg": ["Mandya", "Mysore", "Hunsur", "Kushalnagar"],
        "coorg-bangalore": ["Kushalnagar", "Hunsur", "Mysore", "Mandya"],
        "bangalore-ooty": ["Mysore", "Nanjangud", "Bandipur", "Mudumalai"],
        "ooty-bangalore": ["Mudumalai", "Bandipur", "Nanjangud", "Mysore"],
        "chandigarh-manali": ["Bilaspur", "Mandi", "Kullu"],
        "manali-chandigarh": ["Kullu", "Mandi", "Bilaspur"],
        "delhi-haridwar": ["Roorkee", "Nayidwar", "Har Ki Pauri"],
        "haridwar-delhi": ["Nayidwar", "Roorkee", "Muzaffarnagar"],
        "delhi-rishikesh": ["Roorkee", "Haridwar", "Rishikesh Beach"],
        "rishikesh-delhi": ["Haridwar", "Roorkee", "Muzaffarnagar"],
        "jaipur-udaipur": ["Ajmer", "Beawar", "Chittorgarh"],
        "udaipur-jaipur": ["Chittorgarh", "Beawar", "Ajmer"],
        "chennai-pondicherry": ["Mahabalipuram", "Kalpakkam", "Marakkanam"],
        "pondicherry-chennai": ["Marakkanam", "Kalpakkam", "Mahabalipuram"],
        "kolkata-darjeeling": ["Malda", "Siliguri", "Kurseong"],
        "darjeeling-kolkata": ["Kurseong", "Siliguri", "Malda"],
        "pune-mahabaleshwar": ["Shirwal", "Wai", "Panchgani"],
        "mahabaleshwar-pune": ["Panchgani", "Wai", "Shirwal"],
    }

    if pair in known_corridors:
        return known_corridors[pair]
    if reverse_pair in known_corridors:
        return list(reversed(known_corridors[reverse_pair]))

    # Dynamic fallback: find cities geographically positioned between origin and destination
    try:
        orig_c = get_coordinates(origin)
        dest_c = get_coordinates(destination)
        total_dist = haversine_distance(orig_c, dest_c)

        if total_dist > 50:
            intermediates = []
            orig_lower = origin.lower()
            dest_lower = destination.lower()

            for city, (c_lat, c_lon) in KNOWN_CITIES.items():
                if city in orig_lower or city in dest_lower:
                    continue
                cand_c = Coordinates(lat=c_lat, lon=c_lon)
                d1 = haversine_distance(orig_c, cand_c)
                d2 = haversine_distance(cand_c, dest_c)
                # Check if candidate is reasonably on the path (detour < 22% of total)
                if (d1 + d2) <= total_dist * 1.22 and d1 > 20 and d2 > 20:
                    intermediates.append((d1, city.title()))

            if intermediates:
                intermediates.sort(key=lambda x: x[0])
                return [name for _, name in intermediates[:4]]
    except Exception:
        pass

    return [f"Midway Junction on NH to {destination.title()}", f"Scenic Rest Area before {destination.title()}"]
