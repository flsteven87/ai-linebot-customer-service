"""
LINE Bot webhook API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header, BackgroundTasks
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.config import settings
from app.services.linebot_service import LineBotService

router = APIRouter(prefix="/linebot", tags=["LINE Bot"])

# Initialize LINE SDK components
configuration = Configuration(access_token=settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

# 緩存 LINE Bot 服務實例
_line_service_instance = None

async def get_line_service():
    """
    Dependency to get LINE Bot service.
    
    Returns:
        LineBotService: Instance of LINE Bot service.
    """
    global _line_service_instance
    
    # 如果已經有實例，直接返回
    if _line_service_instance is not None:
        return _line_service_instance
    
    # 建立新實例，並進行初始化
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        _line_service_instance = LineBotService(line_api, handler)
        await _line_service_instance.initialize()
        return _line_service_instance

@router.post("/webhook")
async def webhook(
    request: Request, 
    x_line_signature: Optional[str] = Header(None),
    line_service: LineBotService = Depends(get_line_service)
):
    """
    LINE Bot webhook endpoint.
    
    Args:
        request (Request): The incoming webhook request.
        x_line_signature (str): LINE signature header.
        line_service (LineBotService): LINE Bot service instance.
        
    Returns:
        dict: Response message.
    """
    if x_line_signature is None:
        raise HTTPException(status_code=400, detail="X-Line-Signature header is missing")
        
    # Get request body as text
    body = await request.body()
    body_text = body.decode('utf-8')
    
    try:
        # Process webhook body with handler
        line_service.handle_webhook(body_text, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        # 記錄更詳細的錯誤信息
        import traceback
        error_details = traceback.format_exc()
        print(f"Webhook 處理錯誤: {error_details}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    return {"status": "ok"}

# 定義請求的數據模型
class TestMessageRequest(BaseModel):
    user_id: str
    message: str

@router.post("/test/push")
async def test_push_message(
    request: TestMessageRequest,
    line_service: LineBotService = Depends(get_line_service)
):
    """
    測試端點，直接推送訊息給指定用戶。
    
    Args:
        request (TestMessageRequest): 請求數據，包含用戶ID和訊息內容。
        line_service (LineBotService): LINE Bot 服務實例。
        
    Returns:
        dict: 回應訊息。
    """
    try:
        response = line_service.push_text(request.user_id, request.message)
        return {"status": "ok", "response": response}
    except Exception as e:
        # 記錄更詳細的錯誤信息
        import traceback
        error_details = traceback.format_exc()
        print(f"推送訊息錯誤: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")
        
@router.get("/verify")
async def verify_webhook():
    """
    簡單的驗證端點，可用於測試 LINE Webhook 是否設置正確。
    
    Returns:
        dict: 成功消息。
    """
    return {"status": "ok", "message": "LINE Webhook URL is valid"}

# === 新增的 Agent 相關 API ===

@router.get("/agents")
async def get_agents(
    line_service: LineBotService = Depends(get_line_service)
):
    """
    獲取所有可用的 Agent 列表。
    
    Args:
        line_service (LineBotService): LINE Bot 服務實例。
        
    Returns:
        List[Dict]: Agent 資訊列表。
    """
    try:
        agents = await line_service.agent_service.get_available_agents()
        return {"agents": agents}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"獲取 Agent 列表錯誤: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

@router.post("/test/agent")
async def test_agent_message(
    request: TestMessageRequest,
    line_service: LineBotService = Depends(get_line_service)
):
    """
    測試端點，直接使用 Agent 處理訊息並返回結果，而不發送給用戶。
    
    Args:
        request (TestMessageRequest): 請求數據，包含用戶ID和訊息內容。
        line_service (LineBotService): LINE Bot 服務實例。
        
    Returns:
        dict: 包含 Agent 回覆的訊息。
    """
    try:
        response = await line_service.agent_service.process_message(
            request.user_id, 
            request.message
        )
        return {"status": "ok", "response": response}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Agent 處理訊息錯誤: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}") 