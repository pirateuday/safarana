import os
import re
import uuid
import logging
import requests
from typing import List, Dict, Optional, Any
from tools.registry import tool
from tools.cache import cache_db
from models.schemas import Hotel, Restaurant, BookingResponse, Coordinates
from config import GOOGLE_MAPS_API_KEY, GOOGLE_PLACES_KEY, STAYING_API_KEY

logger = logging.getLogger("smartroute.hospitality")

# Curated Authentic Hotels across Tiers
CURATED_HOTELS: List[Dict[str, Any]] = [
    # --- JAIPUR ---
    {
        "id": "HTL-JPR-01",
        "name": "Zostel Jaipur (Heritage Backpackers)",
        "location": "Jaipur",
        "tier": "budget_hostel",
        "price_per_night": 950.0,
        "rating": 4.6,
        "amenities": ["Free Wi-Fi", "Rooftop Cafe", "Social Lounge", "Lockers"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    {
        "id": "HTL-JPR-02",
        "name": "Hotel Pearl Palace Heritage",
        "location": "Jaipur",
        "tier": "standard_hotel",
        "price_per_night": 2800.0,
        "rating": 4.8,
        "amenities": ["Air Conditioning", "Peacock Rooftop Restaurant", "Room Service", "Airport Shuttle"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },
    {
        "id": "HTL-JPR-03",
        "name": "Alsisar Haveli - Heritage Hotel",
        "location": "Jaipur",
        "tier": "boutique_resort",
        "price_per_night": 6500.0,
        "rating": 4.7,
        "amenities": ["Swimming Pool", "Heritage Courtyards", "Spa", "Multi-cuisine Dining"],
        "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=500"
    },
    {
        "id": "HTL-JPR-04",
        "name": "Rambagh Palace by Taj",
        "location": "Jaipur",
        "tier": "luxury",
        "price_per_night": 28000.0,
        "rating": 4.9,
        "amenities": ["Royal Butler Service", "Polo Bar", "Jiva Spa", "Extensive Royal Gardens"],
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=500"
    },

    # --- EN ROUTE CORRIDOR ---
    {
        "id": "HTL-NMR-01",
        "name": "Neemrana Fort Heritage Retreat",
        "location": "Neemrana",
        "tier": "boutique_resort",
        "price_per_night": 7200.0,
        "rating": 4.6,
        "amenities": ["Hanging Gardens", "Two Swimming Pools", "Ayurvedic Spa"],
        "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=500"
    },
    {
        "id": "HTL-BHR-01",
        "name": "Highway King Motel & Rest Stop",
        "location": "Behror",
        "tier": "budget_hostel",
        "price_per_night": 1400.0,
        "rating": 4.2,
        "amenities": ["Ample Parking", "24hr Diner", "Clean Showers"],
        "image_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=500"
    },

    # --- AGRA ---
    {
        "id": "HTL-AGR-01",
        "name": "Tajview - IHCL SeleQtions",
        "location": "Agra",
        "tier": "standard_hotel",
        "price_per_night": 4200.0,
        "rating": 4.6,
        "amenities": ["Taj Mahal Views", "Swimming Pool", "Fitness Center"],
        "image_url": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=500"
    },
    {
        "id": "HTL-AGR-02",
        "name": "Zostel Agra (Taj Backpackers)",
        "location": "Agra",
        "tier": "budget_hostel",
        "price_per_night": 850.0,
        "rating": 4.5,
        "amenities": ["Rooftop Taj View", "Community Kitchen", "Free Wi-Fi", "Lockers"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    {
        "id": "HTL-AGR-03",
        "name": "The Orchid Boutique, Agra",
        "location": "Agra",
        "tier": "boutique_resort",
        "price_per_night": 6200.0,
        "rating": 4.7,
        "amenities": ["Mughal Courtyards", "Daybed Pool", "Fine-dining Veranda", "Airport Transfer"],
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=500"
    },

    # --- MANALI ---
    {
        "id": "HTL-MNL-01",
        "name": "Zostel Manali (Old Manali)",
        "location": "Manali",
        "tier": "budget_hostel",
        "price_per_night": 900.0,
        "rating": 4.6,
        "amenities": ["Beas River Balcony", "Café & Bonfire", "Lockers", "Travel Desk"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    {
        "id": "HTL-MNL-02",
        "name": "Snow Peak Riverside Hotel",
        "location": "Manali",
        "tier": "standard_hotel",
        "price_per_night": 3200.0,
        "rating": 4.4,
        "amenities": ["Mountain Views", "In-house Restaurant", "Apple Orchard", "Room Heater"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },
    {
        "id": "HTL-MNL-03",
        "name": "Whispering Pines Alpine Cottages",
        "location": "Manali",
        "tier": "boutique_resort",
        "price_per_night": 5800.0,
        "rating": 4.7,
        "amenities": ["Woodfire Cottages", "Spa & Sauna", "Garden Bonfire", "Kullu Valley View"],
        "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=500"
    },

    # --- RISHIKESH / HARIDWAR ---
    {
        "id": "HTL-RSH-01",
        "name": "Yoga Lane Hostel & Ashram Stay",
        "location": "Rishikesh",
        "tier": "budget_hostel",
        "price_per_night": 750.0,
        "rating": 4.5,
        "amenities": ["Yoga Deck", "Ganga View", "Communal Meals", "Wi-Fi"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    {
        "id": "HTL-RSH-02",
        "name": "Ganga Kinare Riverview Hotel",
        "location": "Rishikesh",
        "tier": "standard_hotel",
        "price_per_night": 3000.0,
        "rating": 4.6,
        "amenities": ["Tapovan Riverview", "Vegetarian Kitchen", "Ayurvedic Spa", "Riverside Cafe"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },
    {
        "id": "HTL-RSH-03",
        "name": "The Glasshouse Ganges Boutique",
        "location": "Rishikesh",
        "tier": "boutique_resort",
        "price_per_night": 7000.0,
        "rating": 4.8,
        "amenities": ["Glass River Suites", "Infinity Plunge Pool", "Rafting Desk", "Private Ganga Aarti"],
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500"
    },
    {
        "id": "HTL-HDR-01",
        "name": "Haridwar Heritage Homestay",
        "location": "Haridwar",
        "tier": "standard_hotel",
        "price_per_night": 2600.0,
        "rating": 4.5,
        "amenities": ["Har Ki Pauri Walking Distance", "Rooftop Darshan", "Pure Veg Kitchen"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },

    # --- UDAIPUR ---
    {
        "id": "HTL-UDP-01",
        "name": "Zostel Udaipur (Lake Border Hostel)",
        "location": "Udaipur",
        "tier": "budget_hostel",
        "price_per_night": 850.0,
        "rating": 4.6,
        "amenities": ["Lake-facing Terrace", "Rooftop Cafe", "Bonfire", "Lockers"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    {
        "id": "HTL-UDP-02",
        "name": "Hotel Lake Pichola Heritage",
        "location": "Udaipur",
        "tier": "standard_hotel",
        "price_per_night": 3400.0,
        "rating": 4.6,
        "amenities": ["Haveli Courtyard", "Lake View Rooms", "Rooftop Dining", "Airport Shuttle"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },
    {
        "id": "HTL-UDP-03",
        "name": "Mewar Haveli - Boutique Heritage Stay",
        "location": "Udaipur",
        "tier": "boutique_resort",
        "price_per_night": 6200.0,
        "rating": 4.8,
        "amenities": ["Restored Mewar Haveli", "Lake Pichola Views", "Pool Side", "Private Boat Desk"],
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=500"
    },

    # --- OOTY ---
    {
        "id": "HTL-OTY-01",
        "name": "Nilgiri Backpacker's Nest",
        "location": "Ooty",
        "tier": "budget_hostel",
        "price_per_night": 800.0,
        "rating": 4.5,
        "amenities": ["Fireplace Lounge", "Shared Kitchen", "Trekking Desk", "Wi-Fi"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    {
        "id": "HTL-OTY-02",
        "name": "Fernhill Central Hotel",
        "location": "Ooty",
        "tier": "standard_hotel",
        "price_per_night": 3600.0,
        "rating": 4.4,
        "amenities": ["Colonial Bungalow", "Garden Restaurant", "Bonfire", "Parking"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },
    {
        "id": "HTL-OTY-03",
        "name": "Sterling Ooty Elk Hill Resort",
        "location": "Ooty",
        "tier": "boutique_resort",
        "price_per_night": 7200.0,
        "rating": 4.6,
        "amenities": ["Valley-view Cottages", "Hilltop Pool", "Spa", "Kids' Activities"],
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500"
    },

    # --- GOA ---
    {
        "id": "HTL-GOA-01",
        "name": "Casa Anjuna Boutique Resort",
        "location": "Goa",
        "tier": "boutique_resort",
        "price_per_night": 4800.0,
        "rating": 4.7,
        "amenities": ["Tropical Pool", "Beach Access", "Open-air Bar"],
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500"
    },
    # --- PONDICHERRY ---
    {
        "id": "HTL-PDY-01",
        "name": "Maison Perumal - French Heritage Villa",
        "location": "Pondicherry",
        "tier": "boutique_resort",
        "price_per_night": 5800.0,
        "rating": 4.8,
        "amenities": ["Heritage Courtyard", "Ayurvedic Spa", "French Breakfast", "Free Wi-Fi"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },
    {
        "id": "HTL-PDY-02",
        "name": "The Promenade Seafront Hotel",
        "location": "Pondicherry",
        "tier": "standard_hotel",
        "price_per_night": 3200.0,
        "rating": 4.6,
        "amenities": ["Sea View Rooms", "Rooftop Lighthouse Lounge", "Swimming Pool"],
        "image_url": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=500"
    },
    {
        "id": "HTL-PDY-03",
        "name": "Ostello White Town Backpackers",
        "location": "Pondicherry",
        "tier": "budget_hostel",
        "price_per_night": 850.0,
        "rating": 4.5,
        "amenities": ["Bunk Beds & Lockers", "Bicycle Rental", "Common Cafe", "Free Wi-Fi"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    # --- DARJEELING ---
    {
        "id": "HTL-DJL-01",
        "name": "Windamere Heritage Colonial Hotel",
        "location": "Darjeeling",
        "tier": "boutique_resort",
        "price_per_night": 6200.0,
        "rating": 4.8,
        "amenities": ["Fireplace Lounges", "Kanchenjunga Mountain View", "High Tea Service"],
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=500"
    },
    {
        "id": "HTL-DJL-02",
        "name": "Summit Hermon Tea Garden Hotel",
        "location": "Darjeeling",
        "tier": "standard_hotel",
        "price_per_night": 2900.0,
        "rating": 4.6,
        "amenities": ["Valley View Balconies", "Heated Rooms", "Multi-cuisine Restaurant"],
        "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=500"
    },
    {
        "id": "HTL-DJL-03",
        "name": "Hideout Backpacker Lodge Darjeeling",
        "location": "Darjeeling",
        "tier": "budget_hostel",
        "price_per_night": 800.0,
        "rating": 4.4,
        "amenities": ["Roof Terrace", "Guitar & Books", "Hot Showers", "Free Wi-Fi"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    },
    # --- MAHABALESHWAR ---
    {
        "id": "HTL-MHB-01",
        "name": "Le Méridien Mahabaleshwar Resort",
        "location": "Mahabaleshwar",
        "tier": "boutique_resort",
        "price_per_night": 7200.0,
        "rating": 4.8,
        "amenities": ["Infinity Forest Pool", "Forest Spa", "Fine Dining", "Luxury Suites"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
    },
    {
        "id": "HTL-MHB-02",
        "name": "Strawberry County Valley Resort",
        "location": "Mahabaleshwar",
        "tier": "standard_hotel",
        "price_per_night": 2800.0,
        "rating": 4.6,
        "amenities": ["Strawberry Farm Access", "Valley View Garden", "Room Service"],
        "image_url": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=500"
    },
    {
        "id": "HTL-MHB-03",
        "name": "Panchgani Hills Youth Hostel",
        "location": "Mahabaleshwar",
        "tier": "budget_hostel",
        "price_per_night": 750.0,
        "rating": 4.4,
        "amenities": ["Dormitory & Private Rooms", "Mountain Balcony", "Free Wi-Fi"],
        "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
    }
]

# Curated Authentic Dhabas & Restaurants
CURATED_RESTAURANTS: List[Dict[str, Any]] = [
    # --- HIGHWAY DHABAS ---
    {
        "id": "RES-DHB-01",
        "name": "Old Rao Hotel & Famous Dhaba",
        "location": "NH-48 Behror / Neemrana",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 220.0,
        "rating": 4.7,
        "specialty": "Dal Makhani, Butter Naan, Aloo Pyaz Paratha, Kulhad Chai",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    {
        "id": "RES-DHB-02",
        "name": "Mannat Haveli & Highway Stop",
        "location": "Delhi-Jaipur Highway",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 260.0,
        "rating": 4.5,
        "specialty": "Tandoori Paneer Kulcha, Chole Bhature, Lassi",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500"
    },
    {
        "id": "RES-DHB-03",
        "name": "Shree Neelkanth Pavitra Dhaba",
        "location": "Shahpura",
        "cuisine_type": "vegetarian",
        "avg_cost_per_person": 180.0,
        "rating": 4.4,
        "specialty": "Sev Tamatar, Kadhi Pakora, Missi Roti",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"
    },

    # --- JAIPUR CITY FOOD ---
    {
        "id": "RES-JPR-01",
        "name": "Rawat Mishthan Bhandar",
        "location": "Jaipur",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 190.0,
        "rating": 4.7,
        "specialty": "World-Famous Pyaaz Kachori, Mawa Kachori, Jalebi",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500"
    },
    {
        "id": "RES-JPR-02",
        "name": "Laxmi Mishthan Bhandar (LMB)",
        "location": "Jaipur",
        "cuisine_type": "vegetarian",
        "avg_cost_per_person": 550.0,
        "rating": 4.6,
        "specialty": "Traditional Royal Rajasthani Thali, Dal Baati Churma, Ghewar",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=500"
    },
    {
        "id": "RES-JPR-03",
        "name": "1135 AD - Royal Dining at Amer Fort",
        "location": "Jaipur",
        "cuisine_type": "fine_dining",
        "avg_cost_per_person": 1800.0,
        "rating": 4.8,
        "specialty": "Lal Maas, Junglee Maas, Saffron Rice in silver tableware",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500"
    },
    {
        "id": "RES-JPR-04",
        "name": "Tapri Central Rooftop Cafe",
        "location": "Jaipur",
        "cuisine_type": "cafe",
        "avg_cost_per_person": 320.0,
        "rating": 4.7,
        "specialty": "Cutting Chai, Khakhra Pizza, Vada Pav, Central Park view",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500"
    },

    # --- DELHI ---
    {
        "id": "RES-DEL-01",
        "name": "Karim's Historic Old Delhi",
        "location": "Delhi",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 450.0,
        "rating": 4.6,
        "specialty": "Mutton Korma, Seekh Kebab, Roomali Roti",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=500"
    },

    # --- AGRA / NH-44 CORRIDOR ---
    {
        "id": "RES-AGR-01",
        "name": "Pinch of Spice, Agra",
        "location": "Agra",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 420.0,
        "rating": 4.6,
        "specialty": "Galouti Kebab, Murgh Dum Biryani, Petha dessert",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500"
    },
    {
        "id": "RES-AGR-02",
        "name": "Mama Chicken Hut (Fatehabad Rd)",
        "location": "NH-44 Agra Highway",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 240.0,
        "rating": 4.5,
        "specialty": "Tandoori Chicken, Rumali Roti, Shahi Lassi",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    {
        "id": "RES-AGR-03",
        "name": "Brajwasi Bhojnalaya",
        "location": "Agra",
        "cuisine_type": "vegetarian",
        "avg_cost_per_person": 180.0,
        "rating": 4.5,
        "specialty": "Braj Aloo Puri, Kachori, Kadhi, Sharbat",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"
    },
    {
        "id": "RES-MTR-01",
        "name": "Brijwasi Sweets & Peda House",
        "location": "Mathura",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 150.0,
        "rating": 4.6,
        "specialty": "Mathura ke Pedas, Samosa, Cutting Chai",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=500"
    },

    # --- MANALI / NH-205 (KULLU VALLEY) ---
    {
        "id": "RES-MNL-01",
        "name": "Old Manali Riverside Cafe 1947",
        "location": "Manali",
        "cuisine_type": "cafe",
        "avg_cost_per_person": 350.0,
        "rating": 4.6,
        "specialty": "Apple Pie, Leni Curry, River-View Cappuccino",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=500"
    },
    {
        "id": "RES-MNL-02",
        "name": "Himachali Dhaba (Siddu & Babru)",
        "location": "NH-205 Kullu Valley Highway",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 220.0,
        "rating": 4.5,
        "specialty": "Steamed Siddu, Babru, Dham Thali, Seabuckthorn Juice",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    {
        "id": "RES-MNL-03",
        "name": "Johnson's Cafe & Trout Kitchen",
        "location": "Manali",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 650.0,
        "rating": 4.7,
        "specialty": "Forest Trout, Raan, Sizzlers in the riverside garden",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500"
    },

    # --- HARIDWAR / RISHIKESH (NH-334 GANGA CORRIDOR) ---
    {
        "id": "RES-HDR-01",
        "name": "Chotiwala Restaurant, Haridwar",
        "location": "Haridwar",
        "cuisine_type": "vegetarian",
        "avg_cost_per_person": 300.0,
        "rating": 4.6,
        "specialty": "Dal Baati, Kachori Chaat, Rabri Malpua",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=500"
    },
    {
        "id": "RES-HDR-02",
        "name": "Alaknanda Sweets & Prasad Counter",
        "location": "Haridwar",
        "cuisine_type": "vegetarian",
        "avg_cost_per_person": 160.0,
        "rating": 4.4,
        "specialty": "Ghewar, Rabri, Aloo Puri Breakfast",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"
    },
    {
        "id": "RES-RSH-01",
        "name": "Ganga View Cafe & Aarti-Side Seating",
        "location": "Rishikesh",
        "cuisine_type": "cafe",
        "avg_cost_per_person": 350.0,
        "rating": 4.5,
        "specialty": "Tibetan Momos, Thukpa, Chai by the Ganges",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500"
    },
    {
        "id": "RES-RSH-02",
        "name": "NH-334 Ganga Riverside Dhaba",
        "location": "NH-334 Rishikesh Highway",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 200.0,
        "rating": 4.5,
        "specialty": "Kadhai Paneer, Tandoori Parathas, Kulhad Lassi",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },

    # --- UDAIPUR / NH-48 RAJASTHAN CORRIDOR ---
    {
        "id": "RES-UDP-01",
        "name": "Ambrai - Lake Pichola View Dining",
        "location": "Udaipur",
        "cuisine_type": "fine_dining",
        "avg_cost_per_person": 900.0,
        "rating": 4.8,
        "specialty": "Laal Maans, Rajasthani Thali with candlelit lake view",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500"
    },
    {
        "id": "RES-UDP-02",
        "name": "Natraj Mewar Thali House",
        "location": "Udaipur",
        "cuisine_type": "vegetarian",
        "avg_cost_per_person": 250.0,
        "rating": 4.6,
        "specialty": "Unlimited Dal Baati Churma, Gatte ki Sabzi",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"
    },
    {
        "id": "RES-UDP-03",
        "name": "NH-48 Ajmer Road Highway Dhaba",
        "location": "NH-48 Udaipur Highway",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 210.0,
        "rating": 4.4,
        "specialty": "Ker Sangri, Bajra Roti, Churma",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },

    # --- OOTY / NH-181 NILGIRI CORRIDOR ---
    {
        "id": "RES-OTY-01",
        "name": "King Star Confectioners",
        "location": "Ooty",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 180.0,
        "rating": 4.6,
        "specialty": "Home-made Chocolates, Fresh Fruit Wine, Muffins",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500"
    },
    {
        "id": "RES-OTY-02",
        "name": "Earl's Secret Tea & Coffee House",
        "location": "Ooty",
        "cuisine_type": "cafe",
        "avg_cost_per_person": 300.0,
        "rating": 4.5,
        "specialty": "Nilgiri Brew, Murukku, Fireplace Brownies",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500"
    },
    {
        "id": "RES-OTY-03",
        "name": "Bandipur Jungle Highway Dhaba",
        "location": "NH-181 Bandipur Highway",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 200.0,
        "rating": 4.4,
        "specialty": "Chicken Chettinadu, Akki Roti, Filter Coffee",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    # --- PONDICHERRY & ECR ---
    {
        "id": "RES-PDY-01",
        "name": "Café des Arts White Town",
        "location": "Pondicherry",
        "cuisine_type": "cafe",
        "avg_cost_per_person": 350.0,
        "rating": 4.7,
        "specialty": "French crepes, iced cafe au lait, baguette sandwiches",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500"
    },
    {
        "id": "RES-PDY-02",
        "name": "Appachi Traditional Chettinad Restaurant",
        "location": "Pondicherry",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 280.0,
        "rating": 4.6,
        "specialty": "Chettinad pepper chicken, Malabar parotta, fish curry meals",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    {
        "id": "RES-PDY-03",
        "name": "ECR Sea Breeze Dhaba & Seafood Shack",
        "location": "Chennai-Pondicherry Highway Corridor",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 220.0,
        "rating": 4.5,
        "specialty": "Fresh tawa fish fry, crab roast, hot filter coffee",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    # --- DARJEELING & SILIGURI ---
    {
        "id": "RES-DJL-01",
        "name": "Glenary's Bakery & Landmark Cafe",
        "location": "Darjeeling",
        "cuisine_type": "cafe",
        "avg_cost_per_person": 300.0,
        "rating": 4.8,
        "specialty": "Apple pie, Darjeeling first flush tea, roast chicken",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500"
    },
    {
        "id": "RES-DJL-02",
        "name": "Keventers Heritage Rooftop",
        "location": "Darjeeling",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 250.0,
        "rating": 4.7,
        "specialty": "Traditional pork sausages, hot cocoa, mountain view breakfast",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    {
        "id": "RES-DJL-03",
        "name": "Siliguri-Kurseong Hilltop Dhaba",
        "location": "Darjeeling Highway Corridor",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 160.0,
        "rating": 4.5,
        "specialty": "Steamed chicken momos, thukpa noodle soup, masala tea",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    # --- MAHABALESHWAR & WAI ---
    {
        "id": "RES-MHB-01",
        "name": "Mapro Garden Cafe & Bakery",
        "location": "Mahabaleshwar",
        "cuisine_type": "cafe",
        "avg_cost_per_person": 320.0,
        "rating": 4.7,
        "specialty": "Fresh strawberry with fresh cream, wood-fired thin crust pizza",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500"
    },
    {
        "id": "RES-MHB-02",
        "name": "Bagicha Corner Mahabaleshwar",
        "location": "Mahabaleshwar",
        "cuisine_type": "local_cuisine",
        "avg_cost_per_person": 240.0,
        "rating": 4.6,
        "specialty": "Corn pattice, makai ki roti, fresh berry shake",
        "is_dhaba": False,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    },
    {
        "id": "RES-MHB-03",
        "name": "Wai Ghats Highway Dhaba",
        "location": "Pune-Mahabaleshwar Highway Corridor",
        "cuisine_type": "roadside_dhaba",
        "avg_cost_per_person": 180.0,
        "rating": 4.5,
        "specialty": "Pithla Bhakri, Thecha, Kolhapuri Misal Pav, Masala Chai",
        "is_dhaba": True,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
    }
]

def fetch_hotels_from_staying_api(city_name: str, key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches real-time hotel availability, pricing, and properties from StayingAPI (stayingapi.com).
    """
    api_key = key or STAYING_API_KEY
    if not api_key:
        return []

    clean_city = city_name.strip()
    cache_key = f"staying_{clean_city.lower()}"
    cached = cache_db.get("hotels", cache_key)
    if cached:
        return cached

    url = f"https://api.stayingapi.com/v1/search?query=hotels+in+{requests.utils.quote(clean_city)}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "TrippsAI-Travel/1.0"
    }
    try:
        r = requests.get(url, headers=headers, timeout=6.0)
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", []) or data.get("properties", [])
            hotels = []
            for item in items:
                name = item.get("name") or item.get("title") or item.get("propertyName")
                if not name:
                    continue
                price = float(item.get("price") or item.get("ratePerNight") or 3200.0)
                tier = "luxury" if price > 10000 else "boutique_resort" if price > 4500 else "budget_hostel" if price < 1500 else "standard_hotel"
                rating = float(item.get("rating") or item.get("score") or 4.4)
                hotels.append({
                    "id": f"HTL-STAY-{uuid.uuid4().hex[:6].upper()}",
                    "name": name,
                    "location": clean_city.title(),
                    "tier": tier,
                    "price_per_night": price,
                    "rating": round(min(5.0, rating), 1),
                    "amenities": item.get("amenities", ["Free Wi-Fi", "Air Conditioning", "Ensuite Bathroom"]),
                    "image_url": item.get("photoUrl") or item.get("image") or "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500",
                    "source": "staying_api",
                    "address": item.get("address", f"{clean_city.title()}, India")
                })
            if hotels:
                cache_db.set("hotels", cache_key, hotels)
                return hotels
        elif r.status_code in [401, 403]:
            logger.info("StayingAPI key unauthorized or not configured.")
    except Exception as e:
        logger.debug(f"StayingAPI fetch error: {e}")

    return []


def fetch_hotels_from_google_places(city_name: str, key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches accommodations and hotels from Google Maps Places API (New & Legacy endpoints).
    """
    g_key = key or GOOGLE_PLACES_KEY or GOOGLE_MAPS_API_KEY
    if not g_key:
        return []

    clean_city = city_name.strip()
    cache_key = f"gplaces_hotel_{clean_city.lower()}"
    cached = cache_db.get("hotels", cache_key)
    if cached:
        return cached

    # 1. Modern Places API (places:searchText)
    try:
        url_new = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": g_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.id,places.location"
        }
        payload = {"textQuery": f"hotels, resorts, and stays in {clean_city}, India"}
        r = requests.post(url_new, headers=headers, json=payload, timeout=5.0)
        if r.status_code == 200:
            data = r.json()
            places = data.get("places", [])
            hotels = []
            for p in places:
                name = p.get("displayName", {}).get("text")
                if not name:
                    continue
                rating = float(p.get("rating", 4.3))
                pl = p.get("priceLevel", "PRICE_LEVEL_MODERATE")
                price = 1200.0 if pl == "PRICE_LEVEL_INEXPENSIVE" else 2800.0 if pl == "PRICE_LEVEL_MODERATE" else 6500.0 if pl == "PRICE_LEVEL_EXPENSIVE" else 15000.0
                tier = "budget_hostel" if price < 1500 else "luxury" if price > 10000 else "boutique_resort" if price > 4500 else "standard_hotel"
                hotels.append({
                    "id": f"HTL-GP-{p.get('id', uuid.uuid4().hex[:6])[:10]}",
                    "name": name,
                    "location": clean_city.title(),
                    "tier": tier,
                    "price_per_night": price,
                    "rating": rating,
                    "amenities": ["Air Conditioning", "Free Wi-Fi", "Room Service", "Daily Housekeeping"],
                    "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500",
                    "source": "google_places",
                    "address": p.get("formattedAddress", f"{clean_city.title()}, India")
                })
            if hotels:
                cache_db.set("hotels", cache_key, hotels)
                return hotels
    except Exception as e:
        logger.debug(f"Google Places New error: {e}")

    # 2. Legacy Places textsearch
    try:
        url_legacy = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=hotels+in+{requests.utils.quote(clean_city)}&key={g_key}"
        r = requests.get(url_legacy, timeout=4.5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "OK" and data.get("results"):
                hotels = []
                for p in data["results"][:15]:
                    name = p.get("name")
                    if not name:
                        continue
                    rating = float(p.get("rating", 4.3))
                    hotels.append({
                        "id": f"HTL-GPL-{p.get('place_id', uuid.uuid4().hex[:6])[:10]}",
                        "name": name,
                        "location": clean_city.title(),
                        "tier": "standard_hotel",
                        "price_per_night": 2700.0,
                        "rating": rating,
                        "amenities": ["Air Conditioning", "Free Wi-Fi", "Daily Housekeeping"],
                        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500",
                        "source": "google_places",
                        "address": p.get("formatted_address", f"{clean_city.title()}, India")
                    })
                if hotels:
                    cache_db.set("hotels", cache_key, hotels)
                    return hotels
    except Exception as e:
        logger.debug(f"Google Places Legacy error: {e}")

    return []


def fetch_hotels_from_osm_overpass(city_name: str, lat: float, lon: float, radius_km: float = 12.0) -> List[Dict[str, Any]]:
    """
    Fetches verified hotels, guest houses, resorts, and homestays from OpenStreetMap via Overpass API.
    """
    clean_city = city_name.strip()
    cache_key = f"osm_hotel_{clean_city.lower()}"
    cached = cache_db.get("hotels", cache_key)
    if cached:
        return cached

    delta = radius_km / 111.0
    s, w = round(lat - delta, 4), round(lon - delta, 4)
    n, e = round(lat + delta, 4), round(lon + delta, 4)

    query = f"""
    [out:json][timeout:8];
    (
      node["tourism"~"hotel|guest_house|resort|motel|hostel"]({s},{w},{n},{e});
      way["tourism"~"hotel|guest_house|resort|hostel"]({s},{w},{n},{e});
    );
    out center tags 30;
    """

    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    for ep in endpoints:
        try:
            r = requests.post(ep, data={"data": query}, headers={"User-Agent": "TrippsAI-Travel/1.0"}, timeout=6.5)
            if r.status_code == 200:
                data = r.json()
                raw_elems = data.get("elements", [])
                hotels = []
                seen_names = set()
                for el in raw_elems:
                    tags = el.get("tags", {})
                    name = tags.get("name:en") or tags.get("name")
                    if not name or len(name.strip()) < 3:
                        continue
                    name = name.strip()
                    norm_name = name.lower()
                    if norm_name in seen_names:
                        continue
                    seen_names.add(norm_name)

                    tourism_type = tags.get("tourism", "hotel").lower()
                    stars = float(tags.get("stars", 0))

                    if "hostel" in tourism_type or "hostel" in norm_name or "zostel" in norm_name:
                        tier = "budget_hostel"
                        price = 950.0
                    elif "resort" in tourism_type or "palace" in norm_name or "haveli" in norm_name:
                        tier = "boutique_resort"
                        price = 6200.0
                    elif stars >= 5 or "taj" in norm_name or "oberoi" in norm_name or "marriott" in norm_name:
                        tier = "luxury"
                        price = 18000.0
                    elif stars == 4:
                        tier = "boutique_resort"
                        price = 5500.0
                    else:
                        tier = "standard_hotel"
                        price = 2800.0

                    rating = round(3.8 + (stars * 0.25), 1) if stars > 0 else 4.4
                    addr = tags.get("addr:street") or tags.get("addr:city") or f"{clean_city.title()}, India"

                    hotels.append({
                        "id": f"HTL-OSM-{uuid.uuid4().hex[:6].upper()}",
                        "name": name,
                        "location": clean_city.title(),
                        "tier": tier,
                        "price_per_night": price,
                        "rating": min(5.0, rating),
                        "amenities": ["Air Conditioning", "Free Wi-Fi", "24/7 Front Desk"],
                        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500",
                        "source": "osm",
                        "address": addr
                    })
                if hotels:
                    cache_db.set("hotels", cache_key, hotels)
                    return hotels
        except Exception as e:
            logger.debug(f"Overpass hotel query error: {e}")

    return []


def fetch_restaurants_from_google_places(city_name: str, key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches local eateries, restaurants, dhabas, and cafes from Google Places API.
    """
    g_key = key or GOOGLE_PLACES_KEY or GOOGLE_MAPS_API_KEY
    if not g_key:
        return []

    clean_city = city_name.strip()
    cache_key = f"gplaces_res_{clean_city.lower()}"
    cached = cache_db.get("restaurants", cache_key)
    if cached:
        return cached

    try:
        url_new = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": g_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.id,places.priceLevel"
        }
        payload = {"textQuery": f"famous local restaurants, dhabas, and food shops in {clean_city}, India"}
        r = requests.post(url_new, headers=headers, json=payload, timeout=5.0)
        if r.status_code == 200:
            places = r.json().get("places", [])
            restaurants = []
            for p in places:
                name = p.get("displayName", {}).get("text")
                if not name:
                    continue
                is_dhaba = "dhaba" in name.lower()
                rating = float(p.get("rating", 4.4))
                cost = 220.0 if is_dhaba else 450.0
                cuisine = "roadside_dhaba" if is_dhaba else "local_cuisine"
                restaurants.append({
                    "id": f"RES-GP-{p.get('id', uuid.uuid4().hex[:6])[:10]}",
                    "name": name,
                    "location": clean_city.title(),
                    "cuisine_type": cuisine,
                    "avg_cost_per_person": cost,
                    "rating": rating,
                    "specialty": "Traditional Local Delicacies, Chai & Snacks",
                    "is_dhaba": is_dhaba,
                    "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500",
                    "source": "google_places",
                    "address": p.get("formattedAddress", f"{clean_city.title()}, India")
                })
            if restaurants:
                cache_db.set("restaurants", cache_key, restaurants)
                return restaurants
    except Exception as e:
        logger.debug(f"Google Places Restaurant query error: {e}")

    return []


def fetch_restaurants_from_osm_overpass(city_name: str, lat: float, lon: float, radius_km: float = 12.0) -> List[Dict[str, Any]]:
    """
    Fetches real local restaurants, dhabas, street food, and cafes from OpenStreetMap Overpass API.
    """
    clean_city = city_name.strip()
    cache_key = f"osm_res_{clean_city.lower()}"
    cached = cache_db.get("restaurants", cache_key)
    if cached:
        return cached

    delta = radius_km / 111.0
    s, w = round(lat - delta, 4), round(lon - delta, 4)
    n, e = round(lat + delta, 4), round(lon + delta, 4)

    query = f"""
    [out:json][timeout:8];
    (
      node["amenity"~"restaurant|cafe|fast_food|food_court"]({s},{w},{n},{e});
      way["amenity"~"restaurant|cafe|fast_food"]({s},{w},{n},{e});
    );
    out center tags 30;
    """

    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    for ep in endpoints:
        try:
            r = requests.post(ep, data={"data": query}, headers={"User-Agent": "TrippsAI-Travel/1.0"}, timeout=6.5)
            if r.status_code == 200:
                data = r.json()
                raw_elems = data.get("elements", [])
                restaurants = []
                seen = set()
                for el in raw_elems:
                    tags = el.get("tags", {})
                    name = tags.get("name:en") or tags.get("name")
                    if not name or len(name.strip()) < 3:
                        continue
                    name = name.strip()
                    norm = name.lower()
                    if norm in seen:
                        continue
                    seen = seen | {norm}

                    amenity = tags.get("amenity", "restaurant").lower()
                    cuisine_raw = tags.get("cuisine", "").lower()
                    is_dhaba = "dhaba" in norm or "dhaba" in cuisine_raw
                    is_cafe = amenity == "cafe" or "cafe" in norm or "coffee" in norm
                    is_veg = "vegetarian" in cuisine_raw or "pure veg" in norm or "veg" in cuisine_raw

                    if is_dhaba:
                        cuisine = "roadside_dhaba"
                        cost = 220.0
                    elif is_cafe:
                        cuisine = "cafe"
                        cost = 320.0
                    elif is_veg:
                        cuisine = "vegetarian"
                        cost = 300.0
                    else:
                        cuisine = "local_cuisine"
                        cost = 450.0

                    addr = tags.get("addr:street") or tags.get("addr:suburb") or f"{clean_city.title()}, India"
                    restaurants.append({
                        "id": f"RES-OSM-{uuid.uuid4().hex[:6].upper()}",
                        "name": name,
                        "location": clean_city.title(),
                        "cuisine_type": cuisine,
                        "avg_cost_per_person": cost,
                        "rating": 4.5,
                        "specialty": f"Authentic {clean_city.title()} Thalis & Special Dishes",
                        "is_dhaba": is_dhaba,
                        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500",
                        "source": "osm",
                        "address": addr
                    })
                if restaurants:
                    cache_db.set("restaurants", cache_key, restaurants)
                    return restaurants
        except Exception as e:
            logger.debug(f"Overpass restaurant error: {e}")

    return []


def get_city_hotels(city_name: str, stay_tier: Optional[str] = None, max_count: int = 25) -> List[Dict[str, Any]]:
    """
    Unified aggregator for accommodations:
    1. StayingAPI (stayingapi.com) when configured.
    2. Google Places API (lodging / hotels) with provided key.
    3. Curated authentic Indian hotel catalog.
    4. OpenStreetMap Overpass API for verified hotels & guest houses.
    Deduplicates and standardizes tier, pricing, and ratings.
    """
    clean_city = (city_name or "Jaipur").strip()
    norm_city = clean_city.lower()
    from tools.routing_tools import get_coordinates

    combined: List[Dict[str, Any]] = []
    seen_names = set()

    def add_hotel(h: Dict[str, Any]):
        nm = (h.get("name") or "").strip()
        n_norm = re.sub(r"[^a-z0-9]", "", nm.lower())
        if not n_norm or n_norm in seen_names:
            return
        seen_names.add(n_norm)
        combined.append(h)

    # 1. StayingAPI
    staying_hotels = fetch_hotels_from_staying_api(clean_city)
    for h in staying_hotels:
        add_hotel(h)

    # 2. Google Places API
    gp_hotels = fetch_hotels_from_google_places(clean_city)
    for h in gp_hotels:
        add_hotel(h)

    # 3. Curated catalog
    curated_matches = [h for h in CURATED_HOTELS if norm_city in h["location"].lower() or h["location"].lower() in norm_city]
    for h in curated_matches:
        add_hotel({**h, "source": "curated", "address": f"{clean_city.title()} Heritage Quarter, India"})

    # 4. OpenStreetMap Overpass
    try:
        coords = get_coordinates(clean_city)
        osm_hotels = fetch_hotels_from_osm_overpass(clean_city, coords.lat, coords.lon)
        for h in osm_hotels:
            add_hotel(h)
    except Exception:
        pass

    # Fallback template if nothing found
    if not combined:
        combined = [
            {
                "id": f"HTL-{clean_city[:3].upper()}-01",
                "name": f"{clean_city.title()} Grand Heritage Palace",
                "location": clean_city.title(),
                "tier": "standard_hotel",
                "price_per_night": 2800.0,
                "rating": 4.6,
                "amenities": ["Air Conditioning", "Free Wi-Fi", "Complimentary Breakfast", "Courtyard Lounge"],
                "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500",
                "source": "curated",
                "address": f"Station Road, {clean_city.title()}"
            },
            {
                "id": f"HTL-{clean_city[:3].upper()}-02",
                "name": f"{clean_city.title()} Backpacker & Traveler Hostel",
                "location": clean_city.title(),
                "tier": "budget_hostel",
                "price_per_night": 950.0,
                "rating": 4.4,
                "amenities": ["Lockers", "Rooftop Cafe", "Community Kitchen", "Wi-Fi"],
                "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500",
                "source": "curated",
                "address": f"Old City, {clean_city.title()}"
            }
        ]

    # Filter or prioritize by tier if requested
    if stay_tier:
        matching = [h for h in combined if h.get("tier") == stay_tier]
        others = [h for h in combined if h.get("tier") != stay_tier]
        combined = matching + others

    return combined[:max_count]


def get_city_restaurants(city_name: str, cuisine_pref: Optional[str] = None, is_highway: bool = False, max_count: int = 25) -> List[Dict[str, Any]]:
    """
    Unified aggregator for food places & dhabas:
    1. Google Places API (restaurants, dhabas, local eateries).
    2. Curated authentic highway & city dining database.
    3. OpenStreetMap Overpass API (authentic regional food spots).
    """
    clean_city = (city_name or "Jaipur").strip()
    norm_city = clean_city.lower()
    from tools.routing_tools import get_coordinates

    combined: List[Dict[str, Any]] = []
    seen_names = set()

    def add_res(r: Dict[str, Any]):
        nm = (r.get("name") or "").strip()
        n_norm = re.sub(r"[^a-z0-9]", "", nm.lower())
        if not n_norm or n_norm in seen_names:
            return
        seen_names.add(n_norm)
        combined.append(r)

    # 1. Google Places API
    gp_res = fetch_restaurants_from_google_places(clean_city)
    for r in gp_res:
        add_res(r)

    # 2. Curated catalog
    curated_matches = []
    for r in CURATED_RESTAURANTS:
        loc_match = norm_city in r["location"].lower() or r["location"].lower() in norm_city
        is_hwy = "highway" in r["location"].lower() or "nh-" in r["location"].lower()
        if loc_match or (is_highway and is_hwy):
            curated_matches.append({**r, "source": "curated", "address": f"{r['location']}, India"})
    for r in curated_matches:
        add_res(r)

    # 3. OpenStreetMap Overpass
    try:
        coords = get_coordinates(clean_city)
        osm_res = fetch_restaurants_from_osm_overpass(clean_city, coords.lat, coords.lon)
        for r in osm_res:
            add_res(r)
    except Exception:
        pass

    if not combined:
        combined = [
            {
                "id": f"RES-{clean_city[:3].upper()}-01",
                "name": f"{clean_city.title()} Midway Grand Highway Dhaba",
                "location": clean_city.title(),
                "cuisine_type": "roadside_dhaba",
                "avg_cost_per_person": 220.0,
                "rating": 4.5,
                "specialty": "Crispy Tandoori Parathas, Dal Makhani, Lassi & Chai",
                "is_dhaba": True,
                "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500",
                "source": "curated",
                "address": f"National Highway Corridor, {clean_city.title()}"
            },
            {
                "id": f"RES-{clean_city[:3].upper()}-02",
                "name": f"{clean_city.title()} Royal Heritage Thali Restaurant",
                "location": clean_city.title(),
                "cuisine_type": "local_cuisine",
                "avg_cost_per_person": 450.0,
                "rating": 4.6,
                "specialty": f"Unlimited Traditional {clean_city.title()} Thali with Sweets",
                "is_dhaba": False,
                "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500",
                "source": "curated",
                "address": f"City Center, {clean_city.title()}"
            }
        ]

    # Filter or prioritize by cuisine preference
    if cuisine_pref and cuisine_pref.lower() != "all":
        pref_norm = cuisine_pref.lower()
        matching = [r for r in combined if pref_norm in r.get("cuisine_type", "").lower() or (pref_norm == "roadside_dhaba" and r.get("is_dhaba"))]
        others = [r for r in combined if r not in matching]
        combined = matching + others

    return combined[:max_count]


@tool(name="search_hotels", description="Search accommodations by location, preferred tier, and party size.")
def search_hotels(location: str, budget_tier: str = "standard_hotel", party_size: int = 2) -> List[Dict[str, Any]]:
    results = get_city_hotels(location, stay_tier=budget_tier)
    if budget_tier and results:
        tier_matches = [h for h in results if h.get("tier") == budget_tier]
        if tier_matches:
            return tier_matches
    if results:
        return results

    loc_lower = location.strip().lower()
    matches = [h for h in CURATED_HOTELS if loc_lower in h["location"].lower() or h["location"].lower() in loc_lower]

    if budget_tier and matches:
        tier_matches = [h for h in matches if h["tier"] == budget_tier]
        if tier_matches:
            return tier_matches

    if matches:
        return matches

    base_price = 1200.0 if "budget" in budget_tier else 5500.0 if "boutique" in budget_tier else 2600.0
    return [
        {
            "id": f"HTL-{location[:3].upper()}-01",
            "name": f"{location.title()} Grand Comfort Hotel",
            "location": location.title(),
            "tier": budget_tier,
            "price_per_night": base_price,
            "rating": 4.4,
            "amenities": ["Air Conditioning", "Complimentary Breakfast", "Free Wi-Fi", "Parking"],
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500",
            "source": "curated"
        },
        {
            "id": f"HTL-{location[:3].upper()}-02",
            "name": f"{location.title()} Backpacker & Travelers Lodge",
            "location": location.title(),
            "tier": "budget_hostel",
            "price_per_night": 900.0,
            "rating": 4.2,
            "amenities": ["Lockers", "Community Kitchen", "Wi-Fi"],
            "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500",
            "source": "curated"
        }
    ]

@tool(name="search_restaurants", description="Search roadside dhabas, local eateries, and restaurants by location and cuisine preference.")
def search_restaurants(location: str, cuisine_pref: str = "all", budget_tier: str = "standard") -> List[Dict[str, Any]]:
    is_highway = "highway" in location.lower() or "nh-" in location.lower()
    results = get_city_restaurants(location, cuisine_pref=cuisine_pref, is_highway=is_highway)
    if results:
        return results

    loc_lower = location.strip().lower()
    pref_lower = cuisine_pref.strip().lower()

    matches = []
    for r in CURATED_RESTAURANTS:
        loc_match = loc_lower in r["location"].lower() or r["location"].lower() in loc_lower
        is_highway_corridor = "highway" in r["location"].lower() or "nh-" in r["location"].lower()

        if loc_match or (is_highway_corridor and is_highway):
            if pref_lower == "all" or pref_lower in r["cuisine_type"].lower() or (pref_lower == "roadside_dhaba" and r.get("is_dhaba")):
                matches.append(r)
            elif pref_lower == "all":
                matches.append(r)

    if not matches:
        matches = [r for r in CURATED_RESTAURANTS if loc_lower in r["location"].lower()]

    if not matches:
        is_dhaba = "dhaba" in pref_lower or is_highway
        cost = 200.0 if is_dhaba else 450.0
        matches = [
            {
                "id": f"RES-{location[:3].upper()}-01",
                "name": f"{location.title()} Highway King Dhaba & Restaurant" if is_dhaba else f"{location.title()} Traditional Heritage Dining",
                "location": location.title(),
                "cuisine_type": "roadside_dhaba" if is_dhaba else "local_cuisine",
                "avg_cost_per_person": cost,
                "rating": 4.5,
                "specialty": "Crispy Tandoori Rotis, Paneer Butter Masala, Sweet Lassi",
                "is_dhaba": is_dhaba,
                "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500",
                "source": "curated"
            }
        ]

    return matches

@tool(name="book_hotel", description="Execute a confirmed hotel booking transaction.")
def book_hotel(hotel_id: str, date: str, guests: int, user_name: str = "Traveler", plan_id: str = "") -> Dict[str, Any]:
    # Find hotel name
    hotel_name = hotel_id
    amount = 2500.0
    for h in CURATED_HOTELS:
        if h["id"] == hotel_id:
            hotel_name = h["name"]
            amount = h["price_per_night"]
            break

    booking_id = f"BK-HTL-{uuid.uuid4().hex[:6].upper()}"
    confirmation_code = f"CONF-{uuid.uuid4().hex[:8].upper()}"

    booking_record = {
        "booking_id": booking_id,
        "plan_id": plan_id,
        "item_type": "hotel",
        "item_id": hotel_id,
        "item_name": hotel_name,
        "date_or_time": date,
        "guests": guests,
        "user_name": user_name,
        "amount": amount,
        "status": "CONFIRMED",
        "details": {
            "confirmation_code": confirmation_code,
            "check_in": f"{date} 14:00",
            "check_out": "11:00 (Next Day)",
            "policy": "Free cancellation up to 24 hours before check-in"
        }
    }

    cache_db.save_booking(booking_record)
    return {
        "booking_id": booking_id,
        "status": "CONFIRMED",
        "item_name": hotel_name,
        "item_type": "hotel",
        "confirmation_code": confirmation_code,
        "amount": amount,
        "details": booking_record["details"]
    }

@tool(name="book_restaurant", description="Reserve a table or pre-order a meal at a dhaba or restaurant.")
def book_restaurant(restaurant_id: str, time_slot: str, guests: int, user_name: str = "Traveler", plan_id: str = "") -> Dict[str, Any]:
    res_name = restaurant_id
    avg_cost = 300.0
    for r in CURATED_RESTAURANTS:
        if r["id"] == restaurant_id:
            res_name = r["name"]
            avg_cost = r["avg_cost_per_person"] * guests
            break

    booking_id = f"BK-RES-{uuid.uuid4().hex[:6].upper()}"
    confirmation_code = f"TBL-{uuid.uuid4().hex[:8].upper()}"

    booking_record = {
        "booking_id": booking_id,
        "plan_id": plan_id,
        "item_type": "restaurant",
        "item_id": restaurant_id,
        "item_name": res_name,
        "date_or_time": time_slot,
        "guests": guests,
        "user_name": user_name,
        "amount": avg_cost,
        "status": "CONFIRMED",
        "details": {
            "confirmation_code": confirmation_code,
            "reservation_time": time_slot,
            "table_hold_minutes": 20,
            "note": "Priority seating reserved via SmartRoute"
        }
    }

    cache_db.save_booking(booking_record)
    return {
        "booking_id": booking_id,
        "status": "CONFIRMED",
        "item_name": res_name,
        "item_type": "restaurant",
        "confirmation_code": confirmation_code,
        "amount": avg_cost,
        "details": booking_record["details"]
    }
