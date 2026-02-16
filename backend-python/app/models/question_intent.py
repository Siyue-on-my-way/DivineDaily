"""智能预处理模型"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class QuestionIntent(Base):
    """问题意图表"""
    __tablename__ = "question_intents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # 可选，用于统计
    
    # 原始问题
    original_question = Column(Text, nullable=False)
    
    # 意图识别结果
    intent_type = Column(String(50), nullable=False, index=True)  # 事业/感情/财运/健康/学业/其他
    confidence = Column(Integer, nullable=False)  # 置信度 0-100
    
    # 问题分类
    category = Column(String(50), nullable=False)  # 占卜类型：iching/tarot
    subcategory = Column(String(50), default='')  # 子类别
    
    # 增强后的问题
    enhanced_question = Column(Text, default='')
    keywords = Column(JSON, nullable=False)  # 关键词列表
    
    # 上下文信息
    context = Column(JSON, default={})  # 额外的上下文信息
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<QuestionIntent(id={self.id}, intent_type={self.intent_type})>"
