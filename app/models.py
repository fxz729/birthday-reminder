from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# 生日-分类关联表
birthday_categories = Table(
    'birthday_categories',
    Base.metadata,
    Column('birthday_id', Integer, ForeignKey('birthdays.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    birthdays = relationship("Birthday", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    """生日分类"""
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_category_user_name'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(20), default="#667eea")  # UI 显示颜色
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="categories")
    birthdays = relationship("Birthday", secondary=birthday_categories, back_populates="categories")


class Birthday(Base):
    """生日对象"""
    __tablename__ = "birthdays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(String(10), nullable=False)  # 存储为 YYYY-MM-DD
    is_lunar = Column(Boolean, default=False)
    email = Column(String(255), nullable=False)
    gift_idea = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="birthdays")
    reminders = relationship("Reminder", back_populates="birthday", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=birthday_categories, back_populates="birthdays")


class Reminder(Base):
    """提醒配置"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    birthday_id = Column(Integer, ForeignKey("birthdays.id"), nullable=False)
    days_before = Column(Integer, default=0)  # 0=当天, 7=提前7天
    cron_time = Column(String(50), default="0 9 * * *")  # 默认每天9点
    is_enabled = Column(Boolean, default=True)
    template = Column(Text, nullable=True)  # 自定义模板
    notification_type = Column(String(20), default="email")  # email / serverchan

    birthday = relationship("Birthday", back_populates="reminders")
