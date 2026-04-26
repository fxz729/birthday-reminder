"""全局异常处理中间件"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def global_error_handler(request: Request, exc: Exception):
    """区分 API 和页面请求的异常处理"""
    if isinstance(exc, StarletteHTTPException):
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        raise exc
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})
