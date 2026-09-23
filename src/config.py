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
    Retrieve the CWA API key.

    Lookup order:
    1. ``st.secrets["CWA_API_KEY"]`` – Streamlit Community Cloud secrets.
    2. ``CWA_API_KEY`` environment variable – local ``.env`` file.

    :return: The CWA_API_KEY string if set, otherwise None.
    """
    # Try Streamlit secrets first (works on Streamlit Cloud)
    try:
        import streamlit as st
        api_key = st.secrets.get("CWA_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass

    # Fallback to environment variable (local development with .env)
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        logger.warning(
            "CWA_API_KEY is not configured. "
            "Set it in Streamlit Secrets or in a local .env file."
        )
    return api_key



def get_cwa_base_url() -> str:
    """
    Retrieve the CWA API base URL from environment variables.

    :return: CWA API base URL string.
    """
    base_url = os.getenv("CWA_API_BASE_URL", DEFAULT_CWA_BASE_URL)
    return base_url.rstrip("/")
