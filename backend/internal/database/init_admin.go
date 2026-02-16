package database

import (
	"divine-daily-backend/internal/model"
	"divine-daily-backend/pkg/crypto"
	"log"
)

// InitAdminUser 初始化管理员用户
func InitAdminUser() error {
	db := GetGormDB()
	if db == nil {
		return nil // 数据库未初始化，跳过
	}

	// 检查 admin 用户是否已存在
	var count int64
	if err := db.Model(&model.AuthUser{}).Where("username = ?", "admin").Count(&count).Error; err != nil {
		return err
	}

	if count > 0 {
		log.Println("Admin user already exists, skipping initialization")
		return nil
	}

	// 创建 admin 用户
	email := "admin@163.com"
	passwordHash, err := crypto.HashPassword("594120")
	if err != nil {
		return err
	}

	adminUser := &model.AuthUser{
		Username:     "admin",
		Email:        &email,
		PasswordHash: passwordHash,
		Role:         "admin",
		Status:       1,
	}

	if err := db.Create(adminUser).Error; err != nil {
		return err
	}

	log.Println("✅ Admin user created successfully (username: admin, password: 594120)")
	return nil
}
