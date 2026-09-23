"""
Unit and smoke tests for Streamlit application (app.py).
"""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

import app


class TestStreamlitApp(unittest.TestCase):
    """Test suite for Streamlit app initialization and data loading."""

    @patch("streamlit.set_page_config")
    def test_init_page(self, mock_set_page_config):
        """Test page configuration initialization."""
        app.init_page()
        mock_set_page_config.assert_called_once_with(
            page_title="Taiwan Weather Forecast ⛅",
            page_icon="⛅",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    @patch("streamlit.title")
    @patch("streamlit.caption")
    @patch("streamlit.divider")
    def test_render_header(self, mock_divider, mock_caption, mock_title):
        """Test header rendering with timestamp."""
        app.render_header("2026-09-23 10:00:00")
        mock_title.assert_called_once()
        mock_caption.assert_called_once()
        mock_divider.assert_called_once()

    @patch("app.query_forecast_data")
    def test_load_weather_data_from_db(self, mock_query):
        """Test load_weather_data returning existing DB records."""
        sample_df = pd.DataFrame([{"locationName": "臺北市", "minTemp": 24}])
        mock_query.return_value = sample_df

        df = app.load_weather_data.__wrapped__()  # Access un-cached function for testing
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["locationName"], "臺北市")


if __name__ == "__main__":
    unittest.main()
