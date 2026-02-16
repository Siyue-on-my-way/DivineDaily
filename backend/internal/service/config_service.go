package service

import (
	"context"
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/repository"
	"fmt"
	"strings"
	"text/template"
	"time"
)

// ConfigService 配置管理服务
type ConfigService struct {
	llmConfigRepo    *repository.LLMConfigRepository
	promptConfigRepo *repository.PromptConfigRepository
}

// NewConfigService 创建配置服务
func NewConfigService(llmRepo *repository.LLMConfigRepository, promptRepo *repository.PromptConfigRepository) *ConfigService {
	return &ConfigService{
		llmConfigRepo:    llmRepo,
		promptConfigRepo: promptRepo,
	}
}

// ========== LLM配置管理 ==========

// GetLLMConfig 根据名称获取LLM配置
func (s *ConfigService) GetLLMConfig(name string) (*model.LLMConfig, error) {
	return s.llmConfigRepo.GetByName(name)
}

// GetDefaultLLMConfig 获取默认LLM配置（兼容旧代码，返回占卜场景的默认配置）
func (s *ConfigService) GetDefaultLLMConfig() (*model.LLMConfig, error) {
	return s.GetDefaultLLMConfigByScene("divination")
}

// GetDefaultLLMConfigByScene 根据场景获取默认LLM配置
func (s *ConfigService) GetDefaultLLMConfigByScene(scene string) (*model.LLMConfig, error) {
	return s.llmConfigRepo.GetDefault()
}

// ListLLMConfigs 获取所有LLM配置
func (s *ConfigService) ListLLMConfigs() ([]*model.LLMConfig, error) {
	return s.llmConfigRepo.ListAll()
}

// CreateLLMConfig 创建LLM配置
func (s *ConfigService) CreateLLMConfig(req *model.LLMConfigCreateRequest) (*model.LLMConfig, error) {
	config := &model.LLMConfig{
		Name:        req.Name,
		Provider:    req.Provider,
		URLType:     req.URLType,
		APIKey:      req.APIKey,
		Endpoint:    req.Endpoint,
		ModelName:   req.ModelName,
		IsDefault:   false,
		IsEnabled:   req.IsEnabled,
		Description: req.Description,
	}

	if err := s.llmConfigRepo.Create(config); err != nil {
		return nil, err
	}

	return config, nil
}

// UpdateLLMConfig 更新LLM配置
func (s *ConfigService) UpdateLLMConfig(id int, req *model.LLMConfigUpdateRequest) (*model.LLMConfig, error) {
	// 获取现有配置
	config, err := s.llmConfigRepo.GetByID(id)
	if err != nil {
		return nil, err
	}

	// 更新字段（只更新提供的字段）
	if req.Name != nil {
		config.Name = *req.Name
	}
	if req.Provider != nil {
		config.Provider = *req.Provider
	}
	if req.URLType != nil {
		config.URLType = *req.URLType
	}
	if req.APIKey != nil {
		// 如果API Key是空字符串，表示不更新（保持原值）
		if *req.APIKey != "" {
			config.APIKey = *req.APIKey
		}
	}
	if req.Endpoint != nil {
		config.Endpoint = *req.Endpoint
	}
	if req.ModelName != nil {
		config.ModelName = *req.ModelName
	}
	if req.IsEnabled != nil {
		config.IsEnabled = *req.IsEnabled
	}
	if req.Description != nil {
		config.Description = *req.Description
	}

	if err := s.llmConfigRepo.Update(config); err != nil {
		return nil, err
	}

	return config, nil
}

// DeleteLLMConfig 删除LLM配置
func (s *ConfigService) DeleteLLMConfig(id int) error {
	return s.llmConfigRepo.Delete(id)
}

// SetDefaultLLMConfig 设置默认LLM配置
func (s *ConfigService) SetDefaultLLMConfig(id int) error {
	return s.llmConfigRepo.SetDefault(id)
}

// TestLLMConfig 测试LLM配置（旧接口，保持兼容）
func (s *ConfigService) TestLLMConfig(id int) (string, error) {
	response, _, _, err := s.TestLLMConfigBlock(id)
	return response, err
}

// TestLLMConfigBlock 阻塞式测试LLM配置
func (s *ConfigService) TestLLMConfigBlock(id int) (response string, tokenCount int, durationMs int64, err error) {
	config, err := s.GetLLMConfigByID(id)
	if err != nil {
		return "", 0, 0, err
	}

	// 实例化OpenAIService (目前只支持OpenAI接口格式的)
	var llmSvc interface {
		GenerateAnswer(ctx context.Context, prompt string) (string, error)
	}

	switch config.Provider {
	case "openai", "local", "custom":
		// local和custom通常也是兼容OpenAI接口
		llmSvc = NewOpenAIService(config)
	default:
		return "", 0, 0, fmt.Errorf("暂不支持测试该提供商配置: %s", config.Provider)
	}

	if llmSvc == nil {
		return "", 0, 0, fmt.Errorf("创建LLM服务失败")
	}

	// 记录开始时间
	startTime := time.Now()

	// 调用GenerateAnswer进行测试
	testPrompt := "你好！这是一个连接测试。请简短回复'连接成功'即可。"
	response, err = llmSvc.GenerateAnswer(context.Background(), testPrompt)
	if err != nil {
		return "", 0, 0, err
	}

	// 计算耗时
	durationMs = time.Since(startTime).Milliseconds()

	// 估算token数（简单估算：中文约1.5字符/token，英文约4字符/token）
	tokenCount = len([]rune(response)) / 2
	if tokenCount == 0 {
		tokenCount = len(response) / 4
	}

	return response, tokenCount, durationMs, nil
}

// TestLLMConfigStream 流式测试LLM配置
func (s *ConfigService) TestLLMConfigStream(id int, streamChan chan<- string) error {
	config, err := s.GetLLMConfigByID(id)
	if err != nil {
		return err
	}

	// 实例化OpenAIService
	var llmSvc interface {
		GenerateAnswerStream(ctx context.Context, prompt string, streamChan chan<- string) error
	}

	switch config.Provider {
	case "openai", "local", "custom":
		llmSvc = NewOpenAIService(config)
	default:
		return fmt.Errorf("暂不支持测试该提供商配置: %s", config.Provider)
	}

	if llmSvc == nil {
		return fmt.Errorf("创建LLM服务失败")
	}

	// 调用流式接口
	testPrompt := "你好！这是一个流式连接测试。请用一段话（约50字）介绍一下你自己。"
	return llmSvc.GenerateAnswerStream(context.Background(), testPrompt, streamChan)
}

// MaskAPIKey 脱敏API Key（只显示前4位和后4位）
func MaskAPIKey(apiKey string) string {
	if apiKey == "" {
		return ""
	}
	if len(apiKey) <= 8 {
		return "****"
	}
	return apiKey[:4] + "****" + apiKey[len(apiKey)-4:]
}

// ToLLMConfigResponse 转换为响应格式（API Key脱敏）
func (s *ConfigService) ToLLMConfigResponse(config *model.LLMConfig) *model.LLMConfigResponse {
	return &model.LLMConfigResponse{
		ID:           config.ID,
		Name:         config.Name,
		Provider:     config.Provider,
		URLType:      config.URLType,
		APIKey:       config.APIKey, // 返回真实API Key
		APIKeyMasked: MaskAPIKey(config.APIKey),
		Endpoint:     config.Endpoint,
		ModelName:    config.ModelName,
		IsDefault:    config.IsDefault,
		IsEnabled:    config.IsEnabled,
		Description:  config.Description,
		CreatedAt:    config.CreatedAt,
		UpdatedAt:    config.UpdatedAt,
	}
}

// ========== Prompt配置管理 ==========

// GetPromptConfig 根据类型获取Prompt配置
func (s *ConfigService) GetPromptConfig(promptType, questionType string) (*model.PromptConfig, error) {
	return s.promptConfigRepo.GetByType(promptType, questionType)
}

// GetDefaultPromptConfig 获取默认Prompt配置
func (s *ConfigService) GetDefaultPromptConfig(promptType, questionType string) (*model.PromptConfig, error) {
	return s.promptConfigRepo.GetDefault(promptType, questionType)
}

// ListPromptConfigs 获取所有Prompt配置
func (s *ConfigService) ListPromptConfigs() ([]*model.PromptConfig, error) {
	return s.promptConfigRepo.ListAll()
}

// CreatePromptConfig 创建Prompt配置
func (s *ConfigService) CreatePromptConfig(req *model.PromptConfigCreateRequest) (*model.PromptConfig, error) {
	config := &model.PromptConfig{
		Name:         req.Name,
		PromptType:   req.PromptType,
		QuestionType: req.QuestionType,
		Template:     req.Template,
		Variables:    req.Variables,
		IsDefault:    false,
		IsEnabled:    req.IsEnabled,
		Description:  req.Description,
	}

	if err := s.promptConfigRepo.Create(config); err != nil {
		return nil, err
	}

	return config, nil
}

// UpdatePromptConfig 更新Prompt配置
func (s *ConfigService) UpdatePromptConfig(id int, req *model.PromptConfigUpdateRequest) (*model.PromptConfig, error) {
	// 获取现有配置
	config, err := s.promptConfigRepo.GetByID(id)
	if err != nil {
		return nil, err
	}

	// 更新字段（只更新提供的字段）
	if req.Name != nil {
		config.Name = *req.Name
	}
	if req.PromptType != nil {
		config.PromptType = *req.PromptType
	}
	if req.QuestionType != nil {
		config.QuestionType = *req.QuestionType
	}
	if req.Template != nil {
		config.Template = *req.Template
	}
	if req.Variables != nil {
		config.Variables = req.Variables
	}
	if req.IsEnabled != nil {
		config.IsEnabled = *req.IsEnabled
	}
	if req.Description != nil {
		config.Description = *req.Description
	}

	if err := s.promptConfigRepo.Update(config); err != nil {
		return nil, err
	}

	return config, nil
}

// DeletePromptConfig 删除Prompt配置
func (s *ConfigService) DeletePromptConfig(id int) error {
	return s.promptConfigRepo.Delete(id)
}

// SetDefaultPromptConfig 设置默认Prompt配置
func (s *ConfigService) SetDefaultPromptConfig(id int) error {
	return s.promptConfigRepo.SetDefault(id)
}

// RenderPrompt 渲染Prompt模板
func (s *ConfigService) RenderPrompt(templateStr string, variables map[string]interface{}) (string, error) {
	// 使用Go的text/template包渲染
	tmpl, err := template.New("prompt").Parse(templateStr)
	if err != nil {
		return "", fmt.Errorf("解析模板失败: %w", err)
	}

	var buf strings.Builder
	if err := tmpl.Execute(&buf, variables); err != nil {
		return "", fmt.Errorf("渲染模板失败: %w", err)
	}

	return buf.String(), nil
}

// RenderPromptFromConfig 从配置渲染Prompt
func (s *ConfigService) RenderPromptFromConfig(promptType, questionType string, variables map[string]interface{}) (string, error) {
	// 获取配置
	config, err := s.GetPromptConfig(promptType, questionType)
	if err != nil {
		return "", fmt.Errorf("获取Prompt配置失败: %w", err)
	}

	// 渲染模板
	return s.RenderPrompt(config.Template, variables)
}

// GetLLMConfigByID 根据ID获取LLM配置（供Handler使用）
func (s *ConfigService) GetLLMConfigByID(id int) (*model.LLMConfig, error) {
	return s.llmConfigRepo.GetByID(id)
}

// GetPromptConfigByID 根据ID获取Prompt配置（供Handler使用）
func (s *ConfigService) GetPromptConfigByID(id int) (*model.PromptConfig, error) {
	return s.promptConfigRepo.GetByID(id)
}
