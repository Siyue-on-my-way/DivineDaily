# Assistant 配置页面优化完成报告

## 📋 更新概述

将 Prompt 配置页面重命名为"Assistant 配置"，并添加了 LLM 模型选择功能，实现了配置的可组合性和灵活性。

---

## ✨ 主要改进

### 1. 页面重命名
- **Prompt 配置** → **Assistant 配置**
- 更准确地反映了页面的功能：配置 AI 助手的行为
- 包含 Prompt 模板 + LLM 模型选择 + 参数配置

### 2. LLM 模型选择
- 在编辑 Assistant 时可以选择使用哪个 LLM 模型
- 支持"使用默认模型"或"选择特定模型"
- 自动加载所有已启用的 LLM 配置
- 下拉列表显示：模型名称 (模型ID)

### 3. 增强的配置选项
- **场景选择**：divination（占卜）/ tarot（塔罗）/ daily_fortune（每日运势）/ preprocessing（预处理）
- **问题类型扩展**：decision / recommendation / fortune / knowledge
- **LLM 参数**：Temperature、Max Tokens、超时时间
- **关联模型**：可选择特定的 LLM 配置

---

## 🏗️ 技术实现

### 数据模型更新

#### PromptConfig（后端已有）
```go
type PromptConfig struct {
    ID             int
    Name           string
    PromptType     string  // answer/detail/recommendation
    QuestionType   string  // decision/recommendation/fortune/knowledge
    Template       string
    Variables      []PromptVariable
    LLMConfigID    *int    // 关联的LLM配置ID（新增）
    Temperature    float64
    MaxTokens      int
    TimeoutSeconds int
    Scene          string  // divination/tarot/daily_fortune/preprocessing
    IsDefault      bool
    IsEnabled      bool
    Description    string
}
```

### 前端更新

#### 1. 页面组件 (`PromptConfigPage.tsx`)
```typescript
<h1>Assistant 配置管理</h1>
<p>管理 AI Assistant 配置，包括 Prompt 模板、LLM 模型选择等</p>
```

#### 2. 列表组件 (`PromptConfigList.tsx`)
- 添加"关联模型"列
- 显示关联的 LLM 配置 ID 或"默认"

#### 3. 表单组件 (`PromptConfigForm.tsx`)
```typescript
// 加载 LLM 配置列表
useEffect(() => {
    const loadLLMConfigs = async () => {
        const configs = await llmConfigApi.list();
        setLlmConfigs(configs.filter(c => c.is_enabled));
    };
    loadLLMConfigs();
}, []);

// LLM 选择下拉框
<select value={formData.llm_config_id || ''}>
    <option value="">使用默认模型</option>
    {llmConfigs.map((llm) => (
        <option key={llm.id} value={llm.id}>
            {llm.name} ({llm.model_name})
        </option>
    ))}
</select>
```

---

## 📊 配置层级关系

```
Assistant 配置 (PromptConfig)
    ├─ 基础信息
    │   ├─ 名称
    │   ├─ 场景 (divination/tarot/...)
    │   ├─ Prompt 类型 (answer/detail/...)
    │   └─ 问题类型 (decision/recommendation/...)
    │
    ├─ LLM 配置
    │   ├─ 关联模型 (可选，留空使用默认)
    │   ├─ Temperature
    │   ├─ Max Tokens
    │   └─ 超时时间
    │
    ├─ Prompt 模板
    │   ├─ 模板内容 (Go template 语法)
    │   └─ 变量说明
    │
    └─ 其他
        ├─ 描述
        └─ 启用状态
```

---

## 🎯 使用场景

### 场景 1：使用默认 LLM
```
创建 Assistant 配置
├─ 名称：塔罗牌-结果卡
├─ 场景：tarot
├─ 关联模型：【使用默认模型】
└─ Prompt 模板：...
```
→ 系统会使用标记为"默认"的 LLM 配置

### 场景 2：使用特定 LLM
```
创建 Assistant 配置
├─ 名称：占卜-详情（使用 GPT-4）
├─ 场景：divination
├─ 关联模型：【GPT-4 (gpt-4-turbo)】
└─ Prompt 模板：...
```
→ 系统会使用指定的 GPT-4 模型

### 场景 3：不同场景使用不同模型
```
占卜-结果卡 → 使用 DeepSeek（快速、便宜）
占卜-详情   → 使用 GPT-4（质量高）
塔罗牌     → 使用 Claude（创意强）
```

---

## 📁 文件清单

### 更新文件
```
web/src/
├── pages/admin/
│   └── PromptConfigPage.tsx          # 改名为 Assistant 配置
├── components/config/
│   ├── PromptConfigList.tsx          # 添加"关联模型"列
│   └── PromptConfigForm.tsx          # 添加 LLM 选择功能
└── types/
    └── config.ts                     # 更新类型定义
```

### 后端（无需修改）
- `model/config.go` 已包含 `LLMConfigID` 字段
- `service/config_service.go` 已支持该字段
- `handler/config_handler.go` 已支持该字段

---

## 🎨 UI 改进

### 表单布局
```
┌─────────────────────────────────────┐
│ 配置名称 *        场景 *             │
│ [塔罗牌-结果卡]   [tarot ▼]         │
├─────────────────────────────────────┤
│ Prompt类型 *      问题类型 *         │
│ [answer ▼]        [decision ▼]      │
├─────────────────────────────────────┤
│ 关联 LLM 模型                        │
│ [使用默认模型 ▼]                     │
│ 💡 留空则使用系统默认 LLM 模型       │
├─────────────────────────────────────┤
│ Temperature  Max Tokens  超时时间   │
│ [0.7]        [2000]      [30]       │
├─────────────────────────────────────┤
│ Prompt 模板 *                        │
│ [                                   ]│
│ [  使用 {{.VariableName}} 作为变量  ]│
│ [                                   ]│
└─────────────────────────────────────┘
```

### 列表显示
```
┌──────────────────────────────────────────────────────┐
│ 名称              Prompt类型  问题类型  关联模型  默认 │
├──────────────────────────────────────────────────────┤
│ 塔罗牌-结果卡     answer     decision  ID: 2     是   │
│ 占卜-详情         detail     decision  默认      否   │
│ 每日运势          answer     fortune   ID: 3     否   │
└──────────────────────────────────────────────────────┘
```

---

## 🔄 工作流程

### 1. 配置 LLM 模型
```
LLM 配置页面
├─ 创建 GPT-4 配置
├─ 创建 DeepSeek 配置
└─ 创建 Claude 配置
```

### 2. 创建 Assistant 配置
```
Assistant 配置页面
├─ 选择场景（占卜/塔罗/运势）
├─ 选择 LLM 模型（或使用默认）
├─ 编写 Prompt 模板
└─ 设置参数（Temperature、Tokens）
```

### 3. 系统运行时
```
用户请求
    ↓
查找 Assistant 配置（根据场景+类型）
    ↓
检查是否有关联的 LLM 配置
    ├─ 有 → 使用指定的 LLM
    └─ 无 → 使用默认 LLM
    ↓
渲染 Prompt 模板
    ↓
调用 LLM API
    ↓
返回结果
```

---

## ✅ 优势

1. **灵活性**：不同场景可以使用不同的 LLM 模型
2. **可维护性**：LLM 配置和 Prompt 配置分离，便于管理
3. **成本优化**：简单任务用便宜模型，复杂任务用高级模型
4. **性能优化**：快速响应的场景用快速模型
5. **质量保证**：重要场景用高质量模型

---

## 🚀 下一步建议

1. **模型性能监控**：记录每个 Assistant 配置的调用次数、耗时、成本
2. **A/B 测试**：同一场景配置多个 Assistant，对比效果
3. **自动选择**：根据问题复杂度自动选择合适的模型
4. **批量操作**：批量更新多个 Assistant 的 LLM 配置
5. **版本管理**：支持 Assistant 配置的版本控制和回滚

---

**更新时间**: 2026-02-11  
**版本**: v2.1
