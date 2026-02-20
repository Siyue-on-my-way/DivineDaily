"""智能占卜路由器"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.question_analyzer import QuestionAnalysis
from app.schemas.divination import DivinationResult


class DivinationRouter:
    """智能占卜路由器 - 根据问题分析结果路由到不同处理策略"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def route_question(
        self,
        session_id: str,
        question: str,
        user_id: str,
        analysis: QuestionAnalysis,
        divination_service,
        daily_fortune_service=None
    ) -> DivinationResult:
        """
        根据问题分析结果路由到不同处理策略
        
        Args:
            session_id: 会话ID
            question: 用户问题
            user_id: 用户ID
            analysis: 问题分析结果
            divination_service: 占卜服务实例
            daily_fortune_service: 每日运势服务实例（可选）
        
        Returns:
            DivinationResult: 占卜结果
        """
        print(f"[路由] 问题类型: {analysis.question_type}, 子类型: {analysis.sub_type}, 复杂度: {analysis.complexity}")
        
        # 构建上下文
        question_context = {
            "analysis": analysis,
            "question_type": analysis.question_type,
            "sub_type": analysis.sub_type,
            "intent": analysis.intent,
            "elements": analysis.elements,
            "complexity": analysis.complexity,
            "keywords": analysis.keywords
        }
        
        # 根据问题类型路由
        if analysis.question_type == "fortune":
            # 运势类问题 → 每日运势服务
            print(f"[路由] 路由到: 每日运势服务")
            return await self._process_fortune(
                session_id, 
                user_id, 
                daily_fortune_service,
                divination_service
            )
        
        elif analysis.question_type == "knowledge":
            # 知识类问题 → 知识解读（卦象+知识传授）
            print(f"[路由] 路由到: 知识解读服务")
            return await self._process_knowledge(
                session_id,
                question,
                user_id,
                analysis,
                question_context,
                divination_service
            )
        
        else:
            # 决策类/感情类/事业类 → 周易卦象占卜
            print(f"[路由] 路由到: 决策占卜服务（周易卦象）")
            return await self._process_decision(
                session_id,
                question,
                user_id,
                analysis,
                question_context,
                divination_service
            )
    
    async def _process_fortune(
        self,
        session_id: str,
        user_id: str,
        daily_fortune_service,
        divination_service
    ) -> DivinationResult:
        """处理运势类问题"""
        if daily_fortune_service:
            try:
                # 调用每日运势服务
                from datetime import date
                fortune = await daily_fortune_service.generate_daily_fortune(user_id, date.today())
                
                # 转换为DivinationResult格式
                result = DivinationResult(
                    session_id=session_id,
                    outcome="吉",
                    title="今日运势",
                    summary=fortune.summary,
                    detail=self._format_fortune_detail(fortune),
                    hexagram_info=None,
                    recommendations=None,
                    daily_fortune={
                        "score": fortune.score,
                        "wealth": fortune.wealth,
                        "career": fortune.career,
                        "love": fortune.love,
                        "health": fortune.health,
                        "lucky_color": fortune.lucky_color,
                        "lucky_number": fortune.lucky_number,
                        "lucky_direction": fortune.lucky_direction,
                        "lucky_time": fortune.lucky_time,
                        "yi": fortune.yi,
                        "ji": fortune.ji
                    },
                    needs_follow_up=False,
                    created_at=fortune.created_at
                )
                result.question_type = "fortune"
                result.question_intent = "fortune_inquiry"
                return result
            except Exception as e:
                print(f"[路由] 每日运势服务失败，降级到推荐服务: {e}")
        
        # 降级：使用推荐服务
        return await self._process_recommendation(session_id, user_id, divination_service)
    
    async def _process_knowledge(
        self,
        session_id: str,
        question: str,
        user_id: str,
        analysis: QuestionAnalysis,
        question_context: Dict[str, Any],
        divination_service
    ) -> DivinationResult:
        """处理知识类问题 - 生成卦象但侧重知识传授"""
        # 使用决策处理逻辑，但会在Prompt中强调知识解释
        result = await self._process_decision(
            session_id,
            question,
            user_id,
            analysis,
            question_context,
            divination_service
        )
        
        # 标记为知识类问题
        result.question_type = "knowledge"
        result.question_intent = "understanding"
        
        return result
    
    async def _process_decision(
        self,
        session_id: str,
        question: str,
        user_id: str,
        analysis: QuestionAnalysis,
        question_context: Dict[str, Any],
        divination_service
    ) -> DivinationResult:
        """处理决策类问题 - 周易卦象占卜"""
        # 调用占卜服务的决策处理方法
        # 这里需要divination_service有相应的方法
        # 暂时使用基础占卜方法
        from app.schemas.divination import CreateDivinationRequest
        
        request = CreateDivinationRequest(
            user_id=user_id,
            version="CN",
            question=question,
            event_type=analysis.question_type,
            orientation=None,
            spread=None,
            intent=analysis.intent,
            context=question_context
        )
        
        # 调用基础占卜
        result = await divination_service.start_divination(request)
        
        # 添加问题分析信息
        result.question_type = analysis.question_type
        result.question_intent = analysis.intent
        
        return result
    
    async def _process_recommendation(
        self,
        session_id: str,
        user_id: str,
        divination_service
    ) -> DivinationResult:
        """处理推荐类问题（降级方案）"""
        # 简单的推荐逻辑
        result = DivinationResult(
            session_id=session_id,
            outcome="平",
            title="个性化推荐",
            summary="根据您的情况，建议您保持积极心态，顺其自然。",
            detail="# 推荐建议\n\n1. 保持开放心态\n2. 关注当下\n3. 相信直觉\n\n具体建议会根据您的个人档案和当前运势生成。",
            hexagram_info=None,
            recommendations=[],
            needs_follow_up=False
        )
        result.question_type = "recommendation"
        result.question_intent = "guidance"
        return result
    
    def _format_fortune_detail(self, fortune) -> str:
        """格式化运势详情"""
        lines = [
            "# 今日运势详解\n",
            f"## 综合评分：{fortune.score}分\n",
            f"**运势概述**：{fortune.summary}\n",
            "## 各方面运势\n",
            f"**财运**：{fortune.wealth}",
            f"**事业**：{fortune.career}",
            f"**感情**：{fortune.love}",
            f"**健康**：{fortune.health}\n",
            "## 幸运指南\n",
            f"- 幸运颜色：{fortune.lucky_color}",
            f"- 幸运数字：{fortune.lucky_number}",
            f"- 幸运方位：{fortune.lucky_direction}",
            f"- 幸运时辰：{fortune.lucky_time}\n",
            "## 宜忌\n",
            "**宜**：" + "、".join(fortune.yi),
            "**忌**：" + "、".join(fortune.ji)
        ]
        return "\n".join(lines)

