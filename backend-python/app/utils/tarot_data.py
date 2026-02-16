"""塔罗牌数据"""

from typing import List

# 78张标准韦特塔罗牌（简化版，实际应该有完整数据）
TAROT_CARDS = [
    # 大阿卡纳（22张）
    {'number': 0, 'name': '愚者', 'name_en': 'The Fool', 'arcana': 'major', 'meaning': '新的开始，冒险精神，天真无邪', 'reversed': '鲁莽，缺乏计划，逃避责任'},
    {'number': 1, 'name': '魔术师', 'name_en': 'The Magician', 'arcana': 'major', 'meaning': '创造力，技能，意志力', 'reversed': '操纵，欺骗，缺乏能力'},
    {'number': 2, 'name': '女祭司', 'name_en': 'The High Priestess', 'arcana': 'major', 'meaning': '直觉，神秘，内在智慧', 'reversed': '隐藏的秘密，缺乏洞察力'},
    {'number': 3, 'name': '皇后', 'name_en': 'The Empress', 'arcana': 'major', 'meaning': '丰饶，母性，自然', 'reversed': '依赖，空虚，缺乏成长'},
    {'number': 4, 'name': '皇帝', 'name_en': 'The Emperor', 'arcana': 'major', 'meaning': '权威，结构，控制', 'reversed': '专制，僵化，缺乏纪律'},
    {'number': 5, 'name': '教皇', 'name_en': 'The Hierophant', 'arcana': 'major', 'meaning': '传统，精神指导，教育', 'reversed': '反叛，非传统，个人信仰'},
    {'number': 6, 'name': '恋人', 'name_en': 'The Lovers', 'arcana': 'major', 'meaning': '爱情，和谐，选择', 'reversed': '失衡，冲突，错误选择'},
    {'number': 7, 'name': '战车', 'name_en': 'The Chariot', 'arcana': 'major', 'meaning': '胜利，意志力，决心', 'reversed': '失控，缺乏方向，侵略'},
    {'number': 8, 'name': '力量', 'name_en': 'Strength', 'arcana': 'major', 'meaning': '勇气，耐心，内在力量', 'reversed': '软弱，自我怀疑，缺乏信心'},
    {'number': 9, 'name': '隐者', 'name_en': 'The Hermit', 'arcana': 'major', 'meaning': '内省，寻找真理，孤独', 'reversed': '孤立，逃避，迷失'},
    {'number': 10, 'name': '命运之轮', 'name_en': 'Wheel of Fortune', 'arcana': 'major', 'meaning': '变化，命运，机遇', 'reversed': '厄运，抗拒变化，失控'},
    {'number': 11, 'name': '正义', 'name_en': 'Justice', 'arcana': 'major', 'meaning': '公平，真理，因果', 'reversed': '不公，偏见，逃避责任'},
    {'number': 12, 'name': '倒吊人', 'name_en': 'The Hanged Man', 'arcana': 'major', 'meaning': '牺牲，放手，新视角', 'reversed': '拖延，抗拒，无谓牺牲'},
    {'number': 13, 'name': '死神', 'name_en': 'Death', 'arcana': 'major', 'meaning': '结束，转变，重生', 'reversed': '抗拒改变，停滞，恐惧'},
    {'number': 14, 'name': '节制', 'name_en': 'Temperance', 'arcana': 'major', 'meaning': '平衡，耐心，和谐', 'reversed': '失衡，过度，缺乏耐心'},
    {'number': 15, 'name': '恶魔', 'name_en': 'The Devil', 'arcana': 'major', 'meaning': '束缚，诱惑，物质主义', 'reversed': '解脱，觉醒，摆脱束缚'},
    {'number': 16, 'name': '塔', 'name_en': 'The Tower', 'arcana': 'major', 'meaning': '突变，混乱，启示', 'reversed': '逃避灾难，恐惧改变，延迟'},
    {'number': 17, 'name': '星星', 'name_en': 'The Star', 'arcana': 'major', 'meaning': '希望，灵感，宁静', 'reversed': '绝望，缺乏信心，失去方向'},
    {'number': 18, 'name': '月亮', 'name_en': 'The Moon', 'arcana': 'major', 'meaning': '幻觉，恐惧，潜意识', 'reversed': '释放恐惧，真相揭示，直觉'},
    {'number': 19, 'name': '太阳', 'name_en': 'The Sun', 'arcana': 'major', 'meaning': '成功，喜悦，活力', 'reversed': '过度乐观，延迟成功，沮丧'},
    {'number': 20, 'name': '审判', 'name_en': 'Judgement', 'arcana': 'major', 'meaning': '觉醒，更新，决定', 'reversed': '自我怀疑，拒绝改变，内疚'},
    {'number': 21, 'name': '世界', 'name_en': 'The World', 'arcana': 'major', 'meaning': '完成，成就，旅程结束', 'reversed': '未完成，缺乏闭环，延迟'},
    
    # 小阿卡纳 - 权杖（简化，只列举几张）
    {'number': 22, 'name': '权杖王牌', 'name_en': 'Ace of Wands', 'arcana': 'minor', 'suit': 'wands', 'meaning': '新的开始，灵感，创造力', 'reversed': '缺乏方向，延迟，挫折'},
    {'number': 23, 'name': '权杖二', 'name_en': 'Two of Wands', 'arcana': 'minor', 'suit': 'wands', 'meaning': '计划，决策，发现', 'reversed': '犹豫不决，恐惧未知，缺乏计划'},
]


def get_spread_positions(spread: str) -> List[str]:
    """获取牌阵位置"""
    spreads = {
        'single': ['当前'],
        'three': ['过去', '现在', '未来'],
        'cross': ['现状', '障碍', '目标', '基础', '过去', '未来', '自己', '环境', '希望/恐惧', '结果'],
    }
    return spreads.get(spread, ['当前'])
