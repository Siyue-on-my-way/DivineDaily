# DivineDaily - 技术实现参考 (Technical Reference)

## 1. 技术栈 (Tech Stack)
- **Backend**: Go (Gin, GORM), Python (Mem0 Service)
- **Frontend**: React 19, Vite, TypeScript
- **Database**: PostgreSQL (Business Data), Milvus (Vector Data)
- **LLM Integration**: OpenAI/Doubao API (via Database Configuration)

---

## 2. 核心算法实现 (Core Algorithms)

### 2.1 周易六爻 (Six Lines / I Ching)
**文件**: `internal/service/iching.go`
- **生成逻辑**: 模拟三枚铜钱抛掷 6 次。
- **概率分布**:
    - 老阳 (O): 3背面 (1/8) -> 变爻
    - 少阳 (I): 1背面 (3/8) -> 不变
    - 少阴 (--): 2背面 (3/8) -> 不变
    - 老阴 (X): 0背面 (1/8) -> 变爻
- **卦象解析**:
    - 存储 64 卦完整数据（卦名、卦辞、上/下卦、五行）。
    - 支持变卦计算：根据变爻位置推导之卦。

### 2.2 塔罗牌 (Tarot)
**文件**: `internal/service/tarot_service.go`
- **数据结构**: 78 张标准韦特塔罗牌（22 大阿卡纳 + 56 小阿卡纳）。
- **抽牌算法**:
    - 基于 Fisher-Yates 洗牌算法。
    - 随机决定正逆位 (`IsReversed`)。
    - `SessionID` 作为随机种子一部分，确保会话内结果可复现（如果需要）。

### 2.3 农历与时间转换 (Time Conversion)
**文件**: `internal/service/time_convert_service.go`
- **核心逻辑**: 移植/封装 `calendar.js` 的算法。
- **功能**:
    - `Solar2Lunar`: 公历转农历。
    - `GetSolarTerm`: 计算精确节气（精确到分）。
    - `GetDailyInfo`: 获取当日的干支、生肖、节日。

---

## 3. 服务架构细节 (Service Details)

### 3.1 意图路由 (Intent Routing)
**文件**: `internal/service/divination.go`
- 在 `StartDivination` 中，根据 `req.Intent` 进行 switch-case 分发。
- `model.IntentDailyLuck` -> `dailyFortuneSvc.GenerateDailyFortune`
- `model.IntentBinaryChoice` -> `processDecisionQuestion` (六爻起卦)

### 3.2 每日运势生成 (Daily Fortune)
**文件**: `internal/service/daily_fortune_service.go`
1.  **Context Assembly**: 聚合 UserProfile (生肖) + Time (节气)。
2.  **Prompt Building**: 动态插入上述信息到 System Prompt。
3.  **LLM Call**: 请求 LLM 生成 JSON 格式。
4.  **Parsing**: 清洗 JSON 字符串（处理 Markdown 代码块包裹），反序列化为 `DailyFortune`。

---

## 4. 数据库设计 (Database Schema)

### `divination_sessions`
存储一次完整的占卜会话。
- `id`: UUID
- `intent`: 意图类型
- `question`: 用户原始问题
- `result_summary`: 简短结论
- `result_detail`: 完整报告

### `daily_fortunes`
存储每日运势记录，避免同一天重复生成。
- `user_id`: 关联用户
- `date`: 日期 (YYYY-MM-DD)
- `score`: 评分
- `content`: 完整 JSON 内容

### `users`
- `birth_date`: 公历生日
- `lunar_info`: JSON (存储转换后的农历信息)

---

## 5. 接口规范 (API Reference)

### POST `/api/v1/divinations/start`
创建占卜会话。
- **Req**: `{ "question": "...", "intent": "daily_luck" }`
- **Res**: `{ "session_id": "...", "result": { ... } }`

### GET `/api/v1/divinations/{id}/result`
获取占卜结果（轮询或重新加载）。

### POST `/api/v1/daily_fortune`
直接获取每日运势（快捷入口）。
- **Req**: `{ "user_id": "...", "date": "2026-02-04" }`
