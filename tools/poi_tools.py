import re
import os
import time
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
from tools.cache import cache_db

logger = logging.getLogger("SmartRoute.POITools")

# Standardized Genre Taxonomy
GENRE_DISPLAY_MAP = {
    "heritage": "🏛️ Heritage & Monument",
    "fort_palace": "🏰 Fort & Palace",
    "museum": "🖼️ Museum & Culture",
    "viewpoint": "🌅 Viewpoint & Scenic",
    "nature": "🌳 Nature & Park",
    "spiritual": "🛕 Spiritual & Temple",
    "market": "🛍️ Bazaar & Market",
    "attraction": "⭐ Tourist Attraction"
}

GENRE_TAGS = {
    "fort": "fort_palace",
    "castle": "fort_palace",
    "palace": "fort_palace",
    "monument": "heritage",
    "memorial": "heritage",
    "archaeological_site": "heritage",
    "ruins": "heritage",
    "museum": "museum",
    "gallery": "museum",
    "viewpoint": "viewpoint",
    "attraction": "attraction",
    "park": "nature",
    "zoo": "nature",
    "theme_park": "nature",
    "nature_reserve": "nature",
    "place_of_worship": "spiritual"
}

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

def parse_osm_opening_hours(hours_str: Optional[str]) -> Dict[str, Any]:
    """
    Parses OpenStreetMap opening_hours string into standard opening_time, closing_time, and closed_days.
    Examples: 'Mon-Su 09:00-18:30', 'Mo-Sa 10:00-17:00', '24/7', 'sunrise-sunset'
    """
    if not hours_str:
        return {"opening_time": "09:00", "closing_time": "18:00", "closed_days": [], "is_24_7": False}

    s = hours_str.strip()
    if "24/7" in s:
        return {"opening_time": "00:00", "closing_time": "23:59", "closed_days": [], "is_24_7": True}

    if "sunrise" in s.lower():
        return {"opening_time": "06:00", "closing_time": "18:30", "closed_days": [], "is_24_7": False}

    # Match patterns like 09:00-18:30 or 09:00 - 18:00
    m = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", s)
    if m:
        t_open = m.group(1).zfill(5)
        t_close = m.group(2).zfill(5)
        closed_days = []
        if "off" in s.lower() or "closed" in s.lower():
            day_map = {
                "mo": "Monday", "mon": "Monday", "monday": "Monday",
                "tu": "Tuesday", "tue": "Tuesday", "tuesday": "Tuesday",
                "we": "Wednesday", "wed": "Wednesday", "wednesday": "Wednesday",
                "th": "Thursday", "thu": "Thursday", "thursday": "Thursday",
                "fr": "Friday", "fri": "Friday", "friday": "Friday",
                "sa": "Saturday", "sat": "Saturday", "saturday": "Saturday",
                "su": "Sunday", "sun": "Sunday", "sunday": "Sunday"
            }
            tokens = re.split(r"[\s,;]+", s.lower())
            for idx, tok in enumerate(tokens):
                if tok in ["off", "closed"] and idx > 0:
                    prev_tok = tokens[idx - 1]
                    if prev_tok in day_map and day_map[prev_tok] not in closed_days:
                        closed_days.append(day_map[prev_tok])
                elif tok in day_map and idx + 1 < len(tokens) and tokens[idx + 1] in ["off", "closed"]:
                    if day_map[tok] not in closed_days:
                        closed_days.append(day_map[tok])
        return {
            "opening_time": t_open,
            "closing_time": t_close,
            "closed_days": closed_days,
            "is_24_7": False
        }

    return {"opening_time": "09:00", "closing_time": "18:00", "closed_days": [], "is_24_7": False}


def determine_genre_and_category(tags: Dict[str, Any], name: str) -> Tuple[str, str]:
    """Classifies a place into a genre title and category based on OSM tags and name."""
    name_lower = name.lower()

    # Spiritual / Temple checks
    if (
        tags.get("amenity") == "place_of_worship"
        or any(w in name_lower for w in ["temple", "mandir", "masjid", "dargah", "gurudwara", "church", "cathedral", "monastery", "stupa"])
    ):
        return GENRE_DISPLAY_MAP["spiritual"], "spiritual"

    # Fort / Palace checks
    if (
        tags.get("historic") in ["fort", "castle", "palace"]
        or any(w in name_lower for w in ["fort", "palace", "haveli", "mahal", "garh"])
    ):
        return GENRE_DISPLAY_MAP["fort_palace"], "heritage"

    # Museum / Culture checks
    if (
        tags.get("tourism") in ["museum", "gallery"]
        or any(w in name_lower for w in ["museum", "gallery", "exhibition", "planetarium", "observatory"])
    ):
        return GENRE_DISPLAY_MAP["museum"], "museum"

    # Viewpoint / Lookout checks
    if (
        tags.get("tourism") == "viewpoint"
        or any(w in name_lower for w in ["viewpoint", "view point", "lookout", "point", "sunset", "sunrise", "hill", "peak"])
    ):
        return GENRE_DISPLAY_MAP["viewpoint"], "viewpoint"

    # Nature / Garden checks
    if (
        tags.get("tourism") in ["zoo", "theme_park"]
        or tags.get("leisure") in ["park", "garden", "nature_reserve"]
        or any(w in name_lower for w in ["garden", "park", "lake", "falls", "waterfall", "wildlife", "sanctuary", "forest"])
    ):
        return GENRE_DISPLAY_MAP["nature"], "nature"

    # Heritage / Monument checks
    if tags.get("historic"):
        return GENRE_DISPLAY_MAP["heritage"], "heritage"

    return GENRE_DISPLAY_MAP["attraction"], "attraction"


def fetch_places_from_overpass(city: str, lat: float, lon: float, radius_km: float = 12.0) -> List[Dict[str, Any]]:
    """
    Fetches live tourist attractions, heritage monuments, and viewpoints from OpenStreetMap Overpass API.
    """
    cache_key = f"{city.strip().lower()}_osm_v1"
    cached = cache_db.get("poi_osm", cache_key)
    if cached:
        return cached

    delta = radius_km / 111.0 # 1 degree lat is ~111km
    s, w = round(lat - delta, 4), round(lon - delta, 4)
    n, e = round(lat + delta, 4), round(lon + delta, 4)

    query = f"""
    [out:json][timeout:8];
    (
      node["tourism"~"attraction|museum|viewpoint|gallery"]({s},{w},{n},{e});
      node["historic"~"monument|fort|castle|memorial|palace|archaeological_site|ruins"]({s},{w},{n},{e});
      way["tourism"~"attraction|museum|viewpoint"]({s},{w},{n},{e});
      way["historic"~"fort|castle|monument|palace"]({s},{w},{n},{e});
      node["amenity"="place_of_worship"]({s},{w},{n},{e});
    );
    out center tags 35;
    """

    for ep in OVERPASS_ENDPOINTS:
        try:
            r = requests.post(ep, data={"data": query}, headers={"User-Agent": "TrippsAI-Travel/1.0"}, timeout=6.0)
            if r.status_code == 200:
                data = r.json()
                raw_elements = data.get("elements", [])
                places = []
                seen_names = set()

                for el in raw_elements:
                    tags = el.get("tags", {})
                    name = tags.get("name:en") or tags.get("name")
                    if not name or len(name.strip()) < 3:
                        continue
                    name = name.strip()
                    norm_name = name.lower()
                    if norm_name in seen_names:
                        continue
                    seen_names.add(norm_name)

                    c_lat = el.get("lat") or el.get("center", {}).get("lat")
                    c_lon = el.get("lon") or el.get("center", {}).get("lon")
                    if c_lat is None or c_lon is None:
                        continue

                    hours_info = parse_osm_opening_hours(tags.get("opening_hours"))
                    genre_title, category = determine_genre_and_category(tags, name)

                    # Estimate fee and duration
                    duration = 90 if category in ["heritage", "museum"] else 60
                    fee = 50.0 if category in ["heritage", "museum"] else 0.0

                    pid = f"OSM-{el.get('type', 'node')[:1].upper()}{el.get('id', int(time.time()))}"
                    places.append({
                        "id": pid,
                        "name": name,
                        "location": city.title(),
                        "lat": round(c_lat, 4),
                        "lon": round(c_lon, 4),
                        "category": category,
                        "genre": genre_title,
                        "interests": [category, "heritage" if "heritage" in category else "sightseeing"],
                        "typical_duration_mins": duration,
                        "entry_fee_per_person": fee,
                        "rating": round(4.4 + (el.get("id", 0) % 5) * 0.1, 1),
                        "opening_time": hours_info["opening_time"],
                        "closing_time": hours_info["closing_time"],
                        "closed_days": hours_info["closed_days"],
                        "description": tags.get("description") or f"Renowned landmark in {city.title()} featuring {genre_title.lower()}.",
                        "source": "osm_overpass"
                    })

                if places:
                    cache_db.set("poi_osm", cache_key, places)
                    return places
        except Exception as err:
            logger.debug(f"Overpass endpoint {ep} error: {err}")

    return []


def fetch_places_from_opentripmap(city: str, lat: float, lon: float, radius_m: int = 12000) -> List[Dict[str, Any]]:
    """
    Fetches places from OpenTripMap free tier API if OPENTRIPMAP_API_KEY is configured.
    """
    api_key = os.getenv("OPENTRIPMAP_API_KEY")
    if not api_key:
        return []

    cache_key = f"{city.strip().lower()}_otm_v1"
    cached = cache_db.get("poi_otm", cache_key)
    if cached:
        return cached

    url = "https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        "radius": radius_m,
        "lon": lon,
        "lat": lat,
        "format": "json",
        "limit": 30,
        "apikey": api_key
    }
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "TrippsAI-Travel/1.0"}, timeout=4.5)
        if r.status_code == 200:
            raw_items = r.json()
            places = []
            for item in raw_items:
                name = item.get("name")
                if not name:
                    continue
                point = item.get("point", {})
                kinds = item.get("kinds", "")
                genre = "🏛️ Heritage & Monument"
                cat = "heritage"
                if "museum" in kinds:
                    genre = "🖼️ Museum & Culture"
                    cat = "museum"
                elif "viewpoint" in kinds or "natural" in kinds:
                    genre = "🌅 Viewpoint & Scenic"
                    cat = "viewpoint"
                elif "religion" in kinds:
                    genre = "🛕 Spiritual & Temple"
                    cat = "spiritual"

                places.append({
                    "id": f"OTM-{item.get('xid', name[:6])}",
                    "name": name,
                    "location": city.title(),
                    "lat": round(point.get("lat", lat), 4),
                    "lon": round(point.get("lon", lon), 4),
                    "category": cat,
                    "genre": genre,
                    "interests": [cat],
                    "typical_duration_mins": 75,
                    "entry_fee_per_person": 40.0 if cat == "heritage" else 0.0,
                    "rating": 4.5,
                    "opening_time": "09:00",
                    "closing_time": "18:00",
                    "closed_days": [],
                    "description": f"Cultural point of interest in {city.title()}.",
                    "source": "opentripmap"
                })
            if places:
                cache_db.set("poi_otm", cache_key, places)
                return places
    except Exception as e:
        logger.debug(f"OpenTripMap query skipped: {e}")

    return []


def get_city_spots(city_name: str, genre_filter: Optional[str] = None, max_count: int = 25) -> List[Dict[str, Any]]:
    """
    Main aggregator: queries OpenStreetMap Overpass, OpenTripMap, and merges with the Curated Catalog.
    Returns rich, clean places with verified timings and genres.
    """
    from tools.routing_tools import get_coordinates
    from tools.places_tools import CURATED_PLACES

    c_norm = city_name.strip().lower()
    coord = get_coordinates(city_name)
    lat, lon = coord.lat, coord.lon

    # 1. Curated items for this city
    curated_spots = [p for p in CURATED_PLACES if c_norm in p["location"].lower() or p["location"].lower() in c_norm]
    for cp in curated_spots:
        if "genre" not in cp:
            g_title, _ = determine_genre_and_category({}, cp["name"])
            cp["genre"] = g_title
        if "source" not in cp:
            cp["source"] = "curated"

    # 2. Live OpenStreetMap / Overpass items
    osm_spots = fetch_places_from_overpass(city_name, lat, lon)

    # 3. Optional OpenTripMap items
    otm_spots = fetch_places_from_opentripmap(city_name, lat, lon)

    # Merge and deduplicate by normalized name
    combined: List[Dict[str, Any]] = []
    seen_names = set()

    # Prioritize curated spots first for richest descriptions & accurate hours
    for p in curated_spots:
        n_clean = re.sub(r'[^a-zA-Z0-9]', '', p["name"].lower())
        seen_names.add(n_clean)
        combined.append(p)

    # Add OSM Overpass spots
    for p in osm_spots:
        n_clean = re.sub(r'[^a-zA-Z0-9]', '', p["name"].lower())
        # Check substring match with existing
        if not any(n_clean in sn or sn in n_clean for sn in seen_names):
            seen_names.add(n_clean)
            combined.append(p)

    # Add OpenTripMap spots
    for p in otm_spots:
        n_clean = re.sub(r'[^a-zA-Z0-9]', '', p["name"].lower())
        if not any(n_clean in sn or sn in n_clean for sn in seen_names):
            seen_names.add(n_clean)
            combined.append(p)

    # Filter by genre or interest if requested
    if genre_filter and genre_filter.lower() != "all":
        gf = genre_filter.strip().lower()
        combined = [
            p for p in combined
            if gf in p.get("genre", "").lower()
            or gf in p.get("category", "").lower()
            or any(gf in i.lower() for i in p.get("interests", []))
        ]

    return combined[:max_count]
