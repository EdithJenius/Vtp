#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feishu_utils.py - 飞书 API 公共模块
所有 Bitable 操作的公共工具函数
"""
import json, os, urllib.request, urllib.parse

CONFIG_PATH = os.path.expanduser('~/.openclaw/config.toml')

def _get_val(key):
    with open(CONFIG_PATH) as f:
        for line in f:
            s = line.strip()
            if s.startswith(key):
                eq = s.index('=')
                return s[eq+1:].strip().strip('"').strip("'")
    return None

def get_token():
    """获取飞书 tenant_access_token"""
    app_id = _get_val('appId')
    app_secret = _get_val('appSecret')
    if not app_id or not app_secret:
        raise RuntimeError("无法读取 appId/appSecret")
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as f:
        return json.loads(f.read().decode())['tenant_access_token']

def api(TOKEN, method, url, data=None, retries=3):
    """通用飞书 API 调用（带重试）"""
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }
    body = json.dumps(data).encode() if data else None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=15) as f:
                return json.loads(f.read().decode())
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:200]
            if attempt < retries - 1 and e.code in (429, 500, 502, 503):
                import time
                time.sleep(2 ** attempt)
                continue
            return {"code": e.code, "msg": err}
        except Exception as e:
            if attempt < retries - 1:
                import time
                time.sleep(2 ** attempt)
                continue
            return {"code": -1, "msg": str(e)[:200]}
    return {"code": -1, "msg": "Max retries"}

def get_all_records(TOKEN, app_token, table_id):
    """获取表内所有记录"""
    records = []
    page_token = None
    while True:
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=50'
        if page_token:
            url += f'&page_token={page_token}'
        r = api(TOKEN, 'GET', url)
        items = r.get('data', {}).get('items', [])
        if not items:
            break
        records.extend(items)
        page_token = r.get('data', {}).get('page_token')
        if not page_token:
            break
    return records

def delete_record(TOKEN, app_token, table_id, record_id):
    """删除单条记录"""
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}'
    return api(TOKEN, 'DELETE', url)

def delete_all_records(TOKEN, app_token, table_id):
    """清空表内所有记录"""
    records = get_all_records(TOKEN, app_token, table_id)
    for r in records:
        delete_record(TOKEN, app_token, table_id, r['record_id'])
    return len(records)

def batch_insert(TOKEN, app_token, table_id, records, batch_size=10):
    """批量插入记录，自动分批"""
    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        payload = {"records": [{"fields": r} for r in batch]}
        resp = api(TOKEN, 'POST',
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create',
            payload)
        if resp.get('code') == 0:
            total += len(batch)
        else:
            print(f"[ERR] 批量写入第{i//batch_size+1}批失败: {resp.get('msg','')[:80]}")
    return total

def update_record(TOKEN, app_token, table_id, record_id, fields):
    """更新单条记录"""
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}'
    return api(TOKEN, 'PUT', url, {"fields": fields})
