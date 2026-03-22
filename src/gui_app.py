"""GUI 主窗口布局模块。

本模块仅实现界面骨架（第一个 GUI 子任务）：
1) 顶部标题区
2) 左侧控制区（预留按钮位置）
3) 右侧图表/结果区（预留图嵌入位置）
4) 底部状态栏
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class DKPApp(tk.Tk):
    """D{0-1}KP 图形界面主窗口（布局骨架）。"""

    def __init__(self) -> None:
        super().__init__()
        self.title("D{0-1} 背包问题求解系统")
        self.geometry("1200x760")
        self.minsize(980, 620)

        self._build_style()
        self._build_layout()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("Hint.TLabel", foreground="#666666", font=("Microsoft YaHei UI", 9))

    def _build_layout(self) -> None:
        # 根网格：标题 / 主区 / 状态栏
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_header()
        self._build_main_area()
        self._build_status_bar()

    def _build_header(self) -> None:
        header = ttk.Frame(self, padding=(16, 12, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="D{0-1} 背包问题动态规划求解器",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="主窗口布局已就绪：后续将接入数据加载、求解、排序、可视化与导出功能。",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _build_main_area(self) -> None:
        main = ttk.Frame(self, padding=(16, 4, 16, 8))
        main.grid(row=1, column=0, sticky="nsew")

        # 左右分栏：左侧控制面板（固定宽度）+ 右侧展示区域（自适应）
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_left_panel(main)
        self._build_right_panel(main)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        left_panel = ttk.LabelFrame(
            parent,
            text="控制面板（待接入交互）",
            style="Section.TLabelframe",
            padding=12,
            width=320,
        )
        left_panel.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        left_panel.grid_propagate(False)

        # 预留：后续子任务“控制面板+按钮”将把控件放在此列
        for i in range(12):
            left_panel.rowconfigure(i, weight=0)
        left_panel.columnconfigure(0, weight=1)

        ttk.Label(left_panel, text="数据文件", style="Hint.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(left_panel, state="readonly").grid(row=1, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(left_panel, text="实例选择", style="Hint.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Combobox(left_panel, state="readonly", values=[]).grid(row=3, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(left_panel, text="操作按钮区域（占位）", style="Hint.TLabel").grid(row=4, column=0, sticky="w")
        for r in range(5, 10):
            ttk.Button(left_panel, text="占位按钮", state="disabled").grid(
                row=r,
                column=0,
                sticky="ew",
                pady=(4, 0),
            )

        ttk.Label(
            left_panel,
            text="说明：当前阶段只完成主窗口布局。",
            style="Hint.TLabel",
        ).grid(row=11, column=0, sticky="sw", pady=(12, 0))

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        right_panel = ttk.LabelFrame(
            parent,
            text="可视化与结果展示区（待接入）",
            style="Section.TLabelframe",
            padding=8,
        )
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(right_panel)
        notebook.grid(row=0, column=0, sticky="nsew")

        tab_chart = ttk.Frame(notebook, padding=8)
        tab_sorted = ttk.Frame(notebook, padding=8)
        tab_result = ttk.Frame(notebook, padding=8)

        notebook.add(tab_chart, text="散点图")
        notebook.add(tab_sorted, text="排序图")
        notebook.add(tab_result, text="求解结果")

        self._build_placeholder_view(tab_chart, "散点图嵌入区域")
        self._build_placeholder_view(tab_sorted, "排序图嵌入区域")
        self._build_placeholder_view(tab_result, "文本结果区域")

    def _build_placeholder_view(self, tab: ttk.Frame, title: str) -> None:
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        ttk.Label(tab, text=title, style="Subtitle.TLabel").grid(row=0, column=0, sticky="w")

        placeholder = tk.Text(tab, height=10, wrap="word")
        placeholder.insert(
            "1.0",
            "当前为主窗口布局阶段，\n"
            "后续子任务将把 matplotlib 图像和求解结果内容嵌入到这里。",
        )
        placeholder.configure(state="disabled")
        placeholder.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

    def _build_status_bar(self) -> None:
        status = ttk.Frame(self, padding=(16, 6))
        status.grid(row=2, column=0, sticky="ew")
        status.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="就绪：GUI 主窗口布局已完成")
        ttk.Label(status, textvariable=self.status_var, style="Hint.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
        )


def run_app() -> None:
    """启动 GUI。"""
    app = DKPApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
