from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Birthday, Reminder, User, Category
from app.schemas import BirthdayCreate, BirthdayUpdate, ReminderCreate


def get_birthday(db: Session, birthday_id: int, user_id: Optional[int] = None) -> Optional[Birthday]:
    query = db.query(Birthday).filter(Birthday.id == birthday_id)
    if user_id is not None:
        query = query.filter(Birthday.user_id == user_id)
    return query.first()


def get_birthdays(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Birthday]:
    query = db.query(Birthday)
    if user_id is not None:
        query = query.filter(Birthday.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def get_birthday_by_name(db: Session, name: str, user_id: Optional[int] = None) -> Optional[Birthday]:
    query = db.query(Birthday).filter(Birthday.name == name)
    if user_id is not None:
        query = query.filter(Birthday.user_id == user_id)
    return query.first()


def create_birthday(db: Session, birthday: BirthdayCreate, user_id: int) -> Birthday:
    db_birthday = Birthday(**birthday.model_dump(), user_id=user_id)
    db.add(db_birthday)
    db.commit()
    db.refresh(db_birthday)
    return db_birthday


def update_birthday(db: Session, birthday_id: int, birthday: BirthdayUpdate, user_id: Optional[int] = None) -> Optional[Birthday]:
    db_birthday = get_birthday(db, birthday_id, user_id)
    if not db_birthday:
        return None
    update_data = birthday.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_birthday, key, value)
    db.commit()
    db.refresh(db_birthday)
    return db_birthday


def delete_birthday(db: Session, birthday_id: int, user_id: Optional[int] = None) -> bool:
    db_birthday = get_birthday(db, birthday_id, user_id)
    if not db_birthday:
        return False
    db.delete(db_birthday)
    db.commit()
    return True


def get_reminders_for_birthday(db: Session, birthday_id: int) -> List[Reminder]:
    return db.query(Reminder).filter(Reminder.birthday_id == birthday_id).all()


def get_enabled_reminders(db: Session) -> List[Reminder]:
    return db.query(Reminder).filter(Reminder.is_enabled == True).all()


def create_reminder(db: Session, birthday_id: int, reminder: ReminderCreate) -> Reminder:
    db_reminder = Reminder(birthday_id=birthday_id, **reminder.model_dump())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def update_reminder(db: Session, reminder_id: int, reminder: ReminderCreate) -> Optional[Reminder]:
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not db_reminder:
        return None
    for key, value in reminder.model_dump().items():
        setattr(db_reminder, key, value)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def delete_reminder(db: Session, reminder_id: int) -> bool:
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not db_reminder:
        return False
    db.delete(db_reminder)
    db.commit()
    return True


def bulk_create_reminders(db: Session, birthday_id: int, reminders: List[ReminderCreate]) -> List[Reminder]:
    """批量创建提醒"""
    db_reminders = [Reminder(birthday_id=birthday_id, **r.model_dump()) for r in reminders]
    db.add_all(db_reminders)
    db.commit()
    for r in db_reminders:
        db.refresh(r)
    return db_reminders


# 用户相关 CRUD
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    user = User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 分类相关 CRUD
def get_categories_by_user(db: Session, user_id: int) -> List[Category]:
    return db.query(Category).filter(Category.user_id == user_id).all()


def get_category_by_id(db: Session, category_id: int, user_id: Optional[int] = None) -> Optional[Category]:
    query = db.query(Category).filter(Category.id == category_id)
    if user_id is not None:
        query = query.filter(Category.user_id == user_id)
    return query.first()


def create_category(db: Session, user_id: int, name: str, color: str = "#667eea") -> Category:
    category = Category(name=name, color=color, user_id=user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, name: Optional[str] = None,
                   color: Optional[str] = None, user_id: Optional[int] = None) -> Optional[Category]:
    category = get_category_by_id(db, category_id, user_id)
    if not category:
        return None
    if name is not None:
        category.name = name
    if color is not None:
        category.color = color
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int, user_id: Optional[int] = None) -> bool:
    category = get_category_by_id(db, category_id, user_id)
    if not category:
        return False
    db.delete(category)
    db.commit()
    return True


def add_birthday_to_category(db: Session, birthday_id: int, category_id: int) -> bool:
    """将生日添加到分类"""
    from app.models import birthday_categories
    existing = db.execute(
        birthday_categories.select().where(
            birthday_categories.c.birthday_id == birthday_id,
            birthday_categories.c.category_id == category_id
        )
    ).fetchone()
    if existing:
        return True
    db.execute(birthday_categories.insert().values(birthday_id=birthday_id, category_id=category_id))
    db.commit()
    return True


def remove_birthday_from_category(db: Session, birthday_id: int, category_id: int) -> bool:
    """从分类移除生日"""
    from app.models import birthday_categories
    result = db.execute(
        birthday_categories.delete().where(
            birthday_categories.c.birthday_id == birthday_id,
            birthday_categories.c.category_id == category_id
        )
    )
    db.commit()
    return result.rowcount > 0


# 通知日志 CRUD
def create_notification_log(db: Session, birthday_id: int, user_id: int,
                             notification_type: str, recipient: str,
                             status: str = "success", subject: str = None,
                             error_message: str = None, reminder_id: int = None):
    """记录通知发送"""
    from app.models import NotificationLog
    log = NotificationLog(
        birthday_id=birthday_id,
        user_id=user_id,
        reminder_id=reminder_id,
        notification_type=notification_type,
        recipient=recipient,
        subject=subject,
        status=status,
        error_message=error_message,
    )
    db.add(log)
    db.commit()


def get_notification_logs(db: Session, user_id: int, limit: int = 20) -> list:
    """获取用户最近的发送记录"""
    from app.models import NotificationLog
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.user_id == user_id)
        .order_by(NotificationLog.created_at.desc())
        .limit(limit)
        .all()
    )
