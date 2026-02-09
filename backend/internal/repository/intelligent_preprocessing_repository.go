package repository

import (
	"database/sql"
	"divine-daily-backend/internal/model"
	"encoding/json"
	"fmt"
	"time"
)

// UserPatternRepository handles user behavior pattern storage
type UserPatternRepository struct {
	db *sql.DB
}

// NewUserPatternRepository creates a new user pattern repository
func NewUserPatternRepository(db *sql.DB) *UserPatternRepository {
	return &UserPatternRepository{db: db}
}

// FindByUserID retrieves patterns for a specific user
func (r *UserPatternRepository) FindByUserID(userID string) ([]model.UserPattern, error) {
	query := `
		SELECT id, user_id, pattern_type, pattern_data, frequency, confidence, created_at, updated_at
		FROM user_patterns
		WHERE user_id = $1
	`
	
	rows, err := r.db.Query(query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var patterns []model.UserPattern
	for rows.Next() {
		var p model.UserPattern
		var dataJSON []byte
		
		err := rows.Scan(
			&p.ID,
			&p.UserID,
			&p.PatternType,
			&dataJSON,
			&p.Frequency,
			&p.Confidence,
			&p.CreatedAt,
			&p.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		
		if err := json.Unmarshal(dataJSON, &p.PatternData); err != nil {
			return nil, fmt.Errorf("failed to unmarshal pattern data: %w", err)
		}
		
		patterns = append(patterns, p)
	}
	
	return patterns, nil
}

// Save saves or updates a user pattern
func (r *UserPatternRepository) Save(pattern *model.UserPattern) error {
	dataJSON, err := json.Marshal(pattern.PatternData)
	if err != nil {
		return err
	}

	// Simple upsert logic could be more complex based on specific needs, 
	// here we assume new patterns are inserted. For updates, we might need ID or unique constraints.
	// For now, let's just insert.
	query := `
		INSERT INTO user_patterns (user_id, pattern_type, pattern_data, frequency, confidence, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id
	`
	
	err = r.db.QueryRow(query,
		pattern.UserID,
		pattern.PatternType,
		dataJSON,
		pattern.Frequency,
		pattern.Confidence,
		pattern.CreatedAt,
		time.Now(),
	).Scan(&pattern.ID)
	
	return err
}

// QuestionQualityRepository handles question quality history storage
type QuestionQualityRepository struct {
	db *sql.DB
}

// NewQuestionQualityRepository creates a new question quality repository
func NewQuestionQualityRepository(db *sql.DB) *QuestionQualityRepository {
	return &QuestionQualityRepository{db: db}
}

// Save saves a quality assessment record
func (r *QuestionQualityRepository) Save(record *model.QuestionQualityHistory) error {
	factorsJSON, err := json.Marshal(record.QualityFactors)
	if err != nil {
		return err
	}
	
	query := `
		INSERT INTO question_quality_history 
		(session_id, original_question, enhanced_question, quality_score, quality_factors, user_feedback, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id
	`
	
	err = r.db.QueryRow(query,
		record.SessionID,
		record.OriginalQuestion,
		record.EnhancedQuestion,
		record.QualityScore,
		factorsJSON,
		record.UserFeedback,
		record.CreatedAt,
	).Scan(&record.ID)
	
	return err
}
