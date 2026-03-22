# D{0-1} 背包问题求解系统

本项目实现了课程要求的完整功能链路：

- 读取实验数据文件（如 `udkp1-10.txt`、`wdkp1-10.txt`）
- 散点图可视化（重量-价值）
- 按第3件物品价值/重量比排序并可视化
- 动态规划求解最优值与选中方案
- 导出结果到 TXT / XLSX / 批量汇总 CSV
- tkinter 图形界面交互

## 1. 环境准备

### Windows PowerShell

```powershell
# 进入项目根目录
Set-Location "E:\学习\课程学习\大三下\软件工程\实验\实验二 软件工程个人项目"

# （可选）创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
python -m pip install -r requirements.txt -i https://pypi.org/simple
```

## 2. 启动方式

```powershell
python run.py
```

也可直接运行：

```powershell
python -m src.gui_app
```

## 3. 在 GUI 中跑完整流程

1. 点击“选择文件...”，选择 `Four kinds of D{0-1}KP instances` 下任意 `.txt`。
2. 点击“加载实例”，并在下拉框中选择实例（如 UDKP1）。
3. 点击“绘制散点图”，查看重量-价值散点图。
4. 点击“执行排序”，查看按第3件价值/重量比排序图。
5. 点击“运行 DP 求解”，查看最优值、耗时和选中物品明细。
6. 点击“导出结果”，保存为 `.txt` 或 `.xlsx`。
7. （可选）点击"批量求解并导出汇总"，对当前文件中所有实例批量求解，汇总结果保存为 `.csv`。

## 4. 常见问题

### 1) 导出 Excel 失败

请确认已安装 `openpyxl`：

```powershell
python -m pip install openpyxl -i https://pypi.org/simple
```

### 2) 图表中文字体告警

这是 matplotlib 默认字体缺少中文字形导致的警告，不影响算法与导出功能。

## 5. 代码结构

- `src/data_parser.py`：数据解析
- `src/dp_solver.py`：动态规划求解
- `src/sorter.py`：排序逻辑
- `src/visualizer.py`：图表生成
- `src/exporter.py`：导出 TXT / XLSX / 批量汇总 CSV
- `src/gui_app.py`：GUI 应用
- `run.py`：启动入口
