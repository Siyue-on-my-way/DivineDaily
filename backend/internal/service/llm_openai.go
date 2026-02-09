package service

import (
	"bytes"
	"context"
	"crypto/tls"
	"divine-daily-backend/internal/model"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// OpenAIService OpenAI服务实现
type OpenAIService struct {
	config     *model.LLMConfig
	httpClient *http.Client
}

// NewOpenAIService 创建OpenAI服务
func NewOpenAIService(config *model.LLMConfig) *OpenAIService {
	if config == nil {
		return nil
	}

	timeout := time.Duration(config.TimeoutSeconds) * time.Second
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	return &OpenAIService{
		config: config,
		httpClient: &http.Client{
			Timeout: timeout,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
	}

}

// OpenAI API请求结构
type openAIRequest struct {
	Model       string    `json:"model"`
	Messages    []message `json:"messages"`
	Temperature float64   `json:"temperature,omitempty"`
	MaxTokens   int       `json:"max_tokens,omitempty"`
}

type message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type openAIResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
	Error *struct {
		Message string `json:"message"`
		Type    string `json:"type"`
	} `json:"error"`
}

// GenerateAnswer 生成直接答案
func (s *OpenAIService) GenerateAnswer(ctx context.Context, prompt string) (string, error) {
	return s.callAPI(ctx, prompt)
}

// GenerateDetail 生成详细解读
func (s *OpenAIService) GenerateDetail(ctx context.Context, prompt string) (string, error) {
	return s.callAPI(ctx, prompt)
}

// GenerateRecommendation 生成推荐列表
func (s *OpenAIService) GenerateRecommendation(ctx context.Context, prompt string) ([]model.RecommendationItem, error) {
	response, err := s.callAPI(ctx, prompt)
	if err != nil {
		return nil, err
	}

	// 解析推荐列表（简单实现，实际应该让LLM返回JSON格式）
	// 这里先返回一个简单的解析，后续可以优化
	items := parseRecommendations(response)
	return items, nil
}

// StreamAnswer 流式生成答案
func (s *OpenAIService) StreamAnswer(ctx context.Context, prompt string) (<-chan string, error) {
	ch := make(chan string)

	go func() {
		defer close(ch)
		// 简化实现：先调用API获取完整结果，然后逐字符发送
		// 实际应该使用SSE流式API
		result, err := s.callAPI(ctx, prompt)
		if err != nil {
			return
		}

		for _, char := range result {
			select {
			case ch <- string(char):
				time.Sleep(10 * time.Millisecond) // 模拟流式输出
			case <-ctx.Done():
				return
			}
		}
	}()

	return ch, nil
}

// callAPI 调用OpenAI API
func (s *OpenAIService) callAPI(ctx context.Context, prompt string) (string, error) {
	endpoint := s.config.Endpoint
	if endpoint == "" {
		endpoint = "https://api.openai.com/v1/chat/completions"
	} else {
		// 根据URLType决定如何处理Endpoint
		if s.config.URLType == "custom" {
			// 自定义模式：直接使用用户提供的URL
			// 不做任何修改
		} else {
			// 默认/OpenAI兼容模式：智能追加 /chat/completions
			endpoint = strings.TrimSuffix(endpoint, "/")
			if !strings.HasSuffix(endpoint, "/chat/completions") {
				endpoint += "/chat/completions"
			}
		}
	}

	reqBody := openAIRequest{
		Model: s.config.ModelName,
		Messages: []message{
			{
				Role:    "user",
				Content: prompt,
			},
		},
		Temperature: s.config.Temperature,
		MaxTokens:   s.config.MaxTokens,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("序列化请求失败: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	if s.config.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+s.config.APIKey)
	}

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("API调用失败: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("读取响应失败: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API返回错误: %d, %s", resp.StatusCode, string(body))
	}

	var apiResp openAIResponse
	if err := json.Unmarshal(body, &apiResp); err != nil {
		return "", fmt.Errorf("解析响应失败: %w", err)
	}

	if apiResp.Error != nil {
		return "", fmt.Errorf("API错误: %s", apiResp.Error.Message)
	}

	if len(apiResp.Choices) == 0 {
		return "", fmt.Errorf("API返回空结果")
	}

	return apiResp.Choices[0].Message.Content, nil
}

// parseRecommendations 解析推荐列表（简单实现）
func parseRecommendations(text string) []model.RecommendationItem {
	// 简单解析：查找"推荐："或"1."开头的行
	// 实际应该让LLM返回JSON格式，这里先做简单解析
	items := []model.RecommendationItem{}

	// 按行分割
	lines := strings.Split(text, "\n")
	currentItem := model.RecommendationItem{}
	inItem := false

	for i := 0; i < len(lines); i++ {
		line := strings.TrimSpace(lines[i])
		if line == "" {
			continue
		}

		// 简单实现：查找数字开头的行作为推荐项
		// 修复：正确处理UTF-8字符 '、'
		isDigit := len(line) > 0 && line[0] >= '1' && line[0] <= '9'
		var content string
		matched := false

		if isDigit {
			if strings.HasPrefix(line[1:], ".") {
				content = strings.TrimSpace(line[2:])
				matched = true
			} else if strings.HasPrefix(line[1:], "、") {
				content = strings.TrimSpace(line[1+len("、"):])
				matched = true
			}
		}

		if matched {
			if inItem && currentItem.Content != "" {
				items = append(items, currentItem)
			}
			currentItem = model.RecommendationItem{}
			inItem = true
			currentItem.Content = content
		} else if inItem {
			// 假设后续行是原因或其他描述
			if currentItem.Reason == "" {
				currentItem.Reason = line
			} else {
				currentItem.Reason += " " + line
			}
		}
	}

	if inItem && currentItem.Content != "" {
		items = append(items, currentItem)
	}

	// 如果没解析出来，尝试整体作为一个
	if len(items) == 0 && text != "" {
		items = append(items, model.RecommendationItem{
			Content: text,
			Reason:  "智能推荐",
		})
	}

	return items
}
