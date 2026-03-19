
"""
analyze_employee.py
员工数据综合分析脚本

功能：
  读取 employee_data.csv，从以下五个维度对员工数据进行分析：
  1. 整体概况   —— 人数、工资/奖金的均值、极值、总额，以及极值员工信息
  2. 各部门分析 —— 每个部门的工资与奖金汇总，以及各部门薪资最高员工
  3. 各入职年份分析 —— 各年度平均工资/奖金，以及在职年限分布
  4. 薪资区间分布 —— 基本工资落在各区间的人数与占比
  5. 奖金占比分析 —— 每位员工奖金占总收入的比例排行榜

依赖：仅使用 Python 标准库（csv、collections），无需安装第三方包
"""

import csv
from collections import defaultdict


# ═══════════════════════════════════════════════════════════
# 数据读取
# ═══════════════════════════════════════════════════════════

def load_data(filename="employee_data.csv"):
    """
    从 CSV 文件中读取员工数据，返回字典列表。

    参数：
        filename (str): CSV 文件路径，默认为 'employee_data.csv'

    返回：
        list[dict]: 每个元素为一名员工的信息字典，包含：
                    姓名(str)、部门(str)、基本工资(int)、奖金(int)、入职年份(int)
    """
    employees = []
    # 使用 utf-8-sig 编码以兼容 Excel 生成的带 BOM 的 CSV 文件
    with open(filename, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)        # 将每行解析为以表头为键的字典
        for row in reader:
            employees.append({
                "姓名":     row["姓名"],
                "部门":     row["部门"],
                "基本工资": int(row["基本工资"]),   # 转为整数，便于数值计算
                "奖金":     int(row["奖金"]),
                "入职年份": int(row["入职年份"]),
            })
    return employees


# ═══════════════════════════════════════════════════════════
# 通用工具函数 & 常量
# ═══════════════════════════════════════════════════════════

# 主标题分隔线（长度 60）
SEPARATOR = "=" * 60
# 子标题分隔线（长度 60）
SUBSEP    = "-" * 60


def avg(lst):
    """
    计算列表的算术平均值。
    若列表为空则返回 0，避免 ZeroDivisionError。

    参数：
        lst (list[int|float]): 数值列表

    返回：
        float: 平均值
    """
    return sum(lst) / len(lst) if lst else 0


def fmt_money(n):
    """
    将数字格式化为带千分位分隔符的字符串，保留整数位。
    例如：17292.5 → '17,293'

    参数：
        n (int|float): 金额数值

    返回：
        str: 格式化后的字符串
    """
    return f"{n:,.0f}"


def print_title(title):
    """打印一级标题，上下各带一条主分隔线。"""
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def print_sub(title):
    """打印二级标题，上下各带一条子分隔线。"""
    print(f"\n{SUBSEP}")
    print(f"  {title}")
    print(SUBSEP)


# ═══════════════════════════════════════════════════════════
# 模块一：整体概况
# ═══════════════════════════════════════════════════════════

def analyze_overall(employees):
    """
    输出全体员工的整体薪酬概况，包括：
      - 总人数
      - 基本工资的平均值、最大值、最小值、总额
      - 奖金的平均值、最大值、最小值、总额
      - 总收入（工资+奖金）的平均值、最大值、最小值、总额
      - 工资最高/最低、奖金最高、总收入最高的员工姓名及部门

    参数：
        employees (list[dict]): 全体员工数据列表
    """
    print_title("📊 一、整体概况")

    # 提取各字段数值列表，方便后续聚合计算
    salaries = [e["基本工资"] for e in employees]
    bonuses  = [e["奖金"]     for e in employees]
    totals   = [e["基本工资"] + e["奖金"] for e in employees]  # 每人总收入

    # ── 打印汇总统计 ──
    print(f"  总人数        : {len(employees)} 人")
    print()
    print(f"  【基本工资】")
    print(f"    平均工资    : {fmt_money(avg(salaries))} 元")
    print(f"    最高工资    : {fmt_money(max(salaries))} 元")
    print(f"    最低工资    : {fmt_money(min(salaries))} 元")
    print(f"    工资总额    : {fmt_money(sum(salaries))} 元")
    print()
    print(f"  【奖金】")
    print(f"    平均奖金    : {fmt_money(avg(bonuses))} 元")
    print(f"    最高奖金    : {fmt_money(max(bonuses))} 元")
    print(f"    最低奖金    : {fmt_money(min(bonuses))} 元")
    print(f"    奖金总额    : {fmt_money(sum(bonuses))} 元")
    print()
    print(f"  【总收入（工资+奖金）】")
    print(f"    平均总收入  : {fmt_money(avg(totals))} 元")
    print(f"    最高总收入  : {fmt_money(max(totals))} 元")
    print(f"    最低总收入  : {fmt_money(min(totals))} 元")
    print(f"    总薪酬支出  : {fmt_money(sum(totals))} 元")

    # ── 找出各项极值对应的员工（用 key 函数指定排序依据）──
    max_sal_emp = max(employees, key=lambda e: e["基本工资"])          # 工资最高
    min_sal_emp = min(employees, key=lambda e: e["基本工资"])          # 工资最低
    max_bon_emp = max(employees, key=lambda e: e["奖金"])              # 奖金最高
    max_tot_emp = max(employees, key=lambda e: e["基本工资"] + e["奖金"])  # 总收入最高

    print()
    print(f"  ▶ 基本工资最高: {max_sal_emp['姓名']}（{max_sal_emp['部门']}）"
          f"  {fmt_money(max_sal_emp['基本工资'])} 元")
    print(f"  ▶ 基本工资最低: {min_sal_emp['姓名']}（{min_sal_emp['部门']}）"
          f"  {fmt_money(min_sal_emp['基本工资'])} 元")
    print(f"  ▶ 奖金最高    : {max_bon_emp['姓名']}（{max_bon_emp['部门']}）"
          f"  {fmt_money(max_bon_emp['奖金'])} 元")
    print(f"  ▶ 总收入最高  : {max_tot_emp['姓名']}（{max_tot_emp['部门']}）"
          f"  {fmt_money(max_tot_emp['基本工资'] + max_tot_emp['奖金'])} 元")


# ═══════════════════════════════════════════════════════════
# 模块二：按部门分析
# ═══════════════════════════════════════════════════════════

def analyze_by_department(employees):
    """
    按部门汇总并输出薪酬分析表，以及各部门薪资/奖金最高员工。

    统计指标（每个部门）：
      - 人数
      - 工资总额、平均工资
      - 奖金总额、平均奖金
      - 人均总收入（平均工资 + 平均奖金）

    参数：
        employees (list[dict]): 全体员工数据列表
    """
    print_title("🏢 二、各部门分析")

    # 用 defaultdict(list) 将员工按部门分组
    # 键为部门名称，值为属于该部门的员工字典列表
    dept_map = defaultdict(list)
    for e in employees:
        dept_map[e["部门"]].append(e)

    # 按各部门人数从多到少排列，方便阅读
    sorted_depts = sorted(dept_map.items(), key=lambda x: len(x[1]), reverse=True)

    # 打印表头
    header = f"  {'部门':<10} {'人数':>4}  {'总工资':>10}  {'平均工资':>10}  {'总奖金':>10}  {'平均奖金':>10}  {'人均总收入':>10}"
    print(f"\n{header}")
    print(f"  {'-'*82}")

    # 逐部门计算并打印一行数据
    for dept, emps in sorted_depts:
        salaries  = [e["基本工资"] for e in emps]
        bonuses   = [e["奖金"]     for e in emps]
        total_sal = sum(salaries)
        total_bon = sum(bonuses)
        avg_sal   = avg(salaries)
        avg_bon   = avg(bonuses)
        avg_total = avg_sal + avg_bon   # 人均总收入

        print(f"  {dept:<10} {len(emps):>4}  "
              f"{fmt_money(total_sal):>10}  "
              f"{fmt_money(avg_sal):>10}  "
              f"{fmt_money(total_bon):>10}  "
              f"{fmt_money(avg_bon):>10}  "
              f"{fmt_money(avg_total):>10}")

    # ── 各部门工资最高员工 ──
    print_sub("各部门工资最高员工")
    for dept, emps in sorted_depts:
        # 在当前部门员工中找出基本工资最大者
        top = max(emps, key=lambda e: e["基本工资"])
        print(f"  {dept:<10}  {top['姓名']}  基本工资 {fmt_money(top['基本工资'])} 元")

    # ── 各部门奖金最高员工 ──
    print_sub("各部门奖金最高员工")
    for dept, emps in sorted_depts:
        # 在当前部门员工中找出奖金最大者
        top = max(emps, key=lambda e: e["奖金"])
        print(f"  {dept:<10}  {top['姓名']}  奖金 {fmt_money(top['奖金'])} 元")


# ═══════════════════════════════════════════════════════════
# 模块三：按入职年份分析
# ═══════════════════════════════════════════════════════════

def analyze_by_year(employees):
    """
    按入职年份分组，输出各年度平均薪酬，并统计在职年限分布。

    统计指标（每个年份）：
      - 人数
      - 平均基本工资、平均奖金、人均总收入

    在职年限分布（以 2026 年为计算基准）：
      - 0-2年（新员工）
      - 3-5年
      - 6-10年
      - 10年以上（资深）

    参数：
        employees (list[dict]): 全体员工数据列表
    """
    print_title("📅 三、各入职年份分析")

    # 将员工按入职年份分组
    year_map = defaultdict(list)
    for e in employees:
        year_map[e["入职年份"]].append(e)

    # 按年份升序排列，呈现时间脉络
    sorted_years = sorted(year_map.items())

    # 打印表头
    header = f"  {'入职年份':>6}  {'人数':>4}  {'平均工资':>10}  {'平均奖金':>10}  {'人均总收入':>10}"
    print(f"\n{header}")
    print(f"  {'-'*56}")

    # 逐年份计算并输出
    for year, emps in sorted_years:
        salaries = [e["基本工资"] for e in emps]
        bonuses  = [e["奖金"]     for e in emps]
        avg_sal  = avg(salaries)
        avg_bon  = avg(bonuses)
        print(f"  {year:>6}  {len(emps):>4}  "
              f"{fmt_money(avg_sal):>10}  "
              f"{fmt_money(avg_bon):>10}  "
              f"{fmt_money(avg_sal + avg_bon):>10}")

    # ── 在职年限分布 ──
    CURRENT_YEAR = 2026   # 当前年份基准，用于计算在职年数
    print_sub("员工在职年限分布")

    tenure_groups = defaultdict(int)   # 各年限区间的人数计数
    for e in employees:
        tenure = CURRENT_YEAR - e["入职年份"]   # 在职年数
        # 根据年限归入对应区间
        if tenure <= 2:
            tenure_groups["0-2年（新员工）"] += 1
        elif tenure <= 5:
            tenure_groups["3-5年"] += 1
        elif tenure <= 10:
            tenure_groups["6-10年"] += 1
        else:
            tenure_groups["10年以上（资深）"] += 1

    # 按从短到长的顺序输出，用 █ 字符生成文本条形图
    order = ["0-2年（新员工）", "3-5年", "6-10年", "10年以上（资深）"]
    for label in order:
        count = tenure_groups[label]
        bar = "█" * count          # 每人对应一个字符块
        print(f"  {label:<14}  {count:>3} 人  {bar}")


# ═══════════════════════════════════════════════════════════
# 模块四：薪资区间分布
# ═══════════════════════════════════════════════════════════

def analyze_salary_distribution(employees):
    """
    统计基本工资在各区间内的人数及占比，并用字符条形图可视化。

    区间划分（单位：元）：
      6k 以下 / 6k~10k / 10k~15k / 15k~20k / 20k~25k / 25k 以上

    参数：
        employees (list[dict]): 全体员工数据列表
    """
    print_title("💰 四、薪资区间分布")

    # 每个元组：(标签, 区间下限, 区间上限)，左闭右开区间
    brackets = [
        ("6k 以下",        0,      6000),
        ("6k ~ 10k",   6000,     10000),
        ("10k ~ 15k",  10000,    15000),
        ("15k ~ 20k",  15000,    20000),
        ("20k ~ 25k",  20000,    25000),
        ("25k 以上",   25000, float("inf")),   # 无上限用正无穷表示
    ]

    print(f"\n  {'区间':<14}  {'人数':>4}  {'占比':>6}  分布")
    print(f"  {'-'*50}")
    total = len(employees)
    for label, lo, hi in brackets:
        # 统计基本工资落在 [lo, hi) 区间内的员工人数
        count = sum(1 for e in employees if lo <= e["基本工资"] < hi)
        pct   = count / total * 100          # 该区间人数占总人数的百分比
        bar   = "█" * count                  # 每人对应一个字符块
        print(f"  {label:<14}  {count:>4}  {pct:>5.1f}%  {bar}")


# ═══════════════════════════════════════════════════════════
# 模块五：奖金占总收入比例分析
# ═══════════════════════════════════════════════════════════

def analyze_bonus_ratio(employees):
    """
    计算每位员工的奖金占总收入（基本工资+奖金）的比例，并按比例降序排列输出。

    同时输出全员平均奖金占比，用 ▓ 字符生成比例条形图（每格代表 5%）。

    参数：
        employees (list[dict]): 全体员工数据列表
    """
    print_title("🎁 五、奖金占总收入比例分析")

    ratios = []
    for e in employees:
        total = e["基本工资"] + e["奖金"]
        # 防止 total 为 0 时出现除零错误（理论上不会，但做防御性处理）
        ratio = e["奖金"] / total * 100 if total > 0 else 0
        ratios.append((e["姓名"], e["部门"], ratio))

    # 按奖金占比从高到低排序
    ratios.sort(key=lambda x: x[2], reverse=True)

    # 全员平均奖金占比
    overall_avg = avg([r[2] for r in ratios])
    print(f"\n  全员平均奖金占比: {overall_avg:.1f}%")

    # 打印排行榜表头
    print(f"\n  {'排名':>4}  {'姓名':<6}  {'部门':<10}  {'奖金占比':>8}")
    print(f"  {'-'*40}")
    for i, (name, dept, ratio) in enumerate(ratios, 1):
        # 每 5% 显示一个 ▓ 字符，直观呈现奖金占比高低
        bar = "▓" * int(ratio / 5)
        print(f"  {i:>4}  {name:<6}  {dept:<10}  {ratio:>7.1f}%  {bar}")


# ═══════════════════════════════════════════════════════════
# 主程序入口
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    DATA_FILE = "employee_data.csv"    # 数据文件路径（与脚本同目录）

    # 打印报告总标题
    print("=" * 60)
    print("        员工数据综合分析报告")
    print("=" * 60)

    # 1. 加载数据
    employees = load_data(DATA_FILE)

    # 2. 依次执行五个分析模块
    analyze_overall(employees)             # 整体概况
    analyze_by_department(employees)       # 按部门分析
    analyze_by_year(employees)             # 按入职年份分析
    analyze_salary_distribution(employees) # 薪资区间分布
    analyze_bonus_ratio(employees)         # 奖金占比分析

    # 打印报告结尾
    print(f"\n{SEPARATOR}")
    print("  ✅ 分析完成")
    print(SEPARATOR)
