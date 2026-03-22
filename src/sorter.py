"""
排序模块：按第 3 件物品的价值/重量比对 D{0-1}KP 实例各组进行非升序排列。

说明：
    第 3 件物品索引为 groups[i].profits[2] / groups[i].weights[2]。
    返回排序后各组的原始索引列表，不修改原实例数据。
"""

from typing import List

from src.data_parser import DKPInstance


def sort_groups_by_ratio(instance: DKPInstance) -> List[int]:
    """
    按第 3 件物品的价值/重量比（非升序）对各组排序。

    Args:
        instance: DKPInstance 目标实例。

    Returns:
        排序后各组在原 instance.groups 中的索引列表（降序排列）。
    """
    def ratio(idx: int) -> float:
        grp = instance.groups[idx]
        w3 = grp.weights[2]
        p3 = grp.profits[2]
        return p3 / w3 if w3 > 0 else 0.0

    indices = list(range(instance.num_groups))
    indices.sort(key=ratio, reverse=True)
    return indices


def get_sorted_ratios(instance: DKPInstance, sorted_order: List[int]) -> List[float]:
    """
    返回按 sorted_order 排列的各组第 3 件物品价值/重量比列表。

    Args:
        instance:     原始实例。
        sorted_order: sort_groups_by_ratio() 的返回值。

    Returns:
        浮点数列表，对应排序后各组的比值。
    """
    result = []
    for idx in sorted_order:
        grp = instance.groups[idx]
        w3 = grp.weights[2]
        p3 = grp.profits[2]
        result.append(p3 / w3 if w3 > 0 else 0.0)
    return result
