"""智能预处理 Schema"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class QuestionAnalyzeRequest(BaseModel):
    """问题分析请求"""
    question: str = Field(..., min_length=1, max_length=500, description="用户问题")
    user_id: Optional[int] = Field(None, description="用户ID（可选）")


class IntentResult(BaseModel):
    """意图识别结果"""
    intent_type: str = Field(..., description="意图类型：事业/感情/财运/健康/学业/其他")
    confidence: int = Field(..., ge=0, le=100, description="置信度 0-100")
    category: str = Field(..., description="占卜类型：iching/tarot")
    subcategory: str = Field('', description="子类别")
    keywords: List[str] = Field([], description="关键词列表")
    enhanced_question: str = Field('', description="增强后的问题")
    suggestions: List[str] = Field([], description="建议")
    context: Dict[str, Any] = Field({}, description="上下文信息")


class QuestionQualityScore(BaseModel):
    """问题质量评分"""
    score: int = Field(..., ge=0, le=100, description="质量评分 0-100")
    clarity: int = Field(..., ge=0, le=100, description="清晰度")
    specificity: int = Field(..., ge=0, le=100, description="具体性")
    completeness: int = Field(..., ge=0, le=100, description="完整性")
    issues: List[str] = Field([], description="问题列表")
    improvements: List[str] = Field([], description="改进建议")


class QuestionEnhanceResult(BaseModel):
    """问题增强结果"""
    original: str = Field(..., description="原始问题")
    enhanced: str = Field(..., description="增强后的问题")
    changes: List[str] = Field([], description="改动说明")
    quality_before: int = Field(..., description="增强前质量分")
    quality_after: int = Field(..., description="增强后质量分")


class IntentStatistics(BaseModel):
    """意图统计"""
    total_count: int = Field(..., description="总数")
    intent_distribution: Dict[str, int] = Field({}, description="意图分布")
    category_distribution: Dict[str, int] = Field({}, description="类别分布")
    avg_confidence: float = Field(..., description="平均置信度")
    top_keywords: List[tuple] = Field([], description="高频关键词")
