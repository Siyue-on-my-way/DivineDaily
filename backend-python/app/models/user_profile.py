"""用户档案模型"""

from sqlalchemy import Column, Integer, String, Date, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import date
from app.core.database import Base


class UserProfile(Base):
    """用户档案表"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # 基本信息
    nickname = Column(String(50), default='')
    avatar = Column(String(255), default='')
    gender = Column(String(10), default='未知')  # 男/女/未知
    
    # 生辰信息
    birth_date = Column(Date, nullable=True)  # 公历生日
    birth_time = Column(String(20), default='')  # 出生时辰 HH:MM
    birth_place = Column(String(100), default='')  # 出生地
    
    # 命理信息（自动计算）
    lunar_birth = Column(String(50), default='')  # 农历生日
    animal = Column(String(10), default='')  # 生肖
    zodiac_sign = Column(String(20), default='')  # 星座
    bazi = Column(String(100), default='')  # 八字
    
    # 偏好设置
    preferred_divination = Column(String(20), default='iching')  # iching/tarot
    notification_enabled = Column(Boolean, default=True)
    notification_time = Column(String(10), default='08:00')  # 每日运势推送时间
    
    # 个性化信息
    bio = Column(Text, default='')  # 个人简介
    interests = Column(Text, default='')  # 兴趣爱好
    
    created_at = Column(Date, server_default=func.current_date(), nullable=False)
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.current_date(), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, nickname={self.nickname})>"
