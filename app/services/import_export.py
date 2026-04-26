import csv
import io
import re
from typing import List, Dict, Iterator, Optional
from sqlalchemy.orm import Session

from app.models import Birthday, Category, birthday_categories
from app.crud import create_birthday, create_category, get_categories_by_user


def export_birthdays_to_csv(db: Session, user_id: int) -> str:
    """导出用户生日为 CSV 格式"""
    birthdays = db.query(Birthday).filter(Birthday.user_id == user_id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # 标题行
    writer.writerow(['name', 'birth_date', 'is_lunar', 'email', 'gift_idea', 'notes', 'categories'])
    db.flush()

    for b in birthdays:
        categories = ','.join([c.name for c in b.categories]) if b.categories else ''
        writer.writerow([
            b.name,
            b.birth_date,
            'true' if b.is_lunar else 'false',
            b.email,
            b.gift_idea or '',
            b.notes or '',
            categories
        ])

    return output.getvalue()


def export_birthdays_to_txt(db: Session, user_id: int) -> str:
    """导出用户生日为可读的 TXT 格式"""
    from datetime import date

    birthdays = db.query(Birthday).filter(Birthday.user_id == user_id).all()
    today = date.today()
    lines = [
        "=" * 50,
        "  Birthday Wishes - 生日列表导出",
        f"  导出时间：{today}",
        "=" * 50,
        "",
    ]

    for i, b in enumerate(birthdays, 1):
        btype = "农历" if b.is_lunar else "公历"
        month, day = b.birth_date[5:7], b.birth_date[8:10]
        lines.append(f"  {i}. {b.name}")
        lines.append(f"     生日：{month}月{day}日（{btype}）")
        lines.append(f"     邮箱：{b.email}")
        if b.gift_idea:
            lines.append(f"     礼物：{b.gift_idea}")
        if b.notes:
            lines.append(f"     备注：{b.notes}")
        if b.categories:
            cats = "、".join([c.name for c in b.categories])
            lines.append(f"     分类：{cats}")
        lines.append("")

    lines.append("=" * 50)
    lines.append(f"  共 {len(birthdays)} 条记录")
    lines.append("=" * 50)

    return "\n".join(lines)


def import_birthdays_from_csv(db: Session, user_id: int, csv_content: str) -> int:
    """从 CSV 导入生日，返回导入数量"""
    from app.schemas import BirthdayCreate

    reader = csv.DictReader(io.StringIO(csv_content))
    count = 0

    for row in reader:
        try:
            name = row.get('name', '').strip()
            birth_date = row.get('birth_date', '').strip()
            is_lunar = row.get('is_lunar', '').strip().lower() in ('true', '1', 'yes')
            email = row.get('email', '').strip()
            category_name = row.get('category', '').strip()

            if not name or not birth_date:
                continue

            # 验证日期格式
            if not is_valid_date(birth_date):
                continue

            # 创建生日
            birthday_data = BirthdayCreate(
                name=name,
                birth_date=birth_date,
                is_lunar=is_lunar,
                email=email
            )
            birthday = create_birthday(db, birthday_data, user_id)

            # 处理分类
            if category_name:
                cat = get_or_create_category(db, user_id, category_name)
                if cat:
                    db.execute(
                        birthday_categories.insert().values(
                            birthday_id=birthday.id,
                            category_id=cat.id
                        )
                    )
                    db.commit()

            count += 1
        except Exception:
            continue

    return count


def get_or_create_category(db: Session, user_id: int, name: str) -> Optional[Category]:
    """获取或创建分类"""
    cat = db.query(Category).filter(
        Category.user_id == user_id,
        Category.name == name
    ).first()

    if cat:
        return cat

    cat = create_category(db, user_id, name)
    return cat


def is_valid_date(date_str: str) -> bool:
    """验证日期格式 YYYY-MM-DD"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False

    try:
        year, month, day = map(int, date_str.split('-'))
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        return True
    except ValueError:
        return False


def parse_vcard(content: str) -> Iterator[Dict]:
    """解析 vCard 格式"""
    vcards = content.split('BEGIN:VCARD')
    for vcard in vcards:
        if 'END:VCARD' not in vcard:
            continue

        contact = {'name': '', 'birth_date': '', 'email': '', 'phone': '', 'notes': ''}

        for line in vcard.split('\n'):
            line = line.strip()
            if line.startswith('FN:'):
                contact['name'] = line[3:].strip()
            elif line.startswith('BDAY:'):
                bday = line[5:].strip()
                # 转换为 YYYY-MM-DD
                contact['birth_date'] = normalize_vcard_date(bday)
            elif line.startswith('EMAIL:'):
                contact['email'] = line[6:].strip()
            elif line.startswith('TEL:'):
                contact['phone'] = line[4:].strip()
            elif line.startswith('NOTE:'):
                contact['notes'] = line[5:].strip()

        if contact['name']:
            yield contact


def normalize_vcard_date(date_str: str) -> str:
    """标准化 vCard 日期格式"""
    # 支持 YYYYMMDDD, YYYY-MM-DD, YYYY/MM/DD 等格式
    date_str = date_str.replace('/', '-').replace('.', '-')

    # 移除时间部分
    if 'T' in date_str:
        date_str = date_str.split('T')[0]

    # 如果是纯数字 YYYYMMDD
    if re.match(r'^\d{8}$', date_str):
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    return date_str


def import_birthdays_from_contacts(
    db: Session,
    user_id: int,
    contacts: List[Dict],
    default_email: str = "no-email@example.com"
) -> int:
    """从联系人列表导入生日"""
    from app.schemas import BirthdayCreate

    count = 0
    for contact in contacts:
        try:
            name = contact.get('name', '').strip()
            birth_date = contact.get('birth_date', '').strip()
            email = contact.get('email', '').strip() or default_email

            if not name or not birth_date:
                continue

            if not is_valid_date(birth_date):
                continue

            birthday_data = BirthdayCreate(
                name=name,
                birth_date=birth_date,
                is_lunar=False,
                email=email
            )
            create_birthday(db, birthday_data, user_id)
            count += 1
        except Exception:
            continue

    return count
