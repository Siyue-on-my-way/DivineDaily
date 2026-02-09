package service

import (
	"context"
	"divine-daily-backend/internal/model"
)

// LLMService defines the interface for Large Language Model interactions
type LLMService interface {
	// GenerateAnswer generates a direct answer for result card (50-100字)
	GenerateAnswer(ctx context.Context, prompt string) (string, error)
	
	// GenerateDetail generates detailed interpretation for detail view
	GenerateDetail(ctx context.Context, prompt string) (string, error)
	
	// GenerateRecommendation generates recommendation list for result card
	GenerateRecommendation(ctx context.Context, prompt string) ([]model.RecommendationItem, error)
	
	// StreamAnswer provides a streaming response for result card
	StreamAnswer(ctx context.Context, prompt string) (<-chan string, error)
}

// MockLLMService is a mock implementation for testing/MVP
type MockLLMService struct{}

func NewMockLLMService() *MockLLMService {
	return &MockLLMService{}
}

func (s *MockLLMService) GenerateAnswer(ctx context.Context, prompt string) (string, error) {
	// In a real scenario, this would call OpenAI/Anthropic/Local LLM
	// For now, return a mock direct answer
	return "根据您的生辰八字和本次卦象分析，建议您选择工作A。理由：工作A更符合您的五行属性，有利于事业发展，且与您的生肖相合，建议优先考虑。", nil
}

func (s *MockLLMService) GenerateDetail(ctx context.Context, prompt string) (string, error) {
	// In a real scenario, this would call OpenAI/Anthropic/Local LLM
	return "这是详细的解卦分析，包含卦象解读、算卦过程和完整分析...", nil
}

func (s *MockLLMService) GenerateRecommendation(ctx context.Context, prompt string) ([]model.RecommendationItem, error) {
	// In a real scenario, this would call OpenAI/Anthropic/Local LLM
	return []model.RecommendationItem{
		{Content: "热汤面", Reason: "结合您当前状态，温热食物有助于缓解不适"},
		{Content: "蒸蛋羹", Reason: "易于消化，营养丰富"},
		{Content: "小米粥", Reason: "温和养胃，适合当前身体状况"},
	}, nil
}

func (s *MockLLMService) StreamAnswer(ctx context.Context, prompt string) (<-chan string, error) {
	ch := make(chan string)
	go func() {
		defer close(ch)
		text := "根据您的生辰八字和本次卦象分析，建议您选择工作A。"
		for _, char := range text {
			ch <- string(char)
			// Simulate streaming delay
		}
	}()
	return ch, nil
}
