"""卦象数据"""

# 八卦定义
TRIGRAMS = [
    {'number': 1, 'name': '乾', 'symbol': '☰', 'yin_yang': [True, True, True], 'wuxing': '金', 'direction': '西北'},
    {'number': 2, 'name': '坤', 'symbol': '☷', 'yin_yang': [False, False, False], 'wuxing': '土', 'direction': '西南'},
    {'number': 3, 'name': '震', 'symbol': '☳', 'yin_yang': [True, False, False], 'wuxing': '木', 'direction': '东'},
    {'number': 4, 'name': '巽', 'symbol': '☴', 'yin_yang': [False, True, True], 'wuxing': '木', 'direction': '东南'},
    {'number': 5, 'name': '坎', 'symbol': '☵', 'yin_yang': [False, True, False], 'wuxing': '水', 'direction': '北'},
    {'number': 6, 'name': '离', 'symbol': '☲', 'yin_yang': [True, False, True], 'wuxing': '火', 'direction': '南'},
    {'number': 7, 'name': '艮', 'symbol': '☶', 'yin_yang': [False, False, True], 'wuxing': '土', 'direction': '东北'},
    {'number': 8, 'name': '兑', 'symbol': '☱', 'yin_yang': [True, True, False], 'wuxing': '金', 'direction': '西'},
]

# 六十四卦定义（简化版，实际应该有完整的64卦）
HEXAGRAMS = [
    {'number': 1, 'name': '乾', 'upper': '乾', 'lower': '乾', 'outcome': '吉', 'summary': '元亨利贞，大吉之象', 'detail': '乾卦，纯阳之卦。天行健，君子以自强不息。', 'wuxing': '金'},
    {'number': 2, 'name': '坤', 'upper': '坤', 'lower': '坤', 'outcome': '吉', 'summary': '厚德载物，柔顺之象', 'detail': '坤卦，纯阴之卦。地势坤，君子以厚德载物。', 'wuxing': '土'},
    {'number': 3, 'name': '屯', 'upper': '坎', 'lower': '震', 'outcome': '平', 'summary': '初始艰难，需耐心等待', 'detail': '屯卦，象征初生之难。宜守不宜攻。', 'wuxing': '水'},
    # ... 其他61卦（为简化先省略）
]

# 补充默认卦象（当数据库中没有时使用）
def get_hexagram_by_number(number: int) -> dict:
    """根据卦序号获取卦象信息"""
    for hexagram in HEXAGRAMS:
        if hexagram['number'] == number:
            return hexagram
    
    # 如果没有找到，返回默认卦象
    return {
        'number': number,
        'name': f'第{number}卦',
        'upper': '未知',
        'lower': '未知',
        'outcome': '平',
        'summary': '此卦需详细分析',
        'detail': '卦象信息待完善',
        'wuxing': '未知',
    }
