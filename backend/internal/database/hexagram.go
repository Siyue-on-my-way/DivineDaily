package database

import (
	"database/sql"
	"fmt"
	"os"

	_ "github.com/lib/pq"
)

var (
	dbInstance *sql.DB
)

// DBConfig 数据库配置
type DBConfig struct {
	Host     string
	Port     string
	User     string
	Password string
	Database string
	SSLMode  string
}

// GetDBConfigFromEnv 从环境变量获取数据库配置
func GetDBConfigFromEnv() DBConfig {
	return DBConfig{
		Host:     getEnv("DB_HOST", "localhost"),
		Port:     getEnv("DB_PORT", "5432"),
		User:     getEnv("DB_USER", "divinedaily"),
		Password: getEnv("DB_PASSWORD", "divinedaily123"),
		Database: getEnv("DB_NAME", "divinedaily"),
		SSLMode:  getEnv("DB_SSLMODE", "disable"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// BuildDSN 构建PostgreSQL连接字符串
func (c DBConfig) BuildDSN() string {
	return fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		c.Host, c.Port, c.User, c.Password, c.Database, c.SSLMode,
	)
}

// InitDB 初始化数据库连接（PostgreSQL）
func InitDB(config ...DBConfig) error {
	var cfg DBConfig
	if len(config) > 0 {
		cfg = config[0]
	} else {
		cfg = GetDBConfigFromEnv()
	}

	dsn := cfg.BuildDSN()
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return fmt.Errorf("open database: %w", err)
	}

	// 测试连接
	if err := db.Ping(); err != nil {
		return fmt.Errorf("ping database: %w", err)
	}

	// 设置连接池参数
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)

	dbInstance = db

	// 自动创建表
	if err := createTables(); err != nil {
		return fmt.Errorf("create tables: %w", err)
	}

	return nil
}

// GetDB 获取数据库实例
func GetDB() *sql.DB {
	return dbInstance
}

// CloseDB 关闭数据库连接
func CloseDB() error {
	if dbInstance != nil {
		return dbInstance.Close()
	}
	return nil
}

// Hexagram 数据库中的卦象结构
type Hexagram struct {
	ID           int    `json:"id"`
	Number       int    `json:"number"`
	Name         string `json:"name"`
	UpperTrigram string `json:"upper_trigram"`
	LowerTrigram string `json:"lower_trigram"`
	Summary      string `json:"summary"`
	Detail       string `json:"detail"`
	Outcome      string `json:"outcome"`
	Wuxing       string `json:"wuxing"`
}

// GetHexagramByNumber 根据序号获取卦象
func GetHexagramByNumber(number int) (*Hexagram, error) {
	if dbInstance == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	query := `
		SELECT id, number, name, upper_trigram, lower_trigram, 
		       summary, detail, outcome, wuxing
		FROM hexagrams
		WHERE number = $1
	`

	var h Hexagram
	err := dbInstance.QueryRow(query, number).Scan(
		&h.ID,
		&h.Number,
		&h.Name,
		&h.UpperTrigram,
		&h.LowerTrigram,
		&h.Summary,
		&h.Detail,
		&h.Outcome,
		&h.Wuxing,
	)

	if err == sql.ErrNoRows {
		return nil, nil // 未找到，返回nil
	}
	if err != nil {
		return nil, fmt.Errorf("query hexagram: %w", err)
	}

	return &h, nil
}

// GetHexagramByName 根据名称获取卦象
func GetHexagramByName(name string) (*Hexagram, error) {
	if dbInstance == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	query := `
		SELECT id, number, name, upper_trigram, lower_trigram, 
		       summary, detail, outcome, wuxing
		FROM hexagrams
		WHERE name = $1 OR name LIKE $2
	`

	var h Hexagram
	err := dbInstance.QueryRow(query, name, "%"+name+"%").Scan(
		&h.ID,
		&h.Number,
		&h.Name,
		&h.UpperTrigram,
		&h.LowerTrigram,
		&h.Summary,
		&h.Detail,
		&h.Outcome,
		&h.Wuxing,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("query hexagram: %w", err)
	}

	return &h, nil
}

// GetAllHexagrams 获取所有卦象
func GetAllHexagrams() ([]*Hexagram, error) {
	if dbInstance == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	query := `
		SELECT id, number, name, upper_trigram, lower_trigram, 
		       summary, detail, outcome, wuxing
		FROM hexagrams
		ORDER BY number
	`

	rows, err := dbInstance.Query(query)
	if err != nil {
		return nil, fmt.Errorf("query hexagrams: %w", err)
	}
	defer rows.Close()

	var hexagrams []*Hexagram
	for rows.Next() {
		var h Hexagram
		if err := rows.Scan(
			&h.ID,
			&h.Number,
			&h.Name,
			&h.UpperTrigram,
			&h.LowerTrigram,
			&h.Summary,
			&h.Detail,
			&h.Outcome,
			&h.Wuxing,
		); err != nil {
			return nil, fmt.Errorf("scan hexagram: %w", err)
		}
		hexagrams = append(hexagrams, &h)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows error: %w", err)
	}

	return hexagrams, nil
}

// createTables 创建数据库表（如果不存在）
func createTables() error {
	if dbInstance == nil {
		return fmt.Errorf("database not initialized")
	}

	createTableSQL := `
	CREATE TABLE IF NOT EXISTS hexagrams (
		id SERIAL PRIMARY KEY,
		number INTEGER UNIQUE NOT NULL,
		name TEXT NOT NULL,
		upper_trigram TEXT,
		lower_trigram TEXT,
		summary TEXT,
		detail TEXT,
		outcome TEXT,
		wuxing TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_hexagram_number ON hexagrams(number);
	CREATE INDEX IF NOT EXISTS idx_hexagram_name ON hexagrams(name);

	CREATE TABLE IF NOT EXISTS user_profiles (
		id SERIAL PRIMARY KEY,
		user_id VARCHAR(255) NOT NULL UNIQUE,
		
		-- 基础信息
		nickname VARCHAR(100),
		gender VARCHAR(20),
		
		-- 公历出生信息（用户输入）
		birth_date DATE,
		birth_time TIME,
		
		-- 农历出生信息（系统自动转换）
		lunar_year INTEGER,
		lunar_month INTEGER,
		lunar_day INTEGER,
		is_leap_month BOOLEAN DEFAULT FALSE,
		lunar_month_cn VARCHAR(50),
		lunar_day_cn VARCHAR(50),
		
		-- 天干地支
		ganzhi_year VARCHAR(10),
		ganzhi_month VARCHAR(10),
		ganzhi_day VARCHAR(10),
		
		-- 其他信息
		animal VARCHAR(10),
		term VARCHAR(20),
		is_term BOOLEAN DEFAULT FALSE,
		
		-- 其他档案信息
		zodiac_sign VARCHAR(20),
		is_menstruating BOOLEAN DEFAULT FALSE,
		recent_exercise VARCHAR(20),
		
		-- 时间戳
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
	CREATE INDEX IF NOT EXISTS idx_user_profiles_birth_date ON user_profiles(birth_date);
	CREATE INDEX IF NOT EXISTS idx_user_profiles_lunar_date ON user_profiles(lunar_year, lunar_month, lunar_day);

	-- LLM配置表
	CREATE TABLE IF NOT EXISTS llm_configs (
		id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL UNIQUE,
		provider VARCHAR(50) NOT NULL,
		api_key TEXT,
		endpoint VARCHAR(500),
		model_name VARCHAR(100) NOT NULL,
		temperature DECIMAL(3,2) DEFAULT 0.7,
		max_tokens INTEGER DEFAULT 1000,
		timeout_seconds INTEGER DEFAULT 30,
		scene VARCHAR(50) DEFAULT 'divination', -- 场景：divination（占卜）/tarot（塔罗牌）
		is_default BOOLEAN DEFAULT FALSE,
		is_enabled BOOLEAN DEFAULT TRUE,
		description TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_llm_configs_provider ON llm_configs(provider);
	CREATE INDEX IF NOT EXISTS idx_llm_configs_enabled ON llm_configs(is_enabled);
	CREATE INDEX IF NOT EXISTS idx_llm_configs_default ON llm_configs(is_default);
	CREATE INDEX IF NOT EXISTS idx_llm_configs_scene ON llm_configs(scene);

	-- Prompt配置表
	CREATE TABLE IF NOT EXISTS prompt_configs (
		id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL UNIQUE,
		prompt_type VARCHAR(50) NOT NULL,
		question_type VARCHAR(50) NOT NULL,
		template TEXT NOT NULL,
		variables JSONB,
		is_default BOOLEAN DEFAULT FALSE,
		is_enabled BOOLEAN DEFAULT TRUE,
		description TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_prompt_configs_type ON prompt_configs(prompt_type, question_type);
	CREATE INDEX IF NOT EXISTS idx_prompt_configs_enabled ON prompt_configs(is_enabled);
	CREATE INDEX IF NOT EXISTS idx_prompt_configs_default ON prompt_configs(is_default);

	-- 占卜会话表
	CREATE TABLE IF NOT EXISTS divination_sessions (
		id VARCHAR(255) PRIMARY KEY,
		user_id VARCHAR(255) NOT NULL,
		version VARCHAR(20) NOT NULL,
		question TEXT NOT NULL,
		event_type VARCHAR(50) NOT NULL,
		orientation VARCHAR(20),
		spread VARCHAR(50),
		status VARCHAR(20) DEFAULT 'processing',
		follow_up_count INTEGER DEFAULT 0,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_divination_sessions_user_id ON divination_sessions(user_id);
	CREATE INDEX IF NOT EXISTS idx_divination_sessions_status ON divination_sessions(status);
	CREATE INDEX IF NOT EXISTS idx_divination_sessions_created_at ON divination_sessions(created_at DESC);

	-- 占卜结果表
	CREATE TABLE IF NOT EXISTS divination_results (
		id SERIAL PRIMARY KEY,
		session_id VARCHAR(255) NOT NULL UNIQUE,
		outcome VARCHAR(20),
		title VARCHAR(255),
		spread VARCHAR(50),
		summary TEXT NOT NULL,
		detail TEXT NOT NULL,
		raw_data TEXT,
		needs_follow_up BOOLEAN DEFAULT FALSE,
		
		-- 卦象信息（JSONB存储）
		hexagram_info JSONB,
		
		-- 推荐列表（JSONB存储）
		recommendations JSONB,
		
		-- 场景建议（JSONB存储）
		scene_advice JSONB,
		
		-- 后续问题（JSONB存储）
		follow_up_question JSONB,
		
		-- 塔罗牌（JSONB存储）
		cards JSONB,
		
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		
		FOREIGN KEY (session_id) REFERENCES divination_sessions(id) ON DELETE CASCADE
	);

	CREATE INDEX IF NOT EXISTS idx_divination_results_session_id ON divination_results(session_id);
	CREATE INDEX IF NOT EXISTS idx_divination_results_created_at ON divination_results(created_at DESC);

	-- 用户行为模式分析表
	CREATE TABLE IF NOT EXISTS user_patterns (
		id SERIAL PRIMARY KEY,
		user_id VARCHAR(255) NOT NULL,
		pattern_type VARCHAR(50) NOT NULL,
		pattern_data JSONB NOT NULL,
		frequency INTEGER DEFAULT 1,
		confidence FLOAT DEFAULT 0.5,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_user_patterns_user_id ON user_patterns(user_id);
	CREATE INDEX IF NOT EXISTS idx_user_patterns_type ON user_patterns(pattern_type);

	-- 问题质量评估历史表
	CREATE TABLE IF NOT EXISTS question_quality_history (
		id SERIAL PRIMARY KEY,
		session_id VARCHAR(255),
		original_question TEXT NOT NULL,
		enhanced_question TEXT,
		quality_score FLOAT NOT NULL,
		quality_factors JSONB NOT NULL,
		user_feedback INTEGER,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_question_quality_session ON question_quality_history(session_id);
	`

	if _, err := dbInstance.Exec(createTableSQL); err != nil {
		return fmt.Errorf("create table: %w", err)
	}

	return nil
}

