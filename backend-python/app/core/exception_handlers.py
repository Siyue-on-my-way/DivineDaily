"""统一异常处理器"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.error_codes import ErrorCode, get_error_message
from app.core.logger import get_logger

logger = get_logger("exception_handler")


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """验证错误处理"""
    logger.warning(f"验证错误 | path={request.url.path} | errors={exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": ErrorCode.VALIDATION_ERROR,
            "message": get_error_message(ErrorCode.VALIDATION_ERROR),
            "detail": exc.errors()
        }
    )


async def authentication_exception_handler(request: Request, exc):
    """认证错误处理"""
    logger.warning(f"认证失败 | path={request.url.path} | detail={exc.detail}")
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error_code": ErrorCode.TOKEN_INVALID,
            "message": str(exc.detail)
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用错误处理"""
    logger.error(
        f"未处理的异常 | path={request.url.path} | method={request.method} | error={str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": ErrorCode.INTERNAL_ERROR,
            "message": get_error_message(ErrorCode.INTERNAL_ERROR)
        }
    )


async def not_found_exception_handler(request: Request, exc):
    """404 错误处理"""
    logger.warning(f"资源不存在 | path={request.url.path} | method={request.method}")
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error_code": "404",
            "message": "资源不存在"
        }
    )
