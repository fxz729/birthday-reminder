"""
邮件发送器
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import Dict
import asyncio
import logging
from functools import wraps
from pathlib import Path
from app.services.notification.base import NotificationBase

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """重试装饰器 - 支持指数退避"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {type(e).__name__}: {e}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff  # 指数退避
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed. Last error: {type(e).__name__}: {e}"
                        )

            raise last_exception

        return wrapper

    return decorator


class EmailSender(NotificationBase):
    """邮件发送器"""

    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
        # 模板目录
        templates_dir = Path(__file__).parent.parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=True)

    def render_content(self, name: str, template_file: str, extra_info: Dict) -> str:
        """渲染邮件内容"""
        try:
            template = self.env.get_template(template_file)
            return template.render(name=name, **extra_info)
        except Exception as e:
            logger.error(f"Failed to render template {template_file}: {e}")
            raise

    @retry_on_failure()
    async def send(self, email: str, name: str, content: str, days_until: int, age: int, extra_info: Dict) -> bool:
        """发送邮件"""
        subject = self.generate_subject(name, age, days_until)
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_config.get("username", "")
            message["To"] = email
            message["Subject"] = subject
            message.attach(MIMEText(content, "html"))

            async with aiosmtplib.SMTP(
                hostname=self.smtp_config.get("server", "smtp.qq.com"),
                port=self.smtp_config.get("port", 587),
                use_tls=self.smtp_config.get("use_tls", False),
            ) as smtp:
                await smtp.login(self.smtp_config.get("username", ""), self.smtp_config.get("password", ""))
                await smtp.send_message(message)
                logger.info(f"Successfully sent email to {email}")
                return True
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {type(e).__name__}: {e}")
            raise


class SimpleEmailSender:
    """简单邮件发送器（用于兼容原有代码）"""

    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config

    async def send(self, email: str, subject: str, html_body: str) -> bool:
        """发送邮件"""
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_config.get("username", "")
            message["To"] = email
            message["Subject"] = subject
            message.attach(MIMEText(html_body, "html"))

            async with aiosmtplib.SMTP(
                hostname=self.smtp_config.get("server", "smtp.qq.com"),
                port=self.smtp_config.get("port", 587),
                use_tls=self.smtp_config.get("use_tls", False),
            ) as smtp:
                await smtp.login(self.smtp_config.get("username", ""), self.smtp_config.get("password", ""))
                await smtp.send_message(message)
                logger.info(f"Successfully sent email to {email}")
                return True
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {type(e).__name__}: {e}")
            return False
