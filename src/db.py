"""
Database management module for Taiwan Weather Forecast.

Provides SQLite connection handling, schema creation, transactional context
management, DataFrame persistence, and SQL query interfaces.
"""

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "weather.db",
)


def get_db_path(custom_path: Optional[str] = None) -> str:
    """
    Get the absolute file path for the SQLite database.

    :param custom_path: Optional path override.
    :return: Absolute database file path.
    """
    path = custom_path or os.getenv("WEATHER_DB_PATH", DEFAULT_DB_PATH)
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
        logger.info("Created database directory: %s", dir_name)
    return path


@contextmanager
def get_db_connection(
    db_path: Optional[str] = None,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for managing SQLite database connections and transactions safely.

    :param db_path: Optional custom path to SQLite database or ':memory:'.
    :yield: Configured sqlite3.Connection instance.
    """
    path = get_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # Access columns by name

    try:
        yield conn
        conn.commit()
    except Exception as err:
        conn.rollback()
        logger.error("Database operation failed; transaction rolled back: %s", err)
        raise
    finally:
        conn.close()


def create_tables(db_path: Optional[str] = None) -> None:
    """
    Create the weather_forecasts table and associated indices if they do not exist.

    :param db_path: Optional custom path to SQLite database.
    """
    schema_sql = """
    CREATE TABLE IF NOT EXISTS weather_forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_name TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        min_temp REAL,
        max_temp REAL,
        temp_diff REAL,
        avg_temp REAL,
        weather TEXT,
        pop REAL,
        comfort TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(location_name, start_time)
    );

    CREATE INDEX IF NOT EXISTS idx_location_start 
    ON weather_forecasts(location_name, start_time);
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        logger.info("Database schema and indices created successfully.")


def save_forecast_dataframe(
    df: pd.DataFrame, db_path: Optional[str] = None
) -> int:
    """
    Save or update a weather forecast DataFrame into the SQLite database.

    :param df: Weather DataFrame produced by process_forecast_to_dataframe.
    :param db_path: Optional custom database path.
    :return: Number of rows inserted or updated.
    """
    if df.empty:
        logger.warning("Attempted to save an empty DataFrame to database.")
        return 0

    create_tables(db_path)

    upsert_sql = """
    INSERT INTO weather_forecasts (
        location_name, start_time, end_time, min_temp, max_temp,
        temp_diff, avg_temp, weather, pop, comfort
    ) VALUES (
        :locationName, :startTime, :endTime, :minTemp, :maxTemp,
        :tempDiff, :avgTemp, :weather, :pop, :comfort
    )
    ON CONFLICT(location_name, start_time) DO UPDATE SET
        end_time = excluded.end_time,
        min_temp = excluded.min_temp,
        max_temp = excluded.max_temp,
        temp_diff = excluded.temp_diff,
        avg_temp = excluded.avg_temp,
        weather = excluded.weather,
        pop = excluded.pop,
        comfort = excluded.comfort,
        updated_at = CURRENT_TIMESTAMP;
    """

    records_df = df.copy()
    if "startTime" in records_df.columns:
        records_df["startTime"] = records_df["startTime"].astype(str)
    if "endTime" in records_df.columns:
        records_df["endTime"] = records_df["endTime"].astype(str)

    records = records_df.to_dict(orient="records")

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(upsert_sql, records)
        inserted_count = cursor.rowcount
        logger.info("Successfully upserted %d records into database.", inserted_count)
        return inserted_count


def query_forecast_data(
    location_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Query weather forecast records from SQLite database into a Pandas DataFrame.

    :param location_name: Optional county/location name filter.
    :param start_date: Optional start date/time string filter (>=).
    :param end_date: Optional end date/time string filter (<=).
    :param db_path: Optional custom database path.
    :return: Filtered Pandas DataFrame.
    """
    create_tables(db_path)

    query = """
    SELECT 
        location_name AS locationName,
        start_time AS startTime,
        end_time AS endTime,
        min_temp AS minTemp,
        max_temp AS maxTemp,
        temp_diff AS tempDiff,
        avg_temp AS avgTemp,
        weather,
        pop,
        comfort,
        updated_at AS updatedAt
    FROM weather_forecasts
    WHERE 1=1
    """
    params: List[Any] = []

    if location_name:
        query += " AND location_name = ?"
        params.append(location_name)

    if start_date:
        query += " AND start_time >= ?"
        params.append(str(start_date))

    if end_date:
        query += " AND start_time <= ?"
        params.append(str(end_date))

    query += " ORDER BY location_name, start_time"

    with get_db_connection(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    if not df.empty:
        if "startTime" in df.columns:
            df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce")
        if "endTime" in df.columns:
            df["endTime"] = pd.to_datetime(df["endTime"], errors="coerce")

    logger.info("Executed SQL query, returned %d rows.", len(df))
    return df


def get_all_locations(db_path: Optional[str] = None) -> List[str]:
    """
    Retrieve distinct location names from database sorted alphabetically.

    :param db_path: Optional custom database path.
    :return: List of location name strings.
    """
    create_tables(db_path)
    sql = "SELECT DISTINCT location_name FROM weather_forecasts ORDER BY location_name"

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [row["location_name"] for row in rows]


def get_latest_update_time(db_path: Optional[str] = None) -> Optional[str]:
    """
    Retrieve latest updated_at timestamp from database.

    :param db_path: Optional custom database path.
    :return: Timestamp string or None if database is empty.
    """
    create_tables(db_path)
    sql = "SELECT MAX(updated_at) AS max_update FROM weather_forecasts"

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        if row and row["max_update"]:
            return str(row["max_update"])
        return None
