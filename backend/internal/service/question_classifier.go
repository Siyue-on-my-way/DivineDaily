package service

import (
	"strings"
)

// QuestionType 问题类型
type QuestionType string

const (
	QuestionTypeRecommendation QuestionType = "recommendation" // 日常推荐类
	QuestionTypeDecision       QuestionType = "decision"       // 决策类
	QuestionTypeFortune        QuestionType = "fortune"        // 运势类
)

// QuestionClassification 问题分类结果
type QuestionClassification struct {
	Type        QuestionType            `json:"type"`
	Confidence  float64                 `json:"confidence"` // 0-1，置信度
	Keywords    []string                `json:"keywords"`   // 匹配到的关键词
	Context     map[string]interface{}  `json:"context"`    // 提取的上下文信息（公司名、行业等）
}

// QuestionClassifier 问题分类器
type QuestionClassifier struct {
	recommendationKeywords []string
	decisionKeywords       []string
	fortuneKeywords        []string
}

// NewQuestionClassifier 创建问题分类器
func NewQuestionClassifier() *QuestionClassifier {
	return &QuestionClassifier{
		recommendationKeywords: []string{
			"吃什么", "去哪", "去哪儿", "看什么", "推荐", "建议", "有什么",
			"吃什么好", "去哪玩", "看什么电影", "听什么", "读什么",
		},
		decisionKeywords: []string{
			"选", "选择", "应该", "哪个", "要不要", "是否", "该不该",
			"去不去", "做不做", "要不要", "选哪个", "哪个好",
			"工作", "跳槽", "投资", "买房", "结婚", "分手",
		},
		fortuneKeywords: []string{
			"运势", "运程", "运气", "今日", "本周", "本月", "今年",
			"桃花运", "财运", "事业运", "健康运",
		},
	}
}

// Classify 分类问题
func (c *QuestionClassifier) Classify(question string) *QuestionClassification {
	question = strings.TrimSpace(question)
	if question == "" {
		return &QuestionClassification{
			Type:       QuestionTypeRecommendation,
			Confidence: 0.5,
		}
	}

	// 转换为小写进行匹配（中文不需要，但英文需要）
	lowerQuestion := strings.ToLower(question)
	
	// 统计各类关键词匹配数
	recommendationCount := 0
	decisionCount := 0
	fortuneCount := 0
	
	var matchedKeywords []string

	// 检查推荐类关键词
	for _, keyword := range c.recommendationKeywords {
		if strings.Contains(question, keyword) || strings.Contains(lowerQuestion, strings.ToLower(keyword)) {
			recommendationCount++
			matchedKeywords = append(matchedKeywords, keyword)
		}
	}

	// 检查决策类关键词
	for _, keyword := range c.decisionKeywords {
		if strings.Contains(question, keyword) || strings.Contains(lowerQuestion, strings.ToLower(keyword)) {
			decisionCount++
			matchedKeywords = append(matchedKeywords, keyword)
		}
	}

	// 检查运势类关键词
	for _, keyword := range c.fortuneKeywords {
		if strings.Contains(question, keyword) || strings.Contains(lowerQuestion, strings.ToLower(keyword)) {
			fortuneCount++
			matchedKeywords = append(matchedKeywords, keyword)
		}
	}

	// 确定问题类型
	var qType QuestionType
	var confidence float64

	if decisionCount > 0 {
		qType = QuestionTypeDecision
		confidence = c.calculateConfidence(decisionCount, len(c.decisionKeywords))
	} else if fortuneCount > 0 {
		qType = QuestionTypeFortune
		confidence = c.calculateConfidence(fortuneCount, len(c.fortuneKeywords))
	} else if recommendationCount > 0 {
		qType = QuestionTypeRecommendation
		confidence = c.calculateConfidence(recommendationCount, len(c.recommendationKeywords))
	} else {
		// 默认归类为推荐类
		qType = QuestionTypeRecommendation
		confidence = 0.3
	}

	// 提取上下文信息
	context := c.extractContext(question)

	return &QuestionClassification{
		Type:       qType,
		Confidence: confidence,
		Keywords:   matchedKeywords,
		Context:    context,
	}
}

// calculateConfidence 计算置信度
func (c *QuestionClassifier) calculateConfidence(matchCount, totalKeywords int) float64 {
	if totalKeywords == 0 {
		return 0.5
	}
	baseConfidence := float64(matchCount) / float64(totalKeywords) * 0.5
	if baseConfidence > 0.9 {
		return 0.9
	}
	if baseConfidence < 0.3 {
		return 0.3
	}
	return baseConfidence + 0.3 // 基础置信度 + 0.3
}

// extractContext 提取上下文信息（公司名、行业等）
func (c *QuestionClassifier) extractContext(question string) map[string]interface{} {
	context := make(map[string]interface{})

	// 提取公司名（简单规则：包含"公司"、"企业"等）
	if strings.Contains(question, "公司") || strings.Contains(question, "企业") {
		context["has_company"] = true
	}

	// 提取行业信息（简单规则）
	industries := []string{"互联网", "金融", "教育", "医疗", "房地产", "制造业"}
	for _, industry := range industries {
		if strings.Contains(question, industry) {
			context["industry"] = industry
			break
		}
	}

	// 提取选项（A和B）
	if strings.Contains(question, "A") && strings.Contains(question, "B") {
		context["has_options"] = true
		context["option_count"] = 2
	}

	return context
}

