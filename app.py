"""
Taiwan Weather Forecast - Streamlit Web Application

Main entry point for the interactive web dashboard displaying weather observation
and forecast data fetched from CWA API and persisted in SQLite.
"""

import logging
from typing import List, Optional
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.config import get_cwa_api_key
from src.cwa_api import CWAAPIError, CWAApiClient
from src.db import (
    get_all_locations,
    get_latest_update_time,
    query_forecast_data,
    save_forecast_dataframe,
)
from src.map_visualization import create_taiwan_weather_map
from src.processor import process_forecast_to_dataframe

logger = logging.getLogger(__name__)

ALL_LOCATIONS_OPTION = "全台灣 (All Locations)"


def init_page():
    """Configure page title, icon, and wide layout."""
    st.set_page_config(
        page_title="Taiwan Weather Forecast ⛅",
        page_icon="⛅",
        layout="wide",
        initial_sidebar_state="expanded",
    )


@st.cache_data(ttl=300)
def load_weather_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load weather forecast data from SQLite database into Pandas DataFrame.
    If database is empty or force_refresh is True, fetches fresh data from CWA API.

    :param force_refresh: Force API refresh even if database records exist.
    :return: Pandas DataFrame containing weather forecast records.
    """
    df = query_forecast_data()

    if df.empty or force_refresh:
        api_key = get_cwa_api_key()
        if api_key:
            try:
                logger.info("Fetching fresh data from CWA API...")
                client = CWAApiClient(api_key=api_key)
                raw_json = client.fetch_forecast_36h()
                new_df = process_forecast_to_dataframe(raw_json)
                if not new_df.empty:
                    save_forecast_dataframe(new_df)
                    df = query_forecast_data()
            except CWAAPIError as err:
                logger.error("CWA API error: %s", err)
            except Exception as err:
                logger.error("Unexpected error fetching CWA data: %s", err)

    return df


def render_header(latest_update: Optional[str] = None):
    """Render dashboard title and intro banner."""
    st.title("⛅ Taiwan Weather Forecast 台灣氣候觀測與預報儀表板")

    subtitle = "資料來源：交通部中央氣象署 (CWA OpenData API) | 本機 SQLite 資料庫驅動"
    if latest_update:
        subtitle += f" | 最後同步時間：`{latest_update}`"

    st.caption(subtitle)
    st.divider()


def render_sidebar(available_locations: List[str]) -> str:
    """
    Render sidebar configuration, region dropdown selector, and controls.

    :param available_locations: List of location names available in database.
    :return: Selected location string (e.g. '全台灣 (All Locations)' or '臺北市').
    """
    with st.sidebar:
        st.header("⚙️ 儀表板控制台")

        location_options = [ALL_LOCATIONS_OPTION] + sorted(available_locations)
        selected_location = st.selectbox(
            "📍 選擇縣市區域",
            options=location_options,
            index=0,
            help="選擇欲檢視的台灣縣市區域，或選擇『全台灣』觀看全島總覽",
        )

        st.divider()

        api_key_set = bool(get_cwa_api_key())
        if api_key_set:
            st.success("✅ CWA API Key 已設定")
        else:
            st.warning("⚠️ 未偵測到 CWA_API_KEY (請設定 .env)")

        st.divider()
        st.markdown("### 關於專案 (System Info)")
        st.markdown(
            """
            - **Data Source**: CWA OpenData API
            - **Database**: SQLite3 (`weather.db`)
            - **Framework**: Streamlit + Folium Map
            """
        )

        return selected_location


def filter_data_by_location(
    df: pd.DataFrame, selected_location: str
) -> pd.DataFrame:
    """
    Filter DataFrame by selected location string.

    :param df: Input DataFrame.
    :param selected_location: Location string selected from sidebar dropdown.
    :return: Filtered DataFrame.
    """
    if df.empty or selected_location == ALL_LOCATIONS_OPTION:
        return df

    if "locationName" in df.columns:
        return df[df["locationName"] == selected_location].reset_index(drop=True)
    return df


def render_metrics(df: pd.DataFrame):
    """
    Render summary metric cards (Min Temp, Max Temp, Avg Temp, Rain PoP, Comfort).

    :param df: Filtered weather DataFrame.
    """
    st.subheader("📌 區域氣候重點指標速覽")

    if df.empty:
        st.info("尚無氣候數據可供指標計算呈現。")
        return

    max_temp = (
        df["maxTemp"].max()
        if "maxTemp" in df.columns and not df["maxTemp"].dropna().empty
        else None
    )
    min_temp = (
        df["minTemp"].min()
        if "minTemp" in df.columns and not df["minTemp"].dropna().empty
        else None
    )
    avg_temp = (
        round(df["avgTemp"].mean(), 1)
        if "avgTemp" in df.columns and not df["avgTemp"].dropna().empty
        else None
    )

    avg_pop = (
        round(df["pop"].mean(), 1)
        if "pop" in df.columns and not df["pop"].dropna().empty
        else None
    )

    most_common_comfort = (
        df["comfort"].mode().iloc[0]
        if "comfort" in df.columns and not df["comfort"].dropna().empty
        else "無資料"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="🔥 最高氣溫",
            value=f"{max_temp:.1f} °C" if max_temp is not None else "--",
        )

    with col2:
        st.metric(
            label="❄️ 最低氣溫",
            value=f"{min_temp:.1f} °C" if min_temp is not None else "--",
        )

    with col3:
        st.metric(
            label="🌡️ 平均氣溫",
            value=f"{avg_temp:.1f} °C" if avg_temp is not None else "--",
        )

    with col4:
        st.metric(
            label="🌧️ 平均降雨機率",
            value=f"{avg_pop:.0f} %" if avg_pop is not None else "--",
        )

    with col5:
        st.metric(
            label="🛋️ 體感舒適度",
            value=str(most_common_comfort),
        )


def render_temperature_map(df: pd.DataFrame):
    """
    Render interactive Folium map showing Taiwan temperature markers.

    :param df: Weather DataFrame.
    """
    st.subheader("🗺️ 台灣互動式地理氣溫地圖")
    if df.empty:
        st.info("尚無地理數據可提供地圖呈現。")
        return

    folium_map = create_taiwan_weather_map(df)
    st_folium(folium_map, width="100%", height=450)


def render_temperature_chart(df: pd.DataFrame):
    """
    Render temperature trend line chart for minTemp and maxTemp over time.

    :param df: Weather DataFrame containing startTime, minTemp, maxTemp.
    """
    st.subheader("📈 氣溫變化趨勢折線圖")

    if df.empty or "startTime" not in df.columns:
        st.info("尚無足夠之時間序列數據可進行折線圖繪製。")
        return

    chart_df = df.copy()

    if pd.api.types.is_datetime64_any_dtype(chart_df["startTime"]):
        chart_df["時間區段"] = chart_df["startTime"].dt.strftime("%m/%d %H:%M")
    else:
        chart_df["時間區段"] = chart_df["startTime"].astype(str)

    if "locationName" in chart_df.columns and len(chart_df["locationName"].unique()) > 1:
        pivot_df = chart_df.groupby("時間區段")[["minTemp", "maxTemp", "avgTemp"]].mean()
        pivot_df.columns = ["平均最低溫 (°C)", "平均最高溫 (°C)", "全島平均溫 (°C)"]
    else:
        pivot_df = chart_df.set_index("時間區段")[["minTemp", "maxTemp", "avgTemp"]]
        pivot_df.columns = ["最低溫 (°C)", "最高溫 (°C)", "平均溫 (°C)"]

    st.line_chart(pivot_df, use_container_width=True)


def render_data_table(df: pd.DataFrame):
    """
    Render structured weather forecast data table with formatting and CSV export button.

    :param df: Weather DataFrame.
    """
    st.subheader("📊 結構化數據明細表")

    if df.empty:
        st.info("尚無資料數據可提供資料表展示。")
        return

    display_df = df.copy()

    if "startTime" in display_df.columns and pd.api.types.is_datetime64_any_dtype(display_df["startTime"]):
        display_df["startTime"] = display_df["startTime"].dt.strftime("%Y-%m-%d %H:%M")
    if "endTime" in display_df.columns and pd.api.types.is_datetime64_any_dtype(display_df["endTime"]):
        display_df["endTime"] = display_df["endTime"].dt.strftime("%Y-%m-%d %H:%M")

    rename_map = {
        "locationName": "縣市名稱",
        "startTime": "預報開始時間",
        "endTime": "預報結束時間",
        "minTemp": "最低溫 (°C)",
        "maxTemp": "最高溫 (°C)",
        "tempDiff": "溫差 (°C)",
        "avgTemp": "平均溫 (°C)",
        "weather": "天氣現象",
        "pop": "降雨機率 (%)",
        "comfort": "體感舒適度",
    }

    cols_to_display = [c for c in rename_map.keys() if c in display_df.columns]
    formatted_df = display_df[cols_to_display].rename(columns=rename_map)

    st.dataframe(formatted_df, use_container_width=True, hide_index=True)

    csv_data = formatted_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 下載 CSV 資料表",
        data=csv_data,
        file_name="taiwan_weather_forecast.csv",
        mime="text/csv",
        help="點擊將當前過濾後之氣候數據下載為 CSV 試算表檔案",
    )


def main():
    """Main application entry point."""
    init_page()

    # Load data and available location list
    df = load_weather_data()
    locations = get_all_locations()
    selected_location = render_sidebar(locations)
    latest_update = get_latest_update_time()

    render_header(latest_update)

    if df.empty:
        st.warning(
            "⚠️ 目前資料庫尚無氣候資料。請確認是否已於 `.env` 中設定有效的 `CWA_API_KEY`。"
        )
        return

    filtered_df = filter_data_by_location(df, selected_location)

    st.subheader(f"📍 當前選擇區域：`{selected_location}`")

    # Render Metric Cards
    render_metrics(filtered_df)

    st.divider()

    # Render Taiwan Folium Map & Line Chart side-by-side or stacked
    map_col, chart_col = st.columns([1, 1])
    with map_col:
        render_temperature_map(filtered_df)
    with chart_col:
        render_temperature_chart(filtered_df)

    st.divider()

    # Render structured data table & CSV download button
    render_data_table(filtered_df)


if __name__ == "__main__":
    main()
