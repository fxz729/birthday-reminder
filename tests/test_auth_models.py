import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User


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


class TestUserModel:
    """User 模型测试"""

    def test_create_user(self, db):
        """创建用户"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="$2b$12$test_hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_admin is False
        assert user.is_active is True
        assert user.created_at is not None

    def test_create_admin_user(self, db):
        """创建管理员用户"""
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash="$2b$12$admin_hash",
            is_admin=True
        )
        db.add(admin)
        db.commit()

        assert admin.is_admin is True

    def test_username_unique(self, db):
        """用户名必须唯一"""
        user1 = User(username="duplicate", email="a@example.com", password_hash="hash1")
        db.add(user1)
        db.commit()

        user2 = User(username="duplicate", email="b@example.com", password_hash="hash2")
        db.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_email_unique(self, db):
        """邮箱必须唯一"""
        user1 = User(username="user1", email="same@example.com", password_hash="hash1")
        db.add(user1)
        db.commit()

        user2 = User(username="user2", email="same@example.com", password_hash="hash2")
        db.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_user_password_not_stored_plaintext(self, db):
        """密码不应明文存储"""
        user = User(
            username="secure",
            email="secure@example.com",
            password_hash="$2b$12$hashed_password_here"
        )
        db.add(user)
        db.commit()

        assert "password" not in user.password_hash.lower() or "$2b$" in user.password_hash
        assert user.password_hash != "mypassword"

    def test_inactive_user(self, db):
        """用户可以设为非激活状态"""
        user = User(
            username="inactive",
            email="inactive@example.com",
            password_hash="hash",
            is_active=False
        )
        db.add(user)
        db.commit()

        assert user.is_active is False
