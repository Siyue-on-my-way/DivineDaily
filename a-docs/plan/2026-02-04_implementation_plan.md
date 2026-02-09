# 2026-02-04 核心功能实现计划

根据项目优化分析报告及用户最新指令，制定以下实施计划，重点完成“每日运势”和“意图识别”两大核心功能。

## 目标
1.  **每日运势 (Daily Fortune)**: 深度集成 `calendar.js` 能力（节气、节日），结合用户档案生成个性化运势。
2.  **意图识别 (Intent Recognition)**: 恢复并完善智能预处理模块，实现对用户提问意图的自动分类（决策、运势、知识）。

---

## 📅 Phase 1: 每日运势深度集成 (Daily Fortune)

此阶段旨在打通时间维度的数据，让系统“感知”当前的农历、节气和节日。

### 1.1 扩展 TimeConvertService
**目标**: 提供完整的农历及节气/节日查询能力。
- **文件**: `/mnt/DivineDaily/backend/internal/service/time_convert_service.go`
- **任务**:
    - [ ] 集成 `calendar.js` 的节气计算逻辑（需移植或调用现有库）。
    - [ ] 实现 `GetSolarTerm(date)`: 返回当日或最近的节气。
    - [ ] 实现 `GetFestivals(date)`: 返回农历/公历节日。
    - [ ] 实现 `GetDailyInfo(date)`: 聚合农历、干支、节气、节日信息。

### 1.2 构建 DailyFortuneService
**目标**: 结合时间信息与用户档案，生成运势报告。
- **文件**: `/mnt/DivineDaily/backend/internal/service/daily_fortune_service.go` (新建)
- **任务**:
    - [ ] 定义 `DailyFortune` 结构体（包含宜忌、幸运色/方位、综合运势）。
    - [ ] 实现 `GenerateDailyFortune(userID, date)` 接口。
    - [ ] **Prompt 工程**: 设计 Prompt，将“用户八字 + 今日干支/节气 + 节日”输入给 LLM，生成运势。

### 1.3 集成到 DivinationService
**目标**: 让“运势类”问题能够调用 DailyFortuneService。
- **文件**: `/mnt/DivineDaily/backend/internal/service/divination.go`
- **任务**:
    - [ ] 在 `processRecommendationQuestion` (或新建 `processDailyLuck`) 中调用 `DailyFortuneService`。

---

## 🧠 Phase 2: 意图识别重构 (Intent Recognition)

此阶段旨在恢复被删除的智能预处理逻辑，并进行轻量化重构。

### 2.1 重建 IntelligentPreprocessingService
**目标**: 快速识别用户意图，无需调用 LLM（基于规则/关键词），降低延迟。
- **文件**: `/mnt/DivineDaily/backend/internal/service/intelligent_preprocessing_service.go` (重建)
- **任务**:
    - [ ] 实现 `ClassifyIntent(question)` 方法。
    - [ ] **规则定义**:
        - `IntentBinaryChoice`: 含“还是”、“要不要”、“选A选B”。
        - `IntentDailyLuck`: 含“运势”、“今天”、“幸运色”、“方位”。
        - `IntentKnowledge`: 含“是什么”、“含义”、“解释”。
        - `IntentDeepAnalysis`: 默认兜底。

### 2.2 恢复模型定义
**目标**: 恢复必要的数据结构。
- **文件**: `/mnt/DivineDaily/backend/internal/model/intelligent_preprocessing.go` (重建)
- **任务**:
    - [ ] 定义 `Intent` 常量。
    - [ ] 定义 `PreprocessResponse` 结构。

### 2.3 全链路集成
**目标**: 串联前端 -> 预处理 -> 占卜服务。
- **前端**:
    - [ ] 恢复 `DivinationPage.tsx` 中的预处理调用逻辑（可选，或直接在后端做隐式处理）。
    - [ ] *建议*: 为了简化用户体验，建议**后端自动识别**，前端只传问题，不再强制要求用户先点“预处理”。
- **后端**:
    - [ ] 在 `DivinationService.StartDivination` 中，如果前端未传 `intent`，则调用 `IntelligentPreprocessingService` 自动补全。

---

## 📝 执行步骤 (Execution Steps)

1.  **TimeConvertService 升级**: 移植/实现节气和节日算法。
2.  **DailyFortuneService 实现**: 编写服务层代码和 Prompt。
3.  **Intent 模块恢复**: 重建文件并实现关键词逻辑。
4.  **DivinationService 整合**: 将上述两部分接入主流程。
5.  **验证**: 使用测试用例验证“运势问答”和“决策问答”是否走了不同路径。
