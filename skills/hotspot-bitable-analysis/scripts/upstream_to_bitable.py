#!/usr/bin/env python3
"""
上游数据写入 Bitable 子表
"""
import json, urllib.request, os, sys, time
import configparser

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId'].strip('"')
APP_SECRET = open('/Users/edy/.openclaw/config.toml').read()
import re
m = re.search(r'appSecret\s*=\s*"([^"]+)"', APP_SECRET)
if m:
    APP_SECRET = m.group(1)
else:
    print("ERROR: can't parse secret"); exit(1)

body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=body, headers={'Content-Type': 'application/json'})
content = urllib.request.urlopen(req).read().decode()
TOKEN = json.loads(content)['tenant_access_token']
print(f"[Token] OK")

MAIN = "ZdpRbPT2qaGsBvsqiNucQX1Knwh"

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    if data:
        payload = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        payload = None
    r = urllib.request.Request(url, data=payload, method=method, headers=headers)
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode())

# 创建子表
table_name = "上游产业链情报·2026-05-29"
body_data = {"table": {"name": table_name, "fields": [
    {"field_name": "热点话题", "type": 1},
    {"field_name": "来源渠道", "type": 4, "property": {"options": [
        {"name": "综合"}, {"name": "环球旅讯"}, {"name": "新华网旅游"},
        {"name": "文旅部"}, {"name": "民航局"}, {"name": "RoutesOnline"},
        {"name": "HotelNewsResource"}, {"name": "FlightGlobal"}
    ]}},
    {"field_name": "话题类别", "type": 3, "property": {"options": [
        {"name": "航空运力"}, {"name": "酒店供应链"}, {"name": "政策签证"},
        {"name": "会展活动"}, {"name": "文旅美食"}, {"name": "国际外交"}
    ]}},
    {"field_name": "热度指数", "type": 1},
    {"field_name": "旅游商机分析", "type": 1},
    {"field_name": "优先级", "type": 3, "property": {"options": [
        {"name": "高"}, {"name": "中"}, {"name": "低"}
    ]}},
    {"field_name": "备注", "type": 1},
]}}
resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables', body_data)
TID = resp['data']['table_id']
print(f"[Table] Created: {table_name} -> {TID}")

# 读取上游数据
with open('/Users/edy/.openclaw/workspace/skills/hotspot-bitable-analysis/data/upstream_feeder_2026-05-29.json') as f:
    raw = json.load(f)

items = raw['items']
print(f"[Data] {len(items)} records to insert")

# 过滤字段到表字段
fields_map = {"热点话题", "来源渠道", "话题类别", "热度指数", "旅游商机分析", "优先级", "备注"}

# 分批插入
inserted = 0
for i in range(0, len(items), 10):
    batch = items[i:i+10]
    records = []
    for item in batch:
        r = {k: v for k, v in item.items() if k in fields_map and v}
        records.append({"fields": r})
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables/{TID}/records/batch_create'
    payload = json.dumps({"records": records}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST',
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json; charset=utf-8'})
    try:
        resp2 = urllib.request.urlopen(req)
        result = json.loads(resp2.read())
        n = len(result.get('data', {}).get('records', []))
        inserted += n
        print(f"  Batch {i//10+1}: {n}")
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:200]
        print(f"  Batch {i//10+1}: Error {e.code}: {err}")
    time.sleep(0.3)

print(f"\n[Insert] Total: {inserted}/{len(items)}")
print(f"URL: https://bytedance.feishu.cn/base/{MAIN}")
