"""问题分类器"""

from typing import List, Dict, Any
import re


class QuestionType:
    """问题类型常量"""
    RECOMMENDATION = "recommendation"  # 日常推荐类
    DECISION = "decision"              # 决策类
    FORTUNE = "fortune"                # 运势类


class QuestionClassification:
    """问题分类结果"""
    def __init__(self, type: str, confidence: float, keywords: List[str], context: Dict[str, Any]):
        self.type = type
        self.confidence = confidence
        self.keywords = keywords
        self.context = context


class QuestionClassifier:
    """问题分类器"""
    
    def __init__(self):
        self.recommendation_keywords = [
            "吃什么", "去哪", "去哪儿", "看什么", "推荐", "建议", "有什么",
            "吃什么好", "去哪玩", "看什么电影", "听什么", "读什么",
        ]
        self.decision_keywords = [
            "选", "选择", "应该", "哪个", "要不要", "是否", "该不该",
            "去不去", "做不做", "选哪个", "哪个好",
            "工作", "跳槽", "投资", "买房", "结婚", "分手",
        ]
        self.fortune_keywords = [
            "运势", "运程", "运气", "今日", "本周", "本月", "今年",
            "桃花运", "财运", "事业运", "健康运",
        ]
    
    def classify(self, question: str) -> QuestionClassification:
        """分类问题"""
        question = question.strip()
        if not question:
            return QuestionClassification(
                type=QuestionType.RECOMMENDATION,
                confidence=0.5,
                keywords=[],
                context={}
            )
        
        lower_question = question.lower()
        
        # 统计各类关键词匹配数
        recommendation_count = 0
        decision_count = 0
        fortune_count = 0
        matched_keywords = []
        
        # 检查推荐类关键词
        for keyword in self.recommendation_keywords:
            if keyword in question or keyword.lower() in lower_question:
                recommendation_count += 1
                matched_keywords.append(keyword)
        
        # 检查决策类关键词
        for keyword in self.decision_keywords:
            if keyword in question or keyword.lower() in lower_question:
                decision_count += 1
                matched_keywords.append(keyword)
        
        # 检查运势类关键词
        for keyword in self.fortune_keywords:
            if keyword in question or keyword.lower() in lower_question:
                fortune_count += 1
                matched_keywords.append(keyword)
        
        # 确定问题类型
        if decision_count > 0:
            q_type = QuestionType.DECISION
            confidence = self._calculate_confidence(decision_count, len(self.decision_keywords))
        elif fortune_count > 0:
            q_type = QuestionType.FORTUNE
            confidence = self._calculate_confidence(fortune_count, len(self.fortune_keywords))
        elif recommendation_count > 0:
            q_type = QuestionType.RECOMMENDATION
            confidence = self._calculate_confidence(recommendation_count, len(self.recommendation_keywords))
        else:
            # 默认归类为推荐类
            q_type = QuestionType.RECOMMENDATION
            confidence = 0.3
        
        # 提取上下文信息
        context = self._extract_context(question)
        
        return QuestionClassification(
            type=q_type,
            confidence=confidence,
            keywords=matched_keywords,
            context=context
        )
    
    def _calculate_confidence(self, match_count: int, total_keywords: int) -> float:
        """计算置信度"""
        if total_keywords == 0:
            return 0.5
        
        base_confidence = (match_count / total_keywords) * 0.5
        if base_confidence > 0.9:
            return 0.9
        if base_confidence < 0.3:
            return 0.3
        return base_confidence + 0.3  # 基础置信度 + 0.3
    
    def _extract_context(self, question: str) -> Dict[str, Any]:
        """提取上下文信息"""
        context = {}
        
        # 提取公司名
        if "公司" in question or "企业" in question:
            context["has_company"] = True
        
        # 提取行业信息
        industries = ["互联网", "金融", "教育", "医疗", "房地产", "制造业"]
        for industry in industries:
            if industry in question:
                context["industry"] = industry
                break
        
        # 提取选项（A和B）
        if "A" in question and "B" in question:
            context["has_options"] = True
            context["option_count"] = 2
        
        return context
