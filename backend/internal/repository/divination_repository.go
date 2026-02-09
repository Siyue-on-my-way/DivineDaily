package repository

import (
	"database/sql"
	"divine-daily-backend/internal/model"
	"encoding/json"
	"fmt"
	"time"
)

// DivinationRepository 占卜数据仓库
type DivinationRepository struct {
	db *sql.DB
}

// NewDivinationRepository 创建占卜数据仓库
func NewDivinationRepository(db *sql.DB) *DivinationRepository {
	return &DivinationRepository{db: db}
}

// SaveSession 保存占卜会话
func (r *DivinationRepository) SaveSession(session *model.DivinationSession) error {
	query := `
		INSERT INTO divination_sessions 
		(id, user_id, version, question, event_type, orientation, spread, status, follow_up_count, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
		ON CONFLICT (id) DO UPDATE SET
			status = EXCLUDED.status,
			follow_up_count = EXCLUDED.follow_up_count,
			updated_at = EXCLUDED.updated_at
	`
	
	_, err := r.db.Exec(query,
		session.ID,
		session.UserID,
		session.Version,
		session.Question,
		session.EventType,
		session.Orientation,
		session.Spread,
		session.Status,
		session.FollowUpCount,
		session.CreatedAt,
		time.Now(),
	)
	
	return err
}

// GetSession 根据ID获取会话
func (r *DivinationRepository) GetSession(sessionID string) (*model.DivinationSession, error) {
	query := `
		SELECT id, user_id, version, question, event_type, orientation, spread, 
		       status, follow_up_count, created_at, updated_at
		FROM divination_sessions
		WHERE id = $1
	`
	
	var session model.DivinationSession
	err := r.db.QueryRow(query, sessionID).Scan(
		&session.ID,
		&session.UserID,
		&session.Version,
		&session.Question,
		&session.EventType,
		&session.Orientation,
		&session.Spread,
		&session.Status,
		&session.FollowUpCount,
		&session.CreatedAt,
		&session.UpdatedAt,
	)
	
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("session not found")
	}
	if err != nil {
		return nil, err
	}
	
	return &session, nil
}

// UpdateSessionStatus 更新会话状态
func (r *DivinationRepository) UpdateSessionStatus(sessionID, status string) error {
	query := `UPDATE divination_sessions SET status = $1, updated_at = $2 WHERE id = $3`
	_, err := r.db.Exec(query, status, time.Now(), sessionID)
	return err
}

// SaveResult 保存占卜结果
func (r *DivinationRepository) SaveResult(result *model.DivinationResult) error {
	// 序列化JSON字段
	hexagramJSON, _ := json.Marshal(result.HexagramInfo)
	recommendationsJSON, _ := json.Marshal(result.Recommendations)
	sceneAdviceJSON, _ := json.Marshal(result.SceneAdvice)
	followUpQJSON, _ := json.Marshal(result.FollowUpQ)
	cardsJSON, _ := json.Marshal(result.Cards)
	
	query := `
		INSERT INTO divination_results 
		(session_id, outcome, title, spread, summary, detail, raw_data, needs_follow_up,
		 hexagram_info, recommendations, scene_advice, follow_up_question, cards, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
		ON CONFLICT (session_id) DO UPDATE SET
			outcome = EXCLUDED.outcome,
			title = EXCLUDED.title,
			spread = EXCLUDED.spread,
			summary = EXCLUDED.summary,
			detail = EXCLUDED.detail,
			raw_data = EXCLUDED.raw_data,
			needs_follow_up = EXCLUDED.needs_follow_up,
			hexagram_info = EXCLUDED.hexagram_info,
			recommendations = EXCLUDED.recommendations,
			scene_advice = EXCLUDED.scene_advice,
			follow_up_question = EXCLUDED.follow_up_question,
			cards = EXCLUDED.cards,
			updated_at = EXCLUDED.updated_at
	`
	
	_, err := r.db.Exec(query,
		result.SessionID,
		result.Outcome,
		result.Title,
		result.Spread,
		result.Summary,
		result.Detail,
		result.RawData,
		result.NeedsFollowUp,
		hexagramJSON,
		recommendationsJSON,
		sceneAdviceJSON,
		followUpQJSON,
		cardsJSON,
		result.CreatedAt,
		time.Now(),
	)
	
	return err
}

// GetResult 根据会话ID获取结果
func (r *DivinationRepository) GetResult(sessionID string) (*model.DivinationResult, error) {
	query := `
		SELECT session_id, outcome, title, spread, summary, detail, raw_data, needs_follow_up,
		       hexagram_info, recommendations, scene_advice, follow_up_question, cards, created_at
		FROM divination_results
		WHERE session_id = $1
	`
	
	var result model.DivinationResult
	var hexagramJSON, recommendationsJSON, sceneAdviceJSON, followUpQJSON, cardsJSON sql.NullString
	
	err := r.db.QueryRow(query, sessionID).Scan(
		&result.SessionID,
		&result.Outcome,
		&result.Title,
		&result.Spread,
		&result.Summary,
		&result.Detail,
		&result.RawData,
		&result.NeedsFollowUp,
		&hexagramJSON,
		&recommendationsJSON,
		&sceneAdviceJSON,
		&followUpQJSON,
		&cardsJSON,
		&result.CreatedAt,
	)
	
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("result not found")
	}
	if err != nil {
		return nil, err
	}
	
	// 反序列化JSON字段
	if hexagramJSON.Valid && hexagramJSON.String != "" {
		json.Unmarshal([]byte(hexagramJSON.String), &result.HexagramInfo)
	}
	if recommendationsJSON.Valid && recommendationsJSON.String != "" {
		json.Unmarshal([]byte(recommendationsJSON.String), &result.Recommendations)
	}
	if sceneAdviceJSON.Valid && sceneAdviceJSON.String != "" {
		json.Unmarshal([]byte(sceneAdviceJSON.String), &result.SceneAdvice)
	}
	if followUpQJSON.Valid && followUpQJSON.String != "" {
		json.Unmarshal([]byte(followUpQJSON.String), &result.FollowUpQ)
	}
	if cardsJSON.Valid && cardsJSON.String != "" {
		json.Unmarshal([]byte(cardsJSON.String), &result.Cards)
	}
	
	return &result, nil
}

// ListSessionsByUser 获取用户的历史会话列表
func (r *DivinationRepository) ListSessionsByUser(userID string, limit, offset int) ([]*model.DivinationSession, error) {
	query := `
		SELECT id, user_id, version, question, event_type, orientation, spread, 
		       status, follow_up_count, created_at, updated_at
		FROM divination_sessions
		WHERE user_id = $1
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3
	`
	
	rows, err := r.db.Query(query, userID, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var sessions []*model.DivinationSession
	for rows.Next() {
		var session model.DivinationSession
		err := rows.Scan(
			&session.ID,
			&session.UserID,
			&session.Version,
			&session.Question,
			&session.EventType,
			&session.Orientation,
			&session.Spread,
			&session.Status,
			&session.FollowUpCount,
			&session.CreatedAt,
			&session.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		sessions = append(sessions, &session)
	}
	
	return sessions, rows.Err()
}

// CountSessionsByUser 统计用户的会话数量
func (r *DivinationRepository) CountSessionsByUser(userID string) (int, error) {
	query := `SELECT COUNT(*) FROM divination_sessions WHERE user_id = $1`
	var count int
	err := r.db.QueryRow(query, userID).Scan(&count)
	return count, err
}

