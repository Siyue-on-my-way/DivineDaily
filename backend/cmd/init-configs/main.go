package main

import (
	"divine-daily-backend/internal/database"
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/repository"
	"log"
)

func main() {
	// 初始化数据库
	if err := database.InitDB(); err != nil {
		log.Fatalf("初始化数据库失败: %v", err)
	}
	defer database.CloseDB()

	llmRepo := repository.NewLLMConfigRepository(database.GetDB())
	promptRepo := repository.NewPromptConfigRepository(database.GetDB())

	// 初始化默认LLM配置（Mock）
	mockLLMConfig := &model.LLMConfig{
		Name:           "Mock LLM",
		Provider:       "local",
		APIKey:         "",
		Endpoint:       "",
		ModelName:      "mock",
		Temperature:    0.7,
		MaxTokens:      1000,
		TimeoutSeconds: 30,
		IsDefault:      true,
		IsEnabled:      true,
		Description:    "默认Mock LLM配置，用于开发和测试",
	}

	if err := llmRepo.Create(mockLLMConfig); err != nil {
		log.Printf("创建Mock LLM配置失败（可能已存在）: %v", err)
	} else {
		log.Println("✅ 创建默认Mock LLM配置成功")
	}

	// 初始化默认Prompt配置
	promptConfigs := []*model.PromptConfig{
		{
			Name:         "决策类-结果卡",
			PromptType:   "answer",
			QuestionType: "decision",
			Template: `你是一位精通周易的占卜师。根据以下信息为用户解卦：

用户问题：{{.question}}

用户生辰八字：
- 农历：{{.lunar_year}}年{{.lunar_month}}月{{.lunar_day}}日
- 天干地支：{{.ganzhi_year}}年{{.ganzhi_month}}月{{.ganzhi_day}}日
- 生肖：{{.animal}}

本次卦象：
- 卦名：{{.hexagram_name}}
- 卦辞：{{.hexagram_summary}}
- 详细解释：{{.hexagram_detail}}
- 吉凶：{{.outcome}}
- 五行：{{.wuxing}}

问题背景：{{.context}}

请直接回答用户的问题，给出明确的建议（50-100字）：
- 不要解释算卦过程
- 不要展示卦象信息
- 直接给出答案和建议
- 语言简洁明了，符合易学传统，但易于理解

格式：直接答案 + 简要理由`,
			Variables: []model.PromptVariable{
				{Name: "question", Type: "string", Description: "用户问题", Required: true},
				{Name: "lunar_year", Type: "int", Description: "农历年份", Required: false},
				{Name: "lunar_month", Type: "int", Description: "农历月份", Required: false},
				{Name: "lunar_day", Type: "int", Description: "农历日期", Required: false},
				{Name: "ganzhi_year", Type: "string", Description: "天干地支年份", Required: false},
				{Name: "ganzhi_month", Type: "string", Description: "天干地支月份", Required: false},
				{Name: "ganzhi_day", Type: "string", Description: "天干地支日期", Required: false},
				{Name: "animal", Type: "string", Description: "生肖", Required: false},
				{Name: "hexagram_name", Type: "string", Description: "卦名", Required: false},
				{Name: "hexagram_summary", Type: "string", Description: "卦辞摘要", Required: false},
				{Name: "hexagram_detail", Type: "string", Description: "详细解释", Required: false},
				{Name: "outcome", Type: "string", Description: "吉凶", Required: false},
				{Name: "wuxing", Type: "string", Description: "五行", Required: false},
				{Name: "context", Type: "string", Description: "问题背景", Required: false},
			},
			IsDefault:   true,
			IsEnabled:   true,
			Description: "决策类问题的结果卡Prompt模板",
		},
		{
			Name:         "决策类-详情",
			PromptType:   "detail",
			QuestionType: "decision",
			Template: `你是一位精通周易的占卜师。根据以下信息为用户详细解卦：

用户问题：{{.question}}

用户生辰八字：
- 农历：{{.lunar_year}}年{{.lunar_month}}月{{.lunar_day}}日
- 天干地支：{{.ganzhi_year}}年{{.ganzhi_month}}月{{.ganzhi_day}}日
- 生肖：{{.animal}}

本次卦象：
- 卦名：{{.hexagram_name}}（第{{.hexagram_number}}卦）
- 上卦：{{.upper_trigram}}
- 下卦：{{.lower_trigram}}
- 卦辞：{{.hexagram_summary}}
- 详细解释：{{.hexagram_detail}}
- 吉凶：{{.outcome}}
- 五行：{{.wuxing}}

问题背景：{{.context}}

请提供完整的解卦分析：
1. 卦象详细解读
2. 结合用户八字的分析
3. 算卦过程说明
4. 具体建议和注意事项
5. 未来趋势预测

语言风格：详细专业，但易于理解。`,
			Variables: []model.PromptVariable{
				{Name: "question", Type: "string", Description: "用户问题", Required: true},
				{Name: "lunar_year", Type: "int", Description: "农历年份", Required: false},
				{Name: "lunar_month", Type: "int", Description: "农历月份", Required: false},
				{Name: "lunar_day", Type: "int", Description: "农历日期", Required: false},
				{Name: "ganzhi_year", Type: "string", Description: "天干地支年份", Required: false},
				{Name: "ganzhi_month", Type: "string", Description: "天干地支月份", Required: false},
				{Name: "ganzhi_day", Type: "string", Description: "天干地支日期", Required: false},
				{Name: "animal", Type: "string", Description: "生肖", Required: false},
				{Name: "hexagram_name", Type: "string", Description: "卦名", Required: false},
				{Name: "hexagram_number", Type: "int", Description: "卦序号", Required: false},
				{Name: "upper_trigram", Type: "string", Description: "上卦", Required: false},
				{Name: "lower_trigram", Type: "string", Description: "下卦", Required: false},
				{Name: "hexagram_summary", Type: "string", Description: "卦辞摘要", Required: false},
				{Name: "hexagram_detail", Type: "string", Description: "详细解释", Required: false},
				{Name: "outcome", Type: "string", Description: "吉凶", Required: false},
				{Name: "wuxing", Type: "string", Description: "五行", Required: false},
				{Name: "context", Type: "string", Description: "问题背景", Required: false},
			},
			IsDefault:   true,
			IsEnabled:   true,
			Description: "决策类问题的详情Prompt模板",
		},
		{
			Name:         "推荐类-结果卡",
			PromptType:   "recommendation",
			QuestionType: "recommendation",
			Template: `根据用户的个人资料和问题，提供个性化推荐：

用户问题：{{.question}}

用户资料：
- 性别：{{.gender}}
- 生理周期：{{.menstruating_status}}
- 运动习惯：{{.exercise_habit}}
- 生肖：{{.animal}}
- 星座：{{.zodiac_sign}}

当前时间：{{.current_time}}

请直接提供3-5个个性化推荐，每个推荐包含：
1. 推荐内容（简洁）
2. 推荐理由（一句话，结合用户资料）

格式要求：
- 不要解释推荐逻辑
- 不要展示用户资料匹配过程
- 直接给出推荐列表
- 语言亲切自然，符合日常对话`,
			Variables: []model.PromptVariable{
				{Name: "question", Type: "string", Description: "用户问题", Required: true},
				{Name: "gender", Type: "string", Description: "性别", Required: false},
				{Name: "menstruating_status", Type: "string", Description: "生理周期状态", Required: false},
				{Name: "exercise_habit", Type: "string", Description: "运动习惯", Required: false},
				{Name: "animal", Type: "string", Description: "生肖", Required: false},
				{Name: "zodiac_sign", Type: "string", Description: "星座", Required: false},
				{Name: "current_time", Type: "string", Description: "当前时间", Required: false},
			},
			IsDefault:   true,
			IsEnabled:   true,
			Description: "推荐类问题的结果卡Prompt模板",
		},
		{
			Name:         "推荐类-详情",
			PromptType:   "detail",
			QuestionType: "recommendation",
			Template: `根据用户的个人资料和问题，详细说明推荐逻辑：

用户问题：{{.question}}

用户资料：
- 性别：{{.gender}}
- 生理周期：{{.menstruating_status}}
- 运动习惯：{{.exercise_habit}}
- 生肖：{{.animal}}
- 星座：{{.zodiac_sign}}

当前时间：{{.current_time}}

已生成的推荐：
{{.recommendations}}

请提供：
1. 推荐逻辑说明（为什么推荐这些）
2. 用户资料匹配分析
3. 每个推荐的详细理由
4. 注意事项

语言风格：详细专业，但易于理解。`,
			Variables: []model.PromptVariable{
				{Name: "question", Type: "string", Description: "用户问题", Required: true},
				{Name: "gender", Type: "string", Description: "性别", Required: false},
				{Name: "menstruating_status", Type: "string", Description: "生理周期状态", Required: false},
				{Name: "exercise_habit", Type: "string", Description: "运动习惯", Required: false},
				{Name: "animal", Type: "string", Description: "生肖", Required: false},
				{Name: "zodiac_sign", Type: "string", Description: "星座", Required: false},
				{Name: "current_time", Type: "string", Description: "当前时间", Required: false},
				{Name: "recommendations", Type: "string", Description: "已生成的推荐列表", Required: false},
			},
			IsDefault:   true,
			IsEnabled:   true,
			Description: "推荐类问题的详情Prompt模板",
		},
		{
			Name:         "塔罗牌-结果卡",
			PromptType:   "tarot_summary",
			QuestionType: "tarot",
			Template: `你是一位专业的塔罗占卜师。用户提出了以下问题：

问题：{{.question}}

抽出的牌：
{{.cards}}

请用50-100字简洁地总结这次占卜的核心信息，直接给出答案和建议，不要解释抽牌过程。`,
			Variables: []model.PromptVariable{
				{Name: "question", Type: "string", Description: "用户问题", Required: true},
				{Name: "cards", Type: "string", Description: "抽出的牌列表（格式：位置 - 牌名）", Required: true},
				{Name: "count", Type: "int", Description: "牌的数量", Required: false},
			},
			IsDefault:   true,
			IsEnabled:   true,
			Description: "塔罗牌占卜的结果卡Prompt模板",
		},
		{
			Name:         "塔罗牌-详情",
			PromptType:   "tarot_detail",
			QuestionType: "tarot",
			Template: `你是一位专业的塔罗占卜师。用户提出了以下问题：

问题：{{.question}}

牌阵类型：{{.spread}}

抽出的牌及其含义：
{{.cards}}

请详细解读每张牌的意义，结合它们在牌阵中的位置，分析它们之间的关系，并结合用户的问题给出完整的占卜解读和具体建议。

解读要求：
1. 每张牌的详细含义
2. 牌阵中牌与牌之间的关系
3. 结合用户问题的综合分析
4. 具体的行动建议
5. 未来趋势预测

语言风格：专业但易于理解，富有启发性和指导性。`,
			Variables: []model.PromptVariable{
				{Name: "question", Type: "string", Description: "用户问题", Required: true},
				{Name: "cards", Type: "string", Description: "抽出的牌及其含义（格式：位置 - 牌名 - 含义）", Required: true},
				{Name: "spread", Type: "string", Description: "牌阵类型（single/three/cross）", Required: true},
				{Name: "card_count", Type: "int", Description: "牌的数量", Required: false},
			},
			IsDefault:   true,
			IsEnabled:   true,
			Description: "塔罗牌占卜的详情Prompt模板",
		},
	}

	for _, config := range promptConfigs {
		if err := promptRepo.Create(config); err != nil {
			log.Printf("创建Prompt配置失败（可能已存在）: %v", err)
		} else {
			log.Printf("✅ 创建Prompt配置成功: %s", config.Name)
		}
	}

	log.Println("\n✅ 默认配置初始化完成！")
}

