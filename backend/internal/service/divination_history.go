package service

import (
	"divine-daily-backend/internal/model"
)

// ListHistory 获取用户历史占卜记录
func (s *DivinationService) ListHistory(userID string, limit, offset int) ([]*model.DivinationSession, error) {
	if s.repo != nil {
		return s.repo.ListSessionsByUser(userID, limit, offset)
	}
	// 如果数据库不可用，返回空列表
	return []*model.DivinationSession{}, nil
}

// GetHistoryCount 获取用户历史记录总数
func (s *DivinationService) GetHistoryCount(userID string) (int, error) {
	if s.repo != nil {
		return s.repo.CountSessionsByUser(userID)
	}
	return 0, nil
}

