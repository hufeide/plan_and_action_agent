"""
Discussion聚合根 - 代表一次团队讨论
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class DiscussionStatus(Enum):
    """讨论状态"""
    IN_PROGRESS = "in_progress"
    CONSENSUS_REACHED = "consensus_reached"
    FAILED = "failed"


@dataclass
class Message:
    """讨论消息"""
    agent_id: str
    agent_name: str
    content: str
    round: int
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "content": self.content,
            "round": self.round,
            "timestamp": self.timestamp
        }


@dataclass
class Discussion:
    """讨论聚合根"""
    id: str
    topic: str
    messages: List[Message] = field(default_factory=list)
    current_round: int = 0
    max_rounds: int = 5
    status: DiscussionStatus = DiscussionStatus.IN_PROGRESS
    consensus: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ended_at: Optional[str] = None
    
    def add_message(self, agent_id: str, agent_name: str, content: str):
        """添加消息"""
        message = Message(
            agent_id=agent_id,
            agent_name=agent_name,
            content=content,
            round=self.current_round
        )
        self.messages.append(message)
    
    def start_new_round(self):
        """开始新一轮讨论"""
        self.current_round += 1
    
    def reach_consensus(self, consensus: str):
        """达成共识"""
        self.status = DiscussionStatus.CONSENSUS_REACHED
        self.consensus = consensus
        self.ended_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def fail(self):
        """讨论失败"""
        self.status = DiscussionStatus.FAILED
        self.ended_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def is_finished(self) -> bool:
        """是否已结束"""
        return self.status != DiscussionStatus.IN_PROGRESS
    
    def has_reached_max_rounds(self) -> bool:
        """是否达到最大轮数"""
        return self.current_round >= self.max_rounds
    
    def get_recent_messages(self, count: int = 3) -> List[Message]:
        """获取最近的消息"""
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "topic": self.topic,
            "messages": [msg.to_dict() for msg in self.messages],
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "status": self.status.value,
            "consensus": self.consensus,
            "started_at": self.started_at,
            "ended_at": self.ended_at
        }
