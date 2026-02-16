"""每日运势数据访问层"""

from typing import Optional, List
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_fortune import DailyFortune


class DailyFortuneRepository:
    """每日运势仓储"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_user_and_date(
        self,
        user_id: int,
        fortune_date: date
    ) -> Optional[DailyFortune]:
        """根据用户ID和日期获取运势"""
        result = await self.db.execute(
            select(DailyFortune).where(
                DailyFortune.user_id == user_id,
                DailyFortune.fortune_date == fortune_date
            )
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        user_id: int,
        fortune_date: date,
        overall_score: int,
        love_score: int,
        career_score: int,
        wealth_score: int,
        health_score: int,
        lucky_color: str,
        lucky_number: int,
        content: str
    ) -> DailyFortune:
        """创建运势记录"""
        fortune = DailyFortune(
            user_id=user_id,
            fortune_date=fortune_date,
            overall_score=overall_score,
            love_score=love_score,
            career_score=career_score,
            wealth_score=wealth_score,
            health_score=health_score,
            lucky_color=lucky_color,
            lucky_number=lucky_number,
            content=content
        )
        self.db.add(fortune)
        await self.db.commit()
        await self.db.refresh(fortune)
        return fortune
    
    async def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 30
    ) -> List[DailyFortune]:
        """获取用户的运势历史"""
        result = await self.db.execute(
            select(DailyFortune)
            .where(DailyFortune.user_id == user_id)
            .order_by(DailyFortune.fortune_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
