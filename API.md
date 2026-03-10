# DivineDaily - API 参考文档

## 基础信息

**Base URL**: `http://localhost:48080/api/v1`

**认证方式**: JWT Bearer Token

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

---

## 认证接口

### 1. 用户注册

**POST** `/auth/register`

**请求体**:
```json
{
  "username": "user@example.com",
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "role": "normal",
  "created_at": "2026-02-22T10:00:00Z"
}
```

### 2. 用户登录

**POST** `/auth/login`

**请求体**:
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "role": "normal"
  }
}
```

### 3. 获取当前用户

**GET** `/auth/me`

**响应**:
```json
{
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "role": "normal",
  "created_at": "2026-02-22T10:00:00Z"
}
```

---

## 占卜接口

### 1. 开始占卜

**POST** `/divinations/start`

**请求体**:
```json
{
  "question": "今天运势如何？",
  "version": "CN",
  "event_type": "fortune",
  "spread": "single"
}
```

**参数说明**:
- `question`: 占卜问题（必填）
- `version`: 版本（CN=周易, TAROT=塔罗）
- `event_type`: 事件类型（decision/career/relationship/fortune/knowledge）
- `spread`: 牌阵类型（single/three/cross，仅塔罗）
- `context`: 扩展上下文（可选）
  - 塔罗推荐传递 `context.tarot_interaction`
  - 示例：
    ```json
    {
      "tarot_interaction": {
        "spread": "three",
        "cut_position": 63,
        "shuffle_trace": [45, 52, 61, 63, 58]
      }
    }
    ```
  - 用途：让用户“洗牌/切牌”交互参与随机种子计算，使抽牌结果更具参与感且可复现

**响应**:
```json
{
  "session_id": "uuid",
  "outcome": "吉",
  "title": "天风姤",
  "summary": "运势良好，诸事顺利...",
  "detail": "# 卦象解析\n...",
  "hexagram_info": {
    "number": 44,
    "name": "天风姤",
    "upper_trigram": "乾",
    "lower_trigram": "巽",
    "wuxing": "金",
    "changing_lines": [2, 5]
  },
  "cards": null,
  "recommendations": ["保持积极心态", "注意人际关系"],
  "daily_fortune": null,
  "needs_follow_up": false,
  "created_at": "2026-02-22T10:00:00Z"
}
```

### 2. 获取占卜结果

**GET** `/divinations/{session_id}`

**响应**: 同上

### 3. 获取占卜历史

**GET** `/divinations/history`

**查询参数**:
- `limit`: 每页数量（默认 20，最大 100）
- `offset`: 偏移量（默认 0）
- `event_type`: 事件类型过滤
- `version`: 版本过滤
- `status`: 状态过滤
- `start_date`: 开始日期（YYYY-MM-DD）
- `end_date`: 结束日期（YYYY-MM-DD）
- `order_by`: 排序字段（created_at/updated_at）
- `order_direction`: 排序方向（asc/desc）

**响应**:
```json
{
  "sessions": [
    {
      "id": "uuid",
      "question": "今天运势如何？",
      "version": "CN",
      "outcome": "吉",
      "summary": "运势良好...",
      "created_at": "2026-02-22T10:00:00Z"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

### 4. 获取占卜统计

**GET** `/divinations/stats`

**响应**:
```json
{
  "total_count": 100,
  "by_type": {
    "decision": 30,
    "fortune": 50,
    "relationship": 20
  },
  "by_version": {
    "CN": 70,
    "TAROT": 30
  },
  "by_status": {
    "completed": 95,
    "pending": 5
  }
}
```

---

## 每日运势接口

### 1. 获取每日运势

**POST** `/daily_fortune`

**请求体**:
```json
{
  "date": "2026-02-22"
}
```

**响应**:
```json
{
  "overall_score": 85,
  "wealth_score": 75,
  "career_score": 90,
  "love_score": 80,
  "health_score": 85,
  "content": "【综合运势 85分】\n今日运势极佳...",
  "lucky_color": "绿色",
  "lucky_number": 8,
  "lucky_direction": "东",
  "lucky_time": "辰时(07:00-09:00)",
  "yi": "出行,开业,会友,签约",
  "ji": "加班,动土",
  "solar_term": "立春",
  "festival": "春节"
}
```

### 2. 获取运势历史

**GET** `/daily_fortune/history`

**查询参数**:
- `limit`: 每页数量（默认 30）
- `offset`: 偏移量（默认 0）

**响应**:
```json
{
  "fortunes": [
    {
      "date": "2026-02-22",
      "overall_score": 85,
      "summary": "今日运势极佳...",
      "lucky_color": "绿色"
    }
  ],
  "total": 30
}
```

---

## 用户档案接口

### 1. 获取用户档案

**GET** `/user_profile`

**响应**:
```json
{
  "user_id": 1,
  "birth_date": "1990-05-15",
  "lunar_birth_date": "1990-04-21",
  "animal": "马",
  "zodiac_sign": "金牛座",
  "ganzhi_year": "庚午",
  "created_at": "2026-02-22T10:00:00Z",
  "updated_at": "2026-02-22T10:00:00Z"
}
```

### 2. 更新用户档案

**PUT** `/user_profile`

**请求体**:
```json
{
  "birth_date": "1990-05-15"
}
```

**响应**: 同上

---

## 时间转换接口

### 1. 公历转农历

**POST** `/time_convert/solar_to_lunar`

**请求体**:
```json
{
  "year": 2026,
  "month": 2,
  "day": 22
}
```

**响应**:
```json
{
  "lunar_year": 2026,
  "lunar_month": 1,
  "lunar_day": 5,
  "lunar_month_cn": "正月",
  "lunar_day_cn": "初五",
  "is_leap": false,
  "ganzhi_year": "丙午",
  "ganzhi_month": "庚寅",
  "ganzhi_day": "甲子",
  "animal": "马",
  "zodiac_sign": "双鱼座",
  "term": "立春",
  "festival": "",
  "lunar_festival": "春节"
}
```

### 2. 获取每日信息

**POST** `/time_convert/daily_info`

**请求体**:
```json
{
  "date": "2026-02-22"
}
```

**响应**: 同上

---

## 管理接口（需要 admin 权限）

### 1. 获取 LLM 配置列表

**GET** `/admin/llm_configs`

**响应**:
```json
{
  "configs": [
    {
      "id": 1,
      "name": "DeepSeek",
      "provider": "deepseek",
      "model_name": "deepseek-chat",
      "is_enabled": true,
      "is_default": true,
      "created_at": "2026-02-22T10:00:00Z"
    }
  ]
}
```

### 2. 创建 LLM 配置

**POST** `/admin/llm_configs`

**请求体**:
```json
{
  "name": "DeepSeek",
  "provider": "deepseek",
  "endpoint": "https://api.deepseek.com/v1/chat/completions",
  "api_key": "your-api-key",
  "model_name": "deepseek-chat",
  "is_enabled": true,
  "is_default": true,
  "extra_config": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

### 3. 获取 Prompt 配置列表

**GET** `/admin/prompt_configs`

**响应**:
```json
{
  "configs": [
    {
      "id": 1,
      "name": "每日运势解读",
      "scene": "daily_fortune",
      "prompt_type": "answer",
      "template": "你是一位精通命理的大师...",
      "llm_config_id": 1,
      "temperature": 0.7,
      "max_tokens": 2000,
      "is_enabled": true
    }
  ]
}
```

### 4. 创建 Prompt 配置

**POST** `/admin/prompt_configs`

**请求体**:
```json
{
  "name": "每日运势解读",
  "scene": "daily_fortune",
  "prompt_type": "answer",
  "template": "你是一位精通命理的大师...",
  "llm_config_id": 1,
  "temperature": 0.7,
  "max_tokens": 2000,
  "timeout_seconds": 30,
  "is_enabled": true
}
```

---

## 错误响应

所有接口在出错时返回统一格式：

```json
{
  "detail": "错误信息"
}
```

**常见状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器错误

---

## 数据类型定义

### DivinationResult

```typescript
interface DivinationResult {
  session_id: string;
  outcome?: string;                 // 吉凶判断
  title?: string;                   // 卦名或标题
  summary: string;                  // 摘要
  detail: string;                   // 详细解读
  hexagram_info?: HexagramInfo;     // 卦象信息（周易）
  cards?: TarotCard[];              // 牌面信息（塔罗）
  recommendations?: string[];       // 建议
  daily_fortune?: DailyFortuneInfo; // 每日运势
  yarrow_trace?: YarrowProcessTrace;// 大衍筮法起卦过程（仅周易）
  needs_follow_up: boolean;
  created_at: string;
}
```

### HexagramInfo

```typescript
interface HexagramInfo {
  number: number;             // 卦序号（1-64）
  name: string;               // 卦名
  upper_trigram: string;      // 上卦
  lower_trigram: string;      // 下卦
  wuxing: string;             // 五行
  changing_lines: number[];   // 变爻位置（0-5，自下而上）
  line_values?: number[];     // 六爻值（自下而上，6/7/8/9）
  outcome: string;            // 吉凶
  summary: string;            // 卦辞
  detail: string;             // 详细解释
}
```

### YarrowProcessTrace（大衍筮法起卦过程）

```typescript
interface YarrowChangeStep {
  step_index: number;              // 第几变（1-3）
  stalks_before: number;           // 本变开始前蓍草数
  left_pile: number;               // 左手蓍草数
  right_pile_before_hang: number;  // 右手蓍草数（挂一前）
  right_hang_one: number;          // 挂一数量，固定为1
  right_pile_after_hang: number;   // 右手蓍草数（挂一后）
  left_remainder: number;          // 左手取四余数（0按4计）
  right_remainder: number;         // 右手取四余数（0按4计）
  removed: number;                 // 本次去除总数
  stalks_after: number;            // 本变结束后蓍草数
}

interface YarrowLineTrace {
  line_index: number;              // 爻位（1-6，自下而上）
  initial_stalks: number;          // 初始蓍草数（通常49）
  changes: YarrowChangeStep[];     // 三变过程
  final_stalks: number;            // 三变后剩余蓍草数
  line_value: number;              // 爻值（6/7/8/9）
  line_type: string;               // 爻类型（老阴/少阳/少阴/老阳）
  is_changing: boolean;            // 是否变爻
}

interface YarrowProcessTrace {
  method: string;                  // 起卦方法，固定为 "dayan_yarrow"
  total_stalks: number;            // 总蓍草数（50）
  effective_stalks: number;        // 参与演算蓍草数（49）
  lines: YarrowLineTrace[];        // 六爻过程（自下而上）
}
```

### TarotCard

```typescript
interface TarotCard {
  name: string;               // 牌名
  name_en: string;            // 英文名
  position: string;           // 位置（过去/现在/未来）
  is_reversed: boolean;       // 是否逆位
  meaning: string;            // 含义
}
```

### DailyFortuneInfo

```typescript
interface DailyFortuneInfo {
  overall_score: number;      // 综合评分（0-100）
  wealth_score: number;       // 财运评分
  career_score: number;       // 事业评分
  love_score: number;         // 感情评分
  health_score: number;       // 健康评分
  content: string;            // 运势内容
  lucky_color: string;        // 幸运色
  lucky_number: number;       // 幸运数字
  lucky_direction: string;    // 幸运方位
  lucky_time: string;         // 幸运时辰
  yi: string;                 // 宜（逗号分隔）
  ji: string;                 // 忌（逗号分隔）
  solar_term: string;         // 节气
  festival: string;           // 节日
}
```

---

## 使用示例

### JavaScript/TypeScript

```typescript
// 登录
const loginResponse = await fetch('http://localhost:48080/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: '594120'
  })
});
const { access_token } = await loginResponse.json();

// 开始占卜
const divinationResponse = await fetch('http://localhost:48080/api/v1/divinations/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    question: '今天运势如何？',
    version: 'CN'
  })
});
const result = await divinationResponse.json();
console.log(result);
```

### Python

```python
import requests

# 登录
login_response = requests.post(
    'http://localhost:48080/api/v1/auth/login',
    json={'username': 'admin', 'password': '594120'}
)
token = login_response.json()['access_token']

# 开始占卜
divination_response = requests.post(
    'http://localhost:48080/api/v1/divinations/start',
    headers={'Authorization': f'Bearer {token}'},
    json={'question': '今天运势如何？', 'version': 'CN'}
)
result = divination_response.json()
print(result)
```

### cURL

```bash
# 登录
TOKEN=$(curl -X POST 'http://localhost:48080/api/v1/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"594120"}' \
  | jq -r '.access_token')

# 开始占卜
curl -X POST 'http://localhost:48080/api/v1/divinations/start' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"question":"今天运势如何？","version":"CN"}'
```

---

## 在线文档

访问 Swagger UI 查看交互式 API 文档：

**URL**: http://localhost:48080/docs

在 Swagger UI 中可以：
- 查看所有接口
- 测试接口调用
- 查看请求/响应示例
- 下载 OpenAPI 规范

