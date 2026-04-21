"""
农历服务模块

使用 lunar_python 库提供：
- 阳历/农历转换
- 干支（年/月/日/时）计算
- 生肖计算
- 节气信息
- 星座信息
- 农历/阳历节日
"""
from datetime import date, datetime, timedelta
from typing import Tuple, Optional, Dict
from lunar_python import Solar, Lunar


def solar_to_lunar(solar_date: date) -> Tuple[int, int, int]:
    """公历转农历

    Returns:
        Tuple[year, month, day] 农历年月日
    """
    solar = Solar.fromYmd(solar_date.year, solar_date.month, solar_date.day)
    lunar = solar.getLunar()
    return lunar.getYear(), lunar.getMonth(), lunar.getDay()


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
        lunar = Lunar.fromYmd(lunar_year, lunar_month, lunar_day)
        solar = lunar.getSolar()
        return date(solar.getYear(), solar.getMonth(), solar.getDay())
    except ValueError:
        pass

    for year_offset in [-1, 1]:
        try:
            lunar = Lunar.fromYmd(reference_year + year_offset, lunar_month, lunar_day)
            solar = lunar.getSolar()
            return date(solar.getYear(), solar.getMonth(), solar.getDay())
        except ValueError:
            continue

    return None


def get_lunar_date_string(solar_date: date) -> str:
    """获取农历日期字符串"""
    solar = Solar.fromYmd(solar_date.year, solar_date.month, solar_date.day)
    lunar = solar.getLunar()
    month_str = lunar.getMonthInChinese() + "月" if lunar.getMonth() > 0 else f"闰{lunar.getMonthInChinese()}月"
    return f"{lunar.getYear()}年{month_str}{lunar.getDayInChinese()}"


def month_to_chinese(month: int) -> str:
    """月份转中文（支持负数表示闰月）"""
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
        solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
        lunar = solar.getLunar()
        try:
            lunar_birthday = Lunar.fromYmd(target_year, lunar.getMonth(), lunar.getDay())
            solar_birthday = lunar_birthday.getSolar()
            return date(solar_birthday.getYear(), solar_birthday.getMonth(), solar_birthday.getDay())
        except ValueError:
            # 闰月情况
            if lunar.getMonth() < 0:
                try:
                    lunar_birthday = Lunar.fromYmd(target_year, lunar.getMonth(), lunar.getDay())
                    solar_birthday = lunar_birthday.getSolar()
                    return date(solar_birthday.getYear(), solar_birthday.getMonth(), solar_birthday.getDay())
                except ValueError:
                    return None
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


def get_date_info(solar_date: date) -> Dict:
    """获取日期的完整信息（干支、生肖、节日、节气等）

    Args:
        solar_date: 公历日期

    Returns:
        Dict: 包含丰富日期信息的字典
    """
    solar = Solar.fromYmd(solar_date.year, solar_date.month, solar_date.day)
    lunar = solar.getLunar()

    info = {
        'solar_date': solar_date,
        'gz_year': lunar.getYearInGanZhi(),       # 干支纪年
        'gz_month': lunar.getMonthInGanZhi(),     # 干支纪月
        'gz_day': lunar.getDayInGanZhi(),         # 干支纪日
        'gz_hour': lunar.getTimeInGanZhi(),       # 干支纪时
        'lunar_month': lunar.getMonthInChinese() + "月",  # 农历月份中文
        'lunar_day': lunar.getDayInChinese(),      # 农历日期中文
        'zodiac': lunar.getYearShengXiao(),        # 生肖
        'constellation': solar.getXingZuo(),       # 星座
        'week_name': solar.getWeekInChinese(),    # 星期
        'lunar_festival': '',                      # 农历节日
        'solar_festival': '',                      # 阳历节日
        'solar_term': '',                          # 节气
    }

    # 获取节日信息
    lunar_festivals = lunar.getFestivals()
    if lunar_festivals:
        info['lunar_festival'] = '、'.join(lunar_festivals)

    solar_festivals = solar.getFestivals()
    if solar_festivals:
        info['solar_festival'] = '、'.join(solar_festivals)

    # 获取节气
    term = lunar.getJieQi()
    if term:
        info['solar_term'] = term

    return info


def get_birthday_info(birth_date: date, is_lunar: bool, check_date: date = None) -> Dict:
    """获取生日日期的详细信息（用于生日提醒）

    Args:
        birth_date: 生日日期
        is_lunar: 是否为农历生日
        check_date: 要检查的日期（默认为今天）

    Returns:
        Dict: 包含生日信息的字典
    """
    if check_date is None:
        check_date = date.today()

    info = get_date_info(check_date)

    # 计算年龄
    info['age'] = calculate_age(birth_date, check_date)

    # 计算距离生日天数
    info['days_until'] = days_until_birthday(birth_date, is_lunar)

    # 标记是阳历还是农历生日
    info['solar_match'] = False
    info['lunar_match'] = False

    if is_lunar:
        solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
        birth_lunar = solar.getLunar()
        check_lunar = Lunar.fromYmd(
            check_date.year,
            check_date.month,
            check_date.day
        )
        if (birth_lunar.getMonth() == check_lunar.getMonth()
                and birth_lunar.getDay() == check_lunar.getDay()):
            info['lunar_match'] = True
            info['zodiac'] = birth_lunar.getYearShengXiao()
    else:
        if (birth_date.month == check_date.month
                and birth_date.day == check_date.day):
            info['solar_match'] = True

    return info


def get_zodiac(birth_date: date) -> str:
    """获取生肖"""
    solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
    lunar = solar.getLunar()
    return lunar.getYearShengXiao()


def get_constellation(birth_date: date) -> str:
    """获取星座"""
    solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
    return solar.getXingZuo()


class LunarService:
    """农历服务类 - 提供闰月处理等高级功能"""

    # 闰月策略选项
    LEAP_POLICY_OPTIONS = ["auto", "before", "after"]

    @classmethod
    def get_leap_month_options(cls) -> list:
        """获取闰月策略选项"""
        return cls.LEAP_POLICY_OPTIONS

    @classmethod
    def validate_lunar_birthday(cls, birth_date_str: str, policy: str = "auto") -> tuple:
        """验证农历生日格式和闰月策略

        Args:
            birth_date_str: YYYY-MM-DD 格式
            policy: 闰月策略 auto/before/after

        Returns:
            (is_valid, error_message)
        """
        if policy not in cls.LEAP_POLICY_OPTIONS:
            return False, f"无效的闰月策略: {policy}"

        try:
            year, month, day = map(int, birth_date_str.split('-'))
        except (ValueError, AttributeError):
            return False, "日期格式错误，需要 YYYY-MM-DD"

        # 验证月份范围
        if month < 1 or month > 12:
            return False, "农历月份必须在 1-12 之间"

        # 验证日期范围
        if day < 1 or day > 30:
            return False, "农历日期必须在 1-30 之间"

        return True, ""

    @classmethod
    def lunar_to_solar(cls, lunar_date_str: str, policy: str = "auto") -> tuple:
        """农历转公历（支持闰月策略）

        Args:
            lunar_date_str: YYYY-MM-DD 格式
            policy: 闰月策略 auto/before/after

        Returns:
            (solar_date_str, is_leap_month)
        """
        try:
            year, month, day = map(int, lunar_date_str.split('-'))
        except (ValueError, AttributeError):
            return None, False

        try:
            lunar = Lunar.fromYmd(year, month, day)
            solar = lunar.getSolar()
            solar_date = date(solar.getYear(), solar.getMonth(), solar.getDay())
            return solar_date.strftime("%Y-%m-%d"), False  # 简化版，不检测闰月
        except ValueError:
            return None, False

    @classmethod
    def get_lunar(cls, birth_date_str: str) -> Optional[Dict]:
        """获取农历详细信息

        Args:
            birth_date_str: YYYY-MM-DD 格式

        Returns:
            农历信息字典
        """
        try:
            year, month, day = map(int, birth_date_str.split('-'))
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()

            return {
                'lunar_year': lunar.getYear(),
                'lunar_month': lunar.getMonth(),
                'lunar_day': lunar.getDay(),
                'is_leap': False,  # 简化版，不检测闰月
                'month_chinese': lunar.getMonthInChinese(),
                'day_chinese': lunar.getDayInChinese(),
                'gan_zhi': lunar.getYearInGanZhi(),
                'sheng_xiao': lunar.getYearShengXiao(),
            }
        except (ValueError, AttributeError, TypeError):
            return None

    @classmethod
    def get_leap_month_info(cls, year: int) -> Optional[Dict]:
        """获取某年的闰月信息

        Args:
            year: 年份

        Returns:
            {'month': 月份, 'days': 天数} 或 None
        """
        try:
            lunar = Lunar.fromYm(year, 1)
            if lunar.getLeapMonth() > 0:
                leap_month = lunar.getLeapMonth()
                lunar_leap = Lunar.fromYmd(year, leap_month, 1, True)
                return {
                    'month': leap_month,
                    'days': lunar_leap.getDaysInMonth() if hasattr(lunar_leap, 'getDaysInMonth') else 29
                }
            return None
        except ValueError:
            return None
