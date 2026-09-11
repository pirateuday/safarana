from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from models.schemas import RouteOption, Coordinates, RouteLeg

class RouteAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RouteAgent",
            role="Routing & Corridor Specialist",
            description="Computes optimal physical paths, highway corridors, transit times, and realistic delay factors."
        )

    def analyze_route(
        self,
        origin: str,
        destination: str,
        stopovers: Optional[List[str]] = None,
        travel_mode: str = "driving",
        leg_modes: Optional[List[str]] = None,
        party_size: int = 1,
        selected_trains: Optional[Dict[str, str]] = None,
        selected_flights: Optional[Dict[str, str]] = None,
        api_key: Optional[str] = None
    ) -> RouteOption:
        stopover_names = [s.strip() for s in (stopovers or []) if s and s.strip()]
        self.log_step(
            recipient="Planner",
            action="initiate_routing",
            payload={"origin": origin, "destination": destination, "stopovers": stopover_names, "mode": travel_mode, "leg_modes": leg_modes, "party_size": party_size, "selected_trains": selected_trains, "selected_flights": selected_flights},
            notes=f"Querying OSRM & geographical topology for path from {origin} to {destination} via {stopover_names if stopover_names else 'direct corridor'} ({travel_mode})."
        )

        route_data = self.execute_tool(
            "get_multi_stop_route",
            origin=origin,
            destination=destination,
            stopovers=stopover_names,
            travel_mode=travel_mode,
            leg_modes=leg_modes,
            party_size=party_size,
            selected_trains=selected_trains,
            selected_flights=selected_flights,
            api_key=api_key
        )

        geometry_points = [
            Coordinates(lat=pt["lat"], lon=pt["lon"])
            for pt in route_data.get("geometry", [])
        ]

        legs = [
            RouteLeg(
                from_place=leg["from_place"],
                to_place=leg["to_place"],
                distance_km=leg["distance_km"],
                duration_hours=leg["duration_hours"],
                buffered_duration_hours=leg.get("buffered_duration_hours", 0.0),
                estimated_transit_cost=leg.get("estimated_transit_cost", 0.0),
                geometry=[Coordinates(lat=p["lat"], lon=p["lon"]) for p in leg.get("geometry", [])],
                selected_mode=leg.get("selected_mode", travel_mode),
                available_modes=leg.get("available_modes", []),
                ticket_cost=leg.get("ticket_cost", 0.0),
                local_transit_cost=leg.get("local_transit_cost", 0.0),
                departure_hub=leg.get("departure_hub", ""),
                arrival_hub=leg.get("arrival_hub", ""),
                local_vehicle_type=leg.get("local_vehicle_type", ""),
                train_number=leg.get("train_number"),
                train_name=leg.get("train_name"),
                departure_time=leg.get("departure_time"),
                arrival_time=leg.get("arrival_time"),
                available_trains=leg.get("available_trains", []),
                flight_number=leg.get("flight_number"),
                airline=leg.get("airline"),
                airline_code=leg.get("airline_code"),
                aircraft=leg.get("aircraft"),
                cabin_class=leg.get("cabin_class"),
                baggage_allowance=leg.get("baggage_allowance"),
                available_flights=leg.get("available_flights", []),
                fare_source=leg.get("fare_source", "calibrated_model"),
                fare_currency=leg.get("fare_currency", "₹"),
                fare_breakdown=leg.get("fare_breakdown", {}),
                seat_status=leg.get("seat_status", []),
                coach_position=leg.get("coach_position"),
                route_stops=leg.get("route_stops", []),
                live_status=leg.get("live_status"),
                live_delay_mins=leg.get("live_delay_mins", 0),
                live_status_text=leg.get("live_status_text", "Scheduled")
            )
            for leg in route_data.get("legs", [])
        ]

        route_option = RouteOption(
            origin=route_data["origin"],
            destination=route_data["destination"],
            waypoints=route_data.get("corridor_stops", []),
            legs=legs,
            total_distance_km=route_data["total_distance_km"],
            base_travel_time_hours=route_data["base_travel_time_hours"],
            buffered_travel_time_hours=route_data["buffered_travel_time_hours"],
            estimated_transit_cost=route_data["estimated_transit_cost"],
            corridor_geometry=geometry_points,
            selected_mode=travel_mode,
            fare_source=route_data.get("fare_source", "calibrated_model")
        )

        via_summary = f" via {', '.join(stopover_names)}" if stopover_names else (f" via {', '.join(route_option.waypoints[:2])}" if route_option.waypoints else "")
        self.log_step(
            recipient="Planner",
            action="route_computed",
            payload={
                "total_distance_km": route_option.total_distance_km,
                "buffered_hours": route_option.buffered_travel_time_hours,
                "corridor_stops": route_option.waypoints,
                "transit_cost": route_option.estimated_transit_cost,
                "legs_count": len(legs),
                "leg_modes": [l.selected_mode for l in legs]
            },
            notes=f"Found corridor with {route_option.total_distance_km} km distance (~{route_option.buffered_travel_time_hours} hrs buffered){via_summary}."
        )

        return route_option
