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
    line_values: Optional[List[int]] = Field(None, description="六爻值（自下而上，6/7/8/9）")


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
    overall_score: int = Field(..., ge=0, le=100, description="综合评分")
    wealth_score: int = Field(..., ge=0, le=100, description="财运评分")
    career_score: int = Field(..., ge=0, le=100, description="事业评分")
    love_score: int = Field(..., ge=0, le=100, description="感情评分")
    health_score: int = Field(..., ge=0, le=100, description="健康评分")
    content: str = Field(..., description="运势内容")
    lucky_color: str = Field(..., description="幸运色")
    lucky_number: int = Field(..., description="幸运数字")
    lucky_direction: str = Field(..., description="幸运方位")
    lucky_time: str = Field(..., description="幸运时辰")
    yi: str = Field("", description="宜（逗号分隔）")
    ji: str = Field("", description="忌（逗号分隔）")
    solar_term: str = Field("", description="节气")
    festival: str = Field("", description="节日")


class YarrowChangeStep(BaseModel):
    """大衍筮法单次变的记录"""
    step_index: int = Field(..., ge=1, le=3, description="第几变（1-3）")
    stalks_before: int = Field(..., description="本变开始前蓍草数")
    left_pile: int = Field(..., description="左手蓍草数")
    right_pile_before_hang: int = Field(..., description="右手蓍草数（挂一前）")
    right_hang_one: int = Field(..., description="挂一数量，固定为1")
    right_pile_after_hang: int = Field(..., description="右手蓍草数（挂一后）")
    left_remainder: int = Field(..., description="左手取四余数（0按4计）")
    right_remainder: int = Field(..., description="右手取四余数（0按4计）")
    removed: int = Field(..., description="本变去除总数")
    stalks_after: int = Field(..., description="本变结束后蓍草数")


class YarrowLineTrace(BaseModel):
    """单爻生成过程"""
    line_index: int = Field(..., ge=1, le=6, description="爻位（1-6，自下而上）")
    initial_stalks: int = Field(..., description="初始蓍草数，通常49")
    changes: List[YarrowChangeStep] = Field(default_factory=list, description="三变过程")
    final_stalks: int = Field(..., description="三变后剩余蓍草数")
    line_value: int = Field(..., description="爻值（6/7/8/9）")
    line_type: str = Field(..., description="爻类型（老阴/少阳/少阴/老阳）")
    is_changing: bool = Field(..., description="是否变爻")


class YarrowProcessTrace(BaseModel):
    """大衍筮法完整过程记录"""
    method: str = Field("dayan_yarrow", description="起卦方法")
    total_stalks: int = Field(50, description="总蓍草数")
    effective_stalks: int = Field(49, description="参与演算蓍草数")
    lines: List[YarrowLineTrace] = Field(default_factory=list, description="六爻过程（自下而上）")


class DivinationResult(BaseModel):
    """占卜结果"""
    session_id: str
    status: Optional[str] = Field(None, description="状态：processing/completed/failed")
    error_code: Optional[str] = Field(None, description="失败错误码")
    error_message: Optional[str] = Field(None, description="失败错误信息")
    retryable: Optional[bool] = Field(None, description="是否可重试")
    outcome: Optional[str] = None  # 吉/凶/平
    title: Optional[str] = None
    spread: Optional[str] = None
    cards: Optional[List[TarotCard]] = None
    
    # 结果内容（processing 状态时可为空）
    summary: Optional[str] = Field(None, description="简要结果")
    detail: Optional[str] = Field(None, description="详细解释")
    
    # 结构化数据
    hexagram_info: Optional[HexagramInfo] = None
    recommendations: Optional[List[RecommendationItem]] = None
    daily_fortune: Optional[DailyFortuneInfo] = None
    yarrow_trace: Optional[YarrowProcessTrace] = Field(None, description="大衍筮法过程记录")
    
    # 问题分析信息
    question_type: Optional[str] = None
    question_intent: Optional[str] = None
    
    needs_follow_up: bool = False
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "uuid-here",
                "status": "completed",
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


class DivinationTaskAccepted(BaseModel):
    """占卜任务已受理响应"""
    accepted: bool = Field(True, description="是否已受理")
    session_id: str = Field(..., description="占卜会话 ID")
    status: str = Field("processing", description="当前状态")
    status_url: str = Field(..., description="查询状态/结果的 API 路径")
    message: str = Field("占卜任务已受理，正在处理中", description="提示信息")
    created_at: datetime
