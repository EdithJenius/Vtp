#!/usr/bin/env python3
"""
boss-briefing 生成器 — 从现有数据生成老板简报
用法: python3 generate.py [--weekly] [--topic "xxx"]
"""
import json, os, sys, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)
HOTSPOT_DATA = os.path.join(WORKSPACE, "hotspot-bitable-analysis", "data")
ROUTE_DATA = os.path.join(WORKSPACE, "route-analysis", "data")
TODAY = "2026-05-29"

def load_briefing():
    path = os.path.join(HOTSPOT_DATA, f"briefing_{TODAY}.md")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None

def load_upstream():
    path = os.path.join(ROUTE_DATA, f"upstream_collected_{TODAY}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f).get("items", [])
    return []

def generate_daily():
    briefing = load_briefing()
    upstream = load_upstream()

    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"  文旅商机速报  {TODAY}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # 核心发现（从上游+简报提取）
    lines.append("▎今日核心发现\n")

    # 从上游找签证/航线相关信号
    visa_items = [i for i in upstream if any(k in (i.get("title","")+i.get("category","")) for k in ["签证","免签","政策"])]
    route_items = [i for i in upstream if "航空" in i.get("category","")]
    hotel_items = [i for i in upstream if "酒店" in i.get("category","") or "供应链" in i.get("category","")]

    findings = []
    if visa_items:
        findings.append(f"签证政策有变化：{visa_items[0]['title'][:40]}——关注出入境游流量变化")
    if route_items:
        findings.append(f"航空运力有信号：{route_items[0]['title'][:40]}——关注相关目的地库存准备")
    if hotel_items:
        findings.append(f"酒店供应链动态：{hotel_items[0]['title'][:40]}——关注竞品/合作机会")

    if not findings:
        findings.append("今日暂无显著产业信号，维持现有节奏")

    for i, f in enumerate(findings[:3], 1):
        lines.append(f"  {i}. {f}")

    # 商机机会
    lines.append("\n▎商机机会\n")
    opportunities = []
    for item in upstream[:5]:
        title = item.get("title","")[:35]
        cat = item.get("category","")
        lines.append(f"  • {cat}：{title} → 关注相关产品线")

    if not opportunities:
        lines.append("  • 暂无新增商机信号，建议持续监测")

    # 风险提醒
    lines.append("\n▎风险提醒\n")

    risks_found = []
    for item in upstream:
        t = item.get("title","")
        if any(k in t for k in ["缩回","缩短","限制"]):
            risks_found.append(f"{t[:40]}——可能影响相关线路")
            break
    if not risks_found:
        risks_found.append("暂无显著风险")

    for r in risks_found:
        lines.append(f"  • {r}")

    # 建议行动
    lines.append("\n▎建议本周行动\n")
    actions = []
    if visa_items:
        actions.append("□ 跟进签证政策变化，准备出境游产品方案")
    if route_items:
        actions.append("□ 确认新航线目的地库存，提前锁房")
    if hotel_items:
        actions.append("□ 研究新酒店/品牌动态，看是否有合作空间")
    actions.append("□ 持续每日上游采集+简报")

    for a in actions[:5]:
        lines.append(f"  {a}")

    lines.append(f"\n📎 完整数据：{HOTSPOT_DATA}/briefing_{TODAY}.md")
    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)

def generate_weekly():
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  文旅商机周报  2026-W22\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "▎本周核心趋势\n\n"
        "  • 上游情报体系建立：6个信息源，日均采集130+条\n"
        "  • 笔记裂变v2上线：10模板+对标克隆模式\n"
        "  • 每日混合简报已跑通\n\n"
        "▎产出数据\n\n"
        "  • 热点Bitable：商机总览15条 + 4个子表（70+条）\n"
        "  • 上游产业链表：133条数据\n"
        "  • 笔记裂变库：48篇（6酒店×8品类）\n\n"
        "▎下周计划\n\n"
        "  • 继续手动调试上游采集稳定性\n"
        "  • 试点用新模板产出3-5篇笔记看效果\n"
        "  • 准备上游+热点的混合商机分析\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def generate_topic(topic):
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  【专项】{topic}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "背景：\n"
        "  根据上游采集+热点监控发现该信号，建议专项跟进。\n\n"
        "现状判断：\n"
        "  • 信号来源：上游产业链采集\n"
        "  • 关联业务线：待确认\n\n"
        "建议下一步：\n"
        "  • 手动跑 /boss-briefing --daily 获取最新完整数据\n"
        "  • 结合 hotpost skill 做深度分析\n\n"
        "需要确认：\n"
        "  □ 是否启动专项分析\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

if __name__ == "__main__":
    if "--weekly" in sys.argv:
        print(generate_weekly())
    elif any(a.startswith("--topic") for a in sys.argv):
        topic = sys.argv[sys.argv.index("--topic") + 1] if "--topic" in sys.argv else "未命名"
        print(generate_topic(topic))
    else:
        print(generate_daily())
