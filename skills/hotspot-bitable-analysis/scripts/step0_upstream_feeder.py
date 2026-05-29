#!/usr/bin/env python3
"""
step0_upstream_feeder.py — 上游信息注入热点分析工作流

归属: hotspot-bitable-analysis 技能
功能: 调用 route-analysis 的采集脚本 → 格式化数据 → 输出可合并进主表的格式

使用方式: python3 step0_upstream_feeder.py
输出: data/upstream_feeder_{date}.json
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")

# === Paths ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(SKILL_DIR, "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ROUTE_ANALYSIS_DIR = os.path.join(SKILL_DIR, "..", "route-analysis")
ROUTE_SCRIPT = os.path.join(ROUTE_ANALYSIS_DIR, "scripts", "step1_upstream_collect.py")
ROUTE_DATA = os.path.join(ROUTE_ANALYSIS_DIR, "data", "upstream_collected_%s.json" % TODAY)


def run_collection() -> bool:
    """Run the route-analysis collection script."""
    if not os.path.exists(ROUTE_SCRIPT):
        print("[ERROR] route-analysis 采集脚本不存在: %s" % ROUTE_SCRIPT)
        return False

    print("[上游] 调用 route-analysis 采集脚本 ...")
    result = subprocess.run(
        [sys.executable, ROUTE_SCRIPT],
        cwd=ROUTE_ANALYSIS_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print("[ERROR] 采集脚本执行失败!")
        print(result.stderr)
        return False

    # Print the output summary
    for line in result.stdout.splitlines():
        if line.strip():
            print("  %s" % line)
    return True


def load_upstream_data() -> list:
    """Load collected upstream data from JSON."""
    route_data = os.path.join(ROUTE_ANALYSIS_DIR, "data", "upstream_collected_%s.json" % TODAY)
    
    if not os.path.exists(route_data):
        print("[ERROR] 上游数据文件不存在: %s" % route_data)
        # Try to find the latest
        data_dir = os.path.join(ROUTE_ANALYSIS_DIR, "data")
        if os.path.exists(data_dir):
            files = sorted([f for f in os.listdir(data_dir) if f.startswith("upstream_collected_")])
            if files:
                latest = files[-1]
                route_data = os.path.join(data_dir, latest)
                print("[INFO] 使用最新数据: %s" % latest)
            else:
                return []

    with open(route_data, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])


def format_for_hotspot(upstream_items: list) -> list:
    """
    Convert upstream items to hotspot-compatible format.
    
    Hotspot fields:
      - 热点话题 (Text, primary)
      - 来源渠道 (MultiSelect)
      - 话题类别 (SingleSelect)
      - 热度指数 (Text)
      - 热度指数数值 (Number)
      - 关联地点 (Text)
      - 关联旅游景点 (Text)
      - 旅游商机分析 (Text)
      - 优先级 (SingleSelect: 高/中/低)
      - 备注 (Text, URL link)
    
    Mapping from upstream:
      - 热点话题 = title
      - 来源渠道 = ["综合"] (always)
      - 话题类别 = category (mapped)
      - 热度指数 = "上游产业信号"
      - 热度指数数值 = 80 (baseline for upstream, can be adjusted)
      - 关联地点 = extracted from title (if any)
      - 关联旅游景点 = ""
      - 旅游商机分析 = impact + summary
      - 优先级 = derived from category
      - 备注 = source + url
    """
    
    # Category mapping
    category_map = {
        "航空运力": "文旅美食",     # closest hotspot category
        "酒店供应链": "文旅美食",
        "政策签证": "国际外交",
        "会展活动": "文旅美食",
    }

    # Keyword-to-location extraction
    location_keywords = {
        "北京": "北京", "上海": "上海", "广州": "广州", "深圳": "深圳",
        "成都": "成都", "杭州": "杭州", "三亚": "三亚", "海南": "海南",
        "云南": "云南", "丽江": "丽江", "大理": "大理",
        "新疆": "新疆", "西藏": "西藏", "青海": "青海",
        "香港": "香港", "澳门": "澳门", "台湾": "台湾",
        "东京": "东京", "大阪": "大阪", "首尔": "首尔", "曼谷": "曼谷",
        "新加坡": "新加坡", "巴厘岛": "巴厘岛", "普吉岛": "普吉岛",
        "欧洲": "欧洲", "美国": "美国", "日本": "日本", "韩国": "韩国",
        "泰国": "泰国", "马尔代夫": "马尔代夫",
    }

    formatted = []
    for item in upstream_items:
        title = item.get("title", "")
        category = item.get("category", "政策签证")
        impact = item.get("impact", "")
        source = item.get("source", "")
        url = item.get("url", "")

        # Derive priority from category + impact keywords
        if any(k in impact for k in ["红利", "阀门", "供给增加", "信号"]):
            priority = "高"
        elif category == "会展活动":
            priority = "中"
        else:
            priority = "中"

        # Try to extract location
        location = ""
        for kw, loc in location_keywords.items():
            if kw in title:
                location = loc
                break

        # Build the analysis text
        analysis_parts = []
        analysis_parts.append("📡 [上游信号]")
        analysis_parts.append("来源: %s" % source)
        if impact:
            analysis_parts.append("影响: %s" % impact)
        analysis_parts.append("类别: %s" % category)
        analysis = " | ".join(analysis_parts)

        hotspot_category = category_map.get(category, "社会民生")

        formatted.append({
            "热点话题": title,
            "来源渠道": ["综合"],
            "话题类别": hotspot_category,
            "热度指数": "上游产业信号 - %s" % source,
            "热度指数数值": 80,
            "关联地点": location,
            "关联旅游景点": "",
            "旅游商机分析": analysis,
            "优先级": priority,
            "备注": "📎 %s | %s" % (source, url),
            # Extra metadata for debugging
            "_upstream_source": source,
            "_upstream_url": url,
        })

    return formatted


def main():
    print("\n" + "=" * 60)
    print("  上游信息注入热点分析工作流 v1.0")
    print("  日期: %s" % TODAY)
    print("=" * 60)

    # Step 1: Run upstream collection (or load existing data)
    print("\n[步骤1] 采集上游信息 ...")
    
    # Load existing data first (if any)
    upstream_items = load_upstream_data()
    
    if not upstream_items:
        print("  [INFO] 未找到已有数据，执行采集...")
        if run_collection():
            upstream_items = load_upstream_data()
    
    if not upstream_items:
        print("[ERROR] 无法获取上游数据")
        sys.exit(1)
    
    print("  [OK] 加载 %d 条上游数据" % len(upstream_items))

    # Step 2: Format for hotspot
    print("\n[步骤2] 格式化为热点兼容格式 ...")
    hotspot_items = format_for_hotspot(upstream_items)
    print("  [OK] 转换 %d 条" % len(hotspot_items))

    # Step 3: Write output
    print("\n[步骤3] 写入输出文件 ...")
    output_file = os.path.join(OUTPUT_DIR, "upstream_feeder_%s.json" % TODAY)
    output_data = {
        "meta": {
            "date": TODAY,
            "total_upstream_items": len(upstream_items),
            "total_hotspot_items": len(hotspot_items),
            "_note": "此数据可与热点分析结果合并，先去重后写入Bitable",
        },
        "items": hotspot_items,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("  [OK] 输出: %s" % output_file)

    # Step 4: Summary
    print("\n[摘要]")
    
    # Count by priority
    priorities = {}
    categories = {}
    sources = set()
    for item in hotspot_items:
        p = item["优先级"]
        priorities[p] = priorities.get(p, 0) + 1
        c = item["话题类别"]
        categories[c] = categories.get(c, 0) + 1
        sources.add(item.get("_upstream_source", ""))

    for p, c in sorted(priorities.items()):
        print("  优先级 %s: %d 条" % (p, c))
    print("  来源: %s" % ", ".join(sorted(sources)))
    
    # Also write a simple dedup-ready version for Bitable insertion
    dedup_file = os.path.join(OUTPUT_DIR, "upstream_feeder_%s_dedup.csv" % TODAY)
    with open(dedup_file, "w", encoding="utf-8") as f:
        f.write("热点话题,来源渠道,话题类别,热度指数,热度指数数值,关联地点,优先级,分析,备注\n")
        for item in hotspot_items:
            f.write('"%s","%s","%s","%s",%d,"%s","%s","%s","%s"\n' % (
                item["热点话题"].replace('"', '""'),
                "综合",
                item["话题类别"],
                item["热度指数"],
                item["热度指数数值"],
                item["关联地点"],
                item["优先级"],
                item["旅游商机分析"].replace('"', '""'),
                item["备注"].replace('"', '""'),
            ))
    print("\n  CSV: %s" % dedup_file)
    print("\n" + "=" * 60)
    print("  完成! 数据已准备就绪，可直接与热点数据合并。")
    print("=" * 60)


if __name__ == "__main__":
    main()
