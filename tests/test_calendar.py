import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Birthday


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


@pytest.fixture
def user(db):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$test"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestICSCalendar:
    """iCalendar 格式测试"""

    def test_generate_ics_header(self):
        """生成 ICS 头部"""
        from app.services.calendar_sync import generate_ics_header

        ics = generate_ics_header()
        assert "BEGIN:VCALENDAR" in ics
        assert "VERSION:2.0" in ics
        assert "PRODID:-//Birthday Reminder//" in ics

    def test_generate_ics_event(self):
        """生成 ICS 事件"""
        from app.services.calendar_sync import generate_ics_event

        event = generate_ics_event(
            uid="test-123",
            summary="张三的生日",
            description="张三 35 岁了！",
            start_date="1990-05-15",
            end_date="1990-05-16"
        )

        assert "BEGIN:VEVENT" in event
        assert "END:VEVENT" in event
        assert "UID:test-123" in event
        assert "SUMMARY:张三的生日" in event

    def test_generate_ics_event_with_recurrence(self):
        """生成带重复的事件"""
        from app.services.calendar_sync import generate_ics_event

        event = generate_ics_event(
            uid="test-456",
            summary="生日提醒",
            description="提醒",
            start_date="1990-05-15",
            end_date="1990-05-16",
            recurrence="YEARLY"
        )

        assert "RRULE:FREQ=YEARLY" in event

    def test_generate_ics_footer(self):
        """生成 ICS 尾部"""
        from app.services.calendar_sync import generate_ics_footer

        footer = generate_ics_footer()
        assert "END:VCALENDAR" in footer


class TestBirthdayToICS:
    """生日转 ICS 测试"""

    def test_birthday_to_ics(self, db, user):
        """生日转换为 ICS 格式"""
        from app.services.calendar_sync import birthday_to_ics

        birthday = Birthday(
            name="张三",
            birth_date="1990-05-15",
            is_lunar=False,
            email="zhang@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        ics = birthday_to_ics(birthday)

        assert "BEGIN:VEVENT" in ics
        assert "SUMMARY:张三的生日" in ics or "SUMMARY:张三生日" in ics
        assert "RRULE:FREQ=YEARLY" in ics

    def test_generate_user_calendar(self, db, user):
        """生成用户完整日历"""
        from app.services.calendar_sync import generate_user_calendar

        # 添加多个生日
        birthdays = [
            Birthday(name="张三", birth_date="1990-05-15", is_lunar=False, email="z1@example.com", user_id=user.id),
            Birthday(name="李四", birth_date="1985-03-20", is_lunar=False, email="l1@example.com", user_id=user.id),
        ]
        db.add_all(birthdays)
        db.commit()

        ics = generate_user_calendar(db, user.id)

        assert "BEGIN:VCALENDAR" in ics
        assert "END:VCALENDAR" in ics
        assert birthdays[0].name in ics
        assert birthdays[1].name in ics


class TestWebCal:
    """WebCal 订阅测试"""

    def test_webcal_url_generation(self, db, user):
        """生成 WebCal URL"""
        from app.services.calendar_sync import generate_webcal_url

        url = generate_webcal_url(user.id, "abc123token")
        assert url.startswith("webcal://")
        assert str(user.id) in url

    def test_generate_calendar_link(self, db, user):
        """生成日历下载链接"""
        from app.services.calendar_sync import generate_calendar_link

        link = generate_calendar_link(user.id, "secret123")
        assert "/calendar/download" in link
        assert "token=secret123" in link
