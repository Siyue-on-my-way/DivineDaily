"""系统配置模型"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False)  # string/int/bool/json
    category = Column(String(50), nullable=False, index=True)  # system/llm/divination/notification
    description = Column(Text, default='')
    is_public = Column(Boolean, default=False)  # 是否对外公开
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SystemConfig(key={self.key}, category={self.category})>"


class PromptTemplate(Base):
    """Prompt 模板表"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    template = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # iching/tarot/fortune
    variables = Column(JSON, nullable=False)  # 模板变量列表
    description = Column(Text, default='')
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PromptTemplate(name={self.name}, category={self.category})>"


class SystemStatistics(Base):
    """系统统计表"""
    __tablename__ = "system_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Integer, nullable=False)
    metric_data = Column(JSON, default={})  # 详细数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SystemStatistics(metric_name={self.metric_name}, date={self.date})>"
