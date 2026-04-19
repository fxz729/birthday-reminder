import pytest
from app.services.template import render_birthday_reminder, validate_template


def test_render_default_template():
    """测试默认模板渲染"""
    result = render_birthday_reminder(
        name="张三",
        birth_date="1990-05-15",
        is_lunar=False,
        email="test@example.com",
        gift_idea="书籍"
    )
    assert "张三" in result
    assert "生日" in result
    assert "书籍" in result


def test_render_with_gift_idea():
    """测试礼物建议渲染"""
    result = render_birthday_reminder(
        name="李四",
        birth_date="1995-03-20",
        is_lunar=False,
        email="li@example.com",
        gift_idea="手机"
    )
    assert "礼物建议" in result or "💝" in result


def test_render_with_notes():
    """测试备注渲染"""
    result = render_birthday_reminder(
        name="王五",
        birth_date="1992-08-10",
        is_lunar=False,
        email="wang@example.com",
        notes="重要客户"
    )
    assert "备注" in result or "📝" in result


def test_render_custom_template():
    """测试自定义模板"""
    custom = "🎉 {{name}} 生日快乐！"
    result = render_birthday_reminder(
        name="测试",
        birth_date="1990-01-01",
        is_lunar=False,
        email="test@example.com",
        custom_template=custom
    )
    assert "🎉 测试 生日快乐！" in result


def test_validate_template_valid():
    """测试有效模板"""
    assert validate_template("Hello {{name}}") is True
    assert validate_template("{% if cond %}Yes{% endif %}") is True
    assert validate_template("Simple text") is True


def test_validate_template_invalid():
    """测试无效模板"""
    assert validate_template("{{invalid") is False
    assert validate_template("{% if %}") is False


def test_render_contains_days_left():
    """测试渲染包含距离天数"""
    result = render_birthday_reminder(
        name="测试",
        birth_date="1990-01-01",
        is_lunar=False,
        email="test@example.com"
    )
    assert "days_left" in result.lower() or "天" in result
