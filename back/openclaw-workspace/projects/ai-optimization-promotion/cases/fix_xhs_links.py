#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复小红书链接：search_result 格式 → explore 格式
"""
import json, os, urllib.request, configparser, sys, re, time

def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appid'].strip('"')
    app_secret = config['provider.feishu']['appsecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_token()
print("TOKEN_OK", flush=True)

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
    if data: headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as f:
            return json.loads(f.read().decode())
    except Exception as e:
        return {'code': -1, 'msg': str(e)[:80]}

APP = 'CURybXQlma9Yu0sMtUHcBw5unqd'
SUB_TID = 'tblwKXR1dSZvZuCC'

# 获取所有记录
resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{SUB_TID}/records?page_size=50')
records = resp.get('data', {}).get('items', [])

print(f'获取到 {len(records)} 条记录', flush=True)

fixed = 0
for rec in records:
    rid = rec['record_id']
    fields = rec.get('fields', {})
    
    # 获取现有链接
    old_url = fields.get('视频链接', '')
    
    if 'search_result' in old_url:
        # 从 URL 中提取 note_id
        match = re.search(r'search_result/([a-f0-9]+)', old_url)
        if match:
            note_id = match.group(1)
            new_url = f'https://www.xiaohongshu.com/explore/{note_id}'
            
            # 更新记录
            r = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{SUB_TID}/records/{rid}',
                    {'fields': {'视频链接': new_url}})
            if r.get('code') == 0:
                fixed += 1
                print(f'  ✅ {note_id[:12]}... → explore', flush=True)
            else:
                print(f'  ❌ {note_id[:12]}... → {r.get("msg","")[:40]}', flush=True)
            time.sleep(0.3)
        else:
            print(f'  ⚠️ 无法提取note_id: {old_url[:40]}...', flush=True)
    else:
        print(f'  - 无需修复: {old_url[:30]}...', flush=True)

print(f'\n修复完成: {fixed}/{len(records)} 条', flush=True)
