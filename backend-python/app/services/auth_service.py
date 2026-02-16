"""认证服务"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AuthenticationError, BadRequestError
from app.config import settings


class AuthService:
    """认证服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, user_data: UserCreate) -> Tuple[User, str, str]:
        """用户注册"""
        # 创建用户对象
        user = User(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            nickname=user_data.nickname,
            password_hash=get_password_hash(user_data.password),
            role=UserRole.NORMAL,
            status=1,
        )
        
        # 保存到数据库
        user = await self.user_repo.create(user)
        
        # 生成令牌
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
            }
        )
        refresh_token = create_refresh_token(
            data={
                "user_id": user.id,
                "username": user.username,
            }
        )
        
        return user, access_token, refresh_token
    
    async def login(self, login_data: UserLogin) -> Tuple[User, str, str]:
        """用户登录"""
        # 查找用户（支持用户名/邮箱/手机号登录）
        user = await self.user_repo.get_by_login_identifier(login_data.username)
        
        if not user:
            raise AuthenticationError(detail="用户名或密码错误")
        
        # 验证密码
        if not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError(detail="用户名或密码错误")
        
        # 检查用户状态
        if user.status != 1:
            raise AuthenticationError(detail="账号已被禁用")
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await self.user_repo.update(user)
        
        # 生成令牌
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
            }
        )
        refresh_token = create_refresh_token(
            data={
                "user_id": user.id,
                "username": user.username,
            }
        )
        
        return user, access_token, refresh_token
    
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """刷新令牌"""
        # 解码刷新令牌
        payload = decode_token(refresh_token)
        if not payload:
            raise AuthenticationError(detail="无效的刷新令牌")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationError(detail="无效的刷新令牌")
        
        # 获取用户
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError(detail="用户不存在")
        
        # 生成新令牌
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
            }
        )
        new_refresh_token = create_refresh_token(
            data={
                "user_id": user.id,
                "username": user.username,
            }
        )
        
        return access_token, new_refresh_token
    
    async def get_current_user(self, token: str) -> User:
        """获取当前用户"""
        # 解码令牌
        payload = decode_token(token)
        if not payload:
            raise AuthenticationError(detail="无效的令牌")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationError(detail="无效的令牌")
        
        # 获取用户
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError(detail="用户不存在")
        
        return user
    
    async def init_admin_user(self):
        """初始化管理员用户"""
        # 检查管理员是否已存在
        admin = await self.user_repo.get_by_username(settings.ADMIN_USERNAME)
        if admin:
            return
        
        # 创建管理员
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            status=1,
        )
        
        await self.user_repo.create(admin)
        print(f"✅ 管理员账号已创建: {settings.ADMIN_USERNAME}")
