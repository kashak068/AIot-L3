"""
Unit tests for data processor module (src/processor.py).
"""

import unittest
import pandas as pd
from src.processor import filter_by_location, process_forecast_to_dataframe


class TestDataProcessor(unittest.TestCase):
    """Test suite for data processor module."""

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
                    },
                    {
                        "locationName": "高雄市",
                        "weatherElement": [
                            {
                                "elementName": "MinT",
                                "time": [
                                    {
                                        "startTime": "2026-09-23 12:00:00",
                                        "endTime": "2026-09-23 18:00:00",
                                        "parameter": {"parameterName": "26"},
                                    }
                                ],
                            },
                            {
                                "elementName": "MaxT",
                                "time": [
                                    {
                                        "startTime": "2026-09-23 12:00:00",
                                        "endTime": "2026-09-23 18:00:00",
                                        "parameter": {"parameterName": "33"},
                                    }
                                ],
                            },
                        ],
                    },
                ],
            },
        }

    def test_process_forecast_to_dataframe(self):
        """Test converting CWA JSON payload to DataFrame."""
        df = process_forecast_to_dataframe(self.sample_json)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn("locationName", df.columns)
        self.assertIn("minTemp", df.columns)
        self.assertIn("maxTemp", df.columns)
        self.assertIn("avgTemp", df.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["startTime"]))

    def test_filter_by_location(self):
        """Test filtering weather DataFrame by location name."""
        df = process_forecast_to_dataframe(self.sample_json)
        taipei_df = filter_by_location(df, "臺北市")

        self.assertEqual(len(taipei_df), 1)
        self.assertEqual(taipei_df.iloc[0]["locationName"], "臺北市")
        self.assertEqual(taipei_df.iloc[0]["maxTemp"], 31.0)

    def test_process_empty_json(self):
        """Test processing empty or invalid JSON payload returns empty DataFrame."""
        empty_json = {"records": {"location": []}}
        df = process_forecast_to_dataframe(empty_json)
        self.assertTrue(df.empty)
        self.assertIn("locationName", df.columns)


if __name__ == "__main__":
    unittest.main()
