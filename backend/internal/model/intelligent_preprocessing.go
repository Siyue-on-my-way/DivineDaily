package model

import "time"

// UserPattern represents analyzed user behavior patterns
type UserPattern struct {
	ID          int             `json:"id" db:"id"`
	UserID      string          `json:"user_id" db:"user_id"`
	PatternType string          `json:"pattern_type" db:"pattern_type"`
	PatternData map[string]any  `json:"pattern_data" db:"pattern_data"` // JSONB
	Frequency   int             `json:"frequency" db:"frequency"`
	Confidence  float64         `json:"confidence" db:"confidence"`
	CreatedAt   time.Time       `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time       `json:"updated_at" db:"updated_at"`
}

// QuestionQualityHistory represents the history of question analysis
type QuestionQualityHistory struct {
	ID               int                    `json:"id" db:"id"`
	SessionID        string                 `json:"session_id" db:"session_id"`
	OriginalQuestion string                 `json:"original_question" db:"original_question"`
	EnhancedQuestion string                 `json:"enhanced_question" db:"enhanced_question"`
	QualityScore     float64                `json:"quality_score" db:"quality_score"`
	QualityFactors   map[string]float64     `json:"quality_factors" db:"quality_factors"` // JSONB
	UserFeedback     int                    `json:"user_feedback" db:"user_feedback"`
	CreatedAt        time.Time              `json:"created_at" db:"created_at"`
}

// PreprocessRequest represents the request payload for preprocessing
type PreprocessRequest struct {
	UserID      string          `json:"user_id" binding:"required"`
	RawQuestion string          `json:"raw_question" binding:"required"`
	Context     QuestionContext `json:"context"`
}

// QuestionContext captures the context of the question
type QuestionContext struct {
	Timestamp        time.Time `json:"timestamp"`
	Location         string    `json:"location"`
	PreviousSessions []string  `json:"previous_sessions"`
}

// PreprocessResponse represents the result of preprocessing
type PreprocessResponse struct {
	OriginalQuestion    string                  `json:"original_question"`
	EnhancedQuestion    string                  `json:"enhanced_question"`
	UseEnhanced         bool                    `json:"use_enhanced"`
	QualityScore        float64                 `json:"quality_score"`
	QualityBreakdown    map[string]float64      `json:"quality_breakdown"`
	Suggestions         []EnhancementSuggestion `json:"suggestions"`
	RecommendedApproach string                  `json:"recommended_approach"`
	Intent              string                  `json:"intent"` // binary_choice, daily_luck, deep_analysis, knowledge
}

// Intent Types
const (
	IntentBinaryChoice = "binary_choice"
	IntentDailyLuck    = "daily_luck"
	IntentDeepAnalysis = "deep_analysis"
	IntentKnowledge    = "knowledge"
)

// EnhancementSuggestion represents a suggestion to improve the question
type EnhancementSuggestion struct {
	Type        string `json:"type"` // clarification, personalization, contextualization
	Message     string `json:"message"`
	AutoApplied bool   `json:"auto_applied"`
}

// QuestionQuality holds detailed quality metrics
type QuestionQuality struct {
	Score             float64
	Specificity       float64
	PersonalRelevance float64
	DecisionValue     float64
	TemporalRelevance float64
}
