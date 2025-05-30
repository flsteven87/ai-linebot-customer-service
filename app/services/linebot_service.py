"""
LINE Bot service for handling LINE webhook events.
"""
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import TextMessage
from linebot.v3.messaging.models import ReplyMessageRequest, PushMessageRequest
from linebot.v3.messaging.exceptions import ApiException
from typing import Dict, Any, List, Optional
import logging
import traceback
import asyncio

from app.config import settings
from app.services.agent_service import AgentService
from app.utils.storage import memory_storage

logger = logging.getLogger(__name__)

# LINE Bot 服務實例緩存
_instance = None

async def get_line_service() -> 'LineBotService':
    """
    獲取 LINE Bot 服務實例的工廠函數。
    如果實例已存在則返回現有實例，否則創建新實例。
    
    Returns:
        LineBotService: 已初始化的 LINE Bot 服務實例
    """
    global _instance
    
    if _instance is not None:
        return _instance
    
    # 建立新實例
    configuration = Configuration(access_token=settings.CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(settings.CHANNEL_SECRET)
    
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        service = LineBotService(line_api, handler)
        await service.initialize()
        _instance = service
        return service

class LineBotService:
    """
    Service class for LINE Bot operations.
    """
    
    def __init__(self, line_api: MessagingApi, handler: WebhookHandler):
        """
        Initialize the LINE Bot service.
        
        Args:
            line_api (MessagingApi): LINE Messaging API client.
            handler (WebhookHandler): LINE webhook handler.
        """
        self.line_api = line_api
        self.handler = handler
        self.agent_service = AgentService()
        
        # Set up event handlers
        self._setup_event_handlers()
        
        logger.info("LineBotService initialized")
    
    async def initialize(self):
        """初始化服務，包括所有 Agent。"""
        await self.agent_service.initialize()
        logger.info("Agent 服務初始化完成")
        
    def _setup_event_handlers(self):
        """
        Set up handlers for different types of LINE events.
        """
        # Handle text messages
        @self.handler.add(MessageEvent, message=TextMessageContent)
        def handle_text_message(event):
            # 使用非同步處理，但在同步環境下執行
            asyncio.create_task(self._async_process_text_message(event))
    
    def handle_webhook(self, body: str, signature: str) -> None:
        """
        Handle incoming webhook from LINE.
        
        Args:
            body (str): Request body.
            signature (str): X-Line-Signature header.
        """
        logger.debug(f"Handling webhook with signature: {signature}")
        try:
            self.handler.handle(body, signature)
            logger.debug("Webhook handled successfully")
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            logger.debug(f"Webhook body: {body}")
            logger.debug(f"Error traceback: {traceback.format_exc()}")
            raise
    
    async def _async_process_text_message(self, event: MessageEvent) -> None:
        """
        非同步處理文字訊息。
        
        Args:
            event (MessageEvent): The message event from LINE.
        """
        try:
            text = event.message.text
            reply_token = event.reply_token
            user_id = event.source.user_id
            
            logger.info(f"Received message from {user_id}: {text}")
            
            # 獲取或創建用戶的活躍對話
            conversation = memory_storage.get_active_conversation(user_id)
            
            # 記錄用戶訊息
            memory_storage.add_message(conversation.id, text, "user")
            
            # 使用 Agent Service 處理訊息
            response = await self.agent_service.process_message(user_id, text)
            
            # 記錄機器人回覆
            memory_storage.add_message(conversation.id, response, "bot")
            
            # 回覆用戶
            self.reply_text(reply_token, response)
            
        except Exception as e:
            logger.error(f"處理訊息時發生錯誤: {e}")
            logger.debug(f"錯誤詳情: {traceback.format_exc()}")
            # 發生錯誤時，回覆一個友好的錯誤訊息
            error_message = "抱歉，我暫時無法理解您的請求。請稍後再試。"
            self.reply_text(event.reply_token, error_message)
            
            # 如果對話已經創建，記錄錯誤回覆
            try:
                conversation = memory_storage.get_active_conversation(event.source.user_id)
                memory_storage.add_message(conversation.id, error_message, "bot")
            except Exception as storage_error:
                logger.error(f"記錄錯誤回覆時出現問題: {storage_error}")
    
    def reply_text(self, reply_token: str, text: str) -> Dict[str, Any]:
        """
        Reply to a message with text.
        
        Args:
            reply_token (str): The reply token from the event.
            text (str): The text to send.
            
        Returns:
            Dict[str, Any]: Response from LINE API.
        """
        try:
            logger.debug(f"Replying to token {reply_token} with text: {text}")
            message = TextMessage(text=text)
            
            # 創建 ReplyMessageRequest 物件
            reply_request = ReplyMessageRequest(
                replyToken=reply_token,
                messages=[message]
            )
            
            # 使用 ReplyMessageRequest 物件調用 reply_message 方法
            response = self.line_api.reply_message(reply_message_request=reply_request)
            
            logger.info(f"Message sent successfully with reply token: {reply_token}")
            return response
        except ApiException as e:
            logger.error(f"LINE API error when replying: {e}")
            logger.debug(f"Error traceback: {traceback.format_exc()}")
            raise
    
    def push_text(self, user_id: str, text: str) -> Dict[str, Any]:
        """
        Push a text message to a user.
        
        Args:
            user_id (str): User ID to send message to.
            text (str): The text to send.
            
        Returns:
            Dict[str, Any]: Response from LINE API.
        """
        try:
            logger.debug(f"Pushing message to user {user_id}: {text}")
            message = TextMessage(text=text)
            
            # 創建 PushMessageRequest 物件
            push_request = PushMessageRequest(
                to=user_id,
                messages=[message]
            )
            
            # 使用 PushMessageRequest 物件調用 push_message 方法
            response = self.line_api.push_message(push_message_request=push_request)
            
            logger.info(f"Message pushed successfully to user: {user_id}")
            return response
        except ApiException as e:
            logger.error(f"LINE API error when pushing: {e}")
            logger.debug(f"Error traceback: {traceback.format_exc()}")
            raise 