#!/usr/bin/env python3
"""合并甘孜两个子表"""
import json, urllib.request, os, configparser, sys, time

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId'].strip('"')
APP_SECRET = config['provider.feishu']['appSecret'].strip('"')

body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=body, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']
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

# Find tables
tables = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables?page_size=20')
target_tid = None
source_tid = None

for t in tables.get('data', {}).get('items', []):
    name = t['name']
    if '甘孜' in name and '822' in name:
        target_tid = t['table_id']
        print(f"[Target] {name}")
    elif name == '甘孜·稻城亚丁景区事件':
        source_tid = t['table_id']
        print(f"[Source] {name}")

if not target_tid or not source_tid:
    print("ERROR: tables not found")
    sys.exit(1)

# Read source
src = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables/{source_tid}/records?page_size=50')
src_items = src.get('data', {}).get('items') or []
print(f"[Source] {len(src_items)} records")

# Get target field names
tf = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables/{target_tid}/fields')
target_fnames = {f['field_name'] for f in tf.get('data', {}).get('items', [])}
print(f"[Target] Fields: {target_fnames}")

# Map and insert
records = []
for item in src_items:
    mapped = {}
    for k, v in item.get('fields', {}).items():
        if k in target_fnames:
            mapped[k] = v
    if mapped:
        records.append(mapped)

print(f"[Merge] Adding {len(records)} records")

for i in range(0, len(records), 10):
    batch = records[i:i+10]
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables/{target_tid}/records/batch_create'
    payload = json.dumps({"records": [{"fields": r} for r in batch]}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST',
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req) as f:
        result = json.loads(f.read().decode())
    n = len(result.get('data', {}).get('records', []))
    print(f"  Batch {i//10+1}: {n}")
    time.sleep(0.3)

# Delete source
api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables/{source_tid}')
print("[Delete] Source table removed")

# Verify
final = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables/{target_tid}/records?page_size=50')
total = final.get('data', {}).get('total', 0)
print(f"\n[Verify] 合并后记录数: {total}条 ✅")
