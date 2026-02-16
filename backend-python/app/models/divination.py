"""占卜会话模型"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class DivinationSession(Base):
    """占卜会话表"""
    __tablename__ = "divination_sessions"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(50), nullable=False, index=True)
    version = Column(String(20), nullable=False)  # CN/TAROT
    question = Column(Text, nullable=False)
    event_type = Column(String(50), nullable=True)
    orientation = Column(String(50), nullable=True)
    spread = Column(String(50), nullable=True)
    intent = Column(String(50), nullable=True)
    status = Column(String(20), default="created", nullable=False)  # created/processing/completed/failed
    
    # 结果数据
    result_summary = Column(Text, nullable=True)
    result_detail = Column(Text, nullable=True)
    result_data = Column(JSON, nullable=True)  # 存储结构化结果
    
    follow_up_count = Column(Integer, default=0)
    follow_up_answers = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DivinationSession(id={self.id}, user_id={self.user_id}, version={self.version})>"


class DivinationResult(Base):
    """占卜结果表"""
    __tablename__ = "divination_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), nullable=False, index=True)
    outcome = Column(String(20), nullable=True)  # 吉/凶/平
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    
    # 结构化数据
    hexagram_info = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    daily_fortune = Column(JSON, nullable=True)
    cards = Column(JSON, nullable=True)
    
    needs_follow_up = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DivinationResult(id={self.id}, session_id={self.session_id})>"
