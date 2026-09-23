"""
Unit tests for configuration module (src/config.py).
"""

import os
import unittest
from unittest.mock import patch

from src.config import DEFAULT_CWA_BASE_URL, get_cwa_api_key, get_cwa_base_url


class TestConfigModule(unittest.TestCase):
    """Test suite for config module."""

    @patch.dict(os.environ, {"CWA_API_KEY": "test_secret_key_999"}, clear=True)
    def test_get_cwa_api_key_success(self):
        """Test retrieving CWA API key when present in environment."""
        self.assertEqual(get_cwa_api_key(), "test_secret_key_999")

    @patch.dict(os.environ, {}, clear=True)
    def test_get_cwa_api_key_missing(self):
        """Test behavior when CWA_API_KEY is not set."""
        self.assertIsNone(get_cwa_api_key())

    @patch.dict(os.environ, {"CWA_API_BASE_URL": "https://custom.endpoint.gov/api/"}, clear=True)
    def test_get_cwa_base_url_custom(self):
        """Test retrieving custom base URL with trailing slash stripped."""
        self.assertEqual(get_cwa_base_url(), "https://custom.endpoint.gov/api")

    @patch.dict(os.environ, {}, clear=True)
    def test_get_cwa_base_url_default(self):
        """Test retrieving default base URL when env var is not set."""
        self.assertEqual(get_cwa_base_url(), DEFAULT_CWA_BASE_URL)


if __name__ == "__main__":
    unittest.main()
