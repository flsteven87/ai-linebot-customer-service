"""
簡易儲存工具 - 用於在記憶體中儲存對話記錄
在實際生產環境中，這應該替換為資料庫儲存
"""
from typing import Dict, List, Optional
from uuid import UUID
from app.models.conversation import Conversation, Message

class MemoryStorage:
    """記憶體儲存類，管理對話和訊息"""
    
    def __init__(self):
        """初始化儲存"""
        self.conversations: Dict[UUID, Conversation] = {}
        self.user_conversations: Dict[str, List[UUID]] = {}
    
    def create_conversation(self, user_id: str) -> Conversation:
        """
        為用戶創建新對話
        
        Args:
            user_id: 用戶ID
            
        Returns:
            新創建的對話
        """
        conversation = Conversation(user_id=user_id)
        self.conversations[conversation.id] = conversation
        
        # 添加到用戶的對話列表
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []
        self.user_conversations[user_id].append(conversation.id)
        
        return conversation
    
    def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        獲取指定ID的對話
        
        Args:
            conversation_id: 對話ID
            
        Returns:
            對話對象，如果不存在則返回None
        """
        return self.conversations.get(conversation_id)
    
    def get_active_conversation(self, user_id: str) -> Optional[Conversation]:
        """
        獲取用戶的活躍對話，如果沒有則創建新對話
        
        Args:
            user_id: 用戶ID
            
        Returns:
            活躍對話
        """
        # 檢查用戶是否有對話
        if user_id in self.user_conversations:
            for conv_id in reversed(self.user_conversations[user_id]):
                conv = self.conversations.get(conv_id)
                if conv and conv.status == "active":
                    return conv
        
        # 沒有活躍對話，創建新對話
        return self.create_conversation(user_id)
    
    def add_message(self, 
                   conversation_id: UUID, 
                   content: str, 
                   sender_type: str) -> Optional[Message]:
        """
        添加訊息到對話
        
        Args:
            conversation_id: 對話ID
            content: 訊息內容
            sender_type: 發送者類型
            
        Returns:
            新添加的訊息，如果對話不存在則返回None
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return conversation.add_message(content, sender_type)
    
    def close_conversation(self, conversation_id: UUID) -> bool:
        """
        關閉對話
        
        Args:
            conversation_id: 對話ID
            
        Returns:
            是否成功關閉
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.close()
        return True
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """
        獲取用戶的所有對話
        
        Args:
            user_id: 用戶ID
            
        Returns:
            對話列表
        """
        result = []
        if user_id in self.user_conversations:
            for conv_id in self.user_conversations[user_id]:
                conv = self.conversations.get(conv_id)
                if conv:
                    result.append(conv)
        return result

# 全局儲存實例
memory_storage = MemoryStorage() 