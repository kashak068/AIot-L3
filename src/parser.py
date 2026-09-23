"""
Parser module for CWA API JSON responses.

Extracts structured weather information from raw JSON payload responses
received from Central Weather Administration (CWA) Open Data endpoints.
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
