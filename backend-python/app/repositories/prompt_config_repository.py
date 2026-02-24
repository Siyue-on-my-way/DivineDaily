"""Prompt配置仓储层"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt_config import PromptConfig


class PromptConfigRepository:
    """Prompt配置仓储"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_scene(
        self,
        scene: str,
        prompt_type: str = "answer"
    ) -> Optional[PromptConfig]:
        """根据场景获取Prompt配置"""
        stmt = select(PromptConfig).where(
            PromptConfig.scene == scene,
            PromptConfig.prompt_type == prompt_type,
            PromptConfig.is_enabled == True
        ).order_by(
            PromptConfig.is_default.desc(),
            PromptConfig.created_at.desc()
        ).limit(1)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, config_id: int) -> Optional[PromptConfig]:
        """根据ID获取Prompt配置"""
        stmt = select(PromptConfig).where(PromptConfig.id == config_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

