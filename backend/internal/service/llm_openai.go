package service

import (
	"bufio"
	"bytes"
	"context"
	"crypto/tls"
	"divine-daily-backend/internal/model"
	"encoding/json"
	"fmt"
	"io"
	"log"
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

	return &OpenAIService{
		config: config,
		httpClient: &http.Client{
			Timeout: 60 * time.Second,
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
	Stream      bool      `json:"stream,omitempty"`
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

	items := parseRecommendations(response)
	return items, nil
}

// StreamAnswer 流式生成答案
func (s *OpenAIService) StreamAnswer(ctx context.Context, prompt string) (<-chan string, error) {
	ch := make(chan string)

	go func() {
		defer close(ch)
		result, err := s.callAPI(ctx, prompt)
		if err != nil {
			return
		}

		for _, char := range result {
			select {
			case ch <- string(char):
				time.Sleep(10 * time.Millisecond)
			case <-ctx.Done():
				return
			}
		}
	}()

	return ch, nil
}

// GenerateAnswerStream 流式生成答案（真正的SSE流式）
func (s *OpenAIService) GenerateAnswerStream(ctx context.Context, prompt string, streamChan chan<- string) error {
	endpoint := s.config.Endpoint
	if endpoint == "" {
		endpoint = "https://api.openai.com/v1/chat/completions"
	} else {
		endpoint = strings.TrimSuffix(endpoint, "/")
		if !strings.HasSuffix(endpoint, "/chat/completions") {
			endpoint += "/chat/completions"
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
		Temperature: 0.7,
		MaxTokens:   2000,
		Stream:      true,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return fmt.Errorf("序列化请求失败: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "text/event-stream")
	if s.config.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+s.config.APIKey)
	}

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("API调用失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API返回错误: %d, %s", resp.StatusCode, string(body))
	}

	// 使用 bufio.Scanner 逐行读取 SSE 流
	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		line := scanner.Text()
		line = strings.TrimSpace(line)

		if !strings.HasPrefix(line, "data: ") {
			continue
		}

		content := strings.TrimPrefix(line, "data: ")
		if content == "[DONE]" {
			return nil
		}

		// 解析JSON
		var streamResp struct {
			Choices []struct {
				Delta struct {
					Content string `json:"content"`
				} `json:"delta"`
			} `json:"choices"`
		}

		if err := json.Unmarshal([]byte(content), &streamResp); err != nil {
			continue
		}

		if len(streamResp.Choices) > 0 && streamResp.Choices[0].Delta.Content != "" {
			select {
			case streamChan <- streamResp.Choices[0].Delta.Content:
			case <-ctx.Done():
				return ctx.Err()
			}
		}
	}

	if err := scanner.Err(); err != nil {
		return fmt.Errorf("读取流失败: %w", err)
	}

	return nil
}

// callAPI 调用OpenAI API
func (s *OpenAIService) callAPI(ctx context.Context, prompt string) (string, error) {
	endpoint := s.config.Endpoint
	if endpoint == "" {
		endpoint = "https://api.openai.com/v1/chat/completions"
	} else {
		endpoint = strings.TrimSuffix(endpoint, "/")
		if s.config.URLType == "custom" {
			// 自定义模式：直接使用用户提供的URL
		} else {
			// OpenAI兼容模式：智能追加 /chat/completions
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
		Temperature: 0.7,
		MaxTokens:   2000,
		Stream:      false,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("序列化请求失败: %w", err)
	}

	log.Printf("[LLM Test] 请求端点: %s", endpoint)
	log.Printf("[LLM Test] 请求体: %s", string(jsonData))

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

	log.Printf("[LLM Test] 响应状态码: %d", resp.StatusCode)
	log.Printf("[LLM Test] 响应体: %s", string(body))

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API返回错误: %d, %s", resp.StatusCode, string(body))
	}

	var apiResp openAIResponse
	if err := json.Unmarshal(body, &apiResp); err != nil {
		return "", fmt.Errorf("解析响应失败: %w, 原始响应: %s", err, string(body))
	}

	if apiResp.Error != nil {
		return "", fmt.Errorf("API错误: %s", apiResp.Error.Message)
	}

	if len(apiResp.Choices) == 0 {
		// 返回更详细的错误信息，包含原始响应
		return "", fmt.Errorf("API返回空结果，原始响应: %s", string(body))
	}

	content := apiResp.Choices[0].Message.Content
	log.Printf("[LLM Test] 提取的内容: %s", content)

	return content, nil
}

// parseRecommendations 解析推荐列表
func parseRecommendations(text string) []model.RecommendationItem {
	items := []model.RecommendationItem{}
	lines := strings.Split(text, "\n")
	currentItem := model.RecommendationItem{}
	inItem := false

	for i := 0; i < len(lines); i++ {
		line := strings.TrimSpace(lines[i])
		if line == "" {
			continue
		}

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

	if len(items) == 0 && text != "" {
		items = append(items, model.RecommendationItem{
			Content: text,
			Reason:  "智能推荐",
		})
	}

	return items
}
