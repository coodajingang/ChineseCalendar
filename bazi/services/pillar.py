"""
四柱生成模块 - 根据时间地点信息生成年、月、日、时四柱
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from bazi.models.time_location import TimeConvertResult
from bazi.models.pillar import (
    PillarConfig, PillarInput, PillarResult,
    YearPillar, MonthPillar, DayPillar, HourPillar
)
from bazi.services.basic_data import StemRepository, BranchRepository
from bazi.services.time_location import SolarTermService


class YearPillarService:
    """年柱计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 以1984年(甲子年)为基准
    BASE_YEAR = 1984
    BASE_STEM = 0  # 甲
    BASE_BRANCH = 0  # 子

    def __init__(self, solar_term_service: SolarTermService):
        self.solar_term_service = solar_term_service

    def get_year_pillar(
        self,
        time_result: TimeConvertResult,
        config: PillarConfig
    ) -> YearPillar:
        """
        计算年柱
        
        Args:
            time_result: 时间转换结果
            config: 四柱配置
            
        Returns:
            年柱
        """
        # 解析时间
        utc_dt = datetime.fromisoformat(
            time_result.utc_datetime.replace("Z", "+00:00")
        )
        local_year = int(time_result.local_datetime_standard[:4])

        # 判断年柱划分方式
        if config.year_pillar_rule == "by_li_chun":
            # 以立春划分
            year, is_before = self._get_year_by_li_chun(utc_dt, local_year)
        else:
            # 以农历正月初一划分 (简化处理，使用公历年份)
            year = local_year
            is_before = False

        # 计算干支
        delta = year - self.BASE_YEAR
        stem_index = (self.BASE_STEM + delta) % 10
        branch_index = (self.BASE_BRANCH + delta) % 12

        stem = self.STEMS[stem_index]
        branch = self.BRANCHES[branch_index]

        return YearPillar(
            stem=stem,
            branch=branch,
            year=year
        )

    def _get_year_by_li_chun(self, utc_dt: datetime, local_year: int) -> tuple:
        """根据立春确定年份"""
        # 获取当年立春时间
        li_chun_time = self.solar_term_service.calc_solar_term_date(local_year, 2)  # 立春索引为2

        if utc_dt < li_chun_time:
            # 立春前，属于上一年
            return local_year - 1, True
        else:
            return local_year, False

    def is_yang_year(self, year_ganzhi: str) -> bool:
        """判断是否阳年 (年干为阳干)"""
        stem = year_ganzhi[0]
        stem_index = self.STEMS.index(stem)
        return stem_index % 2 == 0


class MonthPillarService:
    """月柱计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 月支与节气的对应关系
    # 小寒(0): 丑月, 立春(2): 寅月, ..., 冬至(23): 子月
    TERM_TO_BRANCH = {
        0: 1,   # 小寒 -> 丑
        1: 1,   # 大寒 -> 丑 (大寒在丑月中)
        2: 2,   # 立春 -> 寅
        3: 2,   # 雨水 -> 寅
        4: 3,   # 惊蛰 -> 卯
        5: 3,   # 春分 -> 卯
        6: 4,   # 清明 -> 辰
        7: 4,   # 谷雨 -> 辰
        8: 5,   # 立夏 -> 巳
        9: 5,   # 小满 -> 巳
        10: 6,  # 芒种 -> 午
        11: 6,  # 夏至 -> 午
        12: 7,  # 小暑 -> 未
        13: 7,  # 大暑 -> 未
        14: 8,  # 立秋 -> 申
        15: 8,  # 处暑 -> 申
        16: 9,  # 白露 -> 酉
        17: 9,  # 秋分 -> 酉
        18: 10, # 寒露 -> 戌
        19: 10, # 霜降 -> 戌
        20: 11, # 立冬 -> 亥
        21: 11, # 小雪 -> 亥
        22: 0,  # 大雪 -> 子
        23: 0,  # 冬至 -> 子
    }

    # 年干推月干口诀
    # 甲己之年丙作首, 乙庚之岁戊为头
    # 丙辛之岁庚寅上, 丁壬壬位顺行流
    # 若言戊癸何方起, 甲寅之上去推求
    YEAR_STEM_TO_MONTH_STEM_BASE = {
        "甲": 2,  # 丙寅起
        "己": 2,
        "乙": 4,  # 戊寅起
        "庚": 4,
        "丙": 6,  # 庚寅起
        "辛": 6,
        "丁": 8,  # 壬寅起
        "壬": 8,
        "戊": 0,  # 甲寅起
        "癸": 0,
    }

    def __init__(self, solar_term_service: SolarTermService):
        self.solar_term_service = solar_term_service

    def get_month_pillar(
        self,
        time_result: TimeConvertResult,
        year_stem: str,
        config: PillarConfig
    ) -> MonthPillar:
        """
        计算月柱
        
        Args:
            time_result: 时间转换结果
            year_stem: 年干
            config: 四柱配置
            
        Returns:
            月柱
        """
        # 获取当前节气索引
        term_index = time_result.solar_term.index

        # 判断是否在节之后 (使用节来划分月令)
        # 节: 小寒(0), 立春(2), 惊蛰(4), ..., 大雪(22)
        # 气: 大寒(1), 雨水(3), ..., 冬至(23)

        # 根据节气确定月支
        month_branch_index = self.TERM_TO_BRANCH[term_index]

        # 根据年干确定月干
        stem_base = self.YEAR_STEM_TO_MONTH_STEM_BASE.get(year_stem, 0)

        # 从寅月(索引2)开始计算
        if month_branch_index >= 2:
            month_stem_index = (stem_base + month_branch_index - 2) % 10
        else:
            # 子月、丑月
            month_stem_index = (stem_base + month_branch_index + 10) % 10

        stem = self.STEMS[month_stem_index]
        branch = self.BRANCHES[month_branch_index]

        # 计算月序 (建寅为1)
        month_index = (month_branch_index - 1) % 12 + 1

        return MonthPillar(
            stem=stem,
            branch=branch,
            month_index=month_index
        )


class DayPillarService:
    """日柱计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 基准日期配置
    # 默认: 1900-01-31 为甲子日
    DEFAULT_BASE = datetime(1900, 1, 31, tzinfo=timezone.utc)

    def __init__(self):
        self._base_date = self.DEFAULT_BASE
        self._base_stem = 0  # 甲
        self._base_branch = 0  # 子

    def get_day_pillar(
        self,
        time_result: TimeConvertResult,
        config: PillarConfig
    ) -> DayPillar:
        """
        计算日柱
        
        Args:
            time_result: 时间转换结果
            config: 四柱配置
            
        Returns:
            日柱
        """
        # 解析时间
        utc_dt = datetime.fromisoformat(
            time_result.utc_datetime.replace("Z", "+00:00")
        )

        # 解析基准日期
        base_date = self._parse_base_date(config.day_base_reference)

        # 计算天数差
        days = (utc_dt.date() - base_date.date()).days

        # 计算60甲子索引
        ganzhi_index = days % 60
        if ganzhi_index < 0:
            ganzhi_index += 60

        # 计算天干地支索引
        stem_index = ganzhi_index % 10
        branch_index = ganzhi_index % 12

        stem = self.STEMS[stem_index]
        branch = self.BRANCHES[branch_index]

        return DayPillar(
            stem=stem,
            branch=branch,
            day_index_from_base=days
        )

    def _parse_base_date(self, base_str: str) -> datetime:
        """解析基准日期字符串"""
        try:
            return datetime.fromisoformat(base_str).replace(tzinfo=timezone.utc)
        except:
            return self.DEFAULT_BASE


class HourPillarService:
    """时柱计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 时辰与地支对应
    # 子时: 23:00-01:00 (跨日)
    # 丑时: 01:00-03:00
    # ...
    HOUR_TO_BRANCH = [
        (23, 24, 0),   # 子时: 23:00-24:00
        (0, 1, 0),     # 子时: 00:00-01:00
        (1, 3, 1),     # 丑时
        (3, 5, 2),     # 寅时
        (5, 7, 3),     # 卯时
        (7, 9, 4),     # 辰时
        (9, 11, 5),    # 巳时
        (11, 13, 6),   # 午时
        (13, 15, 7),   # 未时
        (15, 17, 8),   # 申时
        (17, 19, 9),   # 酉时
        (19, 21, 10),  # 戌时
        (21, 23, 11),  # 亥时
    ]

    # 日干推时干口诀
    # 甲己还加甲, 乙庚丙作初
    # 丙辛从戊起, 丁壬庚子居
    # 戊癸何方发, 壬子是真途
    DAY_STEM_TO_HOUR_STEM_BASE = {
        "甲": 0,  # 甲子起
        "己": 0,
        "乙": 2,  # 丙子起
        "庚": 2,
        "丙": 4,  # 戊子起
        "辛": 4,
        "丁": 6,  # 庚子起
        "壬": 6,
        "戊": 8,  # 壬子起
        "癸": 8,
    }

    def get_hour_pillar(
        self,
        time_result: TimeConvertResult,
        day_stem: str,
        config: PillarConfig
    ) -> HourPillar:
        """
        计算时柱
        
        Args:
            time_result: 时间转换结果
            day_stem: 日干
            config: 四柱配置
            
        Returns:
            时柱
        """
        # 获取真太阳时或标准时间
        if time_result.local_datetime_true_solar:
            time_str = time_result.local_datetime_true_solar
        else:
            time_str = time_result.local_datetime_standard

        # 解析时间
        dt = datetime.fromisoformat(time_str)
        hour = dt.hour
        minute = dt.minute

        # 处理子时的特殊情况 (23:00-01:00)
        # 23:00-24:00 算当天夜子时
        # 00:00-01:00 算次天早子时 (这里简化处理)

        # 确定时辰
        branch_index = self._get_branch_index(hour)

        # 根据日干确定时干
        stem_base = self.DAY_STEM_TO_HOUR_STEM_BASE.get(day_stem, 0)
        stem_index = (stem_base + branch_index) % 10

        stem = self.STEMS[stem_index]
        branch = self.BRANCHES[branch_index]

        return HourPillar(
            stem=stem,
            branch=branch,
            hour_index=branch_index
        )

    def _get_branch_index(self, hour: int) -> int:
        """根据小时获取地支索引"""
        for start, end, branch_idx in self.HOUR_TO_BRANCH:
            if start <= hour < end:
                return branch_idx
        return 0


class PillarGenerator:
    """四柱生成器"""

    def __init__(self):
        self.solar_term_service = SolarTermService()
        self.year_pillar_service = YearPillarService(self.solar_term_service)
        self.month_pillar_service = MonthPillarService(self.solar_term_service)
        self.day_pillar_service = DayPillarService()
        self.hour_pillar_service = HourPillarService()

    def generate(self, input_data: PillarInput) -> PillarResult:
        """
        生成四柱
        
        Args:
            input_data: 输入数据
            
        Returns:
            四柱结果
        """
        time_result = input_data.time_result
        config = input_data.pillar_config

        # 1. 计算年柱
        year_pillar = self.year_pillar_service.get_year_pillar(time_result, config)

        # 2. 计算月柱
        month_pillar = self.month_pillar_service.get_month_pillar(
            time_result, year_pillar.stem, config
        )

        # 3. 计算日柱
        day_pillar = self.day_pillar_service.get_day_pillar(time_result, config)

        # 4. 计算时柱
        hour_pillar = self.hour_pillar_service.get_hour_pillar(
            time_result, day_pillar.stem, config
        )

        return PillarResult(
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar
        )

    def get_pillar_by_ganzhi(self, ganzhi: str) -> Dict[str, Any]:
        """
        根据干支获取详细信息
        
        Args:
            ganzhi: 干支字符串
            
        Returns:
            详细信息字典
        """
        if len(ganzhi) != 2:
            return {}

        stem, branch = ganzhi[0], ganzhi[1]
        stem_repo = StemRepository()
        branch_repo = BranchRepository()

        stem_info = stem_repo.get_by_name(stem)
        branch_info = branch_repo.get_by_name(branch)

        return {
            "stem": {
                "name": stem,
                "yin_yang": stem_info.yin_yang.value if stem_info else None,
                "element": stem_info.element.value if stem_info else None
            },
            "branch": {
                "name": branch,
                "yin_yang": branch_info.yin_yang.value if branch_info else None,
                "element": branch_info.element.value if branch_info else None,
                "hidden_stems": [
                    {"stem": hs.stem, "weight": hs.weight}
                    for hs in branch_info.hidden_stems
                ] if branch_info else []
            }
        }
