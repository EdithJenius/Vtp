# -*- coding: utf-8 -*-
"""获取笔记库表ID和记录"""
import urllib.request, json, os, configparser

def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appId'].strip('"')
    app_secret = config['provider.feishu']['appSecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_token()
APP_TOKEN = 'KC7GbI8oFaUXAWsMAAtcYxIWnxM'

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

# 找笔记库的表ID+所有字段
resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables?page_size=50')
for t in resp.get('data',{}).get('items',[]):
    if '笔记裂变内容库' in t['name']:
        TID = t['table_id']
        print(f"笔记库: {t['name']} -> {TID}")

        # 获取所有字段ID
        fields_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/fields')
        for f in fields_resp.get('data',{}).get('items',[]):
            print(f"  字段: {f['field_name']} -> {f['field_id']} type={f['type']}")

        # 获取所有记录
        records_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records?page_size=50')
        items = records_resp.get('data',{}).get('items') or []
        print(f"\n记录数: {len(items)}")
        for r in items:
            fs = r['fields']
            print(f"  [{r['record_id']}] 标题={fs.get('笔记标题','')[:30]} | 酒店={fs.get('酒店名称','')}")
