"""时间转换路由"""

from fastapi import APIRouter, Depends
from app.schemas.time_convert import Solar2LunarRequest, Lunar2SolarRequest, ConversionResult
from app.services.time_convert_service import TimeConvertService

router = APIRouter()


def get_time_convert_service() -> TimeConvertService:
    """获取时间转换服务"""
    return TimeConvertService()


@router.post("/solar2lunar", response_model=ConversionResult)
async def solar_to_lunar(
    request: Solar2LunarRequest,
    service: TimeConvertService = Depends(get_time_convert_service)
):
    """公历转农历"""
    result = service.solar_to_lunar(request.year, request.month, request.day)
    return ConversionResult(**result)


@router.post("/lunar2solar", response_model=ConversionResult)
async def lunar_to_solar(
    request: Lunar2SolarRequest,
    service: TimeConvertService = Depends(get_time_convert_service)
):
    """农历转公历"""
    result = service.lunar_to_solar(
        request.year,
        request.month,
        request.day,
        request.is_leap_month
    )
    return ConversionResult(**result)
