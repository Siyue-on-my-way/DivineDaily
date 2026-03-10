"""占卜相关自定义异常

定义占卜服务中使用的各种异常类型，便于错误分类和处理
"""

from fastapi import HTTPException, status


class DivinationError(HTTPException):
    """占卜基础错误"""
    def __init__(self, detail: str = "占卜服务错误", status_code: int = 500):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class DivinationTimeoutError(DivinationError):
    """占卜超时错误"""
    def __init__(self, detail: str = "占卜处理超时，请稍后重试"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


class DivinationProcessingError(DivinationError):
    """占卜处理错误"""
    def __init__(self, detail: str = "占卜处理失败"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class LLMEnhancementError(DivinationError):
    """LLM 增强解读错误"""
    def __init__(self, detail: str = "AI 增强解读失败，已返回基础占卜结果"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class SessionNotFoundError(DivinationError):
    """占卜会话不存在错误"""
    def __init__(self, session_id: str = ""):
        detail = f"占卜会话不存在: {session_id}" if session_id else "占卜会话不存在"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidQuestionError(DivinationError):
    """无效问题错误"""
    def __init__(self, detail: str = "问题格式无效或内容不符合要求"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DatabaseConnectionError(DivinationError):
    """数据库连接错误"""
    def __init__(self, detail: str = "数据库连接失败，请稍后重试"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
