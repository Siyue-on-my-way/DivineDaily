package service

import (
	"context"
	"divine-daily-backend/internal/model"
	"fmt"
	"strings"
	"time"
)

// processTarotQuestion 处理塔罗牌占卜
func (s *DivinationService) processTarotQuestion(
	sessionID string,
	question string,
	userID string,
	spread string,
) (*model.DivinationResult, error) {
	// 1. 获取用户档案（可选）
	profile, err := s.userProfileSvc.GetProfile(userID)
	if err != nil {
		profile = &model.UserProfile{UserID: userID}
	}

	// 2. 确定牌阵类型和需要的牌数
	if spread == "" {
		spread = "single"
	}
	positions := GetSpreadPositions(spread)
	cardCount := GetSpreadCardCount(spread)

	// 3. 创建塔罗牌服务（使用塔罗牌场景的LLM服务）
	var tarotLLMService LLMService
	if s.configSvc != nil {
		// 使用塔罗牌场景的LLM服务
		tarotLLMService = NewDatabaseLLMService(s.configSvc, "tarot")
	} else {
		// 降级到Mock服务
		tarotLLMService = NewMockLLMService()
	}
	tarotSvc := NewTarotService(tarotLLMService, s.configSvc)

	// 4. 抽牌
	cards, reversed, err := tarotSvc.DrawCards(sessionID, spread, cardCount)
	if err != nil {
		return nil, fmt.Errorf("抽牌失败: %w", err)
	}

	// 5. 转换为TarotCardDraw格式（先构建，供后续使用）
	cardDraws := make([]model.TarotCardDraw, 0, len(cards))
	for i, card := range cards {
		pos := "当前"
		if i < len(positions) {
			pos = positions[i]
		}
		// 提取原始牌名（去除逆位标识）
		cardName := card.Name
		cardNameEN := card.NameEN
		isReversed := false
		if i < len(reversed) {
			isReversed = reversed[i]
		}
		// 如果牌名包含逆位标识，去除它（因为我们已经有了IsReversed字段）
		if strings.Contains(cardName, "（逆位）") {
			cardName = strings.ReplaceAll(cardName, "（逆位）", "")
		}
		if strings.Contains(cardNameEN, " (Reversed)") {
			cardNameEN = strings.ReplaceAll(cardNameEN, " (Reversed)", "")
		}
		cardDraws = append(cardDraws, model.TarotCardDraw{
			Name:       cardName,
			NameEN:     cardNameEN,
			Position:   pos,
			IsReversed: isReversed,
		})
	}

	// 6. 构建标题
	title := getTarotSpreadTitle(spread)

	// 7. 生成摘要（结果卡）- 同步生成
	ctx := context.Background()
	summary, err := tarotSvc.GenerateSummary(ctx, question, cards, positions)
	if err != nil {
		summary = tarotSvc.buildSimpleSummary(cards, positions)
	}

	// 8. 生成详细解读
	detail, err := tarotSvc.GenerateInterpretation(ctx, question, cards, positions, spread, profile)
	if err != nil {
		// 如果生成详细解读失败，使用简单解读
		detail = tarotSvc.buildSimpleInterpretation(cards, positions, spread)
	}

	// 9. 返回完整结果
	return &model.DivinationResult{
		SessionID: sessionID,
		Title:     title,
		Spread:    spread,
		Cards:     cardDraws,
		Summary:   summary,
		Detail:    detail,
		CreatedAt: time.Now(),
	}, nil
}

// getTarotSpreadTitle 获取牌阵标题
func getTarotSpreadTitle(spread string) string {
	switch spread {
	case "three":
		return "塔罗牌 · 三张牌阵"
	case "cross":
		return "塔罗牌 · 十字牌阵"
	default:
		return "塔罗牌 · 单张牌"
	}
}
