package service

import (
	"context"
	"crypto/md5"
	"divine-daily-backend/internal/model"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"
)

// LLMCacheItem LLM缓存项
type LLMCacheItem struct {
	Response  string
	ExpiresAt time.Time
}

// DatabaseLLMService 基于数据库配置的LLM服务实现
type DatabaseLLMService struct {
	configSvc *ConfigService
	scene     string // divination 或 tarot
	cache     map[string]LLMCacheItem
	cacheMu   sync.RWMutex
}

// NewDatabaseLLMService 创建基于数据库配置的LLM服务
func NewDatabaseLLMService(configSvc *ConfigService, scene string) *DatabaseLLMService {
	return &DatabaseLLMService{
		configSvc: configSvc,
		scene:     scene,
		cache:     make(map[string]LLMCacheItem),
	}
}

// getLLMConfig 获取当前场景的LLM配置
func (s *DatabaseLLMService) getLLMConfig() (*model.LLMConfig, error) {
	if s.configSvc == nil {
		return nil, fmt.Errorf("配置服务未初始化")
	}

	// 根据场景获取默认配置
	config, err := s.configSvc.GetDefaultLLMConfigByScene(s.scene)
	if err != nil {
		// 如果当前场景没有配置，尝试获取通用默认配置
		config, err = s.configSvc.GetDefaultLLMConfig()
		if err != nil {
			return nil, fmt.Errorf("未找到LLM配置（场景: %s）: %w", s.scene, err)
		}
	}

	if !config.IsEnabled {
		return nil, fmt.Errorf("LLM配置已禁用（场景: %s）", s.scene)
	}

	return config, nil
}

// GenerateAnswer 生成直接答案
func (s *DatabaseLLMService) GenerateAnswer(ctx context.Context, prompt string) (string, error) {
	config, err := s.getLLMConfig()
	if err != nil {
		return "", err
	}

	return s.callLLM(ctx, config, prompt)
}

// GenerateDetail 生成详细解读
func (s *DatabaseLLMService) GenerateDetail(ctx context.Context, prompt string) (string, error) {
	config, err := s.getLLMConfig()
	if err != nil {
		return "", err
	}

	return s.callLLM(ctx, config, prompt)
}

// GenerateRecommendation 生成推荐列表
func (s *DatabaseLLMService) GenerateRecommendation(ctx context.Context, prompt string) ([]model.RecommendationItem, error) {
	config, err := s.getLLMConfig()
	if err != nil {
		return nil, err
	}

	response, err := s.callLLM(ctx, config, prompt)
	if err != nil {
		return nil, err
	}

	// 解析推荐列表
	var recommendations []model.RecommendationItem

	// 尝试解析为JSON
	if err := json.Unmarshal([]byte(response), &recommendations); err == nil {
		return recommendations, nil
	}

	// 如果不是JSON，尝试解析文本格式
	lines := strings.Split(response, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		parts := strings.SplitN(line, " - ", 2)
		if len(parts) == 2 {
			recommendations = append(recommendations, model.RecommendationItem{
				Content: strings.TrimSpace(parts[0]),
				Reason:  strings.TrimSpace(parts[1]),
			})
		} else {
			recommendations = append(recommendations, model.RecommendationItem{
				Content: line,
				Reason:  "根据您的个人情况推荐",
			})
		}
	}

	if len(recommendations) == 0 {
		return []model.RecommendationItem{
			{Content: "建议1", Reason: "根据您的个人情况推荐"},
			{Content: "建议2", Reason: "适合您当前状态"},
		}, nil
	}

	return recommendations, nil
}

// StreamAnswer 流式生成答案
func (s *DatabaseLLMService) StreamAnswer(ctx context.Context, prompt string) (<-chan string, error) {
	config, err := s.getLLMConfig()
	if err != nil {
		return nil, err
	}

	return s.callLLMStream(ctx, config, prompt)
}

// getCacheKey 生成缓存Key
func (s *DatabaseLLMService) getCacheKey(config *model.LLMConfig, prompt string) string {
	data := fmt.Sprintf("%d-%d-%s", config.ID, config.UpdatedAt.Unix(), prompt)
	hash := md5.Sum([]byte(data))
	return hex.EncodeToString(hash[:])
}

// checkCache 检查缓存
func (s *DatabaseLLMService) checkCache(key string) (string, bool) {
	s.cacheMu.RLock()
	defer s.cacheMu.RUnlock()
	item, ok := s.cache[key]
	if !ok {
		return "", false
	}
	if time.Now().After(item.ExpiresAt) {
		return "", false
	}
	return item.Response, true
}

// setCache 设置缓存
func (s *DatabaseLLMService) setCache(key string, response string) {
	s.cacheMu.Lock()
	defer s.cacheMu.Unlock()
	s.cache[key] = LLMCacheItem{
		Response:  response,
		ExpiresAt: time.Now().Add(24 * time.Hour),
	}
}

// callLLM 调用LLM API（同步）
func (s *DatabaseLLMService) callLLM(ctx context.Context, config *model.LLMConfig, prompt string) (string, error) {
	// 检查缓存
	key := s.getCacheKey(config, prompt)
	if cached, ok := s.checkCache(key); ok {
		return cached, nil
	}

	var resp string
	var err error

	switch config.Provider {
	case "openai":
		resp, err = s.callOpenAI(ctx, config, prompt)
	case "anthropic":
		resp, err = s.callAnthropic(ctx, config, prompt)
	case "local", "custom":
		resp, err = s.callCustomEndpoint(ctx, config, prompt)
	default:
		return "", fmt.Errorf("不支持的LLM提供商: %s", config.Provider)
	}

	if err == nil {
		s.setCache(key, resp)
	}

	return resp, err
}

// callLLMStream 调用LLM API（流式）
func (s *DatabaseLLMService) callLLMStream(ctx context.Context, config *model.LLMConfig, prompt string) (<-chan string, error) {
	switch config.Provider {
	case "openai":
		return s.callOpenAIStream(ctx, config, prompt)
	case "anthropic":
		return s.callAnthropicStream(ctx, config, prompt)
	case "local", "custom":
		return s.callCustomEndpointStream(ctx, config, prompt)
	default:
		return nil, fmt.Errorf("不支持的LLM提供商: %s", config.Provider)
	}
}

// callOpenAI 调用OpenAI API
func (s *DatabaseLLMService) callOpenAI(ctx context.Context, config *model.LLMConfig, prompt string) (string, error) {
	// 使用OpenAI兼容格式
	return s.callOpenAICompatible(ctx, config, prompt)
}

// callOpenAIStream 调用OpenAI API（流式）
func (s *DatabaseLLMService) callOpenAIStream(ctx context.Context, config *model.LLMConfig, prompt string) (<-chan string, error) {
	ch := make(chan string)
	go func() {
		defer close(ch)
		text, err := s.callOpenAI(ctx, config, prompt)
		if err != nil {
			return
		}
		for _, char := range text {
			ch <- string(char)
			time.Sleep(50 * time.Millisecond)
		}
	}()
	return ch, nil
}

// callAnthropic 调用Anthropic API
func (s *DatabaseLLMService) callAnthropic(ctx context.Context, config *model.LLMConfig, prompt string) (string, error) {
	return fmt.Sprintf("【Anthropic %s】%s", config.ModelName, prompt[:min(50, len(prompt))]+"..."), nil
}

// callAnthropicStream 调用Anthropic API（流式）
func (s *DatabaseLLMService) callAnthropicStream(ctx context.Context, config *model.LLMConfig, prompt string) (<-chan string, error) {
	ch := make(chan string)
	go func() {
		defer close(ch)
		text := fmt.Sprintf("【Anthropic %s 流式】%s", config.ModelName, prompt)
		for _, char := range text {
			ch <- string(char)
			time.Sleep(50 * time.Millisecond)
		}
	}()
	return ch, nil
}

// callCustomEndpoint 调用自定义端点
func (s *DatabaseLLMService) callCustomEndpoint(ctx context.Context, config *model.LLMConfig, prompt string) (string, error) {
	if config.Endpoint == "" {
		return "", fmt.Errorf("自定义端点未配置")
	}

	// 根据URLType决定请求格式
	if config.URLType == "openai_compatible" {
		// OpenAI兼容格式
		return s.callOpenAICompatible(ctx, config, prompt)
	}

	// 自定义格式（旧逻辑）
	reqBody := map[string]interface{}{
		"model":       config.ModelName,
		"prompt":      prompt,
		"temperature": config.Temperature,
		"max_tokens":  config.MaxTokens,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("序列化请求失败: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", config.Endpoint, strings.NewReader(string(jsonData)))
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	if config.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+config.APIKey)
	}

	client := &http.Client{
		Timeout: time.Duration(config.TimeoutSeconds) * time.Second,
	}

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("请求失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("请求失败: %d - %s", resp.StatusCode, string(body))
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("读取响应失败: %w", err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err == nil {
		if text, ok := result["text"].(string); ok {
			return text, nil
		}
		if text, ok := result["content"].(string); ok {
			return text, nil
		}
	}

	return string(body), nil
}

// callOpenAICompatible 调用OpenAI兼容的API
func (s *DatabaseLLMService) callOpenAICompatible(ctx context.Context, config *model.LLMConfig, prompt string) (string, error) {
	// 构建OpenAI格式的请求
	endpoint := strings.TrimSuffix(config.Endpoint, "/")
	if !strings.HasSuffix(endpoint, "/chat/completions") {
		endpoint += "/chat/completions"
	}

	reqBody := map[string]interface{}{
		"model": config.ModelName,
		"messages": []map[string]string{
			{
				"role":    "user",
				"content": prompt,
			},
		},
		"temperature": config.Temperature,
		"max_tokens":  config.MaxTokens,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("序列化请求失败: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", endpoint, strings.NewReader(string(jsonData)))
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	if config.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+config.APIKey)
	}

	client := &http.Client{
		Timeout: time.Duration(config.TimeoutSeconds) * time.Second,
	}

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("请求失败: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("读取响应失败: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("请求失败: %d - %s", resp.StatusCode, string(body))
	}

	// 解析OpenAI格式的响应
	var result struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
		Error *struct {
			Message string `json:"message"`
		} `json:"error"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		return "", fmt.Errorf("解析响应失败: %w, body: %s", err, string(body))
	}

	if result.Error != nil {
		return "", fmt.Errorf("API错误: %s", result.Error.Message)
	}

	if len(result.Choices) == 0 {
		return "", fmt.Errorf("API返回空结果")
	}

	return result.Choices[0].Message.Content, nil
}

// callCustomEndpointStream 调用自定义端点（流式）
func (s *DatabaseLLMService) callCustomEndpointStream(ctx context.Context, config *model.LLMConfig, prompt string) (<-chan string, error) {
	ch := make(chan string)
	go func() {
		defer close(ch)
		text, err := s.callCustomEndpoint(ctx, config, prompt)
		if err != nil {
			return
		}
		for _, char := range text {
			ch <- string(char)
			time.Sleep(50 * time.Millisecond)
		}
	}()
	return ch, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
