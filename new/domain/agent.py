"""
Agent实体 - 代表团队中的一个智能体成员
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


class AgentStatus(Enum):
    """Agent状态"""
    IDLE = "idle"           # 空闲
    DISCUSSING = "discussing"  # 讨论中
    WORKING = "working"     # 工作中


@dataclass
class Agent:
    """Agent实体"""
    id: str
    name: str
    role: str
    skills: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    
    def start_discussion(self):
        """开始讨论"""
        self.status = AgentStatus.DISCUSSING
    
    def start_working(self, task: str):
        """开始工作"""
        self.status = AgentStatus.WORKING
        self.current_task = task
    
    def finish_work(self):
        """完成工作"""
        self.status = AgentStatus.IDLE
        self.current_task = None
    
    def is_available(self) -> bool:
        """是否可用"""
        return self.status == AgentStatus.IDLE
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "skills": self.skills,
            "status": self.status.value,
            "current_task": self.current_task
        }
