import pytest
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


class TestLunarLeapMonthPolicy:
    """农历闰月策略测试"""

    def test_get_leap_month_options(self):
        """获取闰月选项"""
        from app.services.lunar import LunarService
        assert LunarService.get_leap_month_options() == ["auto", "before", "after"]

    def test_valid_lunar_birthday(self, db, user):
        """验证农历生日"""
        from app.services.lunar import LunarService

        birthday = Birthday(
            name="农历生日",
            birth_date="1990-05-15",
            is_lunar=True,
            email="test@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        is_valid, error = LunarService.validate_lunar_birthday(birthday.birth_date, "auto")
        assert is_valid

    def test_leap_month_before(self, db, user):
        """闰月取前"""
        from app.services.lunar import LunarService

        birthday = Birthday(
            name="闰月生日",
            birth_date="1990-04-15",
            is_lunar=True,
            email="test@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        is_valid, _ = LunarService.validate_lunar_birthday(birthday.birth_date, "before")
        assert is_valid

    def test_leap_month_after(self, db, user):
        """闰月取后"""
        from app.services.lunar import LunarService

        birthday = Birthday(
            name="闰月生日",
            birth_date="1990-04-15",
            is_lunar=True,
            email="test@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        is_valid, _ = LunarService.validate_lunar_birthday(birthday.birth_date, "after")
        assert is_valid


class TestLunarConversion:
    """农历转换测试"""

    def test_convert_lunar_to_solar(self):
        """农历转公历"""
        from app.services.lunar import LunarService

        lunar_date = "1990-05-15"
        result = LunarService.lunar_to_solar(lunar_date)
        assert result is not None
        solar_date, is_leap = result
        assert solar_date is not None
        assert isinstance(is_leap, bool)

    def test_convert_solar_to_lunar(self):
        """公历转农历"""
        from app.services.lunar import solar_to_lunar
        from datetime import date

        solar_date = date(1990, 6, 15)
        lunar_date = solar_to_lunar(solar_date)
        assert lunar_date is not None
        assert len(lunar_date) == 3


class TestBirthdayWithLunar:
    """生日农历处理测试"""

    def test_add_birthday_with_lunar(self, db, user):
        """添加农历生日"""
        from app.crud import create_birthday
        from app.schemas import BirthdayCreate

        birthday_data = BirthdayCreate(
            name="农历生日",
            birth_date="1990-04-15",
            is_lunar=True,
            email="test@example.com"
        )

        birthday = create_birthday(db, birthday_data, user.id)
        assert birthday.id is not None
        assert birthday.is_lunar is True

    def test_lunar_service_get_lunar(self):
        """获取农历信息"""
        from app.services.lunar import LunarService

        # 测试返回结构完整性
        lunar = LunarService.get_lunar("1990-06-15")
        assert lunar is not None
        assert 'lunar_year' in lunar
        assert 'lunar_month' in lunar
        assert 'lunar_day' in lunar
        assert 'month_chinese' in lunar
        assert 'day_chinese' in lunar
        assert 'sheng_xiao' in lunar
