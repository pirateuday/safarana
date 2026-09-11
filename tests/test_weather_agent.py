import unittest
from agents.weather_agent import WeatherAgent
from models.schemas import DayWeather

class TestWeatherAgent(unittest.TestCase):
    def setUp(self):
        self.agent = WeatherAgent()

    def test_hill_station_winter_forecast(self):
        forecasts = self.agent.analyze_weather("Manali", ["2026-12-15", "2026-12-16"])
        self.assertEqual(len(forecasts), 2)
        day1 = forecasts["2026-12-15"]
        self.assertIsInstance(day1, DayWeather)
        self.assertIn("❄️", day1.icon)
        self.assertLess(day1.temperature_celsius, 15.0)
        self.assertTrue(any("thermal" in p.lower() or "wool" in p.lower() for p in day1.clothing_packing_advice))

    def test_coastal_summer_forecast(self):
        forecasts = self.agent.analyze_weather("Goa", ["2026-05-10"])
        day = forecasts["2026-05-10"]
        self.assertGreater(day.temperature_celsius, 25.0)
        self.assertTrue(any("sunscreen" in p.lower() or "cotton" in p.lower() for p in day.clothing_packing_advice))

    def test_desert_winter_forecast(self):
        forecasts = self.agent.analyze_weather("Jaipur", ["2026-11-20"])
        day = forecasts["2026-11-20"]
        self.assertIsNotNone(day.risk_alert)
        self.assertIn("☀️", day.icon)

    def test_agent_history_logging(self):
        self.agent.analyze_weather("Ooty", ["2026-10-01", "2026-10-02"])
        trace = self.agent.to_trace_dict()
        self.assertGreater(len(trace), 0)
        self.assertEqual(trace[0]["sender"], "WeatherAgent")
        self.assertEqual(trace[0]["recipient"], "PlannerAgent")

if __name__ == "__main__":
    unittest.main()
