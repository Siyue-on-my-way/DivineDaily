"""增强占卜服务（集成智能预处理、路由和LLM）"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.divination_service import DivinationService
from app.services.intent_service import IntentRecognitionService
from app.services.question_analyzer import QuestionAnalyzer
from app.services.divination_router import DivinationRouter
from app.services.prompt_builder import PromptBuilder
from app.services.llm_service import LLMService, create_llm_service
from app.repositories.llm_repository import LLMRepository
from app.repositories.config_repository import PromptConfigRepository
from app.models.divination import DivinationSession as DivinationSessionModel
import traceback


class EnhancedDivinationService(DivinationService):
    """增强占卜服务（支持智能预处理、路由和LLM）"""
    
    def __init__(self, db: AsyncSession, llm_service: Optional[LLMService] = None):
        super().__init__(db)
        self.llm_service = llm_service
        self.intent_service = IntentRecognitionService(db, llm_service)
        self.question_analyzer = QuestionAnalyzer(llm_service)
        self.router = DivinationRouter(db)  # 新增：智能路由器
        self.llm_repo = LLMRepository(db)
        self.prompt_repo = PromptConfigRepository(db)
        self.daily_fortune_service = None  # 将在外部注入
        print(f"[DEBUG] EnhancedDivinationService初始化，llm_service={'有' if llm_service else '无'}")
    
    def set_daily_fortune_service(self, service):
        """注入每日运势服务"""
        self.daily_fortune_service = service
    
    async def start_divination_with_enhancement(self, request) -> Dict[str, Any]:
        """开始增强占卜（集成智能预处理和路由）"""
        
        print(f"[DEBUG] 开始增强占卜，问题: {request.question}")
        
        # 步骤1：问题分析（使用增强的QuestionAnalyzer）
        analysis = None
        if self.llm_service:
            try:
                analysis = await self.question_analyzer.analyze_question(request.question)
                print(f"[DEBUG] 问题分析完成 - 类型: {analysis.question_type}, 子类型: {analysis.sub_type}, 复杂度: {analysis.complexity}")
                print(f"[DEBUG] 提取的要素: {analysis.elements}")
            except Exception as e:
                print(f"[WARN] 问题分析失败: {e}")
                pass  # 降级到规则引擎
        
        if not analysis:
            # 使用规则引擎降级
            analysis = self.question_analyzer._fallback_analysis(request.question)
            print(f"[DEBUG] 使用规则引擎分析 - 类型: {analysis.question_type}")
        
        # 步骤2：意图识别（保留原有逻辑）
        intent_result = self.intent_service.analyze_intent(request.question, request.user_id)
        
        # 步骤3：保存意图记录
        try:
            await self.intent_service.save_intent(request.question, intent_result, request.user_id)
            await self.db.commit()
        except:
            pass  # 保存失败不影响占卜
        
        # 步骤4：智能路由 - 根据问题类型选择处理策略
        print(f"[DEBUG] 开始智能路由...")
        try:
            # 生成session_id
            import uuid
            session_id = str(uuid.uuid4())
            
            divination_result = await self.router.route_question(
                session_id=session_id,
                question=request.question,
                user_id=request.user_id,
                analysis=analysis,
                divination_service=self,
                daily_fortune_service=self.daily_fortune_service
            )
            print(f"[DEBUG] 路由处理完成")
        except Exception as e:
            print(f"[ERROR] 路由处理失败，使用基础占卜: {e}")
            traceback.print_exc()
            # 降级到基础占卜
            divination_result = await self.start_divination(request)
        
        print(f"[DEBUG] 占卜完成，hexagram_info={'有' if divination_result.hexagram_info else '无'}")
        
        # 步骤5：如果有LLM且有卦象信息，增强解读
        print(f"[DEBUG] 检查LLM增强条件: llm_service={'有' if self.llm_service else '无'}, hexagram_info={'有' if divination_result.hexagram_info else '无'}")
        if self.llm_service and divination_result.hexagram_info:
            try:
                print(f"[DEBUG] 开始LLM增强解读...")
                enhanced_summary = await self._enhance_summary(
                    request.question,
                    divination_result.hexagram_info,
                    analysis
                )
                print(f"[DEBUG] LLM增强摘要完成，长度: {len(enhanced_summary)}")
                divination_result.summary = enhanced_summary
                
                enhanced_detail = await self._enhance_detail(
                    request.question,
                    divination_result.hexagram_info
                )
                print(f"[DEBUG] LLM增强详情完成，长度: {len(enhanced_detail)}")
                divination_result.detail = enhanced_detail
                
                # 关键修复：更新数据库中的记录
                print(f"[DEBUG] 更新数据库中的LLM增强结果...")
                result = await self.db.execute(
                    select(DivinationSessionModel).where(
                        DivinationSessionModel.id == divination_result.session_id
                    )
                )
                session = result.scalar_one_or_none()
                if session:
                    session.result_summary = enhanced_summary
                    session.result_detail = enhanced_detail
                    # 同时更新result_data中的summary和detail
                    if session.result_data:
                        session.result_data['summary'] = enhanced_summary
                        session.result_data['detail'] = enhanced_detail
                    await self.db.flush()
                    print(f"[DEBUG] 数据库更新完成")
                else:
                    print(f"[WARN] 未找到session记录: {divination_result.session_id}")
                    
            except Exception as e:
                # LLM增强失败，使用原始结果
                print(f"[ERROR] LLM增强失败: {type(e).__name__}: {e}")
                traceback.print_exc()
        else:
            print(f"[WARN] 跳过LLM增强")
        
        return divination_result
    
    async def _enhance_summary(self, question: str, hexagram_info: Dict[str, Any],
                               analysis: Optional[Any] = None) -> str:
        """使用LLM增强摘要"""
        
        print(f"[DEBUG] _enhance_summary开始")
        
        # 获取Prompt配置
        prompt_config = await self.prompt_repo.get_by_scene_and_type("divination", "answer")
        print(f"[DEBUG] Prompt配置: {prompt_config.name if prompt_config else 'None'}")
        
        if prompt_config and prompt_config.llm_config_id:
            # 使用配置的LLM
            llm_config = await self.llm_repo.get_by_id(prompt_config.llm_config_id)
            print(f"[DEBUG] 使用配置的LLM: {llm_config.name if llm_config else 'None'}")
            if llm_config:
                llm = create_llm_service(
                    llm_config,
                    temperature=prompt_config.temperature,
                    max_tokens=prompt_config.max_tokens,
                    timeout=prompt_config.timeout_seconds
                )
                
                # 构建Prompt
                prompt = PromptBuilder.build_answer_prompt(question, hexagram_info, None, analysis)
                print(f"[DEBUG] Prompt构建完成，长度: {len(prompt)}")
                
                # 调用LLM
                try:
                    print(f"[DEBUG] 调用LLM.generate_answer...")
                    enhanced = await llm.generate_answer(prompt)
                    print(f"[DEBUG] LLM返回结果，长度: {len(enhanced)}")
                    return enhanced
                finally:
                    if hasattr(llm, 'close'):
                        await llm.close()
        
        # 降级：使用默认LLM或返回原始摘要
        print(f"[DEBUG] 使用默认LLM或返回原始摘要")
        if self.llm_service:
            prompt = PromptBuilder.build_answer_prompt(question, hexagram_info, None, analysis)
            return await self.llm_service.generate_answer(prompt)
        
        return hexagram_info.get('summary', '')
    
    async def _enhance_detail(self, question: str, hexagram_info: Dict[str, Any]) -> str:
        """使用LLM增强详情"""
        
        print(f"[DEBUG] _enhance_detail开始")
        
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
