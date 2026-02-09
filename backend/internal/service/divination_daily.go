package service

import (
	"divine-daily-backend/internal/model"
	"fmt"
	"time"
)

// processDailyFortune 处理每日运势请求
func (s *DivinationService) processDailyFortune(
	sessionID string,
	userID string,
) (*model.DivinationResult, error) {
	// 调用每日运势服务
	fortune, err := s.dailyFortuneSvc.GenerateDailyFortune(userID, time.Now())
	if err != nil {
		return nil, fmt.Errorf("generate daily fortune: %w", err)
	}

	// 转换为DivinationResult
	// Summary: 简短的运势概述 + 关键幸运信息
	summary := fmt.Sprintf("今日运势评分：%d分。\n%s\n幸运色：%s，幸运数字：%s，幸运方位：%s。", 
		fortune.Score, fortune.Summary, fortune.LuckyColor, fortune.LuckyNumber, fortune.LuckyDirection)

	// Detail: 完整的运势报告
	detail := fmt.Sprintf(`
【综合运势】%d分
%s

【财运】
%s

【事业】
%s

【感情】
%s

【健康】
%s

【今日宜忌】
宜：%v
忌：%v

【幸运指南】
颜色：%s | 数字：%s | 方位：%s | 时辰：%s
`, 
		fortune.Score, fortune.Summary,
		fortune.Wealth,
		fortune.Career,
		fortune.Love,
		fortune.Health,
		fortune.Yi, fortune.Ji,
		fortune.LuckyColor, fortune.LuckyNumber, fortune.LuckyDirection, fortune.LuckyTime)

	// Recommendations: 提取建议作为推荐项
	recommendations := []model.RecommendationItem{
		{Content: "财运建议", Reason: fortune.Wealth},
		{Content: "事业建议", Reason: fortune.Career},
		{Content: "感情建议", Reason: fortune.Love},
		{Content: "健康建议", Reason: fortune.Health},
	}

	return &model.DivinationResult{
		SessionID:       sessionID,
		Outcome:         "吉", // 默认，或根据分数判断
		Title:           "每日运势",
		Summary:         summary,
		Detail:          detail,
		Recommendations: recommendations,
		DailyFortune:    fortune,
		CreatedAt:       time.Now(),
	}, nil
}
