"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from dotenv import load_dotenv

# 確保 .env 文件被加載
load_dotenv()

# 設置日誌
logger = logging.getLogger(__name__)

# 檢查關鍵環境變數
if not settings.OPENAI_API_KEY:
    logger.warning("未設置 OPENAI_API_KEY 環境變數，Agno Agent 可能無法正常工作")
else:
    logger.info(f"OPENAI_API_KEY 已設置: {settings.OPENAI_API_KEY[:5]}...")

app = FastAPI(
    title="AI LineBot Customer Service",
    description="API for AI-powered LINE customer service bot",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routers
from app.api.v1.health import router as health_router
from app.api.v1.linebot import router as linebot_router

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(linebot_router, prefix="/api/v1")

@app.get("/")
async def root():
    """
    Root endpoint returning API information.
    
    Returns:
        dict: Basic API information.
    """
    return {
        "name": "AI LineBot Customer Service API", 
        "version": "0.1.0",
        "status": "active"
    } 