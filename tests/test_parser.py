"""
Unit tests for JSON parser module (src/parser.py).
"""

import unittest
from src.parser import JSONParseError, extract_locations, parse_forecast_json, parse_location_weather


class TestJSONParser(unittest.TestCase):
    """Test suite for CWA JSON parser."""

    def setUp(self):
        """Set up sample CWA F-C0032-001 JSON data payload."""
        self.sample_json = {
            "success": "true",
            "result": {"resource_id": "F-C0032-001"},
            "records": {
                "datasetDescription": "三十六小時天氣預報",
                "location": [
                    {
                        "locationName": "臺北市",
                        "weatherElement": [
                            {
                                "elementName": "Wx",
                                "time": [
                                    {
                                        "startTime": "2026-09-23 12:00:00",
                                        "endTime": "2026-09-23 18:00:00",
                                        "parameter": {
                                            "parameterName": "晴時多雲",
                                            "parameterValue": "2",
                                        },
                                    }
                                ],
                            },
                            {
                                "elementName": "MinT",
                                "time": [
                                    {
                                        "startTime": "2026-09-23 12:00:00",
                                        "endTime": "2026-09-23 18:00:00",
                                        "parameter": {
                                            "parameterName": "24",
                                            "parameterUnit": "C",
                                        },
                                    }
                                ],
                            },
                            {
                                "elementName": "MaxT",
                                "time": [
                                    {
                                        "startTime": "2026-09-23 12:00:00",
                                        "endTime": "2026-09-23 18:00:00",
                                        "parameter": {
                                            "parameterName": "31",
                                            "parameterUnit": "C",
                                        },
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
        }

    def test_extract_locations_success(self):
        """Test extracting locations list from valid CWA JSON payload."""
        locations = extract_locations(self.sample_json)
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]["locationName"], "臺北市")

    def test_extract_locations_invalid_payload(self):
        """Test error handling when JSON is not a dict or missing 'records'."""
        with self.assertRaises(JSONParseError):
            extract_locations("invalid string payload")

        with self.assertRaises(JSONParseError):
            extract_locations({"success": "false"})

    def test_parse_location_weather(self):
        """Test parsing weather elements for a location record."""
        location_record = self.sample_json["records"]["location"][0]
        parsed = parse_location_weather(location_record)

        self.assertEqual(parsed["locationName"], "臺北市")
        self.assertIn("Wx", parsed["elements"])
        self.assertIn("MinT", parsed["elements"])
        self.assertIn("MaxT", parsed["elements"])

        mint_slot = parsed["elements"]["MinT"][0]
        self.assertEqual(mint_slot["parameterName"], "24")
        self.assertEqual(mint_slot["parameterUnit"], "C")

    def test_parse_forecast_json_full(self):
        """Test full parsing function for F-C0032-001 dataset."""
        results = parse_forecast_json(self.sample_json)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["locationName"], "臺北市")
        self.assertEqual(results[0]["elements"]["MaxT"][0]["parameterName"], "31")


if __name__ == "__main__":
    unittest.main()
