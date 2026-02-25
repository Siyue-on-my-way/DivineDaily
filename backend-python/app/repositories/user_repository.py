"""用户仓储层（扩展版）"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_, desc, asc
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from app.models.user import User, UserRole
from app.core.exceptions import NotFoundError, ConflictError


class UserRepository:
    """用户数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user: User) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing = await self.get_by_username(user.username)
        if existing:
            raise ConflictError(detail="用户名已存在")
        
        # 检查邮箱是否已存在
        if user.email:
            existing = await self.get_by_email(user.email)
            if existing:
                raise ConflictError(detail="邮箱已被使用")
        
        # 检查手机号是否已存在
        if user.phone:
            existing = await self.get_by_phone(user.phone)
            if existing:
                raise ConflictError(detail="手机号已被使用")
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_login_identifier(self, identifier: str) -> Optional[User]:
        """根据登录标识获取用户（用户名/邮箱/手机号）"""
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.username == identifier,
                    User.email == identifier,
                    User.phone == identifier
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, user: User) -> User:
        """更新用户"""
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        
        await self.db.delete(user)
        await self.db.flush()
        return True
    
    # ==================== 新增：用户管理功能 ====================
    
    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[int] = None,
        order_by: str = "created_at",
        order_direction: str = "desc",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[User], int]:
        """获取用户列表（分页、搜索、筛选）"""
        query = select(User)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.phone.ilike(search_pattern),
                    User.nickname.ilike(search_pattern)
                )
            )
        
        # 角色筛选
        if role:
            query = query.where(User.role == role)
        
        # 状态筛选
        if status is not None:
            query = query.where(User.status == status)
        
        # 时间范围筛选
        if start_date:
            query = query.where(User.created_at >= start_date)
        if end_date:
            query = query.where(User.created_at <= end_date)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 排序
        order_column = getattr(User, order_by, User.created_at)
        if order_direction == "asc":
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return users, total
    
    async def get_user_stats(self) -> dict:
        """获取用户统计数据"""
        # 总用户数
        total_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_result.scalar()
        
        # 管理员数量
        admin_result = await self.db.execute(
            select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        )
        admin_users = admin_result.scalar()
        
        # 普通用户数量
        normal_users = total_users - admin_users
        
        # 启用用户数量
        active_result = await self.db.execute(
            select(func.count(User.id)).where(User.status == 1)
        )
        active_users = active_result.scalar()
        
        # 禁用用户数量
        disabled_users = total_users - active_users
        
        # 今日新增
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= today)
        )
        today_new_users = today_result.scalar()
        
        # 本周新增
        week_ago = datetime.now() - timedelta(days=7)
        week_result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= week_ago)
        )
        week_new_users = week_result.scalar()
        
        # 本月新增
        month_ago = datetime.now() - timedelta(days=30)
        month_result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= month_ago)
        )
        month_new_users = month_result.scalar()
        
        # 7天活跃用户
        active_7days_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.last_login_at >= week_ago,
                    User.status == 1
                )
            )
        )
        active_7days = active_7days_result.scalar()
        
        # 30天活跃用户
        active_30days_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.last_login_at >= month_ago,
                    User.status == 1
                )
            )
        )
        active_30days = active_30days_result.scalar()
        
        return {
            "total_users": total_users,
            "admin_users": admin_users,
            "normal_users": normal_users,
            "active_users": active_users,
            "disabled_users": disabled_users,
            "today_new_users": today_new_users,
            "week_new_users": week_new_users,
            "month_new_users": month_new_users,
            "active_7days": active_7days,
            "active_30days": active_30days
        }
    
    async def batch_update_status(
        self,
        user_ids: List[int],
        status: int
    ) -> int:
        """批量更新用户状态"""
        from sqlalchemy import update
        
        stmt = update(User).where(User.id.in_(user_ids)).values(status=status)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
    
    async def batch_delete(self, user_ids: List[int]) -> int:
        """批量删除用户"""
        from sqlalchemy import delete
        
        stmt = delete(User).where(User.id.in_(user_ids))
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
    
    async def check_username_exists(
        self,
        username: str,
        exclude_user_id: Optional[int] = None
    ) -> bool:
        """检查用户名是否存在（排除指定用户）"""
        query = select(User).where(User.username == username)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def check_email_exists(
        self,
        email: str,
        exclude_user_id: Optional[int] = None
    ) -> bool:
        """检查邮箱是否存在（排除指定用户）"""
        query = select(User).where(User.email == email)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def check_phone_exists(
        self,
        phone: str,
        exclude_user_id: Optional[int] = None
    ) -> bool:
        """检查手机号是否存在（排除指定用户）"""
        query = select(User).where(User.phone == phone)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
