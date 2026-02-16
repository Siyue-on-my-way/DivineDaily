"""智能预处理路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.schemas.intent import (
    QuestionAnalyzeRequest,
    IntentResult,
    QuestionQualityScore,
    IntentStatistics,
)
from app.services.intent_service import IntentRecognitionService
from app.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()


def get_intent_service(db: AsyncSession = Depends(get_db)) -> IntentRecognitionService:
    """获取意图识别服务"""
    return IntentRecognitionService(db)


@router.post("/analyze", response_model=IntentResult, tags=["智能预处理"])
async def analyze_question(
    request: QuestionAnalyzeRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: IntentRecognitionService = Depends(get_intent_service)
):
    """
    分析问题意图
    
    - 识别问题类型（事业/感情/财运/健康/学业/其他）
    - 识别占卜类型（易经/塔罗）
    - 提取关键词
    - 增强问题
    - 生成建议
    """
    user_id = current_user.id if current_user else None
    
    # 分析意图
    intent_result = service.analyze_intent(request.question, user_id)
    
    # 保存结果（异步，不等待）
    try:
        await service.save_intent(request.question, intent_result, user_id)
        await service.db.commit()
    except:
        pass  # 保存失败不影响返回结果
    
    return intent_result


@router.post("/quality", response_model=QuestionQualityScore, tags=["智能预处理"])
async def evaluate_question_quality(
    request: QuestionAnalyzeRequest,
    service: IntentRecognitionService = Depends(get_intent_service)
):
    """
    评估问题质量
    
    - 清晰度评分
    - 具体性评分
    - 完整性评分
    - 识别问题
    - 生成改进建议
    """
    quality_score = service.evaluate_quality(request.question)
    return quality_score


@router.get("/statistics", response_model=IntentStatistics, tags=["智能预处理"])
async def get_intent_statistics(
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: IntentRecognitionService = Depends(get_intent_service)
):
    """
    获取意图统计
    
    - 总数统计
    - 意图分布
    - 类别分布
    - 平均置信度
    - 高频关键词
    """
    user_id = current_user.id if current_user else None
    statistics = await service.get_statistics(user_id)
    
    return IntentStatistics(
        total_count=statistics['total_count'],
        intent_distribution=statistics['intent_distribution'],
        category_distribution=statistics['category_distribution'],
        avg_confidence=statistics['avg_confidence'],
        top_keywords=statistics['top_keywords'],
    )
