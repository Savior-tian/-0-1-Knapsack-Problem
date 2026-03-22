"""
动态规划求解模块：求解 D{0-1} 背包问题。

D{0-1}KP 规则：
    - 物品共 N 组，每组 3 件：(p1,w1)、(p2,w2)、(p3,w3)。
    - 每组至多选 1 件，也可不选。
    - 目标：在总重量不超过容量 C 的前提下，最大化总价值。

算法：
    标准 0/1 背包 DP 扩展为每组 4 个选项（不选、选第1件、选第2件、选第3件）。
    使用滚动数组（一维 DP），降序遍历容量以保证"每组至多选1件"。
"""

import time
from dataclasses import dataclass, field
from typing import List, Tuple

from src.data_parser import DKPInstance


@dataclass
class SolveResult:
    """动态规划求解结果。"""

    instance_name: str
    optimal_value: int  # 最优目标函数值
    selected_groups: List[int] = field(default_factory=list)
    # selected_groups[i] = 0/1/2/3 表示第 i 组不选/选第1/2/3件
    selected_items: List[Tuple[int, int, int, int]] = field(default_factory=list)
    # (group_idx, item_in_group, profit, weight)
    solve_time_ms: float = 0.0  # 求解耗时（毫秒）


def solve(instance: DKPInstance) -> SolveResult:
    """
    使用动态规划求解 D{0-1}KP 实例。

    Args:
        instance: 待求解的 DKPInstance 对象。

    Returns:
        SolveResult 包含最优值、所选物品和求解时间。
    """
    n = instance.num_groups
    c = instance.capacity
    groups = instance.groups

    # dp[j] 表示容量为 j 时的最大利润
    dp = [0] * (c + 1)
    # 回溯信息：choice[i][j] = 第 i 组结束后容量为 j 时的选择（0/1/2/3）
    choice = [[0] * (c + 1) for _ in range(n)]

    start = time.perf_counter()

    for i, grp in enumerate(groups):
        p = grp.profits  # [p1, p2, p3]
        w = grp.weights  # [w1, w2, w3]

        # 每组独立处理，使用临时数组防止同组内互相影响
        new_dp = dp[:]
        ch = [0] * (c + 1)  # 当前组的选择记录

        for j in range(c + 1):
            best_val = dp[j]  # 不选（选项 0）
            best_k = 0

            for k in range(3):  # 枚举三件物品
                if w[k] <= j:
                    val = dp[j - w[k]] + p[k]
                    if val > best_val:
                        best_val = val
                        best_k = k + 1  # 1/2/3

            new_dp[j] = best_val
            ch[j] = best_k

        dp = new_dp
        choice[i] = ch

    end = time.perf_counter()

    optimal_value = dp[c]
    solve_time_ms = (end - start) * 1000.0

    # 回溯还原选择方案
    selected_groups = [0] * n
    selected_items = []
    remain = c
    for i in range(n - 1, -1, -1):
        k = choice[i][remain]
        selected_groups[i] = k
        if k > 0:
            item_idx = k - 1  # 0-based
            selected_items.append(
                (
                    i,
                    item_idx,
                    groups[i].profits[item_idx],
                    groups[i].weights[item_idx],
                )
            )
            remain -= groups[i].weights[item_idx]
        # k == 0 表示该组不选，remain 不变

    selected_items.sort(key=lambda x: x[0])

    return SolveResult(
        instance_name=instance.name,
        optimal_value=optimal_value,
        selected_groups=selected_groups,
        selected_items=selected_items,
        solve_time_ms=solve_time_ms,
    )
