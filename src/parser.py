"""
Parser module for CWA API JSON responses.

Extracts structured weather information from raw JSON payload responses
received from Central Weather Administration (CWA) Open Data endpoints.
Includes temperature feature extraction (MinT, MaxT, range, average).
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JSONParseError(Exception):
    """Custom exception raised when CWA JSON payload cannot be parsed."""

    pass


def extract_locations(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract raw location records from CWA F-C0032-001 JSON dataset.

    :param json_data: Raw CWA API JSON response dictionary.
    :return: List of location dictionaries.
    :raises JSONParseError: Raised when input is invalid or missing required 'records'.
    """
    if not isinstance(json_data, dict):
        raise JSONParseError("Input json_data must be a dictionary.")

    records = json_data.get("records")
    if not isinstance(records, dict):
        logger.error("JSON payload missing 'records' dictionary.")
        raise JSONParseError("Invalid CWA JSON format: missing 'records' dictionary.")

    locations = records.get("location")
    if not isinstance(locations, list):
        logger.warning("'location' field in 'records' is missing or not a list.")
        return []

    return locations


def parse_location_weather(location_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse weather elements for a single location record.

    :param location_dict: Dictionary containing a single location record.
    :return: Structured dictionary containing locationName and parsed elements.
    """
    location_name = location_dict.get("locationName", "Unknown")
    weather_elements = location_dict.get("weatherElement", [])

    elements_parsed: Dict[str, List[Dict[str, Any]]] = {}
    for element in weather_elements:
        element_name = element.get("elementName")
        times = element.get("time", [])

        time_slots: List[Dict[str, Any]] = []
        for t in times:
            parameter = t.get("parameter", {})
            time_slots.append(
                {
                    "startTime": t.get("startTime"),
                    "endTime": t.get("endTime"),
                    "parameterName": parameter.get("parameterName"),
                    "parameterValue": parameter.get("parameterValue"),
                    "parameterUnit": parameter.get("parameterUnit"),
                }
            )
        if element_name:
            elements_parsed[element_name] = time_slots

    return {
        "locationName": location_name,
        "elements": elements_parsed,
    }


def parse_forecast_json(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse full CWA F-C0032-001 JSON dataset into a list of parsed location weather data.

    :param json_data: Raw CWA API JSON response dictionary.
    :return: List of parsed location weather dictionaries.
    """
    locations = extract_locations(json_data)
    results = []
    for loc in locations:
        parsed_loc = parse_location_weather(loc)
        results.append(parsed_loc)
    return results


def parse_temperature_value(val_str: Optional[Any]) -> Optional[float]:
    """
    Safely convert a temperature parameter value string to float.

    :param val_str: Temperature value representation (e.g., '24', '31.5').
    :return: Float value or None if conversion fails.
    """
    if val_str is None:
        return None
    try:
        return float(val_str)
    except (ValueError, TypeError):
        logger.warning("Failed to convert temperature value '%s' to float.", val_str)
        return None


def extract_temperature_records(parsed_location: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract flattened temperature records (MinT, MaxT, diff, avg) per time interval.

    :param parsed_location: Dictionary returned by parse_location_weather().
    :return: List of time-slot temperature dictionaries.
    """
    location_name = parsed_location.get("locationName", "Unknown")
    elements = parsed_location.get("elements", {})

    mint_list = elements.get("MinT", [])
    maxt_list = elements.get("MaxT", [])
    wx_list = elements.get("Wx", [])
    pop_list = elements.get("PoP", [])
    ci_list = elements.get("CI", [])

    records: List[Dict[str, Any]] = []

    for i, mint_slot in enumerate(mint_list):
        start_time = mint_slot.get("startTime")
        end_time = mint_slot.get("endTime")

        min_temp = parse_temperature_value(mint_slot.get("parameterName"))

        maxt_slot = maxt_list[i] if i < len(maxt_list) else {}
        max_temp = parse_temperature_value(maxt_slot.get("parameterName"))

        wx_slot = wx_list[i] if i < len(wx_list) else {}
        weather_text = wx_slot.get("parameterName", "")

        pop_slot = pop_list[i] if i < len(pop_list) else {}
        pop_val = parse_temperature_value(pop_slot.get("parameterName"))

        ci_slot = ci_list[i] if i < len(ci_list) else {}
        comfort_text = ci_slot.get("parameterName", "")

        temp_diff = (
            round(max_temp - min_temp, 1)
            if (max_temp is not None and min_temp is not None)
            else None
        )
        avg_temp = (
            round((max_temp + min_temp) / 2.0, 1)
            if (max_temp is not None and min_temp is not None)
            else None
        )

        records.append(
            {
                "locationName": location_name,
                "startTime": start_time,
                "endTime": end_time,
                "minTemp": min_temp,
                "maxTemp": max_temp,
                "tempDiff": temp_diff,
                "avgTemp": avg_temp,
                "weather": weather_text,
                "pop": pop_val,
                "comfort": comfort_text,
            }
        )

    return records
