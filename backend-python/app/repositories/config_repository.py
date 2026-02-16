"""配置仓库"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prompt_config import PromptConfig
from app.models.llm_config import LLMConfig


class PromptConfigRepository:
    """Prompt配置数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, config_id: int) -> Optional[PromptConfig]:
        """根据ID获取Prompt配置"""
        result = await self.db.execute(
            select(PromptConfig).where(PromptConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        # 如果有关联的LLM，查询LLM配置
        if config and config.llm_config_id:
            llm_result = await self.db.execute(
                select(LLMConfig).where(LLMConfig.id == config.llm_config_id)
            )
            config.llm_config = llm_result.scalar_one_or_none()
        
        return config
    
    async def get_by_scene_and_type(self, scene: str, prompt_type: str, question_type: str = '') -> Optional[PromptConfig]:
        """根据场景和类型获取Prompt配置"""
        query = select(PromptConfig).where(
            PromptConfig.scene == scene,
            PromptConfig.prompt_type == prompt_type,
            PromptConfig.is_enabled == True
        )
        
        if question_type:
            query = query.where(PromptConfig.question_type == question_type)
        
        # 优先获取默认配置
        query = query.order_by(PromptConfig.is_default.desc())
        
        result = await self.db.execute(query)
        config = result.scalar_one_or_none()
        
        # 如果有关联的LLM，查询LLM配置
        if config and config.llm_config_id:
            llm_result = await self.db.execute(
                select(LLMConfig).where(LLMConfig.id == config.llm_config_id)
            )
            config.llm_config = llm_result.scalar_one_or_none()
        
        return config
    
    async def get_default_by_scene(self, scene: str) -> Optional[PromptConfig]:
        """获取场景的默认配置"""
        result = await self.db.execute(
            select(PromptConfig).where(
                PromptConfig.scene == scene,
                PromptConfig.is_default == True,
                PromptConfig.is_enabled == True
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_scene(self, scene: str) -> List[PromptConfig]:
        """列出场景的所有配置"""
        result = await self.db.execute(
            select(PromptConfig)
            .where(PromptConfig.scene == scene)
            .order_by(PromptConfig.is_default.desc(), PromptConfig.name)
        )
        return list(result.scalars().all())
    
    async def list_all(self) -> List[PromptConfig]:
        """列出所有配置"""
        result = await self.db.execute(
            select(PromptConfig).order_by(PromptConfig.scene, PromptConfig.name)
        )
        return list(result.scalars().all())
    
    async def create(self, config: PromptConfig) -> PromptConfig:
        """创建Prompt配置"""
        # 如果设置为默认，取消同场景的其他默认配置
        if config.is_default:
            existing_defaults = await self.db.execute(
                select(PromptConfig).where(
                    PromptConfig.scene == config.scene,
                    PromptConfig.is_default == True
                )
            )
            for existing in existing_defaults.scalars().all():
                existing.is_default = False
        
        self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config
    
    async def update(self, config: PromptConfig) -> PromptConfig:
        """更新Prompt配置"""
        # 如果设置为默认，取消同场景的其他默认配置
        if config.is_default:
            existing_defaults = await self.db.execute(
                select(PromptConfig).where(
                    PromptConfig.scene == config.scene,
                    PromptConfig.is_default == True,
                    PromptConfig.id != config.id
                )
            )
            for existing in existing_defaults.scalars().all():
                existing.is_default = False
        
        await self.db.flush()
        await self.db.refresh(config)
        return config
    
    async def delete(self, config_id: int) -> bool:
        """删除Prompt配置"""
        config = await self.get_by_id(config_id)
        if config:
            await self.db.delete(config)
            await self.db.flush()
            return True
        return False


class ConfigRepository:
    """配置仓库（统一入口）"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prompt_config = PromptConfigRepository(db)
        # LLM Repository在llm_repository.py中
