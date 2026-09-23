"""
Data processor module for Taiwan Weather Forecast.

Converts parsed CWA weather data into cleaned, structured Pandas DataFrames
ready for database storage or dashboard visualization.
"""

import logging
from typing import Any, Dict, List, Optional
import pandas as pd

from src.parser import extract_temperature_records, parse_forecast_json

logger = logging.getLogger(__name__)


def process_forecast_to_dataframe(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Process raw CWA F-C0032-001 JSON data into a clean Pandas DataFrame.

    :param json_data: Raw CWA API JSON response dictionary.
    :return: Cleaned Pandas DataFrame containing weather forecast records.
    """
    parsed_locations = parse_forecast_json(json_data)
    all_records: List[Dict[str, Any]] = []

    for loc in parsed_locations:
        loc_records = extract_temperature_records(loc)
        all_records.extend(loc_records)

    columns = [
        "locationName",
        "startTime",
        "endTime",
        "minTemp",
        "maxTemp",
        "tempDiff",
        "avgTemp",
        "weather",
        "pop",
        "comfort",
    ]

    if not all_records:
        logger.warning("No weather records found to construct DataFrame.")
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(all_records)

    # Convert ISO / date strings to datetime objects
    if "startTime" in df.columns:
        df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce")
    if "endTime" in df.columns:
        df["endTime"] = pd.to_datetime(df["endTime"], errors="coerce")

    # Sort deterministically by locationName and startTime
    df = df.sort_values(by=["locationName", "startTime"]).reset_index(drop=True)

    logger.info("Successfully created weather DataFrame with %d rows.", len(df))
    return df


def filter_by_location(df: pd.DataFrame, location_name: str) -> pd.DataFrame:
    """
    Filter weather DataFrame by location name.

    :param df: Weather DataFrame.
    :param location_name: County or location name (e.g., '臺北市').
    :return: Filtered DataFrame.
    """
    if df.empty or "locationName" not in df.columns:
        return df
    return df[df["locationName"] == location_name].reset_index(drop=True)


def filter_by_temp_range(df: pd.DataFrame, min_temp: float, max_temp: float) -> pd.DataFrame:
    """Filter DataFrame rows based on temperature range.

    Keeps rows where both `minTemp` and `maxTemp` fall within the inclusive range.
    If temperature columns are missing, returns the original DataFrame unchanged.
    """
    if df.empty:
        return df
    if "minTemp" not in df.columns or "maxTemp" not in df.columns:
        logger.warning("Temperature columns missing for range filter; returning original DataFrame.")
        return df
    mask = (df["minTemp"] >= min_temp) & (df["maxTemp"] <= max_temp)
    return df[mask].reset_index(drop=True)


def filter_by_condition(df: pd.DataFrame, conditions: list[str]) -> pd.DataFrame:
    """Filter DataFrame rows based on weather condition values.

    `conditions` is a list of allowed weather condition strings (e.g., ["晴", "雨"]).
    If the `weather` column is absent, returns the original DataFrame unchanged.
    """
    if df.empty:
        return df
    if "weather" not in df.columns:
        logger.warning("'weather' column missing for condition filter; returning original DataFrame.")
        return df
    mask = df["weather"].isin(conditions)
    return df[mask].reset_index(drop=True)
