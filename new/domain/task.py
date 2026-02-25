"""
Task实体 - 代表一个具体任务
"""
from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Task:
    """任务实体"""
    id: str
    description: str
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    result: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    completed_at: Optional[str] = None
    
    def assign_to(self, agent_id: str, agent_name: str):
        """分配给Agent"""
        self.assignee_id = agent_id
        self.assignee_name = agent_name
        self.status = TaskStatus.IN_PROGRESS
    
    def update_progress(self, progress: int):
        """更新进度"""
        self.progress = min(100, max(0, progress))
        if self.progress >= 100:
            self.complete()
    
    def complete(self):
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == TaskStatus.COMPLETED
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "description": self.description,
            "assignee_id": self.assignee_id,
            "assignee_name": self.assignee_name,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }
