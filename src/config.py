"""
Configuration module for Taiwan Weather Forecast application.
Handles environment variable loading and application settings.
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_CWA_BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"


def get_cwa_api_key() -> Optional[str]:
    """
    Retrieve the CWA API key from environment variables.

    :return: The CWA_API_KEY string if set, otherwise None.
    """
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        logger.warning(
            "CWA_API_KEY environment variable is not configured. "
            "Please copy .env.example to .env and set your CWA_API_KEY."
        )
    return api_key


def get_cwa_base_url() -> str:
    """
    Retrieve the CWA API base URL from environment variables.

    :return: CWA API base URL string.
    """
    base_url = os.getenv("CWA_API_BASE_URL", DEFAULT_CWA_BASE_URL)
    return base_url.rstrip("/")
