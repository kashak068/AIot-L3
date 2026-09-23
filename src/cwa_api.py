"""
Central Weather Administration (CWA) API Client Module

This module provides a client interface for fetching weather data from Taiwan's
Central Weather Administration (CWA) Open Data API platform.
"""

import logging
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import requests

# Load environment variables from .env file if available
load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
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

        :param api_key: CWA API Authorization Key. Defaults to the CWA_API_KEY environment variable.
        :param base_url: Base URL for CWA API endpoints. Defaults to CWA_API_BASE_URL env var or official endpoint.
        :param timeout: HTTP request timeout duration in seconds (default: 10).
        """
        self.api_key = api_key or os.getenv("CWA_API_KEY")
        self.base_url = (
            base_url or os.getenv("CWA_API_BASE_URL", DEFAULT_BASE_URL)
        ).rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            logger.warning(
                "CWA_API_KEY is not set in environment variables or passed to CWAApiClient."
            )

    def get_dataset(
        self,
        dataset_id: str = "F-C0032-001",
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch a weather dataset from the CWA Open Data API.

        :param dataset_id: CWA Dataset ID (e.g., 'F-C0032-001' for 36-hour forecast).
        :param params: Additional query parameters (e.g., locationName, elementName).
        :return: Parsed JSON response dictionary.
        :raises CWAAPIError: Raised when API key is missing, request times out,
                             HTTP error occurs, or response is not valid JSON.
        """
        if not self.api_key:
            raise CWAAPIError(
                "Missing API key. Please set the CWA_API_KEY environment variable or pass api_key."
            )

        url = f"{self.base_url}/{dataset_id}"
        query_params = {"Authorization": self.api_key}
        if params:
            query_params.update(params)

        logger.info("Fetching data from CWA API dataset: %s", dataset_id)

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
            logger.info(
                "Successfully retrieved JSON response for dataset: %s", dataset_id
            )
            return data
        except ValueError as err:
            logger.error("Failed to parse JSON response from CWA API: %s", err)
            raise CWAAPIError("Invalid JSON response received from CWA API.") from err
