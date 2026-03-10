"""问题质量评估服务"""
from app.core.logger import get_logger
logger = get_logger("quality_evaluator")

import json
import re
from typing import Dict, Any, Optional
from app.services.llm_service import LLMService


class QuestionQualityEvaluator:
    """问题质量评估器"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service
    
    async def evaluate(self, question: str) -> Dict[str, Any]:
        """
        评估问题质量
        
        Returns:
            {
                'score': 85,  # 0-100分
                'level': 'high',  # high/medium/low
                'reason': '问题明确，适合占卜',
                'suggestions': []  # 改进建议
            }
        """
        # 如果有 LLM 服务，优先使用 LLM 评估
        if self.llm_service:
            try:
                result = await self._evaluate_with_llm(question)
                return result
            except Exception as e:
                logger.warning("LLM 评估失败，降级到规则引擎", exc_info=True)
        
        # 降级到规则引擎
        return self._evaluate_with_rules(question)
    
    async def _evaluate_with_llm(self, question: str) -> Dict[str, Any]:
        """使用 LLM 评估问题质量"""
        prompt = f"""你是一个占卜问题质量评估专家。请评估以下问题是否适合占卜算卦，给出 0-100 分的评分。

评分标准：
- 80-100分（高质量）：问题明确具体，有明确决策点，适合占卜
  例如："我应该接受这份新工作吗？"、"我和男朋友适合结婚吗？"
  
- 50-79分（中等质量）：问题相对模糊，可以占卜但需要引导
  例如："我的事业运势如何？"、"我该怎么办？"
  
- 0-49分（低质量）：不适合占卜（闲聊、测试、信息查询等）
  例如："你好"、"测试"、"今天天气怎么样？"

用户问题：{question}

请以 JSON 格式返回评估结果，不要有任何其他文字：
{{
    "score": 85,
    "level": "high",
    "reason": "问题明确，涉及职业决策，适合占卜",
    "suggestions": []
}}

如果是中等或低质量，请在 suggestions 中给出改进建议。"""

        # 调用 LLM
        response = await self.llm_service.generate(prompt)
        
        # 解析 JSON
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response)
            
            # 验证和规范化
            score = int(result.get('score', 50))
            score = max(0, min(100, score))  # 限制在 0-100
            
            if score >= 80:
                level = 'high'
            elif score >= 50:
                level = 'medium'
            else:
                level = 'low'
            
            return {
                'score': score,
                'level': level,
                'reason': result.get('reason', ''),
                'suggestions': result.get('suggestions', [])
            }
        except Exception as e:
            logger.error("解析 LLM 响应失败", extra={"response": response}, exc_info=True)
            # 降级到规则引擎
            return self._evaluate_with_rules(question)
    
    def _evaluate_with_rules(self, question: str) -> Dict[str, Any]:
        """基于规则的问题质量评估"""
        score = 50  # 基础分
        reason_parts = []
        suggestions = []
        
        # 清理问题
        question = question.strip()
        
        # 1. 长度检查
        if len(question) < 5:
            score -= 30
            reason_parts.append("问题过短")
            suggestions.append("请提供更详细的问题描述")
        elif len(question) > 10:
            score += 10
            reason_parts.append("问题长度适中")
        
        # 2. 高质量关键词检查
        high_quality_keywords = [
            '应该', '是否', '能否', '适合', '会不会', '可以吗',
            '要不要', '该不该', '值得吗', '好不好', '行不行'
        ]
        if any(kw in question for kw in high_quality_keywords):
            score += 30
            reason_parts.append("包含决策性关键词")
        
        # 3. 中等质量关键词检查
        medium_quality_keywords = [
            '怎么样', '如何', '什么时候', '哪个', '哪里',
            '运势', '财运', '事业', '感情', '婚姻'
        ]
        if any(kw in question for kw in medium_quality_keywords):
            score += 15
            reason_parts.append("包含占卜相关词汇")
        
        # 4. 低质量关键词检查
        low_quality_keywords = [
            '你好', '测试', 'test', '天气', '时间', '日期',
            '你是谁', '你叫什么', '帮我', '告诉我'
        ]
        if any(kw in question.lower() for kw in low_quality_keywords):
            score -= 40
            reason_parts.append("包含非占卜相关内容")
            suggestions.append("请提出与人生决策、运势相关的问题")
        
        # 5. 问号检查
        if '?' in question or '？' in question:
            score += 10
            reason_parts.append("以问句形式提出")
        else:
            suggestions.append("建议以问句形式提出问题")
        
        # 6. 特殊情况检查
        if len(question) <= 3:
            score = 10
            reason_parts = ["问题过于简短"]
            suggestions = ["请提供完整的问题描述"]
        
        # 7. 纯数字或符号
        if re.match(r'^[\d\s\W]+$', question):
            score = 5
            reason_parts = ["无效输入"]
            suggestions = ["请输入有意义的问题"]
        
        # 确定级别
        score = max(0, min(100, score))  # 限制在 0-100
        
        if score >= 80:
            level = 'high'
        elif score >= 50:
            level = 'medium'
        else:
            level = 'low'
        
        # 根据级别添加建议
        if level == 'medium' and not suggestions:
            suggestions.append("建议将问题表述得更具体明确")
        elif level == 'low' and not suggestions:
            suggestions.append("请提出与占卜相关的问题，如感情、事业、决策等")
        
        return {
            'score': score,
            'level': level,
            'reason': '；'.join(reason_parts) if reason_parts else '基于规则评估',
            'suggestions': suggestions
        }
    
    @staticmethod
    def get_quality_description(level: str) -> str:
        """获取质量级别描述"""
        descriptions = {
            'high': '问题质量优秀，适合深度占卜',
            'medium': '问题质量尚可，建议进一步明确',
            'low': '问题不适合占卜，建议重新提问'
        }
        return descriptions.get(level, '未知质量级别')

