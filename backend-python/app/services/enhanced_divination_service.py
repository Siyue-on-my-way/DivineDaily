"""增强占卜服务（集成智能预处理、路由和LLM）"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.divination_service import DivinationService
from app.services.intent_service import IntentRecognitionService
from app.services.question_analyzer import QuestionAnalyzer
from app.services.divination_router import DivinationRouter
from app.services.prompt_builder import PromptBuilder
from app.services.question_quality_evaluator import QuestionQualityEvaluator
from app.services.llm_service import LLMService, create_llm_service
from app.repositories.llm_repository import LLMRepository
from app.repositories.config_repository import PromptConfigRepository
from app.models.divination import DivinationSession as DivinationSessionModel
from app.core.logger import get_logger
import traceback
import uuid
from datetime import datetime, timezone

logger = get_logger("divination")


class EnhancedDivinationService(DivinationService):
    """增强占卜服务（支持智能预处理、路由和LLM）"""
    
    def __init__(self, db: AsyncSession, llm_service: Optional[LLMService] = None):
        # 初始化仓库
        self.llm_repo = LLMRepository(db)
        self.prompt_repo = PromptConfigRepository(db)
        
        # 调用父类初始化,传递LLM相关参数
        super().__init__(db, llm_service=llm_service, prompt_repo=self.prompt_repo, llm_repo=self.llm_repo)
        
        self.llm_service = llm_service
        self.intent_service = IntentRecognitionService(db, llm_service)
        self.question_analyzer = QuestionAnalyzer(llm_service)
        self.quality_evaluator = QuestionQualityEvaluator(llm_service)
        self.router = DivinationRouter(db)
        self.daily_fortune_service = None
        logger.debug("EnhancedDivinationService初始化", extra={"llm_service": "有" if llm_service else "无"})
    
    async def start_divination_with_enhancement(self, request) -> Dict[str, Any]:
        """智能占卜流程（三级处理）"""
        
        logger.info("开始智能占卜", extra={"question": request.question})
        
        # 步骤1：问题质量评估
        quality = await self.quality_evaluator.evaluate(request.question)
        logger.info("问题质量评估", extra=quality)
        
        # 步骤2：根据质量级别选择处理流程
        if quality['level'] == 'high':
            # 高质量：完整占卜流程
            logger.info("执行完整占卜流程")
            result = await self._full_divination_flow(request, quality)
        elif quality['level'] == 'medium':
            # 中等质量：简化占卜流程
            logger.info("执行简化占卜流程")
            result = await self._simple_divination_flow(request, quality)
        else:
            # 低质量：直接 LLM 回答
            logger.info("执行直接回答流程")
            result = await self._direct_answer_flow(request, quality)
        
        logger.info("占卜完成", extra={"processing_type": result.get("processing_type", "unknown")})
        return result
    
    async def _full_divination_flow(self, request, quality: Dict[str, Any]) -> Dict[str, Any]:
        """完整占卜流程（高质量问题）"""
        
        # 问题分析
        analysis = None
        if self.llm_service:
            try:
                analysis = await self.question_analyzer.analyze_question(request.question)
                logger.debug("问题分析完成", extra={"question_type": analysis.question_type})
            except Exception as e:
                logger.warning("问题分析失败", exc_info=True)
                analysis = self.question_analyzer._fallback_analysis(request.question)
        else:
            analysis = self.question_analyzer._fallback_analysis(request.question)
        
        # 智能路由占卜
        session_id = str(uuid.uuid4())
        try:
            divination_result = await self.router.route_question(
                session_id=session_id,
                question=request.question,
                user_id=request.user_id,
                analysis=analysis,
                divination_service=self,
                daily_fortune_service=self.daily_fortune_service
            )
        except Exception as e:
            logger.error("路由处理失败", exc_info=True)
            
            divination_result = await self.start_divination(request)
        
        # LLM 增强解读
        if self.llm_service and divination_result.hexagram_info:
            try:
                enhanced_summary = await self._enhance_summary(
                    request.question,
                    divination_result.hexagram_info,
                    analysis
                )
                divination_result.summary = enhanced_summary
                
                enhanced_detail = await self._enhance_detail(
                    request.question,
                    divination_result.hexagram_info
                )
                divination_result.detail = enhanced_detail
                
                # 更新数据库
                await self._update_session_in_db(divination_result.session_id, enhanced_summary, enhanced_detail)
            except Exception as e:
                logger.error("LLM增强失败", exc_info=True)
                
        
        # 添加质量信息
        result_dict = divination_result.model_dump() if hasattr(divination_result, 'model_dump') else divination_result
        result_dict['quality'] = quality
        result_dict['processing_type'] = 'full_divination'
        
        return result_dict
    
    async def _simple_divination_flow(self, request, quality: Dict[str, Any]) -> Dict[str, Any]:
        """简化占卜流程（中等质量问题）"""
        
        # 执行基础占卜（不做复杂分析）
        divination_result = await self.start_divination(request)
        
        # LLM 基础解读 + 引导
        if self.llm_service and divination_result.hexagram_info:
            try:
                # 构建引导性 Prompt
                prompt = f"""你是一位占卜师。用户的问题质量尚可但不够明确，请给出占卜建议并引导用户细化问题。

用户问题：{request.question}
问题评估：{quality['reason']}
改进建议：{', '.join(quality['suggestions'])}

卦象：{divination_result.hexagram_info.get('name', '')}
卦辞：{divination_result.hexagram_info.get('summary', '')}

请使用 Markdown 格式回答（150-200字）：

## 💡 占卜建议
根据卦象给出初步建议

## 📝 问题优化建议
引导用户如何将问题表述得更明确，以获得更准确的占卜结果

**格式要求**：使用 Markdown 格式，重点内容用 **加粗**"""

                enhanced_summary = await self.llm_service.generate(prompt)
                divination_result.summary = enhanced_summary
                divination_result.detail = enhanced_summary  # 简化流程，详情和摘要相同
                
                # 更新数据库
                await self._update_session_in_db(divination_result.session_id, enhanced_summary, enhanced_summary)
            except Exception as e:
                logger.error("LLM解读失败", exc_info=True)
        
        # 添加质量信息
        result_dict = divination_result.model_dump() if hasattr(divination_result, 'model_dump') else divination_result
        result_dict['quality'] = quality
        result_dict['processing_type'] = 'simple_divination'
        
        return result_dict
    
    async def _direct_answer_flow(self, request, quality: Dict[str, Any]) -> Dict[str, Any]:
        """直接回答流程（低质量问题）"""
        
        session_id = str(uuid.uuid4())
        
        # 构建友好的回复
        if self.llm_service:
            try:
                prompt = f"""你是一位友好的占卜助手。用户的问题不适合占卜，请给出友好的回复并引导用户。

用户问题：{request.question}
问题评估：{quality['reason']}

请使用 Markdown 格式回答（100-150字）：

## 👋 友好提示
解释为什么这个问题不适合占卜

## 💬 如何正确提问
引导用户提出适合占卜的问题，例如：
- 感情决策："我应该和TA在一起吗？"
- 事业选择："我应该接受这份工作吗？"
- 时机把握："现在是创业的好时机吗？"

**语气**：温和友好，不要让用户感到被拒绝"""

                answer = await self.llm_service.generate(prompt)
            except Exception as e:
                logger.error("LLM回答失败", exc_info=True)
                answer = f"""## 👋 友好提示

您的问题似乎不太适合占卜。占卜更适合帮助您做出人生决策，比如感情、事业、时机等方面的选择。

## 💬 如何正确提问

您可以这样提问：
- **感情决策**："我应该和TA在一起吗？"
- **事业选择**："我应该接受这份新工作吗？"
- **时机把握**："现在是创业的好时机吗？"

期待您提出更具体的问题，我会为您认真占卜！"""
        else:
            answer = "您好！请提出与占卜相关的问题，我会为您解答。"
        
        # 创建简化的结果对象
        result = {
            'session_id': session_id,
            'status': 'completed',
            'question': request.question,
            'title': '温馨提示',
            'summary': answer,
            'detail': answer,
            'outcome': '',
            'hexagram_info': None,
            'quality': quality,
            'processing_type': 'direct_answer',
            'created_at': datetime.now(timezone.utc),
        }
        
        # 保存到数据库（可选）
        try:
            session = DivinationSessionModel(
                id=session_id,
                user_id=request.user_id,
                version=getattr(request, 'version', None) or 'CN',
                question=request.question,
                event_type=getattr(request, 'event_type', None),
                orientation=getattr(request, 'orientation', None),
                spread=getattr(request, 'spread', None),
                intent=getattr(request, 'intent', None),
                result_summary=answer,
                result_detail=answer,
                result_data={'quality': quality, 'processing_type': 'direct_answer'},
                status='completed'
            )
            self.db.add(session)
            await self.db.flush()
        except Exception as e:
            await self.db.rollback()
            logger.warning("保存直接回答记录失败", exc_info=True)
        
        return result
    
    async def _update_session_in_db(self, session_id: str, summary: str, detail: str):
        """更新数据库中的 session 记录"""
        try:
            result = await self.db.execute(
                select(DivinationSessionModel).where(
                    DivinationSessionModel.id == session_id
                )
            )
            session = result.scalar_one_or_none()
            if session:
                session.result_summary = summary
                session.result_detail = detail
                if session.result_data:
                    session.result_data['summary'] = summary
                    session.result_data['detail'] = detail
                # 使用 flush 而不是 commit，让调用者控制事务
                await self.db.flush()
                logger.debug("数据库更新完成", extra={"session_id": session_id})
        except Exception as e:
            logger.error("更新数据库失败", exc_info=True, extra={"session_id": session_id, "error": str(e)})
            # 不要抛出异常，避免影响主流程
    
    async def _enhance_summary(self, question: str, hexagram_info: Dict[str, Any],
                               analysis: Optional[Any] = None) -> str:
        """使用LLM增强摘要"""
        
        logger.debug("_enhance_summary开始")
        
        # 获取Prompt配置
        prompt_config = await self.prompt_repo.get_by_scene_and_type("divination", "answer")
        logger.debug("Prompt配置", extra={"config_name": prompt_config.name if prompt_config else None})
        
        if prompt_config and prompt_config.llm_config_id:
            # 使用配置的LLM
            llm_config = await self.llm_repo.get_by_id(prompt_config.llm_config_id)
            logger.debug("使用配置的LLM", extra={"llm_name": llm_config.name if llm_config else None})
            if llm_config:
                llm = create_llm_service(
                    llm_config,
                    temperature=prompt_config.temperature,
                    max_tokens=prompt_config.max_tokens,
                    timeout=prompt_config.timeout_seconds
                )
                
                # 构建Prompt
                prompt = PromptBuilder.build_answer_prompt(question, hexagram_info, None, analysis)
                logger.debug("Prompt构建完成", extra={"length": len(prompt)})
                
                # 调用LLM
                try:
                    logger.debug("调用LLM.generate_answer")
                    enhanced = await llm.generate_answer(prompt)
                    logger.debug("LLM返回结果", extra={"length": len(enhanced)})
                    return enhanced
                finally:
                    if hasattr(llm, 'close'):
                        await llm.close()
        
        # 降级：使用默认LLM或返回原始摘要
        logger.debug("使用默认LLM或返回原始摘要")
        if self.llm_service:
            prompt = PromptBuilder.build_answer_prompt(question, hexagram_info, None, analysis)
            return await self.llm_service.generate_answer(prompt)
        
        return hexagram_info.get('summary', '')
    
    async def _enhance_detail(self, question: str, hexagram_info: Dict[str, Any]) -> str:
        """使用LLM增强详情"""
        
        logger.debug("_enhance_detail开始")
        
        # 获取Prompt配置
        prompt_config = await self.prompt_repo.get_by_scene_and_type("divination", "detail")
        
        if prompt_config and prompt_config.llm_config_id:
            # 使用配置的LLM
            llm_config = await self.llm_repo.get_by_id(prompt_config.llm_config_id)
            if llm_config:
                llm = create_llm_service(
                    llm_config,
                    temperature=prompt_config.temperature,
                    max_tokens=prompt_config.max_tokens,
                    timeout=prompt_config.timeout_seconds
                )
                
                # 构建Prompt
                prompt = PromptBuilder.build_detail_prompt(question, hexagram_info)
                
                # 调用LLM
                try:
                    enhanced = await llm.generate_detail(prompt)
                    return enhanced
                finally:
                    if hasattr(llm, 'close'):
                        await llm.close()
        
        # 降级：使用默认LLM或返回原始详情
        if self.llm_service:
            prompt = PromptBuilder.build_detail_prompt(question, hexagram_info)
            return await self.llm_service.generate_detail(prompt)
        
        return hexagram_info.get('detail', '')
