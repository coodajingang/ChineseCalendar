"""
运势推演模块的数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from bazi.models.pillar import PillarResult
from bazi.models.time_location import TimeConvertResult


@dataclass
class DaYunConfig:
    """大运配置"""
    da_yun_rule: str = "standard"
    da_yun_year_step: int = 10
    direction_rule: str = "by_gender_and_yangyin_year"
    start_age_floor: str = "to_integer"  # floor, ceil, round


@dataclass
class FortuneScope:
    """运势范围"""
    start_age: int = 0
    end_age: int = 80


@dataclass
class PersonInfo:
    """个人信息"""
    gender: str  # "male" | "female"


@dataclass
class FortuneInput:
    """运势计算输入"""
    pillars: PillarResult
    time_result: TimeConvertResult
    fortune_config: DaYunConfig = field(default_factory=DaYunConfig)
    person_info: PersonInfo = field(default_factory=lambda: PersonInfo(gender="male"))
    scope: FortuneScope = field(default_factory=FortuneScope)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pillars": self.pillars.to_dict(),
            "time_result": self.time_result.to_dict(),
            "fortune_config": {
                "da_yun_rule": self.fortune_config.da_yun_rule,
                "da_yun_year_step": self.fortune_config.da_yun_year_step,
                "direction_rule": self.fortune_config.direction_rule,
                "start_age_floor": self.fortune_config.start_age_floor
            },
            "person_info": {
                "gender": self.person_info.gender
            },
            "scope": {
                "start_age": self.scope.start_age,
                "end_age": self.scope.end_age
            }
        }


@dataclass
class DaYun:
    """大运"""
    index: int
    stem: str
    branch: str
    ganzhi: str
    start_age: int
    end_age: int
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "stem": self.stem,
            "branch": self.branch,
            "ganzhi": self.ganzhi,
            "start_age": self.start_age,
            "end_age": self.end_age,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime
        }


@dataclass
class LiuNian:
    """流年"""
    year: int
    stem: str
    branch: str
    ganzhi: str
    age: int
    da_yun_index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "stem": self.stem,
            "branch": self.branch,
            "ganzhi": self.ganzhi,
            "age": self.age,
            "da_yun_index": self.da_yun_index
        }


@dataclass
class FortuneResult:
    """运势结果"""
    da_yun: List[DaYun]
    liu_nian: List[LiuNian]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "da_yun": [d.to_dict() for d in self.da_yun],
            "liu_nian": [l.to_dict() for l in self.liu_nian]
        }
