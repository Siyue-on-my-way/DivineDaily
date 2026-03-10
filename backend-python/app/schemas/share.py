"""分享相关的 Schema"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ShareCreateRequest(BaseModel):
    """创建分享请求"""
    expires_days: Optional[int] = Field(None, description="过期天数，None 表示永久")
    is_public: bool = Field(True, description="是否公开")


class ShareResponse(BaseModel):
    """分享响应"""
    share_token: str
    share_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ShareContentResponse(BaseModel):
    """分享内容响应"""
    share_token: str
    question: str
    result: Dict[str, Any]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class ShareStatsResponse(BaseModel):
    """分享统计响应"""
    total_shares: int
    total_views: int
    shares: list[Dict[str, Any]]
    
    class Config:
        from_attributes = True
