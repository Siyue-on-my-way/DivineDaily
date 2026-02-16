-- 修改 LLM 配置表：移除 scene 字段
ALTER TABLE llm_configs DROP COLUMN IF EXISTS scene;
DROP INDEX IF EXISTS idx_llm_configs_scene;

-- 修改 Prompt(Assistant) 配置表：添加 llm_config_id 字段
ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS llm_config_id INTEGER;
ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS temperature DECIMAL(3,2) DEFAULT 0.7;
ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS max_tokens INTEGER DEFAULT 2000;

-- 添加外键约束
ALTER TABLE prompt_configs ADD CONSTRAINT fk_prompt_llm 
    FOREIGN KEY (llm_config_id) REFERENCES llm_configs(id) ON DELETE SET NULL;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_prompt_configs_llm ON prompt_configs(llm_config_id);

-- 迁移现有数据：根据 scene 匹配 LLM
UPDATE prompt_configs p
SET llm_config_id = (
    SELECT l.id 
    FROM llm_configs l 
    WHERE l.scene = p.scene 
    AND l.is_default = TRUE 
    LIMIT 1
)
WHERE p.llm_config_id IS NULL;
