"""用户仓储层"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
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
