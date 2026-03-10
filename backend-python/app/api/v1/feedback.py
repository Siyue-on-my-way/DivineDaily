"""反馈 API 路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.feedback_service import FeedbackService
from app.schemas.feedback import (
    DivinationFeedbackRequest,
    QualityFeedbackRequest,
    FeedbackResponse
)
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/divination", response_model=FeedbackResponse, tags=["反馈系统"])
async def submit_divination_feedback(
    request: DivinationFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提交占卜反馈
    
    - feedback_type: 'quality'(质量), 'accuracy'(准确性), 'helpfulness'(有用性)
    - rating: 1-5 星评分
    - tags: 标签列表，如 ['准确', '有帮助', '不够具体']
    - is_helpful: 是否有帮助
    """
    service = FeedbackService(db)
    feedback = await service.submit_divination_feedback(
        session_id=request.session_id,
        user_id=current_user.id,
        feedback_type=request.feedback_type,
        rating=request.rating,
        comment=request.comment,
        tags=request.tags,
        is_helpful=request.is_helpful
    )
    await db.commit()
    
    return FeedbackResponse(
        id=feedback.id,
        message="反馈提交成功",
        success=True
    )


@router.post("/quality", response_model=FeedbackResponse, tags=["反馈系统"])
async def submit_quality_feedback(
    request: QualityFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提交问题质量反馈
    
    对问题质量评估结果进行反馈
    """
    service = FeedbackService(db)
    record = await service.submit_quality_feedback(
        quality_history_id=request.quality_history_id,
        rating=request.rating,
        comment=request.comment
    )
    await db.commit()
    
    if not record:
        return FeedbackResponse(
            id=0,
            message="质量记录不存在",
            success=False
        )
    
    return FeedbackResponse(
        id=record.id,
        message="反馈提交成功",
        success=True
    )


@router.get("/statistics", tags=["反馈系统"])
async def get_feedback_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取反馈统计
    
    管理员可查看全局统计，普通用户查看个人统计
    """
    service = FeedbackService(db)
    user_id = None if current_user.role == 'admin' else current_user.id
    stats = await service.get_feedback_statistics(user_id)
    return stats
