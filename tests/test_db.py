"""
Unit tests for database management module (src/db.py).
"""

import os
import sqlite3
import tempfile
import unittest
import pandas as pd

from src.db import (
    DEFAULT_DB_PATH,
    create_tables,
    get_all_locations,
    get_db_connection,
    get_db_path,
    get_latest_update_time,
    query_forecast_data,
    save_forecast_dataframe,
)


class TestDatabaseManager(unittest.TestCase):
    """Test suite for db module."""

    def setUp(self):
        """Set up temporary database file and sample data for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_weather.db")

        self.sample_df = pd.DataFrame(
            [
                {
                    "locationName": "臺北市",
                    "startTime": "2026-09-23 12:00:00",
                    "endTime": "2026-09-23 18:00:00",
                    "minTemp": 24.0,
                    "maxTemp": 31.0,
                    "tempDiff": 7.0,
                    "avgTemp": 27.5,
                    "weather": "晴時多雲",
                    "pop": 10.0,
                    "comfort": "舒適",
                },
                {
                    "locationName": "高雄市",
                    "startTime": "2026-09-23 12:00:00",
                    "endTime": "2026-09-23 18:00:00",
                    "minTemp": 26.0,
                    "maxTemp": 33.0,
                    "tempDiff": 7.0,
                    "avgTemp": 29.5,
                    "weather": "多雲",
                    "pop": 20.0,
                    "comfort": "悶熱",
                },
            ]
        )

    def tearDown(self):
        """Clean up temporary directory after test."""
        self.temp_dir.cleanup()

    def test_get_db_path_default(self):
        """Test default database path generation."""
        path = get_db_path()
        self.assertTrue(path.endswith(os.path.join("data", "weather.db")))

    def test_create_tables(self):
        """Test table and index creation."""
        create_tables(self.db_path)
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='weather_forecasts'"
            )
            table = cursor.fetchone()
            self.assertIsNotNone(table)
            self.assertEqual(table["name"], "weather_forecasts")

    def test_query_forecast_data_filtering(self):
        """Test SQL query filtering by location and date range."""
        save_forecast_dataframe(self.sample_df, self.db_path)

        # 1. Query all locations
        all_df = query_forecast_data(db_path=self.db_path)
        self.assertEqual(len(all_df), 2)

        # 2. Filter by location
        taipei_df = query_forecast_data(location_name="臺北市", db_path=self.db_path)
        self.assertEqual(len(taipei_df), 1)
        self.assertEqual(taipei_df.iloc[0]["locationName"], "臺北市")

        # 3. Filter by start_date
        date_filtered_df = query_forecast_data(
            start_date="2026-09-23 12:00:00", db_path=self.db_path
        )
        self.assertEqual(len(date_filtered_df), 2)

    def test_get_all_locations(self):
        """Test retrieving sorted distinct location names."""
        save_forecast_dataframe(self.sample_df, self.db_path)
        locations = get_all_locations(self.db_path)

        self.assertEqual(len(locations), 2)
        self.assertIn("臺北市", locations)
        self.assertIn("高雄市", locations)

    def test_get_latest_update_time(self):
        """Test retrieving latest update timestamp."""
        save_forecast_dataframe(self.sample_df, self.db_path)
        latest_time = get_latest_update_time(self.db_path)
        self.assertIsNotNone(latest_time)


if __name__ == "__main__":
    unittest.main()
