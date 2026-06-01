#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改Bitable权限：
- 互联网获得链接的可查看（阅读权限）
- 永乐有管理权
- 记录设置方法以备后续统一使用
"""
import json, os, urllib.request, configparser

def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appid'].strip('"')
    app_secret = config['provider.feishu']['appsecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_token()
print(f"[Token] OK")

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8') if data is not None else None
    if data is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as f:
            return json.loads(f.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')[:500]
        return {"code": e.code, "msg": err_body}

APP_TOKEN = 'AXvzbL4E5a5s3vsqqnjc7OOInRb'

# 1. 查看当前公开权限
print("\n=== 当前公开权限 ===")
r = api('GET', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/public?type=bitable')
print(json.dumps(r, ensure_ascii=False, indent=2)[:800])

# 2. 设置公开权限 - 任何人可阅读（仅链接可查看）
# link_share_entity = "anyone_readable" 表示获得链接的任何人可阅读
# security_entity = "anyone_can_view" 表示任何人可查看
print("\n=== 设置公开权限：获得链接可阅读 ===")
perm_data = {
    "external_access_entity": "open",
    "security_entity": "anyone_can_view",
    "comment_entity": "anyone_can_view",
    "share_entity": "anyone_can_view",
    "link_share_entity": "anyone_readable",
    "invite_external": True
}
r2 = api('PATCH', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/public?type=bitable', perm_data)
print(f"结果: code={r2.get('code')}, msg={r2.get('msg','')[:200]}")

if r2.get('code') != 0:
    # 如果PATCH失败，可能某些字段不支持，尝试逐个设置
    print("\n=== 尝试逐个字段设置 ===")
    for key, val in perm_data.items():
        r3 = api('PATCH', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/public?type=bitable', {key: val})
        print(f"  {key}={val}: code={r3.get('code')}")

# 3. 查看当前协作者
print("\n=== 当前协作者列表 ===")
r4 = api('GET', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/members?type=bitable')
print(json.dumps(r4, ensure_ascii=False, indent=2)[:1000])

# 4. 确认永乐有管理权 - 先查用户open_id
# 永乐用的是这个飞书账号，查一下当前账号信息
print("\n=== 获取永乐的用户信息 ===")
r5 = api('GET', 'https://open.feishu.cn/open-apis/user/v1/me')
print(json.dumps(r5, ensure_ascii=False, indent=2)[:500])

print("\n=== 完成 ===")
print(f"Bitable: https://q7yllltm5t.feishu.cn/base/{APP_TOKEN}")
