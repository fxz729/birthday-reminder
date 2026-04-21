from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from config import get_settings
from typing import List
from functools import lru_cache


@lru_cache()
def get_mail_config() -> ConnectionConfig:
    """获取邮件配置（延迟初始化）"""
    settings = get_settings()
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_STARTTLS=settings.mail_starttls,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        USE_CREDENTIALS=settings.mail_use_credentials,
        VALIDATE_CERTS=settings.mail_validate_certs
    )


async def send_email(
    recipients: List[str],
    subject: str,
    html_body: str
) -> bool:
    """发送邮件"""
    settings = get_settings()
    if not settings.mail_username or not settings.mail_password:
        print("邮件配置未设置，跳过发送")
        return False

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html_body,
        subtype=MessageType.html
    )

    conf = get_mail_config()
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


async def send_birthday_reminder(
    email: str,
    name: str,
    days_left: int,
    content: str
) -> bool:
    """发送生日提醒邮件"""
    if days_left == 0:
        subject = f"🎂 今天是 {name} 的生日！"
    else:
        subject = f"🎁 还有 {days_left} 天就是 {name} 的生日了"

    html_body = f"""
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; text-align: center;">🎂 生日提醒</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <pre style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;">{content}</pre>
        </div>
        <p style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
            此邮件由生日定时提醒系统自动发送
        </p>
    </div>
    """

    return await send_email([email], subject, html_body)
