"""意图识别仓库"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.question_intent import QuestionIntent
from datetime import datetime, timedelta


class IntentRepository:
    """意图识别数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save(self, intent: QuestionIntent) -> QuestionIntent:
        """保存意图记录"""
        self.db.add(intent)
        await self.db.flush()
        await self.db.refresh(intent)
        return intent
    
    async def get_by_id(self, intent_id: int) -> Optional[QuestionIntent]:
        """根据ID获取意图记录"""
        result = await self.db.execute(
            select(QuestionIntent).where(QuestionIntent.id == intent_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(self, user_id: int, limit: int = 100) -> List[QuestionIntent]:
        """获取用户的意图记录"""
        result = await self.db.execute(
            select(QuestionIntent)
            .where(QuestionIntent.user_id == user_id)
            .order_by(QuestionIntent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_recent(self, days: int = 7, limit: int = 100) -> List[QuestionIntent]:
        """获取最近的意图记录"""
        since = datetime.now() - timedelta(days=days)
        result = await self.db.execute(
            select(QuestionIntent)
            .where(QuestionIntent.created_at >= since)
            .order_by(QuestionIntent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_intent_type(self, intent_type: str) -> int:
        """统计某种意图类型的数量"""
        result = await self.db.execute(
            select(func.count(QuestionIntent.id))
            .where(QuestionIntent.intent_type == intent_type)
        )
        return result.scalar() or 0
    
    async def count_by_category(self, category: str) -> int:
        """统计某种类别的数量"""
        result = await self.db.execute(
            select(func.count(QuestionIntent.id))
            .where(QuestionIntent.category == category)
        )
        return result.scalar() or 0
    
    async def get_avg_confidence(self) -> float:
        """获取平均置信度"""
        result = await self.db.execute(
            select(func.avg(QuestionIntent.confidence))
        )
        avg = result.scalar()
        return float(avg) if avg else 0.0
