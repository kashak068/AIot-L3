# Taiwan Weather Forecast × Antigravity × GitHub 端到端開發與運作工作流程 🌤️

本文件定義 **Taiwan Weather Forecast** 專案的完整開發與系統架構工作流程（Workflow），涵蓋從**資料來源**、**後端 ETL 與資料庫**、**前端互動介面與地圖視覺化**到 **GitHub CI/CD 自動化** 的端到端整合計畫。

---

## 核心系統管線 (End-to-End Pipeline)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Taiwan Weather Forecast 端到端管線架構                           │
└────────────────────────────────────────────────────────────────────────────────────────┘

 1. 資料源           2. 資料解析         3. 本地儲存        4. 展示與互動       5. 地理視覺化       6. 自動化與版控
┌───────────┐     ┌─────────────┐     ┌───────────┐     ┌─────────────┐     ┌────────────┐     ┌────────────────┐
│ CWA API   │ ──> │ Python JSON │ ──> │  SQLite   │ ──> │  Streamlit  │ ──> │ 台灣地圖   │ ──> │ GitHub Actions │
│ (氣象署)  │     │ (Parser/ETL)│     │ (weather) │     │ (Dashboard) │     │ (Map View) │     │ (CI/CD Pipeline│
└───────────┘     └─────────────┘     └───────────┘     └─────────────┘     └────────────┘     └────────────────┘
```

---

## 使用者核心功能與工作流程 (User Features & Workflow)

系統最終提供使用者以下 8 大核心功能：

1. 📍 **選擇台灣地區**：可依「全台 22 縣市」及「鄉鎮/區域測站」進行彈性切換與過濾。
2. 📅 **選擇查詢日期**：提供日期選擇器（Date Picker）與時間區段選擇，支援檢視歷史紀錄或預報區段。
3. 🌡️ **查看最低／最高溫**：關鍵指標區塊（Metric Cards）即時呈現選定區域之最高溫、最低溫、平均溫與氣候狀態。
4. 📈 **查看氣溫折線圖**：繪製動態時序折線圖，呈現 24~36 小時氣溫變化趨勢與高低溫差。
5. 📊 **查看結構化資料表**：提供可搜尋、排序與下載的完整數據資料表（Pandas DataFrame）。
6. 🗺️ **台灣地圖氣溫分佈**：於互動式台灣地圖（Map View）上以熱調顏色與標籤即時呈現各縣市/測站氣溫。
7. 💾 **從 SQLite 讀取與快取**：所有介面數據優先透過 SQLite 資料庫做離線查詢與 API 請求節流快取。
8. 🚀 **專案同步至 GitHub**：程式碼變更自動發起 Git 提交並同步至 GitHub，觸發 CI/CD 自動化測試。

---

## 模組分工與開發階段 (Development Workflow Phases)

```mermaid
flowchart TD
    subgraph Phase1["階段一：資料擷取與解析 (API & Parser)"]
        A1[cwa_api.py: 發送 HTTP 請求] --> A2[parser.py: JSON 格式轉換與清洗]
    end

    subgraph Phase2["階段二：資料庫持久化 (SQLite DB)"]
        A2 --> B1[db.py: 建立 Schema 與 CRUD 介面]
        B1 --> B2[weather.db: SQLite 儲存與快取]
    end

    subgraph Phase3["階段三：Web 儀表板與地圖 (Streamlit UI)"]
        B2 --> C1[app.py: 地區/日期選擇器]
        C1 --> C2[最高/最低溫指標與趨勢折線圖]
        C1 --> C3[台灣地理地圖繪製 (PyDeck/Folium)]
        C1 --> C4[數據表格呈現]
    end

    subgraph Phase4["階段四：持續整合與自動化 (GitHub CI/CD)"]
        C1 --> D1[tests/: 單元與整合測試]
        D1 --> D2[.github/workflows/ci.yml: 自動測試與驗證]
        D2 --> D3[GitHub 遠端同步]
    end
```

---

## 各階段詳細運作說明

### 階段一：CWA API 資料擷取與 JSON 解析 (`src/cwa_api.py` & `src/parser.py`)
- **輸入**：中央氣象署 OpenData API 授權碼 (`CWA_API_KEY`)。
- **流程**：
  1. `cwa_api.py` 發送 GET 請求取得今明 36 小時預報 (`F-C0032-001`) 或自動站觀測 (`O-A0003-001`)。
  2. `parser.py` 將多層巢狀 JSON 解構為扁平化的結構（包含：縣市、測站、時間點、最高溫 `MaxT`、最低溫 `MinT`、體感舒適度 `CI`、天氣現象 `Wx`）。
- **產出**：標準化 Dict / Pandas DataFrame。

### 階段二：SQLite 資料庫管理 (`src/db.py` & `data/weather.db`)
- **流程**：
  1. 定義 `weather_records` 資料表結構。
  2. 實作 `save_weather_data()` 批量寫入或更新氣象資料。
  3. 實作 `get_weather_by_location_and_date()` 依地區與日期範圍檢索。
- **快取策略**：若請求時間在有效快取時間內，直接從 `weather.db` 讀取，避免重覆呼叫 CWA API。

### 階段三：Streamlit 互動介面與地圖視覺化 (`app.py`)
- **版面配置**：
  - **Sidebar 側邊欄**：縣市選單 (`st.selectbox`)、日期選擇器 (`st.date_input`)、手動更新資料按鈕 (`st.button`)。
  - **主要區域 Top**：最高溫、最低溫、平均溫與舒適度指標卡片 (`st.metric`)。
  - **主要區域 Middle**：時序氣溫趨勢折線圖 (`st.line_chart` 或 Plotly)。
  - **主要區域 Map**：台灣地圖氣溫熱力分佈圖 (`st.pydeck_chart` 或 Folium 地圖)。
  - **主要區域 Bottom**：原始數據資料表 (`st.dataframe`)。

### 階段四：GitHub CI/CD 自動化工作流程 (`.github/workflows/ci.yml`)
- **配置檔案**：`.github/workflows/ci.yml`
- **觸發時機**：Push 至 `main` 分支或提交 Pull Request。
- **執行步驟**：
  1. 自動拉取 GitHub 專案程式碼。
  2. 設定 Python 3.11 環境並啟用 `pip` 快取。
  3. 安裝 `requirements.txt` 相依套件。
  4. 注入 `CWA_API_KEY` 並自動執行 `python -m unittest discover tests` 確保程式碼品質。

---

## GitHub Secrets 與環境變數設定指南

在 GitHub 進行自動化測試前，請確認已設定 API Key Secret：
1. 前往 GitHub 專案：`https://github.com/kashak068/AIot-L3`
2. 點擊 **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**
3. 新增 Secret：`CWA_API_KEY` = `您的中央氣象署 API 金鑰`

---

## 開發者執行與同步指令庫

```powershell
# 1. 執行單元測試
python -m unittest discover tests

# 2. 本地啟動 Streamlit App
streamlit run app.py

# 3. 提交變更並同步至 GitHub
git add .
git commit -m "feat: complete end-to-end workflow architecture"
git push origin main
```
