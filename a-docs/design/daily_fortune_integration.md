# 智能意图驱动占卜与每日运势集成设计文档

## 1. 概述
本项目旨在打造一个能够理解多样化用户提问（如二选一决策、每日运势、深度咨询等）的智能占卜系统。通过引入意图识别和个性化运势生成机制，结合中国传统历法（节气、节日）与用户个人档案（生肖、八字），提供精准且富有文化底蕴的解答。

## 2. 核心架构改进

### 2.1 意图识别系统 (Intelligent Intent Classification)
在用户提问预处理阶段，系统根据问题内容自动分类意图：
- **binary_choice (决策类)**: 
  - 场景：用户面临两个或多个选项的抉择（如“往左走还是往右走”、“选A offer还是B offer”）。
  - 处理：使用六爻卦象或塔罗牌阵进行推演，给出明确的吉凶判断。
- **daily_luck (运势类)**:
  - 场景：询问今日运气、穿搭颜色、幸运数字等（如“今天穿什么颜色运气好”、“今日运势如何”）。
  - 处理：路由至 `DailyFortuneService`，生成包含评分、宜忌、幸运指南的综合报告。
- **deep_analysis (深度分析类)**:
  - 场景：复杂的感情、事业困惑，需要长篇分析。
  - 处理：调用大模型结合RAG（检索增强生成）进行深度解读。
- **knowledge (知识问答类)**:
  - 场景：关于玄学知识的咨询。
  - 处理：直接检索知识库回答。

### 2.2 每日运势深度集成 (Daily Fortune Integration)
为了满足“每日运势”这一高频需求，设计了独立的 `DailyFortuneService`。

#### 数据流
1. **输入**: 用户ID + 当前日期。
2. **上下文获取**:
   - **用户档案**: 获取出生日期，计算生肖、干支（用于个性化匹配）。
   - **时间服务 (`TimeConvertService`)**: 计算当日的农历日期、节气（如立春、清明）、传统节日（如春节、中秋）。
3. **LLM生成**: 
   - 构建Prompt，融合用户特征与时间特征。
   - 要求LLM输出结构化JSON数据。
4. **输出**: `DailyFortune` 对象。

#### 数据结构
```go
type DailyFortune struct {
    Score   int    // 综合评分 (0-100)
    Summary string // 核心短评
    
    // 详细运势
    Wealth string // 财运
    Career string // 事业
    Love   string // 感情
    Health string // 健康
    
    // 幸运指南
    LuckyColor     string
    LuckyNumber    string
    LuckyDirection string
    LuckyTime      string
    
    // 宜忌
    Yi []string
    Ji []string
    
    // 背景信息
    SolarTerm string // 节气
    Festival  string // 节日
}
```

## 3. 实现细节

### 3.1 后端服务拆分
- **`TimeConvertService`**: 封装 `solar2lunar` 逻辑，提供 `GetDailyInfo` 接口，确保节气和节日计算准确。
- **`DailyFortuneService`**: 核心业务层，负责组装Prompt、调用LLM、解析结果。
- **`DivinationService`**: 改造 `StartDivination` 方法，根据预处理识别的 `Intent` 进行路由分发。若 Intent 为 `daily_luck`，直接调用 `DailyFortuneService`。

### 3.2 前端展示优化
- **`DailyFortuneDisplay` 组件**: 
  - 独立的视觉卡片。
  - 顶部展示评分与节气标签。
  - 网格化展示幸运色、数字等关键信息。
  - 清晰的“宜/忌”列表。
  - 折叠/展开的详细运势解读。
- **集成策略**: 在 `DivinationResultCard` 中，根据 `daily_fortune` 字段的存在与否，动态渲染运势卡片，替代通用的文本详情。

## 4. 后续规划
- **Phase 1 (已完成)**: 每日运势后端逻辑与前端基础展示。
- **Phase 2 (待办)**: 引入更丰富的排盘算法（如紫微斗数流日）辅助LLM生成。
- **Phase 3 (待办)**: 增加用户反馈机制，根据用户对运势的准确度反馈调整Prompt策略。
