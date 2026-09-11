import unittest
from tools.google_maps_tools import (
    decode_polyline,
    calculate_transport_fare,
    _parse_google_directions_response,
    get_google_maps_status
)

class TestGoogleMapsTools(unittest.TestCase):

    def test_polyline_decoding(self):
        # Known Google encoded polyline: (38.5, -120.2), (40.7, -120.95), (43.252, -126.453)
        encoded = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
        decoded = decode_polyline(encoded)
        self.assertEqual(len(decoded), 3)
        self.assertAlmostEqual(decoded[0]["lat"], 38.5, places=3)
        self.assertAlmostEqual(decoded[0]["lon"], -120.2, places=3)
        self.assertAlmostEqual(decoded[1]["lat"], 40.7, places=3)
        self.assertAlmostEqual(decoded[1]["lon"], -120.95, places=3)
        self.assertAlmostEqual(decoded[2]["lat"], 43.252, places=3)
        self.assertAlmostEqual(decoded[2]["lon"], -126.453, places=3)

    def test_empty_polyline(self):
        self.assertEqual(decode_polyline(""), [])
        self.assertEqual(decode_polyline(None), [])

    def test_driving_fare_calculation(self):
        res = calculate_transport_fare(distance_km=300.0, travel_mode="driving", party_size=2)
        self.assertIn("total_cost", res)
        self.assertIn("fare_breakdown", res)
        self.assertGreater(res["total_cost"], 1000.0)
        self.assertEqual(res["fare_source"], "calibrated_fuel_and_tolls")
        self.assertEqual(res["fare_breakdown"]["party_size"], 2)

    def test_train_fare_with_google_maps_fare(self):
        google_fare = {"currency": "INR", "value": 340.0, "text": "₹340"}
        res = calculate_transport_fare(distance_km=300.0, travel_mode="train", party_size=2, google_fare_obj=google_fare)
        self.assertEqual(res["fare_source"], "google_maps")
        self.assertEqual(res["ticket_cost_per_person"], 340.0)
        self.assertEqual(res["tickets_total"], 680.0)
        # Includes local feeder auto (₹300)
        self.assertEqual(res["total_cost"], 980.0)

    def test_train_fare_calibrated_slabs(self):
        res_3a = calculate_transport_fare(distance_km=300.0, travel_mode="train", party_size=1, train_class="3A")
        res_2a = calculate_transport_fare(distance_km=300.0, travel_mode="train", party_size=1, train_class="2A")
        res_sl = calculate_transport_fare(distance_km=300.0, travel_mode="train", party_size=1, train_class="SL")
        # 2A must be more expensive than 3A, and 3A more than SL
        self.assertGreater(res_2a["total_cost"], res_3a["total_cost"])
        self.assertGreater(res_3a["total_cost"], res_sl["total_cost"])

    def test_google_directions_parser(self):
        mock_response = {
            "status": "OK",
            "routes": [{
                "overview_polyline": {"points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"},
                "fare": {"currency": "INR", "value": 450.0, "text": "₹450"},
                "legs": [{
                    "distance": {"value": 295000, "text": "295 km"},
                    "duration": {"value": 14400, "text": "4 hours"},
                    "duration_in_traffic": {"value": 15600, "text": "4 hours 20 mins"},
                    "steps": [{
                        "travel_mode": "TRANSIT",
                        "transit_details": {
                            "line": {"name": "Ajmer Shatabdi", "vehicle": {"type": "HEAVY_RAIL"}},
                            "departure_stop": {"name": "New Delhi"},
                            "arrival_stop": {"name": "Jaipur Jn"},
                            "departure_time": {"text": "06:10 AM"},
                            "arrival_time": {"text": "10:35 AM"},
                            "num_stops": 5
                        }
                    }]
                }]
            }]
        }
        parsed = _parse_google_directions_response(mock_response, "Delhi", "Jaipur", "transit")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["distance_km"], 295.0)
        self.assertEqual(parsed["duration_hours"], 4.0)
        self.assertEqual(parsed["traffic_duration_hours"], 4.33)
        self.assertEqual(parsed["transit_fare"]["value"], 450.0)
        self.assertEqual(len(parsed["geometry"]), 3)
        self.assertEqual(len(parsed["transit_steps"]), 1)
        self.assertEqual(parsed["transit_steps"][0]["line_name"], "Ajmer Shatabdi")

    def test_status_info(self):
        status = get_google_maps_status()
        self.assertIn("key_configured", status)
        self.assertTrue(status["key_configured"])

if __name__ == "__main__":
    unittest.main()
