import uuid
from typing import List, Dict, Optional, Any
from tools.registry import tool
from tools.cache import cache_db
from models.schemas import Hotel, Restaurant, BookingResponse

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

@tool(name="search_hotels", description="Search accommodations by location, preferred tier, and party size.")
def search_hotels(location: str, budget_tier: str = "standard_hotel", party_size: int = 2) -> List[Dict[str, Any]]:
    loc_lower = location.strip().lower()
    matches = [h for h in CURATED_HOTELS if loc_lower in h["location"].lower() or h["location"].lower() in loc_lower]

    if budget_tier and matches:
        tier_matches = [h for h in matches if h["tier"] == budget_tier]
        if tier_matches:
            return tier_matches

    if matches:
        return matches

    # Dynamically produce realistic stay option for unknown destination
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
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"
        },
        {
            "id": f"HTL-{location[:3].upper()}-02",
            "name": f"{location.title()} Backpacker & Travelers Lodge",
            "location": location.title(),
            "tier": "budget_hostel",
            "price_per_night": 900.0,
            "rating": 4.2,
            "amenities": ["Lockers", "Community Kitchen", "Wi-Fi"],
            "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500"
        }
    ]

@tool(name="search_restaurants", description="Search roadside dhabas, local eateries, and restaurants by location and cuisine preference.")
def search_restaurants(location: str, cuisine_pref: str = "all", budget_tier: str = "standard") -> List[Dict[str, Any]]:
    loc_lower = location.strip().lower()
    pref_lower = cuisine_pref.strip().lower()

    matches = []
    for r in CURATED_RESTAURANTS:
        loc_match = loc_lower in r["location"].lower() or r["location"].lower() in loc_lower
        is_highway_corridor = "highway" in r["location"].lower() or "nh-" in r["location"].lower()

        if loc_match or (is_highway_corridor and "highway" in loc_lower):
            if pref_lower == "all" or pref_lower in r["cuisine_type"].lower() or (pref_lower == "roadside_dhaba" and r["is_dhaba"]):
                matches.append(r)
            elif pref_lower == "all":
                matches.append(r)

    if not matches:
        # Fallback to any restaurant matching location or return curated dhabas
        matches = [r for r in CURATED_RESTAURANTS if loc_lower in r["location"].lower()]

    if not matches:
        is_dhaba = "dhaba" in pref_lower
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
                "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500"
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
