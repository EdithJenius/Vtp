#!/usr/bin/env python3
"""
小红书内容拆解 - 5维度分析框架
用于自动化拆解对标笔记

使用方法:
  python3 analyze.py <笔记标题/描述> [<笔记正文>]
"""

import sys

DIMENSIONS = {
    "标题": ["公式分析", "人群圈层", "情绪钩子", "关键词布局", "视觉装饰"],
    "选题": ["目标群体", "人群痛点", "选题核心类型"],
    "素材/视觉": ["图片构图", "色调情绪", "信息密度", "视频前3秒", "BGM"],
    "金句": ["焦虑/痛点型", "情绪/价值观型", "认同型"],
    "点击动机": ["审美驱动", "利益驱动", "情绪驱动"]
}

def print_framework():
    print("=" * 50)
    print("📋 内容拆解 5 维度框架")
    print("=" * 50)
    for dim, points in DIMENSIONS.items():
        print(f"\n【{dim}】")
        for p in points:
            print(f"  - {p}")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    print_framework()
    if len(sys.argv) > 1:
        print(f"\n📝 待分析笔记: {sys.argv[1]}")
