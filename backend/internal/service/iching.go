package service

import (
	"divine-daily-backend/internal/database"
	"divine-daily-backend/internal/model"
	"fmt"
	"hash/fnv"
	"strings"
	"time"
)

// 八卦定义
type Trigram struct {
	Name      string // 卦名：乾、坤、震、巽、坎、离、艮、兑
	Symbol    string // 符号表示：☰ ☷ ☳ ☴ ☵ ☲ ☶ ☱
	YinYang   []bool // 三爻：true=阳爻(—), false=阴爻(--)
	Wuxing    string // 五行属性：金、木、水、火、土
	Direction string // 方位
	Number    int    // 八卦序号（1-8）
}

// 六十四卦定义
type Hexagram struct {
	Number       int    // 卦序号（1-64）
	Name         string // 卦名
	UpperTrigram string // 上卦
	LowerTrigram string // 下卦
	Outcome      string // 吉凶：吉、凶、平
	Summary      string // 卦辞摘要
	Detail       string // 详细解释
	Wuxing       string // 五行属性
}

// 变卦结构
type ChangedHexagram struct {
	OriginalHexagram Hexagram // 本卦
	ChangedHexagram  Hexagram // 变卦
	ChangedLines     []int    // 变爻位置（0-5）
	Relationship     string   // 本卦和变卦的关系分析
}

// 六爻结构
type SixLines struct {
	Lines          []Line // 从下往上，6条爻
	UpperTrigram   int    // 上卦序号（1-8）
	LowerTrigram   int    // 下卦序号（1-8）
	HexagramNumber int    // 六十四卦序号（1-64）
	ChangingLines  []int  // 变爻位置（0-5）
}

// 单条爻
type Line struct {
	Value      int  // 6=老阴(变爻), 7=少阳, 8=少阴, 9=老阳(变爻)
	IsChanging bool // 是否为变爻
	YinYang    bool // true=阳, false=阴
}

var trigrams = []Trigram{
	{Name: "乾", Symbol: "☰", YinYang: []bool{true, true, true}, Wuxing: "金", Direction: "西北", Number: 1},
	{Name: "坤", Symbol: "☷", YinYang: []bool{false, false, false}, Wuxing: "土", Direction: "西南", Number: 2},
	{Name: "震", Symbol: "☳", YinYang: []bool{true, false, false}, Wuxing: "木", Direction: "东", Number: 3},
	{Name: "巽", Symbol: "☴", YinYang: []bool{false, true, true}, Wuxing: "木", Direction: "东南", Number: 4},
	{Name: "坎", Symbol: "☵", YinYang: []bool{false, true, false}, Wuxing: "水", Direction: "北", Number: 5},
	{Name: "离", Symbol: "☲", YinYang: []bool{true, false, true}, Wuxing: "火", Direction: "南", Number: 6},
	{Name: "艮", Symbol: "☶", YinYang: []bool{false, false, true}, Wuxing: "土", Direction: "东北", Number: 7},
	{Name: "兑", Symbol: "☱", YinYang: []bool{true, true, false}, Wuxing: "金", Direction: "西", Number: 8},
}

// 五行生克关系
var wuxingCycle = map[string]string{
	"金": "生水，克木",
	"木": "生火，克土",
	"水": "生木，克火",
	"火": "生土，克金",
	"土": "生金，克水",
}

// 摇卦：模拟投掷3枚硬币，生成一爻
// 返回值：6(老阴)、7(少阳)、8(少阴)、9(老阳)
// 传统方法：3枚硬币，每枚正面=3分，反面=2分
// 总和：6=老阴(变爻), 7=少阳, 8=少阴, 9=老阳(变爻)
// 传统概率：老阴(6)和老阳(9)各12.5%，少阳(7)和少阴(8)各37.5%
func castLine(seed string, lineIndex int) int {
	// 模拟3枚硬币投掷
	// 使用不同的哈希种子来模拟3枚独立的硬币
	h1 := fnv.New32a()
	h1.Write([]byte(fmt.Sprintf("%s-coin1-%d", seed, lineIndex)))
	coin1 := int(h1.Sum32() % 2) // 0=反面, 1=正面

	h2 := fnv.New32a()
	h2.Write([]byte(fmt.Sprintf("%s-coin2-%d", seed, lineIndex)))
	coin2 := int(h2.Sum32() % 2)

	h3 := fnv.New32a()
	h3.Write([]byte(fmt.Sprintf("%s-coin3-%d", seed, lineIndex)))
	coin3 := int(h3.Sum32() % 2)

	// 传统方法：正面=3分，反面=2分
	// 但为了简化，我们使用：正面=1，反面=0
	// 然后映射：0=6(老阴), 1=7(少阳), 2=8(少阴), 3=9(老阳)
	sum := coin1 + coin2 + coin3

	// 直接映射到传统值
	switch sum {
	case 0:
		return 6 // 老阴（变爻）- 3个反面
	case 1:
		return 7 // 少阳 - 1个正面
	case 2:
		return 8 // 少阴 - 2个正面
	case 3:
		return 9 // 老阳（变爻）- 3个正面
	default:
		return 7 // 默认少阳
	}
}

// 生成六爻
func generateSixLines(sessionID string) SixLines {
	var lines []Line
	var changingLines []int

	// 从下往上生成6条爻
	for i := 0; i < 6; i++ {
		value := castLine(sessionID, i)
		isChanging := value == 6 || value == 9 // 老阴或老阳为变爻
		yinYang := value == 7 || value == 9    // 7和9为阳爻

		lines = append(lines, Line{
			Value:      value,
			IsChanging: isChanging,
			YinYang:    yinYang,
		})

		if isChanging {
			changingLines = append(changingLines, i)
		}
	}

	// 计算下卦（下三爻）
	lowerTrigram := getTrigramByLines(lines[0:3])

	// 计算上卦（上三爻）
	upperTrigram := getTrigramByLines(lines[3:6])

	// 计算六十四卦序号
	hexagramNumber := getHexagramNumber(upperTrigram, lowerTrigram)

	return SixLines{
		Lines:          lines,
		UpperTrigram:   upperTrigram,
		LowerTrigram:   lowerTrigram,
		HexagramNumber: hexagramNumber,
		ChangingLines:  changingLines,
	}
}

// 根据三爻确定八卦
func getTrigramByLines(lines []Line) int {
	if len(lines) != 3 {
		return 1 // 默认乾
	}

	// 构建三爻的阴阳序列（从下往上）
	yinYang := []bool{
		lines[0].YinYang,
		lines[1].YinYang,
		lines[2].YinYang,
	}

	// 匹配八卦
	for _, trigram := range trigrams {
		if matchTrigram(trigram.YinYang, yinYang) {
			return trigram.Number
		}
	}

	return 1 // 默认乾
}

func matchTrigram(pattern, target []bool) bool {
	if len(pattern) != len(target) {
		return false
	}
	for i := range pattern {
		if pattern[i] != target[i] {
			return false
		}
	}
	return true
}

// 根据上下卦确定六十四卦序号
// 六十四卦排列：上卦*8 + 下卦（但需要按传统顺序）
func getHexagramNumber(upper, lower int) int {
	// 传统六十四卦顺序表（简化版，实际有固定顺序）
	// 这里使用公式：上卦序号*8 + 下卦序号，然后映射到1-64
	// 实际应用中应该使用完整的六十四卦对照表

	// 简化实现：直接计算
	number := (upper-1)*8 + lower
	if number < 1 {
		number = 1
	}
	if number > 64 {
		number = 64
	}
	return number
}

// calculateChangedHexagram 计算变卦
// 变卦规则：老阴(6)变阳，老阳(9)变阴，然后重新计算上下卦
func calculateChangedHexagram(original SixLines) (SixLines, error) {
	if len(original.ChangingLines) == 0 {
		return original, fmt.Errorf("no changing lines")
	}

	// 复制原始六爻
	changedLines := make([]Line, len(original.Lines))
	copy(changedLines, original.Lines)

	// 转换变爻：老阴(6)变阳，老阳(9)变阴
	for _, pos := range original.ChangingLines {
		if pos < 0 || pos >= len(changedLines) {
			continue
		}

		line := &changedLines[pos]
		if line.Value == 6 {
			// 老阴变阳
			line.Value = 7 // 变为少阳
			line.YinYang = true
			line.IsChanging = false // 变后不再是变爻
		} else if line.Value == 9 {
			// 老阳变阴
			line.Value = 8 // 变为少阴
			line.YinYang = false
			line.IsChanging = false
		}
	}

	// 根据变后的六爻重新计算上下卦
	lowerTrigram := getTrigramByLines(changedLines[0:3])
	upperTrigram := getTrigramByLines(changedLines[3:6])

	// 计算变卦序号
	hexagramNumber := getHexagramNumber(upperTrigram, lowerTrigram)

	return SixLines{
		Lines:          changedLines,
		UpperTrigram:   upperTrigram,
		LowerTrigram:   lowerTrigram,
		HexagramNumber: hexagramNumber,
		ChangingLines:  []int{}, // 变卦中不再有变爻
	}, nil
}

// analyzeHexagramRelationship 分析本卦和变卦的关系
func analyzeHexagramRelationship(original, changed Hexagram, changingCount int) string {
	var sb strings.Builder

	sb.WriteString("## 变卦分析\n\n")

	// 基本信息
	sb.WriteString(fmt.Sprintf("**本卦**：%s（第%d卦）\n", original.Name, original.Number))
	sb.WriteString(fmt.Sprintf("**变卦**：%s（第%d卦）\n\n", changed.Name, changed.Number))

	// 变爻数量分析
	sb.WriteString(fmt.Sprintf("**变爻数量**：%d爻\n\n", changingCount))

	// 根据变爻数量给出不同解释
	switch changingCount {
	case 1:
		sb.WriteString("**一变爻**：表示事情有小的变化，但整体趋势不变。变爻所在位置提示需要注意的方面。\n\n")
	case 2:
		sb.WriteString("**二变爻**：表示事情有中等程度的变化，需要关注变爻提示的两个方面。\n\n")
	case 3:
		sb.WriteString("**三变爻**：表示事情有较大变化，本卦和变卦都需要参考，以变卦为主。\n\n")
	case 4:
		sb.WriteString("**四变爻**：表示事情变化很大，以变卦为主，本卦为辅。\n\n")
	case 5:
		sb.WriteString("**五变爻**：表示事情变化极大，几乎完全转向变卦所示的方向。\n\n")
	case 6:
		sb.WriteString("**六变爻**：表示完全变化，本卦已转为变卦，以变卦为准。\n\n")
	default:
		sb.WriteString("**无变爻**：静卦，表示事情稳定，变化不大。\n\n")
	}

	// 本卦和变卦的关系
	if original.Number == changed.Number {
		sb.WriteString("**关系**：本卦与变卦相同，表示虽有变爻，但整体卦象未变，变化在内部。\n\n")
	} else {
		// 分析上下卦的变化
		originalUpper := original.UpperTrigram
		originalLower := original.LowerTrigram
		changedUpper := changed.UpperTrigram
		changedLower := changed.LowerTrigram

		upperChanged := originalUpper != changedUpper
		lowerChanged := originalLower != changedLower

		if upperChanged && lowerChanged {
			sb.WriteString("**关系**：上下卦皆变，表示事情发生根本性变化，需要重新审视。\n\n")
		} else if upperChanged {
			sb.WriteString("**关系**：上卦变化，表示外部环境或结果方向发生变化。\n\n")
		} else if lowerChanged {
			sb.WriteString("**关系**：下卦变化，表示内在基础或起因发生变化。\n\n")
		}

		// 五行关系分析
		if original.Wuxing != "" && changed.Wuxing != "" {
			sb.WriteString(fmt.Sprintf("**五行变化**：本卦%s → 变卦%s\n\n", original.Wuxing, changed.Wuxing))
		}
	}

	// 综合建议
	sb.WriteString("**综合建议**：\n")
	if changingCount <= 2 {
		sb.WriteString("- 以本卦为主，参考变卦提示的变化\n")
		sb.WriteString("- 关注变爻所在位置的具体含义\n")
		sb.WriteString("- 事情会有小到中等程度的变化\n")
	} else if changingCount <= 4 {
		sb.WriteString("- 本卦和变卦都需要重视\n")
		sb.WriteString("- 事情正在发生较大变化\n")
		sb.WriteString("- 需要同时考虑现状和未来趋势\n")
	} else {
		sb.WriteString("- 以变卦为主，本卦为辅\n")
		sb.WriteString("- 事情将发生根本性变化\n")
		sb.WriteString("- 需要做好应对重大变化的准备\n")
	}

	return sb.String()
}

// 获取卦象名称和解释
func getHexagramInfo(number int, sixLines SixLines) Hexagram {
	upper := trigrams[sixLines.UpperTrigram-1]
	lower := trigrams[sixLines.LowerTrigram-1]

	// 首先尝试从数据库读取
	dbHexagram, err := database.GetHexagramByNumber(number)
	if err == nil && dbHexagram != nil {
		// 使用数据库中的数据
		hexagramName := dbHexagram.Name
		if hexagramName == "" {
			hexagramName = fmt.Sprintf("%s%s", lower.Name, upper.Name)
		}

		// 五行分析（如果数据库中没有，使用计算值）
		wuxing := dbHexagram.Wuxing
		if wuxing == "" {
			wuxing = analyzeWuxing(sixLines)
		}

		// 如果有变爻，需要计算变卦
		var changingInfo string
		var relationship string

		if len(sixLines.ChangingLines) > 0 {
			// 生成变爻信息
			changingPositions := make([]string, len(sixLines.ChangingLines))
			for i, pos := range sixLines.ChangingLines {
				changingPositions[i] = fmt.Sprintf("第%d爻", pos+1)
			}
			changingInfo = fmt.Sprintf("变爻：%s", strings.Join(changingPositions, "、"))

			// 计算变卦
			changedSixLines, err := calculateChangedHexagram(sixLines)
			if err == nil {
				// 获取变卦信息
				changedHexagramInfo := getHexagramInfo(changedSixLines.HexagramNumber, changedSixLines)

				// 分析本卦和变卦的关系
				relationship = analyzeHexagramRelationship(
					Hexagram{
						Number:       number,
						Name:         hexagramName,
						UpperTrigram: upper.Name,
						LowerTrigram: lower.Name,
						Wuxing:       wuxing,
					},
					changedHexagramInfo,
					len(sixLines.ChangingLines),
				)
			}
		}

		// 吉凶判断（优先使用数据库中的值）
		outcome := dbHexagram.Outcome
		if outcome == "" {
			outcome = determineOutcome(number, sixLines)
		}

		// 详细解释（如果数据库中有，直接使用；否则生成）
		detail := dbHexagram.Detail
		if detail == "" {
			detail = buildHexagramDetail(hexagramName, upper, lower, sixLines, wuxing, outcome, changingInfo)
		} else {
			// 如果数据库中有详细解释，添加变爻、变卦和五行信息
			if len(sixLines.ChangingLines) > 0 {
				detail = detail + "\n\n## 变爻\n" + changingInfo + "\n\n"
				// 添加变卦分析
				if relationship != "" {
					detail = detail + relationship + "\n"
				}
			}
			if wuxing != "" {
				detail = detail + "## 五行分析\n" + wuxing + "\n\n"
			}
		}

		// 摘要（优先使用数据库中的值）
		summary := dbHexagram.Summary
		if summary == "" {
			summary = getHexagramSummary(number, outcome)
		}

		return Hexagram{
			Number:       number,
			Name:         hexagramName,
			UpperTrigram: dbHexagram.UpperTrigram,
			LowerTrigram: dbHexagram.LowerTrigram,
			Outcome:      outcome,
			Summary:      summary,
			Detail:       detail,
			Wuxing:       wuxing,
		}
	}

	// 数据库中没有，使用默认逻辑
	hexagramName := fmt.Sprintf("%s%s", lower.Name, upper.Name)

	// 五行分析（先计算，因为变卦分析需要）
	wuxing := analyzeWuxing(sixLines)

	// 如果有变爻，需要计算变卦
	var changingInfo string
	var relationship string

	if len(sixLines.ChangingLines) > 0 {
		// 生成变爻信息
		changingPositions := make([]string, len(sixLines.ChangingLines))
		for i, pos := range sixLines.ChangingLines {
			changingPositions[i] = fmt.Sprintf("第%d爻", pos+1)
		}
		changingInfo = fmt.Sprintf("变爻：%s", strings.Join(changingPositions, "、"))

		// 计算变卦
		changedSixLines, err := calculateChangedHexagram(sixLines)
		if err == nil {
			// 获取变卦信息
			changedHexagramInfo := getHexagramInfo(changedSixLines.HexagramNumber, changedSixLines)

			// 分析本卦和变卦的关系
			relationship = analyzeHexagramRelationship(
				Hexagram{
					Number:       number,
					Name:         hexagramName,
					UpperTrigram: upper.Name,
					LowerTrigram: lower.Name,
					Wuxing:       wuxing,
				},
				changedHexagramInfo,
				len(sixLines.ChangingLines),
			)
		}
	}

	// 吉凶判断（简化版）
	outcome := determineOutcome(number, sixLines)

	// 生成详细解释（包含变卦分析）
	detail := buildHexagramDetail(hexagramName, upper, lower, sixLines, wuxing, outcome, changingInfo)
	if relationship != "" {
		detail = detail + "\n" + relationship
	}

	return Hexagram{
		Number:       number,
		Name:         hexagramName,
		UpperTrigram: upper.Name,
		LowerTrigram: lower.Name,
		Outcome:      outcome,
		Summary:      getHexagramSummary(number, outcome),
		Detail:       detail,
		Wuxing:       wuxing,
	}
}

// 五行分析
func analyzeWuxing(sixLines SixLines) string {
	upper := trigrams[sixLines.UpperTrigram-1]
	lower := trigrams[sixLines.LowerTrigram-1]

	// 上下卦的五行
	upperWuxing := upper.Wuxing
	lowerWuxing := lower.Wuxing

	// 判断五行生克关系
	relationship := getWuxingRelationship(lowerWuxing, upperWuxing)

	return fmt.Sprintf("下卦%s，上卦%s。%s", lowerWuxing, upperWuxing, relationship)
}

// 五行生克关系
func getWuxingRelationship(lower, upper string) string {
	// 五行相生：木生火，火生土，土生金，金生水，水生木
	// 五行相克：木克土，土克水，水克火，火克金，金克木

	relationships := map[string]map[string]string{
		"木": {"火": "生", "土": "克", "金": "被克", "水": "被生", "木": "比和"},
		"火": {"土": "生", "金": "克", "水": "被克", "木": "被生", "火": "比和"},
		"土": {"金": "生", "水": "克", "木": "被克", "火": "被生", "土": "比和"},
		"金": {"水": "生", "木": "克", "火": "被克", "土": "被生", "金": "比和"},
		"水": {"木": "生", "火": "克", "土": "被克", "金": "被生", "水": "比和"},
	}

	if rel, ok := relationships[lower][upper]; ok {
		switch rel {
		case "生":
			return fmt.Sprintf("%s生%s，下卦生上卦，主吉，但需循序渐进。", lower, upper)
		case "克":
			return fmt.Sprintf("%s克%s，下卦克上卦，主阻，需化解矛盾。", lower, upper)
		case "被生":
			return fmt.Sprintf("%s被%s生，上卦生下卦，主吉，得贵人相助。", lower, upper)
		case "被克":
			return fmt.Sprintf("%s被%s克，上卦克下卦，主凶，需谨慎应对。", lower, upper)
		case "比和":
			return fmt.Sprintf("%s与%s比和，上下卦同类，主平，宜稳中求进。", lower, upper)
		}
	}

	return "五行关系复杂，需综合分析。"
}

// 判断吉凶
func determineOutcome(number int, sixLines SixLines) string {
	// 简化判断逻辑
	// 实际应该根据卦象、变爻、五行等多因素综合判断

	changingCount := len(sixLines.ChangingLines)

	// 无变爻：静卦，主稳定
	if changingCount == 0 {
		if number <= 20 {
			return "吉"
		} else if number <= 40 {
			return "平"
		}
		return "凶"
	}

	// 有变爻：动卦，主变化
	if changingCount == 1 {
		return "平" // 一变爻，小变化
	} else if changingCount <= 3 {
		return "吉" // 2-3变爻，积极变化
	}

	return "凶" // 多变爻，变化剧烈
}

// 生成卦象摘要
func getHexagramSummary(number int, outcome string) string {
	summaries := map[string]string{
		"吉": "大吉之象，宜积极进取，把握时机。",
		"平": "中平之象，宜稳中求进，谨慎行事。",
		"凶": "需谨慎应对，避免冒进，等待时机。",
	}

	if summary, ok := summaries[outcome]; ok {
		return summary
	}
	return "卦象复杂，需详细分析。"
}

// 构建详细解释
func buildHexagramDetail(name string, upper, lower Trigram, sixLines SixLines, wuxing, outcome, changingInfo string) string {
	var sb strings.Builder

	sb.WriteString("# 卦象解析：")
	sb.WriteString(name)
	sb.WriteString("\n\n")

	// 卦象结构
	sb.WriteString("## 卦象结构\n")
	sb.WriteString(fmt.Sprintf("上卦：%s (%s) - %s\n", upper.Name, upper.Symbol, upper.Wuxing))
	sb.WriteString(fmt.Sprintf("下卦：%s (%s) - %s\n", lower.Name, lower.Symbol, lower.Wuxing))
	sb.WriteString("\n")

	// 六爻展示（从下往上）
	sb.WriteString("## 六爻\n")
	for i := 5; i >= 0; i-- {
		line := sixLines.Lines[i]
		lineSymbol := "—"
		if !line.YinYang {
			lineSymbol = "--"
		}
		changingMark := ""
		if line.IsChanging {
			if line.Value == 6 {
				changingMark = " (老阴，变阳)"
			} else if line.Value == 9 {
				changingMark = " (老阳，变阴)"
			} else {
				changingMark = " (变爻)"
			}
		}
		sb.WriteString(fmt.Sprintf("第%d爻：%s%s (值：%d)\n", i+1, lineSymbol, changingMark, line.Value))
	}
	sb.WriteString("\n")

	// 变爻信息和变卦分析
	if len(sixLines.ChangingLines) > 0 {
		sb.WriteString("## 变爻\n")
		sb.WriteString(changingInfo)
		sb.WriteString("\n\n")

		// 计算并显示变卦
		changedSixLines, err := calculateChangedHexagram(sixLines)
		if err == nil {
			changedHexagramInfo := getHexagramInfo(changedSixLines.HexagramNumber, changedSixLines)
			originalHexagramInfo := Hexagram{
				Number:       sixLines.HexagramNumber,
				Name:         name,
				UpperTrigram: upper.Name,
				LowerTrigram: lower.Name,
				Wuxing:       wuxing,
			}

			relationship := analyzeHexagramRelationship(
				originalHexagramInfo,
				changedHexagramInfo,
				len(sixLines.ChangingLines),
			)
			sb.WriteString(relationship)
			sb.WriteString("\n")
		}
	}

	// 五行分析
	sb.WriteString("## 五行分析\n")
	sb.WriteString(wuxing)
	sb.WriteString("\n\n")

	// 运势判断
	sb.WriteString("## 运势\n")
	sb.WriteString(fmt.Sprintf("总体判断：%s\n", outcome))
	sb.WriteString(getHexagramSummary(sixLines.HexagramNumber, outcome))
	sb.WriteString("\n\n")

	// 建议
	sb.WriteString("## 建议\n")
	sb.WriteString(getAdviceByOutcome(outcome, sixLines))

	return sb.String()
}

// 根据结果给出建议
func getAdviceByOutcome(outcome string, sixLines SixLines) string {
	changingCount := len(sixLines.ChangingLines)

	switch outcome {
	case "吉":
		if changingCount > 0 {
			return "卦象显示积极变化，宜把握时机，主动出击。但需注意变爻提示，不可过于激进。"
		}
		return "卦象稳定，运势良好。宜坚持正道，稳步推进，必有所成。"
	case "平":
		return "卦象中平，宜稳中求进。保持现状，观察变化，等待更好的时机。"
	case "凶":
		if changingCount > 2 {
			return "卦象多变，变化剧烈。宜谨慎应对，避免重大决策，先观察再行动。"
		}
		return "卦象不利，需谨慎行事。宜守不宜攻，等待时机，或寻求化解之道。"
	}

	return "综合分析卦象，结合实际情况做出判断。"
}

// 生成完整的东方占卜结果
func GenerateIChingResult(sessionID, eventType string) *model.DivinationResult {
	// 生成六爻
	sixLines := generateSixLines(sessionID)

	// 获取卦象信息
	hexagram := getHexagramInfo(sixLines.HexagramNumber, sixLines)

	// 构建结果
	result := &model.DivinationResult{
		SessionID: sessionID,
		Outcome:   hexagram.Outcome,
		Title:     hexagram.Name,
		Summary:   hexagram.Summary,
		Detail:    hexagram.Detail,
		CreatedAt: time.Now(),
	}

	// 添加原始数据（用于调试或详细分析）
	result.RawData = fmt.Sprintf("卦序号：%d，上卦：%s，下卦：%s，变爻数：%d",
		hexagram.Number, hexagram.UpperTrigram, hexagram.LowerTrigram, len(sixLines.ChangingLines))

	return result
}
