"""
提醒配置路由
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import crud
from app.schemas import ReminderCreate, ReminderResponse
from app.middleware.auth import get_optional_user, get_current_user
from app.template_setup import templates
from app.models import User
from config import get_settings

router = APIRouter(prefix="/birthdays", tags=["reminders"])

DEFAULT_REMINDER_PRESETS = [
    {"days_before": 0, "label": "当天", "cron_time": "0 9 * * *"},
    {"days_before": 1, "label": "提前1天", "cron_time": "0 9 * * *"},
    {"days_before": 3, "label": "提前3天", "cron_time": "0 9 * * *"},
    {"days_before": 7, "label": "提前7天", "cron_time": "0 9 * * *"},
    {"days_before": 30, "label": "提前30天", "cron_time": "0 9 * * *"},
]


@router.get("/{birthday_id}/reminders", response_class=HTMLResponse)
async def reminder_config_page(
    request: Request,
    birthday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    birthday = crud.get_birthday(db, birthday_id, user_id=current_user.id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")

    reminders = crud.get_reminders_for_birthday(db, birthday_id)
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
            "serverchan_enabled": serverchan_enabled,
            "user": current_user,
        },
    )


@router.post("/{birthday_id}/reminders", response_class=HTMLResponse)
async def update_reminders(
    request: Request,
    birthday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    birthday = crud.get_birthday(db, birthday_id, user_id=current_user.id)
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
            notify_type = form_data.get(f"notify_type_{preset['days_before']}", "email")
            reminder_data = ReminderCreate(
                days_before=preset["days_before"],
                cron_time=form_data.get(f"cron_{preset['days_before']}", preset["cron_time"]),
                is_enabled=True,
                template=form_data.get(f"template_{preset['days_before']}") or None,
                notification_type=notify_type,
            )
            crud.create_reminder(db, birthday_id, reminder_data)
            new_reminders.append(reminder_data)

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
            "serverchan_enabled": serverchan_enabled,
            "user": current_user,
        },
    )


@router.get("/api/{birthday_id}/reminders", response_model=List[ReminderResponse])
async def api_get_reminders(
    birthday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership before returning reminders
    birthday = crud.get_birthday(db, birthday_id, user_id=current_user.id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")
    return crud.get_reminders_for_birthday(db, birthday_id)


@router.post("/{birthday_id}/reminders/test")
async def test_reminder(
    birthday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    """发送测试提醒到当前用户的邮箱"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    birthday = crud.get_birthday(db, birthday_id, user_id=current_user.id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")

    settings = get_settings()
    if not settings.mail_username:
        raise HTTPException(status_code=400, detail="邮件服务未配置")

    try:
        from app.services.notification.email import SimpleEmailSender

        smtp_config = {
            "server": settings.mail_server,
            "port": settings.mail_port,
            "username": settings.mail_username,
            "password": settings.mail_password,
            "use_tls": settings.mail_starttls,
        }
        sender = SimpleEmailSender(smtp_config)
        await sender.send(
            email=current_user.email,
            subject=f"【测试】{birthday.name} 的生日提醒",
            html_body=f"""<p><b>这是一封测试提醒邮件。</b></p>
<p>姓名：{birthday.name}<br>
生日：{birthday.birth_date}<br>
类型：{"农历" if birthday.is_lunar else "公历"}<br>
邮箱：{birthday.email}</p>
<p>如果收到此邮件，说明提醒配置正常。</p>""",
        )
        return {"status": "success", "message": f"测试邮件已发送到 {current_user.email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")
