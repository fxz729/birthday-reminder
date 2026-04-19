from jinja2 import Template, Environment, BaseLoader
from datetime import date
from typing import Dict, Any, Optional
from app.services.lunar import (
    get_lunar_date_string,
    calculate_age,
    days_until_birthday,
    get_upcoming_birthday_date
)

DEFAULT_TEMPLATE = """🎂 生日提醒

{{name}} 的生日还有 {{days_left}} 天！
{{date}} 是今年的生日{% if lunar_date %}（农历：{{lunar_date}}）{% endif %}
{{age}} 岁了 🎉

{% if gift_idea %}
💝 礼物建议：{{gift_idea}}
{% endif %}

{% if notes %}
📝 备注：{{notes}}
{% endif %}
"""


def render_birthday_reminder(
    name: str,
    birth_date: str,
    is_lunar: bool,
    email: str,
    custom_template: Optional[str] = None,
    gift_idea: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    """渲染生日提醒邮件内容"""
    year, month, day = map(int, birth_date.split("-"))
    birth_date_obj = date(year, month, day)

    today = date.today()
    days_left = days_until_birthday(birth_date_obj, is_lunar)
    age = calculate_age(birth_date_obj, today) + 1
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
        "age": age,
        "days_left": days_left,
        "gift_idea": gift_idea,
        "notes": notes,
        "email": email
    }

    template_str = custom_template if custom_template else DEFAULT_TEMPLATE

    env = Environment(loader=BaseLoader())
    template = env.from_string(template_str)
    return template.render(**context)


def validate_template(template_str: str) -> bool:
    """验证模板语法"""
    try:
        env = Environment(loader=BaseLoader())
        env.from_string(template_str)
        return True
    except Exception:
        return False
