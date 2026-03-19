#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_gen.py —— 周报自动生成脚本
用法：
    python report_gen.py                  # 交互式输入模式
    python report_gen.py --file input.txt # 从文本文件读取（格式见 README 注释）

生成文件：weekly_report_YYYY-WW.md（当年第几周）
"""

import argparse
import os
import re
from datetime import datetime, timedelta


# ──────────────────────────────────────────────
# 1. 工具函数：获取本周起止日期
# ──────────────────────────────────────────────
def get_week_range(date: datetime) -> tuple[str, str]:
    """
    根据给定日期，返回该自然周（周一~周日）的起止日期字符串。

    Args:
        date: 参考日期（通常是今天）

    Returns:
        (start_str, end_str) 格式为 YYYY-MM-DD
    """
    # 获取周一（weekday() == 0 表示周一）
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# ──────────────────────────────────────────────
# 2. 工具函数：将用户输入的多行文本解析为条目列表
# ──────────────────────────────────────────────
def parse_items(raw: str) -> list[str]:
    """
    将原始多行字符串解析为去空行、去首尾空格的条目列表。
    每个非空行被视为一个独立条目。

    Args:
        raw: 用户输入的多行文本

    Returns:
        清洗后的字符串列表
    """
    lines = raw.strip().splitlines()
    # 过滤空行，并去掉每行首尾空白
    items = [line.strip() for line in lines if line.strip()]
    return items


# ──────────────────────────────────────────────
# 3. 工具函数：将条目列表渲染为 Markdown 有序列表
# ──────────────────────────────────────────────
def render_ordered_list(items: list[str]) -> str:
    """
    将字符串列表渲染为 Markdown 有序列表（1. 2. 3. …）。

    Args:
        items: 条目列表

    Returns:
        Markdown 格式的有序列表字符串
    """
    if not items:
        return "_（暂无内容）_\n"
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items)) + "\n"


# ──────────────────────────────────────────────
# 4. 核心函数：生成周报 Markdown 内容
# ──────────────────────────────────────────────
def build_report(
    author: str,
    department: str,
    this_week_items: list[str],
    next_week_items: list[str],
    note: str = "",
) -> str:
    """
    根据传入信息组装完整的周报 Markdown 字符串。

    Args:
        author:           填报人姓名
        department:       所属部门
        this_week_items:  本周工作内容条目列表
        next_week_items:  下周工作计划条目列表
        note:             备注（可为空）

    Returns:
        符合预设格式的 Markdown 文本（不少于 200 字）
    """
    now = datetime.now()
    week_num = now.isocalendar()[1]          # ISO 周次
    year = now.year
    start_date, end_date = get_week_range(now)

    # ── 头部元信息（不含生成时间，保持简洁） ──
    header = f"""\
# 📋 工作周报

| 字段 | 内容 |
|------|------|
| **填报人** | {author} |
| **部门** | {department} |
| **周次** | {year} 年第 {week_num:02d} 周（{start_date} ~ {end_date}） |

---

"""

    # ── 本周工作内容 ──
    this_week_section = f"""\
## 一、本周工作内容

{render_ordered_list(this_week_items)}
"""

    # ── 下周工作计划 ──
    next_week_section = f"""\
## 二、下周工作计划

{render_ordered_list(next_week_items)}
"""

    # ── 备注（可选） ──
    note_section = ""
    if note.strip():
        note_section = f"""\
## 三、备注与风险提示

{note.strip()}

"""

    # ── 页脚分隔线 ──
    footer = "---\n"

    # 拼接完整报告（去掉自动署名和补充说明）
    report = header + this_week_section + "\n" + next_week_section + "\n" + note_section + footer

    return report


# ──────────────────────────────────────────────
# 5. 工具函数：从文本文件解析输入
# ──────────────────────────────────────────────
def parse_input_file(filepath: str) -> dict:
    """
    从结构化文本文件中读取周报内容，文件格式示例：

        [author]
        张三
        [department]
        技术部
        [this_week]
        完成需求评审
        修复线上 BUG #123
        [next_week]
        开发新功能模块
        编写单元测试
        [note]
        无风险事项

    Args:
        filepath: 输入文件路径

    Returns:
        包含 author/department/this_week/next_week/note 键的字典
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"找不到输入文件：{filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 用正则按 [section] 标签分割各区块
    sections = re.split(r"\[(\w+)\]", content)
    # sections 结构: ['', 'author', '张三\n', 'department', '技术部\n', ...]
    data = {}
    for i in range(1, len(sections) - 1, 2):
        key = sections[i].strip()
        value = sections[i + 1].strip()
        data[key] = value

    return {
        "author":     data.get("author", "（未填写）"),
        "department": data.get("department", "（未填写）"),
        "this_week":  data.get("this_week", ""),
        "next_week":  data.get("next_week", ""),
        "note":       data.get("note", ""),
    }


# ──────────────────────────────────────────────
# 6. 交互式输入模式
# ──────────────────────────────────────────────
def interactive_input() -> dict:
    """
    通过命令行交互方式逐步引导用户输入周报内容。

    Returns:
        包含 author/department/this_week/next_week/note 键的字典
    """
    print("\n" + "=" * 50)
    print("  📝  周报生成器 —— 交互式输入模式")
    print("=" * 50)

    author = input("\n请输入填报人姓名：").strip() or "（未填写）"
    department = input("请输入所属部门：").strip() or "（未填写）"

    print("\n【本周工作内容】")
    print("  每行输入一条工作内容，输入完毕后连续按两次回车结束：")
    this_week = _read_multiline()

    print("\n【下周工作计划】")
    print("  每行输入一条工作计划，输入完毕后连续按两次回车结束：")
    next_week = _read_multiline()

    print("\n【备注/风险提示】（可直接回车跳过）：")
    note = input("> ").strip()

    return {
        "author": author,
        "department": department,
        "this_week": this_week,
        "next_week": next_week,
        "note": note,
    }


def _read_multiline() -> str:
    """
    读取多行输入，直到用户连续输入两个空行为止。

    Returns:
        多行文本拼接成的字符串
    """
    lines = []
    empty_count = 0
    while True:
        line = input("> ")
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 7. 输出：将报告写入 Markdown 文件
# ──────────────────────────────────────────────
def save_report(content: str, output_dir: str = ".") -> str:
    """
    将生成的周报内容写入 Markdown 文件，文件名含年份和周次。

    Args:
        content:    Markdown 文本内容
        output_dir: 输出目录（默认为当前目录）

    Returns:
        最终写入的文件绝对路径
    """
    now = datetime.now()
    year, week_num, _ = now.isocalendar()
    filename = f"weekly_report_{year}-W{week_num:02d}.md"
    filepath = os.path.join(output_dir, filename)

    os.makedirs(output_dir, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return os.path.abspath(filepath)


# ──────────────────────────────────────────────
# 8. 主入口
# ──────────────────────────────────────────────
def main():
    """
    命令行主入口：解析参数，收集数据，生成并保存周报。
    """
    # 定义命令行参数
    parser = argparse.ArgumentParser(
        description="周报自动生成脚本 —— 输出标准 Markdown 文档"
    )
    parser.add_argument(
        "--file", "-f",
        metavar="INPUT_FILE",
        help="从结构化文本文件读取输入内容（省略则进入交互式输入模式）",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="OUTPUT_DIR",
        default=".",
        help="输出目录（默认：当前目录）",
    )
    args = parser.parse_args()

    # ── 获取输入数据 ──
    if args.file:
        # 文件读取模式
        data = parse_input_file(args.file)
        print(f"\n✅ 已从文件读取输入：{args.file}")
    else:
        # 交互式输入模式
        data = interactive_input()

    # ── 解析条目列表 ──
    this_week_items = parse_items(data["this_week"])
    next_week_items = parse_items(data["next_week"])

    # ── 生成报告内容 ──
    report_content = build_report(
        author=data["author"],
        department=data["department"],
        this_week_items=this_week_items,
        next_week_items=next_week_items,
        note=data.get("note", ""),
    )

    # ── 保存文件 ──
    saved_path = save_report(report_content, output_dir=args.output)

    # 单独定义正则，避免在 f-string 内转义混乱
    _strip_pat = re.compile(r'[#|>\-*`_\[\]()!\n=]')
    char_count = len(_strip_pat.sub("", report_content).replace(" ", ""))
    print(f"\n🎉 周报已生成：{saved_path}")
    print(f"   字符数（去标记后）：{char_count}")


if __name__ == "__main__":
    main()
