"""
Google Maps API routing, distance, travel time, polyline decoding,
and transport fare extraction module with resilient calibrated fallbacks.
"""

import logging
import requests
from typing import Dict, Any, List, Optional, Tuple
from config import GOOGLE_MAPS_API_KEY
from tools.cache import cache_db

logger = logging.getLogger(__name__)

GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
GOOGLE_ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

# State tracking for API status
api_status_info: Dict[str, Any] = {
    "key_configured": bool(GOOGLE_MAPS_API_KEY),
    "active": False,
    "last_error": None,
    "activation_url": "https://console.developers.google.com/apis/library?filter=category:maps"
}


def decode_polyline(polyline_str: str) -> List[Dict[str, float]]:
    """
    Decodes a Google encoded polyline string into a list of {'lat': float, 'lon': float} points.
    Implements Google's polyline encoding algorithm in pure Python.
    """
    if not polyline_str:
        return []

    coordinates: List[Dict[str, float]] = []
    index = 0
    length = len(polyline_str)
    lat = 0
    lng = 0

    while index < length:
        # Decode Latitude
        shift = 0
        result = 0
        while index < length:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        # Decode Longitude
        shift = 0
        result = 0
        while index < length:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append({
            "lat": round(lat * 1e-5, 5),
            "lon": round(lng * 1e-5, 5)
        })

    return coordinates


def get_google_directions(
    origin: str,
    destination: str,
    travel_mode: str = "driving",
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetches route, distance, travel time, road geometry, and transit fare from Google Maps API.
    Attempts modern Google Routes API first, then Directions API, with automatic caching.
    """
    key = api_key or GOOGLE_MAPS_API_KEY
    if not key:
        return None

    # Standardize travel mode for Google Maps
    g_mode = "driving"
    if travel_mode in ("train", "bus", "transit"):
        g_mode = "transit"

    cache_key = f"gmaps_{origin.lower()}_{destination.lower()}_{g_mode}"
    cached = cache_db.get("gmaps_route", cache_key)
    if cached:
        return cached

    # 1. Try Google Directions API
    try:
        params = {
            "origin": f"{origin}, India" if "India" not in origin else origin,
            "destination": f"{destination}, India" if "India" not in destination else destination,
            "mode": g_mode,
            "departure_time": "now",
            "key": key
        }
        resp = requests.get(GOOGLE_DIRECTIONS_URL, params=params, timeout=4.5)
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status")
            if status == "OK" and data.get("routes"):
                api_status_info["active"] = True
                api_status_info["last_error"] = None
                parsed = _parse_google_directions_response(data, origin, destination, g_mode)
                if parsed:
                    cache_db.set("gmaps_route", cache_key, parsed)
                    return parsed
            elif status in ("REQUEST_DENIED", "ACCESS_NOT_CONFIGURED"):
                err_msg = data.get("error_message", "")
                logger.info(f"Google Directions API not yet activated: {err_msg}")
                api_status_info["last_error"] = err_msg
                if "LegacyApiNotActivatedMapError" in err_msg:
                    api_status_info["activation_url"] = "https://console.developers.google.com/apis/api/routes.googleapis.com/overview"
    except Exception as e:
        logger.debug(f"Google Directions request error: {e}")

    # 2. Try Google Routes API (Modern)
    try:
        r_headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": (
                "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,"
                "routes.travelAdvisory.tollInfo,routes.legs.travelAdvisory.transitFare"
            )
        }
        r_mode = "DRIVE" if g_mode == "driving" else "TRANSIT"
        r_payload = {
            "origin": {"address": f"{origin}, India" if "India" not in origin else origin},
            "destination": {"address": f"{destination}, India" if "India" not in destination else destination},
            "travelMode": r_mode
        }
        r_resp = requests.post(GOOGLE_ROUTES_URL, headers=r_headers, json=r_payload, timeout=4.5)
        if r_resp.status_code == 200:
            r_data = r_resp.json()
            if "routes" in r_data and r_data["routes"]:
                api_status_info["active"] = True
                api_status_info["last_error"] = None
                parsed = _parse_google_routes_response(r_data, origin, destination, g_mode)
                if parsed:
                    cache_db.set("gmaps_route", cache_key, parsed)
                    return parsed
        elif r_resp.status_code == 403:
            err_dict = r_resp.json().get("error", {})
            api_status_info["last_error"] = err_dict.get("message", "Routes API disabled")
    except Exception as e:
        logger.debug(f"Google Routes request error: {e}")

    return None


def _parse_google_directions_response(
    data: Dict[str, Any],
    origin: str,
    destination: str,
    mode: str
) -> Optional[Dict[str, Any]]:
    """Parses Google Maps Directions API JSON response into standardized format."""
    try:
        route = data["routes"][0]
        leg = route["legs"][0]

        dist_km = round(leg["distance"]["value"] / 1000.0, 1)
        dur_hours = round(leg["duration"]["value"] / 3600.0, 2)
        
        # Traffic-aware duration if provided
        traffic_dur_hours = dur_hours
        if "duration_in_traffic" in leg:
            traffic_dur_hours = round(leg["duration_in_traffic"]["value"] / 3600.0, 2)

        # Overview polyline
        encoded_poly = route.get("overview_polyline", {}).get("points", "")
        geometry = decode_polyline(encoded_poly)

        # Transit fare
        fare_obj = route.get("fare")
        transit_fare = None
        if fare_obj:
            transit_fare = {
                "currency": fare_obj.get("currency", "INR"),
                "value": float(fare_obj.get("value", 0.0)),
                "text": fare_obj.get("text", f"₹{fare_obj.get('value')}")
            }

        # Transit steps & agency details
        transit_steps = []
        for st in leg.get("steps", []):
            if st.get("travel_mode") == "TRANSIT" and "transit_details" in st:
                td = st["transit_details"]
                line = td.get("line", {})
                vehicle = line.get("vehicle", {})
                transit_steps.append({
                    "vehicle_type": vehicle.get("type", "TRAIN"),
                    "vehicle_name": vehicle.get("name", "Rail/Bus"),
                    "line_name": line.get("name") or line.get("short_name", ""),
                    "departure_stop": td.get("departure_stop", {}).get("name", ""),
                    "arrival_stop": td.get("arrival_stop", {}).get("name", ""),
                    "num_stops": td.get("num_stops", 1),
                    "departure_time": td.get("departure_time", {}).get("text", ""),
                    "arrival_time": td.get("arrival_time", {}).get("text", "")
                })

        return {
            "source": "google_maps",
            "mode": mode,
            "origin": origin,
            "destination": destination,
            "distance_km": dist_km,
            "duration_hours": dur_hours,
            "traffic_duration_hours": traffic_dur_hours,
            "transit_fare": transit_fare,
            "transit_steps": transit_steps,
            "geometry": geometry,
            "polyline": encoded_poly
        }
    except Exception as e:
        logger.error(f"Error parsing Google Directions response: {e}")
        return None


def _parse_google_routes_response(
    data: Dict[str, Any],
    origin: str,
    destination: str,
    mode: str
) -> Optional[Dict[str, Any]]:
    """Parses Google Routes API (modern) JSON response."""
    try:
        route = data["routes"][0]
        meters = route.get("distanceMeters", 0)
        dist_km = round(meters / 1000.0, 1)

        dur_str = route.get("duration", "0s").replace("s", "")
        dur_secs = float(dur_str) if dur_str.replace(".", "").isdigit() else 0.0
        dur_hours = round(dur_secs / 3600.0, 2)

        encoded_poly = route.get("polyline", {}).get("encodedPolyline", "")
        geometry = decode_polyline(encoded_poly)

        transit_fare = None
        legs = route.get("legs", [])
        if legs and "travelAdvisory" in legs[0]:
            tf = legs[0]["travelAdvisory"].get("transitFare", {})
            if tf:
                units = float(tf.get("units", 0.0))
                nanos = float(tf.get("nanos", 0.0)) / 1e9
                val = round(units + nanos, 2)
                transit_fare = {
                    "currency": tf.get("currencyCode", "INR"),
                    "value": val,
                    "text": f"₹{val}"
                }

        return {
            "source": "google_routes",
            "mode": mode,
            "origin": origin,
            "destination": destination,
            "distance_km": dist_km,
            "duration_hours": dur_hours,
            "traffic_duration_hours": dur_hours,
            "transit_fare": transit_fare,
            "transit_steps": [],
            "geometry": geometry,
            "polyline": encoded_poly
        }
    except Exception as e:
        logger.error(f"Error parsing Google Routes response: {e}")
        return None


def calculate_transport_fare(
    distance_km: float,
    travel_mode: str,
    party_size: int = 1,
    google_fare_obj: Optional[Dict[str, Any]] = None,
    train_class: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates realistic transport fare:
    - Extracts transit fare directly from Google Maps when available.
    - Otherwise applies calibrated Indian transport models (fuel, tolls, train slabs, bus tickets, feeder autos).
    """
    eff_dist = max(10.0, distance_km)
    party_size = max(1, party_size)

    # 1. Self-Drive / Personal Car
    if travel_mode == "driving":
        # Fuel: ~14 km/L highway economy at ₹96/L petrol/diesel = ~₹6.86/km
        fuel_rate_per_km = 6.86
        fuel_cost = round(eff_dist * fuel_rate_per_km, 0)
        # Toll Plazas: standard NHAI 4-6 lane corridor toll ~₹1.80/km
        toll_cost = round(eff_dist * 1.80, 0)
        total_vehicle_cost = fuel_cost + toll_cost
        per_person = round(total_vehicle_cost / party_size, 0)

        return {
            "total_cost": total_vehicle_cost,
            "ticket_cost_per_person": 0.0,
            "tickets_total": total_vehicle_cost,
            "local_shared_transit_cost": 0.0,
            "fare_source": "calibrated_fuel_and_tolls",
            "fare_currency": "₹",
            "fare_breakdown": {
                "fuel_cost": fuel_cost,
                "toll_cost": toll_cost,
                "total_vehicle_cost": total_vehicle_cost,
                "party_size": party_size,
                "cost_per_person": per_person,
                "description": f"Fuel: ₹{fuel_cost:,.0f} + NH Tolls: ₹{toll_cost:,.0f} (₹{per_person:,.0f}/person for {party_size})"
            }
        }

    # 2. Train Transit
    elif travel_mode == "train":
        # First-mile & last-mile shared auto-rickshaw feeder transit
        local_feeder = 300.0  # ₹140 origin + ₹160 destination

        # Check if Google Maps returned transit fare
        if google_fare_obj and google_fare_obj.get("value"):
            ticket_per_person = float(google_fare_obj["value"])
            total_tickets = round(ticket_per_person * party_size, 0)
            return {
                "total_cost": total_tickets + local_feeder,
                "ticket_cost_per_person": ticket_per_person,
                "tickets_total": total_tickets,
                "local_shared_transit_cost": local_feeder,
                "fare_source": "google_maps",
                "fare_currency": google_fare_obj.get("currency", "₹"),
                "fare_breakdown": {
                    "ticket_per_person": ticket_per_person,
                    "tickets_total": total_tickets,
                    "local_feeder": local_feeder,
                    "party_size": party_size,
                    "source": "Google Maps Transit Fare API",
                    "description": f"Google Transit Fare: ₹{ticket_per_person:,.0f}/person + Shared Feeder Auto: ₹{local_feeder:,.0f}"
                }
            }

        # Calibrated Indian Railways Slab Fare Model
        fare_slabs = {
            "1A": 450.0 + (eff_dist * 2.65),  # First AC
            "2A": 340.0 + (eff_dist * 2.05),  # 2-Tier AC
            "3A": 210.0 + (eff_dist * 1.45),  # 3-Tier AC
            "CC": 180.0 + (eff_dist * 1.35),  # AC Chair Car
            "EC": 420.0 + (eff_dist * 2.55),  # Executive Chair Car
            "SL": 60.0 + (eff_dist * 0.48),   # Sleeper Class
            "2S": 45.0 + (eff_dist * 0.35)    # Second Sitting
        }
        ticket_per_person = round(fare_slabs.get(train_class or "CC", max(75.0, eff_dist * 1.85)), 0)
        total_tickets = round(ticket_per_person * party_size, 0)
        total_cost = total_tickets + local_feeder

        return {
            "total_cost": total_cost,
            "ticket_cost_per_person": ticket_per_person,
            "tickets_total": total_tickets,
            "local_shared_transit_cost": local_feeder,
            "fare_source": "railway_calibrated_model",
            "fare_currency": "₹",
            "fare_breakdown": {
                "class": train_class or "CC",
                "ticket_per_person": ticket_per_person,
                "tickets_total": total_tickets,
                "local_feeder": local_feeder,
                "party_size": party_size,
                "description": f"Rail Ticket: ₹{ticket_per_person:,.0f} x {party_size} + Feeder Autos: ₹{local_feeder:,.0f}"
            }
        }

    # 3. Highway Express Bus
    elif travel_mode == "bus":
        local_feeder = 200.0  # ₹90 origin + ₹110 destination
        ticket_per_person = round(max(60.0, eff_dist * 1.48), 0)
        total_tickets = round(ticket_per_person * party_size, 0)
        total_cost = total_tickets + local_feeder

        return {
            "total_cost": total_cost,
            "ticket_cost_per_person": ticket_per_person,
            "tickets_total": total_tickets,
            "local_shared_transit_cost": local_feeder,
            "fare_source": "bus_calibrated_model",
            "fare_currency": "₹",
            "fare_breakdown": {
                "ticket_per_person": ticket_per_person,
                "tickets_total": total_tickets,
                "local_feeder": local_feeder,
                "party_size": party_size,
                "description": f"Bus Ticket: ₹{ticket_per_person:,.0f} x {party_size} + Feeder Autos: ₹{local_feeder:,.0f}"
            }
        }

    # 4. Shared Outstation Cab
    elif travel_mode == "shared_cab":
        ticket_per_person = round(max(120.0, eff_dist * 2.25), 0)
        total_tickets = round(ticket_per_person * party_size, 0)
        local_pickup = round(80.0 * party_size, 0)
        total_cost = total_tickets + local_pickup

        return {
            "total_cost": total_cost,
            "ticket_cost_per_person": ticket_per_person,
            "tickets_total": total_tickets,
            "local_shared_transit_cost": local_pickup,
            "fare_source": "shared_cab_model",
            "fare_currency": "₹",
            "fare_breakdown": {
                "ticket_per_person": ticket_per_person,
                "tickets_total": total_tickets,
                "local_pickup": local_pickup,
                "party_size": party_size,
                "description": f"Cab Seat: ₹{ticket_per_person:,.0f} x {party_size} + Local Door Pickup: ₹{local_pickup:,.0f}"
            }
        }

    # Default fallback
    return {
        "total_cost": round(eff_dist * 5.0, 0),
        "ticket_cost_per_person": round(eff_dist * 5.0 / party_size, 0),
        "tickets_total": round(eff_dist * 5.0, 0),
        "local_shared_transit_cost": 0.0,
        "fare_source": "general_estimate",
        "fare_currency": "₹",
        "fare_breakdown": {}
    }


def get_google_maps_status() -> Dict[str, Any]:
    """Returns the current operational status of the Google Maps API integration."""
    st = dict(api_status_info)
    st["status"] = "active" if st.get("active") else ("configured" if st.get("key_configured") else "missing")
    return st
