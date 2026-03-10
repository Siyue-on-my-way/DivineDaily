"""问题质量评估 API 路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.services.question_quality_service import QuestionQualityService
from app.schemas.question_quality import (
    QuestionQualityRequest,
    QuestionQualityResponse,
    QuestionQualityHistoryResponse
)
from app.dependencies import get_current_user_optional
from app.models.user import User
from app.models.question_quality import QuestionQualityHistory

router = APIRouter()


@router.post("/evaluate", response_model=QuestionQualityResponse, tags=["问题质量评估"])
async def evaluate_question_quality(
    request: QuestionQualityRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    评估问题质量
    
    返回 4 维度评分和改进建议：
    - 具体性评分
    - 个人相关性评分
    - 决策价值评分
    - 时效性评分
    """
    service = QuestionQualityService()
    result = service.evaluate_quality(request.question)
    return QuestionQualityResponse(**result)


@router.get("/history", response_model=List[QuestionQualityHistoryResponse], tags=["问题质量评估"])
async def get_quality_history(
    user_id: int = Query(..., description="用户ID"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的问题质量历史
    
    返回用户历史问题的质量评估记录
    """
    result = await db.execute(
        select(QuestionQualityHistory)
        .where(QuestionQualityHistory.user_id == user_id)
        .order_by(QuestionQualityHistory.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    records = result.scalars().all()
    
    return [QuestionQualityHistoryResponse.from_orm(record) for record in records]
