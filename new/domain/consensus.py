"""
Consensus值对象 - 代表团队达成的共识
"""
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Consensus:
    """共识值对象（不可变）"""
    content: str
    discussion_id: str
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "content": self.content,
            "discussion_id": self.discussion_id
        }
    
    def __str__(self) -> str:
        return self.content
