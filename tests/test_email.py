"""测试通知邮件发送"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_send_email_mock():
    """测试邮件发送（Mock）"""
    with patch("aiosmtplib.SMTP") as mock_smtp:
        mock_smtp.return_value.__aenter__.return_value.sendmail = AsyncMock()

        from app.services.notification.email import EmailSender

        sender = EmailSender({
            "server": "smtp.test.com",
            "port": 587,
            "username": "test@test.com",
            "password": "password",
            "use_tls": True,
        })
        result = await sender.send(
            email="recipient@test.com",
            name="张三",
            content="<p>测试内容</p>",
            days_until=7,
            age=25,
            extra_info={},
        )
        assert result is True


@pytest.mark.asyncio
async def test_send_email_no_config():
    """测试未配置邮件时的行为"""
    from app.services.notification.email import EmailSender

    sender = EmailSender({
        "server": "",
        "port": 587,
        "username": "",
        "password": "",
        "use_tls": True,
    })

    with patch("aiosmtplib.SMTP") as mock_smtp:
        mock_smtp.return_value.__aenter__.return_value.sendmail = AsyncMock()

        result = await sender.send(
            email="test@example.com",
            name="test",
            content="<p>Test</p>",
            days_until=7,
            age=30,
            extra_info={},
        )
        assert result is True


@pytest.mark.asyncio
async def test_send_birthday_reminder_mock():
    """测试生日提醒邮件主题"""
    from app.services.notification.email import EmailSender

    sender = EmailSender({
        "server": "smtp.test.com",
        "port": 587,
        "username": "test@test.com",
        "password": "password",
        "use_tls": True,
    })
    subject = sender.generate_subject(name="张三", age=25, days_until=7)
    assert "张三" in subject
    assert "7" in str(subject)


@pytest.mark.asyncio
async def test_send_birthday_reminder_today():
    """测试当天生日提醒主题"""
    from app.services.notification.email import EmailSender

    sender = EmailSender({
        "server": "smtp.test.com",
        "port": 587,
        "username": "test@test.com",
        "password": "password",
        "use_tls": True,
    })
    subject = sender.generate_subject(name="张三", age=25, days_until=0)
    assert "今天" in subject
    assert "生日" in subject
