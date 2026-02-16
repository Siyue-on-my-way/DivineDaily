"""用户资料数据访问层"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile


class UserProfileRepository:
    """用户资料仓储"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """根据用户ID获取资料"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_id: int, **kwargs) -> UserProfile:
        """创建用户资料"""
        profile = UserProfile(user_id=user_id, **kwargs)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
    
    async def update(self, profile: UserProfile, **kwargs) -> UserProfile:
        """更新用户资料"""
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
