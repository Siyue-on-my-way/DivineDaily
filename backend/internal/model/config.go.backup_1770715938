package model

import (
	"time"
)

// LLMConfig LLM模型配置
type LLMConfig struct {
	ID             int       `json:"id" db:"id"`
	Name           string    `json:"name" db:"name"`
	Provider       string    `json:"provider" db:"provider"`           // openai/anthropic/local
	URLType        string    `json:"url_type,omitempty" db:"url_type"` // openai_compatible/custom
	APIKey         string    `json:"api_key,omitempty" db:"api_key"`
	Endpoint       string    `json:"endpoint,omitempty" db:"endpoint"`
	ModelName      string    `json:"model_name" db:"model_name"`
	Temperature    float64   `json:"temperature" db:"temperature"`
	MaxTokens      int       `json:"max_tokens" db:"max_tokens"`
	TimeoutSeconds int       `json:"timeout_seconds" db:"timeout_seconds"`
	Scene          string    `json:"scene" db:"scene"` // divination（占卜）/tarot（塔罗牌）
	IsDefault      bool      `json:"is_default" db:"is_default"`
	IsEnabled      bool      `json:"is_enabled" db:"is_enabled"`
	Description    string    `json:"description,omitempty" db:"description"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time `json:"updated_at" db:"updated_at"`
}

// LLMConfigCreateRequest 创建LLM配置请求
type LLMConfigCreateRequest struct {
	Name           string  `json:"name" binding:"required"`
	Provider       string  `json:"provider" binding:"required"`
	URLType        string  `json:"url_type,omitempty"`
	APIKey         string  `json:"api_key,omitempty"`
	Endpoint       string  `json:"endpoint,omitempty"`
	ModelName      string  `json:"model_name" binding:"required"`
	Temperature    float64 `json:"temperature"`
	MaxTokens      int     `json:"max_tokens"`
	TimeoutSeconds int     `json:"timeout_seconds"`
	Scene          string  `json:"scene"` // divination（占卜）/tarot（塔罗牌），默认divination
	IsEnabled      bool    `json:"is_enabled"`
	Description    string  `json:"description,omitempty"`
}

// LLMConfigUpdateRequest 更新LLM配置请求
type LLMConfigUpdateRequest struct {
	Name           *string  `json:"name,omitempty"`
	Provider       *string  `json:"provider,omitempty"`
	URLType        *string  `json:"url_type,omitempty"`
	APIKey         *string  `json:"api_key,omitempty"` // 如果为空字符串，表示不更新
	Endpoint       *string  `json:"endpoint,omitempty"`
	ModelName      *string  `json:"model_name,omitempty"`
	Temperature    *float64 `json:"temperature,omitempty"`
	MaxTokens      *int     `json:"max_tokens,omitempty"`
	TimeoutSeconds *int     `json:"timeout_seconds,omitempty"`
	Scene          *string  `json:"scene,omitempty"` // divination（占卜）/tarot（塔罗牌）
	IsEnabled      *bool    `json:"is_enabled,omitempty"`
	Description    *string  `json:"description,omitempty"`
}

// LLMConfigResponse LLM配置响应（API Key脱敏）
type LLMConfigResponse struct {
	ID             int       `json:"id"`
	Name           string    `json:"name"`
	Provider       string    `json:"provider"`
	URLType        string    `json:"url_type,omitempty"`
	APIKey         string    `json:"api_key,omitempty"`        // 真实API Key (用于回填)
	APIKeyMasked   string    `json:"api_key_masked,omitempty"` // 脱敏后的API Key
	Endpoint       string    `json:"endpoint,omitempty"`
	ModelName      string    `json:"model_name"`
	Temperature    float64   `json:"temperature"`
	MaxTokens      int       `json:"max_tokens"`
	TimeoutSeconds int       `json:"timeout_seconds"`
	Scene          string    `json:"scene"` // divination（占卜）/tarot（塔罗牌）
	IsDefault      bool      `json:"is_default"`
	IsEnabled      bool      `json:"is_enabled"`
	Description    string    `json:"description,omitempty"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
}

// PromptVariable Prompt变量说明
type PromptVariable struct {
	Name        string `json:"name"`
	Type        string `json:"type"` // string/int/float/bool
	Description string `json:"description"`
	Required    bool   `json:"required"`
}

// PromptConfig Prompt配置
type PromptConfig struct {
	ID           int              `json:"id" db:"id"`
	Name         string           `json:"name" db:"name"`
	PromptType   string           `json:"prompt_type" db:"prompt_type"`     // answer/detail/recommendation
	QuestionType string           `json:"question_type" db:"question_type"` // decision/recommendation
	Template     string           `json:"template" db:"template"`
	Variables    []PromptVariable `json:"variables,omitempty" db:"variables"`
	IsDefault    bool             `json:"is_default" db:"is_default"`
	IsEnabled    bool             `json:"is_enabled" db:"is_enabled"`
	Description  string           `json:"description,omitempty" db:"description"`
	CreatedAt    time.Time        `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time        `json:"updated_at" db:"updated_at"`
}

// PromptConfigCreateRequest 创建Prompt配置请求
type PromptConfigCreateRequest struct {
	Name         string           `json:"name" binding:"required"`
	PromptType   string           `json:"prompt_type" binding:"required"`
	QuestionType string           `json:"question_type" binding:"required"`
	Template     string           `json:"template" binding:"required"`
	Variables    []PromptVariable `json:"variables,omitempty"`
	IsEnabled    bool             `json:"is_enabled"`
	Description  string           `json:"description,omitempty"`
}

// PromptConfigUpdateRequest 更新Prompt配置请求
type PromptConfigUpdateRequest struct {
	Name         *string          `json:"name,omitempty"`
	PromptType   *string          `json:"prompt_type,omitempty"`
	QuestionType *string          `json:"question_type,omitempty"`
	Template     *string          `json:"template,omitempty"`
	Variables    []PromptVariable `json:"variables,omitempty"`
	IsEnabled    *bool            `json:"is_enabled,omitempty"`
	Description  *string          `json:"description,omitempty"`
}

// PromptRenderRequest Prompt渲染请求
type PromptRenderRequest struct {
	Template  string                 `json:"template" binding:"required"`
	Variables map[string]interface{} `json:"variables" binding:"required"`
}

// PromptRenderResponse Prompt渲染响应
type PromptRenderResponse struct {
	Rendered string `json:"rendered"`
}
