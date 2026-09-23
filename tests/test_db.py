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
    get_db_connection,
    get_db_path,
    save_forecast_dataframe,
)


class TestDatabaseManager(unittest.TestCase):
    """Test suite for db module."""

    def setUp(self):
        """Set up temporary database file for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_weather.db")

    def tearDown(self):
        """Clean up temporary directory after test."""
        self.temp_dir.cleanup()

    def test_get_db_path_default(self):
        """Test default database path generation."""
        path = get_db_path()
        self.assertTrue(path.endswith(os.path.join("data", "weather.db")))

    def test_get_db_path_custom(self):
        """Test custom database path override."""
        custom_path = os.path.join(self.temp_dir.name, "sub_dir", "custom_weather.db")
        path = get_db_path(custom_path)
        self.assertEqual(path, custom_path)
        self.assertTrue(os.path.exists(os.path.dirname(custom_path)))

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

    def test_save_forecast_dataframe_upsert(self):
        """Test inserting and updating records via save_forecast_dataframe."""
        sample_df = pd.DataFrame(
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
                }
            ]
        )

        # 1. Initial insert
        inserted_count = save_forecast_dataframe(sample_df, self.db_path)
        self.assertGreater(inserted_count, 0)

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM weather_forecasts WHERE location_name='臺北市'")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["max_temp"], 31.0)

        # 2. Update existing record (Conflict on location_name + start_time)
        updated_df = sample_df.copy()
        updated_df["maxTemp"] = 33.0
        save_forecast_dataframe(updated_df, self.db_path)

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM weather_forecasts WHERE location_name='臺北市'")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["max_temp"], 33.0)

    def test_save_empty_dataframe(self):
        """Test saving empty DataFrame returns 0."""
        empty_df = pd.DataFrame()
        result = save_forecast_dataframe(empty_df, self.db_path)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
