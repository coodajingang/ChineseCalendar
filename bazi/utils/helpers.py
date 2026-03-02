"""
八字命理工具函数
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import json


def get_stem_branch_index(ganzhi: str) -> Tuple[int, int]:
    """
    获取干支索引
    
    Args:
        ganzhi: 干支字符串
        
    Returns:
        (天干索引, 地支索引)
    """
    stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    if len(ganzhi) != 2:
        return (-1, -1)
    
    stem_idx = stems.index(ganzhi[0]) if ganzhi[0] in stems else -1
    branch_idx = branches.index(ganzhi[1]) if ganzhi[1] in branches else -1
    
    return (stem_idx, branch_idx)


def calc_ganzhi_from_index(stem_idx: int, branch_idx: int) -> str:
    """
    根据索引计算干支
    
    Args:
        stem_idx: 天干索引
        branch_idx: 地支索引
        
    Returns:
        干支字符串
    """
    stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    stem_idx = stem_idx % 10
    branch_idx = branch_idx % 12
    
    return stems[stem_idx] + branches[branch_idx]


def get_element_relation(element1: str, element2: str) -> str:
    """
    获取五行关系
    
    Args:
        element1: 第一个五行
        element2: 第二个五行
        
    Returns:
        关系: "self"(同), "generate"(生), "overcome"(克), "generated"(被生), "overcome_by"(被克)
    """
    # 五行相生: 木生火, 火生土, 土生金, 金生水, 水生木
    generate_map = {
        "wood": "fire",
        "fire": "earth",
        "earth": "metal",
        "metal": "water",
        "water": "wood"
    }
    
    # 五行相克: 木克土, 土克水, 水克火, 火克金, 金克木
    overcome_map = {
        "wood": "earth",
        "earth": "water",
        "water": "fire",
        "fire": "metal",
        "metal": "wood"
    }
    
    if element1 == element2:
        return "self"
    
    if generate_map.get(element1) == element2:
        return "generate"
    
    if generate_map.get(element2) == element1:
        return "generated"
    
    if overcome_map.get(element1) == element2:
        return "overcome"
    
    if overcome_map.get(element2) == element1:
        return "overcome_by"
    
    return "unknown"


def get_element_name(element_en: str) -> str:
    """获取五行中文名"""
    element_names = {
        "wood": "木",
        "fire": "火",
        "earth": "土",
        "metal": "金",
        "water": "水"
    }
    return element_names.get(element_en, element_en)


def get_yinyang_name(yinyang_en: str) -> str:
    """获取阴阳中文名"""
    yinyang_names = {
        "yin": "阴",
        "yang": "阳"
    }
    return yinyang_names.get(yinyang_en, yinyang_en)


def get_ten_god_name(ten_god_en: str) -> str:
    """获取十神中文名"""
    ten_god_names = {
        "bi_jian": "比肩",
        "jie_cai": "劫财",
        "shi_shen": "食神",
        "shang_guan": "伤官",
        "zheng_cai": "正财",
        "pian_cai": "偏财",
        "zheng_guan": "正官",
        "qi_sha": "七杀",
        "zheng_yin": "正印",
        "pian_yin": "偏印"
    }
    return ten_god_names.get(ten_god_en, ten_god_en)


def get_growth_phase_name(phase_en: str) -> str:
    """获取十二长生中文名"""
    phase_names = {
        "chang_sheng": "长生",
        "mu_yu": "沐浴",
        "guan_dai": "冠带",
        "lin_guan": "临官",
        "di_wang": "帝旺",
        "shuai": "衰",
        "bing": "病",
        "si": "死",
        "mu": "墓",
        "jue": "绝",
        "tai": "胎",
        "yang": "养"
    }
    return phase_names.get(phase_en, phase_en)


def solar_term_index_to_name(index: int) -> str:
    """节气索引转名称"""
    terms = [
        "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
        "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
        "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
        "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
    ]
    return terms[index] if 0 <= index < 24 else "未知"


def hour_to_branch(hour: int) -> Tuple[str, int]:
    """
    小时转时辰
    
    Args:
        hour: 小时 (0-23)
        
    Returns:
        (时辰名, 时辰索引)
    """
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    # 子时: 23:00-01:00
    if hour == 23 or hour == 0:
        return "子", 0
    # 丑时: 01:00-03:00
    elif 1 <= hour < 3:
        return "丑", 1
    # 寅时: 03:00-05:00
    elif 3 <= hour < 5:
        return "寅", 2
    # 卯时: 05:00-07:00
    elif 5 <= hour < 7:
        return "卯", 3
    # 辰时: 07:00-09:00
    elif 7 <= hour < 9:
        return "辰", 4
    # 巳时: 09:00-11:00
    elif 9 <= hour < 11:
        return "巳", 5
    # 午时: 11:00-13:00
    elif 11 <= hour < 13:
        return "午", 6
    # 未时: 13:00-15:00
    elif 13 <= hour < 15:
        return "未", 7
    # 申时: 15:00-17:00
    elif 15 <= hour < 17:
        return "申", 8
    # 酉时: 17:00-19:00
    elif 17 <= hour < 19:
        return "酉", 9
    # 戌时: 19:00-21:00
    elif 19 <= hour < 21:
        return "戌", 10
    # 亥时: 21:00-23:00
    else:
        return "亥", 11


def format_datetime(dt: datetime, include_timezone: bool = True) -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间
        include_timezone: 是否包含时区
        
    Returns:
        格式化字符串
    """
    if include_timezone and dt.tzinfo:
        return dt.isoformat()
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def to_json(obj: Any, ensure_ascii: bool = False, indent: int = 2) -> str:
    """
    转换为JSON字符串
    
    Args:
        obj: 对象
        ensure_ascii: 是否确保ASCII
        indent: 缩进
        
    Returns:
        JSON字符串
    """
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    return json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent, default=str)
