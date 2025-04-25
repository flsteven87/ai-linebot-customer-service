"""
對話模型 - 用於追蹤用戶與機器人的對話
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID, uuid4

class Message(BaseModel):
    """訊息模型，代表對話中的一條訊息"""
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    content: str
    sender_type: Literal["user", "bot", "agent"]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True

class Conversation(BaseModel):
    """對話模型，代表一個完整的對話"""
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: Literal["active", "closed"] = "active"
    messages: List[Message] = []
    
    class Config:
        from_attributes = True
    
    def add_message(self, content: str, sender_type: Literal["user", "bot", "agent"]) -> Message:
        """
        添加一條新訊息到對話中
        
        Args:
            content: 訊息內容
            sender_type: 發送者類型 (user, bot, agent)
            
        Returns:
            新創建的訊息
        """
        message = Message(
            conversation_id=self.id,
            content=content,
            sender_type=sender_type
        )
        self.messages.append(message)
        return message
    
    def close(self):
        """關閉對話"""
        self.status = "closed"
        self.end_time = datetime.now() 