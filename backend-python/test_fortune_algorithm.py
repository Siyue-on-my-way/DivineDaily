"""测试运势算法服务"""

import sys
from datetime import date, datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.fortune_algorithm_service import FortuneAlgorithmService
from app.utils.calendar import CalendarConverter


def test_wuxing_calculation():
    """测试五行计算"""
    print("=" * 60)
    print("测试五行计算")
    print("=" * 60)
    
    # 测试用户五行
    birth_date = date(1990, 5, 15)
    user_wuxing = FortuneAlgorithmService.get_user_wuxing(birth_date)
    print(f"出生日期: {birth_date}")
    print(f"用户五行: {user_wuxing}")
    
    # 测试日五行
    ganzhi_day = "甲子"
    day_wuxing = FortuneAlgorithmService.get_day_wuxing(ganzhi_day)
    print(f"日干支: {ganzhi_day}")
    print(f"日五行: {day_wuxing}")
    
    # 测试五行评分
    score = FortuneAlgorithmService.calculate_wuxing_score(user_wuxing, day_wuxing)
    print(f"五行评分: {score}")
    print()


def test_animal_calculation():
    """测试生肖计算"""
    print("=" * 60)
    print("测试生肖计算")
    print("=" * 60)
    
    user_animal = "龙"
    day_animal = "鼠"
    
    score = FortuneAlgorithmService.calculate_animal_score(user_animal, day_animal)
    print(f"用户生肖: {user_animal}")
    print(f"日生肖: {day_animal}")
    print(f"生肖评分: {score:+d}")
    
    # 测试相冲
    day_animal_conflict = "狗"
    score_conflict = FortuneAlgorithmService.calculate_animal_score(user_animal, day_animal_conflict)
    print(f"\n用户生肖: {user_animal}")
    print(f"日生肖（相冲）: {day_animal_conflict}")
    print(f"生肖评分: {score_conflict:+d}")
    print()


def test_overall_score():
    """测试综合评分"""
    print("=" * 60)
    print("测试综合评分")
    print("=" * 60)
    
    user_animal = "龙"
    user_wuxing = "金"
    day_animal = "鼠"
    day_wuxing = "水"
    solar_term = "立春"
    
    score = FortuneAlgorithmService.calculate_overall_score(
        user_animal, user_wuxing, day_animal, day_wuxing, solar_term
    )
    
    print(f"用户生肖: {user_animal}, 五行: {user_wuxing}")
    print(f"日生肖: {day_animal}, 五行: {day_wuxing}")
    print(f"节气: {solar_term}")
    print(f"综合评分: {score}")
    print()


def test_lucky_guide():
    """测试幸运指南"""
    print("=" * 60)
    print("测试幸运指南")
    print("=" * 60)
    
    user_animal = "龙"
    user_wuxing = "金"
    day_animal = "鼠"
    day_wuxing = "水"
    ganzhi_day = "甲子"
    
    lucky_color = FortuneAlgorithmService.get_lucky_color(user_wuxing, day_wuxing)
    lucky_number = FortuneAlgorithmService.get_lucky_number(ganzhi_day)
    lucky_direction = FortuneAlgorithmService.get_lucky_direction(user_animal, day_animal)
    lucky_time = FortuneAlgorithmService.get_lucky_time(ganzhi_day)
    
    print(f"幸运颜色: {lucky_color}")
    print(f"幸运数字: {lucky_number}")
    print(f"幸运方位: {lucky_direction}")
    print(f"幸运时辰: {lucky_time}")
    print()


def test_yi_ji():
    """测试宜忌"""
    print("=" * 60)
    print("测试宜忌")
    print("=" * 60)
    
    fortune_date = date.today()
    user_animal = "龙"
    day_animal = "鼠"
    solar_term = "立春"
    
    yi, ji = FortuneAlgorithmService.calculate_yi_ji(
        fortune_date, user_animal, day_animal, solar_term
    )
    
    print(f"日期: {fortune_date}")
    print(f"用户生肖: {user_animal}")
    print(f"日生肖: {day_animal}")
    print(f"节气: {solar_term}")
    print(f"宜: {', '.join(yi)}")
    print(f"忌: {', '.join(ji)}")
    print()


def test_full_fortune_generation():
    """测试完整运势生成"""
    print("=" * 60)
    print("测试完整运势生成")
    print("=" * 60)
    
    # 用户信息
    user_animal = "龙"
    user_birth_date = date(1990, 5, 15)
    fortune_date = date.today()
    
    # 获取时间信息
    converter = CalendarConverter()
    time_info = converter.solar_to_lunar(
        fortune_date.year,
        fortune_date.month,
        fortune_date.day
    )
    
    # 生成运势数据
    fortune_data = FortuneAlgorithmService.generate_fortune_data(
        user_animal=user_animal,
        user_birth_date=user_birth_date,
        fortune_date=fortune_date,
        time_info=time_info
    )
    
    print(f"日期: {fortune_date}")
    print(f"农历: {time_info.get('lunar_month_cn', '')}{time_info.get('lunar_day_cn', '')}")
    print(f"干支: {fortune_data['ganzhi_day']}")
    print(f"节气: {fortune_data['solar_term']}")
    print()
    
    print(f"用户生肖: {user_animal}")
    print(f"用户五行: {fortune_data['user_wuxing']}")
    print(f"日五行: {fortune_data['day_wuxing']}")
    print(f"日生肖: {fortune_data['day_animal']}")
    print()
    
    print("【评分】")
    print(f"综合评分: {fortune_data['overall_score']}")
    print(f"财运评分: {fortune_data['wealth_score']}")
    print(f"事业评分: {fortune_data['career_score']}")
    print(f"感情评分: {fortune_data['love_score']}")
    print(f"健康评分: {fortune_data['health_score']}")
    print()
    
    print("【幸运指南】")
    print(f"幸运颜色: {fortune_data['lucky_color']}")
    print(f"幸运数字: {fortune_data['lucky_number']}")
    print(f"幸运方位: {fortune_data['lucky_direction']}")
    print(f"幸运时辰: {fortune_data['lucky_time']}")
    print()
    
    print("【宜忌】")
    print(f"宜: {', '.join(fortune_data['yi'])}")
    print(f"忌: {', '.join(fortune_data['ji'])}")
    print()


if __name__ == "__main__":
    test_wuxing_calculation()
    test_animal_calculation()
    test_overall_score()
    test_lucky_guide()
    test_yi_ji()
    test_full_fortune_generation()
    
    print("=" * 60)
    print("所有测试完成！")
    print("=" * 60)

