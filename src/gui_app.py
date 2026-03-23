"""GUI 主窗口模块。

当前已完成：
1) 主窗口布局
2) 控制面板 + 按钮交互骨架
3) 散点图/排序图嵌入
4) 求解结果展示

说明：绘图、排序、求解、导出的完整业务接入在后续子任务完成。
"""

from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.data_parser import DKPInstance, parse_file
from src.dp_solver import SolveResult, solve
from src.exporter import export_batch_summary_csv, export_excel, export_txt
from src.sorter import sort_groups_by_ratio
from src.visualizer import create_scatter_figure, create_sorted_scatter_figure


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
        self.last_sorted_order: List[int] = []
        self.last_solve_result: Optional[SolveResult] = None

        self.notebook: Optional[ttk.Notebook] = None
        self.tab_chart: Optional[ttk.Frame] = None
        self.tab_sorted: Optional[ttk.Frame] = None
        self.tab_result: Optional[ttk.Frame] = None
        self.chart_host: Optional[ttk.Frame] = None
        self.sorted_host: Optional[ttk.Frame] = None
        self.result_text: Optional[tk.Text] = None

        self.chart_canvas: Optional[FigureCanvasTkAgg] = None
        self.sorted_canvas: Optional[FigureCanvasTkAgg] = None

        self._build_style()
        self._build_layout()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 10))
        style.configure(
            "Section.TLabelframe.Label", font=("Microsoft YaHei UI", 10, "bold")
        )
        style.configure(
            "Hint.TLabel", foreground="#666666", font=("Microsoft YaHei UI", 9)
        )

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
            text=(
                "当前阶段：主窗口布局 + 控制面板按钮 + 图表嵌入 + 求解结果展示已接入。"
            ),
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

        self._build_file_selector(left_panel)
        self._build_instance_selector(left_panel)
        self._build_action_buttons(left_panel)

        ttk.Label(
            left_panel,
            text="说明：导出支持 TXT 与 XLSX。",
            style="Hint.TLabel",
        ).grid(row=15, column=0, sticky="sw", pady=(12, 0))

    def _build_file_selector(self, left_panel: ttk.LabelFrame) -> None:

        ttk.Label(left_panel, text="数据文件", style="Hint.TLabel").grid(
            row=0, column=0, sticky="w"
        )
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

    def _build_instance_selector(self, left_panel: ttk.LabelFrame) -> None:

        ttk.Label(left_panel, text="实例选择", style="Hint.TLabel").grid(
            row=3, column=0, sticky="w", pady=(12, 0)
        )
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

        ttk.Separator(left_panel, orient="horizontal").grid(
            row=6, column=0, sticky="ew", pady=10
        )

    def _build_action_buttons(self, left_panel: ttk.LabelFrame) -> None:

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

        self.btn_batch_export = ttk.Button(
            left_panel,
            text="批量求解并导出汇总",
            command=self._on_batch_export,
            state="disabled",
        )
        self.btn_batch_export.grid(row=11, column=0, sticky="ew", pady=(4, 0))

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        right_panel = ttk.LabelFrame(
            parent,
            text="可视化与结果展示区",
            style="Section.TLabelframe",
            padding=8,
        )
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.tab_chart = ttk.Frame(self.notebook, padding=8)
        self.tab_sorted = ttk.Frame(self.notebook, padding=8)
        self.tab_result = ttk.Frame(self.notebook, padding=8)

        self.notebook.add(self.tab_chart, text="散点图")
        self.notebook.add(self.tab_sorted, text="排序图")
        self.notebook.add(self.tab_result, text="求解结果")

        self.chart_host = self._build_chart_tab(self.tab_chart, "散点图嵌入区域")
        self.sorted_host = self._build_chart_tab(self.tab_sorted, "排序图嵌入区域")
        self._build_result_tab(self.tab_result)

    def _build_chart_tab(self, tab: ttk.Frame, title: str) -> ttk.Frame:
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        ttk.Label(tab, text=title, style="Subtitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        host = ttk.Frame(tab)
        host.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        host.columnconfigure(0, weight=1)
        host.rowconfigure(0, weight=1)

        placeholder = ttk.Label(
            host,
            text="等待渲染图表...",
            style="Hint.TLabel",
            anchor="center",
            justify="center",
        )
        placeholder.grid(row=0, column=0, sticky="nsew")

        return host

    def _build_result_tab(self, tab: ttk.Frame) -> None:
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        ttk.Label(tab, text="文本结果区域", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        self.result_text = tk.Text(tab, height=10, wrap="word")
        self.result_text.insert(
            "1.0",
            "当前可通过左侧按钮渲染散点图与排序图。\n"
            "后续子任务将接入 DP 求解详情与导出结果。",
        )
        self.result_text.configure(state="disabled")
        self.result_text.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

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
        self._clear_visualizations()

    def _clear_visualizations(self) -> None:
        if self.chart_canvas is not None:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
        if self.sorted_canvas is not None:
            self.sorted_canvas.get_tk_widget().destroy()
            self.sorted_canvas = None

        self.last_sorted_order = []
        self.last_solve_result = None
        self._set_result_text(
            "当前可通过左侧按钮渲染散点图与排序图。\n"
            "可点击“运行 DP 求解”查看最优值与选中物品明细。"
        )

    def _set_result_text(self, text: str) -> None:
        if self.result_text is None:
            return
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")

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
        self.btn_batch_export.configure(state=state)

    def _require_instance(self) -> bool:
        if self.selected_instance is None:
            messagebox.showwarning("提示", "请先加载并选择实例。")
            self._set_status("请先加载实例")
            return False
        return True

    def _on_show_scatter(self) -> None:
        if not self._require_instance():
            return

        fig = create_scatter_figure(self.selected_instance)
        self._render_figure(fig, target="chart")
        self._set_status(f"已绘制 {self.selected_instance.name} 的散点图")
        self._set_result_text(
            f"实例：{self.selected_instance.name}\n"
            f"组数：{self.selected_instance.num_groups}\n"
            f"容量：{self.selected_instance.capacity}\n"
            "已渲染散点图（重量-价值）。"
        )

        if self.notebook and self.tab_chart:
            self.notebook.select(self.tab_chart)

    def _on_sort(self) -> None:
        if not self._require_instance():
            return

        self.last_sorted_order = sort_groups_by_ratio(self.selected_instance)
        fig = create_sorted_scatter_figure(
            self.selected_instance, self.last_sorted_order
        )
        self._render_figure(fig, target="sorted")

        top_k = min(5, len(self.last_sorted_order))
        top_groups = [str(idx + 1) for idx in self.last_sorted_order[:top_k]]
        self._set_result_text(
            f"实例：{self.selected_instance.name}\n"
            "已按第3件物品价值/重量比完成非升序排序。\n"
            f"前 {top_k} 个组（原始编号）：" + ", ".join(top_groups)
        )
        self._set_status(f"已完成 {self.selected_instance.name} 的排序并绘制排序图")

        if self.notebook and self.tab_sorted:
            self.notebook.select(self.tab_sorted)

    def _render_figure(self, fig, target: str) -> None:
        if target == "chart":
            host = self.chart_host
            old_canvas = self.chart_canvas
        else:
            host = self.sorted_host
            old_canvas = self.sorted_canvas

        if host is None:
            return

        for child in host.winfo_children():
            child.destroy()

        if old_canvas is not None:
            old_canvas.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=host)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        if target == "chart":
            self.chart_canvas = canvas
        else:
            self.sorted_canvas = canvas

    def _on_solve(self) -> None:
        if not self._require_instance():
            return

        self.last_solve_result = solve(self.selected_instance)
        report = self._format_solve_report(
            self.selected_instance, self.last_solve_result
        )
        self._set_result_text(report)

        self._set_status(
            "求解完成："
            f"{self.selected_instance.name} "
            f"最优值 = {self.last_solve_result.optimal_value}"
        )

        if self.notebook and self.tab_result:
            self.notebook.select(self.tab_result)

    def _format_solve_report(self, instance: DKPInstance, result: SolveResult) -> str:
        lines = [
            f"实例：{result.instance_name}",
            f"组数：{instance.num_groups}",
            f"容量：{instance.capacity}",
            f"最优总价值：{result.optimal_value}",
            f"求解耗时：{result.solve_time_ms:.4f} ms",
            "",
            f"选中物品数：{len(result.selected_items)}",
            "组编号  组内编号  价值  重量",
        ]

        total_weight = 0
        for group_idx, item_in_group, profit, weight in result.selected_items:
            lines.append(
                f"{group_idx + 1:>4}    "
                f"{item_in_group + 1:>4}    "
                f"{profit:>4}  {weight:>4}"
            )
            total_weight += weight

        lines.extend(
            [
                "",
                f"总重量：{total_weight}",
                "说明：组编号与组内编号均从 1 开始计数。",
            ]
        )

        return "\n".join(lines)

    def _on_export(self) -> None:
        if not self._require_instance():
            return

        default_name = f"{self.selected_instance.name}_result.txt"
        out_path = filedialog.asksaveasfilename(
            title="导出求解结果",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[
                ("Text Files", "*.txt"),
                ("Excel Files", "*.xlsx"),
                ("All Files", "*.*"),
            ],
        )
        if not out_path:
            return

        self._export_to_path(out_path)

    def _export_to_path(self, out_path: str) -> bool:
        if not self._require_instance():
            return False

        # 若当前实例尚未求解，则先自动求解，保证导出内容完整。
        if (
            self.last_solve_result is None
            or self.last_solve_result.instance_name != self.selected_instance.name
        ):
            self.last_solve_result = solve(self.selected_instance)

        if not self.last_sorted_order:
            self.last_sorted_order = sort_groups_by_ratio(self.selected_instance)

        ext = os.path.splitext(out_path)[1].lower()
        try:
            if ext == ".xlsx":
                export_excel(
                    self.selected_instance,
                    self.last_solve_result,
                    self.last_sorted_order,
                    out_path,
                )
            else:
                export_txt(self.selected_instance, self.last_solve_result, out_path)
        except ImportError as exc:
            messagebox.showerror("导出失败", str(exc))
            self._set_status("导出失败：缺少依赖库")
            return False
        except Exception as exc:
            messagebox.showerror("导出失败", f"写入文件失败：{exc}")
            self._set_status("导出失败：写入异常")
            return False

        self._set_status(f"导出成功：{out_path}")
        messagebox.showinfo("导出成功", f"文件已保存到：\n{out_path}")
        return True

    def _on_batch_export(self) -> None:
        if not self.instances:
            messagebox.showwarning("提示", "请先加载实例。")
            self._set_status("请先加载实例")
            return

        default_name = "batch_summary.csv"
        out_path = filedialog.asksaveasfilename(
            title="导出批量求解汇总",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*"),
            ],
        )
        if not out_path:
            return

        total = len(self.instances)
        cancel_event = threading.Event()
        progress_queue: queue.Queue[tuple[str, object]] = queue.Queue()

        progress_win = tk.Toplevel(self)
        progress_win.title("批量导出进度")
        progress_win.transient(self)
        progress_win.resizable(False, False)
        progress_win.grab_set()
        progress_win.protocol("WM_DELETE_WINDOW", cancel_event.set)

        ttk.Label(
            progress_win,
            text="正在批量求解并导出，请稍候...",
            style="Subtitle.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 6))

        progress_var = tk.StringVar(value=f"0/{total}")
        ttk.Label(progress_win, textvariable=progress_var).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            padx=14,
            pady=(0, 6),
        )

        progress_bar = ttk.Progressbar(
            progress_win,
            orient="horizontal",
            mode="determinate",
            length=360,
            maximum=total,
            value=0,
        )
        progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14)

        def on_cancel() -> None:
            cancel_event.set()
            self._set_status("批量导出取消中，请稍候...")

        ttk.Button(progress_win, text="取消", command=on_cancel).grid(
            row=3,
            column=1,
            sticky="e",
            padx=14,
            pady=(10, 12),
        )

        progress_win.columnconfigure(0, weight=1)

        self._toggle_action_buttons(enabled=False)
        self.update_idletasks()

        def worker() -> None:
            def report_progress(
                done: int, total_count: int, instance: DKPInstance
            ) -> None:
                progress_queue.put(("progress", done, total_count, instance.name))

            try:
                export_batch_summary_csv(
                    self.instances,
                    out_path,
                    progress_callback=report_progress,
                    should_cancel=cancel_event.is_set,
                )
            except InterruptedError:
                progress_queue.put(("cancelled", out_path))
            except Exception as exc:
                progress_queue.put(("error", str(exc)))
            else:
                progress_queue.put(("done", out_path))

        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()

        def finish_dialog() -> None:
            if progress_win.winfo_exists():
                progress_win.grab_release()
                progress_win.destroy()
            self._toggle_action_buttons(enabled=True)

        def poll_progress() -> None:
            try:
                while True:
                    event = progress_queue.get_nowait()
                    kind = event[0]

                    if kind == "progress":
                        done = int(event[1])
                        total_count = int(event[2])
                        instance_name = str(event[3])
                        self._set_status(
                            f"批量求解导出中：{done}/{total_count} - {instance_name}"
                        )
                        progress_var.set(f"{done}/{total_count} - {instance_name}")
                        progress_bar.configure(value=done)
                    elif kind == "cancelled":
                        finish_dialog()
                        self._set_status(f"批量导出已取消：{event[1]}")
                        messagebox.showinfo(
                            "已取消",
                            "批量导出已取消。\n已写入的数据会保留在当前文件中。",
                        )
                        return
                    elif kind == "error":
                        finish_dialog()
                        messagebox.showerror("导出失败", f"批量导出失败：{event[1]}")
                        self._set_status("批量导出失败")
                        return
                    elif kind == "done":
                        finish_dialog()
                        self._set_status(f"批量汇总导出成功：{event[1]}")
                        messagebox.showinfo(
                            "导出成功",
                            f"批量汇总文件已保存到：\n{event[1]}",
                        )
                        return
            except queue.Empty:
                pass

            self.after(100, poll_progress)

        self.after(100, poll_progress)


def run_app() -> None:
    """启动 GUI。"""
    app = DKPApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
