"""API v1 路由"""

from fastapi import APIRouter
from app.api.v1 import auth, admin, divination, user_profile, orientation

router = APIRouter()

# 注册子路由
router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(admin.router, prefix="/configs", tags=["配置管理"])
router.include_router(divination.router, prefix="/divinations", tags=["占卜"])
router.include_router(user_profile.router, tags=["用户档案"])
router.include_router(orientation.router, prefix="/orientation", tags=["方位推荐"])

# TODO: 其他路由需要先实现对应的服务和API
# 暂时返回简单的占位响应，避免404错误

from fastapi import HTTPException
from typing import List, Dict, Any

@router.post("/daily_fortune")
async def get_daily_fortune():
    """每日运势（占位）"""
    return {
        "overall_score": 4,
        "love_score": 4,
        "career_score": 4,
        "wealth_score": 4,
        "health_score": 4,
        "lucky_color": "蓝色",
        "lucky_number": 8,
        "content": "今日运势良好，诸事顺利。"
    }
