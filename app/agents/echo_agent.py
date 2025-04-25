"""
Echo Agent 實現，用於測試 Agent 框架。
"""
from app.agents.base_agent import BaseAgent, AgentResponse

class EchoAgent(BaseAgent):
    """
    簡單的 Echo Agent，回覆使用者發送的訊息。
    """
    
    def __init__(self):
        super().__init__(
            name="Echo Agent",
            description="一個簡單的 Echo Agent，用於測試"
        )
    
    async def process(self, user_id: str, message: str) -> AgentResponse:
        """
        處理用戶訊息，直接回覆相同的訊息。
        
        Args:
            user_id: 用戶 ID
            message: 用戶發送的訊息
            
        Returns:
            AgentResponse: 包含回覆內容與信心度
        """
        return AgentResponse(
            content=f"Echo: {message}",
            confidence=1.0
        ) 