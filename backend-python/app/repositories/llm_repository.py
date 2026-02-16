"""LLM配置仓库"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.llm_config import LLMConfig


class LLMRepository:
    """LLM配置数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, llm_id: int) -> Optional[LLMConfig]:
        """根据ID获取LLM配置"""
        result = await self.db.execute(
            select(LLMConfig).where(LLMConfig.id == llm_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[LLMConfig]:
        """根据名称获取LLM配置"""
        result = await self.db.execute(
            select(LLMConfig).where(LLMConfig.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_default(self) -> Optional[LLMConfig]:
        """获取默认LLM配置"""
        result = await self.db.execute(
            select(LLMConfig)
            .where(LLMConfig.is_default == True)
            .where(LLMConfig.is_enabled == True)
        )
        return result.scalar_one_or_none()
    
    async def list_enabled(self) -> List[LLMConfig]:
        """列出所有启用的LLM配置"""
        result = await self.db.execute(
            select(LLMConfig)
            .where(LLMConfig.is_enabled == True)
            .order_by(LLMConfig.is_default.desc(), LLMConfig.name)
        )
        return list(result.scalars().all())
    
    async def list_all(self) -> List[LLMConfig]:
        """列出所有LLM配置"""
        result = await self.db.execute(
            select(LLMConfig).order_by(LLMConfig.is_default.desc(), LLMConfig.name)
        )
        return list(result.scalars().all())
    
    async def create(self, llm_config: LLMConfig) -> LLMConfig:
        """创建LLM配置"""
        # 如果设置为默认，取消其他默认配置
        if llm_config.is_default:
            await self.db.execute(
                select(LLMConfig).where(LLMConfig.is_default == True)
            )
            existing_defaults = await self.db.execute(
                select(LLMConfig).where(LLMConfig.is_default == True)
            )
            for config in existing_defaults.scalars().all():
                config.is_default = False
        
        self.db.add(llm_config)
        await self.db.flush()
        await self.db.refresh(llm_config)
        return llm_config
    
    async def update(self, llm_config: LLMConfig) -> LLMConfig:
        """更新LLM配置"""
        # 如果设置为默认，取消其他默认配置
        if llm_config.is_default:
            existing_defaults = await self.db.execute(
                select(LLMConfig)
                .where(LLMConfig.is_default == True)
                .where(LLMConfig.id != llm_config.id)
            )
            for config in existing_defaults.scalars().all():
                config.is_default = False
        
        await self.db.flush()
        await self.db.refresh(llm_config)
        return llm_config
    
    async def delete(self, llm_id: int) -> bool:
        """删除LLM配置"""
        llm_config = await self.get_by_id(llm_id)
        if llm_config:
            await self.db.delete(llm_config)
            await self.db.flush()
            return True
        return False
