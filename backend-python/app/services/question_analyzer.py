"""问题分析器（LLM驱动 - 增强版）"""

import json
from typing import Dict, Any, Optional
from app.services.llm_service import LLMService


class QuestionAnalysis:
    """问题分析结果"""
    def __init__(self, question_type: str, sub_type: str, elements: Dict[str, str],
                 intent: str, complexity: str, keywords: list, context: Dict[str, Any]):
        self.question_type = question_type  # decision, relationship, career, fortune, knowledge
        self.sub_type = sub_type            # binary_choice, yes_no, timing, compatibility
        self.elements = elements            # 问题要素（新增：option_a, option_b, concern_1等）
        self.intent = intent                # binary_choice, yes_no, timing, understanding
        self.complexity = complexity        # simple, medium, high（增强：多因素评估）
        self.keywords = keywords            # 关键词
        self.context = context              # 额外上下文


class QuestionAnalyzer:
    """问题分析器（增强版）"""
    
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
            except Exception as e:
                print(f"[WARN] LLM分析失败，降级到规则引擎: {e}")
                # LLM失败，降级到规则引擎
                pass
        
        # 使用规则引擎降级
        return self._fallback_analysis(question)
    
    def _build_analysis_prompt(self, question: str) -> str:
        """构建分析Prompt（增强版，包含示例）"""
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

3. **问题要素** (elements)：
   提取问题中的关键要素，如：
   - option_a: 选项A的描述
   - option_b: 选项B的描述
   - concern_1: 用户的顾虑1
   - concern_2: 用户的顾虑2
   - time_frame: 时间范围
   - target_person: 目标人物

4. **问题意图** (intent)：
   - binary_choice: 需要在两个选项中选一个
   - yes_no: 需要判断做还是不做
   - timing: 需要判断时机
   - understanding: 需要理解和解释
   - guidance: 需要指导和建议

5. **复杂度** (complexity)：
   - simple: 简单问题（单一维度）
   - medium: 中等复杂（2-3个维度）
   - high: 高度复杂（多个维度，有冲突）

6. **关键词** (keywords)：
   提取3-5个关键词

请严格按照以下 JSON 格式返回（不要添加任何其他文字）：

{{
  "question_type": "decision",
  "sub_type": "binary_choice",
  "elements": {{"option_a": "选项A", "option_b": "选项B"}},
  "intent": "binary_choice",
  "complexity": "medium",
  "keywords": ["关键词1", "关键词2"]
}}

示例1：
问题："我应该和研究生学妹谈恋爱还是和大一学妹谈？"
分析：
{{
  "question_type": "relationship",
  "sub_type": "binary_choice",
  "elements": {{
    "option_a": "研究生学妹",
    "option_b": "大一学妹",
    "context": "恋爱选择"
  }},
  "intent": "binary_choice",
  "complexity": "medium",
  "keywords": ["恋爱", "选择", "学妹", "年龄差"]
}}

示例2：
问题："杨冠和刘亦菲同时追我，我应该选谁？我最近在事业上升期，希望事业也有成。但是也怕孤独，想谈恋爱"
分析：
{{
  "question_type": "decision",
  "sub_type": "binary_choice",
  "elements": {{
    "option_a": "杨冠",
    "option_b": "刘亦菲",
    "concern_1": "事业上升期",
    "concern_2": "怕孤独"
  }},
  "intent": "binary_choice",
  "complexity": "high",
  "keywords": ["恋爱", "事业", "选择", "平衡"]
}}

现在请分析用户的问题并返回 JSON："""
    
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
        except Exception as e:
            print(f"[WARN] JSON解析失败: {e}")
            return None
    
    def _fallback_analysis(self, question: str) -> QuestionAnalysis:
        """降级分析（基于规则引擎 - 增强版，10条规则）"""
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
            
            # 增强：提取选项A和B
            if "还是" in question:
                parts = question.split("还是", 1)
                if len(parts) >= 2:
                    # 清理选项文本
                    option_a = parts[0].strip()
                    option_b = parts[1].strip()
                    
                    # 移除常见前缀
                    for prefix in ["我应该", "应该", "要不要", "该不该", "是"]:
                        if option_a.startswith(prefix):
                            option_a = option_a[len(prefix):].strip()
                    
                    # 移除常见后缀（如问号、句号）
                    option_b = option_b.rstrip("？?。.")
                    
                    analysis.elements["option_a"] = option_a
                    analysis.elements["option_b"] = option_b
        
        # 规则2：检测感情类问题
        relationship_keywords = ["恋爱", "喜欢", "爱", "感情", "结婚", "分手", "追", "表白", "相亲", "约会"]
        for keyword in relationship_keywords:
            if keyword in question:
                if analysis.question_type == "decision":
                    analysis.question_type = "relationship"
                if keyword not in analysis.keywords:
                    analysis.keywords.append(keyword)
        
        # 规则3：检测事业类问题
        career_keywords = ["工作", "事业", "职业", "跳槽", "升职", "面试", "公司", "老板", "同事"]
        for keyword in career_keywords:
            if keyword in question:
                if analysis.question_type == "decision" and analysis.question_type != "relationship":
                    analysis.question_type = "career"
                if keyword not in analysis.keywords:
                    analysis.keywords.append(keyword)
        
        # 规则4：检测运势类问题（新增）
        fortune_keywords = ["运势", "运气", "今日", "本周", "本月", "今年", "财运", "桃花运"]
        for keyword in fortune_keywords:
            if keyword in question:
                analysis.question_type = "fortune"
                if keyword not in analysis.keywords:
                    analysis.keywords.append(keyword)
                break
        
        # 规则5：检测知识类问题（新增）
        knowledge_keywords = ["是什么", "什么意思", "解释", "含义", "为什么", "怎么理解"]
        for keyword in knowledge_keywords:
            if keyword in question:
                analysis.question_type = "knowledge"
                analysis.sub_type = "open_ended"
                analysis.intent = "understanding"
                if keyword not in analysis.keywords:
                    analysis.keywords.append(keyword)
                break
        
        # 规则6：检测是非问题
        if any(kw in question for kw in ["应该", "要不要", "该不该", "能不能", "可不可以"]):
            if analysis.sub_type != "binary_choice":  # 二选一优先级更高
                analysis.sub_type = "yes_no"
                analysis.intent = "yes_no"
        
        # 规则7：检测时机问题
        if any(kw in question for kw in ["什么时候", "何时", "时机", "几时", "哪天"]):
            analysis.sub_type = "timing"
            analysis.intent = "timing"
            analysis.elements["time_frame"] = "未指定"
        
        # 规则8：提取顾虑和关注点（新增）
        concern_markers = ["但是", "不过", "可是", "然而"]
        concern_count = 0
        for marker in concern_markers:
            if marker in question:
                concern_count += 1
                # 尝试提取顾虑内容
                parts = question.split(marker, 1)
                if len(parts) > 1:
                    concern_text = parts[1].split("。")[0].split("，")[0].strip()
                    analysis.elements[f"concern_{concern_count}"] = concern_text
        
        # 规则9：检测复杂度（增强版 - 多因素评估）
        complexity_score = 0
        
        # 因素1：关联词数量
        if "但是" in question or "不过" in question or "可是" in question:
            complexity_score += 1
        if "又" in question or "也" in question or "还" in question:
            complexity_score += 1
        
        # 因素2：问题长度
        if len(question) > 50:
            complexity_score += 1
        if len(question) > 100:
            complexity_score += 1
        
        # 因素3：多个维度
        if len(analysis.keywords) >= 3:
            complexity_score += 1
        
        # 因素4：时间因素
        if any(kw in question for kw in ["最近", "现在", "未来", "以后"]):
            complexity_score += 0.5
        
        # 评估复杂度
        if complexity_score >= 3:
            analysis.complexity = "high"
        elif complexity_score >= 1.5:
            analysis.complexity = "medium"
        else:
            analysis.complexity = "simple"
        
        # 规则10：提取目标人物（新增）
        if analysis.question_type == "relationship":
            # 简单的人物提取逻辑
            for keyword in ["他", "她", "男友", "女友", "对象", "喜欢的人"]:
                if keyword in question:
                    analysis.elements["target_person"] = keyword
                    break
        
        return analysis
    
    def get_question_type_label(self) -> str:
        """获取问题类型的中文标签"""
        labels = {
            "decision": "决策",
            "relationship": "感情",
            "career": "事业",
            "fortune": "运势",
            "knowledge": "知识",
        }
        return labels.get(self.question_type, "其他")
    
    def get_intent_label(self) -> str:
        """获取问题意图的中文标签"""
        labels = {
            "binary_choice": "二选一",
            "yes_no": "是非判断",
            "timing": "时机选择",
            "understanding": "理解解释",
            "guidance": "指导建议",
        }
        return labels.get(self.intent, "其他")
