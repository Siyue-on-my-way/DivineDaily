"""LLM服务层"""

import httpx
import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from app.core.logger import get_logger
logger = get_logger("llm")
OPENAI_COMPATIBLE_MAX_TOKENS_LIMIT = 65535


def _mask_api_key(api_key: Optional[str]) -> str:
    if not api_key:
        return "<empty>"
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}***{api_key[-4:]}"


def _truncate_text(text: Optional[str], max_len: int = 800) -> str:
    if text is None:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "...<truncated>"


def _normalize_max_tokens(raw_max_tokens: Any) -> int:
    """归一化 max_tokens，避免超限导致下游 400。"""
    try:
        value = int(raw_max_tokens)
    except (TypeError, ValueError):
        return 2000

    if value < 1:
        return 2000

    return min(value, OPENAI_COMPATIBLE_MAX_TOKENS_LIMIT)



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


def build_chat_completions_url(endpoint: str, url_type: Optional[str] = "openai_compatible") -> str:
    """根据 URL 类型构建最终 chat completions 请求地址"""
    normalized = endpoint.strip().rstrip('/')

    # openai 兼容模式：自动补全 /chat/completions
    if url_type == "openai_compatible":
        if normalized.endswith("/chat/completions"):
            return normalized
        return f"{normalized}/chat/completions"

    # 自定义模式：使用完整 URL
    return normalized


class OpenAICompatibleLLMService(LLMService):
    """OpenAI兼容的LLM服务"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str],
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
        # 分离 connect/read 超时，读超时留更大余量，降低误判超时
        self.http_timeout = httpx.Timeout(connect=10.0, read=float(timeout), write=10.0, pool=10.0)
        self.client = httpx.AsyncClient(timeout=self.http_timeout)

    async def _post_chat(self, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.post(
            self.endpoint,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def generate(self, prompt: str) -> str:
        """调用LLM生成文本"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        request_id = f"llm_generate_{int(time.time() * 1000)}"
        start_time = time.monotonic()
        logger.info(
            "LLM请求开始 | id=%s | endpoint=%s | model=%s | temp=%s | max_tokens=%s | key=%s | prompt_preview=%s",
            request_id,
            self.endpoint,
            self.model_name,
            self.temperature,
            self.max_tokens,
            _mask_api_key(self.api_key),
            _truncate_text(prompt, 300),
        )

        max_attempts = 2
        last_error: Optional[Exception] = None
        for attempt in range(1, max_attempts + 1):
            try:
                data = await self._post_chat(headers, payload)
                duration_ms = int((time.monotonic() - start_time) * 1000)
                logger.info(
                    "LLM响应完成 | id=%s | attempt=%s/%s | duration_ms=%s",
                    request_id,
                    attempt,
                    max_attempts,
                    duration_ms,
                )
                logger.info(
                    "LLM响应内容 | id=%s | attempt=%s/%s | body_preview=%s",
                    request_id,
                    attempt,
                    max_attempts,
                    _truncate_text(json.dumps(data, ensure_ascii=False), 1000),
                )

                if "choices" in data and len(data["choices"]) > 0:
                    choice0 = data["choices"][0]
                    finish_reason = choice0.get("finish_reason") if isinstance(choice0, dict) else None
                    content = choice0.get("message", {}).get("content", "") if isinstance(choice0, dict) else ""
                    if finish_reason == "length":
                        logger.warning(
                            "LLM输出被长度截断，尝试续写 | id=%s | model=%s | finish_reason=%s | max_tokens=%s",
                            request_id,
                            self.model_name,
                            finish_reason,
                            self.max_tokens,
                        )
                        continuation_payload = {
                            "model": self.model_name,
                            "messages": [
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": content},
                                {
                                    "role": "user",
                                    "content": "请从上文末尾继续输出，不要重复已有内容，保持同一格式并尽量完整结束。"
                                },
                            ],
                            "temperature": self.temperature,
                            "max_tokens": self.max_tokens
                        }
                        continuation_data = await self._post_chat(headers, continuation_payload)
                        continuation_choice = continuation_data.get("choices", [{}])[0]
                        continuation_text = continuation_choice.get("message", {}).get("content", "")
                        if continuation_text:
                            content = f"{content}\n{continuation_text}".strip()

                    usage = data.get("usage") if isinstance(data, dict) else None
                    if isinstance(usage, dict):
                        logger.info(
                            "LLM token使用量 | id=%s | model=%s | prompt_tokens=%s | completion_tokens=%s | total_tokens=%s",
                            request_id,
                            self.model_name,
                            usage.get("prompt_tokens"),
                            usage.get("completion_tokens"),
                            usage.get("total_tokens"),
                        )

                    return content
                raise ValueError("Invalid response format")

            except httpx.ReadTimeout as e:
                last_error = e
                duration_ms = int((time.monotonic() - start_time) * 1000)
                logger.info(
                    "LLM读取超时 | id=%s | attempt=%s/%s | duration_ms=%s | timeout=%ss | error=%s",
                    request_id,
                    attempt,
                    max_attempts,
                    duration_ms,
                    self.timeout,
                    str(e),
                )
                if attempt == max_attempts:
                    break
            except Exception as e:
                import traceback
                last_error = e
                duration_ms = int((time.monotonic() - start_time) * 1000)
                logger.info(
                    "LLM调用失败 | id=%s | attempt=%s/%s | duration_ms=%s | error=%s: %s",
                    request_id,
                    attempt,
                    max_attempts,
                    duration_ms,
                    type(e).__name__,
                    str(e),
                )
                logger.info(f"详细错误:\n{traceback.format_exc()}")
                # 非超时错误不重试，直接抛出
                break

        # 不再降级返回固定文案，直接抛错给上层处理
        if last_error:
            raise last_error
        raise RuntimeError("LLM调用失败，未获取到有效响应")
    
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
    # 如果没有配置，直接抛错，避免静默降级
    if not llm_config:
        raise ValueError("LLM配置不存在")
    
    # 如果配置未启用，直接抛错，避免静默降级
    if not llm_config.is_enabled:
        raise ValueError("LLM配置未启用")
    
    # 获取配置参数
    raw_endpoint = llm_config.endpoint
    if not raw_endpoint:
        raise ValueError("LLM endpoint 未配置")

    endpoint = build_chat_completions_url(raw_endpoint, llm_config.url_type)
    api_key = llm_config.api_key
    model_name = llm_config.model_name
    
    # 使用传入的参数或配置中的参数
    if temperature is None:
        temperature = llm_config.extra_config.get("temperature", 0.7) if llm_config.extra_config else 0.7
    
    if max_tokens is None:
        max_tokens = llm_config.extra_config.get("max_tokens", 2000) if llm_config.extra_config else 2000
    normalized_max_tokens = _normalize_max_tokens(max_tokens)
    if normalized_max_tokens != max_tokens:
        logger.warning(
            "LLM max_tokens 超出范围，已自动钳制 | model=%s | original=%s | normalized=%s",
            model_name,
            max_tokens,
            normalized_max_tokens,
        )
    max_tokens = normalized_max_tokens
    
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
        raise ValueError(f"未知的LLM provider: {provider}")


def get_llm_service() -> LLMService:
    """保留接口兼容：默认不再提供降级服务"""
    raise ValueError("默认LLM服务不可用，请先配置可用的LLM")
