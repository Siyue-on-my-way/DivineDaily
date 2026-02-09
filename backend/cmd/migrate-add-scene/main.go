package main

import (
	"divine-daily-backend/internal/database"
	"fmt"
	"log"
)

func main() {
	fmt.Println("=== 添加scene字段到llm_configs表 ===")

	// 初始化数据库
	if err := database.InitDB(); err != nil {
		log.Fatalf("数据库初始化失败: %v", err)
	}
	defer database.CloseDB()

	db := database.GetDB()

	// 检查scene字段是否存在
	var exists bool
	checkQuery := `
		SELECT EXISTS (
			SELECT 1 
			FROM information_schema.columns 
			WHERE table_name = 'llm_configs' 
			AND column_name = 'scene'
		)
	`
	err := db.QueryRow(checkQuery).Scan(&exists)
	if err != nil {
		log.Fatalf("检查字段失败: %v", err)
	}

	if exists {
		fmt.Println("✓ scene字段已存在，跳过迁移")
		return
	}

	// 添加scene字段
	fmt.Println("\n添加scene字段...")
	alterQuery := `
		ALTER TABLE llm_configs 
		ADD COLUMN scene VARCHAR(50) DEFAULT 'divination';
	`
	_, err = db.Exec(alterQuery)
	if err != nil {
		log.Fatalf("添加字段失败: %v", err)
	}
	fmt.Println("✓ scene字段添加成功")

	// 创建索引
	fmt.Println("\n创建索引...")
	indexQuery := `CREATE INDEX IF NOT EXISTS idx_llm_configs_scene ON llm_configs(scene);`
	_, err = db.Exec(indexQuery)
	if err != nil {
		log.Fatalf("创建索引失败: %v", err)
	}
	fmt.Println("✓ 索引创建成功")

	// 更新现有数据：将所有现有配置设置为divination场景
	fmt.Println("\n更新现有数据...")
	updateQuery := `UPDATE llm_configs SET scene = 'divination' WHERE scene IS NULL OR scene = '';`
	result, err := db.Exec(updateQuery)
	if err != nil {
		log.Fatalf("更新数据失败: %v", err)
	}
	rowsAffected, _ := result.RowsAffected()
	fmt.Printf("✓ 更新了 %d 条记录\n", rowsAffected)

	fmt.Println("\n=== 迁移完成 ===")
}

