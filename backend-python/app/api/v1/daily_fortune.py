"""每日运势路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
from app.core.database import get_db
from app.schemas.divination import DailyFortuneInfo
from app.services.daily_fortune_service import DailyFortuneService
from app.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()


def get_daily_fortune_service(db: AsyncSession = Depends(get_db)) -> DailyFortuneService:
    """获取每日运势服务"""
    return DailyFortuneService(db)


@router.post("/daily_fortune", response_model=DailyFortuneInfo, tags=["运势"])
async def generate_daily_fortune(
    target_date: Optional[str] = Query(None, description="目标日期 YYYY-MM-DD，默认为今天"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: DailyFortuneService = Depends(get_daily_fortune_service)
):
    """
    生成每日运势
    
    - 如果已登录，为当前用户生成
    - 如果未登录，使用访客ID
    - 同一天只生成一次，重复请求返回缓存结果
    """
    user_id = str(current_user.id) if current_user else "guest"
    
    # 解析日期
    if target_date:
        try:
            parsed_date = date.fromisoformat(target_date)
        except ValueError:
            parsed_date = date.today()
    else:
        parsed_date = date.today()
    
    # 生成运势
    fortune = await service.generate_daily_fortune(user_id, parsed_date)
    
    return DailyFortuneInfo(
        score=fortune.score,
        summary=fortune.summary,
        wealth=fortune.wealth,
        career=fortune.career,
        love=fortune.love,
        health=fortune.health,
        lucky_color=fortune.lucky_color,
        lucky_number=fortune.lucky_number,
        lucky_direction=fortune.lucky_direction,
        lucky_time=fortune.lucky_time,
        yi=fortune.yi,
        ji=fortune.ji,
        solar_term=fortune.solar_term,
        festival=fortune.festival,
    )
