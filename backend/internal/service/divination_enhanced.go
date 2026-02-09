package service

import (
	"context"
	"divine-daily-backend/internal/model"
	"fmt"
	"time"
)

// processDecisionQuestion 处理决策类问题（包括感情、事业等）
func (s *DivinationService) processDecisionQuestion(
	sessionID string,
	question string,
	userID string,
	questionContext map[string]interface{},
) (*model.DivinationResult, error) {
	// 1. 获取用户档案（生辰八字）
	profile, err := s.userProfileSvc.GetProfile(userID)
	if err != nil {
		// 如果用户没有档案，使用默认值
		profile = &model.UserProfile{UserID: userID}
	}

	// 2. 生成卦象
	sixLines := generateSixLines(sessionID)
	hexagram := getHexagramInfo(sixLines.HexagramNumber, sixLines)

	// 3. 从上下文中获取问题分析结果
	var analysis *QuestionAnalysis
	if analysisData, ok := questionContext["analysis"]; ok {
		if a, ok := analysisData.(*QuestionAnalysis); ok {
			analysis = a
		}
	}

	// 4. 构建智能 Prompt（根据问题分析结果）
	answerPrompt := buildSmartAnswerPrompt(question, profile, hexagram, analysis, questionContext)

	// 5. 调用LLM生成直接答案（结果卡）
	ctx := context.Background()
	answer, err := s.llmService.GenerateAnswer(ctx, answerPrompt)
	if err != nil {
		// 如果LLM调用失败，使用默认答案
		answer = fmt.Sprintf("根据本次卦象分析，建议您谨慎考虑。卦象显示：%s。", hexagram.Summary)
	}

	// 6. 构建详情 Prompt
	detailPrompt := buildSmartDetailPrompt(question, profile, hexagram, analysis, questionContext)
	detail, err := s.llmService.GenerateDetail(ctx, detailPrompt)
	if err != nil {
		// 如果LLM调用失败，使用卦象详情
		detail = hexagram.Detail
	}

	// 7. 构建卦象信息（详情中使用）
	hexagramInfo := &model.HexagramInfo{
		Number:        hexagram.Number,
		Name:          hexagram.Name,
		UpperTrigram:  hexagram.UpperTrigram,
		LowerTrigram:  hexagram.LowerTrigram,
		Outcome:       hexagram.Outcome,
		Summary:       hexagram.Summary,
		Wuxing:        hexagram.Wuxing,
		ChangingLines: sixLines.ChangingLines,
	}

	// 8. 构建结果
	return &model.DivinationResult{
		SessionID:    sessionID,
		Outcome:      hexagram.Outcome,
		Title:        hexagram.Name,
		Summary:      answer,       // 结果卡：直接答案
		Detail:       detail,       // 详情：算卦过程和完整解读
		HexagramInfo: hexagramInfo, // 卦象信息（详情中显示）
		CreatedAt:    time.Now(),
	}, nil
}

// processRecommendationQuestion 处理日常推荐类问题
func (s *DivinationService) processRecommendationQuestion(
	sessionID string,
	question string,
	userID string,
) (*model.DivinationResult, error) {
	// 1. 获取用户档案
	profile, err := s.userProfileSvc.GetProfile(userID)
	if err != nil {
		profile = &model.UserProfile{UserID: userID}
	}

	// 2. 构建推荐Prompt
	recommendationPrompt := buildRecommendationPrompt(question, profile)

	// 3. 调用LLM生成推荐列表
	ctx := context.Background()
	recommendations, err := s.llmService.GenerateRecommendation(ctx, recommendationPrompt)
	if err != nil {
		recommendations = []model.RecommendationItem{
			{Content: "建议1", Reason: "根据您的个人情况推荐"},
			{Content: "建议2", Reason: "适合您当前状态"},
		}
	}

	// 4. 构建详情
	detailPrompt := buildRecommendationDetailPrompt(question, profile, recommendations)
	detail, err := s.llmService.GenerateDetail(ctx, detailPrompt)
	if err != nil {
		detail = "推荐逻辑：根据您的个人资料和当前状态，为您推荐了以上内容。"
	}

	// 5. 格式化推荐列表为Summary
	summary := formatRecommendations(recommendations)

	// 6. 构建结果
	return &model.DivinationResult{
		SessionID:       sessionID,
		Title:           "个性化推荐",
		Summary:         summary,
		Detail:          detail,
		Recommendations: recommendations,
		CreatedAt:       time.Now(),
	}, nil
}

// buildSmartAnswerPrompt 构建智能 Prompt（根据问题分析结果）
func buildSmartAnswerPrompt(
	question string,
	profile *model.UserProfile,
	hexagram Hexagram,
	analysis *QuestionAnalysis,
	questionContext map[string]interface{},
) string {
	// 基础信息
	baseInfo := fmt.Sprintf(`你是一位精通周易、经验丰富的占卜大师。用户向你请教人生抉择，你需要给出明确、实用的建议。

用户问题：%s

用户生辰八字：
- 农历：%d年%d月%d日
- 天干地支：%s年%s月%s日
- 生肖：%s

本次卦象：
- 卦名：%s
- 卦辞：%s
- 吉凶：%s
- 五行：%s`,
		question,
		profile.LunarYear, profile.LunarMonth, profile.LunarDay,
		profile.GanZhiYear, profile.GanZhiMonth, profile.GanZhiDay,
		profile.Animal,
		hexagram.Name, hexagram.Summary,
		hexagram.Outcome, hexagram.Wuxing,
	)

	// 根据问题分析结果，生成针对性的指导
	var specificGuidance string
	if analysis != nil {
		specificGuidance = generateSpecificGuidance(analysis)
	} else {
		specificGuidance = `
【重要】请按照以下格式回答（100-150字）：

第一步：明确结论
- 直接给出建议，不要模棱两可

第二步：卦象解释（2-3句话）
- 简要说明卦象的含义
- 解释为什么卦象支持这个结论

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战`
	}

	// 语言风格指导
	styleGuide := `

语言风格：
- 像一位智慧长者，语气坚定但温和
- 不要说"可能"、"也许"、"或许"这类模糊词
- 要说"建议"、"应当"、"宜"、"不宜"这类明确词
- 结合易经智慧，但用现代语言表达`

	return baseInfo + "\n" + specificGuidance + styleGuide
}

// generateSpecificGuidance 根据问题分析生成针对性指导
func generateSpecificGuidance(analysis *QuestionAnalysis) string {
	var guidance string

	// 根据问题类型生成指导
	switch analysis.QuestionType {
	case "relationship":
		guidance = `
【这是一个感情问题】请按照以下格式回答（100-150字）：

第一步：明确结论`
		if analysis.SubType == "binary_choice" {
			guidance += `
- 如果是选择题（A还是B），直接说"建议选择A"或"建议选择B"
- 明确指出哪个选项更适合，不要模棱两可`
		} else if analysis.SubType == "yes_no" {
			guidance += `
- 如果是是非题，直接说"建议在一起"或"建议暂缓"
- 给出明确的态度`
		}
		guidance += `

第二步：卦象解释（2-3句话）
- 说明卦象对感情的指示
- 解释两人的缘分和匹配度
- 提及五行或阴阳的关系

第三步：未来预测（2-3句话）
- 预测感情的发展趋势
- 可能遇到的挑战和机遇
- 对未来生活的影响`

	case "career":
		guidance = `
【这是一个事业问题】请按照以下格式回答（100-150字）：

第一步：明确结论`
		if analysis.SubType == "binary_choice" {
			guidance += `
- 如果是选择题（工作A还是工作B），直接说"建议选择A"或"建议选择B"
- 明确指出哪个选项更有利于事业发展`
		} else if analysis.SubType == "yes_no" {
			guidance += `
- 如果是是非题（跳槽还是留下），直接说"建议跳槽"或"建议留下"
- 给出明确的建议`
		}
		guidance += `

第二步：卦象解释（2-3句话）
- 说明卦象对事业的指示
- 解释当前的事业运势
- 提及五行对事业的影响

第三步：未来预测（2-3句话）
- 预测事业的发展趋势
- 可能遇到的机遇和挑战
- 对收入和职位的影响`

	case "decision":
		guidance = `
【这是一个决策问题】请按照以下格式回答（100-150字）：

第一步：明确结论`
		if analysis.SubType == "binary_choice" {
			// 检查是否有提取的选项
			optionA := analysis.Elements["option_a"]
			optionB := analysis.Elements["option_b"]
			if optionA != "" && optionB != "" {
				guidance += fmt.Sprintf(`
- 这是一个二选一问题："%s" 还是 "%s"
- 直接说"建议选择%s"或"建议选择%s"
- 必须明确选择其中一个，不要说"都可以"或"看情况"`, optionA, optionB, optionA, optionB)
			} else {
				guidance += `
- 这是一个二选一问题，直接说"建议选择A"或"建议选择B"
- 必须明确选择其中一个`
			}
		} else if analysis.SubType == "yes_no" {
			guidance += `
- 这是一个是非题，直接说"建议去做"或"建议暂缓"
- 给出明确的态度`
		} else if analysis.SubType == "timing" {
			guidance += `
- 这是一个时机问题，直接说"现在是好时机"或"建议等待X个月"
- 给出具体的时间建议`
		}
		guidance += `

第二步：卦象解释（2-3句话）
- 说明卦象的含义
- 解释为什么卦象支持这个结论
- 提及五行或阴阳的关系

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战
- 对生活的影响`

	default:
		guidance = `
【重要】请按照以下格式回答（100-150字）：

第一步：明确结论
- 直接给出建议，不要模棱两可

第二步：卦象解释（2-3句话）
- 简要说明卦象的含义
- 解释为什么卦象支持这个结论

第三步：未来预测（2-3句话）
- 如果按照建议去做，未来会如何发展
- 可能遇到什么机遇或挑战`
	}

	// 添加复杂度提示
	if analysis.Complexity == "high" {
		guidance += `

【注意】这是一个复杂问题，涉及多个维度：`
		for key, value := range analysis.Elements {
			if key != "option_a" && key != "option_b" {
				guidance += fmt.Sprintf("\n- %s: %s", key, value)
			}
		}
		guidance += `
请在回答中综合考虑这些因素，给出平衡的建议。`
	}

	return guidance
}

// buildSmartDetailPrompt 构建智能详情 Prompt
func buildSmartDetailPrompt(
	question string,
	profile *model.UserProfile,
	hexagram Hexagram,
	analysis *QuestionAnalysis,
	questionContext map[string]interface{},
) string {
	prompt := fmt.Sprintf(`你是一位精通周易的占卜师。根据以下信息为用户详细解卦：

用户问题：%s

用户生辰八字：
- 农历：%d年%d月%d日
- 天干地支：%s年%s月%s日
- 生肖：%s

本次卦象：
- 卦名：%s
- 卦辞：%s
- 详细解释：%s
- 吉凶：%s
- 五行：%s

请撰写详细的解卦报告（300-500字）：
1. 卦象分析：解释卦名和卦辞的含义
2. 结合现状：分析卦象与用户问题的关联
3. 详细建议：给出具体的行动指南和注意事项
4. 总结：一句话总结核心建议

语言风格：
- 专业且富有哲理
- 温暖且具有启发性
- 引用易经原文并解释`,
		question,
		profile.LunarYear, profile.LunarMonth, profile.LunarDay,
		profile.GanZhiYear, profile.GanZhiMonth, profile.GanZhiDay,
		profile.Animal,
		hexagram.Name, hexagram.Summary, hexagram.Detail,
		hexagram.Outcome, hexagram.Wuxing,
	)
	return prompt
}

// buildRecommendationPrompt 构建推荐Prompt
func buildRecommendationPrompt(question string, profile *model.UserProfile) string {
	prompt := fmt.Sprintf(`根据用户的个人资料和问题，提供个性化推荐：

用户问题：%s

用户资料：
- 性别：%s
- 生肖：%s
- 星座：%s

当前时间：%s

请直接提供3-5个个性化推荐，每个推荐包含：
1. 推荐内容（简洁）
2. 推荐理由（一句话，结合用户资料）

格式要求：
- 直接给出推荐列表
- 语言亲切自然`,
		question,
		profile.Gender,
		profile.Animal,
		profile.ZodiacSign,
		time.Now().Format("2006-01-02 15:04"),
	)
	return prompt
}

// buildRecommendationDetailPrompt 构建推荐详情Prompt
func buildRecommendationDetailPrompt(question string, profile *model.UserProfile, recommendations []model.RecommendationItem) string {
	recommendationsText := ""
	for i, rec := range recommendations {
		recommendationsText += fmt.Sprintf("%d. %s - %s\n", i+1, rec.Content, rec.Reason)
	}

	prompt := fmt.Sprintf(`根据用户的个人资料和问题，详细说明推荐逻辑：

用户问题：%s

用户资料：
- 性别：%s
- 生肖：%s
- 星座：%s

当前时间：%s

已生成的推荐：
%s

请提供：
1. 推荐逻辑说明
2. 用户资料匹配分析
3. 每个推荐的详细理由
4. 注意事项`,
		question,
		profile.Gender,
		profile.Animal,
		profile.ZodiacSign,
		time.Now().Format("2006-01-02 15:04"),
		recommendationsText,
	)
	return prompt
}

// formatRecommendations 格式化推荐列表
func formatRecommendations(recommendations []model.RecommendationItem) string {
	if len(recommendations) == 0 {
		return "暂无推荐"
	}

	var result string
	for i, rec := range recommendations {
		result += fmt.Sprintf("%d. 推荐：%s\n   理由：%s\n\n", i+1, rec.Content, rec.Reason)
	}
	return result
}
