"""每日运势路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
from app.core.database import get_db
from app.schemas.divination import DailyFortuneInfo
from app.services.daily_fortune_service import DailyFortuneService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


def get_daily_fortune_service(db: AsyncSession = Depends(get_db)) -> DailyFortuneService:
    """获取每日运势服务"""
    return DailyFortuneService(db)


@router.post("", response_model=DailyFortuneInfo)
async def generate_daily_fortune(
    target_date: Optional[str] = Query(None, description="目标日期 YYYY-MM-DD，默认为今天"),
    current_user: User = Depends(get_current_user),
    service: DailyFortuneService = Depends(get_daily_fortune_service)
):
    """
    生成每日运势
    
    - 为当前用户生成每日运势
    - 同一天只生成一次，重复请求返回缓存结果
    - 使用传统算法（五行、生肖、节气）+ LLM 生成
    """
    user_id = current_user.id
    
    # 解析日期
    if target_date:
        try:
            parsed_date = date.fromisoformat(target_date)
        except ValueError:
            parsed_date = date.today()
    else:
        parsed_date = date.today()
    
    # 生成运势
    fortune = await service.get_daily_fortune(user_id, parsed_date)
    
    return DailyFortuneInfo(
        overall_score=fortune.overall_score,
        wealth_score=fortune.wealth_score,
        career_score=fortune.career_score,
        love_score=fortune.love_score,
        health_score=fortune.health_score,
        content=fortune.content,
        lucky_color=fortune.lucky_color,
        lucky_number=fortune.lucky_number,
        lucky_direction=fortune.lucky_direction,
        lucky_time=fortune.lucky_time,
        yi=fortune.yi,
        ji=fortune.ji,
        solar_term=fortune.solar_term or "",
        festival=fortune.festival or "",
    )


@router.get("/history", response_model=list[DailyFortuneInfo])
async def get_fortune_history(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(30, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_user),
    service: DailyFortuneService = Depends(get_daily_fortune_service)
):
    """
    获取用户的运势历史记录
    """
    user_id = current_user.id
    
    fortunes = await service.list_user_fortunes(user_id, skip, limit)
    
    return [
        DailyFortuneInfo(
            overall_score=fortune.overall_score,
            wealth_score=fortune.wealth_score,
            career_score=fortune.career_score,
            love_score=fortune.love_score,
            health_score=fortune.health_score,
            content=fortune.content,
            lucky_color=fortune.lucky_color,
            lucky_number=fortune.lucky_number,
            lucky_direction=fortune.lucky_direction,
            lucky_time=fortune.lucky_time,
            yi=fortune.yi,
            ji=fortune.ji,
            solar_term=fortune.solar_term or "",
            festival=fortune.festival or "",
        )
        for fortune in fortunes
    ]
