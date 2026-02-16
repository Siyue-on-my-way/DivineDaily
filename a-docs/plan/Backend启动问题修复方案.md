# Backend启动问题修复方案

**问题**: Backend容器启动失败  
**错误**: `ImportError: cannot import name 'create_llm_service' from 'app.services.llm_service'`

---

## 🔍 问题分析

### 错误堆栈
```python
File "/app/app/services/enhanced_divination_service.py", line 9, in <module>
    from app.services.llm_service import LLMService, create_llm_service
ImportError: cannot import name 'create_llm_service' from 'app.services.llm_service'
```

### 根本原因
`enhanced_divination_service.py` 导入了 `create_llm_service` 函数，但 `llm_service.py` 中只定义了：
- `LLMService` (抽象基类)
- `MockLLMService` (Mock实现)
- `get_llm_service()` (返回Mock实例)

**缺少**: `create_llm_service()` 函数

---

## 🔧 修复方案

### 方案1: 添加 create_llm_service 函数（推荐）

在 `llm_service.py` 中添加完整的LLM服务创建函数：

```python
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
            print(f"LLM调用失败: {e}")
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
```

---

### 方案2: 修改 enhanced_divination_service.py（不推荐）

如果不想修改 `llm_service.py`，可以修改导入语句：

```python
# 修改前
from app.services.llm_service import LLMService, create_llm_service

# 修改后
from app.services.llm_service import LLMService, get_llm_service
```

**缺点**: 这样会失去根据配置创建不同LLM服务的能力。

---

## 🚀 执行步骤

### 步骤1: 备份原文件
```bash
cd /mnt/DivineDaily/backend-python/app/services
cp llm_service.py llm_service.py.backup
```

### 步骤2: 更新 llm_service.py
使用上面方案1的完整代码替换 `llm_service.py` 的内容。

### 步骤3: 重启Backend容器
```bash
cd /mnt/DivineDaily/docker
docker-compose restart backend-python
```

### 步骤4: 验证服务启动
```bash
# 等待10秒让服务启动
sleep 10

# 检查健康状态
curl http://localhost:48080/health

# 查看日志
docker-compose logs --tail=50 backend-python
```

### 步骤5: 运行测试
```bash
cd /mnt/DivineDaily/backend-python/tests
python run_all_tests.py
```

---

## ✅ 验证清单

- [ ] `llm_service.py` 已更新
- [ ] Backend容器重启成功
- [ ] 健康检查返回正常
- [ ] 日志中无错误信息
- [ ] 测试可以正常运行

---

## 📝 预期结果

### 成功标志
```bash
# 健康检查
$ curl http://localhost:48080/health
{
  "status": "healthy",
  "service": "DivineDaily Backend",
  "version": "1.0.0"
}

# 容器状态
$ docker ps | grep backend-python
divine-daily-backend-python   Up 2 minutes   0.0.0.0:48080->8080/tcp
```

### 测试输出
```
================================================================================
  DivineDaily 完整测试套件
  测试时间: 2026-02-16 19:30:00
================================================================================

...

总计: 35/35 通过 (100%)

🎉 所有测试套件通过！
```

---

## 🔍 故障排查

### 如果容器仍然失败

1. **查看详细日志**
```bash
docker-compose logs backend-python | tail -100
```

2. **检查Python语法**
```bash
cd /mnt/DivineDaily/backend-python
python -m py_compile app/services/llm_service.py
```

3. **进入容器调试**
```bash
docker exec -it divine-daily-backend-python bash
cd /app
python -c "from app.services.llm_service import create_llm_service; print('OK')"
```

---

**创建时间**: 2026-02-16  
**优先级**: 🔴 最高  
**状态**: 待执行

