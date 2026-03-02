"""
测试运势推演模块
"""
import pytest

from bazi.services.fortune import (
    DaYunService, LiuNianService, LiuYueService, LiuRiService, FortuneEngine
)
from bazi.models.fortune import (
    DaYunConfig, FortuneScope, PersonInfo, FortuneInput
)
from bazi.models.pillar import PillarResult, YearPillar, MonthPillar, DayPillar, HourPillar
from bazi.models.time_location import TimeConvertResult, SolarTermInfo
from bazi.services.time_location import TimeLocationConverter, SolarTermService
from bazi.models.time_location import BirthInput
from bazi.models.base import Location, CalendarPref


class TestDaYunService:
    """测试大运服务"""

    def setup_method(self):
        self.solar_term_service = SolarTermService()
        self.service = DaYunService(self.solar_term_service)

    def test_calc_start_age(self):
        """测试计算起运年龄"""
        # 创建测试数据
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        pillars = PillarResult(
            year_pillar=YearPillar(stem="庚", branch="午", year=1990),
            month_pillar=MonthPillar(stem="辛", branch="巳", month_index=4),
            day_pillar=DayPillar(stem="丙", branch="辰", day_index_from_base=1),
            hour_pillar=HourPillar(stem="甲", branch="未", hour_index=7)
        )

        config = DaYunConfig()
        person_info = PersonInfo(gender="male")

        start_age = self.service.calc_start_age(time_result, pillars, config, person_info)
        assert isinstance(start_age, (int, float))
        assert start_age >= 0

    def test_generate_da_yun(self):
        """测试生成大运"""
        pillars = PillarResult(
            year_pillar=YearPillar(stem="庚", branch="午", year=1990),
            month_pillar=MonthPillar(stem="辛", branch="巳", month_index=4),
            day_pillar=DayPillar(stem="丙", branch="辰", day_index_from_base=1),
            hour_pillar=HourPillar(stem="甲", branch="未", hour_index=7)
        )

        config = DaYunConfig(da_yun_year_step=10)
        person_info = PersonInfo(gender="male")

        da_yun_list = self.service.generate_da_yun(pillars, config, 5.0, person_info, 1990)

        assert len(da_yun_list) > 0
        assert da_yun_list[0].index == 1
        assert da_yun_list[0].ganzhi is not None
        assert da_yun_list[0].start_age >= 0

    def test_direction_rules(self):
        """测试大运方向规则"""
        # 阳年男顺行
        pillars_yang_male = PillarResult(
            year_pillar=YearPillar(stem="甲", branch="子", year=1984),
            month_pillar=MonthPillar(stem="丙", branch="寅", month_index=1),
            day_pillar=DayPillar(stem="甲", branch="子", day_index_from_base=1),
            hour_pillar=HourPillar(stem="甲", branch="子", hour_index=0)
        )
        direction = self.service._get_direction(pillars_yang_male, PersonInfo(gender="male"))
        assert direction == 1  # 顺行

        # 阴年男逆行
        pillars_yin_male = PillarResult(
            year_pillar=YearPillar(stem="乙", branch="丑", year=1985),
            month_pillar=MonthPillar(stem="戊", branch="寅", month_index=1),
            day_pillar=DayPillar(stem="甲", branch="子", day_index_from_base=1),
            hour_pillar=HourPillar(stem="甲", branch="子", hour_index=0)
        )
        direction = self.service._get_direction(pillars_yin_male, PersonInfo(gender="male"))
        assert direction == -1  # 逆行


class TestLiuNianService:
    """测试流年服务"""

    def setup_method(self):
        self.service = LiuNianService()

    def test_generate_liu_nian(self):
        """测试生成流年"""
        da_yun_list = []  # 简化测试
        scope = FortuneScope(start_age=0, end_age=10)

        liu_nian_list = self.service.generate_liu_nian(
            "庚午", 1990, da_yun_list, scope
        )

        assert len(liu_nian_list) == 11  # 0-10岁
        assert liu_nian_list[0].year == 1990
        assert liu_nian_list[0].age == 0

    def test_calc_year_ganzhi(self):
        """测试计算年干支"""
        # 1984年是甲子年
        ganzhi = self.service._calc_year_ganzhi(1984)
        assert ganzhi == "甲子"

        # 1990年是庚午年
        ganzhi = self.service._calc_year_ganzhi(1990)
        assert ganzhi == "庚午"


class TestLiuYueService:
    """测试流月服务"""

    def setup_method(self):
        self.service = LiuYueService()

    def test_generate_liu_yue(self):
        """测试生成流月"""
        liu_yue_list = self.service.generate_liu_yue(1990, "庚")

        assert len(liu_yue_list) == 12
        assert liu_yue_list[0]["month"] == 1
        assert liu_yue_list[0]["ganzhi"] is not None


class TestLiuRiService:
    """测试流日服务"""

    def setup_method(self):
        self.service = LiuRiService()

    def test_generate_liu_ri(self):
        """测试生成流日"""
        liu_ri_list = self.service.generate_liu_ri(1990, 5)

        assert len(liu_ri_list) == 31  # 5月有31天
        assert liu_ri_list[0]["day"] == 1
        assert liu_ri_list[0]["ganzhi"] is not None

    def test_get_days_in_month(self):
        """测试获取月份天数"""
        assert self.service._get_days_in_month(1990, 1) == 31
        assert self.service._get_days_in_month(1990, 2) == 28  # 非闰年
        assert self.service._get_days_in_month(1992, 2) == 29  # 闰年
        assert self.service._get_days_in_month(1990, 4) == 30


class TestFortuneEngine:
    """测试运势计算引擎"""

    def setup_method(self):
        self.engine = FortuneEngine()

    def test_calc_fortune(self):
        """测试计算运势"""
        input_data = BirthInput(
            gregorian_datetime="1990-05-21T14:35:00",
            timezone="Asia/Shanghai",
            location=Location(latitude=31.2304, longitude=121.4737),
            calendar_pref=CalendarPref()
        )
        converter = TimeLocationConverter()
        time_result = converter.convert(input_data)

        pillars = PillarResult(
            year_pillar=YearPillar(stem="庚", branch="午", year=1990),
            month_pillar=MonthPillar(stem="辛", branch="巳", month_index=4),
            day_pillar=DayPillar(stem="丙", branch="辰", day_index_from_base=1),
            hour_pillar=HourPillar(stem="甲", branch="未", hour_index=7)
        )

        fortune_input = FortuneInput(
            pillars=pillars,
            time_result=time_result,
            person_info=PersonInfo(gender="male"),
            scope=FortuneScope(start_age=0, end_age=20)
        )

        fortune = self.engine.calc_fortune(fortune_input)

        assert fortune.da_yun is not None
        assert fortune.liu_nian is not None
        assert len(fortune.liu_nian) == 21  # 0-20岁

    def test_get_current_fortune(self):
        """测试获取当前运势"""
        from bazi.models.fortune import DaYun, LiuNian

        # 创建模拟的运势结果
        fortune_result = type('FortuneResult', (), {
            'da_yun': [
                DaYun(index=1, stem="辛", branch="午", ganzhi="辛午",
                      start_age=5, end_age=14),
                DaYun(index=2, stem="壬", branch="未", ganzhi="壬未",
                      start_age=15, end_age=24)
            ],
            'liu_nian': [
                LiuNian(year=2000, stem="庚", branch="辰", ganzhi="庚辰",
                       age=10, da_yun_index=1)
            ]
        })()

        current = self.engine.get_current_fortune(fortune_result, 10)
        assert current["current_age"] == 10
        assert current["da_yun"] is not None
        assert current["liu_nian"] is not None

    def test_analyze_year_fortune(self):
        """测试分析某年运势"""
        pillars = PillarResult(
            year_pillar=YearPillar(stem="庚", branch="午", year=1990),
            month_pillar=MonthPillar(stem="辛", branch="巳", month_index=4),
            day_pillar=DayPillar(stem="丙", branch="辰", day_index_from_base=1),
            hour_pillar=HourPillar(stem="甲", branch="未", hour_index=7)
        )

        analysis = self.engine.analyze_year_fortune(pillars, "甲子")
        assert analysis["year_ganzhi"] == "甲子"
        assert "relations" in analysis
