"""自定义异常"""

from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """认证错误"""
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedError(HTTPException):
    """权限不足错误"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundError(HTTPException):
    """资源不存在错误"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class BadRequestError(HTTPException):
    """请求错误"""
    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ConflictError(HTTPException):
    """冲突错误（如用户名已存在）"""
    def __init__(self, detail: str = "资源冲突"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
