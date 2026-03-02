"""
时间地点转换模块的数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from bazi.models.base import LunarDate, GanZhi, SolarTerm, Location, CalendarPref


@dataclass
class BirthInput:
    """出生时间输入"""
    gregorian_datetime: str  # ISO 8601 格式
    timezone: str            # IANA 时区
    location: Location
    calendar_pref: CalendarPref = field(default_factory=CalendarPref)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gregorian_datetime": self.gregorian_datetime,
            "timezone": self.timezone,
            "location": {
                "city_code": self.location.city_code,
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "altitude": self.location.altitude
            },
            "calendar_pref": {
                "use_true_solar_time": self.calendar_pref.use_true_solar_time,
                "ephemeris_source": self.calendar_pref.ephemeris_source
            }
        }


@dataclass
class SolarTermInfo:
    """节气信息"""
    name: str
    index: int
    start_time_utc: Optional[str] = None
    next_term_name: Optional[str] = None
    next_term_time_utc: Optional[str] = None
    minutes_from_term_start: Optional[int] = None
    minutes_to_next_term: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "index": self.index,
            "start_time_utc": self.start_time_utc,
            "next_term_name": self.next_term_name,
            "next_term_time_utc": self.next_term_time_utc,
            "minutes_from_term_start": self.minutes_from_term_start,
            "minutes_to_next_term": self.minutes_to_next_term
        }


@dataclass
class LunarCalendarInfo:
    """农历信息"""
    year: int
    month: int
    day: int
    is_leap_month: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "is_leap_month": self.is_leap_month
        }


@dataclass
class GanZhiDate:
    """干支日期"""
    year: str   # 年柱干支
    month: str  # 月柱干支
    day: str    # 日柱干支

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day
        }


@dataclass
class TimeConvertResult:
    """时间转换结果"""
    input: BirthInput
    utc_datetime: str
    local_datetime_standard: str
    local_datetime_true_solar: Optional[str] = None
    solar_term: Optional[SolarTermInfo] = None
    lunar_calendar: Optional[LunarCalendarInfo] = None
    ganzhi_date: Optional[GanZhiDate] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "input": self.input.to_dict(),
            "utc_datetime": self.utc_datetime,
            "local_datetime_standard": self.local_datetime_standard
        }
        if self.local_datetime_true_solar:
            result["local_datetime_true_solar"] = self.local_datetime_true_solar
        if self.solar_term:
            result["solar_term"] = self.solar_term.to_dict()
        if self.lunar_calendar:
            result["lunar_calendar"] = self.lunar_calendar.to_dict()
        if self.ganzhi_date:
            result["ganzhi_date"] = self.ganzhi_date.to_dict()
        return result
