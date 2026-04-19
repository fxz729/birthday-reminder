import pytest
from sqlalchemy import inspect, text
from app.database import engine, Base, init_db


def test_database_connection():
    """测试数据库连接"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_tables_created():
    """测试表是否创建"""
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "birthdays" in tables
    assert "reminders" in tables
