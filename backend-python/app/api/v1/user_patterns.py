"""用户行为模式 API 路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user_pattern_service import UserPatternService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/my-patterns", tags=["用户行为模式"])
async def get_my_patterns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的行为模式
    
    返回用户的所有行为模式数据：
    - question_style: 问题风格
    - topic_preference: 话题偏好
    - time_preference: 时间偏好
    - quality_trend: 质量趋势
    """
    service = UserPatternService(db)
    patterns = await service.get_user_patterns(current_user.id)
    return patterns


@router.post("/analyze", tags=["用户行为模式"])
async def trigger_pattern_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    手动触发模式分析
    
    分析并更新用户的所有行为模式
    """
    service = UserPatternService(db)
    await service.analyze_and_update_patterns(current_user.id)
    await db.commit()
    return {"message": "模式分析完成", "success": True}
