"""用户管理相关的 Schema 定义"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import re


# ==================== 用户基础 Schema ====================

class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class UserCreateAdmin(UserBase):
    """管理员创建用户"""
    password: str = Field(..., min_length=8, max_length=50)
    role: str = Field(default="normal")
    status: int = Field(default=1)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'normal']:
            raise ValueError('角色必须是 admin 或 normal')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [0, 1]:
            raise ValueError('状态必须是 0 或 1')
        return v


class UserUpdateAdmin(BaseModel):
    """管理员更新用户"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None
    role: Optional[str] = None
    status: Optional[int] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v and v not in ['admin', 'normal']:
            raise ValueError('角色必须是 admin 或 normal')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in [0, 1]:
            raise ValueError('状态必须是 0 或 1')
        return v


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    nickname: Optional[str]
    avatar: Optional[str]
    role: str
    status: int
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserDetailResponse(UserResponse):
    """用户详情响应（包含统计信息）"""
    divination_count: int = 0
    iching_count: int = 0
    tarot_count: int = 0
    fortune_count: int = 0
    last_divination_at: Optional[datetime] = None
    
    # 用户档案信息
    birth_date: Optional[str] = None
    animal: Optional[str] = None
    zodiac_sign: Optional[str] = None


# ==================== 用户操作 Schema ====================

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    new_password: Optional[str] = Field(None, min_length=8, max_length=50)
    generate_random: bool = False
    send_email: bool = False
    
    @validator('new_password')
    def validate_password(cls, v):
        if v:
            if not re.search(r'[A-Z]', v):
                raise ValueError('密码必须包含至少一个大写字母')
            if not re.search(r'[a-z]', v):
                raise ValueError('密码必须包含至少一个小写字母')
            if not re.search(r'\d', v):
                raise ValueError('密码必须包含至少一个数字')
        return v


class ChangeRoleRequest(BaseModel):
    """修改角色请求"""
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'normal']:
            raise ValueError('角色必须是 admin 或 normal')
        return v


class ChangeStatusRequest(BaseModel):
    """修改状态请求"""
    status: int
    reason: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [0, 1]:
            raise ValueError('状态必须是 0 或 1')
        return v


class BatchStatusRequest(BaseModel):
    """批量修改状态请求"""
    user_ids: List[int]
    status: int
    reason: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [0, 1]:
            raise ValueError('状态必须是 0 或 1')
        return v


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    user_ids: List[int]


# ==================== 统计 Schema ====================

class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int
    admin_users: int
    normal_users: int
    active_users: int
    disabled_users: int
    today_new_users: int
    week_new_users: int
    month_new_users: int
    active_7days: int
    active_30days: int


# ==================== 审计日志 Schema ====================

class AuditLogResponse(BaseModel):
    """审计日志响应"""
    id: int
    operator_id: int
    operator_name: str
    action: str
    target_user_id: Optional[int]
    target_username: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


# ==================== 登录历史 Schema ====================

class LoginHistoryResponse(BaseModel):
    """登录历史响应"""
    id: int
    user_id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class LoginHistoryListResponse(BaseModel):
    """登录历史列表响应"""
    history: List[LoginHistoryResponse]
    total: int


# ==================== 占卜历史 Schema ====================

class UserDivinationResponse(BaseModel):
    """用户占卜历史响应"""
    id: str
    version: str
    question: str
    event_type: Optional[str]
    status: str
    result_summary: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDivinationListResponse(BaseModel):
    """用户占卜历史列表响应"""
    divinations: List[UserDivinationResponse]
    total: int

