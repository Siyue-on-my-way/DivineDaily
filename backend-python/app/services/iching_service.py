"""周易六爻服务"""

import hashlib
from typing import List, Dict, Any, Tuple, Optional
from app.utils.hexagram_data import TRIGRAMS, HEXAGRAMS, get_hexagram_by_number

from app.core.logger import get_logger
logger = get_logger("iching")



class Line:
    """单条爻"""
    def __init__(self, value: int):
        self.value = value  # 6=老阴(变爻), 7=少阳, 8=少阴, 9=老阳(变爻)
        self.is_changing = value in [6, 9]  # 是否为变爻
        self.yin_yang = value in [7, 9]  # True=阳, False=阴


class SixLines:
    """六爻结构"""
    def __init__(self, lines: List[Line]):
        self.lines = lines  # 从下往上，6条爻
        self.upper_trigram = self._get_trigram(lines[3:6])  # 上卦
        self.lower_trigram = self._get_trigram(lines[0:3])  # 下卦
        self.hexagram_number = self._get_hexagram_number()
        self.changing_lines = [i for i, line in enumerate(lines) if line.is_changing]
    
    def _get_trigram(self, three_lines: List[Line]) -> int:
        """根据三爻确定八卦序号"""
        pattern = [line.yin_yang for line in three_lines]
        for trigram in TRIGRAMS:
            if trigram['yin_yang'] == pattern:
                return trigram['number']
        return 1  # 默认乾
    
    def _get_hexagram_number(self) -> int:
        """根据上下卦确定六十四卦序号"""
        # 简化实现：上卦序号*8 + 下卦序号
        number = (self.upper_trigram - 1) * 8 + self.lower_trigram
        return max(1, min(64, number))


class IChingService:
    """周易六爻服务"""
    
    @staticmethod
    def _hash_to_int(seed: str) -> int:
        """将种子字符串稳定映射为整数"""
        return int(hashlib.md5(seed.encode()).hexdigest(), 16)

    @staticmethod
    def _line_type(value: int) -> str:
        mapping = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}
        return mapping.get(value, "少阳")

    @staticmethod
    def cast_line(seed: str, line_index: int) -> int:
        """
        摇卦：模拟投掷3枚硬币，生成一爻
        返回值：6(老阴)、7(少阳)、8(少阴)、9(老阳)
        """
        # 使用不同的哈希种子来模拟3枚独立的硬币
        coins = []
        for i in range(3):
            hash_input = f"{seed}-coin{i+1}-{line_index}".encode()
            hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
            coins.append(hash_value % 2)  # 0=反面, 1=正面

        # 计算总和并映射到传统值
        coin_sum = sum(coins)
        mapping = {0: 6, 1: 7, 2: 8, 3: 9}  # 老阴、少阳、少阴、老阳
        return mapping.get(coin_sum, 7)

    @staticmethod
    def cast_line_dayan(seed: str, line_index: int) -> Tuple[int, Dict[str, Any]]:
        """使用大衍筮法（数字模拟）生成单爻，并返回过程记录"""
        stalks = 49
        changes: List[Dict[str, Any]] = []

        for step in range(1, 4):
            rand = IChingService._hash_to_int(f"{seed}-line-{line_index}-step-{step}")
            # 分两堆，保证左右都大于0
            left = (rand % (stalks - 1)) + 1
            right_before_hang = stalks - left

            # 挂一：从右手取1
            right_after_hang = right_before_hang - 1
            hang_one = 1

            left_remainder = left % 4 or 4
            right_remainder = right_after_hang % 4 or 4
            removed = hang_one + left_remainder + right_remainder
            stalks_after = stalks - removed

            changes.append({
                "step_index": step,
                "stalks_before": stalks,
                "left_pile": left,
                "right_pile_before_hang": right_before_hang,
                "right_hang_one": hang_one,
                "right_pile_after_hang": right_after_hang,
                "left_remainder": left_remainder,
                "right_remainder": right_remainder,
                "removed": removed,
                "stalks_after": stalks_after,
            })
            stalks = stalks_after

        # 三变后以 4 为基数映射到 6/7/8/9
        line_base = stalks // 4
        mapping = {6: 6, 7: 7, 8: 8, 9: 9}
        line_value = mapping.get(line_base, 7)

        trace = {
            "line_index": line_index + 1,
            "initial_stalks": 49,
            "changes": changes,
            "final_stalks": stalks,
            "line_value": line_value,
            "line_type": IChingService._line_type(line_value),
            "is_changing": line_value in [6, 9],
        }
        return line_value, trace
    
    @staticmethod
    def generate_six_lines(session_id: str, method: str = "dayan") -> Tuple[SixLines, Optional[Dict[str, Any]]]:
        """生成六爻，支持返回起卦过程记录"""
        lines = []
        yarrow_lines: List[Dict[str, Any]] = []

        for i in range(6):
            if method == "dayan":
                value, trace = IChingService.cast_line_dayan(session_id, i)
                yarrow_lines.append(trace)
            else:
                value = IChingService.cast_line(session_id, i)
            lines.append(Line(value))

        six_lines = SixLines(lines)
        yarrow_trace = None
        if method == "dayan":
            yarrow_trace = {
                "method": "dayan_yarrow",
                "total_stalks": 50,
                "effective_stalks": 49,
                "lines": yarrow_lines,
            }

        return six_lines, yarrow_trace
    
    @staticmethod
    def calculate_changed_hexagram(original: SixLines) -> SixLines:
        """计算变卦"""
        if not original.changing_lines:
            return original
        
        # 复制原始六爻并转换变爻
        changed_lines = []
        for i, line in enumerate(original.lines):
            if i in original.changing_lines:
                # 老阴(6)变阳(7)，老阳(9)变阴(8)
                new_value = 7 if line.value == 6 else 8
                changed_lines.append(Line(new_value))
            else:
                changed_lines.append(Line(line.value))
        
        return SixLines(changed_lines)
    
    @staticmethod
    def get_hexagram_info(six_lines: SixLines) -> Dict[str, Any]:
        """获取卦象信息"""
        hexagram = get_hexagram_by_number(six_lines.hexagram_number)
        
        # 获取上下卦信息
        upper = next((t for t in TRIGRAMS if t['number'] == six_lines.upper_trigram), TRIGRAMS[0])
        lower = next((t for t in TRIGRAMS if t['number'] == six_lines.lower_trigram), TRIGRAMS[0])
        
        # 构建详细解释
        detail = IChingService._build_detail(hexagram, upper, lower, six_lines)
        
        return {
            'number': hexagram['number'],
            'name': hexagram['name'],
            'upper_trigram': upper['name'],
            'lower_trigram': lower['name'],
            'outcome': hexagram['outcome'],
            'summary': hexagram['summary'],
            'detail': detail,
            'wuxing': hexagram.get('wuxing', ''),
            'changing_lines': six_lines.changing_lines,
            'line_values': [line.value for line in six_lines.lines],
        }
    
    @staticmethod
    def _build_detail(hexagram: Dict, upper: Dict, lower: Dict, six_lines: SixLines) -> str:
        """构建详细解释"""
        lines = []
        lines.append(f"# 卦象解析：{hexagram['name']}\n")
        lines.append(f"## 卦象结构")
        lines.append(f"上卦：{upper['name']} ({upper['symbol']}) - {upper['wuxing']}")
        lines.append(f"下卦：{lower['name']} ({lower['symbol']}) - {lower['wuxing']}\n")
        
        # 六爻展示
        lines.append("## 六爻")
        for i in range(5, -1, -1):
            line = six_lines.lines[i]
            symbol = "—" if line.yin_yang else "--"
            changing = ""
            if line.is_changing:
                changing = " (老阴，变阳)" if line.value == 6 else " (老阳，变阴)"
            lines.append(f"第{i+1}爻：{symbol}{changing} (值：{line.value})")
        
        lines.append("")
        
        # 变爻分析
        if six_lines.changing_lines:
            lines.append("## 变爻")
            positions = [f"第{i+1}爻" for i in six_lines.changing_lines]
            lines.append(f"变爻：{', '.join(positions)}")
            
            # 计算变卦
            changed = IChingService.calculate_changed_hexagram(six_lines)
            changed_hexagram = get_hexagram_by_number(changed.hexagram_number)
            lines.append(f"\n变卦：{changed_hexagram['name']}（第{changed_hexagram['number']}卦）")
            lines.append(IChingService._analyze_relationship(hexagram, changed_hexagram, len(six_lines.changing_lines)))
        
        lines.append("")
        
        # 卦辞
        if hexagram.get('detail'):
            lines.append("## 卦辞")
            lines.append(hexagram['detail'])
        
        lines.append("")
        
        # 运势判断
        lines.append("## 运势")
        lines.append(f"总体判断：{hexagram['outcome']}")
        lines.append(hexagram['summary'])
        
        return "\n".join(lines)
    
    @staticmethod
    def _analyze_relationship(original: Dict, changed: Dict, changing_count: int) -> str:
        """分析本卦和变卦的关系"""
        lines = []
        
        if changing_count == 1:
            lines.append("一变爻：表示事情有小的变化，但整体趋势不变。")
        elif changing_count == 2:
            lines.append("二变爻：表示事情有中等程度的变化。")
        elif changing_count == 3:
            lines.append("三变爻：表示事情有较大变化，本卦和变卦都需要参考。")
        elif changing_count >= 4:
            lines.append("多变爻：表示事情变化很大，以变卦为主。")
        
        if original['number'] != changed['number']:
            lines.append(f"\n本卦{original['name']}转为变卦{changed['name']}，")
            lines.append(f"从{original['outcome']}转向{changed['outcome']}。")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_result(session_id: str, question: str, method: str = "dayan") -> Dict[str, Any]:
        """生成完整的周易占卜结果"""
        # 生成六爻
        six_lines, yarrow_trace = IChingService.generate_six_lines(session_id, method=method)

        # 获取卦象信息
        hexagram_info = IChingService.get_hexagram_info(six_lines)

        return {
            'session_id': session_id,
            'outcome': hexagram_info['outcome'],
            'title': hexagram_info['name'],
            'summary': hexagram_info['summary'],
            'detail': hexagram_info['detail'],
            'hexagram_info': hexagram_info,
            'yarrow_trace': yarrow_trace,
        }
