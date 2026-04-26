from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.services import auth as auth_service
from app.middleware.auth import get_optional_user
from app.template_setup import templates
from config import get_settings

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "用户名或密码错误"},
            status_code=401,
        )

    if not user.is_active:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "用户已被禁用"},
            status_code=403,
        )

    settings = get_settings()
    token = auth_service.create_access_token(
        {"user_id": user.id, "username": user.username}
    )

    response = RedirectResponse(url="/auth/dashboard", status_code=302)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=settings.access_token_expire_hours * 3600,
        samesite="lax",
    )
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "两次输入的密码不一致"}, status_code=400
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "密码长度至少6位"}, status_code=400
        )

    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "用户名已存在"}, status_code=400
        )
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "邮箱已被注册"}, status_code=400
        )

    new_user = User(
        username=username,
        email=email,
        password_hash=auth_service.get_password_hash(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/auth/login?registered=true", status_code=302)


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("session_token")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_optional_user),
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # 统计数据
    from app.services.statistics import get_dashboard_summary

    stats = get_dashboard_summary(db, user_id=user.id)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "stats": stats},
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_optional_user),
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "error": None, "success": None},
    )


@router.post("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    email: str = Form(""),
    current_password: str = Form(""),
    new_password: str = Form(""),
    confirm_password: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(get_optional_user),
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    error = None
    success = None

    # Update email if provided and changed
    if email and email != user.email:
        if db.query(User).filter(User.email == email, User.id != user.id).first():
            error = "该邮箱已被其他账号使用"
        else:
            user.email = email
            success = "邮箱已更新"

    # Change password if current password provided
    if current_password:
        if not auth_service.verify_password(current_password, user.password_hash):
            error = "当前密码错误"
        elif new_password != confirm_password:
            error = "两次输入的新密码不一致"
        elif len(new_password) < 6:
            error = "新密码长度至少6位"
        else:
            user.password_hash = auth_service.get_password_hash(new_password)
            success = "密码已更新"

    if error:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user": user, "error": error, "success": None},
        )

    db.commit()
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "error": None, "success": success},
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "error": None, "success": None},
    )


@router.post("/reset-password", response_class=HTMLResponse)
async def send_reset_email(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "该邮箱未注册", "success": None},
        )

    # Generate reset token (short-lived JWT)
    settings = get_settings()
    reset_token = auth_service.create_access_token(
        {"user_id": user.id, "purpose": "password_reset"},
        expires_delta=timedelta(hours=1),
    )

    # Try to send reset email
    try:
        from app.services.notification.email import SimpleEmailSender

        reset_link = f"{settings.base_url}/auth/reset-password/{reset_token}"
        smtp_config = {
            "server": settings.mail_server,
            "port": settings.mail_port,
            "username": settings.mail_username,
            "password": settings.mail_password,
            "use_tls": settings.mail_starttls,
        }
        sender = SimpleEmailSender(smtp_config)
        body = f"""<p>您好 {user.username}：</p>
<p>我们收到了您的密码重置请求。请点击以下链接重置密码：</p>
<p><a href="{reset_link}">{reset_link}</a></p>
<p>链接有效期为1小时。如果您没有请求重置密码，请忽略此邮件。</p>
<p>— Birthday Wishes 生日提醒系统</p>"""
        await sender.send(
            email=user.email,
            subject="【生日提醒】密码重置请求",
            html_body=body,
        )
        success = "密码重置链接已发送到您的邮箱，请查收"
    except Exception:
        success = "密码重置链接已生成，请联系管理员"

    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "error": None, "success": success},
    )


@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str):
    payload = auth_service.verify_token(token)
    if not payload or payload.get("purpose") != "password_reset":
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "链接已过期或无效", "success": None},
        )
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "error": None, "success": None, "reset_token": token},
    )


@router.post("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str,
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    payload = auth_service.verify_token(token)
    if not payload or payload.get("purpose") != "password_reset":
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "链接已过期或无效", "success": None},
        )

    if password != confirm_password:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "两次输入的密码不一致", "success": None, "reset_token": token},
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "密码长度至少6位", "success": None, "reset_token": token},
        )

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "用户不存在", "success": None},
        )

    user.password_hash = auth_service.get_password_hash(password)
    db.commit()
    return RedirectResponse(url="/auth/login?reset=true", status_code=302)
