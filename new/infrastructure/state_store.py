"""
状态存储 - 统一的状态管理
"""
from typing import Dict, Optional, List
from domain.team import Team
from domain.discussion import Discussion
from domain.plan import Plan


class StateStore:
    """状态存储（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._teams: Dict[str, Team] = {}
        self._discussions: Dict[str, Discussion] = {}
        self._plans: Dict[str, Plan] = {}
        self._current_team_id: Optional[str] = None
        self._current_discussion_id: Optional[str] = None
        self._current_plan_id: Optional[str] = None
        self._initialized = True
    
    # Team相关
    def save_team(self, team: Team):
        """保存团队"""
        self._teams[team.id] = team
        if self._current_team_id is None:
            self._current_team_id = team.id
    
    def get_team(self, team_id: str) -> Optional[Team]:
        """获取团队"""
        return self._teams.get(team_id)
    
    def get_current_team(self) -> Optional[Team]:
        """获取当前团队"""
        if self._current_team_id:
            return self._teams.get(self._current_team_id)
        return None
    
    def set_current_team(self, team_id: str):
        """设置当前团队"""
        if team_id in self._teams:
            self._current_team_id = team_id
    
    # Discussion相关
    def save_discussion(self, discussion: Discussion):
        """保存讨论"""
        self._discussions[discussion.id] = discussion
        self._current_discussion_id = discussion.id
    
    def get_discussion(self, discussion_id: str) -> Optional[Discussion]:
        """获取讨论"""
        return self._discussions.get(discussion_id)
    
    def get_current_discussion(self) -> Optional[Discussion]:
        """获取当前讨论"""
        if self._current_discussion_id:
            return self._discussions.get(self._current_discussion_id)
        return None
    
    def get_all_discussions(self) -> List[Discussion]:
        """获取所有讨论"""
        return list(self._discussions.values())
    
    def clear_current_discussion(self):
        """清除当前讨论"""
        self._current_discussion_id = None
    
    # Plan相关
    def save_plan(self, plan: Plan):
        """保存计划"""
        self._plans[plan.id] = plan
        self._current_plan_id = plan.id
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """获取计划"""
        return self._plans.get(plan_id)
    
    def get_current_plan(self) -> Optional[Plan]:
        """获取当前计划"""
        if self._current_plan_id:
            return self._plans.get(self._current_plan_id)
        return None
    
    def get_all_plans(self) -> List[Plan]:
        """获取所有计划"""
        return list(self._plans.values())
    
    # 清理方法
    def clear_all(self):
        """清空所有数据"""
        self._teams.clear()
        self._discussions.clear()
        self._plans.clear()
        self._current_team_id = None
        self._current_discussion_id = None
        self._current_plan_id = None
