package service

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
)

// QuestionAnalysis 问题分析结果
type QuestionAnalysis struct {
	QuestionType string                 `json:"question_type"` // decision, relationship, career, fortune, knowledge
	SubType      string                 `json:"sub_type"`      // 子类型，如 binary_choice, timing, compatibility
	Elements     map[string]string      `json:"elements"`      // 问题要素，如 option_a, option_b, concern_1
	Intent       string                 `json:"intent"`        // 问题意图：binary_choice, yes_no, timing, understanding
	Complexity   string                 `json:"complexity"`    // 复杂度：simple, medium, high
	Keywords     []string               `json:"keywords"`      // 关键词
	Context      map[string]interface{} `json:"context"`       // 额外上下文
}

// QuestionAnalyzer 问题分析器
type QuestionAnalyzer struct {
	llmService LLMService
}

// NewQuestionAnalyzer 创建问题分析器
func NewQuestionAnalyzer(llmService LLMService) *QuestionAnalyzer {
	return &QuestionAnalyzer{
		llmService: llmService,
	}
}

// AnalyzeQuestion 分析问题
func (qa *QuestionAnalyzer) AnalyzeQuestion(ctx context.Context, question string) (*QuestionAnalysis, error) {
	// 构建分析 Prompt
	prompt := buildAnalysisPrompt(question)

	// 调用 LLM 分析
	response, err := qa.llmService.GenerateAnswer(ctx, prompt)
	if err != nil {
		// 如果 LLM 调用失败，使用规则引擎降级
		return qa.fallbackAnalysis(question), nil
	}

	// 解析 LLM 返回的 JSON
	analysis, err := parseAnalysisResponse(response)
	if err != nil {
		// 如果解析失败，使用规则引擎降级
		return qa.fallbackAnalysis(question), nil
	}

	return analysis, nil
}

// buildAnalysisPrompt 构建问题分析 Prompt
func buildAnalysisPrompt(question string) string {
	return fmt.Sprintf(`你是一位专业的问题分析师。请分析以下用户问题，并以 JSON 格式返回分析结果。

用户问题：%s

请分析以下维度：

1. **问题类型** (question_type)：
   - decision: 决策类（需要做选择）
   - relationship: 感情类（恋爱、婚姻、人际关系）
   - career: 事业类（工作、职业发展）
   - fortune: 运势类（今日运势、未来运势）
   - knowledge: 知识类（了解某个概念或现象）

2. **子类型** (sub_type)：
   - binary_choice: 二选一（A还是B）
   - yes_no: 是非题（做还是不做）
   - timing: 时机问题（什么时候做）
   - compatibility: 匹配度（是否合适）
   - multiple_choice: 多选题（多个选项）
   - open_ended: 开放式问题

3. **问题要素** (elements)：
   提取问题中的关键要素，如：
   - option_a: 选项A的描述
   - option_b: 选项B的描述
   - concern_1: 用户的顾虑1
   - concern_2: 用户的顾虑2
   - time_frame: 时间范围
   - target_person: 目标人物

4. **问题意图** (intent)：
   - binary_choice: 需要在两个选项中选一个
   - yes_no: 需要判断做还是不做
   - timing: 需要判断时机
   - understanding: 需要理解和解释
   - guidance: 需要指导和建议

5. **复杂度** (complexity)：
   - simple: 简单问题（单一维度）
   - medium: 中等复杂（2-3个维度）
   - high: 高度复杂（多个维度，有冲突）

6. **关键词** (keywords)：
   提取3-5个关键词

请严格按照以下 JSON 格式返回（不要添加任何其他文字）：

{
  "question_type": "decision",
  "sub_type": "binary_choice",
  "elements": {
    "option_a": "选项A的描述",
    "option_b": "选项B的描述",
    "concern_1": "顾虑1"
  },
  "intent": "binary_choice",
  "complexity": "high",
  "keywords": ["关键词1", "关键词2", "关键词3"]
}

示例1：
问题："我应该和研究生学妹谈恋爱还是和大一学妹谈？"
分析：
{
  "question_type": "relationship",
  "sub_type": "binary_choice",
  "elements": {
    "option_a": "研究生学妹",
    "option_b": "大一学妹",
    "context": "恋爱选择"
  },
  "intent": "binary_choice",
  "complexity": "medium",
  "keywords": ["恋爱", "选择", "学妹", "年龄差"]
}

示例2：
问题："杨冠和刘亦菲同时追我，我应该选谁？我最近在事业上升期，希望事业也有成。但是也怕孤独，想谈恋爱"
分析：
{
  "question_type": "decision",
  "sub_type": "binary_choice",
  "elements": {
    "option_a": "杨冠",
    "option_b": "刘亦菲",
    "concern_1": "事业上升期",
    "concern_2": "怕孤独"
  },
  "intent": "binary_choice",
  "complexity": "high",
  "keywords": ["恋爱", "事业", "选择", "平衡"]
}

现在请分析用户的问题并返回 JSON：`, question)
}

// parseAnalysisResponse 解析 LLM 返回的分析结果
func parseAnalysisResponse(response string) (*QuestionAnalysis, error) {
	// 清理响应，提取 JSON 部分
	response = strings.TrimSpace(response)

	// 尝试找到 JSON 开始和结束位置
	startIdx := strings.Index(response, "{")
	endIdx := strings.LastIndex(response, "}")

	if startIdx == -1 || endIdx == -1 || startIdx >= endIdx {
		return nil, fmt.Errorf("无法找到有效的 JSON")
	}

	jsonStr := response[startIdx : endIdx+1]

	// 解析 JSON
	var analysis QuestionAnalysis
	err := json.Unmarshal([]byte(jsonStr), &analysis)
	if err != nil {
		return nil, fmt.Errorf("JSON 解析失败: %v", err)
	}

	return &analysis, nil
}

// fallbackAnalysis 降级分析（基于规则引擎）
func (qa *QuestionAnalyzer) fallbackAnalysis(question string) *QuestionAnalysis {
	question = strings.ToLower(question)

	analysis := &QuestionAnalysis{
		Elements:   make(map[string]string),
		Keywords:   []string{},
		Context:    make(map[string]interface{}),
		Complexity: "medium",
	}

	// 规则1：检测是否为二选一问题
	if strings.Contains(question, "还是") || strings.Contains(question, "或者") {
		analysis.QuestionType = "decision"
		analysis.SubType = "binary_choice"
		analysis.Intent = "binary_choice"

		// 尝试提取选项
		if strings.Contains(question, "还是") {
			parts := strings.Split(question, "还是")
			if len(parts) >= 2 {
				analysis.Elements["option_a"] = strings.TrimSpace(parts[0])
				analysis.Elements["option_b"] = strings.TrimSpace(parts[1])
			}
		}
	}

	// 规则2：检测感情类问题
	relationshipKeywords := []string{"恋爱", "喜欢", "爱", "感情", "结婚", "分手", "追", "表白"}
	for _, keyword := range relationshipKeywords {
		if strings.Contains(question, keyword) {
			if analysis.QuestionType == "" {
				analysis.QuestionType = "relationship"
			}
			analysis.Keywords = append(analysis.Keywords, keyword)
		}
	}

	// 规则3：检测事业类问题
	careerKeywords := []string{"工作", "事业", "职业", "跳槽", "升职", "面试", "公司"}
	for _, keyword := range careerKeywords {
		if strings.Contains(question, keyword) {
			if analysis.QuestionType == "" {
				analysis.QuestionType = "career"
			}
			analysis.Keywords = append(analysis.Keywords, keyword)
		}
	}

	// 规则4：检测是非问题
	if strings.Contains(question, "应该") || strings.Contains(question, "要不要") ||
		strings.Contains(question, "该不该") || strings.Contains(question, "能不能") {
		if analysis.SubType == "" {
			analysis.SubType = "yes_no"
			analysis.Intent = "yes_no"
		}
	}

	// 规则5：检测时机问题
	if strings.Contains(question, "什么时候") || strings.Contains(question, "何时") ||
		strings.Contains(question, "时机") {
		analysis.SubType = "timing"
		analysis.Intent = "timing"
	}

	// 规则6：检测复杂度
	concernCount := 0
	if strings.Contains(question, "但是") || strings.Contains(question, "不过") {
		concernCount++
	}
	if strings.Contains(question, "又") || strings.Contains(question, "也") {
		concernCount++
	}
	if concernCount >= 2 {
		analysis.Complexity = "high"
	} else if concernCount == 1 {
		analysis.Complexity = "medium"
	} else {
		analysis.Complexity = "simple"
	}

	// 默认值
	if analysis.QuestionType == "" {
		analysis.QuestionType = "decision"
	}
	if analysis.SubType == "" {
		analysis.SubType = "open_ended"
	}
	if analysis.Intent == "" {
		analysis.Intent = "guidance"
	}

	return analysis
}

// GetQuestionTypeLabel 获取问题类型的中文标签
func (qa *QuestionAnalysis) GetQuestionTypeLabel() string {
	labels := map[string]string{
		"decision":     "决策",
		"relationship": "感情",
		"career":       "事业",
		"fortune":      "运势",
		"knowledge":    "知识",
	}

	if label, ok := labels[qa.QuestionType]; ok {
		return label
	}
	return "其他"
}

// GetIntentLabel 获取问题意图的中文标签
func (qa *QuestionAnalysis) GetIntentLabel() string {
	labels := map[string]string{
		"binary_choice": "二选一",
		"yes_no":        "是非判断",
		"timing":        "时机选择",
		"understanding": "理解解释",
		"guidance":      "指导建议",
	}

	if label, ok := labels[qa.Intent]; ok {
		return label
	}
	return "其他"
}
