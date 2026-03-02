"""
基础数据模型 - 定义八字命理系统的核心数据结构
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class YinYang(Enum):
    """阴阳"""
    YIN = "yin"
    YANG = "yang"


class FiveElement(Enum):
    """五行"""
    WOOD = "wood"
    FIRE = "fire"
    EARTH = "earth"
    METAL = "metal"
    WATER = "water"


class TenGod(Enum):
    """十神"""
    BI_JIAN = "bi_jian"           # 比肩
    JIE_CAI = "jie_cai"           # 劫财
    SHI_SHEN = "shi_shen"         # 食神
    SHANG_GUAN = "shang_guan"     # 伤官
    ZHENG_CAI = "zheng_cai"       # 正财
    PIAN_CAI = "pian_cai"         # 偏财
    ZHENG_GUAN = "zheng_guan"     # 正官
    QI_SHA = "qi_sha"             # 七杀
    ZHENG_YIN = "zheng_yin"       # 正印
    PIAN_YIN = "pian_yin"         # 偏印


class GrowthPhase(Enum):
    """十二长生"""
    CHANG_SHENG = "chang_sheng"   # 长生
    MU_YU = "mu_yu"               # 沐浴
    GUAN_DAI = "guan_dai"         # 冠带
    LIN_GUAN = "lin_guan"         # 临官
    DI_WANG = "di_wang"           # 帝旺
    SHUAI = "shuai"               # 衰
    BING = "bing"                 # 病
    SI = "si"                     # 死
    MU = "mu"                     # 墓
    JUE = "jue"                   # 绝
    TAI = "tai"                   # 胎
    YANG = "yang"                 # 养


class RelationType(Enum):
    """关系类型"""
    CLASH = "clash"       # 冲
    COMBINE = "combine"   # 合
    HARM = "harm"         # 害
    PUNISH = "punish"     # 刑
    BREAK = "break"       # 破


@dataclass
class HeavenlyStem:
    """天干"""
    id: int
    name: str
    yin_yang: YinYang
    element: FiveElement

    def __str__(self) -> str:
        return self.name


@dataclass
class HiddenStem:
    """藏干"""
    stem: str
    weight: float = 1.0


@dataclass
class EarthlyBranch:
    """地支"""
    id: int
    name: str
    yin_yang: YinYang
    element: FiveElement
    hidden_stems: List[HiddenStem] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name


@dataclass
class SolarTerm:
    """节气"""
    name: str
    index: int  # 0-23 对应 24 节气
    start_time_utc: Optional[str] = None

    def __str__(self) -> str:
        return self.name


@dataclass
class LunarDate:
    """农历日期"""
    year: int
    month: int
    day: int
    is_leap_month: bool = False

    def __str__(self) -> str:
        leap = "(闰)" if self.is_leap_month else ""
        return f"农历{self.year}年{leap}{self.month}月{self.day}日"


@dataclass
class GanZhi:
    """干支"""
    stem: str
    branch: str

    @property
    def ganzhi(self) -> str:
        return self.stem + self.branch

    def __str__(self) -> str:
        return self.ganzhi


@dataclass
class Location:
    """地点信息"""
    city_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None

    def __post_init__(self):
        if self.city_code is None and (self.latitude is None or self.longitude is None):
            raise ValueError("必须提供城市编码或经纬度")


@dataclass
class CalendarPref:
    """历法偏好设置"""
    use_true_solar_time: bool = True
    ephemeris_source: str = "internal"


@dataclass
class PillarItem:
    """柱"""
    stem: str
    branch: str

    @property
    def ganzhi(self) -> str:
        return self.stem + self.branch

    def __str__(self) -> str:
        return self.ganzhi
