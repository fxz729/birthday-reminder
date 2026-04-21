"""
通知模块测试
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.notification.base import NotificationBase
from app.services.notification.email import EmailSender
from app.services.notification.serverchan import ServerChanSender
from app.services.notification.factory import NotificationFactory


def test_notification_factory_create_email():
    """测试工厂创建邮件发送器"""
    factory = NotificationFactory(smtp_config={}, serverchan_sckey="")
    sender = factory.create("email")
    assert isinstance(sender, EmailSender)


def test_notification_factory_create_serverchan():
    """测试工厂创建 ServerChan 发送器"""
    factory = NotificationFactory(smtp_config={}, serverchan_sckey="test_sckey")
    sender = factory.create("serverchan")
    assert isinstance(sender, ServerChanSender)


def test_notification_factory_create_invalid():
    """测试工厂处理无效类型"""
    factory = NotificationFactory(smtp_config={}, serverchan_sckey="")
    sender = factory.create("invalid_type")
    assert sender is None


def test_notification_factory_create_serverchan_no_sckey():
    """测试没有配置 sckey 时返回 None"""
    factory = NotificationFactory(smtp_config={}, serverchan_sckey="")
    sender = factory.create("serverchan")
    assert sender is None


def test_notification_factory_get_available_types():
    """测试获取可用通知类型"""
    factory1 = NotificationFactory(smtp_config={}, serverchan_sckey="")
    types1 = factory1.get_available_types()
    assert "email" in types1
    assert "serverchan" not in types1

    factory2 = NotificationFactory(smtp_config={}, serverchan_sckey="test")
    types2 = factory2.get_available_types()
    assert "email" in types2
    assert "serverchan" in types2


class TestEmailSender:
    """邮件发送器测试"""

    def test_email_sender_init(self):
        """测试邮件发送器初始化"""
        config = {
            "server": "smtp.qq.com",
            "port": 587,
            "username": "test@qq.com",
            "password": "test_pass",
            "use_tls": True
        }
        sender = EmailSender(config)
        assert sender.smtp_config == config

    def test_email_sender_generate_subject(self):
        """测试生成邮件主题"""
        config = {"username": "test@qq.com"}
        sender = EmailSender(config)

        # 当天生日
        subject = sender.generate_subject("Test", 30, 0)
        assert "Test" in subject
        # 当天生日格式是 "🎂 今天是 Test 的生日！"
        assert "今天" in subject or "Birthday" in subject

        # 提前7天
        subject = sender.generate_subject("User", 25, 7)
        assert "User" in subject
        assert "7" in subject
        assert "还有" in subject


class TestServerChanSender:
    """ServerChan 发送器测试"""

    def test_serverchan_sender_init(self):
        """测试 ServerChan 发送器初始化"""
        sender = ServerChanSender("test_sckey")
        assert sender.sckey == "test_sckey"

    def test_serverchan_render_content(self):
        """测试渲染纯文本内容"""
        sender = ServerChanSender("test_sckey")
        extra_info = {
            "days_until": 0,
            "solar_match": True,
            "lunar_match": False,
            "age": 30,
            "zodiac": "马",
            "constellation": "狮子座",
            "solar_term": "立秋",
            "lunar_festival": "春节",
            "solar_festival": "元旦",
            "gz_year": "庚午",
            "gz_month": "戊寅",
            "gz_day": "甲子"
        }

        content = sender.render_content("张三", extra_info)
        assert "张三" in content
        assert "马" in content
        assert "狮子座" in content
        assert "生肖" in content
        assert "星座" in content

    def test_serverchan_render_content_future_birthday(self):
        """测试渲染未来生日内容"""
        sender = ServerChanSender("test_sckey")
        extra_info = {
            "days_until": 7,
            "solar_match": True,
            "lunar_match": False,
            "age": 25,
            "zodiac": "龙"
        }

        content = sender.render_content("李四", extra_info)
        assert "7天后" in content
        assert "龙" in content


@pytest.mark.asyncio
async def test_email_sender_send_mock():
    """测试邮件发送（模拟）"""
    config = {
        "server": "smtp.qq.com",
        "port": 587,
        "username": "test@qq.com",
        "password": "test_pass",
        "use_tls": False
    }
    sender = EmailSender(config)

    with patch.object(sender, 'send', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        result = await mock_send(
            email="to@example.com",
            name="测试用户",
            content="<p>测试内容</p>",
            days_until=3,
            age=30,
            extra_info={}
        )
        assert result == True


@pytest.mark.asyncio
async def test_serverchan_sender_render_content():
    """测试 ServerChan 内容渲染"""
    sender = ServerChanSender("test_sckey")
    extra_info = {
        "days_until": 5,
        "solar_match": True,
        "lunar_match": False,
        "age": 28,
        "zodiac": "Tiger",
        "constellation": "Leo"
    }
    content = sender.render_content("Test User", extra_info)
    assert content is not None
    assert "Test User" in content
    assert "Tiger" in content
    assert "28" in content
