"""
数据解析模块：读取 D{0-1} 背包问题实例文件。

文件格式：
    每个实例以 "NAME:" 开头，包含维度行、利润数组和重量数组。
    维度行格式：The dimension is d=3*N, the cubage of knapsack is CAPACITY.
    数据可能跨多行，以逗号分隔，可能有尾随逗号。
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class DKPGroup:
    """D{0-1}KP 中的一组（3 件物品）。"""
    profits: List[int] = field(default_factory=list)  # 长度为 3
    weights: List[int] = field(default_factory=list)  # 长度为 3


@dataclass
class DKPInstance:
    """单个 D{0-1}KP 实例。"""
    name: str
    num_groups: int      # N（组数）
    capacity: int        # 背包容量
    profits: List[int]   # 3*N 个利润值
    weights: List[int]   # 3*N 个重量值
    groups: List[DKPGroup] = field(default_factory=list)

    def __post_init__(self):
        # 按组整理物品
        self.groups = []
        for i in range(self.num_groups):
            g = DKPGroup(
                profits=self.profits[i * 3: i * 3 + 3],
                weights=self.weights[i * 3: i * 3 + 3],
            )
            self.groups.append(g)


def _parse_int_list(raw: str) -> List[int]:
    """从逗号分隔的字符串中解析整数列表（忽略空白和尾随逗号）。"""
    # 数据文件里可能出现如 "523." 的写法，统一用正则提取整数可更稳健。
    return [int(x) for x in re.findall(r"-?\d+", raw)]


def parse_file(file_path: str) -> List[DKPInstance]:
    """
    解析 D{0-1}KP 实例文件，返回实例列表。

    Args:
        file_path: 数据文件的绝对路径。

    Returns:
        DKPInstance 对象列表。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    instances: List[DKPInstance] = []

    # 用实例名称将文件切分（如 UDKP1:、WDKP5: 等）
    # 捕获 "NAME:" 以及其后续内容直到下一个 "NAME:" 或文件末尾
    pattern = re.compile(
        r"([A-Z]+\d+)\s*:\s*\n(.*?)(?=\n[A-Z]+\d+\s*:|$)",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        name = match.group(1).strip()
        body = match.group(2)

        # 解析维度行
        dim_match = re.search(
            r"d\s*=\s*3\s*\*\s*(\d+).*?cubage of knapsack is\s+(\d+)",
            body,
            re.IGNORECASE,
        )
        if not dim_match:
            continue
        n_groups = int(dim_match.group(1))
        capacity = int(dim_match.group(2))

        # 解析利润数组（"profit" 行之后到下一个空行或 "weight" 关键字之前）
        profit_match = re.search(
            r"profit.*?are\s*:\s*\n(.*?)(?=\n\s*\n|\bweight\b|\bThe weight\b)",
            body,
            re.DOTALL | re.IGNORECASE,
        )
        if not profit_match:
            continue
        profits = _parse_int_list(profit_match.group(1))

        # 解析重量数组
        weight_match = re.search(
            r"weight.*?are\s*:\s*\n(.*?)(?=\n\s*\n|$)",
            body,
            re.DOTALL | re.IGNORECASE,
        )
        if not weight_match:
            continue
        weights = _parse_int_list(weight_match.group(1))

        if len(profits) != 3 * n_groups or len(weights) != 3 * n_groups:
            # 数据不完整，跳过
            continue

        inst = DKPInstance(
            name=name,
            num_groups=n_groups,
            capacity=capacity,
            profits=profits,
            weights=weights,
        )
        instances.append(inst)

    return instances
