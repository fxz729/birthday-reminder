from datetime import date
from typing import List
from sqlalchemy.orm import Session
from urllib.parse import quote

from app.models import Birthday


def generate_ics_header() -> str:
    """生成 ICS 文件头部"""
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Birthday Reminder//CN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""


def generate_ics_footer() -> str:
    """生成 ICS 文件尾部"""
    return "END:VCALENDAR\n"


def generate_ics_event(
    uid: str,
    summary: str,
    description: str,
    start_date: str,
    end_date: str,
    recurrence: str = None,
    alarm_minutes: int = 1440  # 默认提前1天提醒
) -> str:
    """生成 ICS 事件"""
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{date.today().strftime('%Y%m%d')}T090000Z",
        f"DTSTART;VALUE=DATE:{start_date.replace('-', '')}",
        f"DTEND;VALUE=DATE:{end_date.replace('-', '')}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{description}",
        "STATUS:CONFIRMED",
        "TRANSP:TRANSPARENT",
    ]

    if recurrence:
        lines.append(f"RRULE:FREQ={recurrence}")

    # 添加提醒
    if alarm_minutes:
        lines.extend([
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"TRIGGER:-PT{alarm_minutes // 60}H{alarm_minutes % 60}M" if alarm_minutes >= 60 else f"-PT{alarm_minutes}M",
            f"DESCRIPTION:{summary}",
            "END:VALARM"
        ])

    lines.append("END:VEVENT")
    return "\n".join(lines)


def birthday_to_ics(birthday: Birthday) -> str:
    """将生日转换为 ICS 事件"""
    uid = f"birthday-{birthday.id}@birthday-reminder"

    summary = f"{birthday.name}的生日"
    description = f"{birthday.name}的生日"
    if birthday.gift_idea:
        description += f"\\n礼物想法: {birthday.gift_idea}"
    if birthday.notes:
        description += f"\\n备注: {birthday.notes}"

    # 使用重复规则 yearly
    return generate_ics_event(
        uid=uid,
        summary=summary,
        description=description,
        start_date=birthday.birth_date,
        end_date=birthday.birth_date,  # 生日当天
        recurrence="YEARLY",
        alarm_minutes=1440  # 提前1天提醒
    )


def generate_user_calendar(db: Session, user_id: int) -> str:
    """生成用户完整日历"""
    birthdays = db.query(Birthday).filter(Birthday.user_id == user_id).all()

    ics_parts = [generate_ics_header()]

    for birthday in birthdays:
        if birthday.is_lunar:
            # 农历跳过（复杂计算暂不处理）
            continue
        ics_parts.append(birthday_to_ics(birthday))

    ics_parts.append(generate_ics_footer())
    return "\n".join(ics_parts)


def generate_webcal_url(user_id: int, token: str) -> str:
    """生成 WebCal 订阅 URL"""
    base_url = f"https://your-domain.com/calendar/feed/{user_id}"
    return f"webcal://{base_url}?token={quote(token)}"


def generate_calendar_link(user_id: int, token: str) -> str:
    """生成日历下载链接"""
    return f"/calendar/download?user_id={user_id}&token={quote(token)}"
