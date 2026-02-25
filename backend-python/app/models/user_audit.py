"""用户审计日志模型"""

from sqlalchemy import Column, Integer, String, DateTime, Text, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class UserAuditLog(Base):
    """用户操作审计日志表"""
    __tablename__ = "user_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, nullable=False, index=True)
    operator_name = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False, index=True)
    target_user_id = Column(Integer, nullable=True, index=True)
    target_username = Column(String(50), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<UserAuditLog(id={self.id}, action={self.action}, operator={self.operator_name})>"


class UserStatusHistory(Base):
    """用户状态变更历史表"""
    __tablename__ = "user_status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    old_status = Column(SmallInteger, nullable=False)
    new_status = Column(SmallInteger, nullable=False)
    reason = Column(Text, nullable=True)
    operator_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<UserStatusHistory(id={self.id}, user_id={self.user_id}, {self.old_status}->{self.new_status})>"

