"""
Team聚合根 - 代表一个AI团队
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .agent import Agent


@dataclass
class Team:
    """团队聚合根"""
    id: str
    name: str
    agents: Dict[str, Agent] = field(default_factory=dict)  # 使用字典，O(1)查找
    
    def add_agent(self, agent: Agent):
        """添加成员"""
        self.agents[agent.id] = agent
    
    def remove_agent(self, agent_id: str):
        """移除成员"""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取成员"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """获取所有成员"""
        return list(self.agents.values())
    
    def get_available_agents(self) -> List[Agent]:
        """获取可用成员"""
        return [agent for agent in self.agents.values() if agent.is_available()]
    
    def get_agent_count(self) -> int:
        """获取成员数量"""
        return len(self.agents)
    
    def start_discussion(self):
        """开始讨论"""
        for agent in self.agents.values():
            agent.start_discussion()
    
    def finish_discussion(self):
        """结束讨论"""
        for agent in self.agents.values():
            agent.finish_work()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "agents": [agent.to_dict() for agent in self.agents.values()],
            "agent_count": self.get_agent_count()
        }
