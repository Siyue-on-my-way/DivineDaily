"""问题质量评估 Schemas"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class QuestionQualityRequest(BaseModel):
    """问题质量评估请求"""
    question: str = Field(..., min_length=1, max_length=500, description="待评估的问题")


class QualitySuggestion(BaseModel):
    """质量改进建议"""
    type: str = Field(..., description="建议类型")
    message: str = Field(..., description="建议内容")
    priority: str = Field(..., description="优先级: high/medium/low")


class QuestionQualityResponse(BaseModel):
    """问题质量评估响应"""
    overall_score: int = Field(..., ge=0, le=100, description="综合评分")
    specificity_score: int = Field(..., ge=0, le=100, description="具体性评分")
    personal_relevance_score: int = Field(..., ge=0, le=100, description="个人相关性评分")
    decision_value_score: int = Field(..., ge=0, le=100, description="决策价值评分")
    temporal_relevance_score: int = Field(..., ge=0, le=100, description="时效性评分")
    quality_factors: Dict[str, float] = Field(..., description="质量因素详情")
    suggestions: List[QualitySuggestion] = Field(default_factory=list, description="改进建议")


class QuestionQualityHistoryResponse(BaseModel):
    """问题质量历史响应"""
    id: int
    original_question: str
    enhanced_question: Optional[str] = None
    overall_score: int
    used_enhanced: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
