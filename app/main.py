from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from app.database import get_db, init_db
from app.routes import birthdays, reminders
from config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="生日定时提醒系统",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
def startup_event():
    """应用启动时初始化数据库"""
    init_db()


@app.get("/", include_in_schema=False)
async def root():
    """首页重定向到生日列表"""
    return RedirectResponse(url="/birthdays")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


app.include_router(birthdays.router)
app.include_router(reminders.router)
