from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Birthday, Reminder
from app.schemas import BirthdayCreate, BirthdayUpdate, ReminderCreate


def get_birthday(db: Session, birthday_id: int) -> Optional[Birthday]:
    return db.query(Birthday).filter(Birthday.id == birthday_id).first()


def get_birthdays(db: Session, skip: int = 0, limit: int = 100) -> List[Birthday]:
    return db.query(Birthday).offset(skip).limit(limit).all()


def get_birthday_by_name(db: Session, name: str) -> Optional[Birthday]:
    return db.query(Birthday).filter(Birthday.name == name).first()


def create_birthday(db: Session, birthday: BirthdayCreate) -> Birthday:
    db_birthday = Birthday(**birthday.model_dump())
    db.add(db_birthday)
    db.commit()
    db.refresh(db_birthday)
    return db_birthday


def update_birthday(db: Session, birthday_id: int, birthday: BirthdayUpdate) -> Optional[Birthday]:
    db_birthday = get_birthday(db, birthday_id)
    if not db_birthday:
        return None
    update_data = birthday.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_birthday, key, value)
    db.commit()
    db.refresh(db_birthday)
    return db_birthday


def delete_birthday(db: Session, birthday_id: int) -> bool:
    db_birthday = get_birthday(db, birthday_id)
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
