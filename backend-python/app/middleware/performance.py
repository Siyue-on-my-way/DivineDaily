"""性能监控中间件"""

import time
from fastapi import Request
from app.core.logger import get_logger

logger = get_logger("performance")


async def performance_middleware(request: Request, call_next):
    """
    记录 API 请求性能
    
    功能：
    - 记录每个请求的处理时间
    - 标记慢请求（超过 1 秒）
    - 在响应头中添加处理时间
    """
    start_time = time.time()
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    duration = time.time() - start_time
    
    # 记录慢请求（超过 1 秒）
    if duration > 1.0:
        logger.warning(
            f"慢请求 | method={request.method} | path={request.url.path} | "
            f"duration={duration:.2f}s | status={response.status_code}"
        )
    else:
        logger.info(
            f"请求完成 | method={request.method} | path={request.url.path} | "
            f"duration={duration:.3f}s | status={response.status_code}"
        )
    
    # 添加响应头
    response.headers["X-Process-Time"] = f"{duration:.3f}"
    
    return response
