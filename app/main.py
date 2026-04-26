from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.database import init_db
from app.routes import birthdays, reminders, auth
from app.middleware.error_handler import global_error_handler
from app.middleware.auth import UserContextMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.logging_config import setup_logging
from config import get_settings

settings = get_settings()
setup_logging(debug=settings.debug)

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时初始化数据库"""
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="生日定时提醒系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户上下文中间件（将当前用户注入 request.state）
app.add_middleware(UserContextMiddleware)

# 速率限制中间件
app.add_middleware(RateLimitMiddleware, max_requests=120, window_seconds=60)

# 全局异常处理
app.add_exception_handler(Exception, global_error_handler)

# 静态文件
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 路由
app.include_router(auth.router)
app.include_router(birthdays.router)
app.include_router(reminders.router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/auth/dashboard")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
