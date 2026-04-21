"""
通知服务模块

提供统一的通知发送接口，支持多种通知渠道：
- Email: 邮件发送
- ServerChan: Server酱推送
"""
from app.services.notification.base import NotificationBase
from app.services.notification.email import EmailSender, SimpleEmailSender
from app.services.notification.serverchan import ServerChanSender
from app.services.notification.factory import NotificationFactory

__all__ = [
    "NotificationBase",
    "EmailSender",
    "ServerChanSender",
    "SimpleEmailSender",
    "NotificationFactory",
]
