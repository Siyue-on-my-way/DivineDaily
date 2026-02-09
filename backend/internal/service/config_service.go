package service

import (
	"context"
	"divine-daily-backend/internal/model"
	"divine-daily-backend/internal/repository"
	"fmt"
	"strings"
	"text/template"
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
	return s.llmConfigRepo.GetDefaultByScene(scene)
}

// ListLLMConfigs 获取所有LLM配置
func (s *ConfigService) ListLLMConfigs() ([]*model.LLMConfig, error) {
	return s.llmConfigRepo.ListAll()
}

// CreateLLMConfig 创建LLM配置
func (s *ConfigService) CreateLLMConfig(req *model.LLMConfigCreateRequest) (*model.LLMConfig, error) {
	// 设置默认值
	if req.Temperature == 0 {
		req.Temperature = 0.7
	}
	if req.MaxTokens == 0 {
		req.MaxTokens = 1000
	}
	if req.TimeoutSeconds == 0 {
		req.TimeoutSeconds = 30
	}
	if req.Scene == "" {
		req.Scene = "divination"
	}

	config := &model.LLMConfig{
		Name:           req.Name,
		Provider:       req.Provider,
		URLType:        req.URLType,
		APIKey:         req.APIKey,
		Endpoint:       req.Endpoint,
		ModelName:      req.ModelName,
		Temperature:    req.Temperature,
		MaxTokens:      req.MaxTokens,
		TimeoutSeconds: req.TimeoutSeconds,
		Scene:          req.Scene,
		IsDefault:      false,
		IsEnabled:      req.IsEnabled,
		Description:    req.Description,
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
	if req.Temperature != nil {
		config.Temperature = *req.Temperature
	}
	if req.MaxTokens != nil {
		config.MaxTokens = *req.MaxTokens
	}
	if req.TimeoutSeconds != nil {
		config.TimeoutSeconds = *req.TimeoutSeconds
	}
	if req.Scene != nil {
		config.Scene = *req.Scene
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

// TestLLMConfig 测试LLM配置
func (s *ConfigService) TestLLMConfig(id int) (string, error) {
	config, err := s.GetLLMConfigByID(id)
	if err != nil {
		return "", err
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
		return "", fmt.Errorf("暂不支持测试该提供商配置: %s", config.Provider)
	}

	if llmSvc == nil {
		return "", fmt.Errorf("创建LLM服务失败")
	}

	// 调用GenerateAnswer进行测试
	return llmSvc.GenerateAnswer(context.Background(), "Hello! This is a test connection. Please reply with 'Connection successful!'.")
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
		ID:             config.ID,
		Name:           config.Name,
		Provider:       config.Provider,
		URLType:        config.URLType,
		APIKey:         config.APIKey, // 返回真实API Key
		APIKeyMasked:   MaskAPIKey(config.APIKey),
		Endpoint:       config.Endpoint,
		ModelName:      config.ModelName,
		Temperature:    config.Temperature,
		MaxTokens:      config.MaxTokens,
		TimeoutSeconds: config.TimeoutSeconds,
		Scene:          config.Scene,
		IsDefault:      config.IsDefault,
		IsEnabled:      config.IsEnabled,
		Description:    config.Description,
		CreatedAt:      config.CreatedAt,
		UpdatedAt:      config.UpdatedAt,
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
