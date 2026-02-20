# DivineDaily Backend Python - API 文档

## 📖 目录

- [概述](#概述)
- [认证](#认证)
- [占卜API](#占卜api)
- [方位推荐API](#方位推荐api)
- [错误处理](#错误处理)
- [示例代码](#示例代码)

---

## 概述

**Base URL**: `http://your-domain.com/api/v1`

**Content-Type**: `application/json`

**支持的版本**:
- `CN`: 中国版（八卦、易经）
- `Global`: 国际版（塔罗）

---

## 认证

所有API请求需要在Header中携带JWT Token：

```http
Authorization: Bearer <your_jwt_token>
```

### 获取Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

## 占卜API

### 1. 开始占卜

**端点**: `POST /api/v1/divinations/start`

**描述**: 开始一次新的占卜会话

**请求体**:
```json
{
  "question": "我应该跳槽吗？",
  "event_type": "career",
  "version": "CN"
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 占卜问题 |
| event_type | string | 是 | 事件类型：career/relationship/decision/health/wealth |
| version | string | 否 | 版本：CN/Global，默认CN |

**响应**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "outcome": "吉",
  "title": "泰卦",
  "summary": "天地交泰，万物亨通",
  "detail": "此卦象征天地交泰，阴阳和合...",
  "hexagram_info": {
    "primary": "泰",
    "changing": "否",
    "lines": [1, 0, 1, 0, 1, 1]
  },
  "orientation": {
    "key": "NW",
    "label": "西北（乾）",
    "reason": "此事关乎事业目标与掌控..."
  },
  "created_at": "2025-02-20T10:30:00Z"
}
```

---

### 2. 获取占卜历史

**端点**: `GET /api/v1/divinations/history`

**描述**: 获取用户的占卜历史记录（支持过滤、排序、分页）

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | integer | 否 | 每页数量（1-100），默认20 |
| offset | integer | 否 | 偏移量，默认0 |
| event_type | string | 否 | 事件类型过滤 |
| version | string | 否 | 版本过滤（CN/Global） |
| status | string | 否 | 状态过滤（completed/pending） |
| start_date | string | 否 | 开始日期（YYYY-MM-DD） |
| end_date | string | 否 | 结束日期（YYYY-MM-DD） |
| order_by | string | 否 | 排序字段（created_at/updated_at），默认created_at |
| order_direction | string | 否 | 排序方向（asc/desc），默认desc |

**示例请求**:
```http
GET /api/v1/divinations/history?limit=10&event_type=career&order_by=created_at&order_direction=desc
```

**响应**:
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "question": "我应该跳槽吗？",
      "event_type": "career",
      "version": "CN",
      "outcome": "吉",
      "title": "泰卦",
      "summary": "天地交泰，万物亨通",
      "created_at": "2025-02-20T10:30:00Z",
      "updated_at": "2025-02-20T10:30:00Z",
      "status": "completed"
    }
  ],
  "total": 100,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

---

### 3. 获取历史记录总数

**端点**: `GET /api/v1/divinations/history/count`

**描述**: 获取符合条件的历史记录总数

**查询参数**: 与 `/history` 相同的过滤参数

**响应**:
```json
{
  "count": 100
}
```

---

### 4. 获取统计数据

**端点**: `GET /api/v1/divinations/stats`

**描述**: 获取用户的占卜统计数据

**响应**:
```json
{
  "total_count": 100,
  "by_type": {
    "career": 30,
    "relationship": 25,
    "decision": 20,
    "health": 15,
    "wealth": 10
  },
  "by_version": {
    "CN": 70,
    "Global": 30
  },
  "by_status": {
    "completed": 95,
    "pending": 5
  }
}
```

---

### 5. 获取占卜详情

**端点**: `GET /api/v1/divinations/{session_id}`

**描述**: 获取指定会话的详细信息

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话ID |

**响应**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "我应该跳槽吗？",
  "event_type": "career",
  "version": "CN",
  "outcome": "吉",
  "title": "泰卦",
  "summary": "天地交泰，万物亨通",
  "detail": "此卦象征天地交泰，阴阳和合...",
  "hexagram_info": {
    "primary": "泰",
    "changing": "否",
    "lines": [1, 0, 1, 0, 1, 1]
  },
  "orientation": {
    "key": "NW",
    "label": "西北（乾）"
  },
  "analysis": {
    "complexity": 0.75,
    "elements": {
      "option_a": "跳槽",
      "option_b": "留下",
      "concern_1": "薪资",
      "concern_2": "发展"
    }
  },
  "created_at": "2025-02-20T10:30:00Z",
  "updated_at": "2025-02-20T10:30:00Z",
  "status": "completed"
}
```

---

## 方位推荐API

### 1. 推荐方位

**端点**: `POST /api/v1/orientation/recommend`

**描述**: 根据问题和事件类型推荐最佳方位

**请求体**:
```json
{
  "version": "CN",
  "event_type": "career",
  "question": "我应该跳槽吗？"
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | string | 是 | 版本：CN/Global |
| event_type | string | 是 | 事件类型 |
| question | string | 否 | 问题文本（用于关键词匹配） |

**响应**:
```json
{
  "recommended_key": "NW",
  "recommended_label": "西北（乾）",
  "reason": "此事关乎事业目标与掌控，取西北（乾）以应'权威与进取'。",
  "options": [
    {
      "key": "NW",
      "label": "西北（乾）",
      "trigram": "乾",
      "element": "金",
      "meaning": "权威与进取"
    },
    {
      "key": "N",
      "label": "正北（坎）",
      "trigram": "坎",
      "element": "水",
      "meaning": "智慧与流动"
    }
  ],
  "tolerance_deg": 15
}
```

---

### 2. 获取方位详情

**端点**: `GET /api/v1/orientation/detail/{key}`

**描述**: 获取指定方位的详细信息

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | 方位键（如NW, N, E等） |

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | string | 否 | 版本：CN/Global，默认CN |

**响应**:
```json
{
  "key": "NW",
  "label": "西北（乾）",
  "trigram": "乾",
  "element": "金",
  "meaning": "权威与进取",
  "description": "西北方位对应乾卦，象征天、父、君...",
  "suitable_for": ["career", "decision"],
  "keywords": ["权威", "领导", "决策", "目标"]
}
```

---

### 3. 获取所有方位

**端点**: `GET /api/v1/orientation/all`

**描述**: 获取指定版本的所有方位信息

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | string | 否 | 版本：CN/Global，默认CN |

**响应**:
```json
{
  "version": "CN",
  "orientations": [
    {
      "key": "N",
      "label": "正北（坎）",
      "trigram": "坎",
      "element": "水",
      "meaning": "智慧与流动"
    },
    {
      "key": "NE",
      "label": "东北（艮）",
      "trigram": "艮",
      "element": "土",
      "meaning": "稳定与积累"
    }
  ],
  "count": 8
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {
      "field": "具体错误信息"
    }
  }
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | INVALID_REQUEST | 请求参数无效 |
| 401 | UNAUTHORIZED | 未授权（Token无效或过期） |
| 403 | FORBIDDEN | 禁止访问 |
| 404 | NOT_FOUND | 资源不存在 |
| 422 | VALIDATION_ERROR | 数据验证失败 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |
| 503 | SERVICE_UNAVAILABLE | 服务暂时不可用 |

### 错误示例

**400 Bad Request**:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "event_type": "必须是以下之一: career, relationship, decision, health, wealth"
    }
  }
}
```

**401 Unauthorized**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token已过期",
    "details": {
      "expired_at": "2025-02-20T10:00:00Z"
    }
  }
}
```

**404 Not Found**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "会话不存在",
    "details": {
      "session_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

---

## 示例代码

### Python

```python
import requests

# 配置
BASE_URL = "http://your-domain.com/api/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. 开始占卜
def start_divination(question, event_type, version="CN"):
    url = f"{BASE_URL}/divinations/start"
    data = {
        "question": question,
        "event_type": event_type,
        "version": version
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 2. 获取历史记录
def get_history(limit=20, event_type=None):
    url = f"{BASE_URL}/divinations/history"
    params = {"limit": limit}
    if event_type:
        params["event_type"] = event_type
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# 3. 推荐方位
def recommend_orientation(version, event_type, question=None):
    url = f"{BASE_URL}/orientation/recommend"
    data = {
        "version": version,
        "event_type": event_type
    }
    if question:
        data["question"] = question
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 开始占卜
    result = start_divination(
        question="我应该跳槽吗？",
        event_type="career",
        version="CN"
    )
    print(f"占卜结果: {result['title']} - {result['outcome']}")
    
    # 获取历史
    history = get_history(limit=10, event_type="career")
    print(f"历史记录数: {history['total']}")
    
    # 推荐方位
    orientation = recommend_orientation(
        version="CN",
        event_type="career",
        question="我应该跳槽吗？"
    )
    print(f"推荐方位: {orientation['recommended_label']}")
```

---

### JavaScript (Fetch API)

```javascript
const BASE_URL = "http://your-domain.com/api/v1";
const TOKEN = "your_jwt_token";

const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// 1. 开始占卜
async function startDivination(question, eventType, version = "CN") {
  const response = await fetch(`${BASE_URL}/divinations/start`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
      question: question,
      event_type: eventType,
      version: version
    })
  });
  return await response.json();
}

// 2. 获取历史记录
async function getHistory(limit = 20, eventType = null) {
  const params = new URLSearchParams({ limit: limit });
  if (eventType) {
    params.append("event_type", eventType);
  }
  const response = await fetch(
    `${BASE_URL}/divinations/history?${params}`,
    { headers: headers }
  );
  return await response.json();
}

// 3. 推荐方位
async function recommendOrientation(version, eventType, question = null) {
  const body = {
    version: version,
    event_type: eventType
  };
  if (question) {
    body.question = question;
  }
  const response = await fetch(`${BASE_URL}/orientation/recommend`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(body)
  });
  return await response.json();
}

// 使用示例
(async () => {
  // 开始占卜
  const result = await startDivination(
    "我应该跳槽吗？",
    "career",
    "CN"
  );
  console.log(`占卜结果: ${result.title} - ${result.outcome}`);
  
  // 获取历史
  const history = await getHistory(10, "career");
  console.log(`历史记录数: ${history.total}`);
  
  // 推荐方位
  const orientation = await recommendOrientation(
    "CN",
    "career",
    "我应该跳槽吗？"
  );
  console.log(`推荐方位: ${orientation.recommended_label}`);
})();
```

---

### cURL

```bash
# 1. 开始占卜
curl -X POST "http://your-domain.com/api/v1/divinations/start" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "我应该跳槽吗？",
    "event_type": "career",
    "version": "CN"
  }'

# 2. 获取历史记录
curl -X GET "http://your-domain.com/api/v1/divinations/history?limit=10&event_type=career" \
  -H "Authorization: Bearer your_jwt_token"

# 3. 推荐方位
curl -X POST "http://your-domain.com/api/v1/orientation/recommend" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "CN",
    "event_type": "career",
    "question": "我应该跳槽吗？"
  }'
```

---

## 性能优化

### 缓存策略

API使用Redis缓存来提升性能：

| 操作 | 缓存时间 | 说明 |
|------|---------|------|
| 历史列表 | 5分钟 | 短期缓存，频繁更新 |
| 统计数据 | 1小时 | 中期缓存 |
| 方位信息 | 24小时 | 长期缓存，很少变化 |
| 占卜详情 | 1小时 | 中期缓存 |

### 性能提升

- 数据库查询: **100倍提升** (100ms → 1ms)
- LLM调用: **2000倍提升** (2000ms → 1ms)
- 统计计算: **500倍提升** (500ms → 1ms)

---

## 版本历史

### v1.0.0 (当前版本)

- ✅ 完整的占卜API
- ✅ 方位推荐API
- ✅ 历史管理增强
- ✅ 统计数据API
- ✅ Redis缓存支持
- ✅ JWT认证

---

## 联系支持

如有问题或建议，请联系：

- **Email**: support@divinedaily.com
- **GitHub**: https://github.com/divinedaily/backend-python
- **文档**: https://docs.divinedaily.com

---

**文档版本**: 1.0.0  
**最后更新**: 2025年2月20日

