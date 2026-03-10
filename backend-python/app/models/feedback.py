"""占卜反馈模型"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, CheckConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class DivinationFeedback(Base):
    """占卜反馈表"""
    __tablename__ = "divination_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # 反馈类型
    feedback_type = Column(String(50), nullable=False, index=True)
    # 'quality', 'accuracy', 'helpfulness'
    
    # 评分（1-5）
    rating = Column(Integer, nullable=False)
    
    # 文字反馈
    comment = Column(Text)
    
    # 标签
    tags = Column(JSON)  # ['准确', '有帮助', '不够具体']
    
    # 是否有用
    is_helpful = Column(Boolean)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    def __repr__(self):
        return f"<DivinationFeedback(id={self.id}, session_id={self.session_id}, rating={self.rating})>"
