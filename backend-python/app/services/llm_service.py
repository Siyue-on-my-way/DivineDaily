"""LLM服务层"""

import httpx
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class LLMService(ABC):
    """LLM服务抽象基类"""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """生成文本"""
        pass
    
    async def generate_answer(self, prompt: str) -> str:
        """生成答案（别名）"""
        return await self.generate(prompt)
    
    async def generate_detail(self, prompt: str) -> str:
        """生成详情（别名）"""
        return await self.generate(prompt)
    
    async def close(self):
        """关闭连接"""
        pass


class MockLLMService(LLMService):
    """Mock LLM服务（用于测试和降级）"""
    
    async def generate(self, prompt: str) -> str:
        return "这是一个测试答案。根据分析，建议您谨慎考虑。"


class OpenAICompatibleLLMService(LLMService):
    """OpenAI兼容的LLM服务"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def generate(self, prompt: str) -> str:
        """调用LLM生成文本"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = await self.client.post(
                self.endpoint,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError("Invalid response format")
        
        except Exception as e:
            import traceback
            print(f"LLM调用失败: {type(e).__name__}: {str(e)}")
            print(f"详细错误:\n{traceback.format_exc()}")
            # 降级到Mock服务
            return await MockLLMService().generate(prompt)
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


def create_llm_service(
    llm_config,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: Optional[int] = None
) -> LLMService:
    """
    根据配置创建LLM服务实例
    
    Args:
        llm_config: LLM配置对象
        temperature: 温度参数（可选，覆盖配置）
        max_tokens: 最大token数（可选，覆盖配置）
        timeout: 超时时间（可选，覆盖配置）
    
    Returns:
        LLMService实例
    """
    # 如果没有配置，返回Mock服务
    if not llm_config:
        return MockLLMService()
    
    # 如果配置未启用，返回Mock服务
    if not llm_config.is_enabled:
        return MockLLMService()
    
    # 获取配置参数
    endpoint = llm_config.endpoint
    api_key = llm_config.api_key
    model_name = llm_config.model_name
    
    # 使用传入的参数或配置中的参数
    if temperature is None:
        temperature = llm_config.extra_config.get("temperature", 0.7) if llm_config.extra_config else 0.7
    
    if max_tokens is None:
        max_tokens = llm_config.extra_config.get("max_tokens", 2000) if llm_config.extra_config else 2000
    
    if timeout is None:
        timeout = llm_config.extra_config.get("timeout", 30) if llm_config.extra_config else 30
    
    # 根据provider创建对应的服务
    provider = llm_config.provider.lower()
    
    if provider in ["openai", "deepseek", "doubao"] or llm_config.url_type == "openai_compatible":
        return OpenAICompatibleLLMService(
            endpoint=endpoint,
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
    else:
        # 未知provider，返回Mock服务
        print(f"未知的LLM provider: {provider}，使用Mock服务")
        return MockLLMService()


def get_llm_service() -> LLMService:
    """获取默认LLM服务实例（Mock）"""
    return MockLLMService()
