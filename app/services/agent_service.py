"""
Agent 服務，管理各種 Agent 並路由用戶訊息。
"""
import logging
from typing import Dict, Type, List
from app.agents.base_agent import BaseAgent, AgentResponse
from app.agents.echo_agent import EchoAgent
from app.agents.simple_agno_agent import SimpleAgnoAgent

logger = logging.getLogger(__name__)

class AgentService:
    """
    管理各種 Agent 的服務類，負責將用戶訊息路由到適當的 Agent 處理。
    """
    
    def __init__(self):
        """初始化 Agent 服務。"""
        self.agents: Dict[str, BaseAgent] = {}
        self._register_default_agents()
    
    async def initialize(self):
        """初始化所有 Agent。"""
        for agent_id, agent in self.agents.items():
            logger.info(f"初始化 Agent: {agent_id}")
            await agent.initialize()
    
    def _register_default_agents(self):
        """註冊預設的 Agent。"""
        # 註冊一個簡單的 Echo Agent 用於測試
        self.register_agent("echo", EchoAgent())
        
        # 註冊 Agno Agent
        self.register_agent("agno", SimpleAgnoAgent())
    
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """
        註冊 Agent。
        
        Args:
            agent_id: Agent ID
            agent: Agent 實例
        """
        self.agents[agent_id] = agent
        logger.info(f"已註冊 Agent: {agent_id} ({agent.name})")
    
    async def process_message(self, user_id: str, message: str) -> str:
        """
        處理用戶訊息，並決定使用哪個 Agent 回應。
        
        Args:
            user_id: 用戶 ID
            message: 用戶發送的訊息
            
        Returns:
            str: Agent 的回覆
        """
        logger.debug(f"處理來自用戶 {user_id} 的訊息: {message}")
        
        # 簡單的命令解析，用於測試和開發
        if message.startswith("/agent "):
            # 格式: /agent {agent_id} {實際訊息}
            parts = message[7:].split(" ", 1)
            if len(parts) == 2:
                agent_id, actual_message = parts
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    response = await agent.process(user_id, actual_message)
                    return response.content
                else:
                    return f"找不到 Agent: {agent_id}"
            else:
                return "命令格式不正確。請使用 /agent {agent_id} {訊息}"
        
        # 預設使用 agno agent
        default_agent_id = "agno"
        
        if default_agent_id in self.agents:
            try:
                agent = self.agents[default_agent_id]
                response = await agent.process(user_id, message)
                return response.content
            except Exception as e:
                logger.error(f"Agent 處理訊息時發生錯誤: {e}", exc_info=True)
                return "抱歉，處理您的訊息時發生錯誤。"
        else:
            # 如果 agno agent 不可用，嘗試使用 echo agent
            if "echo" in self.agents:
                try:
                    agent = self.agents["echo"]
                    response = await agent.process(user_id, message)
                    return response.content
                except Exception as e:
                    logger.error(f"Echo Agent 處理訊息時發生錯誤: {e}", exc_info=True)
                    return "抱歉，處理您的訊息時發生錯誤。"
            else:
                return "抱歉，目前沒有可用的 Agent。"
    
    async def get_available_agents(self) -> List[Dict]:
        """
        獲取所有可用的 Agent 資訊。
        
        Returns:
            List[Dict]: Agent 資訊列表
        """
        result = []
        for agent_id, agent in self.agents.items():
            metadata = await agent.get_metadata()
            result.append({
                "id": agent_id,
                **metadata
            })
        return result 