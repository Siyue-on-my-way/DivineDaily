"""问题质量历史模型"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class QuestionQualityHistory(Base):
    """问题质量历史表"""
    __tablename__ = "question_quality_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), index=True)
    user_id = Column(Integer, index=True)
    original_question = Column(Text, nullable=False)
    enhanced_question = Column(Text)
    
    # 质量评分（0-100）
    overall_score = Column(Integer, nullable=False)
    specificity_score = Column(Integer, nullable=False)
    personal_relevance_score = Column(Integer, nullable=False)
    decision_value_score = Column(Integer, nullable=False)
    temporal_relevance_score = Column(Integer, nullable=False)
    
    # 质量因素详情（JSONB）
    quality_factors = Column(JSON)
    
    # 改进建议
    suggestions = Column(JSON)
    
    # 用户反馈
    user_feedback = Column(Integer)  # 1-5星评分
    feedback_comment = Column(Text)
    
    # 是否使用了增强问题
    used_enhanced = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<QuestionQualityHistory(id={self.id}, score={self.overall_score})>"
