package service

import (
	"context"
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/repository"
	"fmt"
	"strings"
	"time"
)

// LLMProvider defines the interface for LLM interactions
type LLMProvider interface {
	GenerateAnswer(ctx context.Context, prompt string) (string, error)
}

type IntelligentPreprocessingService struct {
	userPatternRepo     *repository.UserPatternRepository
	questionQualityRepo *repository.QuestionQualityRepository
	userProfileSvc      *UserProfileService // Changed to Service dependency
	llmService          LLMProvider
}

// NewIntelligentPreprocessingService creates a new service instance
func NewIntelligentPreprocessingService(
	userPatternRepo *repository.UserPatternRepository,
	questionQualityRepo *repository.QuestionQualityRepository,
	userProfileSvc *UserProfileService,
	llmService LLMProvider,
) *IntelligentPreprocessingService {
	return &IntelligentPreprocessingService{
		userPatternRepo:     userPatternRepo,
		questionQualityRepo: questionQualityRepo,
		userProfileSvc:      userProfileSvc,
		llmService:          llmService,
	}
}

// ProcessQuestion handles the main preprocessing logic
func (s *IntelligentPreprocessingService) ProcessQuestion(
	userID string,
	rawQuestion string,
	reqContext model.QuestionContext,
) (*model.PreprocessResponse, error) {
	// 1. Analyze Quality
	quality := s.analyzeQuality(rawQuestion)

	// 2. Classify Intent
	intent := s.classifyIntent(rawQuestion)

	// 3. User Profile Enhancement
	userEnhancement := s.enhanceWithUserProfile(userID, rawQuestion)

	// 4. Reconstruct Decision
	response := &model.PreprocessResponse{
		OriginalQuestion: rawQuestion,
		QualityScore:     quality.Score,
		QualityBreakdown: map[string]float64{
			"specificity":        quality.Specificity,
			"personal_relevance": quality.PersonalRelevance,
			"decision_value":     quality.DecisionValue,
			"temporal_relevance": quality.TemporalRelevance,
		},
		RecommendedApproach: "direct", // Default
		Intent:              intent,
	}

	if quality.Score < 0.7 {
		enhanced, suggestions := s.reconstructQuestion(rawQuestion, userEnhancement, reqContext)
		response.EnhancedQuestion = enhanced
		response.UseEnhanced = true
		response.Suggestions = suggestions
		response.RecommendedApproach = "guided"
	} else {
		response.EnhancedQuestion = rawQuestion
		response.UseEnhanced = false
		response.Suggestions = []model.EnhancementSuggestion{}
	}

	// 4. Save History
	history := &model.QuestionQualityHistory{
		SessionID:        "", // Optional, might be filled later if session created
		OriginalQuestion: rawQuestion,
		EnhancedQuestion: response.EnhancedQuestion,
		QualityScore:     quality.Score,
		QualityFactors:   response.QualityBreakdown,
		CreatedAt:        time.Now(),
	}
	_ = s.questionQualityRepo.Save(history)

	return response, nil
}

func (s *IntelligentPreprocessingService) classifyIntent(question string) string {
	// Fast keyword-based classification
	q := strings.ToLower(question)

	// Binary Choice
	if strings.Contains(q, "还是") ||
		strings.Contains(q, "要不要") ||
		strings.Contains(q, "该不该") ||
		strings.Contains(q, "选") ||
		(strings.Contains(q, "左") && strings.Contains(q, "右")) {
		return model.IntentBinaryChoice
	}

	// Daily Luck
	if strings.Contains(q, "运势") ||
		strings.Contains(q, "运气") ||
		strings.Contains(q, "颜色") ||
		strings.Contains(q, "方位") ||
		strings.Contains(q, "穿") ||
		strings.Contains(q, "幸运") {
		return model.IntentDailyLuck
	}

	// Knowledge
	if strings.Contains(q, "是什么") ||
		strings.Contains(q, "什么意思") ||
		strings.Contains(q, "解释") ||
		strings.Contains(q, "含义") {
		return model.IntentKnowledge
	}

	// Default to Deep Analysis
	return model.IntentDeepAnalysis
}

func (s *IntelligentPreprocessingService) analyzeQuality(question string) model.QuestionQuality {
	// Simple rule-based analysis for now
	length := len([]rune(question))

	specificity := 0.5
	if length > 10 {
		specificity = 0.8
	} else if length < 5 {
		specificity = 0.2
	}

	personalRelevance := 0.5
	if strings.Contains(question, "我") || strings.Contains(question, "我的") {
		personalRelevance = 0.9
	}

	decisionValue := 0.5
	if strings.Contains(question, "怎么办") || strings.Contains(question, "选") {
		decisionValue = 0.8
	}

	temporalRelevance := 0.5
	if strings.Contains(question, "今天") || strings.Contains(question, "未来") {
		temporalRelevance = 0.8
	}

	score := (specificity + personalRelevance + decisionValue + temporalRelevance) / 4.0

	return model.QuestionQuality{
		Score:             score,
		Specificity:       specificity,
		PersonalRelevance: personalRelevance,
		DecisionValue:     decisionValue,
		TemporalRelevance: temporalRelevance,
	}
}

func (s *IntelligentPreprocessingService) enhanceWithUserProfile(userID string, question string) string {
	// Fetch profile if exists
	if s.userProfileSvc == nil {
		return ""
	}

	profile, err := s.userProfileSvc.GetProfile(userID)
	if err != nil || profile == nil {
		return ""
	}

	// Construct context string from profile
	var info []string
	if profile.Nickname != "" {
		info = append(info, fmt.Sprintf("用户昵称：%s", profile.Nickname))
	}
	if profile.Gender != "" {
		info = append(info, fmt.Sprintf("性别：%s", profile.Gender))
	}
	if profile.ZodiacSign != "" {
		info = append(info, fmt.Sprintf("星座：%s", profile.ZodiacSign))
	}

	// Add more profile details as needed

	return strings.Join(info, "，")
}

func (s *IntelligentPreprocessingService) reconstructQuestion(
	raw string,
	userContext string,
	ctx model.QuestionContext,
) (string, []model.EnhancementSuggestion) {
	// Simple reconstruction logic
	enhanced := raw
	suggestions := []model.EnhancementSuggestion{}

	if len([]rune(raw)) < 5 {
		enhanced = fmt.Sprintf("鉴于当前的情况，%s", raw)
		suggestions = append(suggestions, model.EnhancementSuggestion{
			Type:        "clarification",
			Message:     "问题过于简短，已添加上下文前缀",
			AutoApplied: true,
		})
	}

	if !strings.Contains(raw, "我") {
		enhanced = "对我而言，" + enhanced
		suggestions = append(suggestions, model.EnhancementSuggestion{
			Type:        "personalization",
			Message:     "已添加第一人称视角",
			AutoApplied: true,
		})
	}

	// If LLM service is available, we could use it here to generate a better question
	if s.llmService != nil {
		prompt := fmt.Sprintf("请重构以下占卜问题，使其更具体和具有启发性：'%s'", raw)
		llmEnhanced, err := s.llmService.GenerateAnswer(context.Background(), prompt)
		if err == nil && len(llmEnhanced) > 0 {
			enhanced = llmEnhanced
			suggestions = append(suggestions, model.EnhancementSuggestion{
				Type:        "llm_enhancement",
				Message:     "AI已基于占卜原则优化问题表述",
				AutoApplied: true,
			})
		}
	}

	return enhanced, suggestions
}
