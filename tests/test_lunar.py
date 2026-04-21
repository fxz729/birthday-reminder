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
    get_upcoming_birthday_date,
    get_date_info,
    get_birthday_info,
    get_zodiac,
    get_constellation
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


def test_get_date_info():
    """测试获取丰富日期信息"""
    # 2024-04-21 是清明节后，测试节气信息
    info = get_date_info(date(2024, 4, 21))
    assert "gz_year" in info
    assert "gz_month" in info
    assert "gz_day" in info
    assert "gz_hour" in info
    assert "lunar_month" in info
    assert "lunar_day" in info
    assert "zodiac" in info
    assert "constellation" in info
    assert "week_name" in info
    assert isinstance(info["gz_year"], str)
    assert len(info["gz_year"]) >= 2  # 干支至少2个字符


def test_get_birthday_info():
    """测试获取生日信息"""
    # 阳历生日
    birth_date = date(1990, 7, 15)
    info = get_birthday_info(birth_date, is_lunar=False)
    assert "solar_match" in info
    assert "lunar_match" in info
    assert "days_until" in info
    assert "age" in info
    assert "zodiac" in info
    assert info["solar_match"] == False  # 今天不是 7月15日
    assert info["lunar_match"] == False


def test_get_birthday_info_today():
    """测试今天生日的情况"""
    today = date.today()
    birth_date = date(1990, today.month, today.day)
    info = get_birthday_info(birth_date, is_lunar=False, check_date=today)
    assert info["solar_match"] == True
    assert info["days_until"] == 0


def test_get_zodiac():
    """测试获取生肖"""
    # 测试任意日期能获取到生肖
    zodiac = get_zodiac(date(2024, 1, 1))
    assert zodiac is not None
    assert isinstance(zodiac, str)
    assert len(zodiac) >= 1


def test_get_constellation():
    """测试获取星座"""
    # 7月15日应该是巨蟹座
    constellation = get_constellation(date(2024, 7, 15))
    assert constellation is not None
    assert isinstance(constellation, str)
    # 7月15日应该是巨蟹座
    assert "巨蟹" in constellation or "狮子" in constellation


def test_date_info_contains_festivals():
    """测试节日信息"""
    # 2024-02-10 是春节
    info = get_date_info(date(2024, 2, 10))
    # 春节应该有农历节日信息
    if info["lunar_festival"]:
        assert "春" in info["lunar_festival"] or "节" in info["lunar_festival"]
