#!/usr/bin/env python3
"""批量写入已转写视频到Bitable + 标签分析"""
import json, urllib.request, configparser, ssl, os, time

# Auth
ctx = ssl._create_unverified_context()
config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.openclaw/config.toml"))
app_id = config["provider.feishu"]["appid"].strip('"')
app_secret = config["provider.feishu"]["appsecret"].strip('"')
body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=body)
req.add_header("Content-Type", "application/json")
resp = urllib.request.urlopen(req, timeout=10, context=ctx)
TOKEN = json.loads(resp.read().decode())["tenant_access_token"]

def api(method, url, data=None):
    h = {"Authorization": "***" + TOKEN, "Content-Type": "application/json; charset=utf-8" if data else "application/json"}
    p = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    r = urllib.request.Request(url, data=p, method=method, headers=h)
    try:
        return json.loads(f.read().decode())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.fp.read().decode("utf-8")[:300]}

APP = "JbfSbQjyXaA4vssVABNcm5AhnKh"
TID = "tblvRG2jLW8SF3Pz"
TAG_TID = "tblcMEJdH6quzxg1"

# Video metadata
videos = [
    ("7243650145143770405", "我回来啦！带着目标和你们一起", 18),
    ("7327897405834136883", "进阶英专生就业指南", 30),
    ("7585864257696091430", "这个白手起家现金千万的留学生能谈吗", 92),
    ("7574432204773719974", "这个资产300亿诚觅小娇妻的留学生能谈吗", 116),
    ("7569916094288791801", "这个一天只用睡四小时的留学生能谈吗", 104),
]

# Tag context snippets for each video (based on known content)
tag_data = {
    "7243650145143770405": [
        ("A老师回归", "人物身份", "A老师回归更新"),
        ("英专生就业", "话题标签", "英专生就业话题"),
        ("多巴胺穿搭", "风格标签", "多巴胺女孩穿搭"),
        ("变装", "风格标签", "变装视频"),
    ],
    "7327897405834136883": [
        ("英专生就业", "话题标签", "英专生就业指南"),
        ("佳士得", "背景标签", "佳士得拍卖行背景"),
        ("陈良玲", "人物身份", "佳士得拍卖官陈良玲"),
        ("进阶指南", "话题标签", "英专生就业进阶指南"),
    ],
    "7585864257696091430": [
        ("白手起家", "人物身份", "白手起家现金千万的留学生"),
        ("现金千万", "价值观标签", "现金千万资产"),
        ("留学生", "人物身份", "留学生身份"),
    ],
    "7574432204773719974": [
        ("资产300亿", "人物身份", "资产300亿的留学生"),
        ("诚觅小娇妻", "情感标签", "诚觅小娇妻"),
        ("留学生", "人物身份", "留学生身份"),
    ],
    "7569916094288791801": [
        ("一天只睡四小时", "性格标签", "一天只用睡四小时"),
        ("留学生", "人物身份", "留学生身份"),
        ("精力旺盛", "性格标签", "精力旺盛"),
    ],
}

# 1. Write transcripts to main table
print("=== 写入视频文案库 ===")
for vid, title, dur in videos:
    fpath = f"/tmp/dy_tr_{vid}.txt"
    if not os.path.exists(fpath):
        print(f"⚠️ {title}: 无转写")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        transcript = f.read()
    lines = transcript.strip().split("\n")
    summary = " ".join(lines[:3])[:120]
    
    fields = {
        "视频标题": f"{title} (medium模型)",
        "视频链接": f"https://www.douyin.com/video/{vid}",
        "来源平台": "抖音", "作者": "Amber2.0",
        "时长(秒)": dur,
        "口播文案": transcript,
        "文案摘要": summary + "...",
        "备注": "faster-whisper medium模型转写"
    }
    r = api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TID}/records", {"fields": fields})
    if r.get("code") == 0:
        print(f"✅ {title}")
    else:
        print(f"❌ {title}: {r.get('msg','')[:80]}")
    time.sleep(0.2)

# 2. Tag analysis
print("\n=== 标签分析 ===")
for vid, title, dur in videos:
    tags = tag_data.get(vid, [])
    if not tags:
        continue
    fpath = f"/tmp/dy_tr_{vid}.txt"
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    for name, cat, desc in tags:
        fields = {
            "标签名称": name,
            "标签类别": cat,
            "关联视频": title,
            "关联来源": transcript[:200],
            "标签描述": desc
        }
        r = api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TAG_TID}/records", {"fields": fields})
        if r.get("code") == 0:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}: {r.get('msg','')[:60]}")
        time.sleep(0.2)

print(f"\n🔗 主表: https://q7yllltm5t.feishu.cn/base/{APP}?table={TID}")
print(f"🏷️ 标签: https://q7yllltm5t.feishu.cn/base/{APP}?table={TAG_TID}")
