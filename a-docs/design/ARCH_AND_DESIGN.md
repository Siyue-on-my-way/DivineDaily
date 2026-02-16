# DivineDaily - 架构与设计文档 (Architecture & Design)

## 1. 产品概述 (Product Overview)
DivineDaily 是一款结合传统玄学（国内版）与西方神秘学（国外版）的日常占卜与决策辅助应用。利用大语言模型（LLM）的能力，为用户提供简明扼要的运势分析及生活建议。

### 核心理念
- **万物皆可占 (Everything is Divinable)**: 无论是二选一的决策、每日运势查询，还是深度情感分析，统一通过智能意图识别系统进行处理。
- **文化适配**:
    - **国内版 (CN)**: 基于周易六爻、八卦、五行，强调“吉凶”、“运势”。
    - **国际版 (Global)**: 基于韦特塔罗、占星术，强调“指引”、“能量”。

---

## 2. 核心架构 (Core Architecture)

系统采用 **“三层智能漏斗”** 架构，将用户自然语言转化为结构化的占卜服务。

### 第一层：意图感知 (Intent Recognition)
**模块**: `IntelligentPreprocessingService`
系统在预处理阶段对用户问题进行语义分析，识别核心意图：

| 意图代码 | 类型 | 典型问题 | 处理策略 |
| :--- | :--- | :--- | :--- |
| `binary_choice` | **决策** | “往左走还是往右走？” | 六爻/塔罗起卦 -> 明确吉凶判断 |
| `daily_luck` | **运势** | “今天穿什么颜色运气好？” | `DailyFortuneService` -> 综合运势报告 |
| `knowledge` | **知识** | “什么是潜龙勿用？” | 知识库检索 -> 易学/神秘学解答 |
| `deep_analysis` | **深度** | “我和他的未来发展” | 复杂起卦 -> LLM 深度RAG解析 |

### 第二层：策略分发 (Strategy Dispatch)
**模块**: `DivinationService`
根据识别出的意图，路由到不同的服务：
1.  **标准起卦模式**: 执行完整的纳甲筮法或塔罗抽牌流程（适用于 `binary_choice`, `deep_analysis`）。
2.  **每日运势模式**: 调用 `DailyFortuneService`，结合用户档案与时间数据生成报告（适用于 `daily_luck`）。

### 第三层：情境融合 (Context Fusion)
**模块**: `LLM Service`
在生成最终回复时，动态注入意图指令，调整 AI 的角色设定（决策顾问 vs 生活向导 vs 易学大师）。

---

## 3. 核心功能模块 (Core Modules)

### 3.1 每日运势 (Daily Fortune)
专为 `daily_luck` 意图设计的高频功能。
- **输入**: 用户ID + 当前日期。
- **数据流**:
    1. **用户档案**: 获取生肖、干支。
    2. **时间服务 (`TimeConvertService`)**: 计算农历、节气（如立春）、节日。
    3. **LLM生成**: 融合特征，生成结构化 JSON。
- **输出**: `DailyFortune` 对象（包含评分、宜忌、幸运色/数/位、财运/事业/感情建议）。
- **前端**: 独立的 `DailyFortuneDisplay` 卡片组件。

### 3.2 随时占卜 (Quick Divination)
- **东方版**: 摇钱起卦（六爻），支持后天八卦方位引导。
- **西方版**: 塔罗抽牌（单牌/三牌/十字阵），支持洗牌动画。

### 3.3 用户档案 (User Profile)
- **农历转换**: 用户更新生日时，自动调用 `calendar.js` 逻辑转换为农历（年/月/日/闰/干支/生肖）。
- **数据一致性**: 确保公历与农历信息同步更新。

---

## 4. 数据模型 (Data Models)

### 4.1 预处理响应
```go
type PreprocessResponse struct {
    OriginalQuestion string `json:"original_question"`
    EnhancedQuestion string `json:"enhanced_question"`
    Intent           string `json:"intent"` // binary_choice, daily_luck, etc.
}
```

### 4.2 每日运势
```go
type DailyFortune struct {
    Score     int      `json:"score"`
    Summary   string   `json:"summary"`
    Yi        []string `json:"yi"`
    Ji        []string `json:"ji"`
    LuckyColor string  `json:"lucky_color"`
    // ...更多字段
    SolarTerm string   `json:"solar_term"` // 节气背景
}
```

---

## 5. 版本差异化 (Version Strategy)

| 特性 | 国内版 (CN) | 国际版 (Global) |
| :--- | :--- | :--- |
| **核心算法** | 周易六爻、八字 | 韦特塔罗、占星 |
| **UI 风格** | 新中式、水墨 | 神秘主义、星空 |
| **结果导向** | 吉凶判断、具体宜忌 | 心理暗示、行动指引 |
