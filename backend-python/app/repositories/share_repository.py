"""分享数据访问层"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, timedelta
import secrets

from app.models.share import DivinationShare
from app.core.logger import get_logger

logger = get_logger("share_repository")


class ShareRepository:
    """分享仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_share(
        self,
        session_id: str,
        share_url: str,
        expires_days: Optional[int] = None,
        is_public: bool = True
    ) -> DivinationShare:
        """创建分享记录"""
        # 生成唯一的分享令牌
        share_token = secrets.token_urlsafe(24)[:32]  # 限制长度为32
        
        # 计算过期时间
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        share = DivinationShare(
            session_id=session_id,
            share_token=share_token,
            share_url=share_url,
            is_public=is_public,
            expires_at=expires_at
        )
        
        self.db.add(share)
        await self.db.flush()
        
        logger.info("创建分享记录", extra={
            "session_id": session_id,
            "share_token": share_token,
            "expires_days": expires_days
        })
        
        return share
    
    async def get_by_token(self, share_token: str) -> Optional[DivinationShare]:
        """根据令牌获取分享记录"""
        result = await self.db.execute(
            select(DivinationShare).where(DivinationShare.share_token == share_token)
        )
        return result.scalar_one_or_none()
    
    async def get_by_session_id(self, session_id: str) -> List[DivinationShare]:
        """获取会话的所有分享记录"""
        result = await self.db.execute(
            select(DivinationShare)
            .where(DivinationShare.session_id == session_id)
            .order_by(DivinationShare.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def increment_view_count(self, share_token: str) -> bool:
        """增加浏览次数"""
        share = await self.get_by_token(share_token)
        if not share:
            return False
        
        share.increment_view_count()
        await self.db.flush()
        
        logger.debug("增加浏览次数", extra={
            "share_token": share_token,
            "view_count": share.view_count
        })
        
        return True
    
    async def delete_share(self, share_token: str) -> bool:
        """删除分享记录"""
        share = await self.get_by_token(share_token)
        if not share:
            return False
        
        await self.db.delete(share)
        await self.db.flush()
        
        logger.info("删除分享记录", extra={"share_token": share_token})
        
        return True
    
    async def get_stats_by_session(self, session_id: str) -> dict:
        """获取会话的分享统计"""
        result = await self.db.execute(
            select(
                func.count(DivinationShare.id).label('total_shares'),
                func.sum(DivinationShare.view_count).label('total_views')
            ).where(DivinationShare.session_id == session_id)
        )
        
        row = result.one()
        
        return {
            "total_shares": row.total_shares or 0,
            "total_views": row.total_views or 0
        }
    
    async def cleanup_expired_shares(self) -> int:
        """清理过期的分享记录"""
        result = await self.db.execute(
            select(DivinationShare).where(
                DivinationShare.expires_at.isnot(None),
                DivinationShare.expires_at < datetime.utcnow()
            )
        )
        
        expired_shares = list(result.scalars().all())
        count = len(expired_shares)
        
        for share in expired_shares:
            await self.db.delete(share)
        
        if count > 0:
            await self.db.flush()
            logger.info("清理过期分享记录", extra={"count": count})
        
        return count
