import pytest
from datetime import date
from app.services.lunar import (
    solar_to_lunar,
    lunar_to_solar,
    calculate_age,
    days_until_birthday,
    get_lunar_date_string,
    month_to_chinese,
    day_to_chinese,
    get_upcoming_birthday_date
)


def test_solar_to_lunar():
    """测试公历转农历"""
    lunar_year, lunar_month, lunar_day = solar_to_lunar(date(2024, 2, 10))
    assert lunar_year == 2024
    assert lunar_month == 1
    assert lunar_day == 1


def test_lunar_to_solar():
    """测试农历转公历"""
    solar = lunar_to_solar(2024, 1, 1, 2024)
    assert solar == date(2024, 2, 10)


def test_calculate_age():
    """测试年龄计算"""
    birth = date(1990, 5, 15)
    today = date(2026, 4, 19)
    age = calculate_age(birth, today)
    assert age == 35


def test_calculate_age_already_had_birthday():
    """测试已过生日的年龄"""
    birth = date(1990, 4, 15)
    today = date(2026, 4, 19)
    age = calculate_age(birth, today)
    assert age == 36


def test_calculate_age_same_day():
    """测试生日当天"""
    birth = date(1990, 4, 19)
    today = date(2026, 4, 19)
    age = calculate_age(birth, today)
    assert age == 36


def test_days_until_birthday_tomorrow():
    """测试距离生日1天"""
    today = date.today()
    tomorrow_month = today.month
    tomorrow_day = today.day + 1 if today.day < 28 else 28  # 避免月份溢出
    birth_date = date(1990, tomorrow_month, tomorrow_day)
    days = days_until_birthday(birth_date, is_lunar=False)
    assert days == 1


def test_days_until_birthday_same_day():
    """测试生日当天"""
    today = date.today()
    birth_date = date(1990, today.month, today.day)
    days = days_until_birthday(birth_date, is_lunar=False)
    assert days == 0


def test_month_to_chinese():
    """测试月份转中文"""
    assert month_to_chinese(1) == "正月"
    assert month_to_chinese(10) == "十月"
    assert month_to_chinese(12) == "腊月"
    assert month_to_chinese(5) == "五月"


def test_day_to_chinese():
    """测试日期转中文"""
    assert day_to_chinese(1) == "初一"
    assert day_to_chinese(10) == "初十"
    assert day_to_chinese(15) == "十五"
    assert day_to_chinese(20) == "二十"


def test_get_lunar_date_string():
    """测试农历日期字符串"""
    solar = date(2024, 2, 10)
    result = get_lunar_date_string(solar)
    assert "2024" in result
    assert "正" in result
    assert "初一" in result


def test_get_upcoming_birthday_date_solar():
    """测试公历生日日期"""
    birth = date(1990, 5, 15)
    result = get_upcoming_birthday_date(birth, is_lunar=False, target_year=2026)
    assert result == date(2026, 5, 15)


def test_get_upcoming_birthday_date_lunar():
    """测试农历生日日期"""
    birth = date(1990, 5, 15)
    result = get_upcoming_birthday_date(birth, is_lunar=True, target_year=2026)
    assert result is not None
