"""
可视化模块：为 DKPInstance 绘制散点图并支持嵌入 tkinter 界面。

功能：
    - 绘制所有物品的（重量, 价值）散点图。
    - 第 1、2、3 件用不同颜色和标记区分。
    - 若提供排序后的实例，同步显示排序结果。
    - 返回 matplotlib Figure 供嵌入 GUI 使用。
"""

import matplotlib
matplotlib.use("Agg")  # 非交互后端，嵌入 tkinter 时切换为 TkAgg
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.figure import Figure

from src.data_parser import DKPInstance


# 三件物品的颜色和标记
_COLORS = ["#E63946", "#457B9D", "#2A9D8F"]
_MARKERS = ["o", "s", "^"]
_LABELS = ["物品1 (p1,w1)", "物品2 (p2,w2)", "物品3 (p3,w3)"]


def _configure_chinese_font() -> None:
    """配置 matplotlib 中文字体，避免图表标题/坐标轴出现乱码。"""
    candidates = [
        "Microsoft YaHei UI",
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "WenQuanYi Zen Hei",
        "Arial Unicode MS",
    ]

    installed = {f.name for f in font_manager.fontManager.ttflist}
    selected = None
    for name in candidates:
        if name in installed:
            selected = name
            break

    # 选到中文字体时优先使用；无中文字体时回退 DejaVu Sans。
    if selected:
        plt.rcParams["font.sans-serif"] = [selected, "DejaVu Sans"]
    else:
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]

    plt.rcParams["axes.unicode_minus"] = False


_configure_chinese_font()


def create_scatter_figure(instance: DKPInstance, figsize=(8, 5)) -> Figure:
    """
    生成 DKPInstance 的散点图（重量为 X 轴，价值为 Y 轴）。

    Args:
        instance: 目标实例。
        figsize:  图表尺寸。

    Returns:
        matplotlib Figure 对象。
    """
    fig, ax = plt.subplots(figsize=figsize)

    for item_in_group in range(3):  # 0, 1, 2 对应第1/2/3件
        xs = [
            grp.weights[item_in_group]
            for grp in instance.groups
        ]
        ys = [
            grp.profits[item_in_group]
            for grp in instance.groups
        ]
        ax.scatter(
            xs,
            ys,
            c=_COLORS[item_in_group],
            marker=_MARKERS[item_in_group],
            s=20,
            alpha=0.7,
            label=_LABELS[item_in_group],
        )

    ax.set_title(f"{instance.name} — 物品散点图\n(容量={instance.capacity}, 组数={instance.num_groups})")
    ax.set_xlabel("重量 (Weight)")
    ax.set_ylabel("价值 (Value / Profit)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()

    return fig


def create_sorted_scatter_figure(
    instance: DKPInstance,
    sorted_order: list,
    figsize=(8, 5),
) -> Figure:
    """
    按指定排序顺序绘制散点图，X 轴为排序后的顺序编号，Y 轴为第3件物品的价值/重量比。

    Args:
        instance:     目标实例（原始顺序）。
        sorted_order: 排序后各组的原始索引列表。
        figsize:      图表尺寸。

    Returns:
        matplotlib Figure 对象。
    """
    fig, ax = plt.subplots(figsize=figsize)

    ratios = []
    for orig_idx in sorted_order:
        grp = instance.groups[orig_idx]
        w3 = grp.weights[2]
        p3 = grp.profits[2]
        ratios.append(p3 / w3 if w3 > 0 else 0.0)

    x_vals = list(range(1, len(sorted_order) + 1))
    ax.bar(x_vals, ratios, color="#457B9D", alpha=0.7, width=1.0)
    ax.set_title(f"{instance.name} — 按第3件价值/重量比排序（非升序）")
    ax.set_xlabel("排序后组编号")
    ax.set_ylabel("第3件 价值/重量比")
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    fig.tight_layout()

    return fig
