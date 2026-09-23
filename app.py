"""
Taiwan Weather Forecast - Streamlit Web Application

Main entry point for the interactive web dashboard displaying weather observation
and forecast data fetched from CWA API and persisted in SQLite.
"""

import logging
from typing import Optional
import pandas as pd
import streamlit as st

from src.config import get_cwa_api_key
from src.cwa_api import CWAAPIError, CWAApiClient
from src.db import get_latest_update_time, query_forecast_data, save_forecast_dataframe
from src.processor import process_forecast_to_dataframe

logger = logging.getLogger(__name__)


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


def render_sidebar():
    """Render sidebar configuration and controls."""
    with st.sidebar:
        st.header("⚙️ 儀表板控制台")

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


def main():
    """Main application entry point."""
    init_page()
    render_sidebar()

    # Load data from SQLite (or fetch API if empty)
    df = load_weather_data()
    latest_update = get_latest_update_time()

    render_header(latest_update)

    if df.empty:
        st.warning(
            "⚠️ 目前資料庫尚無氣候資料。請確認是否已於 `.env` 中設定有效的 `CWA_API_KEY`。"
        )
    else:
        st.success(f"✅ 成功從 SQLite 資料庫載入 `{len(df)}` 筆天氣預報數據！")


if __name__ == "__main__":
    main()
