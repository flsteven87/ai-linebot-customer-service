"""
基礎 Agent 類別，定義共通的 Agent 介面。
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AgentResponse(BaseModel):
    """
    Agent 回應的資料模型。
    """
    content: str
    confidence: float = 1.0

class BaseAgent:
    """
    所有 Agent 的基礎類別，定義共通介面。
    """
    def __init__(self, name: str, description: str):
        """
        初始化 Agent。
        
        Args:
            name: Agent 名稱
            description: Agent 描述
        """
        self.name = name
        self.description = description
        
    async def initialize(self):
        """
        初始化 Agent，如載入模型等耗時操作。
        預設為空實作，子類可以根據需要覆寫。
        """
        pass
        
    async def process(self, user_id: str, message: str) -> AgentResponse:
        """
        處理用戶訊息，返回回應。
        
        Args:
            user_id: 用戶 ID
            message: 用戶發送的訊息
            
        Returns:
            AgentResponse: 包含回覆內容與信心度等資訊
        """
        raise NotImplementedError("子類必須實作 process 方法")
    
    async def get_metadata(self) -> Dict[str, Any]:
        """
        獲取 Agent 的元數據，可用於診斷和監控。
        
        Returns:
            Dict[str, Any]: Agent 元數據
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        } 