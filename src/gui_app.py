"""GUI 主窗口模块。

当前已完成：
1) 主窗口布局
2) 控制面板 + 按钮交互骨架

说明：绘图、排序、求解、导出的完整业务接入在后续子任务完成。
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from src.data_parser import DKPInstance, parse_file


class DKPApp(tk.Tk):
    """D{0-1}KP 图形界面主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.title("D{0-1} 背包问题求解系统")
        self.geometry("1200x760")
        self.minsize(980, 620)

        self.file_var = tk.StringVar()
        self.instance_var = tk.StringVar()
        self.status_var = tk.StringVar(value="就绪：GUI 主窗口布局与控制面板已完成")

        self.current_file: str = ""
        self.instances: List[DKPInstance] = []
        self.selected_instance: Optional[DKPInstance] = None

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
            text="当前阶段：主窗口布局 + 控制面板按钮已接入。",
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
            text="控制面板",
            style="Section.TLabelframe",
            padding=12,
            width=320,
        )
        left_panel.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        left_panel.grid_propagate(False)

        for i in range(16):
            left_panel.rowconfigure(i, weight=0)
        left_panel.columnconfigure(0, weight=1)

        ttk.Label(left_panel, text="数据文件", style="Hint.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(left_panel, textvariable=self.file_var, state="readonly").grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(4, 6),
        )
        ttk.Button(left_panel, text="选择文件...", command=self._on_choose_file).grid(
            row=2,
            column=0,
            sticky="ew",
        )

        ttk.Label(left_panel, text="实例选择", style="Hint.TLabel").grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.instance_combo = ttk.Combobox(
            left_panel,
            textvariable=self.instance_var,
            state="readonly",
            values=[],
        )
        self.instance_combo.grid(row=4, column=0, sticky="ew", pady=(4, 6))
        self.instance_combo.bind("<<ComboboxSelected>>", self._on_instance_selected)

        ttk.Button(left_panel, text="加载实例", command=self._on_load_instances).grid(
            row=5,
            column=0,
            sticky="ew",
        )

        ttk.Separator(left_panel, orient="horizontal").grid(row=6, column=0, sticky="ew", pady=10)

        self.btn_show_scatter = ttk.Button(
            left_panel,
            text="绘制散点图",
            command=self._on_show_scatter,
            state="disabled",
        )
        self.btn_show_scatter.grid(row=7, column=0, sticky="ew")

        self.btn_sort = ttk.Button(
            left_panel,
            text="执行排序",
            command=self._on_sort,
            state="disabled",
        )
        self.btn_sort.grid(row=8, column=0, sticky="ew", pady=(4, 0))

        self.btn_solve = ttk.Button(
            left_panel,
            text="运行 DP 求解",
            command=self._on_solve,
            state="disabled",
        )
        self.btn_solve.grid(row=9, column=0, sticky="ew", pady=(4, 0))

        self.btn_export = ttk.Button(
            left_panel,
            text="导出结果",
            command=self._on_export,
            state="disabled",
        )
        self.btn_export.grid(row=10, column=0, sticky="ew", pady=(4, 0))

        ttk.Label(
            left_panel,
            text="说明：完整绘图/求解/导出将在后续子任务接入。",
            style="Hint.TLabel",
        ).grid(row=15, column=0, sticky="sw", pady=(12, 0))

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

        ttk.Label(status, textvariable=self.status_var, style="Hint.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
        )

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _on_choose_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="选择 D{0-1}KP 数据文件",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return
        self.current_file = file_path
        self.file_var.set(file_path)
        self._set_status(f"已选择数据文件：{file_path}")

    def _on_load_instances(self) -> None:
        if not self.current_file:
            messagebox.showwarning("提示", "请先选择数据文件。")
            return

        try:
            self.instances = parse_file(self.current_file)
        except Exception as exc:
            messagebox.showerror("加载失败", f"解析文件失败：{exc}")
            self._set_status("解析失败：请检查数据文件格式")
            return

        if not self.instances:
            messagebox.showwarning("提示", "未解析到实例，请检查文件内容。")
            self._set_status("未解析到实例")
            return

        names = [inst.name for inst in self.instances]
        self.instance_combo["values"] = names
        self.instance_combo.current(0)
        self._sync_selected_instance()

        self._set_status(f"已加载 {len(self.instances)} 个实例")
        self._toggle_action_buttons(enabled=True)

    def _sync_selected_instance(self) -> None:
        if not self.instances:
            self.selected_instance = None
            return

        idx = self.instance_combo.current()
        if idx < 0:
            idx = 0
        self.selected_instance = self.instances[idx]

    def _on_instance_selected(self, _event: tk.Event) -> None:
        self._sync_selected_instance()
        if self.selected_instance:
            self._set_status(f"当前实例：{self.selected_instance.name}")

    def _toggle_action_buttons(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.btn_show_scatter.configure(state=state)
        self.btn_sort.configure(state=state)
        self.btn_solve.configure(state=state)
        self.btn_export.configure(state=state)

    def _require_instance(self) -> bool:
        if self.selected_instance is None:
            messagebox.showwarning("提示", "请先加载并选择实例。")
            self._set_status("请先加载实例")
            return False
        return True

    def _on_show_scatter(self) -> None:
        if not self._require_instance():
            return
        self._set_status(f"待实现：绘制 {self.selected_instance.name} 的散点图")

    def _on_sort(self) -> None:
        if not self._require_instance():
            return
        self._set_status(f"待实现：对 {self.selected_instance.name} 执行排序")

    def _on_solve(self) -> None:
        if not self._require_instance():
            return
        self._set_status(f"待实现：对 {self.selected_instance.name} 运行 DP 求解")

    def _on_export(self) -> None:
        if not self._require_instance():
            return
        self._set_status(f"待实现：导出 {self.selected_instance.name} 的结果")


def run_app() -> None:
    """启动 GUI。"""
    app = DKPApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
