"""占卜Repository - 增强版"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, or_
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
    
    async def get_user_sessions(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[DivinationSession]:
        """
        获取用户的占卜会话（带分页）
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
        
        Returns:
            List[DivinationSession]: 占卜会话列表
        """
        result = await self.db.execute(
            select(DivinationSession)
            .where(DivinationSession.user_id == user_id)
            .order_by(DivinationSession.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_user_sessions_with_filters(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        event_type: Optional[str] = None,
        version: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[DivinationSession]:
        """
        获取用户的占卜会话（带过滤和排序）
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
            event_type: 事件类型过滤（decision/career/relationship等）
            version: 版本过滤（CN/Global/TAROT）
            status: 状态过滤（pending/completed/failed）
            start_date: 开始日期
            end_date: 结束日期
            order_by: 排序字段（created_at/updated_at）
            order_direction: 排序方向（asc/desc）
        
        Returns:
            List[DivinationSession]: 占卜会话列表
        """
        query = select(DivinationSession).where(DivinationSession.user_id == user_id)
        
        # 应用过滤条件
        if event_type:
            query = query.where(DivinationSession.event_type == event_type)
        
        if version:
            query = query.where(DivinationSession.version == version)
        
        if status:
            query = query.where(DivinationSession.status == status)
        
        if start_date:
            query = query.where(DivinationSession.created_at >= start_date)
        
        if end_date:
            query = query.where(DivinationSession.created_at <= end_date)
        
        # 应用排序
        order_column = getattr(DivinationSession, order_by, DivinationSession.created_at)
        if order_direction.lower() == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # 应用分页
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_user_sessions(self, user_id: str) -> int:
        """
        统计用户的占卜会话总数
        
        Args:
            user_id: 用户ID
        
        Returns:
            int: 会话总数
        """
        result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(DivinationSession.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def count_user_sessions_with_filters(
        self,
        user_id: str,
        event_type: Optional[str] = None,
        version: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        统计用户的占卜会话总数（带过滤）
        
        Args:
            user_id: 用户ID
            event_type: 事件类型过滤
            version: 版本过滤
            status: 状态过滤
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            int: 会话总数
        """
        query = select(func.count(DivinationSession.id)).where(
            DivinationSession.user_id == user_id
        )
        
        # 应用过滤条件
        if event_type:
            query = query.where(DivinationSession.event_type == event_type)
        
        if version:
            query = query.where(DivinationSession.version == version)
        
        if status:
            query = query.where(DivinationSession.status == status)
        
        if start_date:
            query = query.where(DivinationSession.created_at >= start_date)
        
        if end_date:
            query = query.where(DivinationSession.created_at <= end_date)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户的占卜统计信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            Dict: 统计信息
        """
        # 总数
        total_result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(DivinationSession.user_id == user_id)
        )
        total_count = total_result.scalar() or 0
        
        # 按事件类型统计
        type_result = await self.db.execute(
            select(
                DivinationSession.event_type,
                func.count(DivinationSession.id)
            )
            .where(DivinationSession.user_id == user_id)
            .group_by(DivinationSession.event_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}
        
        # 按版本统计
        version_result = await self.db.execute(
            select(
                DivinationSession.version,
                func.count(DivinationSession.id)
            )
            .where(DivinationSession.user_id == user_id)
            .group_by(DivinationSession.version)
        )
        by_version = {row[0]: row[1] for row in version_result.all()}
        
        # 按状态统计
        status_result = await self.db.execute(
            select(
                DivinationSession.status,
                func.count(DivinationSession.id)
            )
            .where(DivinationSession.user_id == user_id)
            .group_by(DivinationSession.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}
        
        return {
            "total_count": total_count,
            "by_type": by_type,
            "by_version": by_version,
            "by_status": by_status
        }
    
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
