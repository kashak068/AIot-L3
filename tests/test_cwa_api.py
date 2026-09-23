"""
Unit and integration tests for CWA API Client (src/cwa_api.py).
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import requests

from src.cwa_api import CWAAPIError, CWAApiClient


class TestCWAApiClient(unittest.TestCase):
    """Test suite for CWAApiClient."""

    def setUp(self):
        """Set up client instance for testing."""
        self.test_api_key = "test_api_key_12345"
        self.client = CWAApiClient(api_key=self.test_api_key)

    def test_missing_api_key_raises_error(self):
        """Test that client without API key raises CWAAPIError upon fetching dataset."""
        client_no_key = CWAApiClient(api_key="")

        with patch.dict(os.environ, {}, clear=True):
            client_no_key.api_key = ""
            with self.assertRaises(CWAAPIError) as ctx:
                client_no_key.get_dataset("F-C0032-001")
            self.assertIn("Missing API key", str(ctx.exception))

    @patch("src.cwa_api.requests.get")
    def test_get_dataset_success(self, mock_get):
        """Test successful dataset retrieval returning JSON."""
        expected_json = {
            "success": "true",
            "result": {"resource_id": "F-C0032-001"},
            "records": {"location": [{"locationName": "臺食"}]},
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_json
        mock_get.return_value = mock_response

        data = self.client.get_dataset("F-C0032-001")

        self.assertEqual(data, expected_json)
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["timeout"], 10)
        self.assertEqual(kwargs["params"]["Authorization"], self.test_api_key)

    @patch("src.cwa_api.requests.get")
    def test_get_dataset_http_error(self, mock_get):
        """Test handling of HTTP errors (e.g. 401, 404)."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "401 Client Error: Unauthorized"
        )
        mock_get.return_value = mock_response

        with self.assertRaises(CWAAPIError) as ctx:
            self.client.get_dataset("F-C0032-001")
        self.assertIn("HTTP status 401", str(ctx.exception))

    @patch("src.cwa_api.requests.get")
    def test_get_dataset_timeout_error(self, mock_get):
        """Test handling of request timeouts."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        with self.assertRaises(CWAAPIError) as ctx:
            self.client.get_dataset("F-C0032-001")
        self.assertIn("timed out", str(ctx.exception))

    @patch("src.cwa_api.requests.get")
    def test_custom_base_url_and_params(self, mock_get):
        """Test custom base URL and additional query parameters."""
        custom_base = "https://custom.api.endpoint/v1"
        client = CWAApiClient(
            api_key=self.test_api_key, base_url=custom_base, timeout=15
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {"success": "true"}
        mock_get.return_value = mock_response

        client.get_dataset("F-C0032-001", params={"locationName": "臺北市"})

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://custom.api.endpoint/v1/F-C0032-001")
        self.assertEqual(kwargs["params"]["locationName"], "臺北市")
        self.assertEqual(kwargs["timeout"], 15)


if __name__ == "__main__":
    unittest.main()
