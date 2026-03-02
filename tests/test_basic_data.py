"""
测试命理基础数据模块
"""
import pytest
from bazi.services.basic_data import (
    StemRepository, BranchRepository, TenGodService,
    GrowthPhaseService, RelationService, ShenShaService
)
from bazi.models.base import YinYang, FiveElement, TenGod, GrowthPhase, RelationType


class TestStemRepository:
    """测试天干数据仓库"""

    def setup_method(self):
        self.repo = StemRepository()

    def test_get_by_id(self):
        """测试根据索引获取天干"""
        stem = self.repo.get_by_id(0)
        assert stem is not None
        assert stem.name == "甲"
        assert stem.yin_yang == YinYang.YANG
        assert stem.element == FiveElement.WOOD

    def test_get_by_name(self):
        """测试根据名称获取天干"""
        stem = self.repo.get_by_name("丙")
        assert stem is not None
        assert stem.id == 2
        assert stem.yin_yang == YinYang.YANG
        assert stem.element == FiveElement.FIRE

    def test_get_index(self):
        """测试获取天干索引"""
        assert self.repo.get_index("甲") == 0
        assert self.repo.get_index("癸") == 9
        assert self.repo.get_index("不存在") == -1

    def test_get_all(self):
        """测试获取所有天干"""
        stems = self.repo.get_all()
        assert len(stems) == 10

    def test_names(self):
        """测试获取所有天干名称"""
        names = self.repo.names
        assert names == ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]


class TestBranchRepository:
    """测试地支数据仓库"""

    def setup_method(self):
        self.repo = BranchRepository()

    def test_get_by_id(self):
        """测试根据索引获取地支"""
        branch = self.repo.get_by_id(0)
        assert branch is not None
        assert branch.name == "子"
        assert branch.element == FiveElement.WATER

    def test_get_by_name(self):
        """测试根据名称获取地支"""
        branch = self.repo.get_by_name("寅")
        assert branch is not None
        assert branch.id == 2
        assert branch.element == FiveElement.WOOD

    def test_get_hidden_stems(self):
        """测试获取地支藏干"""
        hidden_stems = self.repo.get_hidden_stems("丑")
        assert len(hidden_stems) == 3
        assert hidden_stems[0].stem == "己"
        assert hidden_stems[1].stem == "癸"
        assert hidden_stems[2].stem == "辛"

    def test_get_all(self):
        """测试获取所有地支"""
        branches = self.repo.get_all()
        assert len(branches) == 12

    def test_names(self):
        """测试获取所有地支名称"""
        names = self.repo.names
        assert names == ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


class TestTenGodService:
    """测试十神服务"""

    def setup_method(self):
        self.stem_repo = StemRepository()
        self.service = TenGodService(self.stem_repo)

    def test_bi_jian(self):
        """测试比肩"""
        name, god = self.service.get_relation("甲", "甲")
        assert name == "比肩"
        assert god == TenGod.BI_JIAN

    def test_jie_cai(self):
        """测试劫财"""
        name, god = self.service.get_relation("甲", "乙")
        assert name == "劫财"
        assert god == TenGod.JIE_CAI

    def test_shi_shen(self):
        """测试食神"""
        name, god = self.service.get_relation("甲", "丙")
        assert name == "食神"
        assert god == TenGod.SHI_SHEN

    def test_shang_guan(self):
        """测试伤官"""
        name, god = self.service.get_relation("甲", "丁")
        assert name == "伤官"
        assert god == TenGod.SHANG_GUAN

    def test_zheng_cai(self):
        """测试正财"""
        name, god = self.service.get_relation("甲", "己")
        assert name == "正财"
        assert god == TenGod.ZHENG_CAI

    def test_pian_cai(self):
        """测试偏财"""
        name, god = self.service.get_relation("甲", "戊")
        assert name == "偏财"
        assert god == TenGod.PIAN_CAI

    def test_zheng_guan(self):
        """测试正官"""
        name, god = self.service.get_relation("甲", "辛")
        assert name == "正官"
        assert god == TenGod.ZHENG_GUAN

    def test_qi_sha(self):
        """测试七杀"""
        name, god = self.service.get_relation("甲", "庚")
        assert name == "七杀"
        assert god == TenGod.QI_SHA

    def test_zheng_yin(self):
        """测试正印"""
        name, god = self.service.get_relation("甲", "癸")
        assert name == "正印"
        assert god == TenGod.ZHENG_YIN

    def test_pian_yin(self):
        """测试偏印"""
        name, god = self.service.get_relation("甲", "壬")
        assert name == "偏印"
        assert god == TenGod.PIAN_YIN


class TestGrowthPhaseService:
    """测试十二长生服务"""

    def setup_method(self):
        self.stem_repo = StemRepository()
        self.service = GrowthPhaseService(self.stem_repo)

    def test_wood_chang_sheng(self):
        """测试木长生"""
        name, phase = self.service.get_phase("wood", "亥")
        assert name == "长生"
        assert phase == GrowthPhase.CHANG_SHENG

    def test_wood_di_wang(self):
        """测试木帝旺"""
        name, phase = self.service.get_phase("wood", "卯")
        assert name == "帝旺"
        assert phase == GrowthPhase.DI_WANG

    def test_fire_chang_sheng(self):
        """测试火长生"""
        name, phase = self.service.get_phase("fire", "寅")
        assert name == "长生"

    def test_by_stem(self):
        """测试通过日干获取长生"""
        name, phase = self.service.get_phase_by_stem("甲", "卯")
        assert name == "帝旺"


class TestRelationService:
    """测试地支关系服务"""

    def setup_method(self):
        self.service = RelationService()

    def test_clash(self):
        """测试冲"""
        relations = self.service.get_branch_relations("子", "午")
        assert len(relations) > 0
        assert any(r[0] == RelationType.CLASH for r in relations)

    def test_combine(self):
        """测试合"""
        relations = self.service.get_branch_relations("子", "丑")
        assert len(relations) > 0
        assert any(r[0] == RelationType.COMBINE for r in relations)

    def test_harm(self):
        """测试害"""
        relations = self.service.get_branch_relations("子", "未")
        assert len(relations) > 0
        assert any(r[0] == RelationType.HARM for r in relations)

    def test_break(self):
        """测试破"""
        relations = self.service.get_branch_relations("子", "酉")
        assert len(relations) > 0
        assert any(r[0] == RelationType.BREAK for r in relations)

    def test_punish(self):
        """测试刑"""
        result = self.service.check_punish(["子", "卯"])
        assert len(result) > 0
        assert "子卯相刑" in result[0]

    def test_three_combine(self):
        """测试三合"""
        result = self.service.check_three_combine(["申", "子", "辰"])
        assert len(result) > 0


class TestShenShaService:
    """测试神煞服务"""

    def setup_method(self):
        self.service = ShenShaService()

    def test_tian_yi_gui_ren(self):
        """测试天乙贵人"""
        result = self.service.get_tian_yi_gui_ren("甲")
        assert "丑" in result
        assert "未" in result

    def test_tao_hua(self):
        """测试桃花"""
        result = self.service.get_tao_hua("子")
        assert result == "卯"

    def test_yi_ma(self):
        """测试驿马"""
        result = self.service.get_yi_ma("寅")
        assert result == "申"

    def test_wen_chang(self):
        """测试文昌"""
        result = self.service.get_wen_chang("甲")
        assert result == "巳"

    def test_yang_ren(self):
        """测试羊刃"""
        result = self.service.get_yang_ren("甲")
        assert result == "卯"

    def test_get_all_shen_sha(self):
        """测试获取所有神煞"""
        result = self.service.get_all_shen_sha("甲", "子", "子")
        assert "天乙贵人" in result
        assert "桃花" in result
        assert "驿马" in result
