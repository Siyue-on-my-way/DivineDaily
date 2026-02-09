package service

import (
	"divine-daily-backend/internal/model"
	"strings"
)

func (s *DivinationService) RecommendOrientation(req model.OrientationRecommendRequest) (*model.OrientationRecommendResponse, error) {
	if req.Version == "CN" {
		options := []model.OrientationOption{
			{Key: "E", Label: "东方（震）"},
			{Key: "SE", Label: "东南（巽）"},
			{Key: "S", Label: "南方（离）"},
			{Key: "SW", Label: "西南（坤）"},
			{Key: "W", Label: "西方（兑）"},
			{Key: "NW", Label: "西北（乾）"},
			{Key: "N", Label: "北方（坎）"},
			{Key: "NE", Label: "东北（艮）"},
		}

		recommendedKey := "E"
		reason := "难以归类时取东方（震），取“行动与开启”之象。"

		q := strings.ToLower(strings.TrimSpace(req.Question))
		switch req.EventType {
		case "decision":
			recommendedKey = "E"
			reason = "此事偏“行动与开启”，取东方（震）以助决断。"
		case "career":
			recommendedKey = "NW"
			reason = "此事关乎事业目标与掌控，取西北（乾）以应“权威与进取”。"
		case "relationship":
			recommendedKey = "W"
			reason = "此事偏沟通与关系互动，取西方（兑）以应“言说与和悦”。"
		}

		if strings.Contains(q, "学习") || strings.Contains(q, "考试") || strings.Contains(q, "看清") || strings.Contains(q, "启示") {
			recommendedKey = "S"
			reason = "此事偏“看清与求启示”，取南方（离）以明照。"
		}
		if strings.Contains(q, "止损") || strings.Contains(q, "休息") || strings.Contains(q, "焦虑") || strings.Contains(q, "内观") {
			recommendedKey = "N"
			reason = "此事宜先止损休整，取北方（坎）以沉潜内观。"
		}
		if strings.Contains(q, "规划") || strings.Contains(q, "稳") || strings.Contains(q, "沉淀") {
			recommendedKey = "NE"
			reason = "此事宜规划沉淀，取东北（艮）以稳固。"
		}
		if strings.Contains(q, "机缘") || strings.Contains(q, "扩展") || strings.Contains(q, "变通") {
			recommendedKey = "SE"
			reason = "此事偏机缘与灵活变通，取东南（巽）以顺势而入。"
		}

		label := findOrientationLabel(options, recommendedKey)
		return &model.OrientationRecommendResponse{
			RecommendedKey:   recommendedKey,
			RecommendedLabel: label,
			Reason:           reason,
			Options:          options,
			ToleranceDeg:     15,
		}, nil
	}

	options := []model.OrientationOption{
		{Key: "E", Label: "East (Air / Swords)"},
		{Key: "S", Label: "South (Fire / Wands)"},
		{Key: "W", Label: "West (Water / Cups)"},
		{Key: "N", Label: "North (Earth / Pentacles)"},
	}

	recommendedKey := "E"
	reason := "When it's unclear, face East to seek clarity."

	q := strings.ToLower(strings.TrimSpace(req.Question))
	switch req.EventType {
	case "decision":
		recommendedKey = "E"
		reason = "Face East (Air) to sharpen thinking and decision-making."
	case "career":
		recommendedKey = "S"
		reason = "Face South (Fire) to boost momentum and ambition."
	case "relationship":
		recommendedKey = "W"
		reason = "Face West (Water) to soften emotions and support connection."
	}

	if strings.Contains(q, "money") || strings.Contains(q, "finance") || strings.Contains(q, "body") || strings.Contains(q, "health") {
		recommendedKey = "N"
		reason = "Face North (Earth) to ground the situation into practical steps."
	}

	label := findOrientationLabel(options, recommendedKey)
	return &model.OrientationRecommendResponse{
		RecommendedKey:   recommendedKey,
		RecommendedLabel: label,
		Reason:           reason,
		Options:          options,
		ToleranceDeg:     15,
	}, nil
}

func findOrientationLabel(options []model.OrientationOption, key string) string {
	for _, opt := range options {
		if opt.Key == key {
			return opt.Label
		}
	}
	if len(options) > 0 {
		return options[0].Label
	}
	return key
}

