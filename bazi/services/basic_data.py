"""
命理基础数据模块 - 提供天干、地支、五行、十神等基础数据
"""
from typing import List, Dict, Any, Optional, Tuple
from bazi.models.base import (
    YinYang, FiveElement, TenGod, GrowthPhase, RelationType,
    HeavenlyStem, HiddenStem, EarthlyBranch
)


class StemRepository:
    """天干数据仓库"""

    # 天干基础数据
    STEMS_DATA: List[Dict[str, Any]] = [
        {"id": 0, "name": "甲", "yin_yang": YinYang.YANG, "element": FiveElement.WOOD},
        {"id": 1, "name": "乙", "yin_yang": YinYang.YIN, "element": FiveElement.WOOD},
        {"id": 2, "name": "丙", "yin_yang": YinYang.YANG, "element": FiveElement.FIRE},
        {"id": 3, "name": "丁", "yin_yang": YinYang.YIN, "element": FiveElement.FIRE},
        {"id": 4, "name": "戊", "yin_yang": YinYang.YANG, "element": FiveElement.EARTH},
        {"id": 5, "name": "己", "yin_yang": YinYang.YIN, "element": FiveElement.EARTH},
        {"id": 6, "name": "庚", "yin_yang": YinYang.YANG, "element": FiveElement.METAL},
        {"id": 7, "name": "辛", "yin_yang": YinYang.YIN, "element": FiveElement.METAL},
        {"id": 8, "name": "壬", "yin_yang": YinYang.YANG, "element": FiveElement.WATER},
        {"id": 9, "name": "癸", "yin_yang": YinYang.YIN, "element": FiveElement.WATER},
    ]

    # 天干名称到索引的映射
    NAME_TO_INDEX: Dict[str, int] = {
        "甲": 0, "乙": 1, "丙": 2, "丁": 3, "戊": 4,
        "己": 5, "庚": 6, "辛": 7, "壬": 8, "癸": 9
    }

    def __init__(self):
        self._stems: List[HeavenlyStem] = [
            HeavenlyStem(**data) for data in self.STEMS_DATA
        ]

    def get_by_id(self, id: int) -> Optional[HeavenlyStem]:
        """根据索引获取天干"""
        if 0 <= id < len(self._stems):
            return self._stems[id]
        return None

    def get_by_name(self, name: str) -> Optional[HeavenlyStem]:
        """根据名称获取天干"""
        idx = self.NAME_TO_INDEX.get(name)
        if idx is not None:
            return self._stems[idx]
        return None

    def get_index(self, name: str) -> int:
        """获取天干索引"""
        return self.NAME_TO_INDEX.get(name, -1)

    def get_all(self) -> List[HeavenlyStem]:
        """获取所有天干"""
        return self._stems.copy()

    @property
    def names(self) -> List[str]:
        """获取所有天干名称"""
        return [s.name for s in self._stems]


class BranchRepository:
    """地支数据仓库"""

    # 地支基础数据（含藏干）
    BRANCHES_DATA: List[Dict[str, Any]] = [
        {
            "id": 0, "name": "子", "yin_yang": YinYang.YANG, "element": FiveElement.WATER,
            "hidden_stems": [{"stem": "癸", "weight": 1.0}]
        },
        {
            "id": 1, "name": "丑", "yin_yang": YinYang.YIN, "element": FiveElement.EARTH,
            "hidden_stems": [
                {"stem": "己", "weight": 0.5},
                {"stem": "癸", "weight": 0.3},
                {"stem": "辛", "weight": 0.2}
            ]
        },
        {
            "id": 2, "name": "寅", "yin_yang": YinYang.YANG, "element": FiveElement.WOOD,
            "hidden_stems": [
                {"stem": "甲", "weight": 0.5},
                {"stem": "丙", "weight": 0.3},
                {"stem": "戊", "weight": 0.2}
            ]
        },
        {
            "id": 3, "name": "卯", "yin_yang": YinYang.YIN, "element": FiveElement.WOOD,
            "hidden_stems": [{"stem": "乙", "weight": 1.0}]
        },
        {
            "id": 4, "name": "辰", "yin_yang": YinYang.YANG, "element": FiveElement.EARTH,
            "hidden_stems": [
                {"stem": "戊", "weight": 0.5},
                {"stem": "乙", "weight": 0.3},
                {"stem": "癸", "weight": 0.2}
            ]
        },
        {
            "id": 5, "name": "巳", "yin_yang": YinYang.YANG, "element": FiveElement.FIRE,
            "hidden_stems": [
                {"stem": "丙", "weight": 0.5},
                {"stem": "戊", "weight": 0.3},
                {"stem": "庚", "weight": 0.2}
            ]
        },
        {
            "id": 6, "name": "午", "yin_yang": YinYang.YIN, "element": FiveElement.FIRE,
            "hidden_stems": [
                {"stem": "丁", "weight": 0.7},
                {"stem": "己", "weight": 0.3}
            ]
        },
        {
            "id": 7, "name": "未", "yin_yang": YinYang.YIN, "element": FiveElement.EARTH,
            "hidden_stems": [
                {"stem": "己", "weight": 0.5},
                {"stem": "丁", "weight": 0.3},
                {"stem": "乙", "weight": 0.2}
            ]
        },
        {
            "id": 8, "name": "申", "yin_yang": YinYang.YANG, "element": FiveElement.METAL,
            "hidden_stems": [
                {"stem": "庚", "weight": 0.5},
                {"stem": "壬", "weight": 0.3},
                {"stem": "戊", "weight": 0.2}
            ]
        },
        {
            "id": 9, "name": "酉", "yin_yang": YinYang.YIN, "element": FiveElement.METAL,
            "hidden_stems": [{"stem": "辛", "weight": 1.0}]
        },
        {
            "id": 10, "name": "戌", "yin_yang": YinYang.YANG, "element": FiveElement.EARTH,
            "hidden_stems": [
                {"stem": "戊", "weight": 0.5},
                {"stem": "辛", "weight": 0.3},
                {"stem": "丁", "weight": 0.2}
            ]
        },
        {
            "id": 11, "name": "亥", "yin_yang": YinYang.YIN, "element": FiveElement.WATER,
            "hidden_stems": [
                {"stem": "壬", "weight": 0.7},
                {"stem": "甲", "weight": 0.3}
            ]
        },
    ]

    # 地支名称到索引的映射
    NAME_TO_INDEX: Dict[str, int] = {
        "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4,
        "巳": 5, "午": 6, "未": 7, "申": 8, "酉": 9,
        "戌": 10, "亥": 11
    }

    def __init__(self):
        self._branches: List[EarthlyBranch] = []
        for data in self.BRANCHES_DATA:
            # Make a copy to avoid modifying the class-level data
            data_copy = data.copy()
            hidden_stems_data = data_copy.pop("hidden_stems", [])
            hidden_stems = [
                HiddenStem(stem=hs["stem"], weight=hs["weight"])
                for hs in hidden_stems_data
            ]
            branch = EarthlyBranch(hidden_stems=hidden_stems, **data_copy)
            self._branches.append(branch)

    def get_by_id(self, id: int) -> Optional[EarthlyBranch]:
        """根据索引获取地支"""
        if 0 <= id < len(self._branches):
            return self._branches[id]
        return None

    def get_by_name(self, name: str) -> Optional[EarthlyBranch]:
        """根据名称获取地支"""
        idx = self.NAME_TO_INDEX.get(name)
        if idx is not None:
            return self._branches[idx]
        return None

    def get_index(self, name: str) -> int:
        """获取地支索引"""
        return self.NAME_TO_INDEX.get(name, -1)

    def get_hidden_stems(self, branch_name: str) -> List[HiddenStem]:
        """获取地支的藏干"""
        branch = self.get_by_name(branch_name)
        if branch:
            return branch.hidden_stems.copy()
        return []

    def get_all(self) -> List[EarthlyBranch]:
        """获取所有地支"""
        return self._branches.copy()

    @property
    def names(self) -> List[str]:
        """获取所有地支名称"""
        return [b.name for b in self._branches]


class TenGodService:
    """十神关系服务"""

    # 五行相生相克关系定义
    # 生我者为印，我生者为食伤，克我者为官杀，我克者为财，同我者为比劫

    ELEMENT_RELATION_MAP: Dict[str, str] = {
        # key: (my_element, other_element) -> relation
        # 同我者
        ("wood", "wood"): "self",
        ("fire", "fire"): "self",
        ("earth", "earth"): "self",
        ("metal", "metal"): "self",
        ("water", "water"): "self",
        # 我生者 (output)
        ("wood", "fire"): "output",
        ("fire", "earth"): "output",
        ("earth", "metal"): "output",
        ("metal", "water"): "output",
        ("water", "wood"): "output",
        # 我克者 (wealth)
        ("wood", "earth"): "wealth",
        ("fire", "metal"): "wealth",
        ("earth", "water"): "wealth",
        ("metal", "wood"): "wealth",
        ("water", "fire"): "wealth",
        # 克我者 (power)
        ("wood", "metal"): "power",
        ("fire", "water"): "power",
        ("earth", "wood"): "power",
        ("metal", "fire"): "power",
        ("water", "earth"): "power",
        # 生我者 (resource)
        ("wood", "water"): "resource",
        ("fire", "wood"): "resource",
        ("earth", "fire"): "resource",
        ("metal", "earth"): "resource",
        ("water", "metal"): "resource",
    }

    # 十神名称映射
    TEN_GOD_MAP: Dict[str, Tuple[str, str]] = {
        # relation + same_yinyang -> (同阴阳性名称, 异阴阳性名称)
        "self": ("比肩", "劫财"),
        "output": ("食神", "伤官"),
        "wealth": ("偏财", "正财"),
        "power": ("七杀", "正官"),
        "resource": ("偏印", "正印"),
    }

    def __init__(self, stem_repo: StemRepository):
        self.stem_repo = stem_repo

    def get_relation(self, day_stem: str, target_stem: str) -> Tuple[str, TenGod]:
        """
        获取日干与目标天干的十神关系
        
        Args:
            day_stem: 日干
            target_stem: 目标天干
            
        Returns:
            (十神名称, 十神枚举)
        """
        day = self.stem_repo.get_by_name(day_stem)
        target = self.stem_repo.get_by_name(target_stem)

        if not day or not target:
            return ("未知", TenGod.BI_JIAN)

        # 获取五行关系
        relation = self.ELEMENT_RELATION_MAP.get(
            (day.element.value, target.element.value), "self"
        )

        # 判断阴阳是否相同
        same_yinyang = day.yin_yang == target.yin_yang

        # 获取十神名称
        names = self.TEN_GOD_MAP.get(relation, ("比肩", "劫财"))
        god_name = names[0] if same_yinyang else names[1]

        # 映射到枚举
        god_enum = self._name_to_enum(god_name)

        return (god_name, god_enum)

    def _name_to_enum(self, name: str) -> TenGod:
        """将十神名称转换为枚举"""
        mapping = {
            "比肩": TenGod.BI_JIAN,
            "劫财": TenGod.JIE_CAI,
            "食神": TenGod.SHI_SHEN,
            "伤官": TenGod.SHANG_GUAN,
            "正财": TenGod.ZHENG_CAI,
            "偏财": TenGod.PIAN_CAI,
            "正官": TenGod.ZHENG_GUAN,
            "七杀": TenGod.QI_SHA,
            "正印": TenGod.ZHENG_YIN,
            "偏印": TenGod.PIAN_YIN,
        }
        return mapping.get(name, TenGod.BI_JIAN)


class GrowthPhaseService:
    """十二长生服务"""

    # 十二长生表 - 以日主五行为参照
    GROWTH_PHASE_DATA: Dict[str, Dict[str, str]] = {
        "wood": {
            "亥": "长生", "子": "沐浴", "丑": "冠带", "寅": "临官",
            "卯": "帝旺", "辰": "衰", "巳": "病", "午": "死",
            "未": "墓", "申": "绝", "酉": "胎", "戌": "养"
        },
        "fire": {
            "寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官",
            "午": "帝旺", "未": "衰", "申": "病", "酉": "死",
            "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"
        },
        "earth": {
            "寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官",
            "午": "帝旺", "未": "衰", "申": "病", "酉": "死",
            "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"
        },
        "metal": {
            "巳": "长生", "午": "沐浴", "未": "冠带", "申": "临官",
            "酉": "帝旺", "戌": "衰", "亥": "病", "子": "死",
            "丑": "墓", "寅": "绝", "卯": "胎", "辰": "养"
        },
        "water": {
            "申": "长生", "酉": "沐浴", "戌": "冠带", "亥": "临官",
            "子": "帝旺", "丑": "衰", "寅": "病", "卯": "死",
            "辰": "墓", "巳": "绝", "午": "胎", "未": "养"
        }
    }

    PHASE_TO_ENUM: Dict[str, GrowthPhase] = {
        "长生": GrowthPhase.CHANG_SHENG,
        "沐浴": GrowthPhase.MU_YU,
        "冠带": GrowthPhase.GUAN_DAI,
        "临官": GrowthPhase.LIN_GUAN,
        "帝旺": GrowthPhase.DI_WANG,
        "衰": GrowthPhase.SHUAI,
        "病": GrowthPhase.BING,
        "死": GrowthPhase.SI,
        "墓": GrowthPhase.MU,
        "绝": GrowthPhase.JUE,
        "胎": GrowthPhase.TAI,
        "养": GrowthPhase.YANG,
    }

    def __init__(self, stem_repo: StemRepository):
        self.stem_repo = stem_repo

    def get_phase(self, day_element: str, branch_name: str) -> Tuple[str, GrowthPhase]:
        """
        获取日主五行在某地支的十二长生状态
        
        Args:
            day_element: 日主五行 (wood/fire/earth/metal/water)
            branch_name: 地支名称
            
        Returns:
            (长生阶段名称, 长生阶段枚举)
        """
        element_data = self.GROWTH_PHASE_DATA.get(day_element, {})
        phase_name = element_data.get(branch_name, "未知")
        phase_enum = self.PHASE_TO_ENUM.get(phase_name, GrowthPhase.CHANG_SHENG)
        return (phase_name, phase_enum)

    def get_phase_by_stem(self, day_stem: str, branch_name: str) -> Tuple[str, GrowthPhase]:
        """
        根据日干获取十二长生状态
        """
        stem = self.stem_repo.get_by_name(day_stem)
        if stem:
            return self.get_phase(stem.element.value, branch_name)
        return ("未知", GrowthPhase.CHANG_SHENG)


class RelationService:
    """地支关系服务（刑冲合害破）"""

    # 六冲
    CLASH_PAIRS: List[Tuple[str, str]] = [
        ("子", "午"), ("丑", "未"), ("寅", "申"),
        ("卯", "酉"), ("辰", "戌"), ("巳", "亥")
    ]

    # 六合
    COMBINE_PAIRS: List[Tuple[str, str]] = [
        ("子", "丑"), ("寅", "亥"), ("卯", "戌"),
        ("辰", "酉"), ("巳", "申"), ("午", "未")
    ]

    # 三合
    THREE_COMBINE: List[Tuple[str, str, str]] = [
        ("申", "子", "辰"),  # 水局
        ("亥", "卯", "未"),  # 木局
        ("寅", "午", "戌"),  # 火局
        ("巳", "酉", "丑"),  # 金局
    ]

    # 六害
    HARM_PAIRS: List[Tuple[str, str]] = [
        ("子", "未"), ("丑", "午"), ("寅", "巳"),
        ("卯", "辰"), ("申", "亥"), ("酉", "戌")
    ]

    # 三刑
    PUNISH_TRIPLE: List[Tuple[str, str, str]] = [
        ("寅", "巳", "申"),
        ("丑", "戌", "未"),
    ]

    # 自刑
    SELF_PUNISH: List[str] = ["辰", "午", "酉", "亥"]

    # 相破
    BREAK_PAIRS: List[Tuple[str, str]] = [
        ("子", "酉"), ("丑", "辰"), ("寅", "亥"),
        ("卯", "午"), ("巳", "申"), ("未", "戌")
    ]

    def get_branch_relations(self, b1: str, b2: str) -> List[Tuple[RelationType, str]]:
        """
        获取两个地支之间的关系
        
        Args:
            b1: 第一个地支
            b2: 第二个地支
            
        Returns:
            关系列表 [(关系类型, 关系描述), ...]
        """
        relations = []

        # 检查冲
        for pair in self.CLASH_PAIRS:
            if (b1, b2) == pair or (b2, b1) == pair:
                relations.append((RelationType.CLASH, f"{b1}{b2}相冲"))

        # 检查合
        for pair in self.COMBINE_PAIRS:
            if (b1, b2) == pair or (b2, b1) == pair:
                relations.append((RelationType.COMBINE, f"{b1}{b2}相合"))

        # 检查害
        for pair in self.HARM_PAIRS:
            if (b1, b2) == pair or (b2, b1) == pair:
                relations.append((RelationType.HARM, f"{b1}{b2}相害"))

        # 检查破
        for pair in self.BREAK_PAIRS:
            if (b1, b2) == pair or (b2, b1) == pair:
                relations.append((RelationType.BREAK, f"{b1}{b2}相破"))

        return relations

    def check_punish(self, branches: List[str]) -> List[str]:
        """
        检查三刑
        
        Args:
            branches: 地支列表
            
        Returns:
            刑的关系描述列表
        """
        result = []
        branch_set = set(branches)

        # 检查三刑
        for triple in self.PUNISH_TRIPLE:
            if set(triple).issubset(branch_set):
                result.append(f"{''.join(triple)}三刑")

        # 检查自刑
        for b in branches:
            if b in self.SELF_PUNISH and branches.count(b) >= 2:
                result.append(f"{b}自刑")

        # 子卯相刑
        if "子" in branch_set and "卯" in branch_set:
            result.append("子卯相刑")

        return result

    def check_three_combine(self, branches: List[str]) -> List[str]:
        """
        检查三合局
        
        Args:
            branches: 地支列表
            
        Returns:
            三合局描述列表
        """
        result = []
        branch_set = set(branches)

        for triple in self.THREE_COMBINE:
            if set(triple).issubset(branch_set):
                result.append(f"{''.join(triple)}三合局")

        return result


class ShenShaService:
    """神煞服务"""

    # 天乙贵人
    TIAN_YI_GUI_REN: Dict[str, List[str]] = {
        "甲": ["丑", "未"],
        "乙": ["子", "申"],
        "丙": ["亥", "酉"],
        "丁": ["亥", "酉"],
        "戊": ["丑", "未"],
        "己": ["子", "申"],
        "庚": ["丑", "未"],
        "辛": ["午", "寅"],
        "壬": ["卯", "巳"],
        "癸": ["卯", "巳"],
    }

    # 桃花 (以年支或日支为基准)
    TAO_HUA: Dict[str, str] = {
        "子": "卯", "卯": "子",
        "午": "卯", "酉": "子",
        "寅": "卯", "申": "子",
        "巳": "卯", "亥": "子",
        "辰": "酉", "戌": "卯",
        "丑": "午", "未": "子",
    }

    # 驿马
    YI_MA: Dict[str, str] = {
        "寅": "申", "午": "申", "戌": "申",
        "申": "寅", "子": "寅", "辰": "寅",
        "巳": "亥", "酉": "亥", "丑": "亥",
        "亥": "巳", "卯": "巳", "未": "巳",
    }

    # 文昌
    WEN_CHANG: Dict[str, str] = {
        "甲": "巳", "乙": "午",
        "丙": "申", "丁": "酉",
        "戊": "申", "己": "酉",
        "庚": "亥", "辛": "子",
        "壬": "寅", "癸": "卯",
    }

    # 羊刃
    YANG_REN: Dict[str, str] = {
        "甲": "卯", "乙": "辰",
        "丙": "午", "丁": "未",
        "戊": "午", "己": "未",
        "庚": "酉", "辛": "戌",
        "壬": "子", "癸": "丑",
    }

    def get_tian_yi_gui_ren(self, day_stem: str) -> List[str]:
        """获取天乙贵人"""
        return self.TIAN_YI_GUI_REN.get(day_stem, [])

    def get_tao_hua(self, branch: str) -> Optional[str]:
        """获取桃花"""
        return self.TAO_HUA.get(branch)

    def get_yi_ma(self, branch: str) -> Optional[str]:
        """获取驿马"""
        return self.YI_MA.get(branch)

    def get_wen_chang(self, day_stem: str) -> Optional[str]:
        """获取文昌"""
        return self.WEN_CHANG.get(day_stem)

    def get_yang_ren(self, day_stem: str) -> Optional[str]:
        """获取羊刃"""
        return self.YANG_REN.get(day_stem)

    def get_all_shen_sha(self, day_stem: str, year_branch: str, day_branch: str) -> Dict[str, Any]:
        """
        获取所有神煞
        
        Args:
            day_stem: 日干
            year_branch: 年支
            day_branch: 日支
            
        Returns:
            神煞字典
        """
        return {
            "天乙贵人": self.get_tian_yi_gui_ren(day_stem),
            "桃花": [self.get_tao_hua(year_branch), self.get_tao_hua(day_branch)],
            "驿马": [self.get_yi_ma(year_branch), self.get_yi_ma(day_branch)],
            "文昌": self.get_wen_chang(day_stem),
            "羊刃": self.get_yang_ren(day_stem),
        }
