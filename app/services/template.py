"""
模板渲染服务

支持变量：
- name, date, days_left, email
- lunar_date
- 自定义: gift_idea, notes
"""
from jinja2 import Environment, BaseLoader
from datetime import date
from typing import Dict, Any, Optional
from app.services.lunar import (
    get_lunar_date_string,
    days_until_birthday,
    get_upcoming_birthday_date,
)

DEFAULT_TEMPLATE = """🎂 生日提醒

{{name}} 的生日还有 {{days_left}} 天！
{{date}} 是今年的生日{% if lunar_date %}（农历：{{lunar_date}}）{% endif %}

{% if gift_idea %}
💝 礼物建议：{{gift_idea}}
{% endif %}

{% if notes %}
📝 备注：{{notes}}
{% endif %}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>生日提醒</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #667eea; text-align: center;">🎂 生日提醒</h1>

        <div style="background: #f9f9f9; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <p><strong>{{name}}</strong> 的生日还有 <strong>{{days_left}}</strong> 天！</p>
            <p>{{date}} 是今年的生日{% if lunar_date %}（农历：{{lunar_date}}）{% endif %}</p>
        </div>

        {% if gift_idea %}
        <div style="background: #fce4ec; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <p>💝 礼物建议：{{gift_idea}}</p>
        </div>
        {% endif %}

        {% if notes %}
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <p>📝 备注：{{notes}}</p>
        </div>
        {% endif %}

        <p style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
            此邮件由生日定时提醒系统自动发送
        </p>
    </div>
</body>
</html>
"""


def render_birthday_reminder(
    name: str,
    birth_date: str,
    is_lunar: bool,
    email: str,
    custom_template: Optional[str] = None,
    gift_idea: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """渲染生日提醒邮件内容

    Args:
        name: 姓名
        birth_date: 生日日期 YYYY-MM-DD
        is_lunar: 是否为农历生日
        email: 邮箱
        custom_template: 自定义模板
        gift_idea: 礼物建议
        notes: 备注

    Returns:
        str: 渲染后的内容
    """
    year, month, day = map(int, birth_date.split("-"))
    birth_date_obj = date(year, month, day)

    today = date.today()
    days_left = days_until_birthday(birth_date_obj, is_lunar)
    lunar_date_str = get_lunar_date_string(birth_date_obj) if is_lunar else None

    this_year_birthday = get_upcoming_birthday_date(birth_date_obj, is_lunar, today.year)
    if this_year_birthday:
        date_str = this_year_birthday.strftime("%Y年%m月%d日")
    else:
        date_str = birth_date_obj.strftime("%Y年%m月%d日")

    context: Dict[str, Any] = {
        "name": name,
        "date": date_str,
        "lunar_date": lunar_date_str,
        "days_left": days_left,
        "gift_idea": gift_idea,
        "notes": notes,
        "email": email,
        "solar_match": not is_lunar,
        "lunar_match": is_lunar,
    }

    template_str = custom_template if custom_template else DEFAULT_TEMPLATE

    env = Environment(loader=BaseLoader())
    template = env.from_string(template_str)
    return template.render(**context)


def render_birthday_reminder_html(
    name: str,
    birth_date: str,
    is_lunar: bool,
    email: str,
    custom_template: Optional[str] = None,
    gift_idea: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """渲染 HTML 格式的生日提醒邮件内容

    Args:
        name: 姓名
        birth_date: 生日日期 YYYY-MM-DD
        is_lunar: 是否为农历生日
        email: 邮箱
        custom_template: 自定义模板
        gift_idea: 礼物建议
        notes: 备注

    Returns:
        str: 渲染后的 HTML 内容
    """
    year, month, day = map(int, birth_date.split("-"))
    birth_date_obj = date(year, month, day)

    today = date.today()
    days_left = days_until_birthday(birth_date_obj, is_lunar)
    lunar_date_str = get_lunar_date_string(birth_date_obj) if is_lunar else None

    this_year_birthday = get_upcoming_birthday_date(birth_date_obj, is_lunar, today.year)
    if this_year_birthday:
        date_str = this_year_birthday.strftime("%Y年%m月%d日")
    else:
        date_str = birth_date_obj.strftime("%Y年%m月%d日")

    context: Dict[str, Any] = {
        "name": name,
        "date": date_str,
        "lunar_date": lunar_date_str,
        "days_left": days_left,
        "gift_idea": gift_idea,
        "notes": notes,
        "email": email,
        "solar_match": not is_lunar,
        "lunar_match": is_lunar,
    }

    if custom_template:
        env = Environment(loader=BaseLoader())
        template = env.from_string(custom_template)
    else:
        env = Environment(loader=BaseLoader())
        template = env.from_string(HTML_TEMPLATE)

    return template.render(**context)


def validate_template(template_str: str) -> bool:
    """验证模板语法"""
    try:
        env = Environment(loader=BaseLoader())
        env.from_string(template_str)
        return True
    except Exception:
        return False
