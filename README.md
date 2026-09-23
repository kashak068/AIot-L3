# Taiwan Weather Forecast ⛅ 台灣氣象觀測與預報系統

本專案使用台灣交通部中央氣象署（CWA）開放資料 API，取得全台各地氣候與氣溫資訊，透過 Python 模組進行 JSON 解析與結構化清理，持久化儲存至 SQLite 資料庫，並運用 Streamlit 與 Folium 構建兼具互動性、地理視覺化與現代化體驗的 Web 儀表板。

---

## 核心技術棧 (Tech Stack)

- **Language**: Python 3.11+
- **API Communication**: Requests, python-dotenv
- **Data Source**: CWA OpenData API (中央氣象署開放資料)
- **Data Processing**: Pandas, JSON
- **Database**: SQLite3
- **Web App**: Streamlit
- **Geospatial Map**: Folium, streamlit-folium
- **Testing**: Pytest, Unittest
- **Version Control & CI/CD**: Git, GitHub, GitHub Actions

---

## 24 步驟專案開發藍圖 (24-Step Roadmap)

```text
[ 基礎篇 01-03 ] ──> [ API與解析 04-07 ] ──> [ 資料庫 08-10 ] ──> [ 儀表板 11-16 ] ──> [ 高級地圖與選單 17-19 ] ──> [ 品質與部署 20-24 ]
```

1. **Step 01** 建立專案結構與基礎相依套件定義
2. **Step 02** README 文件與 24 步驟課程指南
3. **Step 03** CWA API Key 與 `.env` 環境變數配置
4. **Step 04** CWA API HTTP 請求模組實作 (`requests`)
5. **Step 05** JSON 資料解析與結構化轉換
6. **Step 06** 最高溫 (MaxT) 與最低溫 (MinT) 特徵提取
7. **Step 07** Pandas DataFrame 資料清洗與型態轉換
8. **Step 08** SQLite 資料庫管理模組實作 (`db.py`)
9. **Step 09** SQLite Schema 資料表建立與欄位設計
10. **Step 10** SQL 查詢驗證與 API 快取機制測試
11. **Step 11** Streamlit Web App 基礎介面初始化 (`app.py`)
12. **Step 12** SQLite 至 Pandas 資料載入器銜接
13. **Step 13** 全台 22 縣市下拉式選單與過濾器
14. **Step 14** 氣溫趨勢動態折線圖表呈現
15. **Step 15** 結構化數據表格與匯出檢視
16. **Step 16** 整合型儀表板 Top Metrics 卡片佈局
17. **Step 17** 台灣互動式地理氣溫地圖 (Folium Map)
18. **Step 18** 日期與時間範圍篩選器 (Date Selector)
19. **Step 19** 完整端到端動態儀表板整合
20. **Step 20** 程式碼品質重構、例外處理與 Pytest 測試覆蓋
21. **Step 21** GitHub 儲存庫建立與遠端同步
22. **Step 22** 延伸應用模組與快取機制強化
23. **Step 23** 系統整合最終驗證 (`compileall` & `pytest`)
24. **Step 24** 最終文件定稿與 GitHub Release 同步

---

## 快速開始與環境建置

### 1. 建立並啟動虛擬環境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 3. 設定氣象署 API 金鑰

建立 `.env` 檔案並填入權碼（請參考 `.env.example`）：
```env
CWA_API_KEY=YOUR_CWA_API_KEY_HERE
```

### 4. 啟動 Web 應用程式

```bash
streamlit run app.py
```

### 5. 執行單元測試

```bash
python -m pytest
```
