package model

import "time"

// DailyFortune 每日运势模型
type DailyFortune struct {
	ID        uint      `json:"id" gorm:"primaryKey"`
	UserID    string    `json:"user_id" gorm:"index"`
	Date      time.Time `json:"date" gorm:"index"`

	// 基础运势
	Score   int    `json:"score"`   // 综合运势分数 (0-100)
	Summary string `json:"summary"` // 运势概述

	// 详细建议
	Wealth string `json:"wealth"` // 财运
	Career string `json:"career"` // 事业
	Love   string `json:"love"`   // 感情
	Health string `json:"health"` // 健康

	// 幸运指南
	LuckyColor     string `json:"lucky_color"`     // 幸运色
	LuckyNumber    string `json:"lucky_number"`    // 幸运数字
	LuckyDirection string `json:"lucky_direction"` // 幸运方位
	LuckyTime      string `json:"lucky_time"`      // 幸运时辰

	// 宜忌
	Yi []string `json:"yi" gorm:"serializer:json"` // 宜
	Ji []string `json:"ji" gorm:"serializer:json"` // 忌

	// 节气/节日上下文 (生成时的背景)
	SolarTerm string `json:"solar_term"`
	Festival  string `json:"festival"`

	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// DailyFortuneRequest 请求生成每日运势
type DailyFortuneRequest struct {
	UserID string `json:"user_id" binding:"required"`
	Date   string `json:"date"` // YYYY-MM-DD, optional, default to today
}
