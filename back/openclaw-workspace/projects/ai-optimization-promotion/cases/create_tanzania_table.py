#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为坦桑尼亚行程产品创建 Bitale 表格
基于肯尼亚行程文档的结构模板
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
        return {"code": e.code, "msg": e.read().decode('utf-8')[:300]}

# ===== 1. 创建产品库 Bitable =====
print("\n=== 创建坦桑尼亚行程产品库 ===")
resp = api('POST', 'https://open.feishu.cn/open-apis/bitable/v1/apps',
           {"name": "坦桑尼亚行程产品库 2026"})
if resp.get('code') != 0:
    print(f"❌ 创建失败: {resp.get('msg','')[:100]}")
    exit(1)

APP_TOKEN = resp['data']['app']['app_token']
PROD_TID = resp['data']['app']['default_table_id']
print(f"✅ 产品库创建: {APP_TOKEN}")
print(f"   URL: https://q7yllltm5t.feishu.cn/base/{APP_TOKEN}")

# 查看默认字段
fields_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{PROD_TID}/fields')
existing = fields_resp.get('data', {}).get('items', [])
print(f"   默认字段: {len(existing)}个")

# ===== 2. 配置产品表字段 =====
# 重命名文本字段
text_field = next((f for f in existing if f['field_name'] == '文本'), None)
if text_field:
    api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{PROD_TID}/fields/{text_field["field_id"]}',
        {"field_name": "产品名称", "type": 1})
    print("   ✅ 文本→产品名称")

# 删除多余默认字段
for fname in ['单选', '日期', '附件']:
    f = next((x for x in existing if x['field_name'] == fname), None)
    if f:
        api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{PROD_TID}/fields/{f["field_id"]}')

# 创建产品表字段
prod_fields = [
    {"field_name": "目的地", "type": 1},
    {"field_name": "天数", "type": 2},
    {"field_name": "出发地", "type": 1},
    {"field_name": "航班信息", "type": 1},
    {"field_name": "价格区间", "type": 1},
    {"field_name": "适用季节", "type": 1},
    {"field_name": "费用包含", "type": 1},
    {"field_name": "费用不含", "type": 1},
    {"field_name": "自费项目", "type": 1},
    {"field_name": "温馨提示", "type": 1},
    {"field_name": "状态", "type": 3, "property": {"options": [
        {"name": "已确认"}, {"name": "待确认"}, {"name": "已过期"}
    ]}},
]
for fd in prod_fields:
    r = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{PROD_TID}/fields', fd)
    mark = "✅" if r.get('code') == 0 else "❌"
    print(f"   {mark} {fd['field_name']}")

# 删除空记录
init_recs = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{PROD_TID}/records?page_size=50')
for item in (init_recs.get('data', {}).get('items') or []):
    api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{PROD_TID}/records/{item["record_id"]}')

# ===== 3. 创建行程明细子表 =====
print("\n=== 创建行程明细子表 ===")
sub_body = {"table": {
    "name": "行程明细",
    "fields": [
        {"field_name": "关联产品", "type": 1},  # 手动关联产品名
        {"field_name": "第几天", "type": 2},
        {"field_name": "行程安排", "type": 1},
        {"field_name": "早餐", "type": 1},
        {"field_name": "午餐", "type": 1},
        {"field_name": "晚餐", "type": 1},
        {"field_name": "住宿酒店", "type": 1},
        {"field_name": "活动亮点", "type": 1},
        {"field_name": "备注", "type": 1},
    ]
}}
resp2 = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', sub_body)
if resp2.get('code') == 0:
    SUB_TID = resp2['data']['table_id']
    print(f"✅ 行程明细子表: {SUB_TID}")
else:
    print(f"❌ 创建失败: {resp2.get('msg','')[:100]}")

# ===== 4. 设置公开权限 =====
print("\n=== 设置权限 ===")
# 逐个字段设置
perm_items = [
    ("link_share_entity", "anyone_readable"),
    ("security_entity", "anyone_can_view"),
    ("comment_entity", "anyone_can_view"),
]
for key, val in perm_items:
    r = api('PATCH', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/public?type=bitable',
            {key: val})
    print(f"   {key}={val}: code={r.get('code')}")

# 设置用户为管理员
user_id = "ou_b098a77a8b7869d14ccd6e34b7af3583"
r = api('PUT', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/members/{user_id}?type=bitable&need_notification=false',
        {"member_type": "openid", "perm": "full_access"})
print(f"   管理员权限: code={r.get('code')}")

print(f"\n{'='*60}")
print(f"✅ 完成!")
print(f"坦桑尼亚行程产品库: https://q7yllltm5t.feishu.cn/base/{APP_TOKEN}")
print(f"产品表ID: {PROD_TID}")
print(f"行程明细表ID: {SUB_TID}")
print(f"{'='*60}")
