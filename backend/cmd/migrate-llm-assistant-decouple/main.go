package main

import (
	"divine-daily-backend/internal/database"
	"log"
)

func main() {
	if err := database.InitDB(); err != nil {
		log.Fatalf("初始化数据库失败: %v", err)
	}
	defer database.CloseDB()

	db := database.GetDB()
	
	sql := `
	-- 1. LLM配置表：移除scene字段和参数字段
	ALTER TABLE llm_configs DROP COLUMN IF EXISTS scene;
	ALTER TABLE llm_configs DROP COLUMN IF EXISTS temperature;
	ALTER TABLE llm_configs DROP COLUMN IF EXISTS max_tokens;
	ALTER TABLE llm_configs DROP COLUMN IF EXISTS timeout_seconds;
	DROP INDEX IF EXISTS idx_llm_configs_scene;

	-- 2. Assistant配置表：添加LLM关联和参数
	ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS llm_config_id INTEGER;
	ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS temperature DECIMAL(3,2) DEFAULT 0.7;
	ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS max_tokens INTEGER DEFAULT 2000;
	ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS timeout_seconds INTEGER DEFAULT 30;

	-- 3. 添加外键约束
	DO $$ 
	BEGIN
		IF NOT EXISTS (
			SELECT 1 FROM pg_constraint WHERE conname = 'fk_prompt_llm'
		) THEN
			ALTER TABLE prompt_configs ADD CONSTRAINT fk_prompt_llm 
				FOREIGN KEY (llm_config_id) REFERENCES llm_configs(id) ON DELETE SET NULL;
		END IF;
	END $$;

	-- 4. 创建索引
	CREATE INDEX IF NOT EXISTS idx_prompt_configs_llm ON prompt_configs(llm_config_id);

	-- 5. 数据迁移：将现有Assistant配置关联到对应的LLM（根据名称匹配）
	-- 易经占卜的Assistant关联到DeepSeek
	UPDATE prompt_configs 
	SET llm_config_id = (
		SELECT id FROM llm_configs 
		WHERE name LIKE '%DeepSeek%' OR name LIKE '%deepseek%'
		ORDER BY id LIMIT 1
	)
	WHERE scene = 'divination' AND llm_config_id IS NULL;

	-- 塔罗牌的Assistant关联到DeepSeek（如果有专门的塔罗配置则用塔罗的）
	UPDATE prompt_configs 
	SET llm_config_id = (
		SELECT id FROM llm_configs 
		WHERE name LIKE '%tarot%' OR name LIKE '%塔罗%'
		ORDER BY id LIMIT 1
	)
	WHERE scene = 'tarot' AND llm_config_id IS NULL;

	-- 如果塔罗没有专门的LLM，也用DeepSeek
	UPDATE prompt_configs 
	SET llm_config_id = (
		SELECT id FROM llm_configs 
		WHERE name LIKE '%DeepSeek%' OR name LIKE '%deepseek%'
		ORDER BY id LIMIT 1
	)
	WHERE scene = 'tarot' AND llm_config_id IS NULL;
	`
	
	if _, err := db.Exec(sql); err != nil {
		log.Fatalf("执行迁移失败: %v", err)
	}
	
	log.Println("✅ 数据库迁移成功！")
	log.Println("   - 移除了LLM配置的scene、temperature、max_tokens、timeout_seconds字段")
	log.Println("   - 为Assistant配置添加了llm_config_id、temperature、max_tokens、timeout_seconds字段")
	log.Println("   - 添加了外键约束")
	log.Println("   - 创建了索引")
	log.Println("   - 迁移了现有数据")
}
