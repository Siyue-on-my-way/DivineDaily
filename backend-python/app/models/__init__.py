"""数据模型"""

from app.models.user import User, UserSession, UserRole
from app.models.user_profile import UserProfile
from app.models.divination import DivinationSession, DivinationResult
from app.models.daily_fortune import DailyFortune
from app.models.question_intent import QuestionIntent
from app.models.system_config import SystemConfig, PromptTemplate, SystemStatistics

__all__ = [
    'User', 'UserSession', 'UserRole', 
    'UserProfile', 
    'DivinationSession', 'DivinationResult',
    'DailyFortune', 
    'QuestionIntent',
    'SystemConfig', 'PromptTemplate', 'SystemStatistics'
]
