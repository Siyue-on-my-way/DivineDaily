"""问题分析器（LLM驱动）"""

import json
from typing import Dict, Any, Optional
from app.services.llm_service import LLMService


class QuestionAnalysis:
    """问题分析结果"""
    def __init__(self, question_type: str, sub_type: str, elements: Dict[str, str],
                 intent: str, complexity: str, keywords: list, context: Dict[str, Any]):
        self.question_type = question_type  # decision, relationship, career, fortune, knowledge
        self.sub_type = sub_type            # binary_choice, yes_no, timing, compatibility
        self.elements = elements            # 问题要素
        self.intent = intent                # binary_choice, yes_no, timing, understanding
        self.complexity = complexity        # simple, medium, high
        self.keywords = keywords            # 关键词
        self.context = context              # 额外上下文


class QuestionAnalyzer:
    """问题分析器"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service
    
    async def analyze_question(self, question: str) -> QuestionAnalysis:
        """分析问题"""
        # 如果有LLM服务，使用LLM分析
        if self.llm_service:
            try:
                prompt = self._build_analysis_prompt(question)
                response = await self.llm_service.generate_answer(prompt)
                analysis = self._parse_analysis_response(response)
                if analysis:
                    return analysis
            except Exception:
                # LLM失败，降级到规则引擎
                pass
        
        # 使用规则引擎降级
        return self._fallback_analysis(question)
    
    def _build_analysis_prompt(self, question: str) -> str:
        """构建分析Prompt"""
        return f"""你是一位专业的问题分析师。请分析以下用户问题，并以 JSON 格式返回分析结果。

用户问题：{question}

请分析以下维度：

1. **问题类型** (question_type)：
   - decision: 决策类（需要做选择）
   - relationship: 感情类（恋爱、婚姻、人际关系）
   - career: 事业类（工作、职业发展）
   - fortune: 运势类（今日运势、未来运势）
   - knowledge: 知识类（了解某个概念或现象）

2. **子类型** (sub_type)：
   - binary_choice: 二选一（A还是B）
   - yes_no: 是非题（做还是不做）
   - timing: 时机问题（什么时候做）
   - compatibility: 匹配度（是否合适）
   - multiple_choice: 多选题（多个选项）
   - open_ended: 开放式问题

3. **问题要素** (elements)：提取关键要素，如 option_a, option_b, concern_1 等

4. **问题意图** (intent)：binary_choice, yes_no, timing, understanding, guidance

5. **复杂度** (complexity)：simple, medium, high

6. **关键词** (keywords)：提取3-5个关键词

请严格按照以下 JSON 格式返回（不要添加任何其他文字）：

{{
  "question_type": "decision",
  "sub_type": "binary_choice",
  "elements": {{"option_a": "选项A", "option_b": "选项B"}},
  "intent": "binary_choice",
  "complexity": "medium",
  "keywords": ["关键词1", "关键词2"]
}}"""
    
    def _parse_analysis_response(self, response: str) -> Optional[QuestionAnalysis]:
        """解析LLM返回的分析结果"""
        try:
            # 清理响应，提取JSON部分
            response = response.strip()
            start_idx = response.find("{")
            end_idx = response.rfind("}")
            
            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                return None
            
            json_str = response[start_idx:end_idx + 1]
            data = json.loads(json_str)
            
            return QuestionAnalysis(
                question_type=data.get("question_type", "decision"),
                sub_type=data.get("sub_type", "open_ended"),
                elements=data.get("elements", {}),
                intent=data.get("intent", "guidance"),
                complexity=data.get("complexity", "medium"),
                keywords=data.get("keywords", []),
                context=data.get("context", {})
            )
        except Exception:
            return None
    
    def _fallback_analysis(self, question: str) -> QuestionAnalysis:
        """降级分析（基于规则引擎）"""
        question_lower = question.lower()
        
        analysis = QuestionAnalysis(
            question_type="decision",
            sub_type="open_ended",
            elements={},
            intent="guidance",
            complexity="medium",
            keywords=[],
            context={}
        )
        
        # 规则1：检测是否为二选一问题
        if "还是" in question or "或者" in question:
            analysis.question_type = "decision"
            analysis.sub_type = "binary_choice"
            analysis.intent = "binary_choice"
            
            # 尝试提取选项
            if "还是" in question:
                parts = question.split("还是")
                if len(parts) >= 2:
                    analysis.elements["option_a"] = parts[0].strip()
                    analysis.elements["option_b"] = parts[1].strip()
        
        # 规则2：检测感情类问题
        relationship_keywords = ["恋爱", "喜欢", "爱", "感情", "结婚", "分手", "追", "表白"]
        for keyword in relationship_keywords:
            if keyword in question:
                analysis.question_type = "relationship"
                analysis.keywords.append(keyword)
        
        # 规则3：检测事业类问题
        career_keywords = ["工作", "事业", "职业", "跳槽", "升职", "面试", "公司"]
        for keyword in career_keywords:
            if keyword in question:
                analysis.question_type = "career"
                analysis.keywords.append(keyword)
        
        # 规则4：检测是非问题
        if any(kw in question for kw in ["应该", "要不要", "该不该", "能不能"]):
            analysis.sub_type = "yes_no"
            analysis.intent = "yes_no"
        
        # 规则5：检测时机问题
        if any(kw in question for kw in ["什么时候", "何时", "时机"]):
            analysis.sub_type = "timing"
            analysis.intent = "timing"
        
        # 规则6：检测复杂度
        concern_count = 0
        if "但是" in question or "不过" in question:
            concern_count += 1
        if "又" in question or "也" in question:
            concern_count += 1
        
        if concern_count >= 2:
            analysis.complexity = "high"
        elif concern_count == 1:
            analysis.complexity = "medium"
        else:
            analysis.complexity = "simple"
        
        return analysis
