"""
Taiwan Weather Forecast - Streamlit Web Application

Main entry point for the interactive web dashboard displaying weather observation
and forecast data fetched from CWA API and persisted in SQLite.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def init_page():
    """Configure page title, icon, and wide layout."""
    st.set_page_config(
        page_title="Taiwan Weather Forecast ⛅",
        page_icon="⛅",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header():
    """Render dashboard title and intro banner."""
    st.title("⛅ Taiwan Weather Forecast 台灣氣候觀測與預報儀表板")
    st.caption(
        "資料來源：交通部中央氣象署 (CWA OpenData API) | 支援本機 SQLite 快取與歷史資料查詢"
    )
    st.divider()


def render_sidebar():
    """Render sidebar configuration and controls."""
    with st.sidebar:
        st.header("⚙️ 儀表板控制台")
        st.info("💡 提供縣市切換、日期範圍過濾與資料同步功能")
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
    render_header()

    st.subheader("📊 氣溫指標與視覺化看板 (介面初始化完成)")
    st.info("✅ 專案介面佈局初始化成功。接下來將銜接 SQLite 資料庫進行動態數據渲染。")


if __name__ == "__main__":
    main()
