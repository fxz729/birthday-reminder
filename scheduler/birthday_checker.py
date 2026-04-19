"""
生日定时检查器

此脚本由 GitHub Actions + 自托管 Runner 定时触发
检查所有启用的提醒配置，发送邮件通知
"""
import asyncio
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app import crud
from app.services.lunar import days_until_birthday, get_upcoming_birthday_date
from app.services.template import render_birthday_reminder
from app.services.email import send_birthday_reminder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_and_send_reminders():
    """检查并发送提醒"""
    init_db()
    db = SessionLocal()

    try:
        reminders = crud.get_enabled_reminders(db)
        logger.info(f"找到 {len(reminders)} 个启用的提醒配置")

        today = date.today()
        sent_count = 0

        for reminder in reminders:
            birthday = reminder.birthday
            if not birthday:
                continue

            year, month, day = map(int, birthday.birth_date.split("-"))
            birth_date_obj = date(year, month, day)

            days_left = days_until_birthday(birth_date_obj, birthday.is_lunar)

            if days_left == reminder.days_before:
                logger.info(f"发送提醒: {birthday.name}, 提前 {days_left} 天")

                content = render_birthday_reminder(
                    name=birthday.name,
                    birth_date=birthday.birth_date,
                    is_lunar=birthday.is_lunar,
                    email=birthday.email,
                    custom_template=reminder.template,
                    gift_idea=birthday.gift_idea,
                    notes=birthday.notes
                )

                success = await send_birthday_reminder(
                    email=birthday.email,
                    name=birthday.name,
                    days_left=days_left,
                    content=content
                )

                if success:
                    sent_count += 1
                    logger.info(f"✓ 邮件已发送至 {birthday.email}")
                else:
                    logger.error(f"✗ 邮件发送失败: {birthday.email}")

        logger.info(f"检查完成，共发送 {sent_count} 封邮件")

    finally:
        db.close()


def main():
    """主入口"""
    logger.info("=" * 50)
    logger.info("生日定时检查器启动")
    logger.info("=" * 50)

    asyncio.run(check_and_send_reminders())

    logger.info("=" * 50)
    logger.info("生日定时检查器结束")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
