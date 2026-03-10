"""反馈 Schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional


class DivinationFeedbackRequest(BaseModel):
    """占卜反馈请求"""
    session_id: str = Field(..., description="占卜会话ID")
    feedback_type: str = Field(..., pattern='^(quality|accuracy|helpfulness)$', description="反馈类型")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    comment: Optional[str] = Field(None, max_length=500, description="文字反馈")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    is_helpful: Optional[bool] = Field(None, description="是否有帮助")


class QualityFeedbackRequest(BaseModel):
    """问题质量反馈请求"""
    quality_history_id: int = Field(..., description="质量历史记录ID")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    comment: Optional[str] = Field(None, max_length=500, description="文字反馈")


class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int = Field(..., description="反馈ID")
    message: str = Field(..., description="响应消息")
    success: bool = Field(..., description="是否成功")
