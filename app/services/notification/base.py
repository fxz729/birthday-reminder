"""
通知发送基类
"""
from abc import ABC, abstractmethod
from typing import Dict


class NotificationBase(ABC):
    """通知发送器抽象基类"""

    @abstractmethod
    async def send(self, email: str, name: str, content: str, days_until: int, age: int, extra_info: Dict) -> bool:
        """
        发送通知

        Args:
            email: 收件人邮箱（用于邮件）或名称（用于日志）
            name: 收件人姓名
            content: 渲染后的内容
            days_until: 距离生日天数
            age: 年龄
            extra_info: 额外的日期信息（干支、生肖等）

        Returns:
            bool: 发送是否成功
        """
        pass

    def generate_subject(self, name: str, age: int, days_until: int) -> str:
        """生成邮件主题"""
        if days_until == 0:
            return f"🎂 今天是 {name} 的生日！"
        else:
            return f"🎁 还有 {days_until} 天就是 {name} 的生日了"
