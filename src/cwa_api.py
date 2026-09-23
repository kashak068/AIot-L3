"""
Central Weather Administration (CWA) API Client Module

Provides HTTP request functionality to interact with Taiwan's CWA Open Data API.
Integrates with src.config for secure environment configurations.
"""

import logging
from typing import Any, Dict, Optional
import requests

from src.config import DEFAULT_CWA_BASE_URL, get_cwa_api_key, get_cwa_base_url

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # HTTP request timeout in seconds


class CWAAPIError(Exception):
    """Custom exception raised for CWA API errors."""

    pass


class CWAApiClient:
    """Client for interacting with the Central Weather Administration (CWA) Open Data API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the CWA API Client.

        :param api_key: CWA API Authorization Key. Defaults to get_cwa_api_key().
        :param base_url: Base URL for CWA API endpoints. Defaults to get_cwa_base_url().
        :param timeout: HTTP request timeout duration in seconds.
        """
        self.api_key = api_key or get_cwa_api_key()
        self.base_url = (base_url or get_cwa_base_url()).rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            logger.warning("CWA API key is not configured.")

    def get_dataset(
        self,
        dataset_id: str = "F-C0032-001",
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch a weather dataset from the CWA Open Data API.

        :param dataset_id: CWA Dataset ID (default: 'F-C0032-001' for 36-hour forecast).
        :param params: Additional query parameters.
        :return: Parsed JSON response dictionary.
        :raises CWAAPIError: Raised when API key is missing, request times out,
                             HTTP error occurs, or response is not valid JSON.
        """
        if not self.api_key:
            raise CWAAPIError(
                "Missing API key. Please configure CWA_API_KEY in your environment or .env file."
            )

        url = f"{self.base_url}/{dataset_id}"
        query_params = {"Authorization": self.api_key}
        if params:
            query_params.update(params)

        logger.info("Sending HTTP GET request to CWA API dataset: %s", dataset_id)

        try:
            response = requests.get(
                url,
                params=query_params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout as err:
            logger.error("Request to CWA API timed out (%ss): %s", self.timeout, err)
            raise CWAAPIError(
                f"CWA API request timed out after {self.timeout} seconds."
            ) from err
        except requests.exceptions.HTTPError as err:
            logger.error("HTTP error from CWA API (%s): %s", dataset_id, err)
            raise CWAAPIError(
                f"CWA API returned HTTP status {response.status_code}."
            ) from err
        except requests.exceptions.RequestException as err:
            logger.error("Network error when connecting to CWA API: %s", err)
            raise CWAAPIError(f"CWA API request failed: {err}") from err

        try:
            data = response.json()
            logger.info("Successfully retrieved JSON response for dataset: %s", dataset_id)
            return data
        except ValueError as err:
            logger.error("Failed to parse JSON response from CWA API: %s", err)
            raise CWAAPIError("Invalid JSON response received from CWA API.") from err

    def fetch_forecast_36h(self, location_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to fetch 36-hour general weather forecast (F-C0032-001).

        :param location_name: Optional county/location name to filter (e.g., '臺北市').
        :return: Parsed JSON response dictionary.
        """
        params = {}
        if location_name:
            params["locationName"] = location_name
        return self.get_dataset(dataset_id="F-C0032-001", params=params)
