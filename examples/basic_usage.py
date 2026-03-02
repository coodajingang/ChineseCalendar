#!/usr/bin/env python3
"""
八字命理系统使用示例

演示如何使用八字命理库进行时间转换、四柱生成和运势推演。
"""

from bazi import (
    TimeLocationConverter, PillarGenerator, FortuneEngine,
    BirthInput, Location, CalendarPref, PersonInfo,
    PillarInput, FortuneInput, DaYunConfig, FortuneScope
)
from bazi.services.basic_data import (
    StemRepository, BranchRepository, TenGodService, ShenShaService
)


def main():
    print("=" * 60)
    print("八字命理系统 - 使用示例")
    print("=" * 60)

    # 1. 创建出生信息
    print("\n1. 创建出生信息")
    print("-" * 40)
    
    birth_input = BirthInput(
        gregorian_datetime="1990-05-21T14:35:00",
        timezone="Asia/Shanghai",
        location=Location(
            city_code="CN_Shanghai",
            latitude=31.2304,
            longitude=121.4737
        ),
        calendar_pref=CalendarPref(use_true_solar_time=True)
    )
    
    print(f"出生时间: {birth_input.gregorian_datetime}")
    print(f"时区: {birth_input.timezone}")
    print(f"经度: {birth_input.location.longitude}")
    print(f"纬度: {birth_input.location.latitude}")

    # 2. 时间地点转换
    print("\n2. 时间地点转换")
    print("-" * 40)
    
    converter = TimeLocationConverter()
    time_result = converter.convert(birth_input)
    
    print(f"UTC时间: {time_result.utc_datetime}")
    print(f"本地标准时间: {time_result.local_datetime_standard}")
    print(f"真太阳时: {time_result.local_datetime_true_solar}")
    print(f"节气: {time_result.solar_term.name}")
    print(f"农历: {time_result.lunar_calendar.year}年{time_result.lunar_calendar.month}月{time_result.lunar_calendar.day}日")
    print(f"干支日期: 年{time_result.ganzhi_date.year} 月{time_result.ganzhi_date.month} 日{time_result.ganzhi_date.day}")

    # 3. 生成四柱
    print("\n3. 生成四柱")
    print("-" * 40)
    
    pillar_input = PillarInput(time_result=time_result)
    generator = PillarGenerator()
    pillars = generator.generate(pillar_input)
    
    print(f"年柱: {pillars.year_pillar.ganzhi}")
    print(f"月柱: {pillars.month_pillar.ganzhi}")
    print(f"日柱: {pillars.day_pillar.ganzhi}")
    print(f"时柱: {pillars.hour_pillar.ganzhi}")
    print(f"\n四柱: {pillars}")

    # 4. 基础数据查询
    print("\n4. 基础数据查询")
    print("-" * 40)
    
    stem_repo = StemRepository()
    branch_repo = BranchRepository()
    ten_god_service = TenGodService(stem_repo)
    shen_sha_service = ShenShaService()
    
    # 天干信息
    stem = stem_repo.get_by_name(pillars.day_pillar.stem)
    print(f"日干 '{stem.name}': {stem.yin_yang.value} {stem.element.value}")
    
    # 地支藏干
    branch = branch_repo.get_by_name(pillars.day_pillar.branch)
    print(f"日支 '{branch.name}' 藏干:", end=" ")
    for hs in branch.hidden_stems:
        print(f"{hs.stem}({hs.weight})", end=" ")
    print()
    
    # 十神关系
    relation, _ = ten_god_service.get_relation(pillars.day_pillar.stem, pillars.year_pillar.stem)
    print(f"日干见年干: {relation}")
    
    # 神煞
    tian_yi = shen_sha_service.get_tian_yi_gui_ren(pillars.day_pillar.stem)
    print(f"日干 '{pillars.day_pillar.stem}' 天乙贵人: {tian_yi}")

    # 5. 计算运势
    print("\n5. 计算运势")
    print("-" * 40)
    
    fortune_input = FortuneInput(
        pillars=pillars,
        time_result=time_result,
        person_info=PersonInfo(gender="male"),
        fortune_config=DaYunConfig(
            da_yun_year_step=10,
            direction_rule="by_gender_and_yangyin_year"
        ),
        scope=FortuneScope(start_age=0, end_age=80)
    )
    
    engine = FortuneEngine()
    fortune = engine.calc_fortune(fortune_input)
    
    print("大运序列:")
    for da_yun in fortune.da_yun[:8]:  # 显示前8步大运
        print(f"  {da_yun.index}. {da_yun.ganzhi} ({da_yun.start_age}-{da_yun.end_age}岁)")
    
    print("\n流年序列 (前10年):")
    for liu_nian in fortune.liu_nian[:10]:
        print(f"  {liu_nian.year}年 {liu_nian.ganzhi} ({liu_nian.age}岁)")

    # 6. 当前运势
    print("\n6. 当前运势 (假设30岁)")
    print("-" * 40)
    
    current = engine.get_current_fortune(fortune, 30)
    if current["da_yun"]:
        da_yun = current["da_yun"]
        print(f"当前大运: 第{da_yun['index']}步 {da_yun['ganzhi']} ({da_yun['start_age']}-{da_yun['end_age']}岁)")
    
    if current["liu_nian"]:
        liu_nian = current["liu_nian"]
        print(f"当前流年: {liu_nian['year']}年 {liu_nian['ganzhi']}")

    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
