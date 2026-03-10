"""洞察相关数据模型"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OverviewStats(BaseModel):
    """概览统计数据"""
    total_count: int = Field(..., description="总占卜次数")
    week_count: int = Field(..., description="本周占卜次数")
    avg_quality_score: float = Field(..., description="平均问题质量评分")
    most_common_type: str = Field(..., description="最常见的问题类型")
    success_rate: float = Field(..., description="占卜成功率")
    quality_trend: str = Field(..., description="质量趋势 (excellent/good/stable/needs_improvement)")
    last_divination: Optional[str] = Field(None, description="最后一次占卜时间")


class QualityTrendDataPoint(BaseModel):
    """质量趋势数据点"""
    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    score: float = Field(..., description="平均质量评分")
    count: int = Field(..., description="当天占卜次数")


class QualityTrendResponse(BaseModel):
    """质量趋势响应"""
    data: List[QualityTrendDataPoint] = Field(..., description="趋势数据点列表")
    avg_score: float = Field(..., description="平均评分")
    max_score: float = Field(..., description="最高评分")
    min_score: float = Field(..., description="最低评分")


class TypeDistributionItem(BaseModel):
    """类型分布项"""
    type: str = Field(..., description="问题类型")
    count: int = Field(..., description="数量")
    percentage: float = Field(..., description="占比百分比")


class TypeDistributionResponse(BaseModel):
    """类型分布响应"""
    distribution: List[TypeDistributionItem] = Field(..., description="类型分布列表")


class OutcomeDistributionItem(BaseModel):
    """结果分布项"""
    outcome: str = Field(..., description="占卜结果 (吉/凶/平)")
    count: int = Field(..., description="数量")
    percentage: float = Field(..., description="占比百分比")


class OutcomeDistributionResponse(BaseModel):
    """结果分布响应"""
    distribution: List[OutcomeDistributionItem] = Field(..., description="结果分布列表")
    period: str = Field(..., description="时间段 (week/month/all)")


class ActivityItem(BaseModel):
    """活动项"""
    id: str = Field(..., description="会话ID")
    question: str = Field(..., description="问题")
    type: str = Field(..., description="问题类型")
    outcome: str = Field(..., description="占卜结果")
    quality_score: Optional[int] = Field(None, description="问题质量评分")
    created_at: str = Field(..., description="创建时间")


class ActivityTimelineResponse(BaseModel):
    """活动时间线响应"""
    activities: List[ActivityItem] = Field(..., description="活动列表")


class RecommendationItem(BaseModel):
    """建议项"""
    type: str = Field(..., description="建议类型 (quality/balance/frequency/success/encouragement)")
    priority: str = Field(..., description="优先级 (high/medium/low)")
    title: str = Field(..., description="标题")
    message: str = Field(..., description="建议内容")
    action: Optional[str] = Field(None, description="操作按钮文本")


class RecommendationsResponse(BaseModel):
    """建议响应"""
    recommendations: List[RecommendationItem] = Field(..., description="建议列表")
