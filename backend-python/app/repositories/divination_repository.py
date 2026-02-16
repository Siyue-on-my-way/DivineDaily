"""占卜Repository"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.divination import DivinationSession
from datetime import datetime, timedelta


class DivinationRepository:
    """占卜数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_session(self, session: DivinationSession) -> DivinationSession:
        """保存占卜会话"""
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session
    
    async def get_session(self, session_id: str) -> Optional[DivinationSession]:
        """获取占卜会话"""
        result = await self.db.execute(
            select(DivinationSession).where(DivinationSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_sessions(self, user_id: int, limit: int = 50) -> List[DivinationSession]:
        """获取用户的占卜会话"""
        result = await self.db.execute(
            select(DivinationSession)
            .where(DivinationSession.user_id == user_id)
            .order_by(DivinationSession.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_recent_sessions(self, days: int = 7, limit: int = 100) -> List[DivinationSession]:
        """获取最近的占卜会话"""
        since = datetime.now() - timedelta(days=days)
        result = await self.db.execute(
            select(DivinationSession)
            .where(DivinationSession.created_at >= since)
            .order_by(DivinationSession.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_session(self, session: DivinationSession) -> DivinationSession:
        """更新占卜会话"""
        await self.db.flush()
        await self.db.refresh(session)
        return session
    
    async def delete_session(self, session_id: str) -> bool:
        """删除占卜会话"""
        session = await self.get_session(session_id)
        if session:
            await self.db.delete(session)
            await self.db.flush()
            return True
        return False
