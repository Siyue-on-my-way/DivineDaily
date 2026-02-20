"""智能Prompt构建器 - 场景化Prompt生成"""

from typing import Dict, Any, Optional
from app.services.question_analyzer import QuestionAnalysis


class SmartPromptBuilder:
    """智能Prompt构建器 - 根据问题分析结果生成针对性Prompt"""
    
    @staticmethod
    def build_answer_prompt(
        question: str,
        hexagram_info: Dict[str, Any],
        profile: Optional[Any] = None,
        analysis: Optional[QuestionAnalysis] = None
    ) -> str:
        """
        构建答案Prompt（结果卡）
        
        Args:
            question: 用户问题
            hexagram_info: 卦象信息
            profile: 用户档案（可选）
            analysis: 问题分析结果（可选）
        
        Returns:
            str: 构建好的Prompt
        """
        # 基础信息
        base_info = SmartPromptBuilder._build_base_info(question, hexagram_info, profile)
        
        # 根据问题分析生成针对性指导
        if analysis:
            specific_guidance = SmartPromptBuilder._generate_specific_guidance(analysis)
        else:
            specific_guidance = SmartPromptBuilder._default_guidance()
        
        # 语言风格指导
        style_guide = SmartPromptBuilder._build_style_guide()
        
        return base_info + "\n" + specific_guidance + "\n" + style_guide
    
    @staticmethod
    def build_detail_prompt(
        question: str,
        hexagram_info: Dict[str, Any],
        profile: Optional[Any] = None,
        analysis: Optional[QuestionAnalysis] = None
    ) -> str:
        """
        构建详情Prompt（详细解读）
        
        Args:
            question: 用户问题
            hexagram_info: 卦象信息
            profile: 用户档案（可选）
            analysis: 问题分析结果（可选）
        
        Returns:
            str: 构建好的Prompt
        """
        base_info = SmartPromptBuilder._build_base_info(question, hexagram_info, profile)
        
        detail_requirements = f"""
请撰写详细的解卦报告（300-500字）：

1. **卦象分析**：解释卦名和卦辞的含义
2. **结合现状**：分析卦象与用户问题的关联
3. **详细建议**：给出具体的行动指南和注意事项
4. **总结**：一句话总结核心建议

语言风格：
- 专业且富有哲理
- 温暖且具有启发性
- 引用易经原文并解释
"""
        
        return base_info + "\n" + detail_requirements
    
    @staticmethod
    def _build_base_info(question: str, hexagram_info: Dict, profile: Optional[Any]) -> str:
        """构建基础信息"""
        info = f"""你是一位精通周易、经验丰富的占卜大师。用户向你请教人生抉择，你需要给出明确、实用的建议。

用户问题：{question}

本次卦象：
- 卦名：{hexagram_info.get('name', '未知')}
- 卦辞：{hexagram_info.get('summary', '')}
- 吉凶：{hexagram_info.get('outcome', '平')}
- 五行：{hexagram_info.get('wuxing', '')}"""
        
        # 添加用户档案信息（如果有）
        if profile:
            info += f"""

用户生辰八字：
- 农历：{getattr(profile, 'lunar_year', '')}年{getattr(profile, 'lunar_month', '')}月{getattr(profile, 'lunar_day', '')}日
- 天干地支：{getattr(profile, 'gan_zhi_year', '')}年{getattr(profile, 'gan_zhi_month', '')}月{getattr(profile, 'gan_zhi_day', '')}日
- 生肖：{getattr(profile, 'animal', '')}"""
        
        return info
    
    @staticmethod
    def _generate_specific_guidance(analysis: QuestionAnalysis) -> str:
        """根据问题分析生成针对性指导"""
        if analysis.question_type == "relationship":
            return SmartPromptBuilder._relationship_guidance(analysis)
        elif analysis.question_type == "career":
            return SmartPromptBuilder._career_guidance(analysis)
        elif analysis.question_type == "decision":
            return SmartPromptBuilder._decision_guidance(analysis)
        elif analysis.question_type == "knowledge":
            return SmartPromptBuilder._knowledge_guidance(analysis)
        elif analysis.question_type == "fortune":
            return SmartPromptBuilder._fortune_guidance(analysis)
        else:
            return SmartPromptBuilder._default_guidance()
    
    @staticmethod
    def _relationship_guidance(analysis: QuestionAnalysis) -> str:
        """感情类问题的针对性指导"""
        guidance = """
【这是一个感情问题】请按照以下格式回答（100-150字）：

第一步：明确结论"""
        
        if analysis.sub_type == "binary_choice":
            option_a = analysis.elements.get("option_a", "选项A")
            option_b = analysis.elements.get("option_b", "选项B")
            guidance += f"""
- 这是一个二选一问题："{option_a}" 还是 "{option_b}"
- 直接说"建议选择{option_a}"或"建议选择{option_b}"
- 明确指出哪个选项更适合，不要模棱两可"""
        elif analysis.sub_type == "yes_no":
            guidance += """
- 如果是是非题，直接说"建议在一起"或"建议暂缓"
- 给出明确的态度"""
        elif analysis.sub_type == "timing":
            guidance += """
- 如果是时机问题，直接说"现在是好时机"或"建议等待X个月"
- 给出具体的时间建议"""
        
        guidance += """

第二步：卦象解释（2-3句话）
- 说明卦象对感情的指示
- 解释两人的缘分和匹配度
- 提及五行或阴阳的关系

第三步：未来预测（2-3句话）
- 预测感情的发展趋势
- 可能遇到的挑战和机遇
- 对未来生活的影响"""
        
        # 添加复杂度提示
        if analysis.complexity == "high":
            concerns = [v for k, v in analysis.elements.items() if k.startswith("concern_")]
            if concerns:
                guidance += f"""

【注意】这是一个复杂问题，用户有以下顾虑：
{chr(10).join(f'- {c}' for c in concerns)}
请在回答中综合考虑这些因素，给出平衡的建议。"""
        
        return guidance
    
    @staticmethod
    def _career_guidance(analysis: QuestionAnalysis) -> str:
        """事业类问题的针对性指导"""
        guidance = """
【这是一个事业问题】请按照以下格式回答（100-150字）：

第一步：明确结论"""
        
        if analysis.sub_type == "binary_choice":
            option_a = analysis.elements.get("option_a", "选项A")
            option_b = analysis.elements.get("option_b", "选项B")
            guidance += f"""
- 这是一个选择题："{option_a}" 还是 "{option_b}"
- 直接说"建议选择{option_a}"或"建议选择{option_b}"
- 明确指出哪个选项更有利于事业发展"""
        elif analysis.sub_type == "yes_no":
            guidance += """
- 如果是是非题（跳槽还是留下），直接说"建议跳槽"或"建议留下"
- 给出明确的建议"""
        elif analysis.sub_type == "timing":
            guidance += """
- 如果是时机问题，直接说"现在是好时机"或"建议等待X个月"
- 给出具体的时间建议"""
        
        guidance += """

第二步：卦象解释（2-3句话）
- 说明卦象对事业的指示
- 解释当前的事业运势
- 提及五行对事业的影响

第三步：未来预测（2-3句话）
- 预测事业的发展趋势
- 可能遇到的机遇和挑战
- 对收入和职位的影响"""
        
        return guidance
    
    @staticmethod
    def _decision_guidance(analysis: QuestionAnalysis) -> str:
        """决策类问题的针对性指导"""
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
- 必须明确选择其中一个，不要说"都可以"或"看情况\""""
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
- 提及五行或阴阳的关系

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战
- 对生活的影响"""
        
        # 添加复杂度提示
        if analysis.complexity == "high":
            guidance += """

【注意】这是一个复杂问题，涉及多个维度。
请在回答中综合考虑这些因素，给出平衡的建议。"""
        
        return guidance
    
    @staticmethod
    def _knowledge_guidance(analysis: QuestionAnalysis) -> str:
        """知识类问题的针对性指导"""
        return """
【这是一个知识类问题】请按照以下格式回答（150-200字）：

第一步：直接解答
- 用简洁的语言解释概念或现象
- 避免过于学术化的表述

第二步：结合卦象
- 说明卦象如何体现这个概念
- 用卦象来加深理解

第三步：实际应用
- 这个知识在生活中如何应用
- 给出1-2个具体例子

语言风格：
- 深入浅出，通俗易懂
- 既有理论深度，又有实践价值
- 引用经典但不晦涩"""
    
    @staticmethod
    def _fortune_guidance(analysis: QuestionAnalysis) -> str:
        """运势类问题的针对性指导"""
        return """
【这是一个运势问题】请按照以下格式回答（100-150字）：

第一步：综合评分
- 给出今日运势评分（0-100分）
- 一句话概括运势特点

第二步：分项分析
- 财运：简要说明财运状况
- 事业：简要说明事业运势
- 感情：简要说明感情运势
- 健康：简要说明健康状况

第三步：行动建议
- 今日宜做的事（2-3项）
- 今日忌做的事（2-3项）
- 幸运提示（颜色、方位、时辰）

语言风格：
- 积极正面，给人信心
- 具体实用，可操作性强"""
    
    @staticmethod
    def _default_guidance() -> str:
        """默认指导（通用）"""
        return """
【重要】请按照以下格式回答（100-150字）：

第一步：明确结论
- 直接给出建议，不要模棱两可

第二步：卦象解释（2-3句话）
- 简要说明卦象的含义
- 解释为什么卦象支持这个结论

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战"""
    
    @staticmethod
    def _build_style_guide() -> str:
        """构建语言风格指导"""
        return """

语言风格：
- 像一位智慧长者，语气坚定但温和
- 不要说"可能"、"也许"、"或许"这类模糊词
- 要说"建议"、"应当"、"宜"、"不宜"这类明确词
- 结合易经智慧，但用现代语言表达
- 回答要简洁有力，避免冗长"""

