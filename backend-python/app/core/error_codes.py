"""统一错误码定义"""

from enum import Enum
from typing import Dict


class ErrorCode(str, Enum):
    """错误码枚举"""
    
    # 认证错误 (1xxx)
    INVALID_CREDENTIALS = "1001"
    TOKEN_EXPIRED = "1002"
    TOKEN_INVALID = "1003"
    ACCOUNT_DISABLED = "1004"
    PERMISSION_DENIED = "1005"
    
    # 业务错误 (2xxx)
    DIVINATION_FAILED = "2001"
    DIVINATION_NOT_FOUND = "2002"
    DIVINATION_NOT_COMPLETED = "2003"
    QUESTION_REQUIRED = "2004"
    QUESTION_TOO_SHORT = "2005"
    QUESTION_TOO_LONG = "2006"
    
    FORTUNE_NOT_FOUND = "2101"
    FORTUNE_GENERATION_FAILED = "2102"
    
    USER_NOT_FOUND = "2201"
    USER_ALREADY_EXISTS = "2202"
    
    # 验证错误 (3xxx)
    VALIDATION_ERROR = "3001"
    INVALID_EMAIL = "3002"
    INVALID_PHONE = "3003"
    PASSWORD_TOO_WEAK = "3004"
    
    # 系统错误 (5xxx)
    INTERNAL_ERROR = "5001"
    DATABASE_ERROR = "5002"
    NETWORK_ERROR = "5003"
    TIMEOUT = "5004"
    SERVICE_UNAVAILABLE = "5005"


# 错误码对应的消息（支持国际化）
ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    ErrorCode.INVALID_CREDENTIALS: {
        "zh_CN": "用户名或密码错误",
        "en_US": "Invalid username or password"
    },
    ErrorCode.TOKEN_EXPIRED: {
        "zh_CN": "登录已过期，请重新登录",
        "en_US": "Session expired, please login again"
    },
    ErrorCode.TOKEN_INVALID: {
        "zh_CN": "无效的令牌",
        "en_US": "Invalid token"
    },
    ErrorCode.ACCOUNT_DISABLED: {
        "zh_CN": "账号已被禁用",
        "en_US": "Account has been disabled"
    },
    ErrorCode.PERMISSION_DENIED: {
        "zh_CN": "权限不足",
        "en_US": "Permission denied"
    },
    
    ErrorCode.DIVINATION_FAILED: {
        "zh_CN": "占卜失败",
        "en_US": "Divination failed"
    },
    ErrorCode.DIVINATION_NOT_FOUND: {
        "zh_CN": "占卜会话不存在",
        "en_US": "Divination session not found"
    },
    ErrorCode.DIVINATION_NOT_COMPLETED: {
        "zh_CN": "占卜尚未完成",
        "en_US": "Divination not completed yet"
    },
    ErrorCode.QUESTION_REQUIRED: {
        "zh_CN": "请输入问题",
        "en_US": "Question is required"
    },
    ErrorCode.QUESTION_TOO_SHORT: {
        "zh_CN": "问题太短，请详细描述",
        "en_US": "Question is too short"
    },
    ErrorCode.QUESTION_TOO_LONG: {
        "zh_CN": "问题太长，请简化描述",
        "en_US": "Question is too long"
    },
    
    ErrorCode.FORTUNE_NOT_FOUND: {
        "zh_CN": "运势未生成",
        "en_US": "Fortune not found"
    },
    ErrorCode.FORTUNE_GENERATION_FAILED: {
        "zh_CN": "运势生成失败",
        "en_US": "Fortune generation failed"
    },
    
    ErrorCode.USER_NOT_FOUND: {
        "zh_CN": "用户不存在",
        "en_US": "User not found"
    },
    ErrorCode.USER_ALREADY_EXISTS: {
        "zh_CN": "用户已存在",
        "en_US": "User already exists"
    },
    
    ErrorCode.VALIDATION_ERROR: {
        "zh_CN": "数据验证失败",
        "en_US": "Validation failed"
    },
    ErrorCode.INVALID_EMAIL: {
        "zh_CN": "邮箱格式不正确",
        "en_US": "Invalid email format"
    },
    ErrorCode.INVALID_PHONE: {
        "zh_CN": "手机号格式不正确",
        "en_US": "Invalid phone format"
    },
    ErrorCode.PASSWORD_TOO_WEAK: {
        "zh_CN": "密码强度太弱",
        "en_US": "Password is too weak"
    },
    
    ErrorCode.INTERNAL_ERROR: {
        "zh_CN": "服务器内部错误",
        "en_US": "Internal server error"
    },
    ErrorCode.DATABASE_ERROR: {
        "zh_CN": "数据库错误",
        "en_US": "Database error"
    },
    ErrorCode.NETWORK_ERROR: {
        "zh_CN": "网络错误",
        "en_US": "Network error"
    },
    ErrorCode.TIMEOUT: {
        "zh_CN": "请求超时",
        "en_US": "Request timeout"
    },
    ErrorCode.SERVICE_UNAVAILABLE: {
        "zh_CN": "服务暂时不可用",
        "en_US": "Service unavailable"
    }
}


def get_error_message(code: ErrorCode, locale: str = "zh_CN") -> str:
    """
    获取错误消息
    
    Args:
        code: 错误码
        locale: 语言代码（zh_CN 或 en_US）
    
    Returns:
        错误消息文本
    """
    messages = ERROR_MESSAGES.get(code, {})
    return messages.get(locale, messages.get("zh_CN", str(code)))


class APIError(Exception):
    """API 错误基类"""
    
    def __init__(self, code: ErrorCode, message: str = None, locale: str = "zh_CN"):
        self.code = code
        self.message = message or get_error_message(code, locale)
        super().__init__(self.message)
