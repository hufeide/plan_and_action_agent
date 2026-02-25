"""
Plan聚合根 - 代表基于共识制定的执行计划
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from .task import Task
from .consensus import Consensus


@dataclass
class Plan:
    """计划聚合根"""
    id: str
    goal: str
    consensus: Consensus
    tasks: List[Task] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    completed_at: Optional[str] = None
    
    def add_task(self, task: Task):
        """添加任务"""
        self.tasks.append(task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_pending_tasks(self) -> List[Task]:
        """获取待处理任务"""
        return [task for task in self.tasks if not task.is_completed()]
    
    def get_progress(self) -> float:
        """获取整体进度"""
        if not self.tasks:
            return 0.0
        total_progress = sum(task.progress for task in self.tasks)
        return total_progress / len(self.tasks)
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return all(task.is_completed() for task in self.tasks) if self.tasks else False
    
    def complete(self):
        """完成计划"""
        self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "goal": self.goal,
            "consensus": self.consensus.to_dict(),
            "tasks": [task.to_dict() for task in self.tasks],
            "progress": self.get_progress(),
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "is_completed": self.is_completed()
        }
