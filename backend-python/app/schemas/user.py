"""用户相关的 Pydantic 模式"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=6, max_length=50)
    confirm_password: str = Field(..., min_length=6, max_length=50)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次密码不一致')
        return v
    
    @validator('phone', pre=True)
    def validate_phone(cls, v):
        """验证手机号：如果提供了值，必须符合格式；如果为空字符串，转为 None"""
        if v == '' or v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            return None
        # 验证手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @validator('email', pre=True)
    def validate_email(cls, v):
        """验证邮箱：如果为空字符串，转为 None"""
        if v == '' or v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            return None
        return v
    
    @validator('phone')
    def at_least_one_contact(cls, v, values):
        """确保邮箱和手机号至少提供一个"""
        email = values.get('email')
        phone = v
        if not email and not phone:
            raise ValueError('邮箱和手机号至少填写一个')
        return v


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """用户更新模式"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None
    
    @validator('phone', pre=True)
    def validate_phone(cls, v):
        """验证手机号：如果提供了值，必须符合格式；如果为空字符串，转为 None"""
        if v == '' or v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            return None
        # 验证手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class UserResponse(BaseModel):
    """用户响应模式"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: UserRole
    status: int
    last_login_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应模式"""
    token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str
