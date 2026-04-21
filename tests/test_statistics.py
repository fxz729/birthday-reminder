import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Birthday, Category


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


class TestStatistics:
    """统计功能测试"""

    def test_get_total_birthdays(self, db, user):
        """获取生日总数"""
        from app.services.statistics import get_total_birthdays

        assert get_total_birthdays(db, user.id) == 0

        # 添加生日
        b = Birthday(
            name="张三", birth_date="1990-01-01",
            is_lunar=False, email="test@example.com", user_id=user.id
        )
        db.add(b)
        db.commit()

        assert get_total_birthdays(db, user.id) == 1

    def test_get_birthdays_this_month(self, db, user):
        """获取本月生日"""
        from app.services.statistics import get_birthdays_this_month

        today = date.today()
        month = today.month

        # 添加本月生日
        b1 = Birthday(
            name="本月", birth_date=f"1990-{month:02d}-15",
            is_lunar=False, email="b1@example.com", user_id=user.id
        )
        db.add(b1)

        # 添加其他月生日
        other_month = (month % 12) + 1
        b2 = Birthday(
            name="下月", birth_date=f"1990-{other_month:02d}-15",
            is_lunar=False, email="b2@example.com", user_id=user.id
        )
        db.add(b2)
        db.commit()

        results = get_birthdays_this_month(db, user.id)
        assert len(results) == 1
        assert results[0].name == "本月"

    def test_get_upcoming_birthdays(self, db, user):
        """获取即将到来的生日"""
        from app.services.statistics import get_upcoming_birthdays

        today = date.today()

        # 今天生日
        b1 = Birthday(
            name="今天", birth_date=today.strftime("%Y-%m-%d"),
            is_lunar=False, email="today@example.com", user_id=user.id
        )
        db.add(b1)

        # 7天后生日
        b2 = Birthday(
            name="七天后", birth_date=(today + timedelta(days=7)).strftime("%Y-%m-%d"),
            is_lunar=False, email="week@example.com", user_id=user.id
        )
        db.add(b2)

        # 30天后生日
        b3 = Birthday(
            name="三十天后", birth_date=(today + timedelta(days=30)).strftime("%Y-%m-%d"),
            is_lunar=False, email="month@example.com", user_id=user.id
        )
        db.add(b3)
        db.commit()

        # 获取7天内
        upcoming = get_upcoming_birthdays(db, user.id, days=7)
        assert len(upcoming) == 2

    def test_get_category_stats(self, db, user):
        """获取分类统计"""
        from app.services.statistics import get_category_stats
        from app.models import birthday_categories
        from app.crud import create_category

        cat1 = create_category(db, user.id, "家人", "#FF0000")
        cat2 = create_category(db, user.id, "朋友", "#00FF00")

        b1 = Birthday(
            name="家人1", birth_date="1990-01-01",
            is_lunar=False, email="f1@example.com", user_id=user.id
        )
        b2 = Birthday(
            name="家人2", birth_date="1990-01-15",
            is_lunar=False, email="f2@example.com", user_id=user.id
        )
        b3 = Birthday(
            name="朋友1", birth_date="1990-02-01",
            is_lunar=False, email="p1@example.com", user_id=user.id
        )
        db.add_all([b1, b2, b3])
        db.commit()

        # 关联
        db.execute(birthday_categories.insert().values(birthday_id=b1.id, category_id=cat1.id))
        db.execute(birthday_categories.insert().values(birthday_id=b2.id, category_id=cat1.id))
        db.execute(birthday_categories.insert().values(birthday_id=b3.id, category_id=cat2.id))
        db.commit()

        stats = get_category_stats(db, user.id)
        assert stats["家人"] == 2
        assert stats["朋友"] == 1
        assert stats["未分类"] == 0

    def test_get_lunar_vs_solar_stats(self, db, user):
        """获取农历/公历统计"""
        from app.services.statistics import get_lunar_solar_stats

        b1 = Birthday(
            name="公历", birth_date="1990-01-01",
            is_lunar=False, email="solar@example.com", user_id=user.id
        )
        b2 = Birthday(
            name="农历", birth_date="1990-01-01",
            is_lunar=True, email="lunar@example.com", user_id=user.id
        )
        db.add_all([b1, b2])
        db.commit()

        stats = get_lunar_solar_stats(db, user.id)
        assert stats["solar"] == 1
        assert stats["lunar"] == 1

    def test_get_birthday_heatmap_data(self, db, user):
        """获取生日热力图数据"""
        from app.services.statistics import get_birthday_heatmap_data

        # 添加分布在各月的生日
        for month in range(1, 13):
            b = Birthday(
                name=f"月{month}", birth_date=f"1990-{month:02d}-15",
                is_lunar=False, email=f"m{month}@example.com", user_id=user.id
            )
            db.add(b)
        db.commit()

        heatmap = get_birthday_heatmap_data(db, user.id)
        assert len(heatmap) == 12
        for month, count in heatmap.items():
            assert count == 1

    def test_statistics_isolation_by_user(self, db, user):
        """统计按用户隔离"""
        from app.services.statistics import get_total_birthdays

        # 当前用户
        b1 = Birthday(
            name="用户1", birth_date="1990-01-01",
            is_lunar=False, email="u1@example.com", user_id=user.id
        )
        db.add(b1)

        # 另一用户
        other_user = User(username="other", email="other@example.com", password_hash="hash")
        db.add(other_user)
        db.commit()

        b2 = Birthday(
            name="用户2", birth_date="1990-01-01",
            is_lunar=False, email="u2@example.com", user_id=other_user.id
        )
        db.add(b2)
        db.commit()

        assert get_total_birthdays(db, user.id) == 1
        assert get_total_birthdays(db, other_user.id) == 1
