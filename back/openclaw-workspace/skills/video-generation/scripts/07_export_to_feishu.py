#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新素材表：加入YouTube章节信息 + 时间戳链接
"""
import json, os, sys, subprocess, configparser, urllib.request, ssl, time

ctx = ssl._create_unverified_context()
c = configparser.ConfigParser()
c.read(os.path.expanduser("~/.openclaw/config.toml"))
b = json.dumps({"app_id": c["provider.feishu"]["appid"].strip("\""),
                "app_secret": c["provider.feishu"]["appsecret"].strip("\"")}).encode()
r = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                           data=b, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(r, timeout=10, context=ctx) as f:
    TOKEN = json.loads(f.read().decode())["tenant_access_token"]
print("OK", flush=True)

def api(method, url, data=None):
    h = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json; charset=utf-8"}
    p = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=p, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as f:
            return json.loads(f.read().decode())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.fp.read().decode("utf-8")[:200]}

APP = "CURybXQlma9Yu0sMtUHcBw5unqd"
MAT_TID = "tblWrFdFaVs2tUrD"
YT = "/Library/Frameworks/Python.framework/Versions/3.12/bin/yt-dlp"

def fmt(sec):
    s = int(sec or 0)
    return f"{s//60}:{s%60:02d}"

print("获取素材表...", flush=True)
resp = api("GET", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records?page_size=50")
records = resp.get("data", {}).get("items", [])
print(f"共 {len(records)} 条", flush=True)

# 收集所有YouTube链接
links = set()
for rec in records:
    u = rec.get("fields", {}).get("素材链接/路径", "")
    if "youtu" in u:
        links.add(u)

# 分析章节
cache = {}
for url in links:
    try:
        r = subprocess.run([YT, "--no-check-certificate", "--dump-json", url],
                          capture_output=True, text=True, timeout=30)
        line = r.stdout.strip().split("\n")[0]
        if line:
            d = json.loads(line)
            chs = d.get("chapters") or []
            cache[url] = {"title": str(d.get("title",""))[:50], "chs": chs}
            if chs:
                print(f"  ✓ {d.get('title','?')[:40]}... {len(chs)}章", flush=True)
    except:
        cache[url] = {"title": "?", "chs": []}
    time.sleep(0.5)

# 更新素材表
updated = 0
for rec in records:
    fields = rec.get("fields", {})
    url = fields.get("素材链接/路径", "")
    if url not in cache:
        continue
    vc = cache[url]
    chs = vc.get("chs") or []
    if not chs:
        continue
    
    # 构建备注
    note = f"📹 {vc['title']}\n📑 {len(chs)}段:\n"
    for ch in chs:
        note += f"  ⏱ {fmt(ch['start_time'])}-{fmt(ch['end_time'])} | {ch['title']}\n"
    
    # 提取视频ID
    vid = ""
    if "youtu.be/" in url:
        vid = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    elif "watch?v=" in url:
        vid = url.split("watch?v=")[1].split("&")[0]
    
    # 用第一个章节做时间戳链接
    first = chs[0]
    ts_url = f"https://youtu.be/{vid}?t={int(first['start_time'])}" if vid else url
    
    r = api("PUT", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records/{rec['record_id']}",
            {"fields": {"备注": note, "素材链接/路径": ts_url}})
    if r.get("code") == 0:
        updated += 1
    time.sleep(0.3)

print(f"更新: {updated}/{len(records)} 条", flush=True)
print(f"URL: https://q7yllltm5t.feishu.cn/base/{APP}", flush=True)
