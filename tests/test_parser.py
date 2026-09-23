"""
Unit tests for JSON parser module (src/parser.py).
"""

import unittest
from src.parser import (
    JSONParseError,
    extract_locations,
    extract_temperature_records,
    parse_forecast_json,
    parse_location_weather,
    parse_temperature_value,
)


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

    def test_parse_temperature_value(self):
        """Test safe float conversion of temperature strings."""
        self.assertEqual(parse_temperature_value("25"), 25.0)
        self.assertEqual(parse_temperature_value("32.5"), 32.5)
        self.assertIsNone(parse_temperature_value(None))
        self.assertIsNone(parse_temperature_value("invalid"))

    def test_extract_temperature_records(self):
        """Test extracting MinT, MaxT, tempDiff, and avgTemp features."""
        location_record = self.sample_json["records"]["location"][0]
        parsed = parse_location_weather(location_record)
        records = extract_temperature_records(parsed)

        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec["locationName"], "臺北市")
        self.assertEqual(rec["minTemp"], 24.0)
        self.assertEqual(rec["maxTemp"], 31.0)
        self.assertEqual(rec["tempDiff"], 7.0)
        self.assertEqual(rec["avgTemp"], 27.5)
        self.assertEqual(rec["weather"], "晴時多雲")


if __name__ == "__main__":
    unittest.main()
