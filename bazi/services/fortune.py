"""
运势推演模块 - 计算大运、流年等运势信息
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple

from bazi.models.pillar import PillarResult
from bazi.models.time_location import TimeConvertResult
from bazi.models.fortune import (
    DaYunConfig, FortuneScope, PersonInfo, FortuneInput,
    DaYun, LiuNian, FortuneResult
)
from bazi.services.basic_data import StemRepository, BranchRepository
from bazi.services.time_location import SolarTermService


class DaYunService:
    """大运计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 起运方向规则
    # 阳年男、阴年女: 顺行
    # 阴年男、阳年女: 逆行
    DIRECTION_RULES = {
        ("yang", "male"): 1,      # 顺行
        ("yang", "female"): -1,   # 逆行
        ("yin", "male"): -1,      # 逆行
        ("yin", "female"): 1,     # 顺行
    }

    def __init__(self, solar_term_service: SolarTermService):
        self.solar_term_service = solar_term_service
        self.stem_repo = StemRepository()
        self.branch_repo = BranchRepository()

    def calc_start_age(
        self,
        time_result: TimeConvertResult,
        pillars: PillarResult,
        config: DaYunConfig,
        person_info: PersonInfo
    ) -> float:
        """
        计算起运岁数
        
        起运岁数 = 距节气天数 × 3天 = 1年
        
        Args:
            time_result: 时间转换结果
            pillars: 四柱
            config: 大运配置
            person_info: 个人信息
            
        Returns:
            起运岁数
        """
        # 获取方向
        direction = self._get_direction(pillars, person_info)

        # 获取出生时间
        utc_dt = datetime.fromisoformat(
            time_result.utc_datetime.replace("Z", "+00:00")
        )

        # 根据方向选择参照节气
        if direction > 0:
            # 顺行: 距下一节气的时间
            next_term_time = datetime.fromisoformat(
                time_result.solar_term.next_term_time_utc.replace("Z", "+00:00")
            )
            delta = next_term_time - utc_dt
        else:
            # 逆行: 距当前节气开始的时间
            current_term_time = datetime.fromisoformat(
                time_result.solar_term.start_time_utc.replace("Z", "+00:00")
            )
            delta = utc_dt - current_term_time

        # 计算天数
        days = delta.total_seconds() / 86400  # 秒转天

        # 计算起运岁数 (3天=1年)
        start_age = days / 3

        return start_age

    def generate_da_yun(
        self,
        pillars: PillarResult,
        config: DaYunConfig,
        start_age: float,
        person_info: PersonInfo,
        birth_year: int
    ) -> List[DaYun]:
        """
        生成大运序列
        
        Args:
            pillars: 四柱
            config: 大运配置
            start_age: 起运岁数
            person_info: 个人信息
            birth_year: 出生年
            
        Returns:
            大运列表
        """
        # 获取方向
        direction = self._get_direction(pillars, person_info)

        # 获取月柱干支索引
        month_stem = pillars.month_pillar.stem
        month_branch = pillars.month_pillar.branch
        month_stem_idx = self.STEMS.index(month_stem)
        month_branch_idx = self.BRANCHES.index(month_branch)

        # 起运年龄取整
        if config.start_age_floor == "floor":
            actual_start_age = int(start_age)
        elif config.start_age_floor == "ceil":
            actual_start_age = int(start_age) + 1 if start_age > int(start_age) else int(start_age)
        else:  # round
            actual_start_age = round(start_age)

        # 确保最小起运年龄
        actual_start_age = max(1, actual_start_age)

        # 生成大运
        result = []
        current_stem_idx = month_stem_idx
        current_branch_idx = month_branch_idx

        # 计算最大步数
        max_age = 80  # 默认到80岁
        max_steps = (max_age - actual_start_age) // config.da_yun_year_step + 1

        prev_start_age = actual_start_age

        for i in range(1, max_steps + 1):
            # 移动到下一个干支
            current_stem_idx = (current_stem_idx + direction + 10) % 10
            current_branch_idx = (current_branch_idx + direction + 12) % 12

            stem = self.STEMS[current_stem_idx]
            branch = self.BRANCHES[current_branch_idx]

            start = prev_start_age
            end = start + config.da_yun_year_step - 1

            # 计算时间范围
            start_year = birth_year + start
            end_year = birth_year + end
            start_datetime = f"{start_year}-01-01T00:00:00"
            end_datetime = f"{end_year}-12-31T23:59:59"

            result.append(DaYun(
                index=i,
                stem=stem,
                branch=branch,
                ganzhi=stem + branch,
                start_age=start,
                end_age=end,
                start_datetime=start_datetime,
                end_datetime=end_datetime
            ))

            prev_start_age = end + 1

        return result

    def _get_direction(self, pillars: PillarResult, person_info: PersonInfo) -> int:
        """
        获取大运方向
        
        Args:
            pillars: 四柱
            person_info: 个人信息
            
        Returns:
            1: 顺行, -1: 逆行
        """
        # 判断年干阴阳
        year_stem = pillars.year_pillar.stem
        stem_info = self.stem_repo.get_by_name(year_stem)
        yin_yang = stem_info.yin_yang.value if stem_info else "yang"

        # 根据规则确定方向
        key = (yin_yang, person_info.gender)
        return self.DIRECTION_RULES.get(key, 1)


class LiuNianService:
    """流年计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 以1984年(甲子年)为基准
    BASE_YEAR = 1984

    def generate_liu_nian(
        self,
        birth_year_ganzhi: str,
        birth_year: int,
        da_yun_list: List[DaYun],
        scope: FortuneScope
    ) -> List[LiuNian]:
        """
        生成流年序列
        
        Args:
            birth_year_ganzhi: 出生年干支
            birth_year: 出生公历年份
            da_yun_list: 大运列表
            scope: 范围
            
        Returns:
            流年列表
        """
        result = []

        for age in range(scope.start_age, scope.end_age + 1):
            year = birth_year + age
            ganzhi = self._calc_year_ganzhi(year)

            stem = ganzhi[0]
            branch = ganzhi[1]

            # 查找所属大运
            da_yun_index = self._find_da_yun_index(da_yun_list, age)

            result.append(LiuNian(
                year=year,
                stem=stem,
                branch=branch,
                ganzhi=ganzhi,
                age=age,
                da_yun_index=da_yun_index
            ))

        return result

    def _calc_year_ganzhi(self, year: int) -> str:
        """计算年份干支"""
        delta = year - self.BASE_YEAR
        stem_idx = delta % 10
        branch_idx = delta % 12

        if stem_idx < 0:
            stem_idx += 10
        if branch_idx < 0:
            branch_idx += 12

        return self.STEMS[stem_idx] + self.BRANCHES[branch_idx]

    def _find_da_yun_index(self, da_yun_list: List[DaYun], age: int) -> Optional[int]:
        """查找年龄对应的大运索引"""
        for da_yun in da_yun_list:
            if da_yun.start_age <= age <= da_yun.end_age:
                return da_yun.index
        return None


class LiuYueService:
    """流月计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 年干推月干基准
    YEAR_STEM_TO_MONTH_STEM_BASE = {
        "甲": 2, "己": 2,
        "乙": 4, "庚": 4,
        "丙": 6, "辛": 6,
        "丁": 8, "壬": 8,
        "戊": 0, "癸": 0,
    }

    def generate_liu_yue(self, year: int, year_stem: str) -> List[Dict[str, Any]]:
        """
        生成流月序列
        
        Args:
            year: 年份
            year_stem: 年干
            
        Returns:
            流月列表
        """
        result = []
        stem_base = self.YEAR_STEM_TO_MONTH_STEM_BASE.get(year_stem, 0)

        for month in range(1, 13):
            # 月支: 寅(2)开始
            branch_idx = (month + 1) % 12  # 1月=寅, 2月=卯...
            stem_idx = (stem_base + month - 1) % 10

            result.append({
                "month": month,
                "stem": self.STEMS[stem_idx],
                "branch": self.BRANCHES[branch_idx],
                "ganzhi": self.STEMS[stem_idx] + self.BRANCHES[branch_idx]
            })

        return result


class LiuRiService:
    """流日计算服务"""

    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def generate_liu_ri(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        生成流日序列
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            流日列表
        """
        result = []

        # 计算该月天数
        days_in_month = self._get_days_in_month(year, month)

        # 基准日期: 1900-01-31 为甲子日
        base_date = datetime(1900, 1, 31)

        for day in range(1, days_in_month + 1):
            current_date = datetime(year, month, day)
            delta = (current_date - base_date).days

            stem_idx = delta % 10
            branch_idx = delta % 12

            if stem_idx < 0:
                stem_idx += 10
            if branch_idx < 0:
                branch_idx += 12

            result.append({
                "day": day,
                "stem": self.STEMS[stem_idx],
                "branch": self.BRANCHES[branch_idx],
                "ganzhi": self.STEMS[stem_idx] + self.BRANCHES[branch_idx]
            })

        return result

    def _get_days_in_month(self, year: int, month: int) -> int:
        """获取月份天数"""
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 29
            return 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31


class FortuneEngine:
    """运势计算引擎"""

    def __init__(self):
        self.solar_term_service = SolarTermService()
        self.da_yun_service = DaYunService(self.solar_term_service)
        self.liu_nian_service = LiuNianService()
        self.liu_yue_service = LiuYueService()
        self.liu_ri_service = LiuRiService()

    def calc_fortune(self, input_data: FortuneInput) -> FortuneResult:
        """
        计算运势
        
        Args:
            input_data: 输入数据
            
        Returns:
            运势结果
        """
        # 获取出生年份
        birth_year = int(input_data.time_result.local_datetime_standard[:4])

        # 1. 计算起运年龄
        start_age = self.da_yun_service.calc_start_age(
            input_data.time_result,
            input_data.pillars,
            input_data.fortune_config,
            input_data.person_info
        )

        # 2. 生成大运
        da_yun_list = self.da_yun_service.generate_da_yun(
            input_data.pillars,
            input_data.fortune_config,
            start_age,
            input_data.person_info,
            birth_year
        )

        # 3. 生成流年
        birth_year_ganzhi = input_data.pillars.year_pillar.ganzhi
        liu_nian_list = self.liu_nian_service.generate_liu_nian(
            birth_year_ganzhi,
            birth_year,
            da_yun_list,
            input_data.scope
        )

        return FortuneResult(
            da_yun=da_yun_list,
            liu_nian=liu_nian_list
        )

    def get_current_fortune(
        self,
        fortune_result: FortuneResult,
        current_age: int
    ) -> Dict[str, Any]:
        """
        获取当前运势信息
        
        Args:
            fortune_result: 运势结果
            current_age: 当前年龄
            
        Returns:
            当前运势信息
        """
        current_da_yun = None
        current_liu_nian = None

        # 查找当前大运
        for da_yun in fortune_result.da_yun:
            if da_yun.start_age <= current_age <= da_yun.end_age:
                current_da_yun = da_yun
                break

        # 查找当前流年
        for liu_nian in fortune_result.liu_nian:
            if liu_nian.age == current_age:
                current_liu_nian = liu_nian
                break

        return {
            "current_age": current_age,
            "da_yun": current_da_yun.to_dict() if current_da_yun else None,
            "liu_nian": current_liu_nian.to_dict() if current_liu_nian else None
        }

    def analyze_year_fortune(
        self,
        pillars: PillarResult,
        year_ganzhi: str
    ) -> Dict[str, Any]:
        """
        分析某年运势
        
        Args:
            pillars: 四柱
            year_ganzhi: 年份干支
            
        Returns:
            分析结果
        """
        from bazi.services.basic_data import RelationService, TenGodService, StemRepository

        relation_service = RelationService()
        ten_god_service = TenGodService(StemRepository())
        stem_repo = StemRepository()

        year_stem = year_ganzhi[0]
        year_branch = year_ganzhi[1]

        # 分析与四柱的关系
        relations = {
            "year_pillar": {
                "stem_relation": ten_god_service.get_relation(
                    pillars.year_pillar.stem, year_stem
                )[0],
                "branch_relation": relation_service.get_branch_relations(
                    pillars.year_pillar.branch, year_branch
                )
            },
            "month_pillar": {
                "stem_relation": ten_god_service.get_relation(
                    pillars.month_pillar.stem, year_stem
                )[0],
                "branch_relation": relation_service.get_branch_relations(
                    pillars.month_pillar.branch, year_branch
                )
            },
            "day_pillar": {
                "stem_relation": ten_god_service.get_relation(
                    pillars.day_pillar.stem, year_stem
                )[0],
                "branch_relation": relation_service.get_branch_relations(
                    pillars.day_pillar.branch, year_branch
                )
            },
            "hour_pillar": {
                "stem_relation": ten_god_service.get_relation(
                    pillars.hour_pillar.stem, year_stem
                )[0],
                "branch_relation": relation_service.get_branch_relations(
                    pillars.hour_pillar.branch, year_branch
                )
            }
        }

        return {
            "year_ganzhi": year_ganzhi,
            "relations": relations
        }
