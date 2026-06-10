#!/usr/bin/env python3
"""写入剩余10个视频 + 标签分析"""
import json, urllib.request, configparser, ssl, os, time

context = ssl._create_unverified_context()
config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.openclaw/config.toml"))
app_id = config["provider.feishu"]["appid"].strip('"')
app_secret = config["provider.feishu"]["appsecret"].strip('"')
body_data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
token_req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=body_data)
token_req.add_header("Content-Type", "application/json")
token_resp = urllib.request.urlopen(token_req, timeout=10, context=context)
TOKEN = json.loads(token_resp.read().decode())["tenant_access_token"]

def api(method, url, data=None):
    h = {"Authorization": "Bearer " + TOKEN}
    p = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    if data: h["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=p, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30, context=context) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.fp.read().decode("utf-8")[:500]}

APP = "JbfSbQjyXaA4vssVABNcm5AhnKh"
TID = "tblvRG2jLW8SF3Pz"
TAG_TID = "tblcMEJdH6quzxg1"

videos = [
    ("7568779188992563630", "这个热爱亚洲文化反向留学的留学生能谈吗", 108, "small"),
    ("7565144136114949275", "这个彩礼88万孩子随你姓的留学生能谈吗", 122, "small"),
    ("7564376835179132774", "这个愿意给你买买买的留学生能谈吗", 99, "small"),
    ("7560653219988278554", "", 92, "small"),
    ("7558146581414546726", "", 98, "small"),
    ("7555786602259025179", "", 90, "small"),
    ("7555425425188572426", "", 96, "small"),
    ("7555047527575211315", "", 95, "tiny"),
    ("7554723620577594675", "这个靠兼职就能月入十万的留学生能谈吗", 98, "tiny"),
    ("7553956690300292390", "这个愿意给你买买买的留学生能谈吗", 80, "tiny"),
]

# Known titles for some
titles_map = {
    "7560653219988278554": "",
    "7558146581414546726": "",
    "7555786602259025179": "",
    "7555425425188572426": "",
    "7555047527575211315": "",
}

# Tags for remaining videos
tag_data = {
    "7568779188992563630": [("反向留学","人物身份","热爱亚洲文化反向留学"),("留学生","人物身份","留学生身份"),("亚洲文化","话题标签","热爱亚洲文化")],
    "7565144136114949275": [("彩礼88万","价值观标签","彩礼88万孩子随你姓"),("留学生","人物身份","留学生身份"),("婚恋观","话题标签","彩礼和孩子姓氏观念")],
    "7564376835179132774": [("买买买","价值观标签","愿意给你买买买"),("留学生","人物身份","留学生身份"),("大方","性格标签","愿意为伴侣花钱")],
    "7554723620577594675": [("兼职月入十万","人物身份","靠兼职月入十万的留学生"),("留学生","人物身份","留学生身份"),("经济独立","价值观标签","经济独立能力")],
    "7553956690300292390": [("愿意买买买","价值观标签","愿意给你买买买"),("留学生","人物身份","留学生身份"),("大方","性格标签","消费观念大方")],
}

print("=== 写入视频文案库 ===")
for vid, title, dur, model_name in videos:
    fpath = f"/tmp/dy_tr_{vid}.txt"
    if not os.path.exists(fpath):
        print(f"WARN: {vid} no transcript")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        transcript = f.read()
    if not transcript.strip():
        print(f"WARN: {vid} empty transcript")
        continue
    lines = transcript.strip().split("\n")
    summary = " ".join(lines[:3])[:120]
    
    record_title = title or f"能谈吗系列 ({vid[:8]}...)"
    fields = {
        "视频标题": f"{record_title} ({model_name}模型)",
        "视频链接": f"https://www.douyin.com/video/{vid}",
        "来源平台": "抖音", "作者": "Amber2.0",
        "时长(秒)": dur,
        "口播文案": transcript,
        "文案摘要": summary + "...",
        "备注": f"faster-whisper {model_name}模型转写"
    }
    r = api("POST", "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables/" + TID + "/records", {"fields": fields})
    if r.get("code") == 0:
        print(f"OK: {record_title}")
    else:
        print(f"FAIL: {record_title}: {r.get('msg','')[:80]}")
    time.sleep(0.2)

# Tag analysis
print("\n=== 标签分析 ===")
for vid, title, dur, model_name in videos:
    tags = tag_data.get(vid, [])
    if not tags:
        continue
    fpath = f"/tmp/dy_tr_{vid}.txt"
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    record_title = title or f"能谈吗系列 ({vid[:8]}...)"
    for name, cat, desc in tags:
        fields = {"标签名称": name, "标签类别": cat, "关联视频": record_title,
                  "关联来源": transcript[:300], "标签描述": desc}
        r = api("POST", "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables/" + TAG_TID + "/records", {"fields": fields})
        if r.get("code") == 0:
            print(f" OK: {name}")
        else:
            print(f" FAIL: {name}: {r.get('msg','')[:60]}")
        time.sleep(0.2)

print("\nDone! https://q7yllltm5t.feishu.cn/base/" + APP + "?table=" + TID)
