"""每日运势模型"""

from sqlalchemy import Column, Integer, String, Date, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class DailyFortune(Base):
    """每日运势表"""
    __tablename__ = "daily_fortunes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    fortune_date = Column(Date, nullable=False, index=True)
    
    # 基础运势评分
    overall_score = Column(Integer, nullable=False, default=70)  # 0-100
    wealth_score = Column(Integer, nullable=False, default=70)
    career_score = Column(Integer, nullable=False, default=70)
    love_score = Column(Integer, nullable=False, default=70)
    health_score = Column(Integer, nullable=False, default=70)
    
    # 运势内容
    content = Column(Text, nullable=False, default='')
    
    # 幸运指南
    lucky_color = Column(String(50), nullable=False, default='白色')
    lucky_number = Column(Integer, nullable=False, default=8)
    lucky_direction = Column(String(50), nullable=False, default='东')
    lucky_time = Column(String(50), nullable=False, default='辰时(07:00-09:00)')
    
    # 宜忌（存储为逗号分隔的字符串）
    yi = Column(String(200), nullable=False, default='')
    ji = Column(String(200), nullable=False, default='')
    
    # 节气/节日
    solar_term = Column(String(50), default='')
    festival = Column(String(100), default='')
    
    created_at = Column(Date, server_default=func.current_date(), nullable=False)
    
    def __repr__(self):
        return f"<DailyFortune(user_id={self.user_id}, date={self.fortune_date}, score={self.overall_score})>"
