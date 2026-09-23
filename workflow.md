# GitHub Actions CI/CD Workflow 說明文件 🚀

本文件詳細說明 **Taiwan Weather Forecast** 專案所採用的 GitHub Actions 自動化持續整合（Continuous Integration, CI）流程設定。

---

## 1. 概念與架構概覽

專案配置了全自動化的 CI 流程（位於 [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml)）。每當開發者對 `main` 主分支提交程式碼或發起 Pull Request 時，GitHub Actions 將會自動開啟乾淨的 Linux 容器，進行環境建置、套件安裝及單元測試運行。

```text
┌─────────────────────────────────────────────────────────────┐
│                 GitHub Actions CI 工作流程圖                 │
└─────────────────────────────────────────────────────────────┘

   [ 代碼異動 (Push / Pull Request) ]
                   │
                   ▼
       ┌───────────────────────┐
       │   Git Checkout 程式碼  │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │   設定 Python 3.11    │ (開啟 Pip Cache)
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ 安裝相依套件          │ (pip install -r requirements.txt)
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ 執行單元測試 Suite     │ (python -m unittest discover tests)
       └───────────┬───────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
  [ 測試成功 ✅ ]         [ 測試失敗 ❌ ]
  (准許 Merge / Push)     (發送通知並阻擋 Merge)
```

---

## 2. 完整的 Workflow 設定檔 (ci.yml)

完整檔案位於 [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml)：

```yaml
name: Taiwan Weather Forecast CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: "pip"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Run unit tests
      run: |
        python -m unittest discover tests
      env:
        CWA_API_KEY: ${{ secrets.CWA_API_KEY }}
```

---

## 3. 詳細步驟剖析 (Step-by-Step Breakdown)

| 步驟名稱 | 使用 Action / 指令 | 目的說明 |
| :--- | :--- | :--- |
| **Checkout repository** | `actions/checkout@v4` | 將專案儲存庫之程式碼拉取到 CI 運行容器中。 |
| **Set up Python** | `actions/setup-python@v5` | 初始化 Python 3.11 執行環境，並啟用 `cache: "pip"` 加速套件下載。 |
| **Install dependencies** | `pip install -r requirements.txt` | 升級 `pip` 並安裝專案所需的套件（`requests`, `pandas`, `streamlit`, `python-dotenv` 等）。 |
| **Run unit tests** | `python -m unittest discover tests` | 自動搜尋並執行 `tests/` 資料夾下的所有單元測試案例。 |

---

## 4. 敏感資訊設定 (GitHub Secrets Management)

專案測試過程中需存取 CWA API 金鑰，請勿將真實 API Key 硬編碼於程式碼中。

### 設定步驟：
1. 開啟 GitHub 專案頁面 (`https://github.com/kashak068/AIot-L3`)。
2. 進入 **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**。
3. 點擊 **New repository secret**。
4. 設定 Name 為 `CWA_API_KEY`，Value 填入氣象署申請之授權碼。
5. CI 執行時會自動透過 `${{ secrets.CWA_API_KEY }}` 注入環境變數中。

---

## 5. 本機驗證與推送指南

在將程式碼推送到 GitHub 觸發 CI 之前，建議先在本地執行測試：

```powershell
# 1. 執行本地單元測試
python -m unittest discover tests

# 2. 提交 Workflow 檔案至 Git
git add .github/workflows/ci.yml workflow.md
git commit -m "docs: add workflow documentation"
git push origin main
```
