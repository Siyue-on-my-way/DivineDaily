"""用户档案 Schema"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class UserProfileBase(BaseModel):
    """用户档案基础模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field('未知', description="性别：男/女/未知")
    birth_date: Optional[date] = Field(None, description="公历生日")
    birth_time: Optional[str] = Field(None, max_length=20, description="出生时辰 HH:MM")
    birth_place: Optional[str] = Field(None, max_length=100, description="出生地")
    preferred_divination: Optional[str] = Field('iching', description="偏好占卜方式：iching/tarot")
    notification_enabled: Optional[bool] = Field(True, description="是否启用通知")
    notification_time: Optional[str] = Field('08:00', description="通知时间")
    bio: Optional[str] = Field(None, description="个人简介")
    interests: Optional[str] = Field(None, description="兴趣爱好")


class UserProfileCreate(UserProfileBase):
    """创建用户档案"""
    pass


class UserProfileUpdate(UserProfileBase):
    """更新用户档案"""
    pass


class UserProfileInfo(UserProfileBase):
    """用户档案信息"""
    id: int
    user_id: int
    lunar_birth: str = Field('', description="农历生日")
    animal: str = Field('', description="生肖")
    zodiac_sign: str = Field('', description="星座")
    bazi: str = Field('', description="八字")
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True


class UserWithProfile(BaseModel):
    """用户及档案信息"""
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    nickname: Optional[str]
    avatar: Optional[str]
    role: str
    profile: Optional[UserProfileInfo] = None
    
    class Config:
        from_attributes = True
