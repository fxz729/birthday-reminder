import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import crud
from app.schemas import BirthdayCreate, BirthdayUpdate, ReminderCreate


@pytest.fixture
def db():
    """测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_birthday(db):
    birthday = BirthdayCreate(
        name="张三",
        birth_date="1990-05-15",
        is_lunar=False,
        email="test@example.com"
    )
    result = crud.create_birthday(db, birthday)
    assert result.id is not None
    assert result.name == "张三"
    assert result.email == "test@example.com"


def test_get_birthday(db):
    birthday = BirthdayCreate(
        name="李四",
        birth_date="1995-03-20",
        is_lunar=True,
        email="li@example.com"
    )
    created = crud.create_birthday(db, birthday)
    result = crud.get_birthday(db, created.id)
    assert result.name == "李四"
    assert result.is_lunar is True


def test_get_birthdays(db):
    crud.create_birthday(db, BirthdayCreate(
        name="王五", birth_date="1988-12-01", is_lunar=False, email="wang@example.com"
    ))
    crud.create_birthday(db, BirthdayCreate(
        name="赵六", birth_date="1992-08-10", is_lunar=False, email="zhao@example.com"
    ))
    results = crud.get_birthdays(db)
    assert len(results) == 2


def test_update_birthday(db):
    created = crud.create_birthday(db, BirthdayCreate(
        name="测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ))
    update = BirthdayUpdate(name="新名字", gift_idea="礼物")
    result = crud.update_birthday(db, created.id, update)
    assert result.name == "新名字"
    assert result.gift_idea == "礼物"


def test_delete_birthday(db):
    created = crud.create_birthday(db, BirthdayCreate(
        name="删除测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ))
    assert crud.delete_birthday(db, created.id) is True
    assert crud.get_birthday(db, created.id) is None


def test_create_reminder(db):
    birthday = crud.create_birthday(db, BirthdayCreate(
        name="赵六", birth_date="1992-08-10", is_lunar=False, email="zhao@example.com"
    ))
    reminder = ReminderCreate(days_before=7, cron_time="0 9 * * *")
    result = crud.create_reminder(db, birthday.id, reminder)
    assert result.id is not None
    assert result.days_before == 7
    assert result.birthday_id == birthday.id


def test_get_reminders_for_birthday(db):
    birthday = crud.create_birthday(db, BirthdayCreate(
        name="测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ))
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=7))
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=0))
    reminders = crud.get_reminders_for_birthday(db, birthday.id)
    assert len(reminders) == 2


def test_get_enabled_reminders(db):
    birthday = crud.create_birthday(db, BirthdayCreate(
        name="测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ))
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=7, is_enabled=True))
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=0, is_enabled=False))
    enabled = crud.get_enabled_reminders(db)
    assert len(enabled) == 1
    assert enabled[0].days_before == 7
