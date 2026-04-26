"""
生日定时检查器

此脚本由 GitHub Actions + 自托管 Runner 定时触发
检查所有启用的提醒配置，发送通知（支持 Email 和 ServerChan）

特性：
- 异步并发发送多个通知
- 支持多种通知渠道
- 自动去重：同一提醒每天只发送一次
- 精确到分钟的 cron 时间匹配
"""
import asyncio
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app import crud
from app.models import NotificationLog
from app.services.lunar import days_until_birthday
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
        # 渲染邮件内容
        content = render_birthday_reminder_html(
            name=birthday.name,
            birth_date=birthday.birth_date,
            is_lunar=birthday.is_lunar,
            email=birthday.email,
            custom_template=reminder.template,
            gift_idea=birthday.gift_idea,
            notes=birthday.notes,
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
            age=0,
            extra_info={"days_until": days_left}
        )

        if success:
            return True, f"✓ {reminder.notification_type.upper()} 已发送至 {birthday.email}"
        else:
            return False, f"✗ {reminder.notification_type.upper()} 发送失败: {birthday.email}"

    except Exception as e:
        logger.error(f"发送通知时出错: {birthday.name}, 错误: {type(e).__name__}: {e}")
        return False, f"✗ 异常: {type(e).__name__}: {e}"


def _already_sent_today(db: Session, reminder_id: int) -> bool:
    """检查今天是否已经发送过该提醒（基于 UTC 时间，与 created_at 时区一致）"""
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    return db.query(NotificationLog).filter(
        NotificationLog.reminder_id == reminder_id,
        NotificationLog.created_at >= today_start,
        NotificationLog.status == "success",
    ).first() is not None


def _log_notification(db: Session, reminder, birthday, success: bool, message: str):
    """记录通知发送历史"""
    log = NotificationLog(
        birthday_id=birthday.id,
        user_id=birthday.user_id,
        reminder_id=reminder.id,
        notification_type=reminder.notification_type,
        recipient=birthday.email,
        status="success" if success else "failed",
        error_message=None if success else message,
    )
    db.add(log)
    db.commit()


def _matches_cron_time(reminder) -> bool:
    """检查当前时间是否匹配提醒的 cron 时间（精确到分钟）"""
    parts = reminder.cron_time.split() if reminder.cron_time else []
    if len(parts) >= 2:
        try:
            cron_minute, cron_hour = int(parts[0]), int(parts[1])
        except ValueError:
            return False  # 解析失败不发送
        now = datetime.now()
        return now.hour == cron_hour and now.minute == cron_minute
    return False


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

    # 检查当前时间是否匹配 cron 时间
    if not _matches_cron_time(reminder):
        return False, None

    # 去重：今天已发送过则跳过
    if _already_sent_today(db, reminder.id):
        return False, None

    logger.info(f"发送提醒: {birthday.name}, 提前 {days_left} 天, 类型: {reminder.notification_type}")

    result = await send_notification(reminder, birthday, days_left, factory, db)

    # 记录发送历史
    success, message = result
    try:
        _log_notification(db, reminder, birthday, success, message)
    except Exception as e:
        logger.error(f"记录通知日志失败: {e}")

    return result


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
        "use_tls": settings.mail_ssl_tls,
        "starttls": settings.mail_starttls,
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
