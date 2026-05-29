#!/usr/bin/env python3
"""
每日文旅商机速报 — 上游产业链 + 全网热搜 混合简报
飞书安全版本：避免使用[]()等markdown链接语法
"""
import json, os, sys, subprocess

TODAY = "2026-05-29"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(SKILL_DIR, "data")
ROUTE_DIR = os.path.join(SKILL_DIR, "..", "route-analysis")

def fetch_hot_topics():
    print("📡 采集热搜...")
    results = []
    for src, cmd, title_key, hot_key in [
        ("头条", ["opencli","toutiao","hot","--limit","5","-f","json"], "title", "hot_value"),
        ("抖音", ["opencli","douyin","hashtag","hot","--limit","5","-f","json"], "name", "view_count"),
    ]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if r.returncode == 0:
                for item in json.loads(r.stdout):
                    results.append({"source": src, "title": item.get(title_key,""), "hot": item.get(hot_key,0)})
        except: pass
    def parse_hot(h):
        h = str(h).replace(",","").replace("热度","").replace(" ","")
        if "万" in h:
            try: return int(float(h.replace("万","")) * 10000)
            except: return 0
        try: return int(h)
        except: return 0
    results.sort(key=lambda x: parse_hot(x.get("hot",0)), reverse=True)
    return results[:10]

def load_upstream():
    path = os.path.join(ROUTE_DIR, "data", f"upstream_collected_{TODAY}.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        return data.get("items", [])
    return []

def filter_high_value(items):
    high = []
    for item in items:
        pri = item.get("priority", "")
        t = item.get("title", "")
        if pri == "high" or any(k in t for k in ["航线","签证","免签","开业","入驻"]):
            high.append(item)
    return high

def generate_briefing(hot_topics, upstream):
    lines = []
    lines.append("\n📊 今日文旅商机速报  " + TODAY)
    lines.append("=" * 48)

    # 上游产业链
    lines.append("\n🏭 上游产业链情报")
    lines.append("-" * 32)

    cats = {}
    for item in upstream:
        cats.setdefault(item.get("category","其他"), []).append(item)

    src_icon = {"RoutesOnline":"✈️","环球旅讯":"📰","文旅部":"🏛️","新华网旅游":"📡","HotelNewsResource":"🏨","FlightGlobal":"✈️"}
    for cat in ["航空运力", "酒店供应链", "政策签证"]:
        items = cats.get(cat, [])
        if not items:
            continue
        lines.append(f"\n▎{cat} · {len(items)}条")
        for item in items[:3]:
            title = item.get("title","")[:50]
            # 清理数据源中的[]前缀，避免飞书解释为链接
            title = title.replace("[","《").replace("]","》").replace("【","《").replace("】","》")
            src = item.get("source","")
            icon = src_icon.get(src, "📌")
            lines.append(f"  {icon} {title} — {src}")

    # 热搜 TOP10
    lines.append("\n🔥 今日热搜 TOP10")
    lines.append("-" * 32)

    src_emoji = {"头条":"📰","抖音":"🎵","知乎":"💬","微博":"🐦","B站":"📺","贴吧":"💭"}
    for i, t in enumerate(hot_topics[:10], 1):
        icon = src_emoji.get(t["source"], "📍")
        title = t['title'][:50].replace("[","《").replace("]","》")
        lines.append(f"  {i}. {icon} {title}")

    # 混合分析
    lines.append("\n💡 商机交叉分析")
    lines.append("-" * 32)

    all_titles = [t["title"] for t in hot_topics] + [t.get("title","") for t in upstream]
    all_text = " ".join(all_titles)

    signals = []
    if "签证" in all_text or "免签" in all_text:
        signals.append("签证利好：政策放宽信号，关注出入境游放量")
    if "航线" in all_text or "航班" in all_text or "开通" in all_text:
        signals.append("运力增长：新航线或加密信号，关注目的地库存准备")
    if "高温" in all_text or "避暑" in all_text:
        signals.append("高温商机：避暑需求明确，可推丽江、长白山、贵州")
    if "酒店" in all_text or "度假" in all_text or "开业" in all_text:
        signals.append("供给信号：新酒店开业或品牌入驻，关注目的地热度")
    if "端午" in all_text or "暑期" in all_text:
        signals.append("窗口期：端午或暑期临近，锁库存推内容")

    if signals:
        for s in signals:
            lines.append("  ✅ " + s)
    else:
        lines.append("  暂无明显交叉信号")

    lines.append("\n" + "=" * 48)
    lines.append("📎 完整数据：https://bytedance.feishu.cn/base/ZdpRbPT2qaGsBvsqiNucQX1Knwh")

    return "\n".join(lines)

if __name__ == "__main__":
    print("=" * 48)
    print(f"  每日文旅商机速报 v1.1  {TODAY}")
    print("=" * 48)

    hot = fetch_hot_topics()
    print(f"[热搜] {len(hot)} 条")

    up = load_upstream()
    print(f"[上游] {len(up)} 条")

    briefing = generate_briefing(hot, filter_high_value(up))

    out_path = os.path.join(OUTPUT_DIR, f"briefing_{TODAY}.md")
    with open(out_path, "w") as f:
        f.write(briefing)
    print(f"[简报] 已保存: {out_path}")
    print(briefing)
