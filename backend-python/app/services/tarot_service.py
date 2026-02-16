"""塔罗牌服务"""

import hashlib
import random
from typing import List, Dict, Any, Tuple
from app.utils.tarot_data import TAROT_CARDS, get_spread_positions


class TarotService:
    """塔罗牌服务"""
    
    @staticmethod
    def draw_cards(session_id: str, spread: str = "single") -> Tuple[List[Dict], List[str]]:
        """
        抽牌
        返回：(抽到的牌列表, 位置列表)
        """
        # 根据牌阵确定抽牌数量和位置
        positions = get_spread_positions(spread)
        count = len(positions)
        
        # 使用session_id作为随机种子，确保可重现
        hash_value = int(hashlib.md5(session_id.encode()).hexdigest(), 16)
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
    
    @staticmethod
    def generate_result(session_id: str, question: str, spread: str = "single") -> Dict[str, Any]:
        """生成完整的塔罗占卜结果"""
        # 抽牌
        cards, positions = TarotService.draw_cards(session_id, spread)
        
        # 构建摘要
        summary = TarotService._build_summary(cards, positions)
        
        # 构建详细解释
        detail = TarotService._build_detail(cards, positions, spread)
        
        # 转换为响应格式
        card_list = []
        for i, card in enumerate(cards):
            card_list.append({
                'name': card['name'],
                'name_en': card.get('name_en', ''),
                'position': positions[i] if i < len(positions) else '当前',
                'is_reversed': card.get('is_reversed', False),
                'meaning': card.get('meaning', ''),
            })
        
        return {
            'session_id': session_id,
            'spread': spread,
            'cards': card_list,
            'summary': summary,
            'detail': detail,
        }
    
    @staticmethod
    def _build_summary(cards: List[Dict], positions: List[str]) -> str:
        """构建摘要"""
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
        """构建详细解释"""
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
