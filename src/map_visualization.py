"""
Map visualization module for Taiwan Weather Forecast.

Generates interactive Folium geospatial maps displaying Taiwan county temperature
markers, popup details, and color-coded temperature scales.
"""

import logging
from typing import Any, Dict, List, Optional
import folium
import pandas as pd

logger = logging.getLogger(__name__)

# Center coordinate of Taiwan
TAIWAN_CENTER = [23.7, 120.95]
DEFAULT_ZOOM = 7.5

# Representative geographic coordinates for Taiwan 22 counties
TAIWAN_COUNTY_COORDS: Dict[str, List[float]] = {
    "臺北市": [25.0375, 121.5637],
    "新北市": [24.9157, 121.6739],
    "基隆市": [25.1283, 121.7419],
    "桃園市": [24.9936, 121.3010],
    "新竹市": [24.8138, 120.9675],
    "新竹縣": [24.8387, 121.0177],
    "苗栗縣": [24.5602, 120.8217],
    "臺中市": [24.1477, 120.6736],
    "彰化縣": [24.0518, 120.5161],
    "南投縣": [23.9610, 120.9719],
    "雲林縣": [23.7092, 120.4313],
    "嘉義市": [23.4801, 120.4491],
    "嘉義縣": [23.4588, 120.5740],
    "臺南市": [22.9997, 120.2270],
    "高雄市": [22.6273, 120.3014],
    "屏東縣": [22.5519, 120.5487],
    "宜蘭縣": [24.7570, 121.7530],
    "花蓮縣": [23.9872, 121.6016],
    "臺東縣": [22.7613, 121.1444],
    "澎湖縣": [23.5711, 119.5793],
    "金門縣": [24.4493, 118.3766],
    "連江縣": [26.1505, 119.9499],
}


def get_temperature_color(temp: Optional[float]) -> str:
    """
    Get hex color code based on temperature value.

    :param temp: Temperature in Celsius.
    :return: Hex color code string.
    """
    if temp is None:
        return "#718096"  # Gray for missing data
    if temp < 15.0:
        return "#3182ce"  # Cool Blue
    elif temp < 20.0:
        return "#38a169"  # Mild Green
    elif temp < 25.0:
        return "#ecc94b"  # Comfortable Yellow
    elif temp < 30.0:
        return "#ed8936"  # Warm Orange
    else:
        return "#e53e3e"  # Hot Red


def create_taiwan_weather_map(
    df: pd.DataFrame, center: List[float] = TAIWAN_CENTER, zoom: float = DEFAULT_ZOOM
) -> folium.Map:
    """
    Create an interactive Folium map centered on Taiwan with CWA temperature markers.

    :param df: Weather DataFrame.
    :param center: Map center coordinates [lat, lon].
    :param zoom: Initial zoom level.
    :return: Folium Map object.
    """
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    if df.empty or "locationName" not in df.columns:
        logger.warning("Empty DataFrame passed to create_taiwan_weather_map.")
        return m

    # Group by locationName to get average/current temperature per county
    grouped = df.groupby("locationName").first().reset_index()

    for _, row in grouped.iterrows():
        loc_name = str(row["locationName"])
        coords = TAIWAN_COUNTY_COORDS.get(loc_name)

        if not coords:
            continue

        avg_temp = row.get("avgTemp")
        max_temp = row.get("maxTemp")
        min_temp = row.get("minTemp")
        weather = row.get("weather", "未知")
        comfort = row.get("comfort", "未知")
        pop = row.get("pop", "--")

        color = get_temperature_color(avg_temp if avg_temp is not None else max_temp)

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 160px;">
            <h4 style="margin: 0 0 6px 0; color: #2b6cb0;">📍 {loc_name}</h4>
            <hr style="margin: 4px 0;">
            <b>🌡️ 平均氣溫：</b> {avg_temp if avg_temp is not None else '--'} °C<br>
            <b>🔥 最高氣溫：</b> {max_temp if max_temp is not None else '--'} °C<br>
            <b>❄️ 最低氣溫：</b> {min_temp if min_temp is not None else '--'} °C<br>
            <b>🌤️ 天氣狀態：</b> {weather}<br>
            <b>🌧️ 降雨機率：</b> {pop}%<br>
            <b>🛋️ 體感舒適：</b> {comfort}
        </div>
        """

        folium.CircleMarker(
            location=coords,
            radius=12,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{loc_name}: {avg_temp if avg_temp is not None else max_temp}°C",
            color="#ffffff",
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
        ).add_to(m)

    return m
