"""
Unit and smoke tests for Streamlit application (app.py).
"""

import unittest
from unittest.mock import patch
import app


class TestStreamlitApp(unittest.TestCase):
    """Test suite for Streamlit app initialization functions."""

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
        """Test header rendering."""
        app.render_header()
        mock_title.assert_called_once()
        mock_caption.assert_called_once()
        mock_divider.assert_called_once()


if __name__ == "__main__":
    unittest.main()
