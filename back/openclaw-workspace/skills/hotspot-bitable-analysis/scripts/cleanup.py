#!/usr/bin/env python3
"""清理调试残留表"""
import json, urllib.request, os, configparser

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId'].strip('"')
APP_SECRET = open(os.path.expanduser('~/.openclaw/config.toml'), 'r').read()
# Parse appSecret manually
import re
match = re.search(r'appSecret\s*=\s*"([^"]+)"', APP_SECRET)
if match:
    APP_SECRET = match.group(1)
else:
    print("ERROR: could not parse appSecret")
    exit(1)

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

tables = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables?page_size=20')
for t in tables.get('data', {}).get('items', []):
    name = t['name']
    tid = t['table_id']
    if name in ('测试子表2', '测试子表3'):
        api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN}/tables/{tid}')
        print(f"[Delete] {name}")

print("Cleanup done")
