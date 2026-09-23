"""
Database management module for Taiwan Weather Forecast.

Provides SQLite connection handling, path resolution, and transactional
context management for database operations.
"""

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

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
