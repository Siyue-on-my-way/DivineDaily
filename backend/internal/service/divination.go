package service

import (
	"context"
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/repository"
	"fmt"
	"hash/fnv"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
	"log"
)

type DivinationService struct {
	// 数据库仓库（优先使用）
	repo *repository.DivinationRepository

	// 内存存储（降级方案，如果数据库不可用）
	sessions sync.Map
	results  sync.Map

	// Services
	questionClassifier *QuestionClassifier
	questionAnalyzer   *QuestionAnalyzer // 新增：智能问题分析器
	llmService         LLMService
	userProfileSvc     *UserProfileService
	dailyFortuneSvc    *DailyFortuneService
	configSvc          *ConfigService
}

func NewDivinationService() *DivinationService {
	return &DivinationService{
		repo:               nil, // 需要在main.go中注入
		questionClassifier: NewQuestionClassifier(),
		llmService:         NewMockLLMService(),
		userProfileSvc:     NewUserProfileService(),
		configSvc:          nil, // 需要在main.go中注入
	}
}

// SetRepository 设置数据库仓库（依赖注入）
func (s *DivinationService) SetRepository(repo *repository.DivinationRepository) {
	s.repo = repo
}

// SetConfigService 设置配置服务（依赖注入）
func (s *DivinationService) SetConfigService(configSvc *ConfigService) {
	s.configSvc = configSvc

	// 如果配置服务可用，使用数据库配置的LLM服务（占卜场景）
	if configSvc != nil {
		s.llmService = NewDatabaseLLMService(configSvc, "divination")
		// 初始化问题分析器
		s.questionAnalyzer = NewQuestionAnalyzer(s.llmService)
	} else {
		// 降级到Mock服务
		s.llmService = NewMockLLMService()
		s.questionAnalyzer = NewQuestionAnalyzer(s.llmService)
	}
}

// SetDailyFortuneService 设置每日运势服务（依赖注入）
func (s *DivinationService) SetDailyFortuneService(svc *DailyFortuneService) {
	s.dailyFortuneSvc = svc
}

// StartDivination creates a session and triggers the divination process
func (s *DivinationService) StartDivination(req model.CreateDivinationRequest) (*model.DivinationSession, error) {
	log.Printf("[占卜流程] 步骤3: Service层开始处理 - 问题: %s, 版本: %s", req.Question, req.Version)
	
	session := &model.DivinationSession{
		ID:              uuid.New().String(),
		UserID:          req.UserID,
		Version:         req.Version,
		Question:        req.Question,
		EventType:       req.EventType, // 保留但不再强制要求
		Orientation:     req.Orientation,
		Spread:          req.Spread,
		Intent:          req.Intent,
		CreatedAt:       time.Now(),
		UpdatedAt:       time.Now(),
		Status:          "created",
		FollowUpCount:   0,
		FollowUpAnswers: nil,
	}

	// Save to in-memory store (降级方案)
	s.sessions.Store(session.ID, session)
	log.Printf("[占卜流程] 步骤4: 会话已保存到内存 - SessionID: %s", session.ID)

	// Save to database (优先使用)
	if s.repo != nil {
		if err := s.repo.SaveSession(session); err != nil {
			log.Printf("[占卜流程] 警告: 数据库保存失败，使用内存存储 - SessionID: %s, Error: %v", session.ID, err)
		} else {
			log.Printf("[占卜流程] 步骤5: 会话已保存到数据库 - SessionID: %s", session.ID)
		}
	}

	// 根据版本处理
	log.Printf("[占卜流程] 步骤6: 根据版本选择处理方式 - 版本: %s", req.Version)
	
	if req.Version == "TAROT" {
		// 塔罗牌占卜
		log.Printf("[占卜流程] 步骤7: 启动塔罗牌占卜异步处理 - SessionID: %s", session.ID)
		go func() {
			result, err := s.processTarotQuestion(session.ID, req.Question, req.UserID, req.Spread)
			s.saveResult(session.ID, result, err)
		}()
	} else if req.Version == "CN" {
		// 国内版：使用智能问题分析
		log.Printf("[占卜流程] 步骤7: 启动国内版占卜异步处理 - SessionID: %s", session.ID)
		go func() {
			var result *model.DivinationResult
			var err error

			// 1. 使用智能问题分析器分析问题
			log.Printf("[占卜流程] 步骤8: 开始智能问题分析 - SessionID: %s, 问题: %s", session.ID, req.Question)
			ctx := context.Background()
			analysis, analyzeErr := s.questionAnalyzer.AnalyzeQuestion(ctx, req.Question)
			if analyzeErr != nil {
				// 如果分析失败，使用降级逻辑
				log.Printf("[占卜流程] 警告: 智能分析失败，使用降级逻辑 - SessionID: %s, Error: %v", session.ID, analyzeErr)
				analysis = s.questionAnalyzer.fallbackAnalysis(req.Question)
			} else {
				log.Printf("[占卜流程] 步骤9: 问题分析完成 - SessionID: %s, 问题类型: %s, 意图: %s", session.ID, analysis.QuestionType, analysis.Intent)
			}

			// 2. 将分析结果添加到上下文
			questionContext := req.Context
			if questionContext == nil {
				questionContext = make(map[string]interface{})
			}
			questionContext["analysis"] = analysis
			questionContext["question_type"] = analysis.QuestionType
			questionContext["intent"] = analysis.Intent
			questionContext["elements"] = analysis.Elements

			// 3. 根据分析结果选择处理策略
			log.Printf("[占卜流程] 步骤10: 根据问题类型选择处理策略 - SessionID: %s, 类型: %s", session.ID, analysis.QuestionType)
			
			switch analysis.QuestionType {
			case "fortune":
				// 运势类问题
				log.Printf("[占卜流程] 步骤11: 处理运势类问题 - SessionID: %s", session.ID)
				if s.dailyFortuneSvc != nil {
					result, err = s.processDailyFortune(session.ID, req.UserID)
				} else {
					result, err = s.processRecommendationQuestion(session.ID, req.Question, req.UserID)
				}
			case "knowledge":
				// 知识类问题
				log.Printf("[占卜流程] 步骤11: 处理知识类问题 - SessionID: %s", session.ID)
				result, err = s.processKnowledgeQuestion(session.ID, req.Question, req.UserID, questionContext, analysis)
			default:
				// 决策类、感情类、事业类都使用决策逻辑（周易卦象）
				log.Printf("[占卜流程] 步骤11: 处理决策类问题（周易卦象） - SessionID: %s", session.ID)
				result, err = s.processDecisionQuestion(session.ID, req.Question, req.UserID, questionContext)
			}

			// 4. 将分析结果添加到返回结果中
			if result != nil && analysis != nil {
				result.QuestionType = analysis.QuestionType
				result.QuestionIntent = analysis.Intent
				log.Printf("[占卜流程] 步骤12: 占卜处理完成 - SessionID: %s, 卦象: %s, 结果: %s", session.ID, result.Title, result.Outcome)
			}
			
			if err != nil {
				log.Printf("[占卜流程] 错误: 占卜处理失败 - SessionID: %s, Error: %v", session.ID, err)
			}

			s.saveResult(session.ID, result, err)
		}()
	} else if req.Version == "Global" && req.EventType == "tarot" {
		// 全球版：塔罗牌占卜（兼容旧逻辑）
		go func() {
			result, err := s.processTarotQuestion(session.ID, req.Question, req.UserID, req.Spread)
			s.saveResult(session.ID, result, err)
		}()
	} else {
		// 其他情况使用原有逻辑
		go func() {
			spread := strings.TrimSpace(session.Spread)
			if session.Version == "Global" && spread == "" {
				spread = "single"
			}
			result := s.generateWesternResult(session.EventType, spread, session.ID)
			s.saveResult(session.ID, result, nil)
		}()
	}

	return session, nil
}

// processKnowledgeQuestion 处理知识类问题
func (s *DivinationService) processKnowledgeQuestion(
	sessionID string,
	question string,
	userID string,
	questionContext map[string]interface{},
	analysis *QuestionAnalysis,
) (*model.DivinationResult, error) {
	// 知识类问题也生成卦象，但重点在于解释和传授知识
	return s.processDecisionQuestion(sessionID, question, userID, questionContext)
}

// saveResult 保存结果的通用方法
func (s *DivinationService) saveResult(sessionID string, result *model.DivinationResult, err error) {
	if err != nil {
		// 如果处理失败，创建错误结果
		result = &model.DivinationResult{
			SessionID: sessionID,
			Outcome:   "未知",
			Title:     "处理失败",
			Summary:   fmt.Sprintf("处理问题时发生错误: %v", err),
			Detail:    fmt.Sprintf("请稍后再试。错误详情: %v", err),
			CreatedAt: time.Now(),
		}
	}

	if result != nil {
		// 保存结果到数据库（如果可用）或内存
		if s.repo != nil {
			if err := s.repo.SaveResult(result); err != nil {
				// 如果数据库保存失败，降级到内存存储
				s.results.Store(sessionID, result)
			}
			// 更新会话状态
			s.repo.UpdateSessionStatus(sessionID, "completed")
		} else {
			s.results.Store(sessionID, result)
			// 更新内存中的session状态
			if val, ok := s.sessions.Load(sessionID); ok {
				sess := val.(*model.DivinationSession)
				sess.Status = "completed"
				s.sessions.Store(sessionID, sess)
			}
		}
	}
}

// GetResult returns result based on session ID
func (s *DivinationService) GetResult(sessionID string) (*model.DivinationResult, error) {
	// 优先从数据库获取结果
	if s.repo != nil {
		result, err := s.repo.GetResult(sessionID)
		if err == nil && result != nil {
			// 如果数据库中有结果，缓存到内存并返回
			s.results.Store(sessionID, result)
			return result, nil
		}
	}

	// 尝试从内存获取结果
	if resultVal, ok := s.results.Load(sessionID); ok {
		return resultVal.(*model.DivinationResult), nil
	}

	// 如果没有结果，检查session状态
	var session *model.DivinationSession

	// 优先从数据库获取session
	if s.repo != nil {
		dbSession, err := s.repo.GetSession(sessionID)
		if err == nil && dbSession != nil {
			session = dbSession
			s.sessions.Store(sessionID, session)
		}
	}

	// 如果数据库中没有，尝试从内存获取
	if session == nil {
		val, ok := s.sessions.Load(sessionID)
		if !ok {
			return nil, fmt.Errorf("session not found")
		}
		session = val.(*model.DivinationSession)
	}

	// 如果session还在处理中，返回处理中状态
	if session.Status == "processing" {
		return &model.DivinationResult{
			SessionID: sessionID,
			Summary:   "结果生成中，请稍候...",
			CreatedAt: time.Now(),
		}, nil
	}

	// 否则使用旧的buildResult方法（兼容旧逻辑）
	return s.buildResult(session), nil
}

func (s *DivinationService) buildResult(session *model.DivinationSession) *model.DivinationResult {
	spread := strings.TrimSpace(session.Spread)
	if session.Version == "Global" && spread == "" {
		spread = "single"
	}

	var result *model.DivinationResult
	if session.Version == "CN" {
		result = s.generateEasternResult(session.EventType, session.ID)
	} else {
		result = s.generateWesternResult(session.EventType, spread, session.ID)
	}

	result.SceneAdvice = s.generateSceneAdvice(session.EventType, session.Version)

	if q := s.nextFollowUpQuestion(session); q != nil {
		result.NeedsFollowUp = true
		result.FollowUpQ = q
	} else {
		result.NeedsFollowUp = false
	}

	return result
}

// SubmitAnswer handles user's response to a follow-up question
func (s *DivinationService) SubmitAnswer(ans model.FollowUpAnswer) error {
	val, ok := s.sessions.Load(ans.SessionID)
	if !ok {
		return nil
	}

	session := val.(*model.DivinationSession)
	session.FollowUpCount++
	session.FollowUpAnswers = append(session.FollowUpAnswers, ans)
	s.sessions.Store(session.ID, session)
	return nil
}

func (s *DivinationService) nextFollowUpQuestion(session *model.DivinationSession) *model.FollowUpQuestion {
	// 移除追问逻辑，简化流程
	return nil
}

func (s *DivinationService) generateSceneAdvice(eventType, version string) []model.SceneAdviceItem {
	// 简化场景建议
	return []model.SceneAdviceItem{}
}

func (s *DivinationService) generateEasternResult(eventType, sessionID string) *model.DivinationResult {
	// 使用完整的周易六爻算法生成卦象
	return GenerateIChingResult(sessionID, eventType)
}

func (s *DivinationService) generateWesternResult(eventType, spread, sessionID string) *model.DivinationResult {
	cards := []struct {
		Name    string
		Meaning string
	}{
		{Name: "The Fool", Meaning: "New beginnings, openness, and a leap of faith."},
		{Name: "The Magician", Meaning: "Focus, skill, and turning intention into reality."},
		{Name: "The High Priestess", Meaning: "Intuition, inner knowing, and hidden information."},
		{Name: "The Chariot", Meaning: "Willpower, discipline, and decisive movement."},
		{Name: "Justice", Meaning: "Balance, truth, and fair consequences."},
		{Name: "The Hermit", Meaning: "Pause, reflect, and seek wisdom within."},
		{Name: "Wheel of Fortune", Meaning: "Timing, cycles, and shifting circumstances."},
		{Name: "Strength", Meaning: "Courage, patience, and gentle control."},
		{Name: "The Lovers", Meaning: "Alignment, values, and meaningful choice."},
		{Name: "Temperance", Meaning: "Integration, moderation, and steady progress."},
	}

	positions := []string{"Guidance"}
	switch spread {
	case "three":
		positions = []string{"Past", "Present", "Future"}
	case "cross":
		positions = []string{"Present", "Challenge", "Foundation", "Recent Past", "Crown", "Near Future", "Self", "Environment", "Hopes/Fears", "Outcome"}
	}

	var draws []model.TarotCardDraw
	var detailLines []string
	for i, pos := range positions {
		idx := pickIndex(fmt.Sprintf("%s|%d|%s", sessionID, i, pos), len(cards))
		card := cards[idx]
		draws = append(draws, model.TarotCardDraw{Name: card.Name, Position: pos})
		detailLines = append(detailLines, fmt.Sprintf("- %s: %s", pos, card.Name))
	}

	outcome := "Neutral"
	title := "Tarot Spread"
	if spread == "three" {
		title = "Tarot · Three Cards"
	} else if spread == "cross" {
		title = "Tarot · Cross"
	} else {
		title = "Tarot · Single Card"
	}

	summary := fmt.Sprintf("%s. %s", outcome, cards[pickIndex(sessionID+"|summary", len(cards))].Meaning)
	detail := "# Cards\n" + strings.Join(detailLines, "\n") + "\n\n## Insight\n" + summary + "\n\n### Next Step\nChoose one small action you can take within 24 hours."

	return &model.DivinationResult{
		SessionID: sessionID,
		Outcome:   outcome,
		Title:     title,
		Spread:    spread,
		Cards:     draws,
		Summary:   summary,
		Detail:    detail,
		CreatedAt: time.Now(),
	}
}

func pickIndex(seed string, mod int) int {
	if mod <= 0 {
		return 0
	}
	h := fnv.New32a()
	_, _ = h.Write([]byte(seed))
	return int(h.Sum32() % uint32(mod))
}
