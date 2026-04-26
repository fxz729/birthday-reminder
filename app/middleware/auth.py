"""认证中间件 - FastAPI 依赖项"""
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services import auth as auth_service


class UserContextMiddleware(BaseHTTPMiddleware):
    """将当前用户注入 request.state.user（无需 DB 查询）"""

    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        token = request.cookies.get("session_token")
        if token:
            payload = auth_service.verify_token(token)
            if payload:
                request.state.user = {
                    "id": payload.get("user_id"),
                    "username": payload.get("username"),
                }
        response = await call_next(request)
        return response


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """必需认证 - 用于需要登录的页面"""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录"
        )
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期"
        )
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )
    return user


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """可选认证 - 用于可选登录的页面"""
    token = request.cookies.get("session_token")
    if not token:
        return None
    payload = auth_service.verify_token(token)
    if not payload:
        return None
    user_id = payload.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()
