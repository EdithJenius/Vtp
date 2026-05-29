#!/usr/bin/env python3
"""
step1_upstream_collect.py — 上游产业链信息采集主脚本

归属: route-analysis 技能
目标: 采集航空运力/酒店供应链/政策签证等上游信息，输出结构化JSON

独立可运行: python3 step1_upstream_collect.py
输出: data/upstream_collected_{date}.json
"""

import json
import os
import re
import urllib.request
import urllib.error
import html
from datetime import datetime, timezone, timedelta
from typing import Optional

BEIJING_TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

REQUEST_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


def fetch_url(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    return raw.decode("gbk")
                except UnicodeDecodeError:
                    return raw.decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print("  [WARN] %s: %s" % (type(e).__name__, e))
        return None


def clean_title(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ============================================================
# Source 1: 新华网旅游频道 (news.cn/travel)
# URL pattern: href="/travel/YYYYMMDD/.../c.html"
# ============================================================

def collect_xinhua_travel() -> list:
    print("[采集] 新华网旅游频道 ...")
    results = []
    html_content = fetch_url("http://www.news.cn/travel/")
    if not html_content:
        print("  [FALLBACK] 新华网不可用")
        return results

    # Build pattern using non-raw string to avoid quote escaping issues
    # Pattern: <a href="/travel/YYYYMMDD/hash/c.html">title</a>
    url_part = r'/travel/\d{8}/[a-f0-9]+/c\.html'
    pat = '<a[^>]*href="(%s)"[^>]*>(.*?)</a>' % url_part
    raw_links = re.findall(pat, html_content, re.DOTALL)

    url_titles = {}
    for href, text in raw_links:
        title = clean_title(text)
        if title and len(title) > 3:
            if href not in url_titles or len(title) > len(url_titles[href]):
                url_titles[href] = title

    seen_titles = set()
    for href, title in url_titles.items():
        if title in seen_titles:
            continue
        seen_titles.add(title)
        date_match = re.search(r'/travel/(\d{8})/', href)
        article_date = date_match.group(1) if date_match else TODAY.replace("-", "")
        formatted_date = "%s-%s-%s" % (article_date[:4], article_date[4:6], article_date[6:8])
        category = classify_travel_news(title)
        results.append({
            "source": "新华网旅游",
            "title": title,
            "summary": "",
            "category": category,
            "impact": "",
            "url": "http://www.news.cn%s" % href,
            "timestamp": formatted_date,
        })

    print("  [OK] %d 条新闻" % len(results))
    return results


# ============================================================
# Source 2: 文旅部新闻 (mct.gov.cn/whzx/whyw/)
# URL: ./YYYYMM/tYYYYMMDD_ID.htm
# ============================================================

def collect_mct_news() -> list:
    print("[采集] 文旅部官网 ...")
    results = []
    html_content = fetch_url("https://www.mct.gov.cn/whzx/whyw/")
    if not html_content:
        print("  [FALLBACK] 文旅部不可用")
        return results

    # Pattern: ./202605/t20260522_965928.htm  (YYYYMM dir, tYYYYMMDD_ID)
    url_part = r'\./20\d{4}/t20\d{6}_\d+\.htm'
    pat = '<a[^>]*href="(%s)"[^>]*>(.*?)</a>' % url_part
    links = re.findall(pat, html_content, re.DOTALL)

    # Also try absolute paths: /whzx/whyw/202605/t20260522_965928.htm
    url_part2 = r'/whzx/whyw/20\d{4}/t20\d{6}_\d+\.htm'
    pat2 = '<a[^>]*href="(%s)"[^>]*>(.*?)</a>' % url_part2
    links2 = re.findall(pat2, html_content, re.DOTALL)

    # Find all dates in the page
    all_dates = re.findall(r'20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])', html_content)

    seen_titles = set()
    idx = 0
    for href, link_text in links + links2:
        title = clean_title(link_text)
        if not title or len(title) < 5:
            continue
        if title in seen_titles:
            continue
        seen_titles.add(title)
        article_date = all_dates[idx] if idx < len(all_dates) else TODAY
        idx += 1

        if href.startswith("./"):
            abs_url = "https://www.mct.gov.cn/whzx/whyw/%s" % href[2:]
        else:
            abs_url = "https://www.mct.gov.cn%s" % href

        category = classify_policy_news(title)
        results.append({
            "source": "文旅部",
            "title": title,
            "summary": "",
            "category": category,
            "impact": assess_mct_impact(title),
            "url": abs_url,
            "timestamp": article_date,
        })

    print("  [OK] %d 条新闻" % len(results))
    return results


# ============================================================
# Source 3: RoutesOnline — 航线话题
# ============================================================

def collect_routesonline() -> list:
    print("[采集] RoutesOnline ...")
    results = []
    html_content = fetch_url("https://www.routesonline.com/")
    if not html_content:
        print("  [FALLBACK] RoutesOnline 不可用")
        return results

    url_part = r'https://www\.routesonline\.com/news/tagged/\d+/(?:[^"]+)'
    pat = '<a[^>]*href="(%s)"[^>]*>(.*?)</a>' % url_part
    tags = re.findall(pat, html_content, re.DOTALL)

    seen = set()
    for href, text in tags:
        title = clean_title(text)
        if not title or len(title) < 3:
            continue
        if title in seen:
            continue
        seen.add(title)
        results.append({
            "source": "RoutesOnline",
            "title": "[航线动态] %s" % title,
            "summary": "RoutesOnline %s 相关航线动态" % title,
            "category": "航空运力",
            "impact": "",
            "url": href,
            "timestamp": TODAY,
        })

    print("  [OK] %d 条航线话题" % len(results))
    return results


# ============================================================
# Source 4: HotelNewsResource — 国际酒店行业新闻
# ============================================================

def collect_hotelnews() -> list:
    print("[采集] HotelNewsResource ...")
    results = []
    html_content = fetch_url("https://www.hotelnewsresource.com/")
    if not html_content:
        print("  [FALLBACK] HotelNewsResource 不可用")
        return results

    url_part = r'article\d+\.html'
    pat = '<a[^>]*href="(%s)"[^>]*>(.*?)</a>' % url_part
    links = re.findall(pat, html_content, re.DOTALL)

    # Dedup by href: keep longest title
    href_titles = {}
    for href, text in links:
        title = clean_title(text)
        if title and len(title) > 5:
            if href not in href_titles or len(title) > len(href_titles[href]):
                href_titles[href] = title

    seen_titles = set()
    for href, title in href_titles.items():
        if title in seen_titles:
            continue
        seen_titles.add(title)

        abs_url = "https://www.hotelnewsresource.com/%s" % href
        category = "酒店供应链"
        if any(k in title for k in ["Airline", "Flight", "Airport", "Aviation"]):
            category = "航空运力"
        elif any(k in title for k in ["Visa", "Policy", "Regulation"]):
            category = "政策签证"
        elif any(k in title for k in ["Conference", "Summit", "Event"]):
            category = "会展活动"

        results.append({
            "source": "HotelNewsResource",
            "title": title,
            "summary": "",
            "category": category,
            "impact": "",
            "url": abs_url,
            "timestamp": TODAY,
        })

    print("  [OK] %d 条新闻" % len(results))
    return results


# ============================================================
# Source 5: FlightGlobal — 航空新闻
# ============================================================

def collect_flightglobal() -> list:
    print("[采集] FlightGlobal ...")
    results = []
    html_content = fetch_url("https://www.flightglobal.com/")
    if not html_content:
        print("  [FALLBACK] FlightGlobal 不可用")
        return results

    # Only match content/article-like paths (not navigation)
    url_part = r'https://www\.flightglobal\.com/(?:paid-content|news|airlines|airports|technology|business|defence)/[^"]+'  # noqa
    pat = '<a[^>]*href="(%s)"[^>]*>(.*?)</a>' % url_part
    links = re.findall(pat, html_content, re.DOTALL)

    seen_titles = set()
    for href, text in links:
        title = clean_title(text)
        # Filter: skip navigation, very short, subscribes, categories
        if not title or len(title) < 10:
            continue
        if title.lower() in ['subscribe', 'subscribesubscribe', 'news', 'home',
                              'about', 'contact', 'login', 'register', 'search',
                              'menu', 'more', 'view more', 'all news']:
            continue
        if title in seen_titles:
            continue
        seen_titles.add(title)

        prefix = "[付费] " if "paid-content" in href else ""
        results.append({
            "source": "FlightGlobal",
            "title": "%s%s" % (prefix, title),
            "summary": "",
            "category": "航空运力",
            "impact": "",
            "url": href,
            "timestamp": TODAY,
        })

    print("  [OK] %d 条航空新闻" % len(results))
    return results


# ============================================================
# Source 6: 环球旅讯 (JS渲染受限)
# ============================================================

def collect_traveldaily() -> list:
    print("[采集] 环球旅讯 TravelDaily ...")
    results = []
    html_content = fetch_url("https://www.traveldaily.cn/")
    if not html_content:
        print("  [FALLBACK] TravelDaily 不可用")
        return results

    url_part = r'/article/\d+[^"]*'
    pat = '<a[^>]*href="(%s)"[^>]*>(.*?)</a>' % url_part
    articles = re.findall(pat, html_content, re.DOTALL)

    seen_titles = set()
    for href, text in articles:
        title = clean_title(text)
        if not title or len(title) < 5:
            continue
        if title in seen_titles:
            continue
        seen_titles.add(title)

        category = classify_travel_news(title)
        results.append({
            "source": "环球旅讯",
            "title": title,
            "summary": "",
            "category": category,
            "impact": "",
            "url": "https://www.traveldaily.cn%s" % href,
            "timestamp": TODAY,
        })

    if len(results) < 3:
        print("  [NOTE] 仅 %d 条 (JS渲染网站)" % len(results))
    else:
        print("  [OK] %d 条" % len(results))
    return results


# ============================================================
# Classification
# ============================================================

def classify_travel_news(title: str) -> str:
    title_lower = title.lower()
    aviation_kw = ["航空", "航班", "航线", "飞机", "机场", "航司", "国航", "东航",
                    "南航", "海航", "春秋", "吉祥", "出境游", "国际机票"]
    if any(k in title for k in aviation_kw):
        return "航空运力"
    aviation_en = ["airline", "flight", "airport", "route", "aviation", "boeing", "airbus"]
    if any(k in title_lower for k in aviation_en):
        return "航空运力"
    hotel_kw = ["酒店", "民宿", "住宿", "度假村", "客栈", "希尔顿", "万豪", "洲际", "凯悦"]
    if any(k in title for k in hotel_kw):
        return "酒店供应链"
    hotel_en = ["hotel", "resort", "hospitality", "lodging", "property"]
    if any(k in title_lower for k in hotel_en):
        return "酒店供应链"
    visa_kw = ["签证", "免签", "落地签", "护照", "移民", "政策", "入境"]
    if any(k in title for k in visa_kw):
        return "政策签证"
    event_kw = ["展会", "会议", "峰会", "论坛", "博览会", "会展"]
    if any(k in title for k in event_kw):
        return "会展活动"
    return "政策签证"


def classify_policy_news(title: str) -> str:
    if any(k in title for k in ["签证", "免签", "护照", "出入境"]):
        return "政策签证"
    if any(k in title for k in ["航空", "航班", "航线", "机场"]):
        return "航空运力"
    if any(k in title for k in ["酒店", "民宿", "住宿"]):
        return "酒店供应链"
    if any(k in title for k in ["展会", "会议", "峰会", "论坛", "博览会"]):
        return "会展活动"
    return "政策签证"


def assess_mct_impact(title: str) -> str:
    if "人次" in title and "假期" in title:
        return "宏观需求信号：假期出行数据反映市场热度"
    if "免签" in title or "签证" in title:
        return "政策阀门变化：影响出境游目的地的需求爆发"
    if "消费" in title:
        return "消费力指标：反映旅游消费趋势变化"
    if "入境" in title:
        return "入境游信号：关注外国游客需求变化"
    if "强制消费" in title or "市场秩序" in title:
        return "行业合规：影响渠道合作与定价策略"
    return ""


def auto_assess_impact(title: str, category: str) -> str:
    if category == "航空运力":
        if any(k in title for k in ["新开", "新增", "加密", "恢复", "开通"]):
            return "供给增加：新航线/加密航线，关注对应目的地库存变化"
        if any(k in title for k in ["取消", "暂停", "削减", "停飞"]):
            return "供给缩减：航线减少，关注替代方案和价格波动"
        return "运力信号：关注航线运力调整对票价和库存的影响"
    if category == "酒店供应链":
        if any(k in title for k in ["开业", "新开", "入驻", "扩张", "Open", "opens"]):
            return "供给增加：新酒店/品牌入驻，关注竞争格局变化"
        if any(k in title for k in ["收购", "并购", "交易", "出售", "Acquire", "acquire",
                                      "Sale", "sale", "sell"]):
            return "资本动向：酒店资产交易，关注行业整合趋势"
        return "酒店动态：关注供应链变化和品牌布局"
    if category == "政策签证":
        if any(k in title for k in ["免签", "落地签"]):
            return "政策红利：签证便利化将刺激出境游需求"
        if any(k in title for k in ["人次", "数据", "统计"]):
            return "宏观指标：反映旅游市场整体恢复程度"
        return "政策变化：关注对业务合规和需求的影响"
    if category == "会展活动":
        return "集中需求：大型活动将带来阶段性客流和住宿需求"
    return ""


# ============================================================
# Main
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("  上游产业链信息采集 v1.0")
    print("  日期: %s" % TODAY)
    print("=" * 60)

    all_results = []

    print("\n--- 高优先级采集 ---")
    all_results.extend(collect_xinhua_travel())
    all_results.extend(collect_mct_news())
    all_results.extend(collect_routesonline())
    all_results.extend(collect_hotelnews())
    all_results.extend(collect_flightglobal())

    print("\n--- 受限源尝试 ---")
    all_results.extend(collect_traveldaily())

    # Dedup + fill impact
    print("\n" + "=" * 60)
    print("  后处理: 去重 + 补impact")

    final_results = []
    seen_keys = set()
    for r in all_results:
        key = r["url"] + r["title"][:40]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        if not r["impact"]:
            r["impact"] = auto_assess_impact(r["title"], r["category"])
        final_results.append(r)

    # Write output
    output_file = os.path.join(OUTPUT_DIR, "upstream_collected_%s.json" % TODAY)
    output_data = {
        "meta": {
            "date": TODAY,
            "total_items": len(final_results),
            "working_sources": {
                "新华网旅游": "新闻标题+日期提取完整",
                "文旅部官网": "政策新闻+日期提取完整",
                "RoutesOnline": "航线话题提取",
                "HotelNewsResource": "酒店新闻标题提取",
                "FlightGlobal": "航空新闻提取 (含付费标识)",
                "环球旅讯": "JS渲染受限，仅提取静态部分",
            },
            "blocked_sources": [
                "民航局统计 (caac.gov.cn) - WAF 403",
                "携程趋势 - JS应用无法爬取",
                "移民局 (nia.gov.cn) - JS渲染",
                "Booking.com - 反爬机制",
                "LuxuryTravelAdvisor - Cloudflare 403",
                "HospitalityNet - Cloudflare 403",
            ],
        },
        "items": final_results,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Summary
    source_counts = {}
    cat_counts = {}
    for r in final_results:
        source_counts[r["source"]] = source_counts.get(r["source"], 0) + 1
        cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1

    print("\n" + "=" * 60)
    print("  采集完成! 总计 %d 条" % len(final_results))
    print("  输出: %s\n" % output_file)

    print("按来源:")
    for s, c in sorted(source_counts.items(), key=lambda x: -x[1]):
        print("  %s: %d" % (s, c))
    print("\n按类别:")
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print("  %s: %d" % (c, n))
    print()


if __name__ == "__main__":
    main()
