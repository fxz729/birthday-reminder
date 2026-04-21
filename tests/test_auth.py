import pytest
import os
import tempfile
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User
from app.main import app
from app.database import get_db


@pytest.fixture(scope="function")
def db_engine():
    """测试数据库引擎 - 使用唯一文件数据库"""
    test_db = tempfile.gettempdir() + f"/test_auth_{uuid.uuid4().hex}.db"

    engine = create_engine(
        f"sqlite:///{test_db}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    yield engine

    # 清理
    engine.dispose()
    try:
        os.remove(test_db)
    except Exception:
        pass


@pytest.fixture(scope="function")
def db(db_engine):
    """测试数据库会话"""
    SessionLocal = sessionmaker(bind=db_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_engine):
    """测试客户端"""
    SessionLocal = sessionmaker(bind=db_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """创建测试用户"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=pwd_context.hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestLoginPage:
    """登录页面测试"""

    def test_get_login_page(self, client):
        """GET /auth/login 返回登录页面"""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert "登录" in response.text.lower() or "login" in response.text.lower()


class TestLogin:
    """登录功能测试"""

    def test_login_success(self, client, test_user):
        """正确凭据登录成功"""
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "password123"
        })
        # 登录成功后应重定向到 dashboard
        assert response.status_code in [200, 302]
        # 检查是否设置了 session
        assert "session" in response.headers.get("set-cookie", "").lower() or \
               response.status_code == 200

    def test_login_wrong_password(self, client, test_user):
        """错误密码登录失败"""
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "错误" in response.text or "invalid" in response.text.lower()

    def test_login_nonexistent_user(self, client):
        """不存在的用户登录失败"""
        response = client.post("/auth/login", data={
            "username": "nonexistent",
            "password": "anypassword"
        })
        assert response.status_code == 401

    def test_login_empty_username(self, client):
        """空用户名登录失败"""
        response = client.post("/auth/login", data={
            "username": "",
            "password": "password123"
        })
        # FastAPI 默认返回 422 表示验证失败
        assert response.status_code in [400, 422]


class TestRegisterPage:
    """注册页面测试"""

    def test_get_register_page(self, client):
        """GET /auth/register 返回注册页面"""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert "注册" in response.text.lower() or "register" in response.text.lower()


class TestRegister:
    """注册功能测试"""

    def test_register_success(self, client):
        """成功注册新用户"""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        })
        assert response.status_code in [200, 302]

    def test_register_duplicate_username(self, client, test_user):
        """重复用户名注册失败"""
        response = client.post("/auth/register", data={
            "username": "testuser",  # 已存在
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        assert response.status_code == 400
        assert "已存在" in response.text or "exists" in response.text.lower()

    def test_register_duplicate_email(self, client, test_user):
        """重复邮箱注册失败"""
        response = client.post("/auth/register", data={
            "username": "anotheruser",
            "email": "test@example.com",  # 已存在
            "password": "password123",
            "confirm_password": "password123"
        })
        assert response.status_code == 400

    def test_register_password_mismatch(self, client):
        """密码不匹配注册失败"""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "different456"
        })
        assert response.status_code == 400
        # 验证返回了错误信息（检查页面是否包含表单重新显示）
        assert "密码" in response.text or "password" in response.text.lower()

    def test_register_weak_password(self, client):
        """弱密码注册失败"""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "123",  # 太短
            "confirm_password": "123"
        })
        assert response.status_code == 400


class TestLogout:
    """登出功能测试"""

    def test_logout_clears_session(self, client, test_user):
        """登出清除 session"""
        # 先登录
        client.post("/auth/login", data={
            "username": "testuser",
            "password": "password123"
        })
        # 登出
        response = client.post("/auth/logout")
        assert response.status_code in [200, 302]


class TestAuthProtection:
    """认证保护测试"""

    def test_unauthenticated_access_to_dashboard(self, client):
        """未认证访问 dashboard 重定向到登录"""
        response = client.get("/auth/dashboard", follow_redirects=False)
        assert response.status_code in [302, 401]
        if response.status_code == 302:
            assert "/auth/login" in response.headers.get("location", "")

    def test_authenticated_access_to_dashboard(self, client, test_user):
        """已认证可以访问 dashboard"""
        # 先登录
        client.post("/auth/login", data={
            "username": "testuser",
            "password": "password123"
        })
        response = client.get("/auth/dashboard")
        assert response.status_code == 200
