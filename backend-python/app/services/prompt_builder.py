"""Prompt构建器（智能Prompt生成）"""

from typing import Dict, Any, Optional
from app.services.question_analyzer import QuestionAnalysis


class PromptBuilder:
    """智能Prompt构建器"""
    
    @staticmethod
    def build_answer_prompt(question: str, hexagram_info: Dict[str, Any], 
                           user_profile: Optional[Dict[str, Any]] = None,
                           analysis: Optional[QuestionAnalysis] = None) -> str:
        """构建答案Prompt（结果卡）"""
        
        # 基础信息
        base_prompt = f"""你是一位精通周易的占卜大师。用户向你请教人生抉择，你需要给出明确、实用的建议。

用户问题：{question}

本次卦象：
- 卦名：{hexagram_info.get('name', '未知')}
- 卦辞：{hexagram_info.get('summary', '')}
- 吉凶：{hexagram_info.get('outcome', '')}
"""
        
        # 添加用户档案信息
        if user_profile:
            base_prompt += f"""
用户信息：
- 生肖：{user_profile.get('animal', '')}
- 星座：{user_profile.get('zodiac_sign', '')}
"""
        
        # 根据问题分析添加针对性指导
        if analysis:
            guidance = PromptBuilder._generate_guidance(analysis)
            base_prompt += f"\n{guidance}"
        else:
            base_prompt += """
【重要】请按照以下格式回答（100-150字）：

第一步：明确结论
- 直接给出建议，不要模棱两可

第二步：卦象解释（2-3句话）
- 简要说明卦象的含义
- 解释为什么卦象支持这个结论

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战
"""
        
        # 语言风格指导
        base_prompt += """
语言风格：
- 像一位智慧长者，语气坚定但温和
- 不要说"可能"、"也许"、"或许"这类模糊词
- 要说"建议"、"应当"、"宜"、"不宜"这类明确词
- 结合易经智慧，但用现代语言表达
"""
        
        return base_prompt
    
    @staticmethod
    def build_detail_prompt(question: str, hexagram_info: Dict[str, Any],
                           user_profile: Optional[Dict[str, Any]] = None) -> str:
        """构建详情Prompt"""
        
        prompt = f"""你是一位精通周易的占卜师。根据以下信息为用户详细解卦：

用户问题：{question}

本次卦象：
- 卦名：{hexagram_info.get('name', '')}
- 卦辞：{hexagram_info.get('summary', '')}
- 详细解释：{hexagram_info.get('detail', '')}
- 吉凶：{hexagram_info.get('outcome', '')}
"""
        
        if user_profile:
            prompt += f"""
用户信息：
- 生肖：{user_profile.get('animal', '')}
- 星座：{user_profile.get('zodiac_sign', '')}
"""
        
        prompt += """
请撰写详细的解卦报告（300-500字）：
1. 卦象分析：解释卦名和卦辞的含义
2. 结合现状：分析卦象与用户问题的关联
3. 详细建议：给出具体的行动指南和注意事项
4. 总结：一句话总结核心建议

语言风格：
- 专业且富有哲理
- 温暖且具有启发性
- 引用易经原文并解释
"""
        
        return prompt
    
    @staticmethod
    def _generate_guidance(analysis: QuestionAnalysis) -> str:
        """根据问题分析生成针对性指导"""
        
        if analysis.question_type == "relationship":
            return PromptBuilder._guidance_relationship(analysis)
        elif analysis.question_type == "career":
            return PromptBuilder._guidance_career(analysis)
        elif analysis.question_type == "decision":
            return PromptBuilder._guidance_decision(analysis)
        else:
            return PromptBuilder._guidance_default()
    
    @staticmethod
    def _guidance_relationship(analysis: QuestionAnalysis) -> str:
        """感情类问题指导"""
        guidance = """
【这是一个感情问题】请按照以下格式回答（100-150字）：

第一步：明确结论"""
        
        if analysis.sub_type == "binary_choice":
            guidance += """
- 如果是选择题（A还是B），直接说"建议选择A"或"建议选择B"
- 明确指出哪个选项更适合，不要模棱两可"""
        elif analysis.sub_type == "yes_no":
            guidance += """
- 如果是是非题，直接说"建议在一起"或"建议暂缓"
- 给出明确的态度"""
        
        guidance += """

第二步：卦象解释（2-3句话）
- 说明卦象对感情的指示
- 解释两人的缘分和匹配度

第三步：未来预测（2-3句话）
- 预测感情的发展趋势
- 可能遇到的挑战和机遇
"""
        return guidance
    
    @staticmethod
    def _guidance_career(analysis: QuestionAnalysis) -> str:
        """事业类问题指导"""
        guidance = """
【这是一个事业问题】请按照以下格式回答（100-150字）：

第一步：明确结论"""
        
        if analysis.sub_type == "binary_choice":
            guidance += """
- 如果是选择题（工作A还是工作B），直接说"建议选择A"或"建议选择B"
- 明确指出哪个选项更有利于事业发展"""
        elif analysis.sub_type == "yes_no":
            guidance += """
- 如果是是非题（跳槽还是留下），直接说"建议跳槽"或"建议留下"
- 给出明确的建议"""
        
        guidance += """

第二步：卦象解释（2-3句话）
- 说明卦象对事业的指示
- 解释当前的事业运势

第三步：未来预测（2-3句话）
- 预测事业的发展趋势
- 可能遇到的机遇和挑战
"""
        return guidance
    
    @staticmethod
    def _guidance_decision(analysis: QuestionAnalysis) -> str:
        """决策类问题指导"""
        guidance = """
【这是一个决策问题】请按照以下格式回答（100-150字）：

第一步：明确结论"""
        
        if analysis.sub_type == "binary_choice":
            option_a = analysis.elements.get("option_a", "")
            option_b = analysis.elements.get("option_b", "")
            if option_a and option_b:
                guidance += f"""
- 这是一个二选一问题："{option_a}" 还是 "{option_b}"
- 直接说"建议选择{option_a}"或"建议选择{option_b}"
- 必须明确选择其中一个，不要说"都可以"或"看情况"
"""
            else:
                guidance += """
- 这是一个二选一问题，直接说"建议选择A"或"建议选择B"
- 必须明确选择其中一个"""
        elif analysis.sub_type == "yes_no":
            guidance += """
- 这是一个是非题，直接说"建议去做"或"建议暂缓"
- 给出明确的态度"""
        elif analysis.sub_type == "timing":
            guidance += """
- 这是一个时机问题，直接说"现在是好时机"或"建议等待X个月"
- 给出具体的时间建议"""
        
        guidance += """

第二步：卦象解释（2-3句话）
- 说明卦象的含义
- 解释为什么卦象支持这个结论

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战
"""
        
        # 添加复杂度提示
        if analysis.complexity == "high":
            guidance += """
【注意】这是一个复杂问题，涉及多个维度。
请在回答中综合考虑这些因素，给出平衡的建议。
"""
        
        return guidance
    
    @staticmethod
    def _guidance_default() -> str:
        """默认指导"""
        return """
【重要】请按照以下格式回答（100-150字）：

第一步：明确结论
- 直接给出建议，不要模棱两可

第二步：卦象解释（2-3句话）
- 简要说明卦象的含义
- 解释为什么卦象支持这个结论

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战
"""
