"""系统配置 Schema"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SystemConfigBase(BaseModel):
    """系统配置基础模型"""
    key: str = Field(..., max_length=100, description="配置键")
    value: str = Field(..., description="配置值")
    value_type: str = Field(..., description="值类型：string/int/bool/json")
    category: str = Field(..., description="分类：system/llm/divination/notification")
    description: Optional[str] = Field('', description="描述")
    is_public: Optional[bool] = Field(False, description="是否公开")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置"""
    pass


class SystemConfigUpdate(BaseModel):
    """更新系统配置"""
    value: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class SystemConfigInfo(SystemConfigBase):
    """系统配置信息"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PromptTemplateBase(BaseModel):
    """Prompt 模板基础模型"""
    name: str = Field(..., max_length=100, description="模板名称")
    template: str = Field(..., description="模板内容")
    category: str = Field(..., description="分类：iching/tarot/fortune")
    variables: List[str] = Field([], description="变量列表")
    description: Optional[str] = Field('', description="描述")
    is_active: Optional[bool] = Field(True, description="是否启用")


class PromptTemplateCreate(PromptTemplateBase):
    """创建 Prompt 模板"""
    pass


class PromptTemplateUpdate(BaseModel):
    """更新 Prompt 模板"""
    template: Optional[str] = None
    variables: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PromptTemplateInfo(PromptTemplateBase):
    """Prompt 模板信息"""
    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SystemStatisticsInfo(BaseModel):
    """系统统计信息"""
    date: datetime
    metric_name: str
    metric_value: int
    metric_data: Dict[str, Any]
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """仪表盘统计"""
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    total_divinations: int = Field(..., description="总占卜次数")
    total_fortunes: int = Field(..., description="总运势生成次数")
    today_divinations: int = Field(..., description="今日占卜次数")
    today_fortunes: int = Field(..., description="今日运势次数")
    popular_intents: List[Dict[str, Any]] = Field([], description="热门意图")
    popular_categories: List[Dict[str, Any]] = Field([], description="热门类别")
