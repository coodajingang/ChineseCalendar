"""
四柱生成模块的数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from bazi.models.time_location import TimeConvertResult


@dataclass
class PillarConfig:
    """四柱计算配置"""
    year_pillar_rule: str = "by_li_chun"     # 年柱划分规则: by_li_chun 或 by_lunar_new_year
    month_pillar_rule: str = "standard"      # 月柱计算流派
    hour_pillar_rule: str = "standard"       # 时柱计算规则: 子初、子正等
    day_base_reference: str = "1900-01-31"   # 日干支基准日期


@dataclass
class PillarInput:
    """四柱计算输入"""
    time_result: TimeConvertResult
    pillar_config: PillarConfig = field(default_factory=PillarConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_result": self.time_result.to_dict(),
            "pillar_config": {
                "year_pillar_rule": self.pillar_config.year_pillar_rule,
                "month_pillar_rule": self.pillar_config.month_pillar_rule,
                "hour_pillar_rule": self.pillar_config.hour_pillar_rule,
                "day_base_reference": self.pillar_config.day_base_reference
            }
        }


@dataclass
class PillarItemDetail:
    """柱详情"""
    stem: str
    branch: str

    @property
    def ganzhi(self) -> str:
        return self.stem + self.branch

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stem": self.stem,
            "branch": self.branch,
            "ganzhi": self.ganzhi
        }


@dataclass
class YearPillar(PillarItemDetail):
    """年柱"""
    year: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["year"] = self.year
        return result


@dataclass
class MonthPillar(PillarItemDetail):
    """月柱"""
    month_index: Optional[int] = None  # 建寅为1

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["month_index"] = self.month_index
        return result


@dataclass
class DayPillar(PillarItemDetail):
    """日柱"""
    day_index_from_base: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["day_index_from_base"] = self.day_index_from_base
        return result


@dataclass
class HourPillar(PillarItemDetail):
    """时柱"""
    hour_index: Optional[int] = None  # 子=0，丑=1...

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["hour_index"] = self.hour_index
        return result


@dataclass
class PillarResult:
    """四柱结果"""
    year_pillar: YearPillar
    month_pillar: MonthPillar
    day_pillar: DayPillar
    hour_pillar: HourPillar

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year_pillar": self.year_pillar.to_dict(),
            "month_pillar": self.month_pillar.to_dict(),
            "day_pillar": self.day_pillar.to_dict(),
            "hour_pillar": self.hour_pillar.to_dict()
        }

    def __str__(self) -> str:
        return f"年柱: {self.year_pillar.ganzhi}, 月柱: {self.month_pillar.ganzhi}, 日柱: {self.day_pillar.ganzhi}, 时柱: {self.hour_pillar.ganzhi}"
