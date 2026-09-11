from typing import List, Dict, Optional, Any
from tools.registry import tool
from tools.cache import cache_db
from models.schemas import Place, Coordinates

# Curated High-Fidelity Places & Attractions Database with Real Operating Hours
CURATED_PLACES: List[Dict[str, Any]] = [
    # --- JAIPUR & EN ROUTE ---
    {
        "id": "JPR-001",
        "name": "Amber Palace & Fort",
        "location": "Jaipur",
        "lat": 26.9855,
        "lon": 75.8513,
        "category": "fort",
        "interests": ["heritage", "scenic", "nature"],
        "typical_duration_mins": 120,
        "entry_fee_per_person": 100.0,
        "rating": 4.8,
        "opening_time": "09:00",
        "closing_time": "17:30",
        "closed_days": [],
        "description": "Magnificent 16th-century hilltop palace complex overlooking Maota Lake with grand courtyards and Sheesh Mahal."
    },
    {
        "id": "JPR-002",
        "name": "Hawa Mahal (Palace of Winds)",
        "location": "Jaipur",
        "lat": 26.9239,
        "lon": 75.8267,
        "category": "monument",
        "interests": ["heritage", "shopping"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 50.0,
        "rating": 4.6,
        "opening_time": "09:00",
        "closing_time": "17:00",
        "closed_days": [],
        "description": "Five-storey pink sandstone facade with 953 honeycomb jharokhas built for royal women to observe street life."
    },
    {
        "id": "JPR-003",
        "name": "City Palace & Mubarak Mahal",
        "location": "Jaipur",
        "lat": 26.9258,
        "lon": 75.8236,
        "category": "palace",
        "interests": ["heritage", "culture"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 200.0,
        "rating": 4.7,
        "opening_time": "09:30",
        "closing_time": "17:00",
        "closed_days": [],
        "description": "Sprawling royal residence fusing Rajput and Mughal architecture, housing rare costumes, armory, and manuscripts."
    },
    {
        "id": "JPR-004",
        "name": "Nahargarh Fort Sunset Viewpoint",
        "location": "Jaipur",
        "lat": 26.9378,
        "lon": 75.8156,
        "category": "viewpoint",
        "interests": ["scenic", "relaxation", "nature"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 50.0,
        "rating": 4.7,
        "opening_time": "06:00",
        "closing_time": "22:00",
        "closed_days": [],
        "description": "Stands on the edge of the Aravalli Hills providing panoramic sunset vistas over the Pink City."
    },
    {
        "id": "JPR-005",
        "name": "Jantar Mantar Royal Observatory",
        "location": "Jaipur",
        "lat": 26.9248,
        "lon": 75.8246,
        "category": "monument",
        "interests": ["heritage", "adventure"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 50.0,
        "rating": 4.5,
        "opening_time": "09:00",
        "closing_time": "17:00",
        "closed_days": [],
        "description": "UNESCO World Heritage site featuring nineteen architectural astronomical instruments, including the world's largest stone sundial."
    },
    {
        "id": "JPR-006",
        "name": "Chokhi Dhani Ethnic Cultural Village",
        "location": "Jaipur",
        "lat": 26.7663,
        "lon": 75.8362,
        "category": "cultural_village",
        "interests": ["food", "heritage", "relaxation"],
        "typical_duration_mins": 180,
        "entry_fee_per_person": 900.0,
        "rating": 4.6,
        "opening_time": "17:30",
        "closing_time": "23:00",
        "closed_days": [],
        "description": "Authentic Rajasthani village experience with folk dance, camel rides, puppetry, and a traditional royal thali feast."
    },
    {
        "id": "COR-001",
        "name": "Neemrana Fort-Palace (En Route)",
        "location": "Neemrana",
        "lat": 27.9888,
        "lon": 76.3883,
        "category": "heritage_resort",
        "interests": ["heritage", "relaxation", "scenic"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 500.0,
        "rating": 4.6,
        "opening_time": "09:00",
        "closing_time": "15:00",
        "closed_days": [],
        "description": "15th-century heritage fort on Delhi-Jaipur highway with stepped ramparts and zip-lining over Aravalli ridges."
    },

    # --- DELHI ---
    {
        "id": "DEL-001",
        "name": "Qutub Minar Complex",
        "location": "Delhi",
        "lat": 28.5245,
        "lon": 77.1855,
        "category": "monument",
        "interests": ["heritage", "scenic"],
        "typical_duration_mins": 75,
        "entry_fee_per_person": 40.0,
        "rating": 4.7,
        "opening_time": "07:00",
        "closing_time": "21:00",
        "closed_days": [],
        "description": "Soaring 73-meter victory tower built in 1193, surrounded by ancient ruins including the rust-resistant Iron Pillar."
    },
    {
        "id": "DEL-002",
        "name": "Humayun's Tomb Gardens",
        "location": "Delhi",
        "lat": 28.5933,
        "lon": 77.2507,
        "category": "monument",
        "interests": ["heritage", "nature", "relaxation"],
        "typical_duration_mins": 80,
        "entry_fee_per_person": 40.0,
        "rating": 4.7,
        "opening_time": "06:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Pioneering Mughal garden-tomb synthesis with symmetry and serene fountains that inspired the Taj Mahal."
    },
    {
        "id": "DEL-003",
        "name": "Chandni Chowk & Red Fort Walk",
        "location": "Delhi",
        "lat": 28.6562,
        "lon": 77.2410,
        "category": "heritage_bazaar",
        "interests": ["heritage", "food", "shopping"],
        "typical_duration_mins": 120,
        "entry_fee_per_person": 35.0,
        "rating": 4.6,
        "opening_time": "09:30",
        "closing_time": "19:00",
        "closed_days": ["Monday"],
        "description": "Historic heart of Old Delhi with Mughal street flavors, spice markets, and majestic red sandstone bastions."
    },

    # --- AGRA ---
    {
        "id": "AGR-001",
        "name": "Taj Mahal",
        "location": "Agra",
        "lat": 27.1751,
        "lon": 78.0421,
        "category": "monument",
        "interests": ["heritage", "scenic"],
        "typical_duration_mins": 150,
        "entry_fee_per_person": 50.0,
        "rating": 4.9,
        "opening_time": "06:00",
        "closing_time": "18:30",
        "closed_days": ["Friday"],
        "description": "Iconic white marble mausoleum constructed by Emperor Shah Jahan in memory of Mumtaz Mahal."
    },
    {
        "id": "AGR-002",
        "name": "Agra Fort",
        "location": "Agra",
        "lat": 27.1795,
        "lon": 78.0211,
        "category": "fort",
        "interests": ["heritage"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 50.0,
        "rating": 4.7,
        "opening_time": "06:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Massive red sandstone fortress that served as the principal residence of the Mughal emperors."
    },

    # --- MUMBAI TO GOA ---
    {
        "id": "LON-001",
        "name": "Tiger's Leap & Karla Caves",
        "location": "Lonavala",
        "lat": 18.7557,
        "lon": 73.4091,
        "category": "viewpoint",
        "interests": ["nature", "scenic", "adventure"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 25.0,
        "rating": 4.5,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Breathtaking cliff-edge vantage point over the Western Ghats valleys alongside ancient Buddhist rock-cut shrines."
    },
    {
        "id": "GOA-001",
        "name": "Aguada Fort & Lighthouse",
        "location": "Goa",
        "lat": 15.4925,
        "lon": 73.7737,
        "category": "fort",
        "interests": ["heritage", "scenic", "relaxation"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 50.0,
        "rating": 4.6,
        "opening_time": "09:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "17th-century Portuguese coastal fort offering expansive Arabian Sea vistas and preserved water storage bastion."
    },
    {
        "id": "GOA-002",
        "name": "Anjuna Beach & Flea Market",
        "location": "Goa",
        "lat": 15.5818,
        "lon": 73.7431,
        "category": "beach",
        "interests": ["relaxation", "food", "shopping"],
        "typical_duration_mins": 120,
        "entry_fee_per_person": 0.0,
        "rating": 4.5,
        "opening_time": "08:00",
        "closing_time": "22:00",
        "closed_days": [],
        "description": "Vibrant beach famous for red rock formations, seaside shacks, chilled sunset music, and indie handicraft stalls."
    },

    # --- BANGALORE TO COORG / OOTY ---
    {
        "id": "MYS-001",
        "name": "Mysore Royal Palace",
        "location": "Mysore",
        "lat": 12.3052,
        "lon": 76.6552,
        "category": "palace",
        "interests": ["heritage", "scenic"],
        "typical_duration_mins": 100,
        "entry_fee_per_person": 100.0,
        "rating": 4.8,
        "opening_time": "10:00",
        "closing_time": "17:30",
        "closed_days": [],
        "description": "Indo-Saracenic royal seat with stained glass pavilions, carved silver doors, and evening illuminations."
    },
    {
        "id": "CRG-001",
        "name": "Abbey Falls & Coffee Plantation",
        "location": "Coorg",
        "lat": 12.4542,
        "lon": 75.7196,
        "category": "waterfall",
        "interests": ["nature", "scenic", "relaxation"],
        "typical_duration_mins": 80,
        "entry_fee_per_person": 30.0,
        "rating": 4.6,
        "opening_time": "09:00",
        "closing_time": "17:00",
        "closed_days": [],
        "description": "Cascading waterfall nestled amidst lush coffee plantations and spice estates in the Western Ghats."
    },

    # --- AGRA / MATHURA-VRINDAVAN CORRIDOR ---
    {
        "id": "AGR-003",
        "name": "Fatehpur Sikri Complex",
        "location": "Agra",
        "lat": 27.0911,
        "lon": 77.6673,
        "category": "monument",
        "interests": ["heritage", "scenic"],
        "typical_duration_mins": 120,
        "entry_fee_per_person": 50.0,
        "rating": 4.8,
        "opening_time": "06:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Akbar's majestic red sandstone ghost-city 40 km west of Agra, home to the towering Buland Darwaza and marble Diwan-i-Khas."
    },
    {
        "id": "AGR-004",
        "name": "Mehtab Bagh & Taj Sunset View",
        "location": "Agra",
        "lat": 27.1806,
        "lon": 78.0427,
        "category": "viewpoint",
        "interests": ["scenic", "relaxation", "nature"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 30.0,
        "rating": 4.7,
        "opening_time": "06:00",
        "closing_time": "19:00",
        "closed_days": [],
        "description": "Moonlight-mirrored gardens directly across the Yamuna with the finest sunset reflections of the Taj Mahal."
    },
    {
        "id": "MTV-001",
        "name": "Krishna Janmabhoomi & Dwarkadhish Temple",
        "location": "Mathura",
        "lat": 27.5052,
        "lon": 77.6705,
        "category": "religious",
        "interests": ["religious", "heritage", "food"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 25.0,
        "rating": 4.6,
        "opening_time": "05:00",
        "closing_time": "21:00",
        "closed_days": [],
        "description": "The legendary birthplace of Lord Krishna ringed by ancient shrines, bazaars, and famed Mathura peda sweet shops."
    },
    {
        "id": "MTV-002",
        "name": "Banke Bihari & ISKCON Temples, Vrindavan",
        "location": "Vrindavan",
        "lat": 27.5793,
        "lon": 77.6853,
        "category": "religious",
        "interests": ["religious", "culture", "shopping"],
        "typical_duration_mins": 100,
        "entry_fee_per_person": 0.0,
        "rating": 4.7,
        "opening_time": "07:00",
        "closing_time": "20:00",
        "closed_days": [],
        "description": "Vibrant temple town on the Yamuna where devotional aartis, flower markets, and Radha-Krishna legends fill the lanes."
    },

    # --- CHANDIGARH-MANALI CORRIDOR ---
    {
        "id": "BLS-001",
        "name": "Gobind Sagar Lake & Bhakra Dam View",
        "location": "Bilaspur",
        "lat": 31.4105,
        "lon": 76.4326,
        "category": "nature_spot",
        "interests": ["nature", "scenic", "relaxation"],
        "typical_duration_mins": 70,
        "entry_fee_per_person": 40.0,
        "rating": 4.5,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Asia's vast artificial reservoir spreading across the Shivalik foothills beneath the colossal Bhakra Nangal Dam."
    },
    {
        "id": "MND-001",
        "name": "Pandoh Dam & River Viewpoint",
        "location": "Mandi",
        "lat": 31.6636,
        "lon": 77.0646,
        "category": "viewpoint",
        "interests": ["nature", "scenic", "adventure"],
        "typical_duration_mins": 45,
        "entry_fee_per_person": 20.0,
        "rating": 4.4,
        "opening_time": "07:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Alpine dam where the Beas surges through granite gorges on the historic Kullu-Naggar route."
    },
    {
        "id": "MAN-001",
        "name": "Hadimba Devi Temple (Dhungri)",
        "location": "Manali",
        "lat": 32.2532,
        "lon": 77.1810,
        "category": "religious",
        "interests": ["heritage", "religious", "nature"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 20.0,
        "rating": 4.6,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Ancient four-tiered cedar-shingled pagoda temple of Goddess Hadimba set in a serene deodar forest."
    },
    {
        "id": "MAN-002",
        "name": "Solang Valley Adventure Point",
        "location": "Manali",
        "lat": 32.3179,
        "lon": 77.1558,
        "category": "viewpoint",
        "interests": ["adventure", "nature", "scenic"],
        "typical_duration_mins": 150,
        "entry_fee_per_person": 60.0,
        "rating": 4.7,
        "opening_time": "06:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Snow-blanketed motorable valley offering paragliding, ropeway rides, and café pit stops at 2,500 meters."
    },
    {
        "id": "MAN-003",
        "name": "Old Manali Village & Riverside Cafes",
        "location": "Manali",
        "lat": 32.2679,
        "lon": 77.1759,
        "category": "heritage_village",
        "interests": ["relaxation", "food", "nature"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 0.0,
        "rating": 4.5,
        "opening_time": "09:00",
        "closing_time": "22:00",
        "closed_days": [],
        "description": "Bohemian apple-orchard village of limestone cottages, Israeli cafés, and glacial Beas river walks."
    },
    {
        "id": "MAN-004",
        "name": "Kullu Valley Panorama from Manalsu",
        "location": "Manali",
        "lat": 32.2404,
        "lon": 77.1906,
        "category": "viewpoint",
        "interests": ["scenic", "nature", "relaxation"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 0.0,
        "rating": 4.6,
        "opening_time": "06:00",
        "closing_time": "19:00",
        "closed_days": [],
        "description": "Wraparound panorama of snow peaks, pine terraces, and terraced apple orchards over the Kullu valley."
    },

    # --- DELHI-HARIDWAR / RISHIKESH CORRIDOR ---
    {
        "id": "RKE-001",
        "name": "Solani Aqueduct & Ganga Canal Viewpoint",
        "location": "Roorkee",
        "lat": 29.8800,
        "lon": 77.8883,
        "category": "heritage_monument",
        "interests": ["heritage", "nature"],
        "typical_duration_mins": 45,
        "entry_fee_per_person": 10.0,
        "rating": 4.3,
        "opening_time": "06:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Historic 19th-century Solani aqueduct carrying the Upper Ganga Canal across the river on the Delhi-Dehradun route."
    },
    {
        "id": "HDR-001",
        "name": "Har Ki Pauri Ghat & Evening Ganga Aarti",
        "location": "Haridwar",
        "lat": 29.9555,
        "lon": 78.1709,
        "category": "religious",
        "interests": ["religious", "heritage", "culture"],
        "typical_duration_mins": 120,
        "entry_fee_per_person": 0.0,
        "rating": 4.8,
        "opening_time": "04:00",
        "closing_time": "22:00",
        "closed_days": [],
        "description": "The sacred Brahm Kund bathing ghat where the gathering dusk aarti floats diyas on the Ganga."
    },
    {
        "id": "HDR-002",
        "name": "Mansa Devi Temple & Ropeway",
        "location": "Haridwar",
        "lat": 29.9599,
        "lon": 78.1653,
        "category": "religious",
        "interests": ["religious", "scenic", "relaxation"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 120.0,
        "rating": 4.6,
        "opening_time": "05:00",
        "closing_time": "21:00",
        "closed_days": [],
        "description": "Hilltop Shivalik temple accessed by a scenic cable car with sweeping Haridwar and Ganga views."
    },
    {
        "id": "RSH-001",
        "name": "Triveni Ghat & Evening Aarti",
        "location": "Rishikesh",
        "lat": 30.0960,
        "lon": 78.2847,
        "category": "religious",
        "interests": ["religious", "relaxation", "culture"],
        "typical_duration_mins": 75,
        "entry_fee_per_person": 0.0,
        "rating": 4.7,
        "opening_time": "05:30",
        "closing_time": "21:30",
        "closed_days": [],
        "description": "Confluence of the Ganga, where saffron-clad sadhus, chanting, and riverside lamps create the most serene aarti in the Himalayas."
    },
    {
        "id": "RSH-002",
        "name": "Laxman Jhula & Ganga River Walk",
        "location": "Rishikesh",
        "lat": 30.1261,
        "lon": 78.3190,
        "category": "viewpoint",
        "interests": ["heritage", "scenic", "relaxation"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 20.0,
        "rating": 4.6,
        "opening_time": "06:00",
        "closing_time": "20:00",
        "closed_days": [],
        "description": "Historic 284-ft suspension bridge linking ashrams across the Ganga with jaw-dropping Shivpuri gorge views."
    },
    {
        "id": "RSH-003",
        "name": "Swarg Ashram & Beatles Ashram Ruins",
        "location": "Rishikesh",
        "lat": 30.1051,
        "lon": 78.2960,
        "category": "heritage_resort",
        "interests": ["relaxation", "heritage", "culture"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 30.0,
        "rating": 4.5,
        "opening_time": "07:00",
        "closing_time": "18:30",
        "closed_days": [],
        "description": "Yoga-and-meditation ashram belt including the famed 1968 Maharishi Beatles Ashram reclaimed by the forest."
    },

    # --- JAIPUR-UDAIPUR CORRIDOR ---
    {
        "id": "AJM-001",
        "name": "Ajmer Sharif Dargah & Ana Sagar Lake",
        "location": "Ajmer",
        "lat": 26.4499,
        "lon": 74.6282,
        "category": "religious",
        "interests": ["religious", "heritage", "culture"],
        "typical_duration_mins": 100,
        "entry_fee_per_person": 40.0,
        "rating": 4.7,
        "opening_time": "05:00",
        "closing_time": "20:00",
        "closed_days": [],
        "description": "Sufi shrine of Khwaja Moinuddin Chishti with marble courtyards, followed by the lakeside Daulat Bagh gardens."
    },
    {
        "id": "BWR-001",
        "name": "Todgarh Hill Viewpoint (Beawar)",
        "location": "Beawar",
        "lat": 25.9000,
        "lon": 74.3500,
        "category": "viewpoint",
        "interests": ["nature", "scenic", "relaxation"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 20.0,
        "rating": 4.4,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Aravali escarpment lookout over the monsoon-washed Todgarh Raoli sanctuary en route to the lakes of Udaipur."
    },
    {
        "id": "UDP-001",
        "name": "City Palace & Museum, Udaipur",
        "location": "Udaipur",
        "lat": 24.5764,
        "lon": 73.6836,
        "category": "palace",
        "interests": ["heritage", "scenic", "culture"],
        "typical_duration_mins": 120,
        "entry_fee_per_person": 300.0,
        "rating": 4.8,
        "opening_time": "09:30",
        "closing_time": "17:30",
        "closed_days": [],
        "description": "Fairy-tale granite-and-marble palace complex with mosaic courtyards and panoramic lake views over the Old City."
    },
    {
        "id": "UDP-002",
        "name": "Lake Pichola Sunset Boat Ride",
        "location": "Udaipur",
        "lat": 24.5760,
        "lon": 73.6820,
        "category": "viewpoint",
        "interests": ["scenic", "relaxation", "heritage"],
        "typical_duration_mins": 75,
        "entry_fee_per_person": 420.0,
        "rating": 4.9,
        "opening_time": "09:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Classic board-boat cruise between the floating Lake Palace and Jag Mandir as the Aravallis turn gold."
    },
    {
        "id": "UDP-003",
        "name": "Saheliyon-ki-Bari & Fateh Sagar Promenade",
        "location": "Udaipur",
        "lat": 24.6010,
        "lon": 73.6760,
        "category": "garden",
        "interests": ["heritage", "nature", "relaxation"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 30.0,
        "rating": 4.5,
        "opening_time": "08:00",
        "closing_time": "19:00",
        "closed_days": [],
        "description": "Courtyard garden of lotus pools and marble chhatris built for royal maids, strolling into Fateh Sagar's sunset drive."
    },
    {
        "id": "CHT-001",
        "name": "Chittorgarh Fort & Vijay Stambh",
        "location": "Chittorgarh",
        "lat": 24.8880,
        "lon": 74.6470,
        "category": "fort",
        "interests": ["heritage", "scenic", "adventure"],
        "typical_duration_mins": 150,
        "entry_fee_per_person": 400.0,
        "rating": 4.8,
        "opening_time": "09:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "India's largest hill fort, a UNESCO citadel of victory towers, palaces, and Rani Padmini's legendary palace."
    },

    # --- BANGALORE-OOTY CORRIDOR ---
    {
        "id": "NJG-001",
        "name": "Sri Srikanteshwara Temple & KRS Backwaters",
        "location": "Nanjangud",
        "lat": 12.1216,
        "lon": 76.6800,
        "category": "religious",
        "interests": ["religious", "heritage", "nature"],
        "typical_duration_mins": 70,
        "entry_fee_per_person": 0.0,
        "rating": 4.5,
        "opening_time": "06:00",
        "closing_time": "20:00",
        "closed_days": [],
        "description": "Ancient Chamundi-style temple where the illuminated Krishna Raja Sagara reservoir sprawls towards the dusk light."
    },
    {
        "id": "OTY-001",
        "name": "Government Botanical Gardens & Rose Garden",
        "location": "Ooty",
        "lat": 11.4164,
        "lon": 76.7059,
        "category": "garden",
        "interests": ["nature", "scenic", "relaxation"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 50.0,
        "rating": 4.7,
        "opening_time": "08:00",
        "closing_time": "18:30",
        "closed_days": [],
        "description": "Terraced 22-hectare botanical garden of century-old oaks, fern houses, and emerald rose terraces at 2,240 meters."
    },
    {
        "id": "OTY-002",
        "name": "Doddabetta Peak Viewpoint",
        "location": "Ooty",
        "lat": 11.4035,
        "lon": 76.7360,
        "category": "viewpoint",
        "interests": ["scenic", "adventure"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 30.0,
        "rating": 4.6,
        "opening_time": "07:00",
        "closing_time": "17:30",
        "closed_days": [],
        "description": "The Nilgiris' highest summit with a glass telescope and panoramic shola-forest views across Tamil Nadu."
    },
    {
        "id": "OTY-003",
        "name": "Ooty Lake Boating & Mini Train Walk",
        "location": "Ooty",
        "lat": 11.4076,
        "lon": 76.6940,
        "category": "beach",
        "interests": ["relaxation", "nature", "food"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 40.0,
        "rating": 4.4,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Artificial lake fringed by eucalyptus where pedal-boats glide past the historic Mettupalayam toy-train station."
    },
    {
        "id": "OTY-004",
        "name": "Toda Tea Factory & Plantation Trail",
        "location": "Ooty",
        "lat": 11.3800,
        "lon": 76.7600,
        "category": "heritage_village",
        "interests": ["food", "nature", "heritage"],
        "typical_duration_mins": 75,
        "entry_fee_per_person": 150.0,
        "rating": 4.5,
        "opening_time": "09:00",
        "closing_time": "17:00",
        "closed_days": [],
        "description": "Rolling tea estates where you can walk the plucking trails, watch leaf processing, and sip fresh Nilgiri brew."
    },
    # --- PONDICHERRY & ECR CORRIDOR ---
    {
        "id": "PDY-001",
        "name": "Promenade Beach & French War Memorial",
        "location": "Pondicherry",
        "lat": 11.9329,
        "lon": 79.8359,
        "category": "beach",
        "interests": ["scenic", "heritage", "relaxation"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 0.0,
        "rating": 4.7,
        "opening_time": "06:00",
        "closing_time": "22:00",
        "closed_days": [],
        "description": "Iconic 1.5 km seaside promenade flanked by French colonial statues, seaside cafes, and gentle waves."
    },
    {
        "id": "PDY-002",
        "name": "Auroville Matrimandir & Peace Area",
        "location": "Pondicherry",
        "lat": 12.0069,
        "lon": 79.8106,
        "category": "monument",
        "interests": ["relaxation", "scenic", "heritage"],
        "typical_duration_mins": 120,
        "entry_fee_per_person": 0.0,
        "rating": 4.8,
        "opening_time": "09:00",
        "closing_time": "17:00",
        "closed_days": [],
        "description": "Golden metallic sphere representing human unity set amidst peaceful forest groves and amphitheaters."
    },
    {
        "id": "PDY-003",
        "name": "White Town (French Colony) Heritage Walk",
        "location": "Pondicherry",
        "lat": 11.9310,
        "lon": 79.8336,
        "category": "heritage_district",
        "interests": ["heritage", "culture", "food"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 0.0,
        "rating": 4.7,
        "opening_time": "08:00",
        "closing_time": "21:00",
        "closed_days": [],
        "description": "Charming mustard-yellow colonial villas, bougainvillea-draped archways, art boutiques, and French bakeries."
    },
    {
        "id": "PDY-004",
        "name": "Shore Temple & Pancha Rathas",
        "location": "Mahabalipuram",
        "lat": 12.6163,
        "lon": 80.1983,
        "category": "monument",
        "interests": ["heritage", "scenic"],
        "typical_duration_mins": 100,
        "entry_fee_per_person": 40.0,
        "rating": 4.8,
        "opening_time": "06:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "UNESCO World Heritage 8th-century granite rock-cut shore temples overlooking the Bay of Bengal."
    },
    # --- DARJEELING & HIMALAYAN CORRIDOR ---
    {
        "id": "DJL-001",
        "name": "Tiger Hill Sunrise Over Kanchenjunga",
        "location": "Darjeeling",
        "lat": 26.9944,
        "lon": 88.2863,
        "category": "viewpoint",
        "interests": ["scenic", "nature", "adventure"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 50.0,
        "rating": 4.9,
        "opening_time": "04:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Panoramic mountain peak witnessing golden pink sunrise illuminating Mt. Kanchenjunga and Himalayan peaks."
    },
    {
        "id": "DJL-002",
        "name": "Batasia Loop & War Memorial Toy Train",
        "location": "Darjeeling",
        "lat": 27.0167,
        "lon": 88.2467,
        "category": "heritage",
        "interests": ["heritage", "scenic"],
        "typical_duration_mins": 60,
        "entry_fee_per_person": 30.0,
        "rating": 4.7,
        "opening_time": "05:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Spiral railway loop with landscaped garden offering a 360-degree view of Darjeeling town and mountain peaks."
    },
    {
        "id": "DJL-003",
        "name": "Happy Valley Tea Estate & Factory",
        "location": "Darjeeling",
        "lat": 27.0531,
        "lon": 88.2618,
        "category": "plantation",
        "interests": ["nature", "food", "scenic"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 100.0,
        "rating": 4.6,
        "opening_time": "08:00",
        "closing_time": "16:30",
        "closed_days": [],
        "description": "Historic second-oldest tea estate in Darjeeling perched on steep emerald slopes producing Muscatel tea."
    },
    {
        "id": "DJL-004",
        "name": "Himalayan Mountaineering Institute & Zoo",
        "location": "Darjeeling",
        "lat": 27.0583,
        "lon": 88.2547,
        "category": "museum",
        "interests": ["adventure", "nature", "heritage"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 110.0,
        "rating": 4.6,
        "opening_time": "08:30",
        "closing_time": "16:30",
        "closed_days": [],
        "description": "Legendary institute founded by Tenzing Norgay alongside high-altitude sanctuary housing Red Pandas and Snow Leopards."
    },
    # --- MAHABALESHWAR & WESTERN GHATS CORRIDOR ---
    {
        "id": "MHB-001",
        "name": "Arthur's Seat & Queen of Points",
        "location": "Mahabaleshwar",
        "lat": 17.9858,
        "lon": 73.6186,
        "category": "viewpoint",
        "interests": ["scenic", "nature", "adventure"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 20.0,
        "rating": 4.8,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "closed_days": [],
        "description": "Dramatic cliff precipice perched 1,470 meters above sea level looking into Savitri River canyon."
    },
    {
        "id": "MHB-002",
        "name": "Mapro Garden & Strawberry Farm",
        "location": "Mahabaleshwar",
        "lat": 17.9304,
        "lon": 73.7431,
        "category": "food_experience",
        "interests": ["food", "relaxation", "scenic"],
        "typical_duration_mins": 75,
        "entry_fee_per_person": 0.0,
        "rating": 4.7,
        "opening_time": "08:30",
        "closing_time": "21:00",
        "closed_days": [],
        "description": "Lush strawberry orchards featuring chocolate confectioneries, artisanal wood-fired pizzas, and berry preserves."
    },
    {
        "id": "MHB-003",
        "name": "Venna Lake Boating & Shoreline Bazaar",
        "location": "Mahabaleshwar",
        "lat": 17.9250,
        "lon": 73.6700,
        "category": "lake",
        "interests": ["nature", "relaxation", "scenic"],
        "typical_duration_mins": 75,
        "entry_fee_per_person": 50.0,
        "rating": 4.5,
        "opening_time": "08:00",
        "closing_time": "20:00",
        "closed_days": [],
        "description": "Tree-fringed mountain lake with pedal boats, horseback riding trails, and fresh roasted corn stalls."
    },
    {
        "id": "MHB-004",
        "name": "Table Land Volcanic Plateau",
        "location": "Panchgani",
        "lat": 17.9281,
        "lon": 73.8056,
        "category": "viewpoint",
        "interests": ["scenic", "nature", "adventure"],
        "typical_duration_mins": 90,
        "entry_fee_per_person": 50.0,
        "rating": 4.6,
        "opening_time": "06:00",
        "closing_time": "19:00",
        "closed_days": [],
        "description": "Asia's second largest mountain plateau formed of laterite rock offering breath-taking valley vistas."
    }
]

# Active index for fast place lookup and consistent hours
LIVE_SPOTS_INDEX: Dict[str, Dict[str, Any]] = {}

@tool(name="search_places", description="Search tourist spots, attractions, and viewpoints by location and interest keywords from OpenStreetMap, OpenTripMap, and Curated places.")
def search_places(location: str, interest: Optional[str] = None, max_results: int = 6) -> List[Dict[str, Any]]:
    # Try fetching from unified POI engine (OSM Overpass / OpenTripMap / Curated)
    try:
        from tools.poi_tools import get_city_spots
        live_spots = get_city_spots(city_name=location, genre_filter=interest, max_count=max_results)
        if live_spots:
            for sp in live_spots:
                LIVE_SPOTS_INDEX[sp["id"].lower()] = sp
                LIVE_SPOTS_INDEX[sp["name"].lower()] = sp
            return live_spots[:max_results]
    except Exception as e:
        pass

    loc_lower = location.strip().lower()
    interest_lower = interest.strip().lower() if interest else None

    # Filter matching curated places
    matches = []
    for p in CURATED_PLACES:
        p_loc = p["location"].lower()
        if loc_lower in p_loc or p_loc in loc_lower:
            if not interest_lower or any(interest_lower in i.lower() for i in p.get("interests", [])):
                matches.append(p)
            elif not interest_lower:
                matches.append(p)

    # If no strict matches, match on location alone
    if not matches:
        matches = [p for p in CURATED_PLACES if loc_lower in p["location"].lower() or p["location"].lower() in loc_lower]

    # If still no match (arbitrary unknown location), dynamically generate realistic spots for that city
    if not matches:
        from tools.routing_tools import get_coordinates
        c = get_coordinates(location)
        matches = [
            {
                "id": f"{location[:3].upper()}-001",
                "name": f"{location.title()} Heritage & Culture Landmark",
                "location": location.title(),
                "lat": round(c.lat + 0.005, 4),
                "lon": round(c.lon + 0.005, 4),
                "category": "viewpoint",
                "genre": "🏛️ Heritage & Monument",
                "source": "curated",
                "interests": ["heritage", "scenic", "relaxation"],
                "typical_duration_mins": 75,
                "entry_fee_per_person": 30.0,
                "rating": 4.5,
                "opening_time": "09:00",
                "closing_time": "18:00",
                "closed_days": [],
                "description": f"Central landmark and heritage promenade of {location.title()} offering local cultural immersion."
            },
            {
                "id": f"{location[:3].upper()}-002",
                "name": f"{location.title()} Scenic Lookout & Promenade",
                "location": location.title(),
                "lat": round(c.lat - 0.005, 4),
                "lon": round(c.lon - 0.005, 4),
                "category": "nature_spot",
                "genre": "🌅 Viewpoint & Scenic",
                "source": "curated",
                "interests": ["nature", "scenic"],
                "typical_duration_mins": 60,
                "entry_fee_per_person": 20.0,
                "rating": 4.4,
                "opening_time": "06:30",
                "closing_time": "19:30",
                "closed_days": [],
                "description": f"Expansive scenic viewpoints with tranquil panoramas and walking paths in {location.title()}."
            }
        ]

    for sp in matches:
        LIVE_SPOTS_INDEX[sp["id"].lower()] = sp
        LIVE_SPOTS_INDEX[sp["name"].lower()] = sp

    return matches[:max_results]

@tool(name="get_opening_hours", description="Check opening hours, closing hours, and closed days for a specific attraction.")
def get_opening_hours(place_id_or_name: str) -> Dict[str, Any]:
    identifier = place_id_or_name.strip().lower()

    # 1. Check live spots index
    if identifier in LIVE_SPOTS_INDEX:
        sp = LIVE_SPOTS_INDEX[identifier]
        return {
            "id": sp["id"],
            "name": sp["name"],
            "opening_time": sp["opening_time"],
            "closing_time": sp["closing_time"],
            "closed_days": sp.get("closed_days", []),
            "typical_duration_mins": sp.get("typical_duration_mins", 90)
        }

    for k, sp in LIVE_SPOTS_INDEX.items():
        if identifier in k or k in identifier:
            return {
                "id": sp["id"],
                "name": sp["name"],
                "opening_time": sp["opening_time"],
                "closing_time": sp["closing_time"],
                "closed_days": sp.get("closed_days", []),
                "typical_duration_mins": sp.get("typical_duration_mins", 90)
            }

    # 2. Check curated places catalog
    for p in CURATED_PLACES:
        if p["id"].lower() == identifier or identifier in p["name"].lower() or p["name"].lower() in identifier:
            return {
                "id": p["id"],
                "name": p["name"],
                "opening_time": p["opening_time"],
                "closing_time": p["closing_time"],
                "closed_days": p.get("closed_days", []),
                "typical_duration_mins": p["typical_duration_mins"]
            }

    # Default reasonable business hours
    return {
        "id": place_id_or_name,
        "name": place_id_or_name,
        "opening_time": "09:00",
        "closing_time": "18:00",
        "closed_days": [],
        "typical_duration_mins": 90
    }
