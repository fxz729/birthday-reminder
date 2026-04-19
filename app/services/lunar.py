from datetime import date, datetime
from typing import Tuple, Optional
from lunardate import LunarDate


def solar_to_lunar(solar_date: date) -> Tuple[int, int, int]:
    """公历转农历

    Returns:
        Tuple[year, month, day] 农历年月日
    """
    lunar = LunarDate.fromSolarDate(solar_date.year, solar_date.month, solar_date.day)
    return lunar.year, lunar.month, lunar.day


def lunar_to_solar(lunar_year: int, lunar_month: int, lunar_day: int, reference_year: int = None) -> Optional[date]:
    """农历转公历

    Args:
        lunar_year: 农历年
        lunar_month: 农历月
        lunar_day: 农历日
        reference_year: 参考年份（用于闰月等情况）

    Returns:
        公历日期
    """
    if reference_year is None:
        reference_year = datetime.now().year

    try:
        lunar = LunarDate(reference_year, lunar_month, lunar_day)
        return lunar.toSolarDate()
    except ValueError:
        pass

    for year_offset in [-1, 1]:
        try:
            lunar = LunarDate(reference_year + year_offset, lunar_month, lunar_day)
            return lunar.toSolarDate()
        except ValueError:
            continue

    return None


def get_lunar_date_string(solar_date: date) -> str:
    """获取农历日期字符串"""
    lunar = LunarDate.fromSolarDate(solar_date.year, solar_date.month, solar_date.day)
    return f"{lunar.year}年{month_to_chinese(lunar.month)}{day_to_chinese(lunar.day)}"


def month_to_chinese(month: int) -> str:
    """月份转中文"""
    chinese_months = ["", "正月", "二月", "三月", "四月", "五月", "六月",
                      "七月", "八月", "九月", "十月", "冬月", "腊月"]
    if month < 0:  # 闰月
        return f"闰{chinese_months[-month]}"
    return chinese_months[month]


def day_to_chinese(day: int) -> str:
    """日期转中文"""
    chinese_days = [
        "", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
        "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
        "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
    ]
    if 1 <= day <= 30:
        return chinese_days[day]
    return ""


def calculate_age(birth_date: date, current_date: date = None) -> int:
    """计算年龄"""
    if current_date is None:
        current_date = date.today()
    age = current_date.year - birth_date.year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def get_upcoming_birthday_date(birth_date: date, is_lunar: bool, target_year: int = None) -> Optional[date]:
    """获取今年/明年生日日期"""
    if target_year is None:
        target_year = date.today().year

    if is_lunar:
        lunar = LunarDate.fromSolarDate(birth_date.year, birth_date.month, birth_date.day)
        try:
            this_year_lunar = LunarDate(target_year, lunar.month, lunar.day)
            return this_year_lunar.toSolarDate()
        except ValueError:
            try:
                this_year_lunar = LunarDate(target_year, -lunar.month, lunar.day)
                return this_year_lunar.toSolarDate()
            except ValueError:
                return None
    else:
        return date(target_year, birth_date.month, birth_date.day)


def days_until_birthday(birth_date: date, is_lunar: bool) -> int:
    """计算距离下次生日的天数"""
    today = date.today()
    this_year_birthday = get_upcoming_birthday_date(birth_date, is_lunar, today.year)

    if this_year_birthday is None:
        return -1

    if this_year_birthday < today:
        next_year_birthday = get_upcoming_birthday_date(birth_date, is_lunar, today.year + 1)
        if next_year_birthday:
            return (next_year_birthday - today).days

    return (this_year_birthday - today).days
