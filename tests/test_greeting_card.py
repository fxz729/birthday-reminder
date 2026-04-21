import pytest
import os
import tempfile
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


class TestGreetingCardGeneration:
    """贺卡生成测试"""

    def test_create_basic_card(self):
        """创建基础贺卡"""
        from app.services.greeting_card import GreetingCardGenerator

        card = GreetingCardGenerator()
        card.create(
            name="张三",
            age=30,
            zodiac="龙",
            output_path=None  # 返回 bytes
        )
        image_bytes = card.get_image_bytes()
        assert image_bytes is not None
        assert len(image_bytes) > 0
        # PNG 签名
        assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n'

    def test_card_with_template(self):
        """使用模板创建贺卡"""
        from app.services.greeting_card import GreetingCardGenerator

        templates = GreetingCardGenerator.get_available_templates()
        assert len(templates) > 0

    def test_card_with_color_scheme(self):
        """使用配色方案"""
        from app.services.greeting_card import GreetingCardGenerator

        card = GreetingCardGenerator()
        card.create(
            name="李四",
            age=25,
            color_scheme="pink",
            output_path=None
        )
        image_bytes = card.get_image_bytes()
        assert image_bytes is not None


class TestGreetingCardFromBirthday:
    """从生日创建贺卡测试"""

    def test_generate_card_from_birthday(self, db, user):
        """从生日对象生成贺卡"""
        from app.services.greeting_card import generate_card_from_birthday

        birthday = Birthday(
            name="王五",
            birth_date="1995-06-15",
            is_lunar=False,
            email="wang@example.com",
            user_id=user.id
        )
        db.add(birthday)
        db.commit()

        image_bytes = generate_card_from_birthday(birthday)
        assert image_bytes is not None
        assert len(image_bytes) > 0

    def test_generate_card_with_zodiac(self, db, user):
        """生成带生肖的贺卡"""
        from app.services.greeting_card import generate_card_with_zodiac

        image_bytes = generate_card_with_zodiac(
            name="赵六",
            age=28,
            zodiac="虎"
        )
        assert image_bytes is not None

    def test_generate_card_with_constellation(self, db, user):
        """生成带星座的贺卡"""
        from app.services.greeting_card import generate_card_with_constellation

        image_bytes = generate_card_with_constellation(
            name="孙七",
            age=22,
            constellation="双子座"
        )
        assert image_bytes is not None


class TestGreetingCardTemplates:
    """贺卡模板测试"""

    def test_get_templates(self):
        """获取可用模板"""
        from app.services.greeting_card import GreetingCardGenerator

        templates = GreetingCardGenerator.get_available_templates()
        assert "classic" in templates
        assert "modern" in templates

    def test_template_exists(self):
        """检查模板是否存在"""
        from app.services.greeting_card import GreetingCardGenerator

        assert GreetingCardGenerator.template_exists("classic")
        assert not GreetingCardGenerator.template_exists("nonexistent")

    def test_get_color_schemes(self):
        """获取配色方案"""
        from app.services.greeting_card import GreetingCardGenerator

        schemes = GreetingCardGenerator.get_color_schemes()
        assert len(schemes) > 0
        assert "default" in schemes
        assert "pink" in schemes


class TestGreetingCardEdgeCases:
    """边界情况测试"""

    def test_card_with_long_name(self):
        """长名字处理"""
        from app.services.greeting_card import GreetingCardGenerator

        card = GreetingCardGenerator()
        card.create(
            name="这是一个非常非常长的名字" * 3,
            age=30,
            output_path=None
        )
        image_bytes = card.get_image_bytes()
        assert image_bytes is not None

    def test_card_with_special_chars(self):
        """特殊字符处理"""
        from app.services.greeting_card import GreetingCardGenerator

        card = GreetingCardGenerator()
        card.create(
            name="张三·李四",
            age=25,
            output_path=None
        )
        image_bytes = card.get_image_bytes()
        assert image_bytes is not None

    def test_card_age_zero(self):
        """零岁处理"""
        from app.services.greeting_card import GreetingCardGenerator

        card = GreetingCardGenerator()
        card.create(
            name="婴儿",
            age=0,
            output_path=None
        )
        image_bytes = card.get_image_bytes()
        assert image_bytes is not None
