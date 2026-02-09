# 用户认证系统 API 文档

## 概述

本文档描述了 Divine Daily 用户认证系统的 API 接口。

**Base URL**: `http://your-domain.com/api/v1`

**认证方式**: JWT Bearer Token

---

## 接口列表

### 1. 用户注册

**接口**: `POST /auth/register`

**描述**: 用户注册接口，支持邮箱或手机号注册

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "phone": "13800138000",
  "password": "password123",
  "confirm_password": "password123"
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，3-50个字符，只能包含字母、数字、下划线 |
| email | string | 否* | 邮箱地址 |
| phone | string | 否* | 手机号（中国大陆） |
| password | string | 是 | 密码，6-32个字符 |
| confirm_password | string | 是 | 确认密码，必须与 password 一致 |

*注：email 和 phone 至少提供一个

**成功响应** (200):
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "phone": "13800138000"
    }
  }
}
```

**错误响应**:
- 400 Bad Request: 参数错误
  ```json
  {
    "code": 400,
    "message": "用户名已被占用"
  }
  ```
- 400 Bad Request: 邮箱已注册
  ```json
  {
    "code": 400,
    "message": "邮箱已被注册"
  }
  ```

---

### 2. 用户登录

**接口**: `POST /auth/login`

**描述**: 用户登录接口，支持用户名/邮箱/手机号登录

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名/邮箱/手机号 |
| password | string | 是 | 密码 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

**错误响应**:
- 401 Unauthorized: 凭证错误
  ```json
  {
    "code": 401,
    "message": "用户名或密码错误"
  }
  ```
- 403 Forbidden: 账号被禁用
  ```json
  {
    "code": 403,
    "message": "账号已被禁用"
  }
  ```

---

### 3. 获取当前用户信息

**接口**: `GET /auth/me`

**描述**: 获取当前登录用户的信息

**请求头**:
```
Authorization: Bearer {token}
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "avatar": "https://example.com/avatar.jpg",
    "nickname": "测试用户"
  }
}
```

**错误响应**:
- 401 Unauthorized: 未授权
  ```json
  {
    "code": 401,
    "message": "未授权"
  }
  ```

---

### 4. 刷新 Token

**接口**: `POST /auth/refresh`

**描述**: 使用 Refresh Token 刷新访问 Token

**请求头**:
```
Authorization: Bearer {refresh_token}
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "Token 刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**错误响应**:
- 401 Unauthorized: Token 无效
  ```json
  {
    "code": 401,
    "message": "Token 刷新失败"
  }
  ```

---

### 5. 用户登出

**接口**: `POST /auth/logout`

**描述**: 用户登出接口

**请求头**:
```
Authorization: Bearer {token}
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "登出成功"
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### cURL 示例

**注册**:
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

**登录**:
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

**获取用户信息**:
```bash
curl -X GET http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 安全建议

1. **HTTPS**: 生产环境必须使用 HTTPS
2. **Token 存储**: 前端应将 Token 存储在 localStorage 或 sessionStorage
3. **Token 刷新**: Token 过期前应主动刷新
4. **密码强度**: 建议用户使用强密码
5. **限流**: 建议对登录接口进行限流保护

---

## 数据库迁移

执行以下 SQL 创建用户表：

```bash
mysql -u root -p divinedaily < migrations/001_create_users_table.sql
```

或使用 GORM 自动迁移：

```go
db.AutoMigrate(&model.User{}, &model.UserSession{})
```

---

## 环境变量配置

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

必须配置的环境变量：
- `JWT_SECRET`: JWT 密钥（生产环境必须修改）
- `DB_PASSWORD`: 数据库密码
- `DB_NAME`: 数据库名称

---

## 测试

运行单元测试：

```bash
go test ./pkg/validator/...
go test ./pkg/crypto/...
```

---

## 更新日志

### v1.0.0 (2024-02-07)
- 实现用户注册功能
- 实现用户登录功能
- 实现 JWT Token 认证
- 实现密码加密存储
- 添加输入验证
