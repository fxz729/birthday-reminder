from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class ReminderBase(BaseModel):
    """提醒基础Schema"""
    days_before: int = Field(default=0, ge=0, le=365)
    cron_time: str = "0 9 * * *"
    is_enabled: bool = True
    template: Optional[str] = None
    notification_type: str = Field(default="email", pattern="^(email|serverchan)$")


class ReminderCreate(ReminderBase):
    pass


class ReminderResponse(ReminderBase):
    id: int
    birthday_id: int

    class Config:
        from_attributes = True


class BirthdayBase(BaseModel):
    """生日基础Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    is_lunar: bool = False
    email: EmailStr
    gift_idea: Optional[str] = None
    notes: Optional[str] = None


class BirthdayCreate(BirthdayBase):
    pass


class BirthdayUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    birth_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    is_lunar: Optional[bool] = None
    email: Optional[EmailStr] = None
    gift_idea: Optional[str] = None
    notes: Optional[str] = None


class BirthdayResponse(BirthdayBase):
    id: int
    created_at: datetime
    updated_at: datetime
    reminders: List[ReminderResponse] = []

    class Config:
        from_attributes = True
