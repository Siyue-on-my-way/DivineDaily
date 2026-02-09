package database

import (
	"fmt"
	"log"
	
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var (
	gormDB *gorm.DB
)

// InitGormDB 初始化 GORM 数据库连接（用于认证系统）
func InitGormDB(config ...DBConfig) error {
	var cfg DBConfig
	if len(config) > 0 {
		cfg = config[0]
	} else {
		cfg = GetDBConfigFromEnv()
	}

	dsn := cfg.BuildDSN()
	
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return fmt.Errorf("open gorm database: %w", err)
	}

	// 获取底层的 *sql.DB 并设置连接池
	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("get sql.DB: %w", err)
	}

	sqlDB.SetMaxOpenConns(25)
	sqlDB.SetMaxIdleConns(5)

	gormDB = db
	log.Println("GORM database initialized successfully")

	return nil
}

// GetGormDB 获取 GORM 数据库实例
func GetGormDB() *gorm.DB {
	return gormDB
}

// CloseGormDB 关闭 GORM 数据库连接
func CloseGormDB() error {
	if gormDB != nil {
		sqlDB, err := gormDB.DB()
		if err != nil {
			return err
		}
		return sqlDB.Close()
	}
	return nil
}
