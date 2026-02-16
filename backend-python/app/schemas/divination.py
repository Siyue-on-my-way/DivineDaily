"""占卜相关的 Pydantic 模式"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HexagramInfo(BaseModel):
    """卦象信息"""
    number: int = Field(..., description="卦序号（1-64）")
    name: str = Field(..., description="卦名")
    upper_trigram: str = Field(..., description="上卦")
    lower_trigram: str = Field(..., description="下卦")
    outcome: str = Field(..., description="吉凶判断")
    summary: str = Field(..., description="卦辞摘要")
    wuxing: str = Field(..., description="五行")
    changing_lines: Optional[List[int]] = Field(None, description="变爻位置")


class TarotCard(BaseModel):
    """塔罗牌"""
    name: str = Field(..., description="牌名")
    name_en: Optional[str] = Field(None, description="英文名")
    position: str = Field(..., description="位置（如：过去、现在、未来）")
    is_reversed: bool = Field(False, description="是否逆位")
    meaning: Optional[str] = Field(None, description="牌义")


class RecommendationItem(BaseModel):
    """推荐项"""
    content: str = Field(..., description="推荐内容")
    reason: str = Field(..., description="推荐理由")


class DailyFortuneInfo(BaseModel):
    """每日运势信息"""
    score: int = Field(..., ge=0, le=100, description="综合评分")
    summary: str = Field(..., description="运势概述")
    wealth: str = Field(..., description="财运")
    career: str = Field(..., description="事业")
    love: str = Field(..., description="感情")
    health: str = Field(..., description="健康")
    lucky_color: str = Field(..., description="幸运色")
    lucky_number: str = Field(..., description="幸运数字")
    lucky_direction: str = Field(..., description="幸运方位")
    lucky_time: str = Field(..., description="幸运时辰")
    yi: List[str] = Field(default_factory=list, description="宜")
    ji: List[str] = Field(default_factory=list, description="忌")
    solar_term: str = Field("", description="节气")
    festival: str = Field("", description="节日")


class DivinationResult(BaseModel):
    """占卜结果"""
    session_id: str
    outcome: Optional[str] = None  # 吉/凶/平
    title: Optional[str] = None
    spread: Optional[str] = None
    cards: Optional[List[TarotCard]] = None
    
    # 结果内容
    summary: str = Field(..., description="简要结果")
    detail: str = Field(..., description="详细解释")
    
    # 结构化数据
    hexagram_info: Optional[HexagramInfo] = None
    recommendations: Optional[List[RecommendationItem]] = None
    daily_fortune: Optional[DailyFortuneInfo] = None
    
    needs_follow_up: bool = False
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "uuid-here",
                "outcome": "吉",
                "summary": "此卦大吉，诸事顺利",
                "detail": "详细的卦象解释...",
                "hexagram_info": {
                    "number": 1,
                    "name": "乾",
                    "upper_trigram": "乾",
                    "lower_trigram": "乾",
                    "outcome": "吉",
                    "summary": "元亨利贞",
                    "wuxing": "金",
                    "changing_lines": []
                },
                "needs_follow_up": False,
                "created_at": "2026-02-13T12:00:00"
            }
        }


class CreateDivinationRequest(BaseModel):
    """创建占卜请求"""
    user_id: str = Field(..., description="用户ID")
    question: str = Field(..., min_length=1, max_length=500, description="占卜问题")
    event_type: Optional[str] = Field(None, description="事件类型")
    version: str = Field("CN", description="版本（CN/TAROT）")
    orientation: Optional[str] = Field(None, description="方位")
    spread: Optional[str] = Field(None, description="牌阵类型")
    intent: Optional[str] = Field(None, description="意图类型")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class DivinationSession(BaseModel):
    """占卜会话"""
    id: str
    user_id: str
    version: str
    question: str
    event_type: Optional[str] = None
    orientation: Optional[str] = None
    spread: Optional[str] = None
    status: str
    follow_up_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
