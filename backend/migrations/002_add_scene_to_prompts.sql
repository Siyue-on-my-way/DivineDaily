-- 为 prompt_configs 表添加 scene 字段
ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS scene VARCHAR(50) DEFAULT 'divination';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_prompt_configs_scene ON prompt_configs(scene);

-- 更新现有数据
UPDATE prompt_configs SET scene = 'divination' WHERE question_type IN ('decision', 'recommendation');
UPDATE prompt_configs SET scene = 'tarot' WHERE question_type = 'tarot';

-- 更新塔罗牌的 prompt_type
UPDATE prompt_configs SET prompt_type = 'answer' WHERE prompt_type = 'tarot_summary';
UPDATE prompt_configs SET prompt_type = 'detail' WHERE prompt_type = 'tarot_detail';
