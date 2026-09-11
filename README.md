# SmartRoute — AI Multi-Agent Trip Planner

An intelligent multi-agent trip planning engine that models traveling from **Origin A to Destination B within budget and time** as a structured **constraint-satisfaction and optimization problem**.

---

## 🌟 Architecture & The 6 Agentic Concepts

SmartRoute maps directly to the 6 core agentic concepts:

```
User inputs (A, B, budget, time, travel mode, preferences, party size)
  │
  ▼
[Planner Agent] (Orchestrator) ──▶ Workflow: Plan ➔ Route ➔ Discover ➔ Weather ➔ Filter ➔ Schedule ➔ Refine ➔ Present
  │     ▲
  │     │  Structured JSON Messages (AgentMessage)
  ▼     │
[Route Agent]  [Spot Agent]  [Food & Stay Agent]  [Weather Agent]  [Budget Agent]  [Scheduler Agent]
  │                │                 │                   │               │                │
  └────────────────┴─────────────────┴───────────────────┴───────────────┴────────────────┘
        │
        ▼ Function Calling Tool Registry
  get_route, search_places, get_opening_hours, search_hotels, search_restaurants, book_hotel, book_restaurant
```

### 1. AI Specialist Agents
- **Planner Agent (`agents/planner_agent.py`)**: Central orchestrator coordinating specialist agents, managing the feedback loop, and synthesizing 4 Pareto-optimal alternatives.
- **Route Agent (`agents/route_agent.py`)**: Determines geodesic/highway paths from A to B, evaluates intermediate corridor waypoints, and calculates driving distance.
- **Spot Agent (`agents/spot_agent.py`)**: Discovers attractions, monuments, and viewpoints matching user interests; verifies opening/closing hours and typical dwell times.
- **Food & Stay Agent (`agents/food_stay_agent.py`)**: Discovers authentic roadside dhabas, local culinary spots, and accommodations within budget tiers; handles confirmed booking simulations.
- **Weather Agent (`agents/weather_agent.py`)**: Models destination climatology, delivers daily temperature and weather condition forecasts, generates packing advisories, and flags environmental alerts.
- **Budget Agent (`agents/budget_agent.py`)**: Audits every item (transport, stays, food, entry tickets, buffer reserve) against the hard budget cap; rejects over-budget options and provides concrete remediation advice.
- **Scheduler Agent (`agents/scheduler_agent.py`)**: Constructs chronological timelines with traffic delay factors (+18%), inter-activity buffers (25 min), and operating window alignment.

### 2. Function Calling Tool Registry
Registered in `tools/registry.py` with parameter schemas:
- `get_route(origin, destination, mode)`: OSRM public routing + geodesic fallback
- `get_coordinates(place_name)`: Nominatim geocoding + offline lookup
- `search_places(location, interest, max_results)`: Curated POIs with operating hours
- `get_opening_hours(place_id_or_name)`: Detailed opening time, closing time, closed days
- `search_hotels(location, budget_tier, party_size)`: Accommodations by tier and party size
- `search_restaurants(location, cuisine_pref)`: Roadside dhabas and local restaurants
- `book_hotel(hotel_id, date, guests, user_name)`: Creates confirmed reservation
- `book_restaurant(restaurant_id, time_slot, guests, user_name)`: Table reservation

### 3. Structured Output & Data Models
Pydantic V2 schemas in `models/schemas.py`:
- `TripInput`: Origin, Destination, Budget, Dates, Mode, Preferences, Party Size.
- `RouteOption`: Geometry coordinates, waypoints, total distance, buffered travel time.
- `Activity`: Place, Scheduled times, Duration, Buffer, Cost, Opening status.
- `DayItinerary`: Day number, activities, meals, overnight stay, cost breakdown.
- `TripPlan`: Plan ID, 4 Pareto-optimal variants (`balanced`, `fastest`, `cheapest`, `scenic`), complete agent trace.

### 4. The 4 Hard Constraints Solved
1. **Budget**: `Total Cost (Fuel + Stays + Food + Tickets + Buffer) <= Budget Cap`
2. **Time Window**: Daily driving hours <= 8.0h and arrival deadlines met
3. **Opening Hours**: Every visit falls strictly within `[opening_time, closing_time]`
4. **Delays & Buffers**: `+18% traffic delay factor` on transit + `25 min buffer` between activities

### 5. Multi-Objective Pareto Frontier
Instead of a single rigid plan, SmartRoute computes 4 Pareto-optimal variants:
- 🌟 **Balanced & Curated (Recommended)**: Optimal balance of heritage, authentic dhabas, comfort stay, and relaxed buffers.
- ⚡ **Fastest / Direct**: Minimizes travel friction with crown-jewel sights.
- 💰 **Budget Explorer**: Roadside dhabas, backpacker lodges, maximum savings.
- 🌄 **Scenic & Explorer**: Dense sightseeing, sunset viewpoints, boutique haveli stay.

### 6. Agent-to-Agent Feedback Loop
When the **Budget Agent** detects an over-budget plan, it rejects the itinerary and sends concrete remediation feedback to the **Planner**:
- Automatically downgrades hotel tier (e.g. boutique to standard/hostel).
- Re-schedules meals to highway dhabas.
- Re-runs the feasibility gate until constraints are satisfied.

---

## 🚀 Getting Started

### 1. Run Unit & Integration Tests
```powershell
& "..\venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py"
```

### 2. Launch the Web Application
```powershell
& "..\venv\Scripts\python.exe" app.py
```

Open your browser at **`http://localhost:8000`** to access the interactive web dashboard with:
- Interactive Leaflet Route Map
- Day-by-Day Timeline Visualizer
- Budget Feasibility Meter
- Live Agent-to-Agent Trace Log
- One-Click Hotel & Dhaba Table Booking
