"""问题质量评估服务"""

import re
from typing import Dict, List
from datetime import datetime


class QuestionQualityService:
    """问题质量评估服务"""
    
    # 关键词权重配置
    SPECIFIC_KEYWORDS = {
        'high': ['具体', '明确', '详细', '什么时候', '如何', '怎样', '哪个', '是否'],
        'medium': ['关于', '有关', '想知道'],
        'low': ['好不好', '行不行', '可以吗']
    }
    
    PERSONAL_KEYWORDS = ['我', '我的', '自己', '本人']
    
    DECISION_KEYWORDS = ['选择', '决定', '要不要', '还是', '应该', '建议']
    
    TEMPORAL_KEYWORDS = {
        'high': ['今天', '明天', '本周', '这个月', '近期'],
        'medium': ['今年', '未来', '将来'],
        'low': ['以后', '有一天']
    }
    
    def evaluate_quality(self, question: str) -> Dict:
        """
        评估问题质量
        
        返回：
        {
            'overall_score': 75,
            'specificity_score': 80,
            'personal_relevance_score': 90,
            'decision_value_score': 70,
            'temporal_relevance_score': 60,
            'quality_factors': {...},
            'suggestions': [...]
        }
        """
        # 1. 具体性评分
        specificity = self._evaluate_specificity(question)
        
        # 2. 个人相关性评分
        personal_relevance = self._evaluate_personal_relevance(question)
        
        # 3. 决策价值评分
        decision_value = self._evaluate_decision_value(question)
        
        # 4. 时效性评分
        temporal_relevance = self._evaluate_temporal_relevance(question)
        
        # 5. 计算综合评分（加权平均）
        overall_score = int(
            specificity * 0.35 +
            personal_relevance * 0.25 +
            decision_value * 0.25 +
            temporal_relevance * 0.15
        )
        
        # 6. 生成改进建议
        suggestions = self._generate_suggestions(
            question, specificity, personal_relevance, 
            decision_value, temporal_relevance
        )
        
        return {
            'overall_score': overall_score,
            'specificity_score': specificity,
            'personal_relevance_score': personal_relevance,
            'decision_value_score': decision_value,
            'temporal_relevance_score': temporal_relevance,
            'quality_factors': {
                'length': len(question),
                'has_question_mark': '？' in question or '?' in question,
                'word_count': len(question.split())
            },
            'suggestions': suggestions
        }
    
    def _evaluate_specificity(self, question: str) -> int:
        """评估具体性（0-100）"""
        score = 50  # 基础分
        
        # 检查高价值关键词
        for keyword in self.SPECIFIC_KEYWORDS['high']:
            if keyword in question:
                score += 10
        
        # 检查中等价值关键词
        for keyword in self.SPECIFIC_KEYWORDS['medium']:
            if keyword in question:
                score += 5
        
        # 检查低价值关键词（扣分）
        for keyword in self.SPECIFIC_KEYWORDS['low']:
            if keyword in question:
                score -= 10
        
        # 问题长度加成
        if len(question) > 20:
            score += 10
        elif len(question) < 10:
            score -= 10
        
        # 是否包含具体名词（简单检测）
        if re.search(r'[A-Z][a-z]+|[\u4e00-\u9fa5]{2,}公司|[\u4e00-\u9fa5]{2,}项目', question):
            score += 10
        
        return max(0, min(100, score))
    
    def _evaluate_personal_relevance(self, question: str) -> int:
        """评估个人相关性（0-100）"""
        score = 50
        
        # 检查第一人称
        personal_count = sum(1 for kw in self.PERSONAL_KEYWORDS if kw in question)
        score += personal_count * 15
        
        # 检查是否是泛泛而谈
        if any(word in question for word in ['大家', '人们', '一般']):
            score -= 20
        
        return max(0, min(100, score))
    
    def _evaluate_decision_value(self, question: str) -> int:
        """评估决策价值（0-100）"""
        score = 50
        
        # 检查决策关键词
        decision_count = sum(1 for kw in self.DECISION_KEYWORDS if kw in question)
        score += decision_count * 12
        
        # 检查是否有明确选项
        if '还是' in question or '或者' in question:
            score += 20
        
        # 检查是否只是知识问答
        if any(word in question for word in ['是什么', '什么是', '为什么']):
            score -= 15
        
        return max(0, min(100, score))
    
    def _evaluate_temporal_relevance(self, question: str) -> int:
        """评估时效性（0-100）"""
        score = 50
        
        # 检查高时效性关键词
        for keyword in self.TEMPORAL_KEYWORDS['high']:
            if keyword in question:
                score += 20
                break
        
        # 检查中等时效性关键词
        for keyword in self.TEMPORAL_KEYWORDS['medium']:
            if keyword in question:
                score += 10
                break
        
        # 检查低时效性关键词
        for keyword in self.TEMPORAL_KEYWORDS['low']:
            if keyword in question:
                score -= 10
        
        return max(0, min(100, score))
    
    def _generate_suggestions(
        self, question: str, specificity: int, 
        personal_relevance: int, decision_value: int, 
        temporal_relevance: int
    ) -> List[Dict]:
        """生成改进建议"""
        suggestions = []
        
        if specificity < 60:
            suggestions.append({
                'type': 'specificity',
                'message': '建议增加更具体的细节，如时间、地点、人物等',
                'priority': 'high'
            })
        
        if personal_relevance < 60:
            suggestions.append({
                'type': 'personal_relevance',
                'message': '建议使用第一人称（我、我的）使问题更具个人相关性',
                'priority': 'medium'
            })
        
        if decision_value < 60:
            suggestions.append({
                'type': 'decision_value',
                'message': '建议明确你需要做出的决策或选择',
                'priority': 'medium'
            })
        
        if temporal_relevance < 60:
            suggestions.append({
                'type': 'temporal_relevance',
                'message': '建议添加时间范围（如"近期"、"本月"）',
                'priority': 'low'
            })
        
        return suggestions
    
    async def save_quality_record(
        self, db, session_id: str, user_id: int,
        original_question: str, enhanced_question: str,
        quality_result: Dict, used_enhanced: bool
    ):
        """保存质量评估记录"""
        from app.models.question_quality import QuestionQualityHistory
        
        record = QuestionQualityHistory(
            session_id=session_id,
            user_id=user_id,
            original_question=original_question,
            enhanced_question=enhanced_question,
            overall_score=quality_result['overall_score'],
            specificity_score=quality_result['specificity_score'],
            personal_relevance_score=quality_result['personal_relevance_score'],
            decision_value_score=quality_result['decision_value_score'],
            temporal_relevance_score=quality_result['temporal_relevance_score'],
            quality_factors=quality_result['quality_factors'],
            suggestions=quality_result['suggestions'],
            used_enhanced=used_enhanced
        )
        
        db.add(record)
        await db.flush()
        return record
