"""用户档案路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileInfo,
)
from app.services.user_profile_service import UserProfileService
from app.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import NotFoundError

router = APIRouter()


def get_profile_service(db: AsyncSession = Depends(get_db)) -> UserProfileService:
    """获取用户档案服务"""
    return UserProfileService(db)


@router.get("/profile", response_model=UserProfileInfo, tags=["用户档案"])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    service: UserProfileService = Depends(get_profile_service)
):
    """
    获取当前用户档案
    
    - 需要登录
    - 如果档案不存在，返回 404
    """
    profile = await service.get_profile(current_user.id)
    if not profile:
        raise NotFoundError("用户档案不存在，请先创建")
    
    return profile


@router.post("/profile", response_model=UserProfileInfo, tags=["用户档案"])
async def create_my_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    service: UserProfileService = Depends(get_profile_service)
):
    """
    创建当前用户档案
    
    - 需要登录
    - 如果已存在档案，返回错误
    - 自动计算农历、生肖、星座、八字
    """
    profile = await service.create_profile(current_user.id, profile_data)
    return profile


@router.put("/profile", response_model=UserProfileInfo, tags=["用户档案"])
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: UserProfileService = Depends(get_profile_service)
):
    """
    更新当前用户档案
    
    - 需要登录
    - 只更新提供的字段
    - 如果生日更新，自动重新计算命理信息
    """
    profile = await service.update_profile(current_user.id, profile_data)
    return profile


@router.delete("/profile", tags=["用户档案"])
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    service: UserProfileService = Depends(get_profile_service)
):
    """
    删除当前用户档案
    
    - 需要登录
    - 删除后无法恢复
    """
    success = await service.delete_profile(current_user.id)
    if not success:
        raise NotFoundError("用户档案不存在")
    
    return {"message": "档案已删除"}
