"""LLM配置模型"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class LLMConfig(Base):
    """LLM配置表（去除scene字段，实现配置解耦）"""
    __tablename__ = "llm_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # "DeepSeek-V3.1"
    provider = Column(String(50), nullable=False)  # "openai"/"anthropic"/"deepseek"/"local"
    url_type = Column(String(50), nullable=False, default="openai_compatible")  # "openai_compatible"/"custom"
    api_key = Column(Text, nullable=False)  # API密钥
    endpoint = Column(String(500), nullable=False)  # "https://api.deepseek.com/v1"
    model_name = Column(String(100), nullable=False)  # "deepseek-chat"
    
    is_default = Column(Boolean, default=False, nullable=False)  # 是否为默认LLM
    is_enabled = Column(Boolean, default=True, nullable=False)  # 是否启用
    description = Column(Text, default='')  # 描述
    
    # 额外配置（JSON格式）：temperature, max_tokens, timeout等
    extra_config = Column(JSONB, default={}, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<LLMConfig(id={self.id}, name={self.name}, provider={self.provider})>"
