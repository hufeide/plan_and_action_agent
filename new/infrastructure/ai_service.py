"""
AI服务 - 统一的AI调用接口
"""
import requests
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class AIConfig:
    """AI配置"""
    base_url: str
    model: str
    api_key: str
    max_tokens: int = 2000
    temperature: float = 0.7


class AIService:
    """AI服务"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.total_tokens = 0
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> Dict:
        """
        生成AI响应
        
        Returns:
            {
                "text": str,
                "tokens": int,
                "success": bool,
                "error": Optional[str]
            }
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            response = requests.post(
                f"{self.config.base_url}/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["choices"][0]["text"].strip()
                tokens = result.get("usage", {}).get("total_tokens", 0)
                
                self.total_tokens += tokens
                
                return {
                    "text": text,
                    "tokens": tokens,
                    "success": True,
                    "error": None
                }
            else:
                return {
                    "text": "",
                    "tokens": 0,
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {
                "text": "",
                "tokens": 0,
                "success": False,
                "error": str(e)
            }
    
    def get_total_tokens(self) -> int:
        """获取总token消耗"""
        return self.total_tokens
