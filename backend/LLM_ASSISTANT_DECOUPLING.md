# Divine Daily - LLM与Assistant配置解耦方案

## 🎯 优化目标

将LLM配置和Assistant配置解耦，实现更灵活的配置管理。

## 📊 当前问题

1. **LLM配置冗余**
   - 同一个模型（如DeepSeek）需要为每个场景创建配置
   - 配置重复，管理复杂

2. **耦合度高**
   - LLM配置包含scene字段
   - 无法灵活切换模型

3. **不够灵活**
   - 想让易经用GPT-4，塔罗用DeepSeek？需要创建多个配置
   - 无法快速切换模型进行对比测试

## ✅ 优化方案

### 核心思想
- **LLM配置**：只管理模型本身（endpoint、api_key、model_name）
- **Assistant配置**：选择使用哪个LLM + 自己的参数（temperature、max_tokens）

### 配置关系

```
┌─────────────────────────────────────────────────────────┐
│                    LLM配置池（模型库）                      │
├─────────────────────────────────────────────────────────┤
│ 1. DeepSeek-V3.1                                        │
│    - Endpoint: https://api.deepseek.com/v1             │
│    - API Key: sk-xxx                                    │
│    - Model: deepseek-v3.1-thinking                      │
│                                                          │
│ 2. GPT-4                                                │
│    - Endpoint: https://api.openai.com/v1               │
│    - API Key: sk-yyy                                    │
│    - Model: gpt-4                                       │
└─────────────────────────────────────────────────────────┘
                          ↓ 选择使用
┌─────────────────────────────────────────────────────────┐
│              Assistant配置（AI助手定义）                    │
├─────────────────────────────────────────────────────────┤
│ 易经占卜Assistant                                         │
│ ├── Scene: divination                                   │
│ ├── 选择LLM: DeepSeek-V3.1  ← 从LLM池选择               │
│ ├── Temperature: 0.7        ← Assistant自己的参数        │
│ ├── Max Tokens: 2000                                    │
│ ├── Prompt模板: ...                                      │
│ └── Variables: ...                                      │
│                                                          │
│ 塔罗牌Assistant                                           │
│ ├── Scene: tarot                                        │
│ ├── 选择LLM: GPT-4          ← 从LLM池选择               │
│ ├── Temperature: 0.8        ← Assistant自己的参数        │
│ ├── Max Tokens: 2000                                    │
│ ├── Prompt模板: ...                                      │
│ └── Variables: ...                                      │
└─────────────────────────────────────────────────────────┘
```

## 🔧 实施步骤

### 步骤1：数据库迁移

```sql
-- 1. LLM配置表：移除scene字段，移除temperature/max_tokens
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
ALTER TABLE prompt_configs ADD CONSTRAINT fk_prompt_llm 
    FOREIGN KEY (llm_config_id) REFERENCES llm_configs(id) ON DELETE SET NULL;

-- 4. 创建索引
CREATE INDEX IF NOT EXISTS idx_prompt_configs_llm ON prompt_configs(llm_config_id);

-- 5. 数据迁移：将现有Assistant配置关联到对应的LLM
UPDATE prompt_configs p
SET llm_config_id = (
    SELECT l.id 
    FROM llm_configs l 
    WHERE l.scene = p.scene 
    AND l.is_default = TRUE 
    LIMIT 1
)
WHERE p.llm_config_id IS NULL;

-- 6. 清理：删除重复的LLM配置，只保留唯一的模型
-- 手动操作：在管理后台删除重复的LLM配置
```

### 步骤2：更新数据模型

#### LLMConfig（简化）
```go
type LLMConfig struct {
    ID          int       `json:"id"`
    Name        string    `json:"name"`        // "DeepSeek-V3.1"
    Provider    string    `json:"provider"`    // "openai"/"anthropic"/"local"
    URLType     string    `json:"url_type"`    // "openai_compatible"/"custom"
    APIKey      string    `json:"api_key"`
    Endpoint    string    `json:"endpoint"`    // "https://api.deepseek.com/v1"
    ModelName   string    `json:"model_name"`  // "deepseek-v3.1-thinking"
    IsDefault   bool      `json:"is_default"`
    IsEnabled   bool      `json:"is_enabled"`
    Description string    `json:"description"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
}
```

#### PromptConfig（Assistant配置，增强）
```go
type PromptConfig struct {
    ID            int              `json:"id"`
    Name          string           `json:"name"`
    Scene         string           `json:"scene"`         // divination/tarot
    LLMConfigID   *int             `json:"llm_config_id"` // 关联的LLM ID
    LLMConfig     *LLMConfig       `json:"llm_config"`    // 关联的LLM对象（查询时填充）
    Temperature   float64          `json:"temperature"`   // 0.7
    MaxTokens     int              `json:"max_tokens"`    // 2000
    TimeoutSeconds int             `json:"timeout_seconds"` // 30
    PromptType    string           `json:"prompt_type"`   // answer/detail
    Template      string           `json:"template"`
    Variables     []PromptVariable `json:"variables"`
    IsDefault     bool             `json:"is_default"`
    IsEnabled     bool             `json:"is_enabled"`
    Description   string           `json:"description"`
    CreatedAt     time.Time        `json:"created_at"`
    UpdatedAt     time.Time        `json:"updated_at"`
}
```

### 步骤3：更新前端表单

#### Assistant配置表单添加LLM选择器
```tsx
<div className="form-group">
  <label>选择LLM模型 *</label>
  <select
    value={formData.llm_config_id || ''}
    onChange={(e) => setFormData({ 
      ...formData, 
      llm_config_id: e.target.value ? parseInt(e.target.value) : null 
    })}
    required
  >
    <option value="">请选择LLM模型</option>
    {availableLLMs.map(llm => (
      <option key={llm.id} value={llm.id}>
        {llm.name} ({llm.model_name})
      </option>
    ))}
  </select>
</div>

<div className="form-group">
  <label>Temperature</label>
  <input
    type="number"
    step="0.1"
    min="0"
    max="2"
    value={formData.temperature}
    onChange={(e) => setFormData({ 
      ...formData, 
      temperature: parseFloat(e.target.value) 
    })}
  />
</div>

<div className="form-group">
  <label>Max Tokens</label>
  <input
    type="number"
    min="1"
    value={formData.max_tokens}
    onChange={(e) => setFormData({ 
      ...formData, 
      max_tokens: parseInt(e.target.value) 
    })}
  />
</div>
```

### 步骤4：更新Repository层

```go
// 查询Assistant配置时，自动关联LLM配置
func (r *PromptConfigRepository) GetByID(id int) (*model.PromptConfig, error) {
    config := &model.PromptConfig{}
    
    // 查询Assistant配置
    query := `
        SELECT id, name, scene, llm_config_id, temperature, max_tokens, 
               timeout_seconds, prompt_type, question_type, template,
               variables, is_default, is_enabled, description,
               created_at, updated_at
        FROM prompt_configs
        WHERE id = $1
    `
    
    err := r.db.QueryRow(query, id).Scan(...)
    
    // 如果有关联的LLM，查询LLM配置
    if config.LLMConfigID != nil {
        llmConfig, err := r.llmRepo.GetByID(*config.LLMConfigID)
        if err == nil {
            config.LLMConfig = llmConfig
        }
    }
    
    return config, nil
}
```

## 🎨 管理后台界面

### LLM配置页面
```
┌─────────────────────────────────────────────────────────┐
│ LLM配置列表                              [+ 新建配置]     │
├─────────────────────────────────────────────────────────┤
│ 名称              模型                  端点              │
│ DeepSeek-V3.1    deepseek-v3.1-...   api.deepseek.com  │
│ GPT-4            gpt-4                api.openai.com    │
│ Claude-3         claude-3-opus        api.anthropic.com│
└─────────────────────────────────────────────────────────┘
```

### Assistant配置页面
```
┌─────────────────────────────────────────────────────────┐
│ Assistant配置列表                        [+ 新建配置]     │
├─────────────────────────────────────────────────────────┤
│ 名称        场景        使用LLM         温度    Token    │
│ 易经-结果卡  divination  DeepSeek-V3.1  0.7    2000    │
│ 易经-详情    divination  GPT-4          0.7    2000    │
│ 塔罗-结果卡  tarot       GPT-4          0.8    2000    │
│ 塔罗-详情    tarot       Claude-3       0.8    3000    │
└─────────────────────────────────────────────────────────┘
```

## 💡 优势

### 1. 灵活性
- ✅ 一个LLM可以被多个Assistant使用
- ✅ 轻松切换模型进行对比测试
- ✅ 不同Assistant可以使用不同的参数

### 2. 简洁性
- ✅ LLM配置只需要2-3个（实际使用的模型数量）
- ✅ 不需要为每个场景创建重复配置
- ✅ 配置清晰，易于管理

### 3. 可维护性
- ✅ 修改LLM的API Key，所有使用它的Assistant自动生效
- ✅ 添加新模型，所有Assistant都可以选择使用
- ✅ 配置关系清晰，易于理解

### 4. 扩展性
- ✅ 未来可以为Assistant添加Tools配置
- ✅ 未来可以为Assistant添加Function Calls
- ✅ 未来可以添加更多LLM提供商

## 📝 使用示例

### 场景1：对比测试
```
想测试GPT-4和DeepSeek哪个更适合易经占卜？

1. 创建两个Assistant：
   - 易经-GPT4版：选择GPT-4
   - 易经-DeepSeek版：选择DeepSeek-V3.1
   
2. 分别测试，对比效果

3. 选择最佳的设为默认
```

### 场景2：快速切换
```
DeepSeek API出问题了，想临时切换到GPT-4？

1. 编辑"易经-结果卡"Assistant
2. 将LLM从DeepSeek改为GPT-4
3. 保存，立即生效
```

### 场景3：统一管理
```
DeepSeek的API Key过期了？

1. 只需要在LLM配置中更新一次
2. 所有使用DeepSeek的Assistant自动生效
3. 不需要逐个修改Assistant配置
```

## 🚀 实施建议

### 阶段1：数据库迁移（立即执行）
1. 运行迁移SQL
2. 验证数据完整性
3. 备份数据库

### 阶段2：后端代码更新（1-2小时）
1. 更新Model定义
2. 更新Repository层
3. 更新Service层
4. 测试API

### 阶段3：前端界面更新（1-2小时）
1. 更新Assistant表单，添加LLM选择器
2. 更新LLM表单，移除scene字段
3. 更新列表显示
4. 测试界面

### 阶段4：清理和优化（30分钟）
1. 删除重复的LLM配置
2. 更新文档
3. 全面测试

## ✅ 验收标准

- [ ] LLM配置只有2-3个（实际使用的模型）
- [ ] Assistant配置可以选择任意LLM
- [ ] 修改LLM的API Key，相关Assistant自动生效
- [ ] 可以为不同Assistant设置不同的temperature和max_tokens
- [ ] 管理后台界面清晰易用
- [ ] 所有API正常工作
- [ ] 占卜功能正常

## 📊 预期效果

### 配置数量对比
```
优化前：
- LLM配置：4个（易经-DeepSeek、塔罗-DeepSeek、易经-GPT4、塔罗-GPT4）
- Assistant配置：4个

优化后：
- LLM配置：2个（DeepSeek、GPT-4）
- Assistant配置：4个（但可以灵活选择LLM）

配置减少50%，灵活性提升100%！
```

这个方案完全符合您的想法，实现了配置的解耦和灵活化！🎉
