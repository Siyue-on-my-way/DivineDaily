"""方位推荐服务"""

from typing import Dict, List


class OrientationService:
    """方位推荐服务"""
    
    # 易经八卦方位
    ICHING_ORIENTATIONS = [
        {"key": "E", "label": "东方（震）", "element": "木", "meaning": "行动与开启"},
        {"key": "SE", "label": "东南（巽）", "element": "木", "meaning": "机缘与变通"},
        {"key": "S", "label": "南方（离）", "element": "火", "meaning": "看清与启示"},
        {"key": "SW", "label": "西南（坤）", "element": "土", "meaning": "包容与承载"},
        {"key": "W", "label": "西方（兑）", "element": "金", "meaning": "言说与和悦"},
        {"key": "NW", "label": "西北（乾）", "element": "金", "meaning": "权威与进取"},
        {"key": "N", "label": "北方（坎）", "element": "水", "meaning": "沉潜与内观"},
        {"key": "NE", "label": "东北（艮）", "element": "土", "meaning": "规划与沉淀"},
    ]
    
    # 塔罗四元素方位
    TAROT_ORIENTATIONS = [
        {"key": "E", "label": "East (Air / Swords)", "element": "Air", "meaning": "Clarity"},
        {"key": "S", "label": "South (Fire / Wands)", "element": "Fire", "meaning": "Passion"},
        {"key": "W", "label": "West (Water / Cups)", "element": "Water", "meaning": "Emotion"},
        {"key": "N", "label": "North (Earth / Pentacles)", "element": "Earth", "meaning": "Stability"},
    ]
    
    def recommend_orientation(self, question: str, version: str = "CN", event_type: str = "") -> Dict:
        """推荐方位"""
        
        if version == "TAROT":
            return self._recommend_tarot(question, event_type)
        else:
            return self._recommend_iching(question, event_type)
    
    def _recommend_iching(self, question: str, event_type: str) -> Dict:
        """推荐易经方位"""
        
        recommended_key = "E"  # 默认东方
        reason = "难以归类时取东方（震），取"行动与开启"之象。"
        
        # 根据事件类型推荐
        if event_type == "decision":
            recommended_key = "E"
            reason = "此事偏"行动与开启"，取东方（震）以助决断。"
        elif event_type == "career":
            recommended_key = "NW"
            reason = "此事关乎事业目标与掌控，取西北（乾）以应"权威与进取"。"
        elif event_type == "relationship":
            recommended_key = "W"
            reason = "此事偏沟通与关系互动，取西方（兑）以应"言说与和悦"。"
        
        # 根据关键词推荐
        if any(kw in question for kw in ["学习", "考试", "看清", "启示"]):
            recommended_key = "S"
            reason = "此事偏"看清与求启示"，取南方（离）以明照。"
        elif any(kw in question for kw in ["止损", "休息", "焦虑", "内观"]):
            recommended_key = "N"
            reason = "此事宜先止损休整，取北方（坎）以沉潜内观。"
        elif any(kw in question for kw in ["规划", "稳", "沉淀"]):
            recommended_key = "NE"
            reason = "此事宜规划沉淀，取东北（艮）以稳固。"
        elif any(kw in question for kw in ["机缘", "扩展", "变通"]):
            recommended_key = "SE"
            reason = "此事偏机缘与灵活变通，取东南（巽）以顺势而入。"
        
        # 找到对应的方位信息
        orientation = next((o for o in self.ICHING_ORIENTATIONS if o["key"] == recommended_key), self.ICHING_ORIENTATIONS[0])
        
        return {
            "recommended_key": recommended_key,
            "recommended_label": orientation["label"],
            "reason": reason,
            "options": self.ICHING_ORIENTATIONS,
            "tolerance_deg": 15
        }
    
    def _recommend_tarot(self, question: str, event_type: str) -> Dict:
        """推荐塔罗方位"""
        
        recommended_key = "E"  # 默认东方
        reason = "When it's unclear, face East to seek clarity."
        
        # 根据事件类型推荐
        if event_type == "decision":
            recommended_key = "E"
            reason = "Face East (Air) to sharpen thinking and decision-making."
        elif event_type == "career":
            recommended_key = "S"
            reason = "Face South (Fire) to boost momentum and ambition."
        elif event_type == "relationship":
            recommended_key = "W"
            reason = "Face West (Water) to soften emotions and support connection."
        
        # 根据关键词推荐
        if any(kw in question.lower() for kw in ["money", "finance", "body", "health"]):
            recommended_key = "N"
            reason = "Face North (Earth) to ground the situation into practical steps."
        
        # 找到对应的方位信息
        orientation = next((o for o in self.TAROT_ORIENTATIONS if o["key"] == recommended_key), self.TAROT_ORIENTATIONS[0])
        
        return {
            "recommended_key": recommended_key,
            "recommended_label": orientation["label"],
            "reason": reason,
            "options": self.TAROT_ORIENTATIONS,
            "tolerance_deg": 15
        }
