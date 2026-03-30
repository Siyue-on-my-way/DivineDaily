"""分享相关数据模型"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class DivinationShare(Base):
    """占卜分享记录"""
    
    __tablename__ = "divination_shares"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("divination_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    share_token = Column(String(32), unique=True, nullable=False, index=True)
    share_url = Column(Text, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    session = relationship("DivinationSession", back_populates="shares")
    
    def __repr__(self):
        return f"<DivinationShare(id={self.id}, token={self.share_token}, views={self.view_count})>"
    
    def is_expired(self) -> bool:
        """检查分享是否已过期（兼容 naive/aware datetime）"""
        if self.expires_at is None:
            return False

        expires_at = self.expires_at

        # aware datetime：使用 UTC aware now 比较
        if expires_at.tzinfo is not None:
            return datetime.now(timezone.utc) > expires_at

        # naive datetime：保持 naive 比较，避免 TypeError
        return datetime.utcnow() > expires_at
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        self.updated_at = datetime.utcnow()
