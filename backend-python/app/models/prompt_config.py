"""Prompt配置模型（Assistant配置）"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class PromptConfig(Base):
    """Prompt配置表（Assistant配置，关联LLM）"""
    __tablename__ = "prompt_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # "易经-结果卡"
    scene = Column(String(50), nullable=False, index=True)  # "divination"/"tarot"/"daily_fortune"
    
    # 关联LLM配置
    llm_config_id = Column(Integer, ForeignKey('llm_configs.id', ondelete='SET NULL'), nullable=True)
    
    # Assistant自己的参数
    temperature = Column(Float, nullable=False, default=0.7)  # 0.0-2.0
    max_tokens = Column(Integer, nullable=False, default=2000)  # 最大token数
    timeout_seconds = Column(Integer, nullable=False, default=30)  # 超时时间（秒）
    
    # Prompt配置
    prompt_type = Column(String(50), nullable=False)  # "answer"/"detail"/"recommendation"
    question_type = Column(String(50), default='')  # "decision"/"relationship"/"career"等
    template = Column(Text, nullable=False)  # Prompt模板
    variables = Column(JSON, nullable=False, default=list)  # 变量列表
    
    is_default = Column(Boolean, default=False, nullable=False)  # 是否为默认配置
    is_enabled = Column(Boolean, default=True, nullable=False)  # 是否启用
    description = Column(Text, default='')  # 描述
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PromptConfig(id={self.id}, name={self.name}, scene={self.scene})>"
