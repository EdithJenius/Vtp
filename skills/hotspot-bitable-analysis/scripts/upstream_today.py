#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 11: 上游数据写入Bitable子表
从上游采集数据中提取旅游相关上游信息
"""
import json, os, sys, time, urllib.request, configparser

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
app_id = config['provider.feishu']['appid'].strip('"')
app_secret = config['provider.feishu']['appsecret'].strip('"')
body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=body, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']
print(f"[Token] OK")

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
    if data: headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as f:
            return json.loads(f.read().decode())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.read().decode()[:300]}

APP_TOKEN = 'AXvzbL4E5a5s3vsqqnjc7OOInRb'

# 读取上游采集数据
upstream_path = os.path.expanduser('~/.openclaw/workspace/skills/route-analysis/data/upstream_collected_2026-06-01.json')
with open(upstream_path) as f:
    upstream_data = json.load(f)

# 格式化数据
def fmt_item(item):
    source = item.get('source', '')
    title = item.get('title', '')
    impact = item.get('impact', '')
    category = item.get('category', '行业动态')
    
    # 类别映射
    category_map = {
        "政策签证": "政策签证",
        "航空运力": "航空运力",
        "酒店供应链": "酒店供应链",
        "会展活动": "会展活动",
    }
    cat = category_map.get(category, "行业动态")
    
    return {"名称": title, "类别": cat, "来源": source, "影响分析": impact, "关联热度": "上游产业链"}

all_items = []
for item in upstream_data.get('items', []):
    all_items.append(fmt_item(item))

print(f"准备插入 {len(all_items)} 条上游数据")

# 创建上游数据子表
print("\n=== 创建上游产业链数据子表 ===")
body = {"table": {
    "name": "上游产业链数据 2026-06-01 v2",
    "fields": [
        {"field_name": "名称", "type": 1},
        {"field_name": "类别", "type": 3, "property": {"options": [
            {"name": "政策签证"}, {"name": "航空运力"}, {"name": "酒店供应链"},
            {"name": "会展活动"}, {"name": "行业动态"}
        ]}},
        {"field_name": "来源", "type": 1},
        {"field_name": "影响分析", "type": 1},
        {"field_name": "关联热度", "type": 1},
    ]
}}
resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', body)
if resp.get('code') != 0:
    print(f"❌ 创建子表失败: {resp.get('msg','')[:100]}")
    sys.exit(1)
UPSTREAM_TID = resp['data']['table_id']
print(f"✅ 上游数据子表: {UPSTREAM_TID}")

# 分批次插入
batch_size = 10
inserted = 0
for i in range(0, len(all_items), batch_size):
    batch = all_items[i:i+batch_size]
    payload = {"records": [{"fields": r} for r in batch]}
    resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{UPSTREAM_TID}/records/batch_create', payload)
    if resp.get('code') == 0:
        inserted += len(batch)
    else:
        print(f"  ❌ 第{i//batch_size+1}批: {resp.get('msg','')[:80]}")
    time.sleep(0.5)

print(f"✅ 上游数据写入完成: {inserted}/{len(all_items)}")
print(f"URL: https://q7yllltm5t.feishu.cn/base/{APP_TOKEN}")
