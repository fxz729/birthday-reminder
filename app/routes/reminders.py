"""
提醒配置路由
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from app.database import get_db
from app import crud
from app.schemas import ReminderCreate, ReminderResponse
from config import get_settings

router = APIRouter(prefix="/birthdays", tags=["reminders"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

DEFAULT_REMINDER_PRESETS = [
    {"days_before": 0, "label": "当天", "cron_time": "0 9 * * *"},
    {"days_before": 1, "label": "提前1天", "cron_time": "0 9 * * *"},
    {"days_before": 3, "label": "提前3天", "cron_time": "0 9 * * *"},
    {"days_before": 7, "label": "提前7天", "cron_time": "0 9 * * *"},
    {"days_before": 30, "label": "提前30天", "cron_time": "0 9 * * *"},
]


@router.get("/{birthday_id}/reminders", response_class=HTMLResponse)
async def reminder_config_page(request: Request, birthday_id: int, db: Session = Depends(get_db)):
    """提醒配置页"""
    birthday = crud.get_birthday(db, birthday_id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")

    reminders = crud.get_reminders_for_birthday(db, birthday_id)

    # 检查 ServerChan 是否配置
    settings = get_settings()
    serverchan_enabled = bool(settings.serverchan_sckey)

    return templates.TemplateResponse(
        "reminder_form.html",
        {
            "request": request,
            "birthday": birthday,
            "reminders": reminders,
            "presets": DEFAULT_REMINDER_PRESETS,
            "errors": None,
            "serverchan_enabled": serverchan_enabled
        }
    )


@router.post("/{birthday_id}/reminders", response_class=HTMLResponse)
async def update_reminders(request: Request, birthday_id: int, db: Session = Depends(get_db)):
    """更新提醒配置"""
    birthday = crud.get_birthday(db, birthday_id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")

    form_data = await request.form()

    existing_reminders = crud.get_reminders_for_birthday(db, birthday_id)
    for r in existing_reminders:
        crud.delete_reminder(db, r.id)

    new_reminders = []
    for preset in DEFAULT_REMINDER_PRESETS:
        key = f"reminder_{preset['days_before']}"
        if key in form_data:
            # 获取通知类型
            notify_type = form_data.get(f"notify_type_{preset['days_before']}", "email")

            reminder_data = ReminderCreate(
                days_before=preset["days_before"],
                cron_time=form_data.get(f"cron_{preset['days_before']}", preset["cron_time"]),
                is_enabled=True,
                template=form_data.get(f"template_{preset['days_before']}") or None,
                notification_type=notify_type
            )
            crud.create_reminder(db, birthday_id, reminder_data)
            new_reminders.append(reminder_data)

    # 检查 ServerChan 是否配置
    settings = get_settings()
    serverchan_enabled = bool(settings.serverchan_sckey)

    return templates.TemplateResponse(
        "reminder_form.html",
        {
            "request": request,
            "birthday": birthday,
            "reminders": new_reminders,
            "presets": DEFAULT_REMINDER_PRESETS,
            "errors": None,
            "success": True,
            "serverchan_enabled": serverchan_enabled
        }
    )


@router.get("/api/{birthday_id}/reminders", response_model=List[ReminderResponse])
async def api_get_reminders(birthday_id: int, db: Session = Depends(get_db)):
    """API: 获取生日的提醒配置"""
    return crud.get_reminders_for_birthday(db, birthday_id)
