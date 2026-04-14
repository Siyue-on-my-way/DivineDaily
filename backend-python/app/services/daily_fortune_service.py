"""每日运势服务"""

import json
import re
from typing import Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.daily_fortune import DailyFortune
from app.repositories.daily_fortune_repository import DailyFortuneRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.config_repository import PromptConfigRepository
from app.repositories.llm_repository import LLMRepository
from app.services.llm_service import create_llm_service
from app.services.time_convert_service import TimeConvertService
from app.services.fortune_algorithm_service import FortuneAlgorithmService

from app.core.logger import get_logger
logger = get_logger("fortune")



class DailyFortuneService:
    """每日运势服务 - 集成传统算法"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = DailyFortuneRepository(db)
        self.user_profile_repo = UserProfileRepository(db)
        self.prompt_config_repo = PromptConfigRepository(db)
        self.llm_repo = LLMRepository(db)
        self.time_service = TimeConvertService()
        self.algorithm_service = FortuneAlgorithmService()
    
    async def get_daily_fortune(
        self,
        user_id: int,
        fortune_date: Optional[date] = None
    ) -> Optional[DailyFortune]:
        """获取每日运势"""
        if fortune_date is None:
            fortune_date = date.today()
        
        fortune = await self.repository.get_by_user_and_date(user_id, fortune_date)
        
        if fortune:
            return fortune
        
        return await self.generate_daily_fortune(user_id, fortune_date)
    
    async def generate_daily_fortune(
        self,
        user_id: int,
        fortune_date: date
    ) -> DailyFortune:
        """生成每日运势 - 使用传统算法 + LLM"""
        
        user_profile = await self.user_profile_repo.get_by_user_id(user_id)
        
        if not user_profile or not user_profile.birth_date:
            return await self._generate_default_fortune(user_id, fortune_date)
        
        user_animal = user_profile.animal or "鼠"
        user_birth_date = user_profile.birth_date
        user_zodiac = user_profile.zodiac_sign or "白羊座"
        
        time_info = self.time_service.get_daily_info(datetime.combine(fortune_date, datetime.min.time()))
        
        algorithm_data = self.algorithm_service.generate_fortune_data(
            user_animal=user_animal,
            user_birth_date=user_birth_date,
            fortune_date=fortune_date,
            time_info=time_info
        )
        
        prompt = await self._build_prompt_with_config(
            user_animal=user_animal,
            user_zodiac=user_zodiac,
            fortune_date=fortune_date,
            time_info=time_info,
            algorithm_data=algorithm_data
        )
        
        content = await self._generate_llm_content(prompt, algorithm_data)
        
        fortune_data = {
            "overall_score": algorithm_data["overall_score"],
            "wealth_score": algorithm_data["wealth_score"],
            "career_score": algorithm_data["career_score"],
            "love_score": algorithm_data["love_score"],
            "health_score": algorithm_data["health_score"],
            "lucky_color": algorithm_data["lucky_color"],
            "lucky_number": algorithm_data["lucky_number"],
            "lucky_direction": algorithm_data["lucky_direction"],
            "lucky_time": algorithm_data["lucky_time"],
            "content": content,
            "yi": ",".join(algorithm_data["yi"]),
            "ji": ",".join(algorithm_data["ji"])
        }
        
        try:
            fortune = await self.repository.create(
                user_id=user_id,
                fortune_date=fortune_date,
                **fortune_data
            )
            return fortune
        except IntegrityError:
            # 并发场景下可能已被其他请求写入同一天记录
            await self.db.rollback()
            existing_fortune = await self.repository.get_by_user_and_date(user_id, fortune_date)
            if existing_fortune:
                return existing_fortune
            raise
    
    async def _generate_llm_content(self, prompt: str, algorithm_data: Dict[str, Any]) -> str:
        """调用 LLM 生成内容"""
        try:
            prompt_config = await self.prompt_config_repo.get_by_scene_and_type(
                scene="daily_fortune",
                prompt_type="answer"
            )
            
            if prompt_config and prompt_config.llm_config_id:
                llm_config = await self.llm_repo.get_by_id(prompt_config.llm_config_id)
                
                if llm_config and llm_config.is_enabled:
                    llm_service = create_llm_service(
                        llm_config=llm_config,
                        temperature=prompt_config.temperature,
                        max_tokens=prompt_config.max_tokens,
                        timeout=prompt_config.timeout_seconds
                    )
                    
                    try:
                        llm_response = await llm_service.generate(prompt)
                        content = self._parse_llm_response(llm_response, algorithm_data)
                        return content
                    finally:
                        if hasattr(llm_service, 'close'):
                            await llm_service.close()
                raise RuntimeError("每日运势配置的LLM不可用或未启用")
            raise RuntimeError("未找到每日运势可用的Prompt/LLM配置")
            
        except Exception as e:
            logger.error(f"LLM 生成失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _build_prompt_with_config(
        self,
        user_animal: str,
        user_zodiac: str,
        fortune_date: date,
        time_info: Dict[str, Any],
        algorithm_data: Dict[str, Any]
    ) -> str:
        """使用 Prompt 配置构建 Prompt"""
        
        prompt_config = await self.prompt_config_repo.get_by_scene_and_type(
            scene="daily_fortune",
            prompt_type="answer"
        )
        
        if not prompt_config:
            return self._build_default_prompt(
                user_animal, user_zodiac, fortune_date, time_info, algorithm_data
            )
        
        solar_term = time_info.get("term", "无")
        festival = time_info.get("festival", "") or time_info.get("lunar_festival", "")
        if not festival:
            festival = "无"
        
        variables = {
            "user_animal": user_animal,
            "user_zodiac": user_zodiac,
            "user_wuxing": algorithm_data.get("user_wuxing", "未知"),
            "solar_date": fortune_date.strftime('%Y年%m月%d日'),
            "lunar_date": f"{time_info.get('lunar_month_cn', '')}{time_info.get('lunar_day_cn', '')}",
            "ganzhi_day": algorithm_data.get("ganzhi_day", ""),
            "day_wuxing": algorithm_data.get("day_wuxing", ""),
            "day_animal": algorithm_data.get("day_animal", ""),
            "solar_term": solar_term,
            "festival": festival,
            "overall_score": algorithm_data["overall_score"],
            "wealth_score": algorithm_data["wealth_score"],
            "career_score": algorithm_data["career_score"],
            "love_score": algorithm_data["love_score"],
            "health_score": algorithm_data["health_score"],
            "lucky_color": algorithm_data["lucky_color"],
            "lucky_number": algorithm_data["lucky_number"],
            "lucky_direction": algorithm_data["lucky_direction"],
            "lucky_time": algorithm_data["lucky_time"],
            "yi_list": "、".join(algorithm_data["yi"]),
            "ji_list": "、".join(algorithm_data["ji"])
        }
        
        prompt = prompt_config.template
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        return prompt
    
    def _build_default_prompt(
        self,
        user_animal: str,
        user_zodiac: str,
        fortune_date: date,
        time_info: Dict[str, Any],
        algorithm_data: Dict[str, Any]
    ) -> str:
        """构建默认 LLM Prompt（当没有配置时）"""
        solar_term = time_info.get("term", "")
        festival = time_info.get("festival", "") or time_info.get("lunar_festival", "")
        
        prompt = f"""你是一位精通命理的大师。请根据以下算法计算结果，生成今日运势解读。

【用户信息】
- 生肖：{user_animal}
- 星座：{user_zodiac}
- 五行：{algorithm_data['user_wuxing']}

【时间信息】
- 日期：{fortune_date.strftime('%Y年%m月%d日')}
- 农历：{time_info.get('lunar_month_cn', '')}{time_info.get('lunar_day_cn', '')}
- 干支：{algorithm_data['ganzhi_day']}
- 日五行：{algorithm_data['day_wuxing']}
- 日生肖：{algorithm_data['day_animal']}
{f"- 节气：{solar_term}" if solar_term else ""}
{f"- 节日：{festival}" if festival else ""}

【算法计算结果】
- 综合评分：{algorithm_data['overall_score']}分（满分100）
- 财运评分：{algorithm_data['wealth_score']}分
- 事业评分：{algorithm_data['career_score']}分
- 感情评分：{algorithm_data['love_score']}分
- 健康评分：{algorithm_data['health_score']}分
- 幸运色：{algorithm_data['lucky_color']}
- 幸运数字：{algorithm_data['lucky_number']}
- 幸运方位：{algorithm_data['lucky_direction']}
- 幸运时辰：{algorithm_data['lucky_time']}
- 宜：{', '.join(algorithm_data['yi'])}
- 忌：{', '.join(algorithm_data['ji'])}

请根据以上信息，生成温暖、积极、有启发性的运势解读。要求：
1. 总体运势（50-80字）：解释为什么会有这样的评分，结合五行生克和生肖关系
2. 财运解读（30-50字）：基于财运评分给出建议
3. 事业解读（30-50字）：基于事业评分给出建议
4. 感情解读（30-50字）：基于感情评分给出建议
5. 健康解读（30-50字）：基于健康评分给出建议

请以JSON格式返回：
{{
  "summary": "总体运势解读",
  "wealth": "财运解读",
  "career": "事业解读",
  "love": "感情解读",
  "health": "健康解读"
}}"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, algorithm_data: Dict[str, Any]) -> str:
        """解析 LLM 响应"""
        try:
            json_str = response
            
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                if end > start:
                    json_str = response[start:end].strip()
            elif '```' in response:
                start = response.find('```') + 3
                end = response.find('```', start)
                if end > start:
                    json_str = response[start:end].strip()
            elif '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
            
            data = json.loads(json_str)
            
            content_parts = [
                f"【综合运势 {algorithm_data['overall_score']}分】",
                data.get("summary", ""),
                "",
                f"【财运 {algorithm_data['wealth_score']}分】",
                data.get("wealth", ""),
                "",
                f"【事业 {algorithm_data['career_score']}分】",
                data.get("career", ""),
                "",
                f"【感情 {algorithm_data['love_score']}分】",
                data.get("love", ""),
                "",
                f"【健康 {algorithm_data['health_score']}分】",
                data.get("health", "")
            ]
            
            return "\n".join(content_parts)
        except Exception as e:
            logger.warning(f"JSON 解析失败: {e}, 返回原始响应")
            if response:
                return response
            raise RuntimeError("LLM返回为空，无法生成每日运势内容")
    
    def _generate_default_content(self, algorithm_data: Dict[str, Any]) -> str:
        """生成默认内容（当 LLM 失败时）"""
        score = algorithm_data['overall_score']
        
        if score >= 80:
            summary = "今日运势极佳，诸事顺利。五行相生，生肖相合，是行动的好时机。"
        elif score >= 60:
            summary = "今日运势良好，平稳发展。保持积极心态，稳中求进。"
        elif score >= 40:
            summary = "今日运势平平，需谨慎行事。注意五行相克，避免冲动决策。"
        else:
            summary = "今日运势欠佳，宜静不宜动。调整心态，等待时机。"
        
        content_parts = [
            f"【综合运势 {score}分】",
            summary,
            "",
            f"【财运 {algorithm_data['wealth_score']}分】",
            "财运方面需要根据五行关系调整策略。",
            "",
            f"【事业 {algorithm_data['career_score']}分】",
            "事业方面保持稳定，注意人际关系。",
            "",
            f"【感情 {algorithm_data['love_score']}分】",
            "感情方面需要多沟通，增进理解。",
            "",
            f"【健康 {algorithm_data['health_score']}分】",
            "健康方面注意作息，保持良好习惯。"
        ]
        
        return "\n".join(content_parts)
    
    async def _generate_default_fortune(
        self,
        user_id: int,
        fortune_date: date
    ) -> DailyFortune:
        """生成默认运势（用户无档案时）"""
        fortune_data = {
            "overall_score": 70,
            "love_score": 70,
            "career_score": 70,
            "wealth_score": 70,
            "health_score": 70,
            "lucky_color": "白色",
            "lucky_number": 8,
            "lucky_direction": "东",
            "lucky_time": "辰时(07:00-09:00)",
            "content": "今日运势平稳，诸事顺利。建议完善个人档案以获得更精准的运势分析。",
            "yi": "祈福,沐浴,扫舍",
            "ji": "诸事不宜"
        }
        
        try:
            fortune = await self.repository.create(
                user_id=user_id,
                fortune_date=fortune_date,
                **fortune_data
            )
            return fortune
        except IntegrityError:
            # 并发场景下可能已被其他请求写入同一天记录
            await self.db.rollback()
            existing_fortune = await self.repository.get_by_user_and_date(user_id, fortune_date)
            if existing_fortune:
                return existing_fortune
            raise
    
    async def list_user_fortunes(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 30
    ) -> list[DailyFortune]:
        """获取用户的运势历史"""
        return await self.repository.list_by_user(user_id, skip, limit)
