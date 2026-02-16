"""增强占卜服务（集成智能预处理和LLM）"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.divination_service import DivinationService
from app.services.intent_service import IntentRecognitionService
from app.services.question_analyzer import QuestionAnalyzer
from app.services.prompt_builder import PromptBuilder
from app.services.llm_service import LLMService, create_llm_service
from app.repositories.llm_repository import LLMRepository
from app.repositories.config_repository import PromptConfigRepository


class EnhancedDivinationService(DivinationService):
    """增强占卜服务（支持智能预处理和LLM）"""
    
    def __init__(self, db: AsyncSession, llm_service: Optional[LLMService] = None):
        super().__init__(db)
        self.llm_service = llm_service
        self.intent_service = IntentRecognitionService(db, llm_service)
        self.question_analyzer = QuestionAnalyzer(llm_service)
        self.llm_repo = LLMRepository(db)
        self.prompt_repo = PromptConfigRepository(db)
    
    async def start_divination_with_enhancement(self, request) -> Dict[str, Any]:
        """开始增强占卜（集成智能预处理）"""
        
        # 步骤1：问题分析
        analysis = None
        if self.llm_service:
            try:
                analysis = await self.question_analyzer.analyze_question(request.question)
            except:
                pass  # 降级到规则引擎
        
        # 步骤2：意图识别
        intent_result = self.intent_service.analyze_intent(request.question, request.user_id)
        
        # 步骤3：保存意图记录
        try:
            await self.intent_service.save_intent(request.question, intent_result, request.user_id)
            await self.db.commit()
        except:
            pass  # 保存失败不影响占卜
        
        # 步骤4：执行占卜
        divination_result = await self.start_divination(request)
        
        # 步骤5：如果有LLM，增强解读
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
            except Exception as e:
                # LLM增强失败，使用原始结果
                pass
        
        return divination_result
    
    async def _enhance_summary(self, question: str, hexagram_info: Dict[str, Any],
                               analysis: Optional[Any] = None) -> str:
        """使用LLM增强摘要"""
        
        # 获取Prompt配置
        prompt_config = await self.prompt_repo.get_by_scene_and_type("divination", "answer")
        
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
                prompt = PromptBuilder.build_answer_prompt(question, hexagram_info, None, analysis)
                
                # 调用LLM
                try:
                    enhanced = await llm.generate_answer(prompt)
                    return enhanced
                finally:
                    if hasattr(llm, 'close'):
                        await llm.close()
        
        # 降级：使用默认LLM或返回原始摘要
        if self.llm_service:
            prompt = PromptBuilder.build_answer_prompt(question, hexagram_info, None, analysis)
            return await self.llm_service.generate_answer(prompt)
        
        return hexagram_info.get('summary', '')
    
    async def _enhance_detail(self, question: str, hexagram_info: Dict[str, Any]) -> str:
        """使用LLM增强详情"""
        
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
