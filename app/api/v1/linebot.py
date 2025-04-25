"""
LINE Bot webhook API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header
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

def get_line_service():
    """
    Dependency to get LINE Bot service.
    
    Returns:
        LineBotService: Instance of LINE Bot service.
    """
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        return LineBotService(line_api, handler)

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