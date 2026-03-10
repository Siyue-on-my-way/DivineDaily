# Divine Daily API 错误码文档

## 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "error_code": "1001",
  "message": "用户名或密码错误",
  "detail": "可选的详细错误信息"
}
```

---

## 错误码分类

### 1xxx - 认证错误

| 错误码 | 说明 | HTTP 状态码 | 中文消息 | 英文消息 |
|--------|------|-------------|----------|----------|
| 1001 | 用户名或密码错误 | 401 | 用户名或密码错误 | Invalid username or password |
| 1002 | 登录已过期 | 401 | 登录已过期，请重新登录 | Session expired, please login again |
| 1003 | 无效的令牌 | 401 | 无效的令牌 | Invalid token |
| 1004 | 账号已被禁用 | 403 | 账号已被禁用 | Account has been disabled |
| 1005 | 权限不足 | 403 | 权限不足 | Permission denied |

---

### 2xxx - 业务错误

#### 2001-2099 占卜相关

| 错误码 | 说明 | HTTP 状态码 | 中文消息 | 英文消息 |
|--------|------|-------------|----------|----------|
| 2001 | 占卜失败 | 500 | 占卜失败 | Divination failed |
| 2002 | 占卜会话不存在 | 404 | 占卜会话不存在 | Divination session not found |
| 2003 | 占卜尚未完成 | 400 | 占卜尚未完成 | Divination not completed yet |
| 2004 | 请输入问题 | 400 | 请输入问题 | Question is required |
| 2005 | 问题太短 | 400 | 问题太短，请详细描述 | Question is too short |
| 2006 | 问题太长 | 400 | 问题太长，请简化描述 | Question is too long |

#### 2101-2199 运势相关

| 错误码 | 说明 | HTTP 状态码 | 中文消息 | 英文消息 |
|--------|------|-------------|----------|----------|
| 2101 | 运势未生成 | 404 | 运势未生成 | Fortune not found |
| 2102 | 运势生成失败 | 500 | 运势生成失败 | Fortune generation failed |

#### 2201-2299 用户相关

| 错误码 | 说明 | HTTP 状态码 | 中文消息 | 英文消息 |
|--------|------|-------------|----------|----------|
| 2201 | 用户不存在 | 404 | 用户不存在 | User not found |
| 2202 | 用户已存在 | 409 | 用户已存在 | User already exists |

---

### 3xxx - 验证错误

| 错误码 | 说明 | HTTP 状态码 | 中文消息 | 英文消息 |
|--------|------|-------------|----------|----------|
| 3001 | 数据验证失败 | 400 | 数据验证失败 | Validation failed |
| 3002 | 邮箱格式不正确 | 400 | 邮箱格式不正确 | Invalid email format |
| 3003 | 手机号格式不正确 | 400 | 手机号格式不正确 | Invalid phone format |
| 3004 | 密码强度太弱 | 400 | 密码强度太弱 | Password is too weak |

---

### 5xxx - 系统错误

| 错误码 | 说明 | HTTP 状态码 | 中文消息 | 英文消息 |
|--------|------|-------------|----------|----------|
| 5001 | 服务器内部错误 | 500 | 服务器内部错误 | Internal server error |
| 5002 | 数据库错误 | 500 | 数据库错误 | Database error |
| 5003 | 网络错误 | 503 | 网络错误 | Network error |
| 5004 | 请求超时 | 504 | 请求超时 | Request timeout |
| 5005 | 服务暂时不可用 | 503 | 服务暂时不可用 | Service unavailable |

---

## 使用示例

### Python (后端)

```python
from app.core.error_codes import ErrorCode, APIError, get_error_message

# 抛出错误
raise APIError(ErrorCode.INVALID_CREDENTIALS, locale="zh_CN")

# 获取错误消息
message = get_error_message(ErrorCode.TOKEN_EXPIRED, locale="en_US")
# 返回: "Session expired, please login again"

# 自定义错误消息
raise APIError(ErrorCode.DIVINATION_FAILED, message="LLM 服务不可用")
```

### TypeScript (前端)

```typescript
// 处理错误响应
try {
  const response = await api.post('/api/v1/divinations', data);
} catch (error) {
  if (error.response?.data?.error_code) {
    const errorCode = error.response.data.error_code;
    const message = error.response.data.message;
    
    // 根据错误码处理
    switch (errorCode) {
      case '1002': // TOKEN_EXPIRED
        // 跳转到登录页
        router.push('/login');
        break;
      case '2004': // QUESTION_REQUIRED
        // 提示用户输入问题
        toast.error(message);
        break;
      case '5001': // INTERNAL_ERROR
        // 显示通用错误提示
        toast.error('服务器错误，请稍后重试');
        break;
      default:
        toast.error(message);
    }
  }
}
```

---

## 错误处理最佳实践

### 1. 后端统一错误处理

```python
from fastapi import HTTPException
from app.core.error_codes import ErrorCode, get_error_message

def raise_api_error(code: ErrorCode, locale: str = "zh_CN", detail: str = None):
    """抛出 API 错误"""
    message = get_error_message(code, locale)
    
    # 根据错误码确定 HTTP 状态码
    status_code_map = {
        "1xxx": 401,  # 认证错误
        "2xxx": 400,  # 业务错误
        "3xxx": 400,  # 验证错误
        "5xxx": 500,  # 系统错误
    }
    
    status_code = 400
    for prefix, code_status in status_code_map.items():
        if code.startswith(prefix[0]):
            status_code = code_status
            break
    
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": code,
            "message": message,
            "detail": detail
        }
    )
```

### 2. 前端统一错误处理

```typescript
// axios 拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    const errorCode = error.response?.data?.error_code;
    const message = error.response?.data?.message;
    
    // 全局错误处理
    if (errorCode === '1002' || errorCode === '1003') {
      // 令牌过期，跳转登录
      store.dispatch('logout');
      router.push('/login');
    } else if (errorCode?.startsWith('5')) {
      // 系统错误，显示通用提示
      toast.error('服务器错误，请稍后重试');
    } else {
      // 显示具体错误消息
      toast.error(message || '操作失败');
    }
    
    return Promise.reject(error);
  }
);
```

---

## 扩展错误码

如需添加新的错误码，请遵循以下规范：

1. **选择合适的分类**
   - 1xxx: 认证相关
   - 2xxx: 业务逻辑
   - 3xxx: 数据验证
   - 5xxx: 系统错误

2. **在 error_codes.py 中添加**
   ```python
   class ErrorCode(str, Enum):
       # ... 现有错误码 ...
       NEW_ERROR = "2999"  # 新错误码
   
   ERROR_MESSAGES = {
       # ... 现有消息 ...
       ErrorCode.NEW_ERROR: {
           "zh_CN": "中文错误消息",
           "en_US": "English error message"
       }
   }
   ```

3. **更新本文档**
   - 在对应分类表格中添加新错误码
   - 更新使用示例（如需要）

---

## 常见问题

### Q: 如何处理多语言错误消息？

A: 使用 `get_error_message(code, locale)` 函数，根据用户语言返回对应消息。

### Q: 前端如何知道用户的语言？

A: 从 localStorage 或 i18n 配置中获取当前语言，在请求时通过 `Accept-Language` 头传递。

### Q: 错误码会变化吗？

A: 已发布的错误码不会变化，保持向后兼容。新功能会添加新的错误码。

---

**文档版本**: 1.0.0  
**最后更新**: 2026-02-27  
**维护者**: Divine Daily Team
