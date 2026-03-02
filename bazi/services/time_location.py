"""
时间地点转换模块 - 处理时区、真太阳时、历法转换、节气计算等
"""
import math
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from zoneinfo import ZoneInfo

from bazi.models.base import Location, CalendarPref
from bazi.models.time_location import (
    BirthInput, TimeConvertResult, SolarTermInfo, LunarCalendarInfo, GanZhiDate
)
from bazi.services.basic_data import StemRepository, BranchRepository


class TimezoneService:
    """时区处理服务"""

    # 常用时区的标准经度
    ZONE_LONGITUDE_MAP: Dict[str, float] = {
        "Asia/Shanghai": 120.0,
        "Asia/Chongqing": 105.0,
        "Asia/Urumqi": 90.0,
        "Asia/Harbin": 135.0,
        "Asia/Tokyo": 135.0,
        "Asia/Seoul": 135.0,
        "Asia/Singapore": 105.0,
        "Asia/Hong_Kong": 120.0,
        "Asia/Taipei": 120.0,
        "America/New_York": -75.0,
        "America/Los_Angeles": -120.0,
        "Europe/London": 0.0,
        "Europe/Paris": 0.0,
    }

    def to_utc(self, local_dt: datetime, timezone_str: str) -> datetime:
        """
        将本地时间转换为 UTC 时间
        
        Args:
            local_dt: 本地时间 (naive datetime)
            timezone_str: IANA 时区字符串
            
        Returns:
            UTC 时间 (timezone-aware datetime)
        """
        tz = ZoneInfo(timezone_str)
        local_aware = local_dt.replace(tzinfo=tz)
        return local_aware.astimezone(timezone.utc)

    def from_utc(self, utc_dt: datetime, timezone_str: str) -> datetime:
        """
        将 UTC 时间转换为本地时间
        
        Args:
            utc_dt: UTC 时间
            timezone_str: IANA 时区字符串
            
        Returns:
            本地时间 (timezone-aware datetime)
        """
        tz = ZoneInfo(timezone_str)
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(tz)

    def get_zone_longitude(self, timezone_str: str) -> float:
        """
        获取时区对应的标准经度
        
        Args:
            timezone_str: IANA 时区字符串
            
        Returns:
            标准经度
        """
        if timezone_str in self.ZONE_LONGITUDE_MAP:
            return self.ZONE_LONGITUDE_MAP[timezone_str]

        # 根据时区偏移推断
        tz = ZoneInfo(timezone_str)
        now = datetime.now(tz)
        offset_hours = now.utcoffset().total_seconds() / 3600
        return offset_hours * 15


class TrueSolarTimeService:
    """真太阳时计算服务"""

    # 方程时差表 (简化版，每日一个值，单位：分钟)
    # 真太阳时 = 平太阳时 + 方程时差
    EQUATION_OF_TIME: list = [
        -3, -6, -10, -13, -15, -16, -15, -14, -11, -8, -4, 0, 3, 5, 6, 5, 3, 0, -4, -8, -12, -15, -17, -17,
        -15, -12, -8, -4, 2, 7, 11, 13, 14, 13, 11, 8, 4, 0, -3, -6, -9, -11, -12, -11, -9, -6, -3, 0, 3,
        6, 9, 11, 12, 12, 11, 9, 6, 3, 0, -3, -6, -9, -11, -12, -11, -9, -6, -3, 0, 3, 6, 9, 11, 12, 12,
        11, 9, 6, 3, 0, -3, -6, -9, -11, -12, -11, -9, -6, -3, 0, 3, 6, 9, 11, 12, 12, 11, 9, 6, 3, 0,
    ]

    def __init__(self, timezone_service: TimezoneService):
        self.timezone_service = timezone_service

    def calc_true_solar_time(
        self,
        local_standard: datetime,
        longitude: float,
        timezone_str: str
    ) -> datetime:
        """
        计算真太阳时
        
        Args:
            local_standard: 本地标准时间
            longitude: 地点经度
            timezone_str: 时区
            
        Returns:
            真太阳时
        """
        # 1. 经度时差
        zone_longitude = self.timezone_service.get_zone_longitude(timezone_str)
        longitude_diff = (longitude - zone_longitude) * 4  # 每1度4分钟

        # 2. 方程时差
        day_of_year = local_standard.timetuple().tm_yday
        # 获取当天的方程时差 (使用线性插值)
        eot_index = min(day_of_year - 1, len(self.EQUATION_OF_TIME) - 1)
        eot_index = max(0, eot_index)
        equation_of_time = self.EQUATION_OF_TIME[eot_index]

        # 总时差 (分钟)
        total_diff_minutes = longitude_diff + equation_of_time

        # 计算真太阳时
        true_solar_time = local_standard + timedelta(minutes=total_diff_minutes)

        return true_solar_time

    def get_equation_of_time(self, date: datetime) -> float:
        """
        获取指定日期的方程时差 (分钟)
        
        Args:
            date: 日期
            
        Returns:
            方程时差 (分钟)
        """
        day_of_year = date.timetuple().tm_yday
        eot_index = min(day_of_year - 1, len(self.EQUATION_OF_TIME) - 1)
        return self.EQUATION_OF_TIME[eot_index]


class SolarTermService:
    """节气计算服务"""

    # 24节气名称
    SOLAR_TERMS: list = [
        "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
        "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
        "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
        "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
    ]

    # 节气对应的太阳黄经
    SOLAR_LONGITUDE: list = [
        285, 300, 315, 330, 345, 0,
        15, 30, 45, 60, 75, 90,
        105, 120, 135, 150, 165, 180,
        195, 210, 225, 240, 255, 270
    ]

    def __init__(self):
        # 简化的节气数据 (1900-2100年)
        # 实际应用中应使用更精确的天文计算或预置数据表
        self._term_cache: Dict[int, Dict[int, datetime]] = {}

    def calc_solar_term_date(self, year: int, term_index: int) -> datetime:
        """
        计算指定年份节气的 UTC 时间
        
        使用简化算法，实际应用中应使用更精确的天文公式
        
        Args:
            year: 年份
            term_index: 节气索引 (0-23)
            
        Returns:
            节气的 UTC 时间
        """
        # 使用近似公式计算节气时间
        # 这个公式基于回归年长度约为365.2422天
        # 节气间隔约为15.2184天

        # 冬至基准 (约在12月22日)
        winter_solstice_day = 355 + (year - 2000) * 0.2422
        winter_solstice_day = winter_solstice_day % 365

        # 计算目标节气距冬至的天数
        term_day_offset = (term_index - 23) * 15.2184 if term_index >= 0 else term_index * 15.2184
        if term_index < 23:
            term_day_offset = (term_index + 1) * 15.2184  # 从小寒开始算

        # 计算节气日期
        base_date = datetime(year, 1, 1, tzinfo=timezone.utc)
        days_from_base = int(winter_solstice_day + term_day_offset)

        # 处理跨年情况
        if days_from_base < 0:
            base_date = datetime(year - 1, 1, 1, tzinfo=timezone.utc)
            days_from_base += 365
        elif days_from_base > 365:
            days_from_base -= 365

        # 粗略估算节气时间 (实际应用需要更精确的计算)
        hour = 12 + int((term_index % 3) * 2)  # 简化的小时估算
        hour = hour % 24

        return base_date + timedelta(days=days_from_base, hours=hour)

    def get_nearest_terms(self, utc_dt: datetime) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        获取距离指定时间最近的两个节气
        
        Args:
            utc_dt: UTC 时间
            
        Returns:
            (当前节气信息, 下一节气信息)
        """
        year = utc_dt.year

        # 查找包含该时间的节气区间
        for i in range(24):
            term_time = self.calc_solar_term_date(year, i)
            next_term_time = self.calc_solar_term_date(year, (i + 1) % 24)

            # 处理跨年
            if i == 23:
                next_term_time = self.calc_solar_term_date(year + 1, 0)

            if term_time <= utc_dt < next_term_time:
                current = {
                    "name": self.SOLAR_TERMS[i],
                    "index": i,
                    "start_time_utc": term_time.isoformat().replace("+00:00", "Z")
                }
                next_idx = (i + 1) % 24
                next_term = {
                    "name": self.SOLAR_TERMS[next_idx],
                    "index": next_idx,
                    "start_time_utc": next_term_time.isoformat().replace("+00:00", "Z")
                }
                return current, next_term

        # 如果未找到（可能在年初），返回小寒和大寒
        current = {
            "name": "小寒",
            "index": 0,
            "start_time_utc": self.calc_solar_term_date(year, 0).isoformat().replace("+00:00", "Z")
        }
        next_term = {
            "name": "大寒",
            "index": 1,
            "start_time_utc": self.calc_solar_term_date(year, 1).isoformat().replace("+00:00", "Z")
        }
        return current, next_term

    def get_term_by_name(self, name: str) -> int:
        """根据名称获取节气索引"""
        return self.SOLAR_TERMS.index(name) if name in self.SOLAR_TERMS else -1

    def is_jie_term(self, term_index: int) -> bool:
        """
        判断是否为"节" (节气)
        节: 小寒、立春、惊蛰、清明、立夏、芒种、小暑、立秋、白露、寒露、立冬、大雪 (奇数索引)
        气: 大寒、雨水、春分、谷雨、小满、夏至、大暑、处暑、秋分、霜降、小雪、冬至 (偶数索引)
        """
        return term_index % 2 == 0


class LunarCalendarService:
    """农历转换服务"""

    # 1900-2100年农历数据
    # 每年数据包含: (闰月月份, 各月天数) 
    # 天数: 1为大月30天，0为小月29天
    # 这里使用简化的预置数据结构

    # 农历年份信息表 (简化版)
    # 格式: {年份: (闰月, [各月大小], 农历新年公历日期)}
    # 实际应用中应该使用更完整的数据

    # 天干地支
    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def __init__(self):
        self._lunar_data = self._init_lunar_data()

    def _init_lunar_data(self) -> Dict[int, Dict]:
        """初始化农历数据"""
        # 简化的农历数据，实际应用中应使用完整的数据表
        lunar_data = {}
        
        # 使用新农历算法基准: 1900年正月初一为1900-01-31
        for year in range(1900, 2101):
            # 计算农历新年 (简化公式)
            lunar_new_year = self._calc_lunar_new_year(year)
            lunar_data[year] = {
                "new_year_date": lunar_new_year,
                "leap_month": self._calc_leap_month(year),
                "month_days": self._calc_month_days(year)
            }
        
        return lunar_data

    def _calc_lunar_new_year(self, year: int) -> datetime:
        """计算农历新年 (简化算法)"""
        # 使用近似公式
        # 农历新年大约在公历1月21日到2月20日之间
        base = datetime(1900, 1, 31, tzinfo=timezone.utc)
        days = int((year - 1900) * 365.2422 + 0.5)
        return base + timedelta(days=days % 30)

    def _calc_leap_month(self, year: int) -> int:
        """计算闰月 (简化)"""
        # 闰月周期约为19年7闰
        # 简化处理
        cycle = year % 19
        leap_months = {0: 0, 3: 0, 6: 0, 9: 0, 11: 0, 14: 0, 17: 0}
        return leap_months.get(cycle, 0)

    def _calc_month_days(self, year: int) -> list:
        """计算各月天数 (简化)"""
        # 简化: 假设大小月交替
        return [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]

    def to_lunar(self, gregorian: datetime) -> Dict[str, Any]:
        """
        公历转农历
        
        Args:
            gregorian: 公历时间
            
        Returns:
            农历日期信息
        """
        year = gregorian.year
        if year < 1900 or year > 2100:
            raise ValueError(f"不支持的年份: {year}")

        lunar_info = self._lunar_data.get(year)
        if not lunar_info:
            raise ValueError(f"缺少农历数据: {year}")

        # 简化计算
        new_year = lunar_info["new_year_date"]
        days_from_new_year = (gregorian - new_year).days

        # 计算农历月日
        lunar_month = 1
        lunar_day = days_from_new_year + 1

        month_days = lunar_info["month_days"]
        for i, md in enumerate(month_days):
            days_in_month = 30 if md == 1 else 29
            if lunar_day <= days_in_month:
                lunar_month = i + 1
                break
            lunar_day -= days_in_month

        # 处理闰月
        is_leap = False
        leap_month = lunar_info["leap_month"]
        if leap_month > 0 and lunar_month > leap_month:
            lunar_month -= 1
            is_leap = (lunar_month == leap_month)

        return {
            "year": year,
            "month": max(1, lunar_month),
            "day": max(1, lunar_day),
            "is_leap_month": is_leap
        }

    def to_gregorian(self, lunar_year: int, lunar_month: int, lunar_day: int, is_leap: bool = False) -> datetime:
        """
        农历转公历
        
        Args:
            lunar_year: 农历年
            lunar_month: 农历月
            lunar_day: 农历日
            is_leap: 是否闰月
            
        Returns:
            公历日期
        """
        if lunar_year < 1900 or lunar_year > 2100:
            raise ValueError(f"不支持的年份: {lunar_year}")

        lunar_info = self._lunar_data.get(lunar_year)
        if not lunar_info:
            raise ValueError(f"缺少农历数据: {lunar_year}")

        # 从新年开始计算
        result = lunar_info["new_year_date"]
        
        # 加上各月天数
        month_days = lunar_info["month_days"]
        for i in range(lunar_month - 1):
            days = 30 if month_days[i] == 1 else 29
            result += timedelta(days=days)

        # 加上日数
        result += timedelta(days=lunar_day - 1)

        return result


class GanzhiDayService:
    """干支日期计算服务"""

    # 基准日期: 1900-01-31 为甲子日
    BASE_DATE = datetime(1900, 1, 31, tzinfo=timezone.utc)
    BASE_STEM = 0  # 甲
    BASE_BRANCH = 0  # 子

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def __init__(self, stem_repo: StemRepository, branch_repo: BranchRepository):
        self.stem_repo = stem_repo
        self.branch_repo = branch_repo

    def get_ganzhi_day(self, utc_dt: datetime) -> str:
        """
        获取干支日
        
        Args:
            utc_dt: UTC 时间
            
        Returns:
            干支日 (如 "甲子")
        """
        # 计算与基准日期的天数差
        days = (utc_dt.date() - self.BASE_DATE.date()).days

        # 计算60甲子索引
        ganzhi_index = days % 60
        if ganzhi_index < 0:
            ganzhi_index += 60

        # 计算天干地支索引
        stem_index = (self.BASE_STEM + ganzhi_index) % 10
        branch_index = (self.BASE_BRANCH + ganzhi_index) % 12

        return self.STEMS[stem_index] + self.BRANCHES[branch_index]

    def get_day_stem_branch(self, utc_dt: datetime) -> Tuple[str, str]:
        """
        获取日干支
        
        Returns:
            (日干, 日支)
        """
        ganzhi = self.get_ganzhi_day(utc_dt)
        return ganzhi[0], ganzhi[1]

    def get_ganzhi_year(self, year: int, is_before_li_chun: bool = False) -> str:
        """
        获取干支年
        
        Args:
            year: 公历年份
            is_before_li_chun: 是否在立春之前
            
        Returns:
            干支年 (如 "甲子")
        """
        # 以1984年(甲子年)为基准
        base_year = 1984
        delta = year - base_year

        if is_before_li_chun:
            delta -= 1

        # 60甲子循环
        ganzhi_index = delta % 60
        if ganzhi_index < 0:
            ganzhi_index += 60

        stem_index = ganzhi_index % 10
        branch_index = ganzhi_index % 12

        return self.STEMS[stem_index] + self.BRANCHES[branch_index]


class TimeLocationConverter:
    """时间地点转换器"""

    def __init__(self):
        self.timezone_service = TimezoneService()
        self.true_solar_time_service = TrueSolarTimeService(self.timezone_service)
        self.solar_term_service = SolarTermService()
        self.lunar_service = LunarCalendarService()
        self.stem_repo = StemRepository()
        self.branch_repo = BranchRepository()
        self.ganzhi_service = GanzhiDayService(self.stem_repo, self.branch_repo)

    def convert(self, input_data: BirthInput) -> TimeConvertResult:
        """
        执行时间地点转换
        
        Args:
            input_data: 输入数据
            
        Returns:
            转换结果
        """
        # 解析时间
        local_dt = datetime.fromisoformat(input_data.gregorian_datetime)

        # 转换为 UTC
        utc_dt = self.timezone_service.to_utc(local_dt, input_data.timezone)

        # 本地标准时间 (带时区)
        local_standard = self.timezone_service.from_utc(utc_dt, input_data.timezone)

        # 计算真太阳时 (如果启用)
        local_true_solar = None
        if input_data.calendar_pref.use_true_solar_time:
            longitude = input_data.location.longitude
            if longitude:
                local_true_solar = self.true_solar_time_service.calc_true_solar_time(
                    local_dt, longitude, input_data.timezone
                )

        # 获取节气信息
        current_term, next_term = self.solar_term_service.get_nearest_terms(utc_dt)

        # 计算与节气的时间差
        term_start = datetime.fromisoformat(current_term["start_time_utc"].replace("Z", "+00:00"))
        minutes_from_start = int((utc_dt - term_start).total_seconds() / 60)

        next_term_time = datetime.fromisoformat(next_term["start_time_utc"].replace("Z", "+00:00"))
        minutes_to_next = int((next_term_time - utc_dt).total_seconds() / 60)

        solar_term_info = SolarTermInfo(
            name=current_term["name"],
            index=current_term["index"],
            start_time_utc=current_term["start_time_utc"],
            next_term_name=next_term["name"],
            next_term_time_utc=next_term["start_time_utc"],
            minutes_from_term_start=minutes_from_start,
            minutes_to_next_term=minutes_to_next
        )

        # 农历转换
        lunar_info = self.lunar_service.to_lunar(utc_dt)
        lunar_calendar = LunarCalendarInfo(
            year=lunar_info["year"],
            month=lunar_info["month"],
            day=lunar_info["day"],
            is_leap_month=lunar_info["is_leap_month"]
        )

        # 干支日期
        # 判断是否在立春之前
        is_before_li_chun = self._is_before_li_chun(utc_dt, current_term)
        year_ganzhi = self.ganzhi_service.get_ganzhi_year(
            local_dt.year, is_before_li_chun
        )
        day_ganzhi = self.ganzhi_service.get_ganzhi_day(utc_dt)

        # 月干支 (简化计算)
        month_ganzhi = self._calc_month_ganzhi(year_ganzhi, current_term["index"])

        ganzhi_date = GanZhiDate(
            year=year_ganzhi,
            month=month_ganzhi,
            day=day_ganzhi
        )

        return TimeConvertResult(
            input=input_data,
            utc_datetime=utc_dt.isoformat().replace("+00:00", "Z"),
            local_datetime_standard=local_standard.isoformat(),
            local_datetime_true_solar=local_true_solar.isoformat() if local_true_solar else None,
            solar_term=solar_term_info,
            lunar_calendar=lunar_calendar,
            ganzhi_date=ganzhi_date
        )

    def _is_before_li_chun(self, utc_dt: datetime, current_term: dict) -> bool:
        """判断是否在立春之前"""
        if current_term["index"] < 2:  # 小寒(0)或大寒(1)
            return True
        if current_term["index"] == 2:  # 立春
            term_start = datetime.fromisoformat(
                current_term["start_time_utc"].replace("Z", "+00:00")
            )
            return utc_dt < term_start
        return False

    def _calc_month_ganzhi(self, year_ganzhi: str, term_index: int) -> str:
        """计算月干支"""
        # 月支: 根据节气确定
        # 小寒(0): 丑月, 立春(2): 寅月, ..., 冬至(23): 子月
        month_branch_index = (term_index + 1) % 12
        if term_index == 23:
            month_branch_index = 0  # 子月

        # 月干: 根据年干推算
        # 甲己年: 丙寅起
        # 乙庚年: 戊寅起
        # 丙辛年: 庚寅起
        # 丁壬年: 壬寅起
        # 戊癸年: 甲寅起
        year_stem = year_ganzhi[0]
        year_stem_index = self.stem_repo.get_index(year_stem)

        # 甲(0)己(5) -> 丙(2)
        # 乙(1)庚(6) -> 戊(4)
        # 丙(2)辛(7) -> 庚(6)
        # 丁(3)壬(8) -> 壬(8)
        # 戊(4)癸(9) -> 甲(0)
        month_stem_base = (year_stem_index % 5) * 2 + 2
        month_stem_base = month_stem_base % 10

        # 从寅月开始
        month_stem_index = (month_stem_base + month_branch_index - 2) % 10
        if month_branch_index < 2:  # 丑月或子月
            month_stem_index = (month_stem_base + month_branch_index + 10) % 10

        return self.ganzhi_service.STEMS[month_stem_index] + self.ganzhi_service.BRANCHES[month_branch_index]
