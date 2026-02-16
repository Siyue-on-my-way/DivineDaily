"""测试时间转换服务"""

import pytest
from datetime import datetime
from app.services.time_convert_service import TimeConvertService


def test_solar_to_lunar():
    """测试公历转农历"""
    service = TimeConvertService()
    
    # 测试 2026年2月13日
    result = service.solar_to_lunar(2026, 2, 13)
    
    assert result["solar_year"] == 2026
    assert result["solar_month"] == 2
    assert result["solar_day"] == 13
    assert result["lunar_year"] == 2026
    assert "lunar_month" in result
    assert "lunar_day" in result
    assert "ganzhi_year" in result
    assert "animal" in result


def test_lunar_to_solar():
    """测试农历转公历"""
    service = TimeConvertService()
    
    # 测试农历 2026年正月初一
    result = service.lunar_to_solar(2026, 1, 1, False)
    
    assert result["lunar_year"] == 2026
    assert result["lunar_month"] == 1
    assert result["lunar_day"] == 1
    assert "solar_year" in result
    assert "solar_month" in result
    assert "solar_day" in result


def test_get_daily_info():
    """测试获取日期详细信息"""
    service = TimeConvertService()
    
    date = datetime(2026, 2, 13)
    result = service.get_daily_info(date)
    
    assert "lunar_month_cn" in result
    assert "lunar_day_cn" in result
    assert "weekday_cn" in result
    assert "astro" in result


def test_get_festivals():
    """测试获取节日"""
    service = TimeConvertService()
    
    # 测试元旦
    date = datetime(2026, 1, 1)
    festivals = service.get_festivals(date)
    
    assert isinstance(festivals, list)
    # 元旦应该有节日
    if festivals:
        assert "元旦" in festivals[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
