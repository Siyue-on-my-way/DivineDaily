package service

import (
	"context"
	"database/sql"
	"divine-daily-backend/internal/model"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"
)

type DailyFortuneService struct {
	timeSvc        *TimeConvertService
	userProfileSvc *UserProfileService
	llmSvc         LLMService
	configSvc      *ConfigService
}

func NewDailyFortuneService(timeSvc *TimeConvertService, userProfileSvc *UserProfileService, llmSvc LLMService, configSvc *ConfigService) *DailyFortuneService {
	return &DailyFortuneService{
		timeSvc:        timeSvc,
		userProfileSvc: userProfileSvc,
		llmSvc:         llmSvc,
		configSvc:      configSvc,
	}
}

// GenerateDailyFortune 生成每日运势
func (s *DailyFortuneService) GenerateDailyFortune(userID string, date time.Time) (*model.DailyFortune, error) {
	// 1. 获取用户信息
	userProfile, err := s.userProfileSvc.GetProfile(userID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || strings.Contains(err.Error(), "no rows in result set") {
			return nil, fmt.Errorf("未找到用户档案，请先登录并完善个人资料")
		}
		return nil, fmt.Errorf("failed to get user profile: %w", err)
	}

	// 2. 获取当日时间信息 (节气、节日、干支等)
	dailyInfo, err := s.timeSvc.GetDailyInfo(date)
	if err != nil {
		return nil, fmt.Errorf("failed to get daily info: %w", err)
	}

	// 3. 构建Prompt
	prompt := s.buildPrompt(userProfile, dailyInfo, date)

	// 4. 调用LLM
	response, err := s.llmSvc.GenerateAnswer(context.Background(), prompt)
	if err != nil {
		return nil, fmt.Errorf("failed to call LLM: %w", err)
	}

	// 5. 解析结果
	fortune, err := s.parseLLMResponse(response)
	if err != nil {
		return nil, fmt.Errorf("failed to parse LLM response: %w", err)
	}

	// 6. 填充额外信息
	fortune.UserID = userID
	fortune.Date = date
	fortune.SolarTerm = dailyInfo.Term
	if dailyInfo.Festival != "" {
		fortune.Festival = dailyInfo.Festival
	} else {
		fortune.Festival = dailyInfo.LunarFestival
	}
	fortune.CreatedAt = time.Now()
	fortune.UpdatedAt = time.Now()

	return fortune, nil
}

func (s *DailyFortuneService) buildPrompt(profile *model.UserProfile, dailyInfo *ConversionResult, date time.Time) string {
	// 准备变量
	variables := map[string]interface{}{
		"Date":          date.Format("2006-01-02"),
		"Nickname":      profile.Nickname,
		"Gender":        profile.Gender,
		"BirthDate":     profile.BirthDate,
		"Animal":        profile.Animal,
		"ZodiacSign":    profile.ZodiacSign,
		"LunarMonthCn":  dailyInfo.LunarMonthCn,
		"LunarDayCn":    dailyInfo.LunarDayCn,
		"GanZhiYear":    dailyInfo.GanZhiYear,
		"GanZhiMonth":   dailyInfo.GanZhiMonth,
		"GanZhiDay":     dailyInfo.GanZhiDay,
		"Term":          dailyInfo.Term,
		"Festival":      dailyInfo.Festival,
		"LunarFestival": dailyInfo.LunarFestival,
	}

	// 尝试从配置中渲染
	prompt, err := s.configSvc.RenderPromptFromConfig("daily_fortune", "default", variables)
	if err == nil && prompt != "" {
		return prompt
	}

	// 降级使用硬编码Prompt
	return fmt.Sprintf(`
请为用户生成今日(%s)运势。
用户信息:
昵称: %s
性别: %s
生日: %s
生肖: %s
星座: %s

今日时间信息:
农历: %s %s
干支: %s年 %s月 %s日
节气: %s
节日: %s / %s
宜忌参考: (可根据干支自行推演或忽略)

请返回严格的JSON格式，包含以下字段:
{
  "score": 0-100的整数,
  "summary": "一句话运势概述",
  "wealth": "财运建议",
  "career": "事业建议",
  "love": "感情建议",
  "health": "健康建议",
  "lucky_color": "幸运色",
  "lucky_number": "幸运数字",
  "lucky_direction": "幸运方位",
  "lucky_time": "幸运时辰",
  "yi": ["宜做的事1", "宜做的事2"],
  "ji": ["忌做的事1", "忌做的事2"]
}
仅返回JSON，不要Markdown格式。
`, date.Format("2006-01-02"),
		profile.Nickname, profile.Gender, profile.BirthDate, profile.Animal, profile.ZodiacSign,
		dailyInfo.LunarMonthCn, dailyInfo.LunarDayCn,
		dailyInfo.GanZhiYear, dailyInfo.GanZhiMonth, dailyInfo.GanZhiDay,
		dailyInfo.Term, dailyInfo.Festival, dailyInfo.LunarFestival)
}

func (s *DailyFortuneService) parseLLMResponse(resp string) (*model.DailyFortune, error) {
	// Clean up markdown code blocks if present
	jsonStr := resp
	if idx := strings.Index(jsonStr, "```json"); idx != -1 {
		jsonStr = jsonStr[idx+7:]
		if endIdx := strings.LastIndex(jsonStr, "```"); endIdx != -1 {
			jsonStr = jsonStr[:endIdx]
		}
	} else if idx := strings.Index(jsonStr, "```"); idx != -1 {
		jsonStr = jsonStr[idx+3:]
		if endIdx := strings.LastIndex(jsonStr, "```"); endIdx != -1 {
			jsonStr = jsonStr[:endIdx]
		}
	}

	jsonStr = strings.TrimSpace(jsonStr)

	var fortune model.DailyFortune
	err := json.Unmarshal([]byte(jsonStr), &fortune)
	if err != nil {
		return nil, fmt.Errorf("json unmarshal error: %w, response: %s", err, resp)
	}
	return &fortune, nil
}
