"""农历转换工具"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.utils.calendar_constants import (
    LUNAR_INFO, SOLAR_MONTH, GAN, ZHI, CHINESE_ZODIAC,
    NSTR1, NSTR2, NSTR3, SOLAR_TERM, FESTIVAL, LUNAR_FESTIVAL
)


class CalendarConverter:
    """农历转换器"""
    
    @staticmethod
    def l_year_days(year: int) -> int:
        """返回农历year年一整年的总天数"""
        sum_days = 348
        for i in range(0x8000, 0x8, -1):
            if LUNAR_INFO[year - 1900] & i:
                sum_days += 1
        return sum_days + CalendarConverter.leap_days(year)
    
    @staticmethod
    def leap_month(year: int) -> int:
        """返回农历year年闰月是哪个月；若year年没有闰月则返回0"""
        return LUNAR_INFO[year - 1900] & 0xf
    
    @staticmethod
    def leap_days(year: int) -> int:
        """返回农历year年闰月的天数 若该年没有闰月则返回0"""
        if CalendarConverter.leap_month(year):
            if LUNAR_INFO[year - 1900] & 0x10000:
                return 30
            return 29
        return 0
    
    @staticmethod
    def month_days(year: int, month: int) -> int:
        """返回农历year年month月（非闰月）的总天数"""
        if month > 12 or month < 1:
            return -1
        if LUNAR_INFO[year - 1900] & (0x10000 >> month):
            return 30
        return 29
    
    @staticmethod
    def solar_days(year: int, month: int) -> int:
        """返回公历year年month月的天数"""
        if month > 12 or month < 1:
            return -1
        if month == 2:  # 2月份
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 29
            return 28
        return SOLAR_MONTH[month - 1]
    
    @staticmethod
    def to_ganzhi_year(lunar_year: int) -> str:
        """农历年份转换为干支纪年"""
        gan_key = (lunar_year - 3) % 10
        zhi_key = (lunar_year - 3) % 12
        if gan_key == 0:
            gan_key = 10
        if zhi_key == 0:
            zhi_key = 12
        return GAN[gan_key - 1] + ZHI[zhi_key - 1]
    
    @staticmethod
    def to_ganzhi(offset: int) -> str:
        """传入offset偏移量返回干支"""
        return GAN[offset % 10] + ZHI[offset % 12]
    
    @staticmethod
    def to_china_month(month: int) -> str:
        """传入农历数字月份返回汉语表示"""
        if month > 12 or month < 1:
            return ""
        return NSTR3[month - 1] + "月"
    
    @staticmethod
    def to_china_day(day: int) -> str:
        """传入农历日期数字返回汉字表示"""
        if day == 10:
            return "初十"
        elif day == 20:
            return "二十"
        elif day == 30:
            return "三十"
        else:
            day_tens = day // 10
            day_ones = day % 10
            if day_tens >= len(NSTR2):
                day_tens = len(NSTR2) - 1
            if day_ones >= len(NSTR1):
                day_ones = len(NSTR1) - 1
            return NSTR2[day_tens] + NSTR1[day_ones]
    
    @staticmethod
    def get_animal(year: int) -> str:
        """年份转生肖"""
        return CHINESE_ZODIAC[(year - 4) % 12]
    
    @staticmethod
    def to_astro(month: int, day: int) -> str:
        """公历月、日判断所属星座"""
        astro_str = "摩羯水瓶双鱼白羊金牛双子巨蟹狮子处女天秤天蝎射手摩羯"
        arr = [20, 19, 21, 21, 21, 22, 23, 23, 23, 23, 22, 22]
        
        start = month * 2
        if day < arr[month - 1]:
            start -= 2
        
        if start < 0:
            start = 0
        if start >= len(astro_str):
            start = len(astro_str) - 2
        
        return astro_str[start:start + 2] + "座"
    
    @staticmethod
    def solar_to_lunar(year: int, month: int, day: int) -> Dict[str, Any]:
        """公历转农历"""
        # 参数验证
        if year < 1900 or year > 3000:
            raise ValueError("年份超出支持范围（1900-3000）")
        if year == 1900 and month == 1 and day < 31:
            raise ValueError("日期超出支持范围（最早1900年1月31日）")
        
        # 创建日期对象
        obj_date = datetime(year, month, day)
        
        # 计算与1900年1月31日的天数差
        base_date = datetime(1900, 1, 31)
        offset = (obj_date - base_date).days
        
        # 计算农历年
        i = 1900
        temp = 0
        while i < 2101 and offset > 0:
            temp = CalendarConverter.l_year_days(i)
            offset -= temp
            i += 1
        
        if offset < 0:
            offset += temp
            i -= 1
        
        # 判断是否是今天
        now = datetime.now()
        is_today = (now.year == year and now.month == month and now.day == day)
        
        # 计算星期
        weekday = obj_date.weekday() + 1  # Python的weekday()返回0-6，转换为1-7
        if weekday == 7:
            weekday = 0
        weekday_cn = "星期" + NSTR1[weekday if weekday != 0 else 7]
        if weekday == 0:
            weekday = 7
        
        # 农历年
        lunar_year = i
        leap = CalendarConverter.leap_month(i)
        is_leap = False
        
        # 计算农历月
        i = 1
        while i < 13 and offset > 0:
            # 闰月
            if leap > 0 and i == (leap + 1) and not is_leap:
                i -= 1
                is_leap = True
                temp = CalendarConverter.leap_days(lunar_year)
            else:
                temp = CalendarConverter.month_days(lunar_year, i)
            
            # 解除闰月
            if is_leap and i == (leap + 1):
                is_leap = False
            
            offset -= temp
            i += 1
        
        # 闰月导致数组下标重叠取反
        if offset == 0 and leap > 0 and i == leap + 1:
            if is_leap:
                is_leap = False
            else:
                is_leap = True
                i -= 1
        
        if offset < 0:
            offset += temp
            i -= 1
        
        lunar_month = i
        lunar_day = offset + 1
        
        # 天干地支处理
        gz_year = CalendarConverter.to_ganzhi_year(lunar_year)
        
        # 依据12节气修正干支月（简化处理）
        gz_month = CalendarConverter.to_ganzhi((year - 1900) * 12 + month + 11)
        
        # 日柱
        day_base = datetime(year, month, 1)
        base_1900 = datetime(1900, 1, 1)
        day_cyclical = (day_base - base_1900).days + 25567 + 10
        gz_day = CalendarConverter.to_ganzhi(day_cyclical + day - 1)
        
        # 星座
        astro = CalendarConverter.to_astro(month, day)
        
        # 节日
        festival_date = f"{month}-{day}"
        festival_title = FESTIVAL.get(festival_date, "")
        
        lunar_festival_date = f"{lunar_month}-{lunar_day}"
        # 农历节日修正：农历12月小月则29号除夕，大月则30号除夕
        if lunar_month == 12 and lunar_day == 29 and CalendarConverter.month_days(lunar_year, lunar_month) == 29:
            lunar_festival_date = "12-30"
        lunar_festival_title = LUNAR_FESTIVAL.get(lunar_festival_date, "")
        
        # 农历月份中文
        lunar_month_cn = CalendarConverter.to_china_month(lunar_month)
        if is_leap:
            lunar_month_cn = "闰" + lunar_month_cn
        
        return {
            "solar_year": year,
            "solar_month": month,
            "solar_day": day,
            "lunar_year": lunar_year,
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "is_leap": is_leap,
            "lunar_month_cn": lunar_month_cn,
            "lunar_day_cn": CalendarConverter.to_china_day(lunar_day),
            "ganzhi_year": gz_year,
            "ganzhi_month": gz_month,
            "ganzhi_day": gz_day,
            "animal": CalendarConverter.get_animal(lunar_year),
            "weekday": weekday,
            "weekday_cn": weekday_cn,
            "astro": astro,
            "term": "",  # 节气需要更复杂的计算
            "is_term": False,
            "festival": festival_title,
            "lunar_festival": lunar_festival_title,
            "is_today": is_today,
        }
    
    @staticmethod
    def lunar_to_solar(year: int, month: int, day: int, is_leap_month: bool = False) -> Dict[str, Any]:
        """农历转公历"""
        # 参数验证
        if year < 1900 or year > 3000:
            raise ValueError("年份超出支持范围（1900-3000）")
        
        leap_month_num = CalendarConverter.leap_month(year)
        if is_leap_month and leap_month_num != month:
            raise ValueError(f"该年没有闰{month}月")
        
        day_count = CalendarConverter.month_days(year, month)
        if is_leap_month:
            day_count = CalendarConverter.leap_days(year)
        
        if day > day_count:
            raise ValueError(f"日期超出该月范围（最大{day_count}天）")
        
        # 计算农历的时间差
        offset = 0
        for i in range(1900, year):
            offset += CalendarConverter.l_year_days(i)
        
        # 在循环外计算闰月信息，提高效率
        leap = CalendarConverter.leap_month(year)
        is_add = False
        for i in range(1, month):
            # 处理闰月
            if not is_add and leap > 0 and leap <= i:
                offset += CalendarConverter.leap_days(year)
                is_add = True
            offset += CalendarConverter.month_days(year, i)
        
        # 转换闰月农历 需补充该年闰月的前一个月的时差
        if is_leap_month:
            offset += CalendarConverter.month_days(year, month)
        
        # 1900年农历正月一日的公历时间为1900年1月31日
        base_date = datetime(1900, 1, 31)
        target_date = base_date + timedelta(days=offset + day - 1)
        
        # 使用 solar_to_lunar 获取完整信息
        return CalendarConverter.solar_to_lunar(
            target_date.year,
            target_date.month,
            target_date.day
        )
