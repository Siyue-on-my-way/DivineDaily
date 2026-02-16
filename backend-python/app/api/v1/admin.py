"""配置管理路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json
import httpx
from pathlib import Path
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.llm_config import LLMConfig
from app.models.prompt_config import PromptConfig

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员权限"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


# ==================== Pydantic 模型 ====================

class LLMConfigCreate(BaseModel):
    name: str
    provider: str
    url_type: Optional[str] = "openai_compatible"
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model_name: str
    is_default: Optional[bool] = False
    is_enabled: Optional[bool] = True
    description: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None


class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    url_type: Optional[str] = None
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model_name: Optional[str] = None
    is_default: Optional[bool] = None
    is_enabled: Optional[bool] = None
    description: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None


class LLMTestRequest(BaseModel):
    message: str = "你好，请介绍一下你自己"
    mode: str = "block"


class AssistantConfigCreate(BaseModel):
    name: str
    scene: str
    prompt_type: str
    question_type: str
    template: str
    llm_config_id: int
    variables: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    timeout_seconds: Optional[int] = 30
    is_enabled: Optional[bool] = True
    description: Optional[str] = None


class AssistantConfigUpdate(BaseModel):
    name: Optional[str] = None
    scene: Optional[str] = None
    prompt_type: Optional[str] = None
    question_type: Optional[str] = None
    template: Optional[str] = None
    llm_config_id: Optional[int] = None
    variables: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout_seconds: Optional[int] = None
    is_enabled: Optional[bool] = None
    description: Optional[str] = None


# ==================== LLM 配置 ====================

@router.get("/llm", tags=["LLM配置"])
async def get_llm_configs(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取所有 LLM 配置"""
    result = await db.execute(select(LLMConfig))
    configs = result.scalars().all()
    
    return {
        "data": [
            {
                "id": config.id,
                "name": config.name,
                "provider": config.provider,
                "url_type": config.url_type,
                "model": config.model_name,
                "api_key": config.api_key[:10] + "***" if config.api_key else None,
                "endpoint": config.endpoint,
                "is_default": config.is_default,
                "is_enabled": config.is_enabled,
                "description": config.description,
                "temperature": config.extra_config.get("temperature") if config.extra_config else None,
                "max_tokens": config.extra_config.get("max_tokens") if config.extra_config else None,
                "timeout": config.extra_config.get("timeout") if config.extra_config else None,
                "created_at": config.created_at.isoformat() if config.created_at else None,
                "updated_at": config.updated_at.isoformat() if config.updated_at else None,
            }
            for config in configs
        ]
    }


@router.post("/llm", tags=["LLM配置"])
async def create_llm_config(
    config_data: LLMConfigCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建 LLM 配置"""
    result = await db.execute(select(LLMConfig).where(LLMConfig.name == config_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="配置名称已存在")
    
    if config_data.is_default:
        await db.execute(update(LLMConfig).values(is_default=False))
    
    extra_config = {}
    if config_data.temperature is not None:
        extra_config["temperature"] = config_data.temperature
    if config_data.max_tokens is not None:
        extra_config["max_tokens"] = config_data.max_tokens
    if config_data.timeout is not None:
        extra_config["timeout"] = config_data.timeout
    
    config_dict = config_data.dict(exclude={"temperature", "max_tokens", "timeout"})
    config_dict["extra_config"] = extra_config
    
    new_config = LLMConfig(**config_dict)
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)
    
    return {"message": "创建成功", "data": {"id": new_config.id, "name": new_config.name}}


@router.put("/llm/{config_id}", tags=["LLM配置"])
async def update_llm_config(
    config_id: int,
    config_data: LLMConfigUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新 LLM 配置"""
    result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    if config_data.is_default:
        await db.execute(update(LLMConfig).where(LLMConfig.id != config_id).values(is_default=False))
    
    update_data = config_data.dict(exclude_unset=True, exclude={"temperature", "max_tokens", "timeout"})
    for key, value in update_data.items():
        setattr(config, key, value)
    
    extra_config = dict(config.extra_config) if config.extra_config else {}
    if config_data.temperature is not None:
        extra_config["temperature"] = config_data.temperature
    if config_data.max_tokens is not None:
        extra_config["max_tokens"] = config_data.max_tokens
    if config_data.timeout is not None:
        extra_config["timeout"] = config_data.timeout
    
    config.extra_config = extra_config
    flag_modified(config, "extra_config")
    
    await db.commit()
    await db.refresh(config)
    
    return {"message": "更新成功", "data": {"id": config.id, "name": config.name}}


@router.delete("/llm/{config_id}", tags=["LLM配置"])
async def delete_llm_config(
    config_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除 LLM 配置"""
    result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    if config.is_default:
        raise HTTPException(status_code=400, detail="不能删除默认配置")
    
    prompt_result = await db.execute(select(PromptConfig).where(PromptConfig.llm_config_id == config_id))
    prompt_configs = prompt_result.scalars().all()
    if prompt_configs:
        raise HTTPException(
            status_code=400, 
            detail=f"该配置正在被 {len(prompt_configs)} 个 Assistant 配置使用，无法删除。"
        )
    
    try:
        await db.delete(config)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    
    return {"message": "删除成功"}


@router.post("/llm/{config_id}/set-default", tags=["LLM配置"])
async def set_default_llm_config(
    config_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """设置默认 LLM 配置"""
    result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await db.execute(update(LLMConfig).values(is_default=False))
    config.is_default = True
    await db.commit()
    
    return {"message": "设置成功"}


@router.post("/llm/{config_id}/test", tags=["LLM配置"])
async def test_llm_config(
    config_id: int,
    test_data: LLMTestRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """测试 LLM 配置 - 真实调用"""
    result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    
    request_body = {
        "model": config.model_name,
        "messages": [{"role": "user", "content": test_data.message}],
        "temperature": config.extra_config.get("temperature", 0.7) if config.extra_config else 0.7,
        "max_tokens": config.extra_config.get("max_tokens", 1000) if config.extra_config else 1000,
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(config.endpoint, headers=headers, json=request_body)
            response.raise_for_status()
            result_data = response.json()
            if "choices" in result_data and len(result_data["choices"]) > 0:
                llm_response = result_data["choices"][0]["message"]["content"]
            else:
                llm_response = str(result_data)
        
        return {
            "success": True,
            "message": "测试成功",
            "request": {"user_message": test_data.message, "model": config.model_name, "endpoint": config.endpoint},
            "response": llm_response
        }
    except httpx.HTTPError as e:
        return {
            "success": False,
            "message": "测试失败",
            "error": str(e),
            "request": {"user_message": test_data.message, "model": config.model_name, "endpoint": config.endpoint}
        }


# ==================== Assistant 配置 ====================

@router.get("/assistant", tags=["Assistant配置"])
@router.get("/prompt", tags=["Assistant配置"])
async def get_assistant_configs(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取所有 Assistant 配置"""
    result = await db.execute(
        select(PromptConfig, LLMConfig)
        .outerjoin(LLMConfig, PromptConfig.llm_config_id == LLMConfig.id)
    )
    rows = result.all()
    
    return {
        "data": [
            {
                "id": config.id,
                "name": config.name,
                "scene": config.scene,
                "template": config.template,
                "llm_config_id": config.llm_config_id,
                "llm_config_name": llm_config.name if llm_config else None,
                "is_default": config.is_default,
                "is_enabled": config.is_enabled,
                "description": config.description,
                "prompt_type": config.prompt_type,
                "question_type": config.question_type,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "timeout_seconds": config.timeout_seconds,
                "variables": config.variables,
                "created_at": config.created_at.isoformat() if config.created_at else None,
                "updated_at": config.updated_at.isoformat() if config.updated_at else None,
            }
            for config, llm_config in rows
        ]
    }


@router.post("/assistant", tags=["Assistant配置"])
async def create_assistant_config(
    config_data: AssistantConfigCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建 Assistant 配置"""
    result = await db.execute(select(PromptConfig).where(PromptConfig.name == config_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="配置名称已存在")
    
    new_config = PromptConfig(**config_data.dict())
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)
    
    return {"message": "创建成功", "data": {"id": new_config.id, "name": new_config.name}}


@router.put("/assistant/{config_id}", tags=["Assistant配置"])
@router.put("/prompt/{config_id}", tags=["Assistant配置"])
async def update_assistant_config(
    config_id: int,
    config_data: AssistantConfigUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新 Assistant 配置"""
    result = await db.execute(select(PromptConfig).where(PromptConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    update_data = config_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    await db.commit()
    await db.refresh(config)
    
    return {"message": "更新成功", "data": {"id": config.id, "name": config.name}}


@router.delete("/assistant/{config_id}", tags=["Assistant配置"])
async def delete_assistant_config(
    config_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除 Assistant 配置"""
    result = await db.execute(select(PromptConfig).where(PromptConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await db.delete(config)
    await db.commit()
    
    return {"message": "删除成功"}


@router.post("/assistant/{config_id}/set-default", tags=["Assistant配置"])
async def set_default_assistant_config(
    config_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """设置默认 Assistant 配置"""
    result = await db.execute(select(PromptConfig).where(PromptConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await db.execute(update(PromptConfig).values(is_default=False))
    config.is_default = True
    await db.commit()
    
    return {"message": "设置成功"}


# ==================== Assistant 测试功能 ====================

def load_test_cases() -> Dict[str, Any]:
    """加载测试用例"""
    test_case_path = Path(__file__).parent.parent.parent / "extra_file" / "test_case.json"
    
    if not test_case_path.exists():
        return {}
    
    try:
        with open(test_case_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载测试用例失败: {e}")
        return {}


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """渲染模板"""
    result = template
    for key, value in variables.items():
        placeholder1 = f"{{{{.{key}}}}}"
        placeholder2 = f"{{{{{key}}}}}"
        result = result.replace(placeholder1, str(value))
        result = result.replace(placeholder2, str(value))
    return result


@router.get("/assistant/test-cases", tags=["Assistant配置"])
async def get_test_cases(
    admin: User = Depends(require_admin)
):
    """获取所有测试用例"""
    test_cases = load_test_cases()
    return {
        "data": test_cases,
        "count": len(test_cases)
    }


@router.post("/assistant/{config_id}/test", tags=["Assistant配置"])
async def test_assistant_config(
    config_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """测试 Assistant 配置"""
    result = await db.execute(
        select(PromptConfig, LLMConfig)
        .outerjoin(LLMConfig, PromptConfig.llm_config_id == LLMConfig.id)
        .where(PromptConfig.id == config_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Assistant 配置不存在")
    
    assistant_config, llm_config = row
    
    if not llm_config:
        raise HTTPException(status_code=400, detail="该 Assistant 未关联 LLM 配置")
    
    test_cases = load_test_cases()
    test_case = test_cases.get(assistant_config.name)
    
    if not test_case:
        raise HTTPException(
            status_code=404, 
            detail=f"未找到名为 '{assistant_config.name}' 的测试用例，请在 test_case.json 中添加"
        )
    
    if test_case.get("scene") != assistant_config.scene:
        raise HTTPException(
            status_code=400,
            detail=f"测试用例场景 ({test_case.get('scene')}) 与配置场景 ({assistant_config.scene}) 不匹配"
        )
    
    test_input = test_case.get("test_input", {})
    try:
        rendered_prompt = render_template(assistant_config.template, test_input)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"渲染模板失败: {str(e)}"
        )
    
    try:
        headers = {"Content-Type": "application/json"}
        
        if llm_config.api_key:
            if llm_config.provider.lower() == "openai" or llm_config.url_type == "openai_compatible":
                headers["Authorization"] = f"Bearer {llm_config.api_key}"
        
        request_body = {
            "model": llm_config.model_name,
            "messages": [{"role": "user", "content": rendered_prompt}],
            "temperature": assistant_config.temperature,
            "max_tokens": assistant_config.max_tokens,
        }
        
        async with httpx.AsyncClient(timeout=assistant_config.timeout_seconds) as client:
            llm_response = await client.post(llm_config.endpoint, headers=headers, json=request_body)
            llm_response.raise_for_status()
            
            result_data = llm_response.json()
            if "choices" in result_data and len(result_data["choices"]) > 0:
                response = result_data["choices"][0]["message"]["content"]
            else:
                response = str(result_data)
        
        expected_keywords = test_case.get("expected_keywords", [])
        found_keywords = [kw for kw in expected_keywords if kw in response]
        missing_keywords = [kw for kw in expected_keywords if kw not in response]
        
        return {
            "success": True,
            "test_case": {
                "name": assistant_config.name,
                "scene": test_case.get("scene"),
                "prompt_type": test_case.get("prompt_type"),
                "question_type": test_case.get("question_type"),
                "test_input": test_input
            },
            "rendered_prompt": rendered_prompt,
            "llm_response": response,
            "validation": {
                "expected_keywords": expected_keywords,
                "found_keywords": found_keywords,
                "missing_keywords": missing_keywords,
                "keyword_match_rate": f"{len(found_keywords)}/{len(expected_keywords)}" if expected_keywords else "N/A"
            },
            "config_info": {
                "assistant_name": assistant_config.name,
                "llm_name": llm_config.name,
                "model": llm_config.model_name,
                "temperature": assistant_config.temperature,
                "max_tokens": assistant_config.max_tokens
            }
        }
        
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP 请求失败: {str(e)}",
            "test_case": {
                "name": assistant_config.name,
                "test_input": test_input
            },
            "rendered_prompt": rendered_prompt
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_case": {
                "name": assistant_config.name,
                "test_input": test_input
            },
            "rendered_prompt": rendered_prompt
        }
