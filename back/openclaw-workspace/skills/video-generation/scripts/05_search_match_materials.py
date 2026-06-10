#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube素材搜索+关键词匹配+写入Bitable
"""
import json, os, sys, subprocess, configparser, urllib.request, time

YT = "/Library/Frameworks/Python.framework/Versions/3.12/bin/yt-dlp"

def get_token():
    import ssl
    ctx = ssl._create_unverified_context()
    c = configparser.ConfigParser()
    c.read(os.path.expanduser('~/.openclaw/config.toml'))
    b = json.dumps({"app_id": c["provider.feishu"]["appid"].strip('"'),
                     "app_secret": c["provider.feishu"]["appsecret"].strip('"')}).encode()
    r = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=b, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=10, context=ctx) as f:
        return json.loads(f.read().decode())["tenant_access_token"]

TOKEN = get_token()
print("OK", flush=True)

def api(method, url, data=None):
    h = {"Authorization": f"Bearer {TOKEN}"}
    if data is not None:
        h["Content-Type"] = "application/json; charset=utf-8"
    p = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    r = urllib.request.Request(url, data=p, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=15) as f:
            return json.loads(f.read().decode())
    except Exception as e:
        return {"code": -1, "msg": str(e)[:80]}

APP = "CURybXQlma9Yu0sMtUHcBw5unqd"
MAT_TID = "tblWrFdFaVs2tUrD"

keywords = [
    "Serengeti Tanzania 4K aerial",
    "Serengeti wildebeest migration river crossing",
    "Tarangire elephants baobab trees",
    "Ngorongoro crater landscape",
    "African safari luxury lodge tent camp",
    "Serengeti sunset golden hour",
    "Safari jeep guide Tanzania",
    "Tanzania travel essentials packing",
]

all_vids = []
for kw in keywords:
    try:
        r = subprocess.run([YT, "--no-check-certificate", "--flat-playlist",
                            f"ytsearch5:{kw}", "--dump-json"],
                           capture_output=True, text=True, timeout=30)
        for line in r.stdout.strip().split("\n"):
            if line.strip():
                try:
                    d = json.loads(line)
                    all_vids.append({"title": d.get("title",""), "id": d.get("id",""),
                                     "url": f"https://youtu.be/{d.get('id','')}", "kw": kw})
                except: pass
    except: pass
    time.sleep(0.5)

print(f"搜到 {len(all_vids)} 条", flush=True)

scene_kw = {
    "塞伦盖蒂草原航拍全景（开场）": ["Serengeti","aerial","landscape"],
    "角马过马拉河实拍（天河之渡）": ["wildebeest","migration","river","crossing"],
    "塔兰吉雷猴面包树+象群": ["Tarangire","elephants","baobab"],
    "恩戈罗恩戈罗火山口全景+狮子": ["Ngorongoro","crater","lions"],
    "塞伦盖蒂大草原上的斑马角马群": ["Serengeti","wildebeest","zebra","herd"],
    "草原野奢酒店房间/帐篷内部": ["safari","lodge","luxury","tent"],
    "Safari越野车+向导实拍": ["safari","jeep","guide","vehicle"],
    "夕阳下的塞伦盖蒂金色草原": ["Serengeti","sunset","golden","hour"],
    "行前准备清单卡片式排版": ["travel","packing","tips","essentials"],
    "动物大迁徙时间线动画/信息图": ["migration","documentary","wildebeest"],
}

matched = []
for scene, kws in scene_kw.items():
    scores = []
    for v in all_vids:
        t = v["title"].lower()
        s = sum(1 for kw in kws if kw.lower() in t)
        if s > 0:
            scores.append((s, v))
    scores.sort(key=lambda x: x[0], reverse=True)
    for s, v in scores[:3]:
        matched.append({"镜头编号": len(matched)+1, "画面描述": scene,
                        "对应文案": v["title"][:50], "素材来源": "YouTube",
                        "素材链接/路径": v["url"], "是否已下载": "否",
                        "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"})

print(f"匹配 {len(matched)} 条", flush=True)

old = api("GET", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records?page_size=50")
for item in (old.get("data",{}).get("items") or []):
    api("DELETE", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records/{item['record_id']}")

ok = 0
for i in range(0, len(matched), 10):
    batch = matched[i:i+10]
    r = api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records/batch_create",
            {"records": [{"fields": x} for x in batch]})
    if r.get("code") == 0: ok += len(batch)
    time.sleep(0.3)

print(f"写入: {ok}/{len(matched)}", flush=True)
print(f"URL: https://q7yllltm5t.feishu.cn/base/{APP}", flush=True)
