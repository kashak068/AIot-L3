"""
Taiwan Weather Forecast - Streamlit Web Application

This file serves as the main entry point for the interactive web dashboard.
Core features (CWA API fetching, SQLite query, charts) will be connected here.
"""

import streamlit as st


def main():
    st.set_page_config(
        page_title="Taiwan Weather Forecast",
        page_icon="⛅",
        layout="wide",
    )

    st.title("⛅ Taiwan Weather Forecast 台灣氣溫觀測與預報")
    st.markdown(
        """
        歡迎使用 **Taiwan Weather Forecast** 儀表板。
        
        本專案目標：
        1. 串接中央氣象署 (CWA) API 取得台灣各地氣象資料。
        2. 透過 Python 解析 JSON 資料。
        3. 將觀測與預報資料儲存至 SQLite 資料庫。
        4. 使用 Streamlit 呈現視覺化與互動式分析。
        
        > 🚧 **目前狀態**：專案架構已初始化完成，尚未實作資料串接功能。
        """
    )


if __name__ == "__main__":
    main()
