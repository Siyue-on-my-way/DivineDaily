"""运势算法服务 - 整合传统算法计算运势"""

import math
from datetime import date, datetime
from typing import Dict, Any, Optional, List, Tuple
from app.utils.calendar import CalendarConverter
from app.utils.calendar_constants import GAN, ZHI


class FortuneAlgorithmService:
    """运势算法服务 - 基于传统算法计算运势评分"""
    
    # 五行生克关系
    WUXING_RELATIONSHIPS = {
        "木": {"火": "生", "土": "克", "金": "被克", "水": "被生", "木": "比和"},
        "火": {"土": "生", "金": "克", "水": "被克", "木": "被生", "火": "比和"},
        "土": {"金": "生", "水": "克", "木": "被克", "火": "被生", "土": "比和"},
        "金": {"水": "生", "木": "克", "火": "被克", "土": "被生", "金": "比和"},
        "水": {"木": "生", "火": "克", "土": "被克", "金": "被生", "水": "比和"},
    }
    
    # 生肖相冲相合
    ANIMAL_CONFLICT = {
        "鼠": "马", "牛": "羊", "虎": "猴", "兔": "鸡",
        "龙": "狗", "蛇": "猪", "马": "鼠", "羊": "牛",
        "猴": "虎", "鸡": "兔", "狗": "龙", "猪": "蛇"
    }
    
    ANIMAL_HARMONY = {
        "鼠": ["龙", "猴"], "牛": ["蛇", "鸡"], "虎": ["马", "狗"], "兔": ["羊", "猪"],
        "龙": ["鼠", "猴"], "蛇": ["牛", "鸡"], "马": ["虎", "狗"], "羊": ["兔", "猪"],
        "猴": ["鼠", "龙"], "鸡": ["牛", "蛇"], "狗": ["虎", "马"], "猪": ["兔", "羊"]
    }
    
    # 纳音五行（简化版）
    NAYIN_WUXING = {
        0: "金", 1: "金", 2: "火", 3: "火", 4: "木", 5: "木",
        6: "土", 7: "土", 8: "金", 9: "金"
    }
    
    # 天干五行
    GAN_WUXING = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
    }
    
    # 地支五行
    ZHI_WUXING = {
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
        "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    
    # 节气加成
    SOLAR_TERM_BONUS = {
        "立春": 15, "立夏": 15, "立秋": 15, "立冬": 15,
        "春分": 10, "夏至": 10, "秋分": 10, "冬至": 10,
        "清明": -5, "寒食": -5
    }
    
    @staticmethod
    def get_user_wuxing(birth_date: date) -> str:
        """根据出生年份计算用户五行（纳音五行简化版）"""
        year = birth_date.year
        return FortuneAlgorithmService.NAYIN_WUXING[year % 10]
    
    @staticmethod
    def get_day_wuxing(ganzhi_day: str) -> str:
        """根据日干支获取日五行"""
        if len(ganzhi_day) >= 1:
            gan = ganzhi_day[0]
            return FortuneAlgorithmService.GAN_WUXING.get(gan, "土")
        return "土"
    
    @staticmethod
    def get_day_animal(ganzhi_day: str) -> str:
        """根据日干支获取日地支对应的生肖"""
        if len(ganzhi_day) >= 2:
            zhi = ganzhi_day[1]
            zhi_index = ZHI.index(zhi) if zhi in ZHI else 0
            from app.utils.calendar_constants import CHINESE_ZODIAC
            return CHINESE_ZODIAC[zhi_index]
        return "鼠"
    
    @staticmethod
    def calculate_wuxing_score(user_wuxing: str, day_wuxing: str) -> int:
        """
        基于五行生克关系计算评分
        相生: 80-100分
        比和: 60-80分
        相克: 30-60分
        """
        if user_wuxing not in FortuneAlgorithmService.WUXING_RELATIONSHIPS:
            return 60
        
        relationship = FortuneAlgorithmService.WUXING_RELATIONSHIPS[user_wuxing].get(day_wuxing, "比和")
        
        if relationship == "生":
            return 85  # 我生日，消耗能量
        elif relationship == "被生":
            return 90  # 日生我，得到助力
        elif relationship == "比和":
            return 70  # 同类，平稳
        elif relationship == "克":
            return 45  # 我克日，需要努力
        elif relationship == "被克":
            return 40  # 日克我，有压力
        
        return 60
    
    @staticmethod
    def calculate_animal_score(user_animal: str, day_animal: str) -> int:
        """
        基于生肖相冲相合计算评分
        相合: +20分
        相冲: -20分
        其他: 0分
        """
        if user_animal == day_animal:
            return 10  # 同生肖，稳定
        
        # 相冲
        if FortuneAlgorithmService.ANIMAL_CONFLICT.get(user_animal) == day_animal:
            return -20
        
        # 相合
        if day_animal in FortuneAlgorithmService.ANIMAL_HARMONY.get(user_animal, []):
            return 20
        
        return 0
    
    @staticmethod
    def calculate_solar_term_bonus(solar_term: str) -> int:
        """根据节气计算加成"""
        return FortuneAlgorithmService.SOLAR_TERM_BONUS.get(solar_term, 0)
    
    @staticmethod
    def calculate_overall_score(
        user_animal: str,
        user_wuxing: str,
        day_animal: str,
        day_wuxing: str,
        solar_term: str
    ) -> int:
        """
        计算综合运势评分
        基础分: 50
        五行分: ±40
        生肖分: ±20
        节气分: ±15
        """
        base_score = 50
        
        # 五行评分（权重0.4）
        wuxing_score = FortuneAlgorithmService.calculate_wuxing_score(user_wuxing, day_wuxing)
        wuxing_contribution = (wuxing_score - 60) * 0.67  # 转换为±40范围
        
        # 生肖评分
        animal_contribution = FortuneAlgorithmService.calculate_animal_score(user_animal, day_animal)
        
        # 节气加成
        term_bonus = FortuneAlgorithmService.calculate_solar_term_bonus(solar_term)
        
        # 综合评分
        total_score = base_score + wuxing_contribution + animal_contribution + term_bonus
        
        # 限制在0-100范围
        return max(0, min(100, int(total_score)))
    
    @staticmethod
    def calculate_wealth_score(user_wuxing: str, day_wuxing: str) -> int:
        """
        计算财运评分
        财运主要看五行相生相克
        我克者为财
        """
        if user_wuxing not in FortuneAlgorithmService.WUXING_RELATIONSHIPS:
            return 60
        
        relationship = FortuneAlgorithmService.WUXING_RELATIONSHIPS[user_wuxing].get(day_wuxing, "比和")
        
        if relationship == "克":
            return 85  # 我克日，得财
        elif relationship == "被生":
            return 75  # 日生我，有财源
        elif relationship == "生":
            return 55  # 我生日，破财
        elif relationship == "被克":
            return 45  # 日克我，财运差
        else:
            return 65  # 比和，平稳
    
    @staticmethod
    def calculate_career_score(user_animal: str, day_animal: str, day_wuxing: str) -> int:
        """
        计算事业运评分
        事业看生肖和五行综合
        """
        base_score = 60
        
        # 生肖影响
        animal_bonus = FortuneAlgorithmService.calculate_animal_score(user_animal, day_animal)
        
        # 五行影响（简化）
        wuxing_bonus = 0
        if day_wuxing in ["金", "木"]:
            wuxing_bonus = 10  # 金木主事业
        
        total = base_score + animal_bonus + wuxing_bonus
        return max(0, min(100, int(total)))
    
    @staticmethod
    def calculate_love_score(user_wuxing: str, day_wuxing: str, fortune_date: date) -> int:
        """
        计算感情运评分
        感情看五行相生和日期
        """
        if user_wuxing not in FortuneAlgorithmService.WUXING_RELATIONSHIPS:
            return 60
        
        relationship = FortuneAlgorithmService.WUXING_RELATIONSHIPS[user_wuxing].get(day_wuxing, "比和")
        
        base_score = 60
        if relationship == "被生":
            base_score = 80  # 被生，得到关爱
        elif relationship == "生":
            base_score = 75  # 我生，付出关爱
        elif relationship == "比和":
            base_score = 70  # 同类，和谐
        elif relationship == "克" or relationship == "被克":
            base_score = 50  # 相克，有矛盾
        
        # 日期影响（简化：周末加分）
        if fortune_date.weekday() in [5, 6]:
            base_score += 10
        
        return max(0, min(100, int(base_score)))
    
    @staticmethod
    def calculate_health_score(user_wuxing: str, solar_term: str, day_wuxing: str) -> int:
        """
        计算健康运评分
        健康看五行平衡和节气
        """
        base_score = 70
        
        # 节气影响
        if solar_term in ["立春", "立夏", "立秋", "立冬"]:
            base_score += 10  # 四立，阳气旺
        elif solar_term in ["清明", "寒食"]:
            base_score -= 10  # 需注意健康
        
        # 五行影响
        if user_wuxing not in FortuneAlgorithmService.WUXING_RELATIONSHIPS:
            return base_score
        
        relationship = FortuneAlgorithmService.WUXING_RELATIONSHIPS[user_wuxing].get(day_wuxing, "比和")
        if relationship == "被生":
            base_score += 10  # 得生，健康好
        elif relationship == "被克":
            base_score -= 10  # 被克，需注意
        
        return max(0, min(100, int(base_score)))
    
    @staticmethod
    def get_lucky_color(user_wuxing: str, day_wuxing: str) -> str:
        """根据五行获取幸运颜色"""
        # 优先使用能生我的五行对应颜色
        wuxing_colors = {
            "木": "绿色",
            "火": "红色",
            "土": "黄色",
            "金": "白色",
            "水": "黑色"
        }
        
        # 找到生我的五行
        for wuxing, relationships in FortuneAlgorithmService.WUXING_RELATIONSHIPS.items():
            if relationships.get(user_wuxing) == "生":
                return wuxing_colors.get(wuxing, "白色")
        
        # 默认返回日五行颜色
        return wuxing_colors.get(day_wuxing, "白色")
    
    @staticmethod
    def get_lucky_number(ganzhi_day: str) -> int:
        """根据日干支获取幸运数字"""
        # 使用天干地支的序号计算
        if len(ganzhi_day) >= 2:
            gan = ganzhi_day[0]
            zhi = ganzhi_day[1]
            gan_index = GAN.index(gan) if gan in GAN else 0
            zhi_index = ZHI.index(zhi) if zhi in ZHI else 0
            return ((gan_index + zhi_index) % 9) + 1
        return 8
    
    @staticmethod
    def get_lucky_direction(user_animal: str, day_animal: str) -> str:
        """根据生肖获取幸运方位"""
        # 生肖方位对应
        animal_directions = {
            "鼠": "北", "牛": "东北", "虎": "东北", "兔": "东",
            "龙": "东南", "蛇": "东南", "马": "南", "羊": "西南",
            "猴": "西南", "鸡": "西", "狗": "西北", "猪": "西北"
        }
        
        # 如果日生肖与用户生肖相合，使用日生肖方位
        if day_animal in FortuneAlgorithmService.ANIMAL_HARMONY.get(user_animal, []):
            return animal_directions.get(day_animal, "东")
        
        return animal_directions.get(user_animal, "东")
    
    @staticmethod
    def get_lucky_time(ganzhi_day: str) -> str:
        """根据日干支获取幸运时辰"""
        if len(ganzhi_day) >= 2:
            zhi = ganzhi_day[1]
            zhi_index = ZHI.index(zhi) if zhi in ZHI else 0
            
            # 时辰对应
            time_periods = [
                "子时(23:00-01:00)", "丑时(01:00-03:00)", "寅时(03:00-05:00)",
                "卯时(05:00-07:00)", "辰时(07:00-09:00)", "巳时(09:00-11:00)",
                "午时(11:00-13:00)", "未时(13:00-15:00)", "申时(15:00-17:00)",
                "酉时(17:00-19:00)", "戌时(19:00-21:00)", "亥时(21:00-23:00)"
            ]
            
            # 使用三合时辰
            lucky_index = (zhi_index + 4) % 12
            return time_periods[lucky_index]
        
        return "辰时(07:00-09:00)"
    
    @staticmethod
    def calculate_yi_ji(
        fortune_date: date,
        user_animal: str,
        day_animal: str,
        solar_term: str
    ) -> Tuple[List[str], List[str]]:
        """
        计算宜忌
        返回: (宜列表, 忌列表)
        """
        yi = []
        ji = []
        
        # 基于生肖相冲相合
        if day_animal in FortuneAlgorithmService.ANIMAL_HARMONY.get(user_animal, []):
            yi.extend(["出行", "会友", "签约", "开业"])
        elif FortuneAlgorithmService.ANIMAL_CONFLICT.get(user_animal) == day_animal:
            ji.extend(["动土", "嫁娶", "搬家", "开业"])
        
        # 基于节气
        if solar_term in ["立春", "立夏", "立秋", "立冬"]:
            yi.extend(["祈福", "祭祀"])
        elif solar_term == "清明":
            yi.append("祭祀")
            ji.append("嫁娶")
        
        # 基于星期
        weekday = fortune_date.weekday()
        if weekday == 0:  # 周一
            yi.extend(["求职", "面试"])
        elif weekday == 4:  # 周五
            yi.extend(["聚会", "娱乐"])
        elif weekday in [5, 6]:  # 周末
            yi.extend(["休息", "旅游"])
            ji.append("加班")
        
        # 去重
        yi = list(set(yi))
        ji = list(set(ji))
        
        # 如果为空，添加默认值
        if not yi:
            yi = ["祈福", "沐浴", "扫舍"]
        if not ji:
            ji = ["诸事不宜"]
        
        return yi, ji
    
    @staticmethod
    def generate_fortune_data(
        user_animal: str,
        user_birth_date: date,
        fortune_date: date,
        time_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成完整的运势算法数据
        
        Args:
            user_animal: 用户生肖
            user_birth_date: 用户出生日期
            fortune_date: 运势日期
            time_info: 时间信息（包含农历、干支、节气等）
        
        Returns:
            Dict: 包含所有算法计算结果的字典
        """
        # 获取用户五行
        user_wuxing = FortuneAlgorithmService.get_user_wuxing(user_birth_date)
        
        # 获取日期信息
        ganzhi_day = time_info.get("ganzhi_day", "甲子")
        day_wuxing = FortuneAlgorithmService.get_day_wuxing(ganzhi_day)
        day_animal = FortuneAlgorithmService.get_day_animal(ganzhi_day)
        solar_term = time_info.get("term", "")
        
        # 计算各项评分
        overall_score = FortuneAlgorithmService.calculate_overall_score(
            user_animal, user_wuxing, day_animal, day_wuxing, solar_term
        )
        
        wealth_score = FortuneAlgorithmService.calculate_wealth_score(user_wuxing, day_wuxing)
        career_score = FortuneAlgorithmService.calculate_career_score(user_animal, day_animal, day_wuxing)
        love_score = FortuneAlgorithmService.calculate_love_score(user_wuxing, day_wuxing, fortune_date)
        health_score = FortuneAlgorithmService.calculate_health_score(user_wuxing, solar_term, day_wuxing)
        
        # 获取幸运指南
        lucky_color = FortuneAlgorithmService.get_lucky_color(user_wuxing, day_wuxing)
        lucky_number = FortuneAlgorithmService.get_lucky_number(ganzhi_day)
        lucky_direction = FortuneAlgorithmService.get_lucky_direction(user_animal, day_animal)
        lucky_time = FortuneAlgorithmService.get_lucky_time(ganzhi_day)
        
        # 计算宜忌
        yi, ji = FortuneAlgorithmService.calculate_yi_ji(fortune_date, user_animal, day_animal, solar_term)
        
        return {
            "overall_score": overall_score,
            "wealth_score": wealth_score,
            "career_score": career_score,
            "love_score": love_score,
            "health_score": health_score,
            "lucky_color": lucky_color,
            "lucky_number": lucky_number,
            "lucky_direction": lucky_direction,
            "lucky_time": lucky_time,
            "yi": yi,
            "ji": ji,
            "user_wuxing": user_wuxing,
            "day_wuxing": day_wuxing,
            "day_animal": day_animal,
            "solar_term": solar_term,
            "ganzhi_day": ganzhi_day
        }

