"""API v1 路由"""

from fastapi import APIRouter
from app.api.v1 import auth, admin, divination, user_profile, orientation, daily_fortune, users

router = APIRouter()

# 注册子路由
router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(admin.router, prefix="/configs", tags=["配置管理"])
router.include_router(users.router, prefix="/admin", tags=["用户管理"])
router.include_router(divination.router, prefix="/divinations", tags=["占卜"])
router.include_router(user_profile.router, tags=["用户档案"])
router.include_router(orientation.router, prefix="/orientation", tags=["方位推荐"])
router.include_router(daily_fortune.router, prefix="/daily_fortune", tags=["每日运势"])
