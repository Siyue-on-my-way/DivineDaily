"""用户管理服务层"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from datetime import datetime
import secrets
import string

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.schemas.user_management import (
    UserCreateAdmin, UserUpdateAdmin, UserDetailResponse,
    ResetPasswordRequest, ChangeRoleRequest, ChangeStatusRequest,
    BatchStatusRequest, UserStatsResponse
)
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundError, BadRequestError, PermissionDeniedError

from app.core.logger import get_logger
logger = get_logger("user_management")



class UserManagementService:
    """用户管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.profile_repo = UserProfileRepository(db)
    
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
        """获取用户列表"""
        return await self.user_repo.list_users(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            status=status,
            order_by=order_by,
            order_direction=order_direction,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_user_detail(self, user_id: int) -> UserDetailResponse:
        """获取用户详情（包含统计信息）"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        
        # 获取用户档案
        profile = await self.profile_repo.get_by_user_id(user_id)
        
        # 获取占卜统计
        from app.models.divination import DivinationSession
        from sqlalchemy import select, func
        
        # 总占卜次数
        divination_count_result = await self.db.execute(
            select(func.count(DivinationSession.id)).where(
                DivinationSession.user_id == str(user_id)
            )
        )
        divination_count = divination_count_result.scalar() or 0
        
        # 周易占卜次数
        iching_count_result = await self.db.execute(
            select(func.count(DivinationSession.id)).where(
                DivinationSession.user_id == str(user_id),
                DivinationSession.version == "CN"
            )
        )
        iching_count = iching_count_result.scalar() or 0
        
        # 塔罗占卜次数
        tarot_count_result = await self.db.execute(
            select(func.count(DivinationSession.id)).where(
                DivinationSession.user_id == str(user_id),
                DivinationSession.version == "TAROT"
            )
        )
        tarot_count = tarot_count_result.scalar() or 0
        
        # 最后占卜时间
        last_divination_result = await self.db.execute(
            select(DivinationSession.created_at).where(
                DivinationSession.user_id == str(user_id)
            ).order_by(DivinationSession.created_at.desc()).limit(1)
        )
        last_divination_at = last_divination_result.scalar_one_or_none()
        
        # 运势查询次数
        from app.models.daily_fortune import DailyFortune
        fortune_count_result = await self.db.execute(
            select(func.count(DailyFortune.id)).where(
                DailyFortune.user_id == user_id
            )
        )
        fortune_count = fortune_count_result.scalar() or 0
        
        return UserDetailResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            role=user.role,
            status=user.status,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            divination_count=divination_count,
            iching_count=iching_count,
            tarot_count=tarot_count,
            fortune_count=fortune_count,
            last_divination_at=last_divination_at,
            birth_date=profile.birth_date.isoformat() if profile and profile.birth_date else None,
            animal=profile.animal if profile else None,
            zodiac_sign=profile.zodiac_sign if profile else None
        )
    
    async def create_user(
        self,
        user_data: UserCreateAdmin,
        operator: User,
        ip_address: Optional[str] = None
    ) -> User:
        """创建用户"""
        # 创建用户对象
        user = User(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            nickname=user_data.nickname,
            avatar=user_data.avatar,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            status=user_data.status
        )
        
        # 保存用户
        user = await self.user_repo.create(user)
        
        # 记录审计日志
        await self.audit_repo.create_log(
            operator_id=operator.id,
            operator_name=operator.username,
            action="create_user",
            target_user_id=user.id,
            target_username=user.username,
            details={
                "role": user.role,
                "status": user.status
            },
            ip_address=ip_address
        )
        
        await self.db.commit()
        return user
    
    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdateAdmin,
        operator: User,
        ip_address: Optional[str] = None
    ) -> User:
        """更新用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        
        # 不允许修改自己的角色
        if user_id == operator.id and user_data.role and user_data.role != user.role:
            raise PermissionDeniedError(detail="不能修改自己的角色")
        
        # 记录变更
        changes = {}
        
        # 更新字段
        if user_data.username and user_data.username != user.username:
            # 检查用户名是否已存在
            if await self.user_repo.check_username_exists(user_data.username, user_id):
                raise BadRequestError(detail="用户名已存在")
            changes["username"] = {"old": user.username, "new": user_data.username}
            user.username = user_data.username
        
        if user_data.email is not None and user_data.email != user.email:
            # 检查邮箱是否已存在
            if user_data.email and await self.user_repo.check_email_exists(user_data.email, user_id):
                raise BadRequestError(detail="邮箱已被使用")
            changes["email"] = {"old": user.email, "new": user_data.email}
            user.email = user_data.email
        
        if user_data.phone is not None and user_data.phone != user.phone:
            # 检查手机号是否已存在
            if user_data.phone and await self.user_repo.check_phone_exists(user_data.phone, user_id):
                raise BadRequestError(detail="手机号已被使用")
            changes["phone"] = {"old": user.phone, "new": user_data.phone}
            user.phone = user_data.phone
        
        if user_data.nickname is not None:
            changes["nickname"] = {"old": user.nickname, "new": user_data.nickname}
            user.nickname = user_data.nickname
        
        if user_data.avatar is not None:
            user.avatar = user_data.avatar
        
        if user_data.role and user_data.role != user.role:
            changes["role"] = {"old": user.role, "new": user_data.role}
            user.role = user_data.role
        
        if user_data.status is not None and user_data.status != user.status:
            old_status = user.status
            changes["status"] = {"old": old_status, "new": user_data.status}
            user.status = user_data.status
            
            # 记录状态变更历史
            await self.audit_repo.create_status_history(
                user_id=user_id,
                old_status=old_status,
                new_status=user_data.status,
                operator_id=operator.id
            )
        
        # 保存更新
        user = await self.user_repo.update(user)
        
        # 记录审计日志
        if changes:
            await self.audit_repo.create_log(
                operator_id=operator.id,
                operator_name=operator.username,
                action="update_user",
                target_user_id=user.id,
                target_username=user.username,
                details={"changes": changes},
                ip_address=ip_address
            )
        
        await self.db.commit()
        return user
    
    async def delete_user(
        self,
        user_id: int,
        operator: User,
        ip_address: Optional[str] = None
    ) -> bool:
        """删除用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        
        # 不允许删除自己
        if user_id == operator.id:
            raise PermissionDeniedError(detail="不能删除自己")
        
        # 不允许删除超级管理员（假设 ID=1 是超级管理员）
        if user_id == 1:
            raise PermissionDeniedError(detail="不能删除超级管理员")
        
        # 记录审计日志
        await self.audit_repo.create_log(
            operator_id=operator.id,
            operator_name=operator.username,
            action="delete_user",
            target_user_id=user.id,
            target_username=user.username,
            details={
                "role": user.role,
                "status": user.status
            },
            ip_address=ip_address
        )
        
        # 删除用户
        await self.user_repo.delete(user_id)
        await self.db.commit()
        return True
    
    async def batch_delete_users(
        self,
        user_ids: List[int],
        operator: User,
        ip_address: Optional[str] = None
    ) -> dict:
        """批量删除用户"""
        # 过滤掉自己和超级管理员
        filtered_ids = [uid for uid in user_ids if uid != operator.id and uid != 1]
        
        if not filtered_ids:
            raise BadRequestError(detail="没有可删除的用户")
        
        # 记录审计日志
        await self.audit_repo.create_log(
            operator_id=operator.id,
            operator_name=operator.username,
            action="batch_delete_users",
            details={
                "user_ids": filtered_ids,
                "count": len(filtered_ids)
            },
            ip_address=ip_address
        )
        
        # 批量删除
        deleted_count = await self.user_repo.batch_delete(filtered_ids)
        await self.db.commit()
        
        return {
            "deleted_count": deleted_count,
            "skipped_count": len(user_ids) - len(filtered_ids)
        }
    
    async def reset_password(
        self,
        user_id: int,
        request: ResetPasswordRequest,
        operator: User,
        ip_address: Optional[str] = None
    ) -> dict:
        """重置用户密码"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        
        # 生成密码
        if request.generate_random:
            new_password = self._generate_random_password()
        elif request.new_password:
            new_password = request.new_password
        else:
            raise BadRequestError(detail="请提供新密码或选择生成随机密码")
        
        # 更新密码
        user.password_hash = get_password_hash(new_password)
        await self.user_repo.update(user)
        
        # 记录审计日志
        await self.audit_repo.create_log(
            operator_id=operator.id,
            operator_name=operator.username,
            action="reset_password",
            target_user_id=user.id,
            target_username=user.username,
            details={
                "generate_random": request.generate_random,
                "send_email": request.send_email
            },
            ip_address=ip_address
        )
        
        await self.db.commit()
        
        # TODO: 发送邮件通知（如果需要）
        
        return {
            "success": True,
            "new_password": new_password if request.generate_random else None
        }
    
    async def change_role(
        self,
        user_id: int,
        request: ChangeRoleRequest,
        operator: User,
        ip_address: Optional[str] = None
    ) -> User:
        """修改用户角色"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        
        # 不允许修改自己的角色
        if user_id == operator.id:
            raise PermissionDeniedError(detail="不能修改自己的角色")
        
        # 不允许修改超级管理员的角色
        if user_id == 1:
            raise PermissionDeniedError(detail="不能修改超级管理员的角色")
        
        old_role = user.role
        user.role = request.role
        await self.user_repo.update(user)
        
        # 记录审计日志
        await self.audit_repo.create_log(
            operator_id=operator.id,
            operator_name=operator.username,
            action="change_role",
            target_user_id=user.id,
            target_username=user.username,
            details={
                "old_role": old_role,
                "new_role": request.role
            },
            ip_address=ip_address
        )
        
        await self.db.commit()
        return user
    
    async def change_status(
        self,
        user_id: int,
        request: ChangeStatusRequest,
        operator: User,
        ip_address: Optional[str] = None
    ) -> User:
        """修改用户状态"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        
        # 不允许禁用自己
        if user_id == operator.id and request.status == 0:
            raise PermissionDeniedError(detail="不能禁用自己")
        
        old_status = user.status
        user.status = request.status
        await self.user_repo.update(user)
        
        # 记录状态变更历史
        await self.audit_repo.create_status_history(
            user_id=user_id,
            old_status=old_status,
            new_status=request.status,
            operator_id=operator.id,
            reason=request.reason
        )
        
        # 记录审计日志
        await self.audit_repo.create_log(
            operator_id=operator.id,
            operator_name=operator.username,
            action="change_status",
            target_user_id=user.id,
            target_username=user.username,
            details={
                "old_status": old_status,
                "new_status": request.status,
                "reason": request.reason
            },
            ip_address=ip_address
        )
        
        await self.db.commit()
        return user
    
    async def batch_change_status(
        self,
        request: BatchStatusRequest,
        operator: User,
        ip_address: Optional[str] = None
    ) -> dict:
        """批量修改用户状态"""
        # 如果是禁用操作，过滤掉自己
        filtered_ids = request.user_ids
        if request.status == 0:
            filtered_ids = [uid for uid in request.user_ids if uid != operator.id]
        
        if not filtered_ids:
            raise BadRequestError(detail="没有可修改的用户")
        
        # 批量更新状态
        updated_count = await self.user_repo.batch_update_status(filtered_ids, request.status)
        
        # 记录审计日志
        await self.audit_repo.create_log(
            operator_id=operator.id,
            operator_name=operator.username,
            action="batch_change_status",
            details={
                "user_ids": filtered_ids,
                "status": request.status,
                "reason": request.reason,
                "count": updated_count
            },
            ip_address=ip_address
        )
        
        await self.db.commit()
        
        return {
            "updated_count": updated_count,
            "skipped_count": len(request.user_ids) - len(filtered_ids)
        }
    
    async def get_user_stats(self) -> UserStatsResponse:
        """获取用户统计数据"""
        stats = await self.user_repo.get_user_stats()
        return UserStatsResponse(**stats)
    
    def _generate_random_password(self, length: int = 12) -> str:
        """生成随机密码"""
        # 确保包含大写、小写、数字
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits)
        ]
        
        # 填充剩余字符
        all_chars = string.ascii_letters + string.digits
        password.extend(secrets.choice(all_chars) for _ in range(length - 3))
        
        # 打乱顺序
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)

