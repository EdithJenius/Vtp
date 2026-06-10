#!/usr/bin/env python3
"""写入已完成转写的视频到Bitable"""
import json, urllib.request, configparser, ssl, os, time

context = ssl._create_unverified_context()
config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
app_id = config["provider.feishu"]["appid"].strip('"')
app_secret = config["provider.feishu"]["appsecret"].strip('"')
body_data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
token_req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=body_data)
token_req.add_header("Content-Type", "application/json")
token_resp = urllib.request.urlopen(token_req, timeout=10, context=context)
TOKEN = json.l…())["tenant_access_token"]]

def api_call(method, url, data=None):
    headers = {"Authorization": "***" + TOKEN}
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    if data: headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=30, context=context)
        return json.loads(token_resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.fp.read().decode("utf-8")[:500]}

APP = "JbfSbQjyXaA4vssVABNcm5AhnKh"
TID = "tblvRG2jLW8SF3Pz"

# Process all completed transcriptions from batch 1
videos = [
    ("7326481780477938954", "谁说英专生不好就业？You just need to be confident", 29),
    ("7641188270096786034", "全听懂的前途一片抖音", 56),
    ("7629606403158679026", "这个只能地下恋的留学生能谈吗", 134),
    ("7600341208284762030", "盘点过年相亲各类头像", 96),
    ("7597742669141432474", "这个八块腹肌愿意入赘的留学生能谈吗", 87),
]

for vid, title, dur in videos:
    fpath = f"/tmp/dy_tr_{vid}.txt"
    if not os.path.exists(fpath):
        print(f"⚠️ {title}: 无转写文件")
        continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        transcript = f.read()
    lines = transcript.strip().split("\n")
    summary = " ".join(lines[:3])[:120]
    
    fields = {
        "视频标题": f"{title} (medium模型)",
        "视频链接": f"https://www.douyin.com/video/{vid}",
        "来源平台": "抖音",
        "作者": "Amber2.0",
        "时长(秒)": dur,
        "口播文案": transcript,
        "文案摘要": summary + "...",
        "备注": "faster-whisper medium模型转写"
    }
    
    r = api_call("POST", "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables/" + TID + "/records", {"fields": fields})
    if r.get("code") == 0:
        print(f"✅ {title}")
    else:
        print(f"❌ {title}: {r.get('msg','')[:80]}")
    time.sleep(0.2)

print(f"\nDone: https://q7yllltm5t.feishu.cn/base/{APP}?table={TID}")
