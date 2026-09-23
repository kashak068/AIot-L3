"""
Unit tests for database management module (src/db.py).
"""

import os
import sqlite3
import unittest
from unittest.mock import patch

from src.db import DEFAULT_DB_PATH, get_db_connection, get_db_path


class TestDatabaseManager(unittest.TestCase):
    """Test suite for db module."""

    def test_get_db_path_default(self):
        """Test default database path generation."""
        path = get_db_path()
        self.assertTrue(path.endswith(os.path.join("data", "weather.db")))

    def test_get_db_path_custom(self):
        """Test custom database path override."""
        custom_path = os.path.join("tmp_test_data", "test_weather.db")
        path = get_db_path(custom_path)
        self.assertEqual(path, custom_path)

        # Cleanup created temporary directory
        if os.path.exists("tmp_test_data"):
            os.rmdir("tmp_test_data")

    def test_get_db_connection_memory(self):
        """Test acquiring connection and executing query in memory."""
        with get_db_connection(":memory:") as conn:
            self.assertIsInstance(conn, sqlite3.Connection)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS num")
            row = cursor.fetchone()
            self.assertEqual(row["num"], 1)

    def test_get_db_connection_rollback_on_error(self):
        """Test automatic transaction rollback upon exception."""
        with self.assertRaises(sqlite3.OperationalError):
            with get_db_connection(":memory:") as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test_tbl (id INT)")
                # Execute invalid SQL to trigger rollback
                cursor.execute("INVALID SQL STATEMENT")


if __name__ == "__main__":
    unittest.main()
