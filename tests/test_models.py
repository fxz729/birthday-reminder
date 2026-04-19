import pytest
from datetime import datetime
from app.models import Birthday, Reminder


def test_birthday_model():
    """测试生日模型"""
    birthday = Birthday(
        name="张三",
        birth_date="1990-05-15",
        is_lunar=False,
        email="test@example.com"
    )
    assert birthday.name == "张三"
    assert birthday.is_lunar is False
    assert birthday.gift_idea is None


def test_birthday_model_with_lunar():
    """测试农历生日模型"""
    birthday = Birthday(
        name="李四",
        birth_date="1995-03-20",
        is_lunar=True,
        email="li@example.com",
        gift_idea="书籍",
        notes="备注信息"
    )
    assert birthday.is_lunar is True
    assert birthday.gift_idea == "书籍"
    assert birthday.notes == "备注信息"


def test_reminder_model():
    """测试提醒模型"""
    reminder = Reminder(
        days_before=7,
        cron_time="0 9 * * *",
        is_enabled=True
    )
    assert reminder.days_before == 7
    assert reminder.cron_time == "0 9 * * *"
    assert reminder.is_enabled is True


def test_reminder_default_values():
    """测试提醒默认配置"""
    reminder = Reminder(days_before=0, cron_time="0 9 * * *", is_enabled=True)
    assert reminder.days_before == 0
    assert reminder.cron_time == "0 9 * * *"
    assert reminder.is_enabled is True
