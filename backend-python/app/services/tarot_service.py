"""塔罗牌服务"""

import hashlib
import random
import json
from typing import List, Dict, Any, Tuple, Optional
from app.utils.tarot_data import TAROT_CARDS, get_spread_positions

from app.core.logger import get_logger
logger = get_logger("tarot")



class TarotService:
    """塔罗牌服务"""
    
    def __init__(self, llm_service=None, prompt_repo=None, llm_repo=None):
        """初始化塔罗牌服务
        
        Args:
            llm_service: LLM服务实例（可选）
            prompt_repo: Prompt配置仓库（可选）
            llm_repo: LLM配置仓库（可选）
        """
        self.llm_service = llm_service
        self.prompt_repo = prompt_repo
        self.llm_repo = llm_repo
    
    @staticmethod
    def draw_cards(session_seed: str, spread: str = "single") -> Tuple[List[Dict], List[str]]:
        """
        抽牌
        返回：(抽到的牌列表, 位置列表)
        """
        # 根据牌阵确定抽牌数量和位置
        positions = get_spread_positions(spread)
        count = len(positions)

        # 使用 session_seed 作为随机种子，确保可重现
        hash_value = int(hashlib.md5(session_seed.encode()).hexdigest(), 16)
        rng = random.Random(hash_value)
        
        # 随机抽取不重复的牌
        all_cards = list(TAROT_CARDS)
        selected_indices = rng.sample(range(len(all_cards)), count)
        
        cards = []
        for idx in selected_indices:
            card = all_cards[idx].copy()
            # 50%概率逆位
            is_reversed = rng.random() < 0.5
            if is_reversed:
                card['is_reversed'] = True
                card['name'] = card['name'] + '（逆位）'
            else:
                card['is_reversed'] = False
            cards.append(card)
        
        return cards, positions
    
    async def generate_result(
        self,
        session_id: str,
        question: str,
        spread: str = "single",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成完整的塔罗占卜结果（支持LLM增强）"""
        session_seed = self._build_session_seed(session_id, question, spread, context)

        # 抽牌
        cards, positions = self.draw_cards(session_seed, spread)
        
        # 尝试使用LLM增强解读
        if self.llm_service and self.prompt_repo:
            try:
                enhanced_result = await self._enhance_with_llm(question, cards, positions, spread)
                if enhanced_result:
                    # 转换为响应格式
                    card_list = self._format_cards(cards, positions)
                    return {
                        'session_id': session_id,
                        'spread': spread,
                        'cards': card_list,
                        'summary': enhanced_result.get('summary', ''),
                        'detail': enhanced_result.get('detail', ''),
                    }
            except Exception as e:
                logger.warning(f"LLM增强失败，使用基础解读: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级：使用基础解读
        summary = self._build_summary(cards, positions)
        detail = self._build_detail(cards, positions, spread)
        card_list = self._format_cards(cards, positions)
        
        return {
            'session_id': session_id,
            'spread': spread,
            'cards': card_list,
            'summary': summary,
            'detail': detail,
        }
    
    @staticmethod
    def _build_session_seed(
        session_id: str,
        question: str,
        spread: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """构建塔罗抽牌种子，让用户交互（洗牌/切牌）可影响抽牌结果"""
        base = {
            "session_id": session_id,
            "question": question,
            "spread": spread,
        }

        # 仅提取与塔罗交互相关字段，避免种子受无关字段波动
        tarot_ctx = {}
        if context and isinstance(context, dict):
            interaction = context.get("tarot_interaction")
            if isinstance(interaction, dict):
                tarot_ctx = {
                    "cut_position": interaction.get("cut_position"),
                    "shuffle_trace": interaction.get("shuffle_trace", []),
                    "spread": interaction.get("spread"),
                }

        seed_payload = {"base": base, "tarot_interaction": tarot_ctx}
        seed_str = json.dumps(seed_payload, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(seed_str.encode()).hexdigest()

    async def _enhance_with_llm(self, question: str, cards: List[Dict], 
                                positions: List[str], spread: str) -> Optional[Dict[str, Any]]:
        """使用LLM增强塔罗牌解读"""
        logger.debug(f"开始LLM增强塔罗牌解读")
        
        # 获取Prompt配置
        prompt_config = await self.prompt_repo.get_by_scene_and_type("tarot", "answer")
        if not prompt_config:
            logger.warning(f"未找到塔罗牌Prompt配置")
            return None
        
        logger.debug(f"使用Prompt配置: {prompt_config.name}")
        
        # 构建牌面信息字符串
        cards_info = self._format_cards_for_prompt(cards, positions)
        
        # 构建Prompt
        spread_names = {
            'single': '单张牌',
            'three': '三张牌阵（过去/现在/未来）',
            'cross': '十字牌阵',
        }
        
        prompt = prompt_config.template.format(
            question=question,
            spread=spread_names.get(spread, '单张牌'),
            cards=cards_info
        )
        
        logger.debug(f"Prompt构建完成，长度: {len(prompt)}")
        
        # 获取LLM配置
        if prompt_config.llm_config_id and self.llm_repo:
            from app.services.llm_service import create_llm_service
            llm_config = await self.llm_repo.get_by_id(prompt_config.llm_config_id)
            if llm_config:
                llm = create_llm_service(
                    llm_config,
                    temperature=prompt_config.temperature,
                    max_tokens=prompt_config.max_tokens,
                    timeout=prompt_config.timeout_seconds
                )
            else:
                llm = self.llm_service
        else:
            llm = self.llm_service
        
        # 调用LLM
        try:
            logger.debug(f"调用LLM生成解读...")
            response = await llm.generate_answer(prompt)
            logger.debug(f"LLM返回结果，长度: {len(response)}")
            
            # 解析JSON响应
            parsed = self._parse_llm_response(response)
            if parsed:
                # 构建summary和detail
                summary = self._build_summary_from_llm(parsed)
                detail = self._build_detail_from_llm(parsed, cards, positions, spread)
                
                return {
                    'summary': summary,
                    'detail': detail,
                    'llm_raw': parsed
                }
            else:
                logger.warning(f"无法解析LLM响应")
                return None
                
        finally:
            if llm != self.llm_service and hasattr(llm, 'close'):
                await llm.close()
    
    def _format_cards_for_prompt(self, cards: List[Dict], positions: List[str]) -> str:
        """格式化牌面信息用于Prompt"""
        lines = []
        for i, card in enumerate(cards):
            pos = positions[i] if i < len(positions) else "当前"
            name = card['name']
            is_reversed = card.get('is_reversed', False)
            meaning = card.get('reversed' if is_reversed else 'meaning', '')
            
            lines.append(f"位置{i+1}【{pos}】: {name}")
            lines.append(f"  - 正逆位: {'逆位' if is_reversed else '正位'}")
            lines.append(f"  - 基础含义: {meaning}")
        
        return "\n".join(lines)
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析LLM的JSON响应"""
        logger.debug(f"开始解析LLM响应,长度: {len(response)}")
        
        try:
            # 尝试直接解析
            parsed = json.loads(response)
            logger.debug(f"直接解析成功")
            return parsed
        except json.JSONDecodeError as e:
            logger.debug(f"直接解析失败: {e}")
            
            # 尝试提取JSON代码块
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    logger.debug(f"从```json```代码块解析成功")
                    return parsed
                except Exception as e2:
                    logger.debug(f"从代码块解析失败: {e2}")
            
            # 尝试查找第一个完整的JSON对象
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    logger.debug(f"从正则匹配解析成功")
                    return parsed
                except Exception as e3:
                    logger.debug(f"从正则匹配解析失败: {e3}")
            
            logger.error(f"所有解析方法都失败")
            return None
    
    def _build_summary_from_llm(self, parsed: Dict[str, Any]) -> str:
        """从LLM解析结果构建摘要"""
        parts = []
        
        if 'overview' in parsed:
            parts.append(f"**牌面概览**\n{parsed['overview']}\n")
        
        if 'core_insight' in parsed:
            parts.append(f"**核心洞察**\n{parsed['core_insight']}\n")
        
        if 'conclusion' in parsed:
            parts.append(f"**总结**\n{parsed['conclusion']}")
        
        return "\n".join(parts) if parts else "塔罗牌为您揭示了重要的信息，请仔细思考牌面的含义。"
    
    def _build_detail_from_llm(self, parsed: Dict[str, Any], cards: List[Dict], 
                               positions: List[str], spread: str) -> str:
        """从LLM解析结果构建详细解读"""
        lines = ["# 塔罗牌占卜深度解读\n"]
        
        # 牌面概览
        if 'overview' in parsed:
            lines.append(f"## 牌面概览\n{parsed['overview']}\n")
        
        # 核心洞察
        if 'core_insight' in parsed:
            lines.append(f"## 核心洞察\n{parsed['core_insight']}\n")
        
        # 深度解读
        if 'deep_reading' in parsed:
            lines.append("## 深度解读\n")
            deep = parsed['deep_reading']
            
            if spread == 'three':
                if 'past' in deep:
                    lines.append(f"### 根源与过去\n{deep['past']}\n")
                if 'present' in deep:
                    lines.append(f"### 当前状况\n{deep['present']}\n")
                if 'future' in deep:
                    lines.append(f"### 发展趋势\n{deep['future']}\n")
            else:
                if 'single' in deep:
                    lines.append(f"{deep['single']}\n")
        
        # 牌面关联分析
        if 'card_correlation' in parsed:
            lines.append(f"## 牌面关联分析\n{parsed['card_correlation']}\n")
        
        # 具体建议
        if 'recommendations' in parsed and isinstance(parsed['recommendations'], list):
            lines.append("## 具体建议\n")
            for i, rec in enumerate(parsed['recommendations'], 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # 总结
        if 'conclusion' in parsed:
            lines.append(f"## 总结\n{parsed['conclusion']}")
        
        return "\n".join(lines)
    
    def _format_cards(self, cards: List[Dict], positions: List[str]) -> List[Dict[str, Any]]:
        """格式化牌面信息为响应格式"""
        card_list = []
        for i, card in enumerate(cards):
            card_list.append({
                'name': card['name'],
                'name_en': card.get('name_en', ''),
                'position': positions[i] if i < len(positions) else '当前',
                'is_reversed': card.get('is_reversed', False),
                'meaning': card.get('meaning', ''),
            })
        return card_list
    
    @staticmethod
    def _build_summary(cards: List[Dict], positions: List[str]) -> str:
        """构建基础摘要（降级方案）"""
        if not cards:
            return "未能完成占卜，请稍后再试。"
        
        lines = ["根据您抽出的牌面：\n"]
        for i, card in enumerate(cards):
            pos = positions[i] if i < len(positions) else "当前"
            meaning = card.get('meaning', '')
            if card.get('is_reversed'):
                meaning = card.get('reversed', meaning)
            
            # 截取前50个字符
            short_meaning = meaning[:50] + "..." if len(meaning) > 50 else meaning
            lines.append(f"**{pos} - {card['name']}**：{short_meaning}\n")
        
        lines.append("\n建议您保持开放的心态，结合牌面的指引，相信自己的直觉做出决定。")
        return "\n".join(lines)
    
    @staticmethod
    def _build_detail(cards: List[Dict], positions: List[str], spread: str) -> str:
        """构建基础详细解释（降级方案）"""
        lines = ["# 塔罗牌占卜解读\n"]
        
        spread_names = {
            'single': '单张牌',
            'three': '三张牌阵（过去/现在/未来）',
            'cross': '十字牌阵',
        }
        lines.append(f"**牌阵类型**：{spread_names.get(spread, '单张牌')}\n")
        
        for i, card in enumerate(cards):
            pos = positions[i] if i < len(positions) else "当前"
            lines.append(f"## {pos}: {card['name']}\n")
            
            meaning = card.get('meaning', '')
            if card.get('is_reversed'):
                meaning = card.get('reversed', meaning)
            
            lines.append(f"**含义**: {meaning}\n")
        
        lines.append("## 综合建议\n")
        lines.append("请结合每张牌的含义，思考它们与您问题的关联。")
        lines.append("塔罗牌为您提供了一个视角，但最终的决定权在您手中。")
        lines.append("相信您的直觉会指引您找到答案。")
        
        return "\n".join(lines)
