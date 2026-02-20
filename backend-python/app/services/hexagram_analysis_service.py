"""变卦关系深度分析服务"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Trigram:
    """八卦定义"""
    name: str  # 卦名：乾、坤、震、巽、坎、离、艮、兑
    symbol: str  # 符号：☰ ☷ ☳ ☴ ☵ ☲ ☶ ☱
    yin_yang: List[bool]  # 三爻：True=阳爻(—), False=阴爻(--)
    wuxing: str  # 五行属性：金、木、水、火、土
    direction: str  # 方位
    number: int  # 八卦序号（1-8）


@dataclass
class HexagramInfo:
    """六十四卦信息"""
    number: int  # 卦序号（1-64）
    name: str  # 卦名
    upper_trigram: str  # 上卦
    lower_trigram: str  # 下卦
    outcome: str  # 吉凶：吉、凶、平
    summary: str  # 卦辞摘要
    detail: str  # 详细解释
    wuxing: str  # 五行属性


@dataclass
class ChangedHexagram:
    """变卦结构"""
    original_hexagram: HexagramInfo  # 本卦
    changed_hexagram: HexagramInfo  # 变卦
    changed_lines: List[int]  # 变爻位置（0-5）
    relationship: str  # 本卦和变卦的关系分析


class HexagramAnalysisService:
    """变卦关系深度分析服务"""
    
    # 八卦数据
    TRIGRAMS = [
        Trigram("乾", "☰", [True, True, True], "金", "西北", 1),
        Trigram("坤", "☷", [False, False, False], "土", "西南", 2),
        Trigram("震", "☳", [True, False, False], "木", "东", 3),
        Trigram("巽", "☴", [False, True, True], "木", "东南", 4),
        Trigram("坎", "☵", [False, True, False], "水", "北", 5),
        Trigram("离", "☲", [True, False, True], "火", "南", 6),
        Trigram("艮", "☶", [False, False, True], "土", "东北", 7),
        Trigram("兑", "☱", [True, True, False], "金", "西", 8),
    ]
    
    # 五行生克关系
    WUXING_RELATIONSHIPS = {
        "木": {"火": "生", "土": "克", "金": "被克", "水": "被生", "木": "比和"},
        "火": {"土": "生", "金": "克", "水": "被克", "木": "被生", "火": "比和"},
        "土": {"金": "生", "水": "克", "木": "被克", "火": "被生", "土": "比和"},
        "金": {"水": "生", "木": "克", "火": "被克", "土": "被生", "金": "比和"},
        "水": {"木": "生", "火": "克", "土": "被克", "金": "被生", "水": "比和"},
    }
    
    @staticmethod
    def analyze_hexagram_relationship(
        original: HexagramInfo,
        changed: HexagramInfo,
        changing_count: int
    ) -> str:
        """
        分析本卦和变卦的关系
        
        Args:
            original: 本卦信息
            changed: 变卦信息
            changing_count: 变爻数量
        
        Returns:
            str: 关系分析文本
        """
        lines = []
        
        lines.append("## 变卦分析\n")
        
        # 基本信息
        lines.append(f"**本卦**：{original.name}（第{original.number}卦）")
        lines.append(f"**变卦**：{changed.name}（第{changed.number}卦）\n")
        
        # 变爻数量分析
        lines.append(f"**变爻数量**：{changing_count}爻\n")
        
        # 根据变爻数量给出不同解释
        changing_analysis = HexagramAnalysisService._analyze_changing_count(changing_count)
        lines.append(changing_analysis)
        
        # 本卦和变卦的关系
        if original.number == changed.number:
            lines.append("**关系**：本卦与变卦相同，表示虽有变爻，但整体卦象未变，变化在内部。\n")
        else:
            # 分析上下卦的变化
            relationship_analysis = HexagramAnalysisService._analyze_trigram_change(
                original, changed
            )
            lines.append(relationship_analysis)
            
            # 五行关系分析
            if original.wuxing and changed.wuxing:
                wuxing_analysis = HexagramAnalysisService._analyze_wuxing_change(
                    original.wuxing, changed.wuxing
                )
                lines.append(f"**五行变化**：本卦{original.wuxing} → 变卦{changed.wuxing}")
                lines.append(wuxing_analysis + "\n")
        
        # 综合建议
        advice = HexagramAnalysisService._generate_advice(changing_count)
        lines.append("**综合建议**：")
        lines.append(advice)
        
        return "\n".join(lines)
    
    @staticmethod
    def _analyze_changing_count(count: int) -> str:
        """根据变爻数量分析"""
        analyses = {
            0: "**无变爻**：静卦，表示事情稳定，变化不大。\n",
            1: "**一变爻**：表示事情有小的变化，但整体趋势不变。变爻所在位置提示需要注意的方面。\n",
            2: "**二变爻**：表示事情有中等程度的变化，需要关注变爻提示的两个方面。\n",
            3: "**三变爻**：表示事情有较大变化，本卦和变卦都需要参考，以变卦为主。\n",
            4: "**四变爻**：表示事情变化很大，以变卦为主，本卦为辅。\n",
            5: "**五变爻**：表示事情变化极大，几乎完全转向变卦所示的方向。\n",
            6: "**六变爻**：表示完全变化，本卦已转为变卦，以变卦为准。\n",
        }
        return analyses.get(count, "**变爻异常**：需要重新占卜。\n")
    
    @staticmethod
    def _analyze_trigram_change(original: HexagramInfo, changed: HexagramInfo) -> str:
        """分析上下卦的变化"""
        upper_changed = original.upper_trigram != changed.upper_trigram
        lower_changed = original.lower_trigram != changed.lower_trigram
        
        if upper_changed and lower_changed:
            return "**关系**：上下卦皆变，表示事情发生根本性变化，需要重新审视。\n"
        elif upper_changed:
            return "**关系**：上卦变化，表示外部环境或结果方向发生变化。\n"
        elif lower_changed:
            return "**关系**：下卦变化，表示内在基础或起因发生变化。\n"
        else:
            return "**关系**：上下卦未变，但内部爻位有变化。\n"
    
    @staticmethod
    def _analyze_wuxing_change(original_wuxing: str, changed_wuxing: str) -> str:
        """分析五行变化"""
        if original_wuxing == changed_wuxing:
            return f"{original_wuxing}与{changed_wuxing}相同，五行不变，主稳定。"
        
        relationships = HexagramAnalysisService.WUXING_RELATIONSHIPS
        if original_wuxing in relationships and changed_wuxing in relationships[original_wuxing]:
            rel = relationships[original_wuxing][changed_wuxing]
            
            if rel == "生":
                return f"{original_wuxing}生{changed_wuxing}，本卦生变卦，主吉，变化顺利。"
            elif rel == "克":
                return f"{original_wuxing}克{changed_wuxing}，本卦克变卦，主阻，变化有阻力。"
            elif rel == "被生":
                return f"{original_wuxing}被{changed_wuxing}生，变卦生本卦，主吉，得助力。"
            elif rel == "被克":
                return f"{original_wuxing}被{changed_wuxing}克，变卦克本卦，主凶，需谨慎。"
        
        return "五行关系复杂，需综合分析。"
    
    @staticmethod
    def _generate_advice(changing_count: int) -> str:
        """根据变爻数量生成建议"""
        if changing_count <= 2:
            return """- 以本卦为主，参考变卦提示的变化
- 关注变爻所在位置的具体含义
- 事情会有小到中等程度的变化"""
        elif changing_count <= 4:
            return """- 本卦和变卦都需要重视
- 事情正在发生较大变化
- 需要同时考虑现状和未来趋势"""
        else:
            return """- 以变卦为主，本卦为辅
- 事情将发生根本性变化
- 需要做好应对重大变化的准备"""
    
    @staticmethod
    def analyze_wuxing_relationship(lower_wuxing: str, upper_wuxing: str) -> str:
        """
        分析上下卦的五行关系
        
        Args:
            lower_wuxing: 下卦五行
            upper_wuxing: 上卦五行
        
        Returns:
            str: 五行关系分析
        """
        if lower_wuxing == upper_wuxing:
            return f"{lower_wuxing}与{upper_wuxing}比和，上下卦同类，主平，宜稳中求进。"
        
        relationships = HexagramAnalysisService.WUXING_RELATIONSHIPS
        if lower_wuxing in relationships and upper_wuxing in relationships[lower_wuxing]:
            rel = relationships[lower_wuxing][upper_wuxing]
            
            if rel == "生":
                return f"{lower_wuxing}生{upper_wuxing}，下卦生上卦，主吉，但需循序渐进。"
            elif rel == "克":
                return f"{lower_wuxing}克{upper_wuxing}，下卦克上卦，主阻，需化解矛盾。"
            elif rel == "被生":
                return f"{lower_wuxing}被{upper_wuxing}生，上卦生下卦，主吉，得贵人相助。"
            elif rel == "被克":
                return f"{lower_wuxing}被{upper_wuxing}克，上卦克下卦，主凶，需谨慎应对。"
            elif rel == "比和":
                return f"{lower_wuxing}与{upper_wuxing}比和，上下卦同类，主平，宜稳中求进。"
        
        return "五行关系复杂，需综合分析。"
    
    @staticmethod
    def get_trigram_by_number(number: int) -> Optional[Trigram]:
        """根据序号获取八卦"""
        for trigram in HexagramAnalysisService.TRIGRAMS:
            if trigram.number == number:
                return trigram
        return None
    
    @staticmethod
    def get_trigram_by_name(name: str) -> Optional[Trigram]:
        """根据名称获取八卦"""
        for trigram in HexagramAnalysisService.TRIGRAMS:
            if trigram.name == name:
                return trigram
        return None
    
    @staticmethod
    def analyze_line_position(position: int) -> str:
        """
        分析爻位的含义
        
        Args:
            position: 爻位（0-5，从下往上）
        
        Returns:
            str: 爻位含义
        """
        positions = {
            0: "初爻：事情的开始，基础阶段，宜谨慎布局。",
            1: "二爻：事情的发展，中间阶段，宜稳步推进。",
            2: "三爻：事情的转折，关键阶段，宜审时度势。",
            3: "四爻：事情的高潮，重要阶段，宜把握时机。",
            4: "五爻：事情的成熟，关键阶段，宜果断决策。",
            5: "上爻：事情的结束，收尾阶段，宜善始善终。",
        }
        return positions.get(position, "爻位异常")
    
    @staticmethod
    def calculate_hexagram_compatibility(
        hexagram1: HexagramInfo,
        hexagram2: HexagramInfo
    ) -> Dict[str, any]:
        """
        计算两个卦象的相容性
        
        Args:
            hexagram1: 第一个卦象
            hexagram2: 第二个卦象
        
        Returns:
            Dict: 相容性分析结果
        """
        # 五行相容性
        wuxing_compat = 0
        if hexagram1.wuxing == hexagram2.wuxing:
            wuxing_compat = 100  # 相同五行，完全相容
        else:
            relationships = HexagramAnalysisService.WUXING_RELATIONSHIPS
            if hexagram1.wuxing in relationships and hexagram2.wuxing in relationships[hexagram1.wuxing]:
                rel = relationships[hexagram1.wuxing][hexagram2.wuxing]
                if rel == "生" or rel == "被生":
                    wuxing_compat = 80  # 相生，高度相容
                elif rel == "比和":
                    wuxing_compat = 100  # 比和，完全相容
                elif rel == "克" or rel == "被克":
                    wuxing_compat = 30  # 相克，低度相容
        
        # 吉凶相容性
        outcome_compat = 0
        if hexagram1.outcome == hexagram2.outcome:
            outcome_compat = 100
        elif (hexagram1.outcome == "吉" and hexagram2.outcome == "平") or \
             (hexagram1.outcome == "平" and hexagram2.outcome == "吉"):
            outcome_compat = 70
        else:
            outcome_compat = 40
        
        # 综合相容性
        overall_compat = (wuxing_compat * 0.6 + outcome_compat * 0.4)
        
        return {
            "wuxing_compatibility": wuxing_compat,
            "outcome_compatibility": outcome_compat,
            "overall_compatibility": overall_compat,
            "level": "高" if overall_compat >= 70 else "中" if overall_compat >= 50 else "低"
        }

