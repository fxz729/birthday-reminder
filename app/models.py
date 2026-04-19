from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reminders = relationship("Reminder", back_populates="birthday", cascade="all, delete-orphan")


class Reminder(Base):
    """提醒配置"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    birthday_id = Column(Integer, ForeignKey("birthdays.id"), nullable=False)
    days_before = Column(Integer, default=0)  # 0=当天, 7=提前7天
    cron_time = Column(String(50), default="0 9 * * *")  # 默认每天9点
    is_enabled = Column(Boolean, default=True)
    template = Column(Text, nullable=True)  # 自定义模板

    birthday = relationship("Birthday", back_populates="reminders")
