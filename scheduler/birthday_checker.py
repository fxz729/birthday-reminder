"""
生日定时检查器

此脚本由 GitHub Actions + 自托管 Runner 定时触发
检查所有启用的提醒配置，发送通知（支持 Email 和 ServerChan）

特性：
- 异步并发发送多个通知
- 支持多种通知渠道
- 包含丰富的干支/生肖/节日信息
"""
import asyncio
import sys
from datetime import date
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app import crud
from app.services.lunar import days_until_birthday, get_birthday_info
from app.services.template import render_birthday_reminder_html
from app.services.notification import NotificationFactory
from config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_notification(
    reminder,
    birthday,
    days_left: int,
    factory: NotificationFactory,
    db: Session
) -> Tuple[bool, str]:
    """
    发送单个通知

    Returns:
        Tuple[bool, str]: (是否成功, 消息)
    """
    try:
        # 获取丰富的日期信息
        year, month, day = map(int, birthday.birth_date.split("-"))
        birth_date_obj = date(year, month, day)
        extra_info = get_birthday_info(birth_date_obj, birthday.is_lunar)

        # 渲染邮件内容
        content = render_birthday_reminder_html(
            name=birthday.name,
            birth_date=birthday.birth_date,
            is_lunar=birthday.is_lunar,
            email=birthday.email,
            custom_template=reminder.template,
            gift_idea=birthday.gift_idea,
            notes=birthday.notes,
            include_rich_info=True
        )

        # 创建发送器并发送
        sender = factory.create(reminder.notification_type)
        if sender is None:
            return False, f"无法创建 {reminder.notification_type} 发送器"

        success = await sender.send(
            email=birthday.email,
            name=birthday.name,
            content=content,
            days_until=days_left,
            age=extra_info.get('age', 0),
            extra_info=extra_info
        )

        if success:
            return True, f"✓ {reminder.notification_type.upper()} 已发送至 {birthday.email}"
        else:
            return False, f"✗ {reminder.notification_type.upper()} 发送失败: {birthday.email}"

    except Exception as e:
        logger.error(f"发送通知时出错: {birthday.name}, 错误: {type(e).__name__}: {e}")
        return False, f"✗ 异常: {type(e).__name__}: {e}"


async def process_reminder(
    reminder,
    factory: NotificationFactory,
    db: Session
) -> Tuple[bool, str]:
    """处理单个提醒配置"""
    birthday = reminder.birthday
    if not birthday:
        return False, "生日不存在"

    year, month, day = map(int, birthday.birth_date.split("-"))
    birth_date_obj = date(year, month, day)
    days_left = days_until_birthday(birth_date_obj, birthday.is_lunar)

    if days_left != reminder.days_before:
        return False, None  # 不需要发送

    logger.info(f"发送提醒: {birthday.name}, 提前 {days_left} 天, 类型: {reminder.notification_type}")

    return await send_notification(reminder, birthday, days_left, factory, db)


async def check_and_send_reminders():
    """检查并发送所有提醒（异步并发）"""
    init_db()

    settings = get_settings()

    # 初始化通知工厂
    smtp_config = {
        "server": settings.mail_server,
        "port": settings.mail_port,
        "username": settings.mail_username,
        "password": settings.mail_password,
        "use_tls": settings.mail_starttls,
    }
    factory = NotificationFactory(
        smtp_config=smtp_config,
        serverchan_sckey=settings.serverchan_sckey
    )

    db = SessionLocal()

    try:
        reminders = crud.get_enabled_reminders(db)
        logger.info(f"找到 {len(reminders)} 个启用的提醒配置")

        # 收集需要处理的任务
        tasks = []
        for reminder in reminders:
            task = process_reminder(reminder, factory, db)
            tasks.append(task)

        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        success_count = 0
        fail_count = 0
        skip_count = 0

        for i, result in enumerate(results):
            reminder = reminders[i]
            birthday = reminder.birthday

            if isinstance(result, Exception):
                logger.error(f"任务执行异常: {birthday.name if birthday else 'Unknown'}, {type(result).__name__}: {result}")
                fail_count += 1
                continue

            success, message = result
            if message is None:
                skip_count += 1
            elif success:
                logger.info(message)
                success_count += 1
            else:
                logger.error(message)
                fail_count += 1

        logger.info("=" * 50)
        logger.info(f"检查完成: 成功 {success_count}, 失败 {fail_count}, 跳过 {skip_count}")
        logger.info("=" * 50)

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
