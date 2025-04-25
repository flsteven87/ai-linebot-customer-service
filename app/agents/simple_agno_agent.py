"""
實現基於 Agno 的簡單 Agent。
"""
import asyncio
from app.agents.base_agent import BaseAgent, AgentResponse
import logging
from app.config import settings  # 導入 settings

logger = logging.getLogger(__name__)

class SimpleAgnoAgent(BaseAgent):
    """
    使用 Agno 框架的簡單 Agent 實現。
    """
    
    def __init__(self):
        super().__init__(
            name="Simple Agent",
            description="使用 Agno 框架的簡單 Agent"
        )
        self.agent = None
        
    async def initialize(self):
        """初始化 Agno Agent。"""
        logger.info("初始化 Agno Agent")
        # 使用非同步方式初始化 Agno Agent
        # 這樣可以避免在服務啟動時阻塞
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._init_agno_agent)
        logger.info("Agno Agent 初始化完成")
    
    def _init_agno_agent(self):
        """在另一個執行緒中初始化 Agno Agent。"""
        try:
            from agno.agent import Agent
            from agno.models.openai import OpenAIChat
            
            # 檢查 API Key 是否存在
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY 未設置")
                self.agent = None
                return
            
            logger.debug(f"使用 OpenAI API Key: {settings.OPENAI_API_KEY[:5]}...")
            
            self.agent = Agent(
                model=OpenAIChat(
                    id="gpt-4o-mini",
                    api_key=settings.OPENAI_API_KEY  # 明確傳遞 API Key
                ),
                description="你是一個友善的客服助手，負責回答用戶的問題",
                instructions=[
                    "以禮貌的方式回應用戶",
                    "如果不確定答案，坦白說明",
                    "回答要簡潔明瞭"
                ],
                markdown=True,
                # 添加下列設定以便更好地處理聊天
                num_history_responses=10,  # 保留過去10次回應的歷史
                reasoning_model=None,  # 不使用推理模型，以簡化處理
                show_tool_calls=True,  # 顯示工具調用，有助於調試
            )
            logger.debug("Agno Agent 建立成功")
        except Exception as e:
            logger.error(f"初始化 Agno Agent 時發生錯誤: {e}", exc_info=True)
            self.agent = None
    
    async def process(self, user_id: str, message: str) -> AgentResponse:
        """
        處理用戶訊息，使用 Agno Agent 回覆。
        
        Args:
            user_id: 用戶 ID
            message: 用戶發送的訊息
            
        Returns:
            AgentResponse: 包含回覆內容與信心度
        """
        if not self.agent:
            logger.warning(f"Agent 尚未初始化完成，用戶 {user_id} 的請求無法處理")
            return AgentResponse(
                content="Agent 尚未初始化完成，請稍後再試",
                confidence=0.0
            )
        
        try:
            logger.info(f"處理來自用戶 {user_id} 的訊息: {message}")
            
            # 設置 session_id 為用戶 ID，以保持對話上下文
            # 使用非同步方式調用 Agno Agent
            loop = asyncio.get_event_loop()
            run_response = await loop.run_in_executor(
                None, 
                lambda: self.agent.run(
                    message, 
                    user_id=user_id, 
                    session_id=user_id  # 使用用戶ID作為會話ID
                )
            )
            
            # 從 RunResponse 對象獲取回應文本
            response_content = run_response.content
            
            # 記錄 Agno Agent 回覆內容
            logger.debug(f"Agno Agent 回覆: {response_content}")
            
            return AgentResponse(
                content=response_content,
                confidence=0.9  # 固定信心度，未來可以根據回應內容分析
            )
        except Exception as e:
            logger.error(f"處理訊息時發生錯誤: {e}", exc_info=True)
            return AgentResponse(
                content="抱歉，處理您的請求時發生錯誤，請稍後再試",
                confidence=0.0
            ) 