"""方位推荐服务 - 八卦方位智能推荐系统"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class OrientationOption(BaseModel):
    """方位选项"""
    key: str
    label: str


class OrientationRecommendRequest(BaseModel):
    """方位推荐请求"""
    version: str  # CN, Global, TAROT
    event_type: str  # decision, career, relationship等
    question: str
    user_id: Optional[str] = None


class OrientationRecommendResponse(BaseModel):
    """方位推荐响应"""
    recommended_key: str
    recommended_label: str
    reason: str
    options: List[OrientationOption]
    tolerance_deg: int = 15


class OrientationService:
    """方位推荐服务 - 基于八卦和塔罗的方位系统"""
    
    # 八卦方位数据（中国版）
    BAGUA_ORIENTATIONS = [
        {"key": "E", "label": "东方（震）", "trigram": "震", "element": "木", "meaning": "行动与开启"},
        {"key": "SE", "label": "东南（巽）", "trigram": "巽", "element": "木", "meaning": "机缘与变通"},
        {"key": "S", "label": "南方（离）", "trigram": "离", "element": "火", "meaning": "明照与启示"},
        {"key": "SW", "label": "西南（坤）", "trigram": "坤", "element": "土", "meaning": "包容与承载"},
        {"key": "W", "label": "西方（兑）", "trigram": "兑", "element": "金", "meaning": "言说与和悦"},
        {"key": "NW", "label": "西北（乾）", "trigram": "乾", "element": "金", "meaning": "权威与进取"},
        {"key": "N", "label": "北方（坎）", "trigram": "坎", "element": "水", "meaning": "沉潜与内观"},
        {"key": "NE", "label": "东北（艮）", "trigram": "艮", "element": "土", "meaning": "稳固与沉淀"},
    ]
    
    # 塔罗方位数据（国际版）
    TAROT_ORIENTATIONS = [
        {"key": "E", "label": "East (Air / Swords)", "element": "Air", "meaning": "clarity and thinking"},
        {"key": "S", "label": "South (Fire / Wands)", "element": "Fire", "meaning": "momentum and ambition"},
        {"key": "W", "label": "West (Water / Cups)", "element": "Water", "meaning": "emotions and connection"},
        {"key": "N", "label": "North (Earth / Pentacles)", "element": "Earth", "meaning": "practical steps"},
    ]
    
    @staticmethod
    def recommend_orientation(request: OrientationRecommendRequest) -> OrientationRecommendResponse:
        """
        推荐方位
        
        Args:
            request: 方位推荐请求
        
        Returns:
            OrientationRecommendResponse: 推荐结果
        """
        if request.version == "CN":
            return OrientationService._recommend_bagua(request)
        else:
            return OrientationService._recommend_tarot(request)
    
    @staticmethod
    def _recommend_bagua(request: OrientationRecommendRequest) -> OrientationRecommendResponse:
        """
        基于八卦的方位推荐（中国版）
        
        推荐逻辑：
        1. 根据event_type确定基础方位
        2. 根据问题关键词进行微调
        3. 返回推荐方位和理由
        """
        # 构建选项列表
        options = [
            OrientationOption(key=item["key"], label=item["label"])
            for item in OrientationService.BAGUA_ORIENTATIONS
        ]
        
        # 默认推荐：东方（震）- 行动与开启
        recommended_key = "E"
        reason = "难以归类时取东方（震），取'行动与开启'之象。"
        
        # 问题文本（转小写便于匹配）
        q = request.question.lower().strip()
        
        # 第一层：根据事件类型确定基础方位
        if request.event_type == "decision":
            recommended_key = "E"
            reason = "此事偏'行动与开启'，取东方（震）以助决断。"
        elif request.event_type == "career":
            recommended_key = "NW"
            reason = "此事关乎事业目标与掌控，取西北（乾）以应'权威与进取'。"
        elif request.event_type == "relationship":
            recommended_key = "W"
            reason = "此事偏沟通与关系互动，取西方（兑）以应'言说与和悦'。"
        elif request.event_type == "fortune":
            recommended_key = "S"
            reason = "此事求运势指引，取南方（离）以明照前路。"
        elif request.event_type == "knowledge":
            recommended_key = "S"
            reason = "此事求知识启示，取南方（离）以明照智慧。"
        
        # 第二层：根据问题关键词进行微调（优先级更高）
        # 学习、考试、启示 → 南方（离）
        if any(keyword in q for keyword in ["学习", "考试", "看清", "启示", "明白", "理解"]):
            recommended_key = "S"
            reason = "此事偏'看清与求启示'，取南方（离）以明照。"
        
        # 止损、休息、内观 → 北方（坎）
        elif any(keyword in q for keyword in ["止损", "休息", "焦虑", "内观", "冷静", "沉淀"]):
            recommended_key = "N"
            reason = "此事宜先止损休整，取北方（坎）以沉潜内观。"
        
        # 规划、稳定 → 东北（艮）
        elif any(keyword in q for keyword in ["规划", "稳", "沉淀", "积累", "基础"]):
            recommended_key = "NE"
            reason = "此事宜规划沉淀，取东北（艮）以稳固。"
        
        # 机缘、扩展、变通 → 东南（巽）
        elif any(keyword in q for keyword in ["机缘", "扩展", "变通", "灵活", "顺势"]):
            recommended_key = "SE"
            reason = "此事偏机缘与灵活变通，取东南（巽）以顺势而入。"
        
        # 包容、承载、母性 → 西南（坤）
        elif any(keyword in q for keyword in ["包容", "承载", "母亲", "家庭", "养育"]):
            recommended_key = "SW"
            reason = "此事需包容承载，取西南（坤）以厚德载物。"
        
        # 找到对应的label
        recommended_label = OrientationService._find_label(options, recommended_key)
        
        return OrientationRecommendResponse(
            recommended_key=recommended_key,
            recommended_label=recommended_label,
            reason=reason,
            options=options,
            tolerance_deg=15
        )
    
    @staticmethod
    def _recommend_tarot(request: OrientationRecommendRequest) -> OrientationRecommendResponse:
        """
        基于塔罗的方位推荐（国际版）
        
        推荐逻辑：
        1. 根据event_type确定基础方位
        2. 根据问题关键词进行微调
        3. 返回推荐方位和理由
        """
        # 构建选项列表
        options = [
            OrientationOption(key=item["key"], label=item["label"])
            for item in OrientationService.TAROT_ORIENTATIONS
        ]
        
        # 默认推荐：东方（风/宝剑）- 清晰思考
        recommended_key = "E"
        reason = "When it's unclear, face East to seek clarity."
        
        # 问题文本（转小写便于匹配）
        q = request.question.lower().strip()
        
        # 第一层：根据事件类型确定基础方位
        if request.event_type == "decision":
            recommended_key = "E"
            reason = "Face East (Air) to sharpen thinking and decision-making."
        elif request.event_type == "career":
            recommended_key = "S"
            reason = "Face South (Fire) to boost momentum and ambition."
        elif request.event_type == "relationship":
            recommended_key = "W"
            reason = "Face West (Water) to soften emotions and support connection."
        
        # 第二层：根据问题关键词进行微调
        # 金钱、财务、身体、健康 → 北方（土/星币）
        if any(keyword in q for keyword in ["money", "finance", "body", "health", "practical"]):
            recommended_key = "N"
            reason = "Face North (Earth) to ground the situation into practical steps."
        
        # 找到对应的label
        recommended_label = OrientationService._find_label(options, recommended_key)
        
        return OrientationRecommendResponse(
            recommended_key=recommended_key,
            recommended_label=recommended_label,
            reason=reason,
            options=options,
            tolerance_deg=15
        )
    
    @staticmethod
    def _find_label(options: List[OrientationOption], key: str) -> str:
        """查找方位的label"""
        for option in options:
            if option.key == key:
                return option.label
        return options[0].label if options else key
    
    @staticmethod
    def get_orientation_detail(key: str, version: str = "CN") -> Dict:
        """
        获取方位的详细信息
        
        Args:
            key: 方位键（E, SE, S等）
            version: 版本（CN或Global）
        
        Returns:
            Dict: 方位详细信息
        """
        orientations = (
            OrientationService.BAGUA_ORIENTATIONS 
            if version == "CN" 
            else OrientationService.TAROT_ORIENTATIONS
        )
        
        for item in orientations:
            if item["key"] == key:
                return item
        
        return orientations[0] if orientations else {}
    
    @staticmethod
    def get_all_orientations(version: str = "CN") -> List[Dict]:
        """
        获取所有方位信息
        
        Args:
            version: 版本（CN或Global）
        
        Returns:
            List[Dict]: 所有方位信息
        """
        return (
            OrientationService.BAGUA_ORIENTATIONS 
            if version == "CN" 
            else OrientationService.TAROT_ORIENTATIONS
        )

