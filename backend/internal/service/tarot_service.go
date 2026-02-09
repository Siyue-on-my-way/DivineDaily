package service

import (
	"context"
	"divine-daily-backend/internal/model"
	"fmt"
	"hash/fnv"
	"log"
	"math/rand"
	"strings"
)

// TarotService 塔罗牌服务
type TarotService struct {
	llmService LLMService
	configSvc  *ConfigService
}

// NewTarotService 创建塔罗牌服务
func NewTarotService(llmService LLMService, configSvc *ConfigService) *TarotService {
	return &TarotService{
		llmService: llmService,
		configSvc:  configSvc,
	}
}

// DrawCards 抽牌（基于sessionID确保可重现）
func (s *TarotService) DrawCards(sessionID string, spread string, count int) ([]TarotCard, []bool, error) {
	allCards := GetAllTarotCards()
	if count > len(allCards) {
		count = len(allCards)
	}

	// 使用sessionID和spread作为种子，确保可重现
	h := fnv.New32a()
	h.Write([]byte(sessionID + spread))
	seed := int64(h.Sum32())
	rng := rand.New(rand.NewSource(seed))

	// 随机抽取不重复的牌
	used := make(map[int]bool)
	cards := make([]TarotCard, 0, count)
	reversed := make([]bool, 0, count)

	for i := 0; i < count; i++ {
		var cardIndex int
		for {
			cardIndex = rng.Intn(len(allCards))
			if !used[cardIndex] {
				used[cardIndex] = true
				break
			}
		}

		card := allCards[cardIndex]
		// 50%概率逆位
		isReversed := rng.Intn(2) == 1
		if isReversed {
			// 创建逆位牌（可以添加逆位标识）
			card = TarotCard{
				Number:   card.Number,
				Name:     card.Name + "（逆位）",
				NameEN:   card.NameEN + " (Reversed)",
				Arcana:   card.Arcana,
				Suit:     card.Suit,
				Meaning:  card.Reversed, // 逆位时使用逆位含义
				Reversed: card.Meaning,  // 交换正逆位含义
			}
		}

		cards = append(cards, card)
		reversed = append(reversed, isReversed)
	}

	return cards, reversed, nil
}

// GenerateSummary 生成结果卡摘要
func (s *TarotService) GenerateSummary(
	ctx context.Context,
	question string,
	cards []TarotCard,
	positions []string,
) (string, error) {
	// 构建卡片描述
	cardsDesc := ""
	for i, card := range cards {
		pos := "当前"
		if i < len(positions) {
			pos = positions[i]
		}
		cardsDesc += fmt.Sprintf("- %s: %s\n", pos, card.Name)
	}

	// 尝试从数据库读取Prompt模板
	var prompt string
	if s.configSvc != nil {
		promptConfig, err := s.configSvc.GetPromptConfig("answer", "tarot")
		if err == nil {
			variables := map[string]interface{}{
				"question": question,
				"cards":    cardsDesc,
				"count":    len(cards),
			}
			prompt, err = s.configSvc.RenderPrompt(promptConfig.Template, variables)
			if err == nil {
				// 使用数据库模板成功
			} else {
				// 渲染失败，使用默认模板
				log.Printf("[TarotService] 渲染Prompt模板失败: %v", err)
				prompt = s.buildDefaultSummaryPrompt(question, cardsDesc)
			}
		} else {
			// 数据库中没有配置，使用默认模板
			log.Printf("[TarotService] 获取Prompt配置失败: %v", err)
			prompt = s.buildDefaultSummaryPrompt(question, cardsDesc)
		}
	} else {
		// 没有配置服务，使用默认模板
		prompt = s.buildDefaultSummaryPrompt(question, cardsDesc)
	}

	// 调用LLM生成摘要
	result, err := s.llmService.GenerateAnswer(ctx, prompt)
	if err != nil {
		// 如果LLM调用失败，记录日志并使用简单摘要
		log.Printf("[TarotService] LLM生成摘要失败，使用降级方案: %v", err)
		return s.buildSimpleSummary(cards, positions), nil
	}

	return result, nil
}

// GenerateInterpretation 生成详细解读
func (s *TarotService) GenerateInterpretation(
	ctx context.Context,
	question string,
	cards []TarotCard,
	positions []string,
	spread string,
	userProfile *model.UserProfile,
) (string, error) {
	// 构建详细的卡片描述
	cardsDesc := ""
	for i, card := range cards {
		pos := "当前"
		if i < len(positions) {
			pos = positions[i]
		}
		meaning := card.Meaning
		if strings.Contains(card.Name, "逆位") {
			meaning = card.Reversed
		}
		cardsDesc += fmt.Sprintf("- %s: %s - %s\n", pos, card.Name, meaning)
	}

	// 尝试从数据库读取Prompt模板
	var prompt string
	if s.configSvc != nil {
		promptConfig, err := s.configSvc.GetPromptConfig("detail", "tarot")
		if err == nil {
			variables := map[string]interface{}{
				"question":     question,
				"cards":        cardsDesc,
				"spread":       spread,
				"card_count":   len(cards),
				"user_profile": userProfile,
			}
			prompt, err = s.configSvc.RenderPrompt(promptConfig.Template, variables)
			if err == nil {
				// 使用数据库模板成功
			} else {
				// 渲染失败，使用默认模板
				log.Printf("[TarotService] 渲染Prompt模板失败: %v", err)
				prompt = s.buildDefaultDetailPrompt(question, cardsDesc, spread)
			}
		} else {
			// 数据库中没有配置，使用默认模板
			log.Printf("[TarotService] 获取Prompt配置失败: %v", err)
			prompt = s.buildDefaultDetailPrompt(question, cardsDesc, spread)
		}
	} else {
		// 没有配置服务，使用默认模板
		prompt = s.buildDefaultDetailPrompt(question, cardsDesc, spread)
	}

	// 调用LLM生成详细解读
	result, err := s.llmService.GenerateDetail(ctx, prompt)
	if err != nil {
		// 如果LLM调用失败，记录日志并使用简单解读
		log.Printf("[TarotService] LLM生成详细解读失败，使用降级方案: %v", err)
		return s.buildSimpleInterpretation(cards, positions, spread), nil
	}

	return result, nil
}

// StreamSummary 流式生成结果卡摘要
func (s *TarotService) StreamSummary(
	ctx context.Context,
	question string,
	cards []TarotCard,
	positions []string,
) (<-chan string, error) {
	// 构建卡片描述
	cardsDesc := ""
	for i, card := range cards {
		pos := "当前"
		if i < len(positions) {
			pos = positions[i]
		}
		cardsDesc += fmt.Sprintf("- %s: %s\n", pos, card.Name)
	}

	// 尝试从数据库读取Prompt模板
	var prompt string
	if s.configSvc != nil {
		promptConfig, err := s.configSvc.GetPromptConfig("answer", "tarot")
		if err == nil {
			variables := map[string]interface{}{
				"question": question,
				"cards":    cardsDesc,
				"count":    len(cards),
			}
			prompt, err = s.configSvc.RenderPrompt(promptConfig.Template, variables)
			if err != nil {
				// 渲染失败，使用默认模板
				log.Printf("[TarotService] 渲染Prompt模板失败: %v", err)
				prompt = s.buildDefaultSummaryPrompt(question, cardsDesc)
			}
		} else {
			// 数据库中没有配置，使用默认模板
			log.Printf("[TarotService] 获取Prompt配置失败: %v", err)
			prompt = s.buildDefaultSummaryPrompt(question, cardsDesc)
		}
	} else {
		// 没有配置服务，使用默认模板
		prompt = s.buildDefaultSummaryPrompt(question, cardsDesc)
	}

	// 使用LLM的流式API
	return s.llmService.StreamAnswer(ctx, prompt)
}

// buildDefaultSummaryPrompt 构建默认摘要Prompt
func (s *TarotService) buildDefaultSummaryPrompt(question, cardsDesc string) string {
	return fmt.Sprintf(`你是一位专业的塔罗占卜师。用户提出了以下问题：

问题：%s

抽出的牌：
%s

请用50-100字简洁地总结这次占卜的核心信息，直接给出答案和建议，不要解释抽牌过程。`, question, cardsDesc)
}

// buildDefaultDetailPrompt 构建默认详情Prompt
func (s *TarotService) buildDefaultDetailPrompt(question, cardsDesc, spread string) string {
	spreadName := "单张牌"
	switch spread {
	case "three":
		spreadName = "三张牌阵（过去/现在/未来）"
	case "cross":
		spreadName = "十字牌阵（10张牌）"
	}

	return fmt.Sprintf(`你是一位专业的塔罗占卜师。用户提出了以下问题：

问题：%s

牌阵类型：%s

抽出的牌及其含义：
%s

请详细解读每张牌的意义，结合它们在牌阵中的位置，分析它们之间的关系，并结合用户的问题给出完整的占卜解读和具体建议。`, question, spreadName, cardsDesc)
}

// buildSimpleSummary 构建简单摘要（降级方案）
func (s *TarotService) buildSimpleSummary(cards []TarotCard, positions []string) string {
	if len(cards) == 0 {
		return "未能完成占卜，请稍后再试。"
	}

	// 改进的降级方案：包含基本的牌面含义
	var summary strings.Builder
	summary.WriteString("根据您抽出的牌面：\n\n")

	for i, card := range cards {
		pos := "当前"
		if i < len(positions) {
			pos = positions[i]
		}
		// 获取牌面的基本含义
		meaning := card.Meaning
		if strings.Contains(card.Name, "逆位") {
			meaning = card.Reversed
		}
		// 截取前50个字符作为简短描述
		shortMeaning := meaning
		if len(meaning) > 50 {
			shortMeaning = meaning[:50] + "..."
		}
		summary.WriteString(fmt.Sprintf("**%s - %s**：%s\n\n", pos, card.Name, shortMeaning))
	}

	summary.WriteString("建议您保持开放的心态，结合牌面的指引，相信自己的直觉做出决定。")

	return summary.String()
}

// buildSimpleInterpretation 构建简单解读（降级方案）
func (s *TarotService) buildSimpleInterpretation(cards []TarotCard, positions []string, spread string) string {
	var detail strings.Builder
	detail.WriteString("# 塔罗牌占卜解读\n\n")

	for i, card := range cards {
		pos := "当前"
		if i < len(positions) {
			pos = positions[i]
		}
		detail.WriteString(fmt.Sprintf("## %s: %s\n\n", pos, card.Name))

		// 使用完整的牌面含义
		meaning := card.Meaning
		if strings.Contains(card.Name, "逆位") {
			meaning = card.Reversed
		}
		detail.WriteString(fmt.Sprintf("**含义**: %s\n\n", meaning))
	}

	detail.WriteString("## 综合建议\n\n")
	detail.WriteString("请结合每张牌的含义，思考它们与您问题的关联。塔罗牌为您提供了一个视角，但最终的决定权在您手中。相信您的直觉会指引您找到答案。\n\n")
	detail.WriteString("如需更深入的解读，建议您稍后重试或咨询专业的塔罗占卜师。")

	return detail.String()
}
