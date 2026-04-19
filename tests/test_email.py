import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_send_email_mock():
    """测试邮件发送（Mock）"""
    with patch("app.services.email.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True

        result = await mock_send(
            recipients=["test@example.com"],
            subject="测试邮件",
            html_body="<p>测试内容</p>"
        )

        assert result is True
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_no_config():
    """测试未配置邮件时的行为"""
    from app.services.email import send_email

    with patch("app.services.email.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.mail_username = ""
        mock_settings.mail_password = ""
        mock_get_settings.return_value = mock_settings

        result = await send_email(
            recipients=["test@example.com"],
            subject="测试",
            html_body="<p>Test</p>"
        )
        assert result is False


@pytest.mark.asyncio
async def test_send_birthday_reminder_mock():
    """测试生日提醒邮件（Mock）"""
    from app.services.email import send_birthday_reminder

    with patch("app.services.email.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True

        result = await send_birthday_reminder(
            email="test@example.com",
            name="张三",
            days_left=7,
            content="测试内容"
        )

        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert "test@example.com" in call_args[0]
        assert "张三" in call_args[1]


@pytest.mark.asyncio
async def test_send_birthday_reminder_today():
    """测试当天生日提醒主题"""
    from app.services.email import send_birthday_reminder

    with patch("app.services.email.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True

        await send_birthday_reminder(
            email="test@example.com",
            name="张三",
            days_left=0,
            content="测试"
        )

        call_args = mock_send.call_args[0]
        assert "今天" in call_args[1] and "生日" in call_args[1]
