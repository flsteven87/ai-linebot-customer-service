# AI LineBot 客服系統

AI LineBot 客服系統是一個為台灣中小品牌設計的LINE客服機器人，旨在自動回答常見問題、轉接人工客服，以及提供每日摘要報告。

## 功能特點

- 自動回答FAQ（基於RAG技術）
- 智能轉接人工客服
- 每日摘要推播通知
- 簡單易用的API介面

## 技術堆疊

- **後端框架**: FastAPI
- **LINE SDK**: line-bot-sdk
- **AI 模型**: OpenAI GPT-4o-mini
- **向量資料庫**: PostgreSQL + pgvector
- **ORM**: SQLModel

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設置環境變數

複製 `.env.example` 到 `.env` 並填入相關設定：

```bash
cp .env.example .env
```

### 3. 啟動服務

```bash
uvicorn app.main:app --reload
```

訪問 http://localhost:8000/docs 查看API文檔。

## 開發指南

詳細的開發規範和架構說明請參閱 [PLANNING.md](PLANNING.md)。

## 授權

本專案使用 MIT 授權，詳見 LICENSE 文件。
