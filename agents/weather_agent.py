from typing import List, Dict, Optional, Any
from datetime import datetime
from agents.base_agent import BaseAgent
from models.schemas import DayWeather

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="WeatherAgent",
            role="Environmental & Climate Specialist",
            description="Evaluates seasonal climate, regional meteorological patterns, weather risks, and packing guidelines along travel corridors."
        )

    def analyze_weather(
        self,
        destination: str,
        dates: List[str],
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, DayWeather]:
        """
        Generates daily meteorological forecasts, packing recommendations, and alerts
        tailored to the destination's geography and the time of year.
        """
        dest_lower = destination.lower()
        forecasts: Dict[str, DayWeather] = {}

        # Categorize destination biome/climate zone
        is_hill_station = any(k in dest_lower for k in ["manali", "darjeeling", "ooty", "coorg", "mahabaleshwar", "shimla", "munnar"])
        is_coastal = any(k in dest_lower for k in ["goa", "pondicherry", "chennai", "mumbai", "kochi", "puri"])
        is_desert_semiarid = any(k in dest_lower for k in ["jaipur", "udaipur", "jodhpur", "jaisalmer"])
        is_river_valley = any(k in dest_lower for k in ["rishikesh", "haridwar", "varanasi"])

        for idx, date_str in enumerate(dates):
            month = 10 # default October if parsing fails
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                month = dt.month
            except Exception:
                pass

            # Model temperature and condition based on zone and month
            if is_hill_station:
                if month in [12, 1, 2]:
                    temp = 7.0 + (idx % 3)
                    condition = "Cold & Frosty"
                    icon = "❄️"
                    packing = ["Heavy woolens & thermal innerwear", "Puffer jacket", "Insulated gloves & beanie", "Sturdy walking boots"]
                    alert = "Cold morning frost and sudden temperature drops after 5 PM."
                elif month in [7, 8]:
                    temp = 17.0 + (idx % 3)
                    condition = "Misty & Monsoon Showers"
                    icon = "🌧️"
                    packing = ["Waterproof rain jacket", "Compact umbrella", "Anti-skid trekking shoes", "Quick-dry clothes"]
                    alert = "Monsoon mountain mist; drive with fog lamps on hairpin curves."
                else:
                    temp = 16.0 + (idx % 4)
                    condition = "Crisp & Breezy Mountain Air"
                    icon = "⛅"
                    packing = ["Light fleece jacket / sweater", "Comfortable walking shoes", "Sun hat & moisturizer", "Windbreaker"]
                    alert = "Cool evening breeze; perfect weather for outdoor viewpoints."

            elif is_coastal:
                if month in [6, 7, 8, 9]:
                    temp = 28.0 + (idx % 2)
                    condition = "Tropical Rain & Strong Breeze"
                    icon = "🌧️"
                    packing = ["Waterproof poncho / umbrella", "Sandals / waterproof footwear", "Breathable light fabrics"]
                    alert = "High sea tides and frequent coastal showers; avoid deep ocean swimming."
                elif month in [11, 12, 1, 2]:
                    temp = 27.0 + (idx % 2)
                    condition = "Pleasant Coastal Breeze & Sunny"
                    icon = "☀️"
                    packing = ["Light cotton clothing", "UV sunglasses & high-SPF sunscreen", "Flip-flops / beachwear", "Wide-brim hat"]
                    alert = "Ideal beach weather; moderate evening humidity."
                else:
                    temp = 32.0 + (idx % 3)
                    condition = "Warm & Humid Maritime Sun"
                    icon = "☀️"
                    packing = ["Loose linen/cotton shirts", "Hydration water flask", "Sunscreen & sunglasses", "Cap"]
                    alert = "High daytime UV and humidity; stay hydrated during midday heritage walks."

            elif is_desert_semiarid:
                if month in [11, 12, 1, 2]:
                    temp = 21.0 + (idx % 3)
                    condition = "Crisp Sunny Days, Cool Nights"
                    icon = "☀️"
                    packing = ["Daytime light cottons", "Evening jacket or shawl", "Sunglasses & lip balm", "Comfortable walking sneakers"]
                    alert = "Significant diurnal temperature swing (cool nights below 12°C)."
                elif month in [4, 5, 6]:
                    temp = 38.0 + (idx % 3)
                    condition = "Hot & Sunny"
                    icon = "🔥"
                    packing = ["Light airy cottons", "Electrolyte packets & water flask", "Sun hat & dark sunglasses", "Scarf for dust/sun"]
                    alert = "Extreme heat warning: schedule fort visits before 11 AM or after 4 PM."
                else:
                    temp = 29.0 + (idx % 3)
                    condition = "Pleasant & Clear Skies"
                    icon = "☀️"
                    packing = ["Cotton shirts & trousers", "Sun hat & sunscreen", "Comfortable walking shoes"]
                    alert = "Clear visibility across forts and palaces; mild afternoon warmth."

            elif is_river_valley:
                if month in [12, 1]:
                    temp = 14.0 + (idx % 3)
                    condition = "Misty Morning & Cool River Breeze"
                    icon = "🌫️"
                    packing = ["Warm fleece jacket", "Woolen socks & scarf", "Walking shoes for ghats"]
                    alert = "Morning river fog along ghats; visibility improves by 10 AM."
                else:
                    temp = 26.0 + (idx % 3)
                    condition = "Pleasant & Sunny"
                    icon = "☀️"
                    packing = ["Modest comfortable cotton clothes", "Slip-on shoes for temples", "Sun hat & water bottle"]
                    alert = "Gentle river valley breezes; ideal for evening aarti and walking."

            else:
                # Default temperate / general Indian plains
                temp = 25.0 + (idx % 3)
                condition = "Clear Skies & Mild Sunshine"
                icon = "☀️"
                packing = ["Comfortable casual wear", "Walking shoes", "Sunglasses & sunscreen", "Light windcheater"]
                alert = "Pleasant travel conditions throughout the corridor."

            forecasts[date_str] = DayWeather(
                temperature_celsius=round(temp, 1),
                condition=condition,
                icon=icon,
                clothing_packing_advice=packing,
                risk_alert=alert
            )

        self.log_step(
            recipient="PlannerAgent",
            action="deliver_weather_advisory",
            payload={
                "destination": destination,
                "dates": dates,
                "forecasts": {k: v.model_dump() for k, v in forecasts.items()}
            },
            notes=f"Calculated {len(dates)}-day seasonal weather matrix and packing advice for {destination}."
        )

        return forecasts
