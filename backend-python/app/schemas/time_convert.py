"""时间转换相关的 Pydantic 模式"""

from pydantic import BaseModel, Field
from typing import Optional


class Solar2LunarRequest(BaseModel):
    """公历转农历请求"""
    year: int = Field(..., ge=1900, le=3000, description="公历年份")
    month: int = Field(..., ge=1, le=12, description="公历月份")
    day: int = Field(..., ge=1, le=31, description="公历日期")


class Lunar2SolarRequest(BaseModel):
    """农历转公历请求"""
    year: int = Field(..., ge=1900, le=3000, description="农历年份")
    month: int = Field(..., ge=1, le=12, description="农历月份")
    day: int = Field(..., ge=1, le=30, description="农历日期")
    is_leap_month: bool = Field(False, description="是否闰月")


class ConversionResult(BaseModel):
    """转换结果"""
    # 公历信息
    solar_year: int
    solar_month: int
    solar_day: int
    
    # 农历信息
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap: bool
    lunar_month_cn: str
    lunar_day_cn: str
    
    # 天干地支
    ganzhi_year: str
    ganzhi_month: str
    ganzhi_day: str
    
    # 其他信息
    animal: str
    weekday: int
    weekday_cn: str
    astro: str
    term: str
    is_term: bool
    festival: str
    lunar_festival: str
    is_today: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "solar_year": 2026,
                "solar_month": 2,
                "solar_day": 13,
                "lunar_year": 2026,
                "lunar_month": 1,
                "lunar_day": 26,
                "is_leap": False,
                "lunar_month_cn": "正月",
                "lunar_day_cn": "廿六",
                "ganzhi_year": "丙午",
                "ganzhi_month": "庚寅",
                "ganzhi_day": "甲子",
                "animal": "马",
                "weekday": 5,
                "weekday_cn": "星期五",
                "astro": "水瓶座",
                "term": "",
                "is_term": False,
                "festival": "",
                "lunar_festival": "",
                "is_today": True
            }
        }
