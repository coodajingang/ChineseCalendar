"""
八字命理系统配置
"""
from typing import Dict, Any
from dataclasses import dataclass, field
import yaml
import os


@dataclass
class CalendarConfig:
    """历法配置"""
    use_true_solar_time: bool = True
    ephemeris_source: str = "internal"
    supported_year_range_start: int = 1900
    supported_year_range_end: int = 2100
    zone_longitude_map: Dict[str, float] = field(default_factory=lambda: {
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
    })


@dataclass
class PillarConfig:
    """四柱配置"""
    year_pillar_rule: str = "by_li_chun"  # by_li_chun | by_lunar_new_year
    month_pillar_rule: str = "standard"
    hour_pillar_rule: str = "standard"
    day_base_reference: str = "1900-01-31"


@dataclass
class FortuneConfig:
    """大运配置"""
    da_yun_rule: str = "standard"
    da_yun_year_step: int = 10
    direction_rule: str = "by_gender_and_yangyin_year"
    start_age_formula_type: str = "linear"
    start_age_factor: float = 1 / 3  # 3天=1年
    start_age_round: str = "floor"


@dataclass
class BaziConfig:
    """八字系统总配置"""
    calendar: CalendarConfig = field(default_factory=CalendarConfig)
    pillar: PillarConfig = field(default_factory=PillarConfig)
    fortune: FortuneConfig = field(default_factory=FortuneConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "BaziConfig":
        """从YAML文件加载配置"""
        if not os.path.exists(yaml_path):
            return cls()

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        calendar_data = data.get("calendar", {})
        pillar_data = data.get("pillar", {})
        fortune_data = data.get("fortune", {})

        calendar_config = CalendarConfig(
            use_true_solar_time=calendar_data.get("use_true_solar_time", True),
            ephemeris_source=calendar_data.get("ephemeris_source", "internal"),
            supported_year_range_start=calendar_data.get("supported_year_range", {}).get("start", 1900),
            supported_year_range_end=calendar_data.get("supported_year_range", {}).get("end", 2100),
            zone_longitude_map=calendar_data.get("zone_longitude_map", {})
        )

        pillar_config = PillarConfig(
            year_pillar_rule=pillar_data.get("year_pillar_rule", "by_li_chun"),
            month_pillar_rule=pillar_data.get("month_pillar_rule", "standard"),
            hour_pillar_rule=pillar_data.get("hour_pillar_rule", "standard"),
            day_base_reference=pillar_data.get("day_base_reference", "1900-01-31")
        )

        fortune_config = FortuneConfig(
            da_yun_rule=fortune_data.get("da_yun_rule", "standard"),
            da_yun_year_step=fortune_data.get("da_yun_year_step", 10),
            direction_rule=fortune_data.get("direction_rule", "by_gender_and_yangyin_year"),
            start_age_formula_type=fortune_data.get("start_age_formula", {}).get("type", "linear"),
            start_age_factor=fortune_data.get("start_age_formula", {}).get("factor", 1 / 3),
            start_age_round=fortune_data.get("start_age_formula", {}).get("round", "floor")
        )

        return cls(
            calendar=calendar_config,
            pillar=pillar_config,
            fortune=fortune_config
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "calendar": {
                "use_true_solar_time": self.calendar.use_true_solar_time,
                "ephemeris_source": self.calendar.ephemeris_source,
                "supported_year_range": {
                    "start": self.calendar.supported_year_range_start,
                    "end": self.calendar.supported_year_range_end
                },
                "zone_longitude_map": self.calendar.zone_longitude_map
            },
            "pillar": {
                "year_pillar_rule": self.pillar.year_pillar_rule,
                "month_pillar_rule": self.pillar.month_pillar_rule,
                "hour_pillar_rule": self.pillar.hour_pillar_rule,
                "day_base_reference": self.pillar.day_base_reference
            },
            "fortune": {
                "da_yun_rule": self.fortune.da_yun_rule,
                "da_yun_year_step": self.fortune.da_yun_year_step,
                "direction_rule": self.fortune.direction_rule,
                "start_age_formula": {
                    "type": self.fortune.start_age_formula_type,
                    "factor": self.fortune.start_age_factor,
                    "round": self.fortune.start_age_round
                }
            }
        }
