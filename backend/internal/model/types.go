package model

import "time"

// ... existing structs ...

// SceneAdviceItem represents a single piece of actionable advice
type SceneAdviceItem struct {
	Title   string `json:"title"`
	Content string `json:"content"`
	Type    string `json:"type"` // "food", "action", "mindset"
}

// FollowUpQuestion represents a question from the system to the user
type FollowUpQuestion struct {
	ID        string   `json:"id"`
	SessionID string   `json:"session_id"`
	Question  string   `json:"question"`
	Options   []string `json:"options,omitempty"` // Optional predefined answers
}

// FollowUpAnswer represents the user's answer to a follow-up question
type FollowUpAnswer struct {
	SessionID  string `json:"session_id" binding:"required"`
	QuestionID string `json:"question_id" binding:"required"`
	Answer     string `json:"answer" binding:"required"`
}

type OrientationRecommendRequest struct {
	Version   string `json:"version" binding:"required,oneof=CN Global TAROT"`
	EventType string `json:"event_type" binding:"required"`
	Question  string `json:"question"`
	UserID    string `json:"user_id,omitempty"`
}

type OrientationOption struct {
	Key   string `json:"key"`
	Label string `json:"label"`
}

type OrientationRecommendResponse struct {
	RecommendedKey   string              `json:"recommended_key"`
	RecommendedLabel string              `json:"recommended_label"`
	Reason           string              `json:"reason"`
	Options          []OrientationOption `json:"options"`
	ToleranceDeg     int                 `json:"tolerance_deg"`
}

type TarotCardDraw struct {
	Name       string `json:"name"`
	NameEN     string `json:"name_en,omitempty"`
	Position   string `json:"position"`
	IsReversed bool   `json:"is_reversed"`
}

// DivinationResult updated to include structured scene advice and follow-up status
type DivinationResult struct {
	SessionID string          `json:"session_id"`
	Outcome   string          `json:"outcome,omitempty"` // 吉/凶/平（决策类）
	Title     string          `json:"title,omitempty"`
	Spread    string          `json:"spread,omitempty"`
	Cards     []TarotCardDraw `json:"cards,omitempty"`

	// 问题分析结果（新增）
	QuestionType   string `json:"question_type,omitempty"`   // decision, relationship, career, fortune, knowledge
	QuestionIntent string `json:"question_intent,omitempty"` // binary_choice, yes_no, timing, understanding, guidance

	// 结果卡内容（默认显示）
	Summary string `json:"summary"` // 直接答案/推荐列表（50-100字）

	// 详情内容（点击展开）
	Detail string `json:"detail"` // 算卦过程/推荐逻辑

	// 结构化数据（详情中使用）
	HexagramInfo    *HexagramInfo        `json:"hexagram_info,omitempty"`   // 卦象信息（决策类）
	Recommendations []RecommendationItem `json:"recommendations,omitempty"` // 推荐列表（推荐类）
	DailyFortune    *DailyFortune        `json:"daily_fortune,omitempty"`   // 每日运势（运势类）

	RawData       string            `json:"raw_data,omitempty"`
	SceneAdvice   []SceneAdviceItem `json:"scene_advice,omitempty"` // Changed from string to struct slice
	NeedsFollowUp bool              `json:"needs_follow_up"`        // Flag to trigger frontend follow-up UI
	FollowUpQ     *FollowUpQuestion `json:"follow_up_question,omitempty"`
	CreatedAt     time.Time         `json:"created_at"`
}

// HexagramInfo 卦象信息（用于详情展示）
type HexagramInfo struct {
	Number        int    `json:"number"`                   // 卦序号（1-64）
	Name          string `json:"name"`                     // 卦名
	UpperTrigram  string `json:"upper_trigram"`            // 上卦
	LowerTrigram  string `json:"lower_trigram"`            // 下卦
	Outcome       string `json:"outcome"`                  // 吉/凶/平
	Summary       string `json:"summary"`                  // 卦辞摘要
	Wuxing        string `json:"wuxing"`                   // 五行
	ChangingLines []int  `json:"changing_lines,omitempty"` // 变爻位置
}

// RecommendationItem 推荐项（用于结果卡展示）
type RecommendationItem struct {
	Content string `json:"content"` // 推荐内容
	Reason  string `json:"reason"`  // 推荐理由
}

// User represents a user of the application
type User struct {
	ID        string    `json:"id"`
	Username  string    `json:"username"`
	CreatedAt time.Time `json:"created_at"`
}

// UserProfile stores user's personal and metaphysical data
type UserProfile struct {
	UserID string `json:"user_id"`

	// 基础信息
	Nickname string `json:"nickname"`
	Gender   string `json:"gender"` // "male", "female", "other"

	// 公历出生信息（用户输入）
	BirthDate string `json:"birth_date"`           // YYYY-MM-DD
	BirthTime string `json:"birth_time,omitempty"` // HH:mm

	// 农历出生信息（系统自动转换）
	LunarYear    int    `json:"lunar_year,omitempty"`
	LunarMonth   int    `json:"lunar_month,omitempty"`
	LunarDay     int    `json:"lunar_day,omitempty"`
	IsLeapMonth  bool   `json:"is_leap_month,omitempty"`
	LunarMonthCn string `json:"lunar_month_cn,omitempty"` // 如"九月"、"闰九月"
	LunarDayCn   string `json:"lunar_day_cn,omitempty"`   // 如"初十"、"廿一"

	// 天干地支
	GanZhiYear  string `json:"ganzhi_year,omitempty"`  // 如"丁卯"
	GanZhiMonth string `json:"ganzhi_month,omitempty"` // 如"庚戌"
	GanZhiDay   string `json:"ganzhi_day,omitempty"`   // 如"甲寅"

	// 其他信息
	Animal string `json:"animal,omitempty"`  // 生肖，如"兔"
	Term   string `json:"term,omitempty"`    // 节气，如"立春"（如果有）
	IsTerm bool   `json:"is_term,omitempty"` // 是否是节气

	// 其他档案信息
	ZodiacSign     string `json:"zodiac_sign,omitempty"`
	IsMenstruating bool   `json:"is_menstruating,omitempty"`
	RecentExercise string `json:"recent_exercise,omitempty"` // "none", "light", "heavy"

	// 时间戳
	CreatedAt string `json:"created_at,omitempty"`
	UpdatedAt string `json:"updated_at,omitempty"`
}

// CreateUserProfileRequest 创建用户档案请求
type CreateUserProfileRequest struct {
	UserID         string `json:"user_id" binding:"required"`
	Nickname       string `json:"nickname"`
	Gender         string `json:"gender"`               // "male", "female", "other"
	BirthDate      string `json:"birth_date"`           // YYYY-MM-DD
	BirthTime      string `json:"birth_time,omitempty"` // HH:mm
	ZodiacSign     string `json:"zodiac_sign,omitempty"`
	IsMenstruating bool   `json:"is_menstruating,omitempty"`
	RecentExercise string `json:"recent_exercise,omitempty"` // "none", "light", "heavy"
}

// UpdateUserProfileRequest 更新用户档案请求
type UpdateUserProfileRequest struct {
	Nickname       *string `json:"nickname,omitempty"`
	Gender         *string `json:"gender,omitempty"`     // "male", "female", "other"
	BirthDate      *string `json:"birth_date,omitempty"` // YYYY-MM-DD
	BirthTime      *string `json:"birth_time,omitempty"` // HH:mm
	ZodiacSign     *string `json:"zodiac_sign,omitempty"`
	IsMenstruating *bool   `json:"is_menstruating,omitempty"`
	RecentExercise *string `json:"recent_exercise,omitempty"` // "none", "light", "heavy"
}

// DivinationSession represents a single divination request
type DivinationSession struct {
	ID              string           `json:"id"`
	UserID          string           `json:"user_id"`
	Version         string           `json:"version"` // "CN", "Global", or "TAROT"
	Question        string           `json:"question"`
	EventType       string           `json:"event_type"`            // "decision", "relationship", etc.
	Orientation     string           `json:"orientation,omitempty"` // "East", "North", etc.
	Spread          string           `json:"spread,omitempty"`
	Intent          string           `json:"intent,omitempty"`
	CreatedAt       time.Time        `json:"created_at"`
	UpdatedAt       time.Time        `json:"updated_at"`
	Status          string           `json:"status"`          // "created", "processing", "completed", "failed"
	FollowUpCount   int              `json:"follow_up_count"` // Track number of follow-ups
	FollowUpAnswers []FollowUpAnswer `json:"-"`
}

// CreateDivinationRequest is the input payload for starting a divination
type CreateDivinationRequest struct {
	UserID      string                 `json:"user_id"` // For MVP, we might trust client or use mock token
	Question    string                 `json:"question" binding:"required"`
	EventType   string                 `json:"event_type"` // 改为可选，不再强制要求
	Version     string                 `json:"version" binding:"required,oneof=CN Global TAROT"`
	Orientation string                 `json:"orientation"`
	Spread      string                 `json:"spread,omitempty"`
	Intent      string                 `json:"intent,omitempty"` // Added for intelligent intent handling
	Context     map[string]interface{} `json:"context,omitempty"`
}
