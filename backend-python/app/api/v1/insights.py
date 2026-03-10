"""洞察相关 API 路由

提供用户洞察数据的 API 端点
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.insights_service import InsightsService
from app.schemas.insights import (
    OverviewStats,
    QualityTrendResponse,
    TypeDistributionResponse,
    OutcomeDistributionResponse,
    ActivityTimelineResponse,
    RecommendationsResponse
)
import traceback

from app.core.logger import get_logger
logger = get_logger("api.insights")


router = APIRouter()


@router.get("/overview", response_model=OverviewStats)
async def get_insights_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户洞察概览
    
    返回用户的占卜统计概览，包括：
    - 总占卜次数
    - 本周占卜次数
    - 平均问题质量评分
    - 最常见的问题类型
    - 占卜成功率
    - 质量趋势
    
    Returns:
        OverviewStats: 概览统计数据
    """
    try:
        service = InsightsService(db)
        overview = await service.get_overview(str(current_user.id))
        return overview
    except Exception as e:
        logger.error(f"获取洞察概览失败: {e}")
        traceback.print_exc()
        raise


@router.get("/quality-trend", response_model=QualityTrendResponse)
async def get_quality_trend(
    days: int = Query(30, ge=1, le=90, description="天数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取问题质量趋势数据
    
    返回指定天数内的问题质量评分趋势
    
    Args:
        days: 天数（1-90天）
        
    Returns:
        QualityTrendResponse: 质量趋势数据
    """
    try:
        service = InsightsService(db)
        trend = await service.get_quality_trend(str(current_user.id), days)
        return trend
    except Exception as e:
        logger.error(f"获取质量趋势失败: {e}")
        traceback.print_exc()
        raise


@router.get("/type-distribution", response_model=TypeDistributionResponse)
async def get_type_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取占卜类型分布
    
    返回用户各类型占卜的数量和占比
    
    Returns:
        TypeDistributionResponse: 类型分布数据
    """
    try:
        service = InsightsService(db)
        distribution = await service.get_type_distribution(str(current_user.id))
        return distribution
    except Exception as e:
        logger.error(f"获取类型分布失败: {e}")
        traceback.print_exc()
        raise


@router.get("/outcome-distribution", response_model=OutcomeDistributionResponse)
async def get_outcome_distribution(
    period: str = Query('all', regex='^(week|month|all)$', description="时间段"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取占卜结果分布
    
    返回吉/凶/平的数量和占比
    
    Args:
        period: 时间段 (week/month/all)
        
    Returns:
        OutcomeDistributionResponse: 结果分布数据
    """
    try:
        service = InsightsService(db)
        distribution = await service.get_outcome_distribution(str(current_user.id), period)
        return distribution
    except Exception as e:
        logger.error(f"获取结果分布失败: {e}")
        traceback.print_exc()
        raise


@router.get("/activity-timeline", response_model=ActivityTimelineResponse)
async def get_activity_timeline(
    limit: int = Query(10, ge=1, le=50, description="数量限制"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取活动时间线
    
    返回最近的占卜活动列表
    
    Args:
        limit: 数量限制（1-50）
        
    Returns:
        ActivityTimelineResponse: 活动列表
    """
    try:
        service = InsightsService(db)
        timeline = await service.get_activity_timeline(str(current_user.id), limit)
        return timeline
    except Exception as e:
        logger.error(f"获取活动时间线失败: {e}")
        traceback.print_exc()
        raise


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取个性化建议
    
    基于用户的占卜数据分析，提供改进建议
    
    Returns:
        RecommendationsResponse: 建议列表
    """
    try:
        service = InsightsService(db)
        recommendations = await service.get_recommendations(str(current_user.id))
        return recommendations
    except Exception as e:
        logger.error(f"获取建议失败: {e}")
        traceback.print_exc()
        raise
