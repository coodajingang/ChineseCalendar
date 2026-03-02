"""
八字命理系统 (BaZi Fortune Telling System)

基于中国八字命理理论的 Python 实现库，包含以下模块：
1. 时间地点转换模块 (time_location)
2. 四柱生成模块 (pillar)
3. 命理基础数据模块 (basic_data)
4. 运势推演模块 (fortune)

使用示例:
    from bazi import TimeLocationConverter, PillarGenerator, FortuneEngine
    from bazi.models import BirthInput, Location, CalendarPref, PersonInfo

    # 创建输入
    birth_input = BirthInput(
        gregorian_datetime="1990-05-21T14:35:00",
        timezone="Asia/Shanghai",
        location=Location(latitude=31.2304, longitude=121.4737),
        calendar_pref=CalendarPref(use_true_solar_time=True)
    )

    # 时间转换
    converter = TimeLocationConverter()
    time_result = converter.convert(birth_input)

    # 生成四柱
    pillar_input = PillarInput(time_result=time_result)
    generator = PillarGenerator()
    pillars = generator.generate(pillar_input)

    # 计算运势
    fortune_input = FortuneInput(
        pillars=pillars,
        time_result=time_result,
        person_info=PersonInfo(gender="male")
    )
    engine = FortuneEngine()
    fortune = engine.calc_fortune(fortune_input)
"""

# Version
__version__ = "1.0.0"
__author__ = "BaZi Development Team"

# Import main classes and functions
from bazi.models import (
    # Base models
    YinYang, FiveElement, TenGod, GrowthPhase, RelationType,
    HeavenlyStem, HiddenStem, EarthlyBranch, SolarTerm,
    LunarDate, GanZhi, Location, CalendarPref, PillarItem,
    # Time location models
    BirthInput, SolarTermInfo, LunarCalendarInfo, GanZhiDate, TimeConvertResult,
    # Pillar models
    PillarConfig, PillarInput, PillarItemDetail,
    YearPillar, MonthPillar, DayPillar, HourPillar, PillarResult,
    # Fortune models
    DaYunConfig, FortuneScope, PersonInfo, FortuneInput,
    DaYun, LiuNian, FortuneResult
)

from bazi.services import (
    # Basic data services
    StemRepository, BranchRepository, TenGodService,
    GrowthPhaseService, RelationService, ShenShaService,
    # Time location services
    TimezoneService, TrueSolarTimeService, SolarTermService,
    LunarCalendarService, GanzhiDayService, TimeLocationConverter,
    # Pillar services
    YearPillarService, MonthPillarService, DayPillarService,
    HourPillarService, PillarGenerator,
    # Fortune services
    DaYunService, LiuNianService, LiuYueService, LiuRiService, FortuneEngine
)

from bazi.config import BaziConfig, CalendarConfig, PillarConfig, FortuneConfig

from bazi.utils import (
    get_stem_branch_index, calc_ganzhi_from_index,
    get_element_relation, get_element_name, get_yinyang_name,
    get_ten_god_name, get_growth_phase_name,
    solar_term_index_to_name, hour_to_branch,
    format_datetime, to_json
)

__all__ = [
    # Version
    "__version__", "__author__",
    # Base models
    "YinYang", "FiveElement", "TenGod", "GrowthPhase", "RelationType",
    "HeavenlyStem", "HiddenStem", "EarthlyBranch", "SolarTerm",
    "LunarDate", "GanZhi", "Location", "CalendarPref", "PillarItem",
    # Time location models
    "BirthInput", "SolarTermInfo", "LunarCalendarInfo", "GanZhiDate", "TimeConvertResult",
    # Pillar models
    "PillarConfig", "PillarInput", "PillarItemDetail",
    "YearPillar", "MonthPillar", "DayPillar", "HourPillar", "PillarResult",
    # Fortune models
    "DaYunConfig", "FortuneScope", "PersonInfo", "FortuneInput",
    "DaYun", "LiuNian", "FortuneResult",
    # Basic data services
    "StemRepository", "BranchRepository", "TenGodService",
    "GrowthPhaseService", "RelationService", "ShenShaService",
    # Time location services
    "TimezoneService", "TrueSolarTimeService", "SolarTermService",
    "LunarCalendarService", "GanzhiDayService", "TimeLocationConverter",
    # Pillar services
    "YearPillarService", "MonthPillarService", "DayPillarService",
    "HourPillarService", "PillarGenerator",
    # Fortune services
    "DaYunService", "LiuNianService", "LiuYueService", "LiuRiService", "FortuneEngine",
    # Config
    "BaziConfig", "CalendarConfig", "PillarConfig", "FortuneConfig",
    # Utils
    "get_stem_branch_index", "calc_ganzhi_from_index",
    "get_element_relation", "get_element_name", "get_yinyang_name",
    "get_ten_god_name", "get_growth_phase_name",
    "solar_term_index_to_name", "hour_to_branch",
    "format_datetime", "to_json"
]
