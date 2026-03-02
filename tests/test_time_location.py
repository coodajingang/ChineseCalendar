"""
测试时间地点转换模块
"""
import pytest
from datetime import datetime, timezone, timedelta

from bazi.services.time_location import (
    TimezoneService, TrueSolarTimeService, SolarTermService,
    LunarCalendarService, GanzhiDayService, TimeLocationConverter
)
from bazi.models.time_location import BirthInput
from bazi.models.base import Location, CalendarPref
from bazi.services.basic_data import StemRepository, BranchRepository


class TestTimezoneService:
    """测试时区服务"""

    def setup_method(self):
        self.service = TimezoneService()

    def test_to_utc(self):
        """测试本地时间转 UTC"""
        local_dt = datetime(1990, 5, 21, 14, 35, 0)
        utc_dt = self.service.to_utc(local_dt, "Asia/Shanghai")
        # UTC+8 的 14:35 对应 UTC 约 06:35
        # 由于历史时区规则，可能有一小时差异
        assert utc_dt.hour in [5, 6]

    def test_from_utc(self):
        """测试 UTC 转本地时间"""
        utc_dt = datetime(1990, 5, 21, 6, 35, 0, tzinfo=timezone.utc)
        local_dt = self.service.from_utc(utc_dt, "Asia/Shanghai")
        # UTC+8 的 06:35 对应本地约 14:35
        # 由于历史时区规则，可能有一小时差异
        assert local_dt.hour in [14, 15]

    def test_get_zone_longitude(self):
        """测试获取时区标准经度"""
        lon = self.service.get_zone_longitude("Asia/Shanghai")
        assert lon == 120.0

        lon = self.service.get_zone_longitude("Asia/Tokyo")
        assert lon == 135.0


class TestTrueSolarTimeService:
    """测试真太阳时服务"""

    def setup_method(self):
        self.timezone_service = TimezoneService()
        self.service = TrueSolarTimeService(self.timezone_service)

    def test_calc_true_solar_time(self):
        """测试真太阳时计算"""
        local_standard = datetime(1990, 5, 21, 14, 35, 0)
        longitude = 121.4737  # 上海经度
        true_solar = self.service.calc_true_solar_time(
            local_standard, longitude, "Asia/Shanghai"
        )
        # 真太阳时应该与标准时间有差异
        assert isinstance(true_solar, datetime)

    def test_get_equation_of_time(self):
        """测试获取方程时差"""
        # 测试不同日期的方程时差
        spring_equinox = datetime(1990, 3, 21)
        eot = self.service.get_equation_of_time(spring_equinox)
        assert isinstance(eot, (int, float))


class TestSolarTermService:
    """测试节气服务"""

    def setup_method(self):
        self.service = SolarTermService()

    def test_solar_terms_count(self):
        """测试节气数量"""
        assert len(self.service.SOLAR_TERMS) == 24

    def test_calc_solar_term_date(self):
        """测试节气日期计算"""
        # 测试立春 (index=2)
        li_chun = self.service.calc_solar_term_date(1990, 2)
        assert isinstance(li_chun, datetime)
        # 立春通常在2月4日左右
        assert li_chun.month == 2

    def test_get_nearest_terms(self):
        """测试获取最近节气"""
        utc_dt = datetime(1990, 5, 21, 6, 35, 0, tzinfo=timezone.utc)
        current, next_term = self.service.get_nearest_terms(utc_dt)
        
        assert "name" in current
        assert "index" in current
        assert current["index"] >= 0 and current["index"] < 24

    def test_is_jie_term(self):
        """测试判断节/气"""
        # 小寒是节
        assert self.service.is_jie_term(0) == True
        # 大寒是气
        assert self.service.is_jie_term(1) == False
        # 立春是节
        assert self.service.is_jie_term(2) == True


class TestGanzhiDayService:
    """测试干支日期服务"""

    def setup_method(self):
        self.stem_repo = StemRepository()
        self.branch_repo = BranchRepository()
        self.service = GanzhiDayService(self.stem_repo, self.branch_repo)

    def test_get_ganzhi_day(self):
        """测试获取干支日"""
        # 1900-01-31 是甲子日
        utc_dt = datetime(1900, 1, 31, tzinfo=timezone.utc)
        ganzhi = self.service.get_ganzhi_day(utc_dt)
        assert ganzhi == "甲子"

    def test_get_day_stem_branch(self):
        """测试获取日干支"""
        utc_dt = datetime(1900, 1, 31, tzinfo=timezone.utc)
        stem, branch = self.service.get_day_stem_branch(utc_dt)
        assert stem == "甲"
        assert branch == "子"

    def test_get_ganzhi_year(self):
        """测试获取干支年"""
        # 1984 年是甲子年
        ganzhi = self.service.get_ganzhi_year(1984)
        assert ganzhi == "甲子"

        # 1985 年是乙丑年
        ganzhi = self.service.get_ganzhi_year(1985)
        assert ganzhi == "乙丑"

    def test_ganzhi_cycle(self):
        """测试60甲子循环"""
        # 测试连续日期的干支变化
        base_dt = datetime(1900, 1, 31, tzinfo=timezone.utc)
        
        for i in range(60):
            dt = base_dt + timedelta(days=i)
            ganzhi = self.service.get_ganzhi_day(dt)
            stem = ganzhi[0]
            branch = ganzhi[1]
            
            # 验证天干地支正确循环
            expected_stem_idx = i % 10
            expected_branch_idx = i % 12
            
            assert self.stem_repo.get_index(stem) == expected_stem_idx
            assert self.branch_repo.get_index(branch) == expected_branch_idx


class TestTimeLocationConverter:
    """测试时间地点转换器"""

    def setup_method(self):
        self.converter = TimeLocationConverter()

    def test_convert_basic(self):
        """测试基本转换"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref(use_true_solar_time=True)
        )

        result = self.converter.convert(input_data)

        assert result.utc_datetime is not None
        assert result.local_datetime_standard is not None
        assert result.solar_term is not None
        assert result.ganzhi_date is not None

    def test_convert_with_true_solar_time(self):
        """测试带真太阳时的转换"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref(use_true_solar_time=True)
        )

        result = self.converter.convert(input_data)
        assert result.local_datetime_true_solar is not None

    def test_convert_without_true_solar_time(self):
        """测试不带真太阳时的转换"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref(use_true_solar_time=False)
        )

        result = self.converter.convert(input_data)
        assert result.local_datetime_true_solar is None

    def test_to_dict(self):
        """测试转换为字典"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )

        result = self.converter.convert(input_data)
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "utc_datetime" in result_dict
        assert "local_datetime_standard" in result_dict
        assert "solar_term" in result_dict
        assert "ganzhi_date" in result_dict
