"""审计日志仓储层"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List, Tuple
from datetime import datetime
from app.models.user_audit import UserAuditLog, UserStatusHistory


class AuditLogRepository:
    """审计日志数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_log(
        self,
        operator_id: int,
        operator_name: str,
        action: str,
        target_user_id: Optional[int] = None,
        target_username: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None
    ) -> UserAuditLog:
        """创建审计日志"""
        log = UserAuditLog(
            operator_id=operator_id,
            operator_name=operator_name,
            action=action,
            target_user_id=target_user_id,
            target_username=target_username,
            details=details,
            ip_address=ip_address
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log
    
    async def list_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        operator_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[UserAuditLog], int]:
        """查询审计日志列表"""
        query = select(UserAuditLog)
        
        # 筛选条件
        if operator_id:
            query = query.where(UserAuditLog.operator_id == operator_id)
        if target_user_id:
            query = query.where(UserAuditLog.target_user_id == target_user_id)
        if action:
            query = query.where(UserAuditLog.action == action)
        if start_date:
            query = query.where(UserAuditLog.created_at >= start_date)
        if end_date:
            query = query.where(UserAuditLog.created_at <= end_date)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 分页查询
        query = query.order_by(desc(UserAuditLog.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return logs, total
    
    async def create_status_history(
        self,
        user_id: int,
        old_status: int,
        new_status: int,
        operator_id: int,
        reason: Optional[str] = None
    ) -> UserStatusHistory:
        """创建状态变更历史"""
        history = UserStatusHistory(
            user_id=user_id,
            old_status=old_status,
            new_status=new_status,
            operator_id=operator_id,
            reason=reason
        )
        self.db.add(history)
        await self.db.flush()
        await self.db.refresh(history)
        return history
    
    async def get_status_history(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[UserStatusHistory]:
        """获取用户状态变更历史"""
        query = select(UserStatusHistory).where(
            UserStatusHistory.user_id == user_id
        ).order_by(desc(UserStatusHistory.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

