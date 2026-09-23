"""
Unit tests for map visualization module (src/map_visualization.py).
"""

import unittest
import folium
import pandas as pd

from src.map_visualization import (
    TAIWAN_COUNTY_COORDS,
    create_taiwan_weather_map,
    get_temperature_color,
)


class TestMapVisualization(unittest.TestCase):
    """Test suite for map visualization module."""

    def test_get_temperature_color(self):
        """Test temperature color scale function."""
        self.assertEqual(get_temperature_color(10.0), "#3182ce")
        self.assertEqual(get_temperature_color(18.0), "#38a169")
        self.assertEqual(get_temperature_color(22.0), "#ecc94b")
        self.assertEqual(get_temperature_color(28.0), "#ed8936")
        self.assertEqual(get_temperature_color(32.0), "#e53e3e")
        self.assertEqual(get_temperature_color(None), "#718096")

    def test_create_taiwan_weather_map(self):
        """Test creating Folium map object with weather DataFrame."""
        sample_df = pd.DataFrame(
            [
                {
                    "locationName": "臺北市",
                    "minTemp": 24.0,
                    "maxTemp": 31.0,
                    "avgTemp": 27.5,
                    "weather": "晴時多雲",
                    "pop": 10.0,
                    "comfort": "舒適",
                },
                {
                    "locationName": "高雄市",
                    "minTemp": 26.0,
                    "maxTemp": 33.0,
                    "avgTemp": 29.5,
                    "weather": "多雲",
                    "pop": 20.0,
                    "comfort": "悶熱",
                },
            ]
        )

        folium_map = create_taiwan_weather_map(sample_df)
        self.assertIsInstance(folium_map, folium.Map)
        self.assertEqual(folium_map.location, [23.7, 120.95])

    def test_create_map_empty_dataframe(self):
        """Test creating map with empty DataFrame returns valid base map."""
        empty_df = pd.DataFrame()
        folium_map = create_taiwan_weather_map(empty_df)
        self.assertIsInstance(folium_map, folium.Map)


if __name__ == "__main__":
    unittest.main()
