"""每日运势模型"""

from sqlalchemy import Column, Integer, String, Date, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class DailyFortune(Base):
    """每日运势表"""
    __tablename__ = "daily_fortunes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # 基础运势
    score = Column(Integer, nullable=False)  # 0-100
    summary = Column(Text, nullable=False)
    
    # 详细建议
    wealth = Column(Text, nullable=False)
    career = Column(Text, nullable=False)
    love = Column(Text, nullable=False)
    health = Column(Text, nullable=False)
    
    # 幸运指南
    lucky_color = Column(String(50), nullable=False)
    lucky_number = Column(String(50), nullable=False)
    lucky_direction = Column(String(50), nullable=False)
    lucky_time = Column(String(50), nullable=False)
    
    # 宜忌
    yi = Column(JSON, nullable=False)  # List[str]
    ji = Column(JSON, nullable=False)  # List[str]
    
    # 节气/节日
    solar_term = Column(String(50), default='')
    festival = Column(String(100), default='')
    
    created_at = Column(Date, server_default=func.current_date(), nullable=False)
    
    def __repr__(self):
        return f"<DailyFortune(user_id={self.user_id}, date={self.date}, score={self.score})>"
