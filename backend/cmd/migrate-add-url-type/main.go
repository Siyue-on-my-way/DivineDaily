package main

import (
	"divine-daily-backend/internal/database"
	"fmt"
	"log"
)

func main() {
	fmt.Println("=== 添加url_type字段到llm_configs表 ===")

	// 初始化数据库
	if err := database.InitDB(); err != nil {
		log.Fatalf("数据库初始化失败: %v", err)
	}
	defer database.CloseDB()

	db := database.GetDB()

	// 检查url_type字段是否存在
	var exists bool
	checkQuery := `
		SELECT EXISTS (
			SELECT 1 
			FROM information_schema.columns 
			WHERE table_name = 'llm_configs' 
			AND column_name = 'url_type'
		)
	`
	err := db.QueryRow(checkQuery).Scan(&exists)
	if err != nil {
		log.Fatalf("检查字段失败: %v", err)
	}

	if exists {
		fmt.Println("✓ url_type字段已存在，跳过添加字段")
	} else {
		// 添加url_type字段
		fmt.Println("\n添加url_type字段...")
		alterQuery := `
			ALTER TABLE llm_configs 
			ADD COLUMN url_type VARCHAR(50) DEFAULT 'openai_compatible';
		`
		_, err = db.Exec(alterQuery)
		if err != nil {
			log.Fatalf("添加字段失败: %v", err)
		}
		fmt.Println("✓ url_type字段添加成功")
	}

	// 更新现有数据：将所有现有配置的url_type默认为openai_compatible（如果是NULL）
	fmt.Println("\n更新现有数据...")
	updateQuery := `UPDATE llm_configs SET url_type = 'openai_compatible' WHERE url_type IS NULL OR url_type = '';`
	result, err := db.Exec(updateQuery)
	if err != nil {
		log.Fatalf("更新数据失败: %v", err)
	}
	rowsAffected, _ := result.RowsAffected()
	fmt.Printf("✓ 更新了 %d 条记录\n", rowsAffected)

	fmt.Println("\n=== 迁移完成 ===")
}
