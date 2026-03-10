"""用户行为模式模型"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class UserPattern(Base):
    """用户行为模式表"""
    __tablename__ = "user_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # 模式类型
    pattern_type = Column(String(50), nullable=False, index=True)
    # 'question_style', 'topic_preference', 'time_preference', 'quality_trend'
    
    # 模式数据（JSONB）
    pattern_data = Column(JSON, nullable=False)
    
    # 统计信息
    frequency = Column(Integer, default=1)  # 出现频率
    confidence = Column(Float, default=0.5)  # 置信度 0-1
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'pattern_type', name='uq_user_pattern_type'),
    )
    
    def __repr__(self):
        return f"<UserPattern(id={self.id}, user_id={self.user_id}, type={self.pattern_type})>"
