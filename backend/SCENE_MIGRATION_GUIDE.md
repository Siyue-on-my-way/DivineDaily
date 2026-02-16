# Divine Daily - 添加Scene字段支持

## 📋 改进目标

为Prompt配置添加Scene字段，使其与LLM配置保持一致，实现：
- 易经占卜（divination）和塔罗牌（tarot）使用不同的LLM和Prompt
- 每个场景可以独立配置和管理
- 未来可扩展更多场景（如每日运势、智能预处理等）

## ✅ 已完成的修改

### 1. 数据模型 (internal/model/config.go)
- ✅ 为 `PromptConfig` 添加 `Scene` 字段
- ✅ 更新 `PromptConfigCreateRequest` 添加 `Scene` 字段（必填）
- ✅ 更新 `PromptConfigUpdateRequest` 添加 `Scene` 字段
- ✅ 将 `QuestionType` 改为可选（用于向后兼容）

### 2. 数据库迁移 SQL
- ✅ 创建迁移脚本：`/tmp/add_scene.sql`
- ✅ 添加 `scene` 列到 `prompt_configs` 表
- ✅ 创建索引 `idx_prompt_configs_scene`
- ✅ 更新现有数据的scene值
- ✅ 将 `question_type` 改为可选

### 3. 初始化脚本 (cmd/init-configs/main.go)
- ✅ 创建易经占卜专用LLM配置
- ✅ 创建塔罗牌专用LLM配置
- ✅ 创建易经占卜Prompt模板（结果卡、详情）
- ✅ 创建塔罗牌Prompt模板（结果卡、详情）
- ✅ 所有配置都包含Scene字段

### 4. 管理后台页面
- ✅ 创建独立的管理后台布局（/admin/config）
- ✅ 桌面端友好的界面设计
- ✅ 左侧边栏导航
- ✅ 专业的视觉设计

## 🔧 需要手动执行的步骤

### 步骤1：运行数据库迁移
```bash
cd /mnt/DivineDaily/backend

# 方法1：使用psql（如果已安装）
psql -h localhost -U divinedaily -d divinedaily -f /tmp/add_scene.sql

# 方法2：使用Go程序执行
cat > cmd/migrate-add-scene/main.go << 'EOF'
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
	ALTER TABLE prompt_configs ADD COLUMN IF NOT EXISTS scene VARCHAR(50) DEFAULT 'divination';
	CREATE INDEX IF NOT EXISTS idx_prompt_configs_scene ON prompt_configs(scene);
	UPDATE prompt_configs SET scene = 'divination' WHERE question_type IN ('decision', 'recommendation');
	UPDATE prompt_configs SET scene = 'tarot' WHERE question_type = 'tarot';
	UPDATE prompt_configs SET scene = 'tarot' WHERE prompt_type IN ('tarot_summary', 'tarot_detail');
	ALTER TABLE prompt_configs ALTER COLUMN question_type DROP NOT NULL;
	`
	
	if _, err := db.Exec(sql); err != nil {
		log.Fatalf("执行迁移失败: %v", err)
	}
	
	log.Println("✅ 数据库迁移成功！")
}
EOF

go run cmd/migrate-add-scene/main.go
```

### 步骤2：重新初始化配置
```bash
cd /mnt/DivineDaily/backend
go run cmd/init-configs/main.go
```

### 步骤3：更新Repository层（需要修改代码）

需要修改 `internal/repository/config_repository.go` 中的以下函数：

#### 3.1 PromptConfigRepository.Create
在INSERT语句中添加scene字段：
```go
query := `
    INSERT INTO prompt_configs (
        name, scene, prompt_type, question_type, template,
        variables, is_default, is_enabled, description
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    RETURNING id, created_at, updated_at
`

err := r.db.QueryRow(
    query,
    config.Name, config.Scene, config.PromptType, config.QuestionType,
    config.Template, variablesJSON, config.IsDefault,
    config.IsEnabled, config.Description,
).Scan(&config.ID, &config.CreatedAt, &config.UpdatedAt)
```

#### 3.2 PromptConfigRepository.GetByID
在SELECT语句中添加scene字段：
```go
query := `
    SELECT id, name, scene, prompt_type, question_type, template,
           variables, is_default, is_enabled, description,
           created_at, updated_at
    FROM prompt_configs
    WHERE id = $1
`

err := r.db.QueryRow(query, id).Scan(
    &config.ID, &config.Name, &config.Scene, &config.PromptType, &config.QuestionType,
    &config.Template, &variablesJSON, &config.IsDefault,
    &config.IsEnabled, &config.Description, &config.CreatedAt,
    &config.UpdatedAt,
)
```

#### 3.3 PromptConfigRepository.GetByType
添加scene参数，按scene筛选：
```go
func (r *PromptConfigRepository) GetByTypeAndScene(promptType, scene string) (*model.PromptConfig, error) {
    // ...
    query := `
        SELECT id, name, scene, prompt_type, question_type, template,
               variables, is_default, is_enabled, description,
               created_at, updated_at
        FROM prompt_configs
        WHERE prompt_type = $1 AND scene = $2 AND is_enabled = TRUE
        ORDER BY is_default DESC
        LIMIT 1
    `
    // ...
}
```

#### 3.4 PromptConfigRepository.ListAll
在SELECT和Scan中添加scene：
```go
query := `
    SELECT id, name, scene, prompt_type, question_type, template,
           variables, is_default, is_enabled, description,
           created_at, updated_at
    FROM prompt_configs
    ORDER BY scene, prompt_type, is_default DESC, created_at DESC
`

// 在Scan中添加 &config.Scene
```

#### 3.5 PromptConfigRepository.Update
在UPDATE语句中添加scene字段：
```go
query := `
    UPDATE prompt_configs
    SET name = $2, scene = $3, prompt_type = $4, question_type = $5,
        template = $6, variables = $7, is_default = $8,
        is_enabled = $9, description = $10, updated_at = $11
    WHERE id = $1
`

result, err := r.db.Exec(
    query,
    config.ID, config.Name, config.Scene, config.PromptType, config.QuestionType,
    config.Template, variablesJSON, config.IsDefault,
    config.IsEnabled, config.Description, config.UpdatedAt,
)
```

### 步骤4：更新Service层

修改 `internal/service/config_service.go`：

```go
// 添加按scene获取Prompt的方法
func (s *ConfigService) GetPromptConfigByScene(promptType, scene string) (*model.PromptConfig, error) {
    return s.promptConfigRepo.GetByTypeAndScene(promptType, scene)
}
```

### 步骤5：更新前端类型定义

修改 `web/src/types/config.ts`，添加scene字段：

```typescript
export interface PromptConfig {
  id: number;
  name: string;
  scene: string; // 新增
  prompt_type: string;
  question_type?: string; // 改为可选
  template: string;
  variables?: PromptVariable[];
  is_default: boolean;
  is_enabled: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface PromptConfigCreateRequest {
  name: string;
  scene: string; // 新增，必填
  prompt_type: string;
  question_type?: string; // 改为可选
  template: string;
  variables?: PromptVariable[];
  is_enabled: boolean;
  description?: string;
}
```

### 步骤6：更新前端表单

修改 `web/src/components/config/PromptConfigForm.tsx`，添加scene选择：

```tsx
<div className="form-group">
  <label>场景 *</label>
  <select
    value={formData.scene}
    onChange={(e) => setFormData({ ...formData, scene: e.target.value })}
    required
  >
    <option value="divination">易经占卜</option>
    <option value="tarot">塔罗牌</option>
    <option value="daily_fortune">每日运势</option>
  </select>
</div>
```

### 步骤7：重启服务

```bash
# 重启后端
cd /mnt/DivineDaily/backend
pkill -f divine-daily-server
./divine-daily-server

# 前端会自动热重载
```

## 📊 配置架构

```
场景（Scene）
├── divination（易经占卜）
│   ├── LLM配置：易经占卜-DeepSeek
│   └── Prompt配置
│       ├── 易经-结果卡 (prompt_type: answer)
│       └── 易经-详情 (prompt_type: detail)
│
├── tarot（塔罗牌）
│   ├── LLM配置：塔罗牌-DeepSeek
│   └── Prompt配置
│       ├── 塔罗牌-结果卡 (prompt_type: answer)
│       └── 塔罗牌-详情 (prompt_type: detail)
│
└── daily_fortune（每日运势）
    ├── LLM配置：每日运势-XXX
    └── Prompt配置：...
```

## 🎯 使用方式

### 在代码中使用

```go
// 获取易经占卜的LLM配置
llmConfig, err := configService.GetDefaultLLMConfigByScene("divination")

// 获取易经占卜的结果卡Prompt
promptConfig, err := configService.GetPromptConfigByScene("answer", "divination")

// 获取塔罗牌的详情Prompt
promptConfig, err := configService.GetPromptConfigByScene("detail", "tarot")
```

### 在管理后台配置

1. 访问 `http://your-server:40080/admin/config`
2. 点击"LLM配置"标签
   - 为每个场景创建专用的LLM配置
   - 设置不同的模型、温度、Token数等
3. 点击"Prompt配置"标签
   - 为每个场景创建专用的Prompt模板
   - 选择对应的场景（divination/tarot）
   - 设置Prompt类型（answer/detail）

## 🔍 验证

运行以下SQL验证配置：

```sql
-- 查看LLM配置
SELECT id, name, scene, model_name, is_default, is_enabled 
FROM llm_configs 
ORDER BY scene, is_default DESC;

-- 查看Prompt配置
SELECT id, name, scene, prompt_type, is_default, is_enabled 
FROM prompt_configs 
ORDER BY scene, prompt_type;
```

## 📝 注意事项

1. **向后兼容**：保留了 `question_type` 字段，现有代码不会报错
2. **默认值**：scene默认为 `divination`，确保兼容性
3. **索引优化**：添加了scene索引，提高查询性能
4. **独立配置**：每个场景可以使用完全不同的LLM和Prompt
5. **扩展性**：未来可以轻松添加新场景（如风水、星座等）
