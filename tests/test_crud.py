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
    """创建生日（使用默认 user_id=1）"""
    birthday = BirthdayCreate(
        name="张三",
        birth_date="1990-05-15",
        is_lunar=False,
        email="test@example.com"
    )
    result = crud.create_birthday(db, birthday, user_id=1)
    assert result.id is not None
    assert result.name == "张三"
    assert result.email == "test@example.com"
    assert result.user_id == 1


def test_get_birthday(db):
    """获取单个生日"""
    birthday = BirthdayCreate(
        name="李四",
        birth_date="1995-03-20",
        is_lunar=True,
        email="li@example.com"
    )
    created = crud.create_birthday(db, birthday, user_id=1)
    result = crud.get_birthday(db, created.id, user_id=1)
    assert result.name == "李四"
    assert result.is_lunar is True


def test_get_birthdays(db):
    """获取生日列表（按用户隔离）"""
    crud.create_birthday(db, BirthdayCreate(
        name="王五", birth_date="1988-12-01", is_lunar=False, email="wang@example.com"
    ), user_id=1)
    crud.create_birthday(db, BirthdayCreate(
        name="赵六", birth_date="1992-08-10", is_lunar=False, email="zhao@example.com"
    ), user_id=2)  # 不同用户
    crud.create_birthday(db, BirthdayCreate(
        name="孙七", birth_date="1993-09-15", is_lunar=False, email="sun@example.com"
    ), user_id=1)  # 同用户

    # 获取用户1的生日
    results = crud.get_birthdays(db, user_id=1)
    assert len(results) == 2

    # 获取所有生日
    all_results = crud.get_birthdays(db)
    assert len(all_results) == 3


def test_update_birthday(db):
    """更新生日"""
    created = crud.create_birthday(db, BirthdayCreate(
        name="测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ), user_id=1)
    update = BirthdayUpdate(name="新名字", gift_idea="礼物")
    result = crud.update_birthday(db, created.id, update, user_id=1)
    assert result.name == "新名字"
    assert result.gift_idea == "礼物"


def test_delete_birthday(db):
    """删除生日"""
    created = crud.create_birthday(db, BirthdayCreate(
        name="删除测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ), user_id=1)
    assert crud.delete_birthday(db, created.id, user_id=1) is True
    assert crud.get_birthday(db, created.id, user_id=1) is None


def test_create_reminder(db):
    """创建提醒"""
    birthday = crud.create_birthday(db, BirthdayCreate(
        name="赵六", birth_date="1992-08-10", is_lunar=False, email="zhao@example.com"
    ), user_id=1)
    reminder = ReminderCreate(days_before=7, cron_time="0 9 * * *")
    result = crud.create_reminder(db, birthday.id, reminder)
    assert result.id is not None
    assert result.days_before == 7
    assert result.birthday_id == birthday.id


def test_get_reminders_for_birthday(db):
    """获取生日的提醒列表"""
    birthday = crud.create_birthday(db, BirthdayCreate(
        name="测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ), user_id=1)
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=7))
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=0))
    reminders = crud.get_reminders_for_birthday(db, birthday.id)
    assert len(reminders) == 2


def test_get_enabled_reminders(db):
    """获取启用的提醒"""
    birthday = crud.create_birthday(db, BirthdayCreate(
        name="测试", birth_date="1990-01-01", is_lunar=False, email="test@example.com"
    ), user_id=1)
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=7, is_enabled=True))
    crud.create_reminder(db, birthday.id, ReminderCreate(days_before=0, is_enabled=False))
    enabled = crud.get_enabled_reminders(db)
    assert len(enabled) == 1
    assert enabled[0].days_before == 7
