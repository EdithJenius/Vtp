#!/usr/bin/env python3
"""读取表格数据"""
import json, urllib.request, configparser, ssl, os

context = ssl._create_unverified_context()
config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.openclaw/config.toml"))
app_id = config["provider.feishu"]["appid"].strip('"')
app_secret = config["provider.feishu"]["appsecret"].strip('"')
body_data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
token_req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=body_data)
token_req.add_header("Content-Type", "application/json")
token_resp = urllib.request.urlopen(token_req, timeout=10, context=context)
TOKEN = ***"tenant_access_token"]

def api_call(method, url, data=None):
    headers = {"Authorization": "Bearer " + TOKEN}
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    if data: headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30, context=context) as response:
            return json.l…()))
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.fp.read().decode("utf-8")[:500]}

APP = "VWhpbyRChawykPsVr2Pc2FlRnpn"
TID = "tbl7ubjEpYYepeUj"

# 表结构
r = api_call("GET", "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables")
print("=== 所有表 ===")
for t in r.get("data",{}).get("items",[]):
    print("  " + t["name"] + " (" + t["table_id"] + ")")

# 字段
r2 = api_call("GET", "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables/" + TID + "/fields")
print("\n=== 字段 ===")
for f in r2.get("data",{}).get("items",[]):
    print("  " + f["field_name"] + " (type=" + str(f["type"]) + ")")

# 记录
r3 = api_call("GET", "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables/" + TID + "/records?page_size=5")
items = r3.get("data",{}).get("items") or []
print("\n=== 记录 (前5条) ===")
for item in items:
    fields = item.get("fields", {})
    for k, v in fields.items():
        val = str(v)[:300]
        print("  [" + k + "] " + val)
    print("  ---")
