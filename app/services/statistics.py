from datetime import date
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models import Birthday, Category, birthday_categories


def get_total_birthdays(db: Session, user_id: int) -> int:
    """获取用户生日总数"""
    return db.query(Birthday).filter(Birthday.user_id == user_id).count()


def get_birthdays_this_month(db: Session, user_id: int) -> List[Birthday]:
    """获取本月生日"""
    today = date.today()
    month = today.month

    birthdays = db.query(Birthday).filter(
        Birthday.user_id == user_id
    ).all()

    # 筛选本月生日
    this_month = []
    for b in birthdays:
        if b.is_lunar:
            # 农历跳过（复杂计算暂不处理）
            continue
        _, m, _ = b.birth_date.split('-')
        if int(m) == month:
            this_month.append(b)

    return this_month


def get_upcoming_birthdays(db: Session, user_id: int, days: int = 7) -> List[Birthday]:
    """获取即将到来的生日"""
    today = date.today()

    birthdays = db.query(Birthday).filter(
        Birthday.user_id == user_id
    ).all()

    upcoming = []
    for b in birthdays:
        if b.is_lunar:
            # 农历跳过
            continue

        year, month, day = b.birth_date.split('-')
        birth_month = int(month)
        birth_day = int(day)

        # 今年生日日期
        try:
            this_year_birthday = date(today.year, birth_month, birth_day)
        except ValueError:
            continue

        # 计算距离
        if this_year_birthday >= today:
            days_left = (this_year_birthday - today).days
        else:
            # 今年已过，明年
            try:
                next_year_birthday = date(today.year + 1, birth_month, birth_day)
            except ValueError:
                continue
            days_left = (next_year_birthday - today).days

        if days_left <= days:
            upcoming.append(b)

    return upcoming


def get_category_stats(db: Session, user_id: int) -> Dict[str, int]:
    """获取分类统计"""
    # 获取用户所有分类
    categories = db.query(Category).filter(Category.user_id == user_id).all()

    stats = {}
    for cat in categories:
        count = db.execute(
            birthday_categories.select().where(
                birthday_categories.c.category_id == cat.id
            )
        ).fetchall()
        stats[cat.name] = len(count)

    # 未分类
    all_birthdays = db.query(Birthday).filter(Birthday.user_id == user_id).all()
    categorized = sum(stats.values())
    stats["未分类"] = len(all_birthdays) - categorized

    return stats


def get_lunar_solar_stats(db: Session, user_id: int) -> Dict[str, int]:
    """获取农历/公历统计"""
    birthdays = db.query(Birthday).filter(Birthday.user_id == user_id).all()

    solar = sum(1 for b in birthdays if not b.is_lunar)
    lunar = sum(1 for b in birthdays if b.is_lunar)

    return {"solar": solar, "lunar": lunar}


def get_birthday_heatmap_data(db: Session, user_id: int) -> Dict[int, int]:
    """获取生日分布热力图数据（按月份）"""
    birthdays = db.query(Birthday).filter(
        Birthday.user_id == user_id,
        Birthday.is_lunar == False  # 只统计公历
    ).all()

    heatmap = {month: 0 for month in range(1, 13)}

    for b in birthdays:
        try:
            _, month, _ = b.birth_date.split('-')
            heatmap[int(month)] += 1
        except (ValueError, AttributeError):
            continue

    return heatmap


def get_dashboard_summary(db: Session, user_id: int) -> Dict:
    """获取仪表盘摘要数据"""
    today = date.today()

    return {
        "total": get_total_birthdays(db, user_id),
        "this_month": len(get_birthdays_this_month(db, user_id)),
        "upcoming_7_days": len(get_upcoming_birthdays(db, user_id, 7)),
        "categories": get_category_stats(db, user_id),
        "lunar_solar": get_lunar_solar_stats(db, user_id),
        "heatmap": get_birthday_heatmap_data(db, user_id),
    }
