"""时间转换服务"""

from datetime import datetime
from typing import Dict, Any
from app.utils.calendar import CalendarConverter


class TimeConvertService:
    """时间转换服务"""
    
    def __init__(self):
        self.converter = CalendarConverter()
    
    def solar_to_lunar(self, year: int, month: int, day: int) -> Dict[str, Any]:
        """公历转农历"""
        return self.converter.solar_to_lunar(year, month, day)
    
    def lunar_to_solar(self, year: int, month: int, day: int, is_leap_month: bool = False) -> Dict[str, Any]:
        """农历转公历"""
        return self.converter.lunar_to_solar(year, month, day, is_leap_month)
    
    def get_daily_info(self, date: datetime) -> Dict[str, Any]:
        """获取指定日期的详细信息（包含农历、节气、节日等）"""
        return self.solar_to_lunar(date.year, date.month, date.day)
    
    def get_solar_term(self, date: datetime) -> str:
        """获取指定日期的节气"""
        info = self.get_daily_info(date)
        return info.get("term", "")
    
    def get_festivals(self, date: datetime) -> list:
        """获取指定日期的节日列表（公历和农历）"""
        info = self.get_daily_info(date)
        festivals = []
        
        if info.get("festival"):
            festivals.append(info["festival"])
        
        if info.get("lunar_festival"):
            festivals.append(info["lunar_festival"])
        
        return festivals
