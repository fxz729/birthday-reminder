import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Birthday, Category, birthday_categories


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


@pytest.fixture
def category(db, user):
    """创建测试分类"""
    cat = Category(
        name="家人",
        color="#FF5733",
        user_id=user.id
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


class TestCategoryModel:
    """Category 模型测试"""

    def test_create_category(self, db, user):
        """创建分类"""
        cat = Category(
            name="朋友",
            color="#3498DB",
            user_id=user.id
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)

        assert cat.id is not None
        assert cat.name == "朋友"
        assert cat.color == "#3498DB"
        assert cat.user_id == user.id

    def test_category_belongs_to_user(self, db, user):
        """分类属于用户"""
        cat = Category(name="同事", color="#27AE60", user_id=user.id)
        db.add(cat)
        db.commit()

        user_categories = db.query(Category).filter(Category.user_id == user.id).all()
        assert len(user_categories) >= 1
        assert cat in user_categories

    def test_category_name_unique_per_user(self, db, user):
        """同一用户分类名唯一"""
        cat1 = Category(name="家人", color="#FF0000", user_id=user.id)
        db.add(cat1)
        db.commit()

        cat2 = Category(name="家人", color="#00FF00", user_id=user.id)
        db.add(cat2)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_different_users_same_category_name(self, db, user):
        """不同用户可以有同名分类"""
        user2 = User(username="user2", email="user2@example.com", password_hash="$2b$12$test")
        db.add(user2)
        db.commit()

        cat1 = Category(name="家人", color="#FF0000", user_id=user.id)
        cat2 = Category(name="家人", color="#00FF00", user_id=user2.id)
        db.add(cat1)
        db.add(cat2)
        db.commit()

        assert cat1.id is not None
        assert cat2.id is not None


class TestBirthdayCategoryRelation:
    """Birthday-Category 多对多关系测试"""

    def test_birthday_has_categories(self, db, user, category):
        """生日可以属于多个分类"""
        birthday = Birthday(
            name="张三",
            birth_date="1990-05-15",
            is_lunar=False,
            email="zhang@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        # 建立关系
        db.execute(birthday_categories.insert().values(birthday_id=birthday.id, category_id=category.id))
        db.commit()

        # 刷新
        db.refresh(birthday)
        db.refresh(category)

        assert category in birthday.categories
        assert birthday in category.birthdays

    def test_birthday_multiple_categories(self, db, user):
        """生日可属于多个分类"""
        cat1 = Category(name="家人", color="#FF0000", user_id=user.id)
        cat2 = Category(name="亲戚", color="#00FF00", user_id=user.id)
        db.add_all([cat1, cat2])
        db.commit()

        birthday = Birthday(
            name="李四",
            birth_date="1985-03-20",
            is_lunar=False,
            email="li@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        db.execute(birthday_categories.insert().values(birthday_id=birthday.id, category_id=cat1.id))
        db.execute(birthday_categories.insert().values(birthday_id=birthday.id, category_id=cat2.id))
        db.commit()

        db.refresh(birthday)
        assert len(birthday.categories) == 2
        assert cat1 in birthday.categories
        assert cat2 in birthday.categories

    def test_category_has_multiple_birthdays(self, db, user, category):
        """分类可包含多个生日"""
        b1 = Birthday(
            name="王五",
            birth_date="1992-01-01",
            is_lunar=False,
            email="wang@example.com",
            user_id=user.id
        )
        b2 = Birthday(
            name="赵六",
            birth_date="1988-06-15",
            is_lunar=False,
            email="zhao@example.com",
            user_id=user.id
        )
        db.add_all([b1, b2])
        db.commit()

        db.execute(birthday_categories.insert().values(birthday_id=b1.id, category_id=category.id))
        db.execute(birthday_categories.insert().values(birthday_id=b2.id, category_id=category.id))
        db.commit()

        db.refresh(category)
        assert len(category.birthdays) == 2
        assert b1 in category.birthdays
        assert b2 in category.birthdays


class TestCategoryCRUD:
    """分类 CRUD 测试"""

    def test_get_categories_by_user(self, db, user):
        """获取用户的所有分类"""
        db.add_all([
            Category(name="家人", color="#FF0000", user_id=user.id),
            Category(name="朋友", color="#00FF00", user_id=user.id),
            Category(name="同事", color="#0000FF", user_id=user.id),
        ])
        db.commit()

        from app.crud import get_categories_by_user
        categories = get_categories_by_user(db, user.id)
        assert len(categories) == 3

    def test_create_category_crud(self, db, user):
        """通过 CRUD 创建分类"""
        from app.crud import create_category

        cat = create_category(db, user.id, "客户", "#9B59B6")
        assert cat.id is not None
        assert cat.name == "客户"
        assert cat.color == "#9B59B6"

    def test_delete_category(self, db, user, category):
        """删除分类（关系也删除）"""
        from app.crud import delete_category

        # 添加生日关联
        birthday = Birthday(
            name="测试",
            birth_date="1990-01-01",
            is_lunar=False,
            email="test@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()
        db.execute(birthday_categories.insert().values(birthday_id=birthday.id, category_id=category.id))
        db.commit()

        result = delete_category(db, category.id, user.id)
        assert result is True
        assert db.query(Category).filter(Category.id == category.id).first() is None
        assert db.execute(birthday_categories.select().where(birthday_categories.c.category_id == category.id)).fetchone() is None
