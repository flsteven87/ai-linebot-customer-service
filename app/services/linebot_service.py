"""
LINE Bot service for handling LINE webhook events.
"""
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import TextMessage
from linebot.v3.messaging.models import ReplyMessageRequest, PushMessageRequest
from linebot.v3.messaging.exceptions import ApiException
from typing import Dict, Any, List
import logging
import traceback

logger = logging.getLogger(__name__)

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
        
        # Set up event handlers
        self._setup_event_handlers()
        
        logger.info("LineBotService initialized")
    
    def _setup_event_handlers(self):
        """
        Set up handlers for different types of LINE events.
        """
        # Handle text messages
        @self.handler.add(MessageEvent, message=TextMessageContent)
        def handle_text_message(event):
            self._process_text_message(event)
    
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
    
    def _process_text_message(self, event: MessageEvent) -> None:
        """
        Process text messages from users.
        
        Args:
            event (MessageEvent): The message event from LINE.
        """
        # For now, just echo the message back
        try:
            text = event.message.text
            reply_token = event.reply_token
            user_id = event.source.user_id
            
            logger.info(f"Received message from {user_id}: {text}")
            
            # Create a response message
            self.reply_text(reply_token, f"您傳送的訊息：{text}")
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            logger.debug(f"Error traceback: {traceback.format_exc()}")
    
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