"""
测试四柱生成模块
"""
import pytest
from datetime import datetime, timezone

from bazi.services.pillar import (
    YearPillarService, MonthPillarService, DayPillarService,
    HourPillarService, PillarGenerator
)
from bazi.models.time_location import BirthInput, TimeConvertResult, SolarTermInfo
from bazi.models.pillar import PillarConfig, PillarInput
from bazi.models.base import Location, CalendarPref
from bazi.services.time_location import TimeLocationConverter, SolarTermService


class TestYearPillarService:
    """测试年柱服务"""

    def setup_method(self):
        self.solar_term_service = SolarTermService()
        self.service = YearPillarService(self.solar_term_service)

    def test_get_year_pillar_by_li_chun(self):
        """测试以立春划分年柱"""
        # 创建一个在立春之后的时间结果
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        config = PillarConfig(year_pillar_rule="by_li_chun")
        pillar = self.service.get_year_pillar(time_result, config)

        assert pillar.stem is not None
        assert pillar.branch is not None
        assert pillar.year is not None

    def test_is_yang_year(self):
        """测试判断阳年"""
        assert self.service.is_yang_year("甲子") == True  # 甲为阳
        assert self.service.is_yang_year("乙丑") == False  # 乙为阴
        assert self.service.is_yang_year("庚午") == True  # 庚为阳


class TestMonthPillarService:
    """测试月柱服务"""

    def setup_method(self):
        self.solar_term_service = SolarTermService()
        self.service = MonthPillarService(self.solar_term_service)

    def test_get_month_pillar(self):
        """测试获取月柱"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        config = PillarConfig()
        pillar = self.service.get_month_pillar(time_result, "庚", config)

        assert pillar.stem is not None
        assert pillar.branch is not None
        assert pillar.month_index is not None

    def test_term_to_branch_mapping(self):
        """测试节气到月支的映射"""
        # 小寒 (index 0) 对应丑月
        assert self.service.TERM_TO_BRANCH[0] == 1
        # 立春 (index 2) 对应寅月
        assert self.service.TERM_TO_BRANCH[2] == 2


class TestDayPillarService:
    """测试日柱服务"""

    def setup_method(self):
        self.service = DayPillarService()

    def test_get_day_pillar(self):
        """测试获取日柱"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        config = PillarConfig()
        pillar = self.service.get_day_pillar(time_result, config)

        assert pillar.stem is not None
        assert pillar.branch is not None
        assert pillar.ganzhi is not None

    def test_base_date(self):
        """测试基准日期"""
        # 1900-01-31 是甲子日
        assert self.service.DEFAULT_BASE == datetime(1900, 1, 31, tzinfo=timezone.utc)


class TestHourPillarService:
    """测试时柱服务"""

    def setup_method(self):
        self.service = HourPillarService()

    def test_get_hour_pillar(self):
        """测试获取时柱"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        config = PillarConfig()
        pillar = self.service.get_hour_pillar(time_result, "丙", config)

        assert pillar.stem is not None
        assert pillar.branch is not None
        assert pillar.hour_index is not None

    def test_hour_to_branch(self):
        """测试小时到时辰的映射"""
        # 午时: 11:00-13:00
        assert self.service._get_branch_index(12) == 6
        # 子时: 23:00-01:00
        assert self.service._get_branch_index(23) == 0
        assert self.service._get_branch_index(0) == 0


class TestPillarGenerator:
    """测试四柱生成器"""

    def setup_method(self):
        self.generator = PillarGenerator()

    def test_generate(self):
        """测试生成四柱"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        pillar_input = PillarInput(time_result=time_result)
        pillars = self.generator.generate(pillar_input)

        assert pillars.year_pillar is not None
        assert pillars.month_pillar is not None
        assert pillars.day_pillar is not None
        assert pillars.hour_pillar is not None

        # 验证干支格式正确
        assert len(pillars.year_pillar.ganzhi) == 2
        assert len(pillars.month_pillar.ganzhi) == 2
        assert len(pillars.day_pillar.ganzhi) == 2
        assert len(pillars.hour_pillar.ganzhi) == 2

    def test_to_dict(self):
        """测试转换为字典"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        pillar_input = PillarInput(time_result=time_result)
        pillars = self.generator.generate(pillar_input)

        result_dict = pillars.to_dict()
        assert isinstance(result_dict, dict)
        assert "year_pillar" in result_dict
        assert "month_pillar" in result_dict
        assert "day_pillar" in result_dict
        assert "hour_pillar" in result_dict

    def test_get_pillar_by_ganzhi(self):
        """测试根据干支获取详细信息"""
        info = self.generator.get_pillar_by_ganzhi("甲子")
        assert info is not None
        assert "stem" in info
        assert "branch" in info
        assert info["stem"]["name"] == "甲"
        assert info["branch"]["name"] == "子"
