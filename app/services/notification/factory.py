"""
通知发送器工厂
"""
from typing import Dict, Optional
from app.services.notification.base import NotificationBase
from app.services.notification.email import EmailSender
from app.services.notification.serverchan import ServerChanSender


class NotificationFactory:
    """通知发送器工厂"""

    def __init__(self, smtp_config: Dict, serverchan_sckey: str = ""):
        self.smtp_config = smtp_config
        self.serverchan_sckey = serverchan_sckey

    def create(self, notification_type: str) -> Optional[NotificationBase]:
        """
        根据类型创建发送器

        Args:
            notification_type: 通知类型 "email" 或 "serverchan"

        Returns:
            NotificationBase 实例，或 None
        """
        if notification_type == "email":
            return EmailSender(self.smtp_config)
        elif notification_type == "serverchan":
            if not self.serverchan_sckey:
                return None
            return ServerChanSender(self.serverchan_sckey)
        else:
            return None

    def get_available_types(self) -> list:
        """获取可用的通知类型列表"""
        types = ["email"]
        if self.serverchan_sckey:
            types.append("serverchan")
        return types
