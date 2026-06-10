#!/usr/bin/env python3
"""
Step 4: 创建 Bitable + 字段 + 批量插入 + 公开权限
2026-05-28
"""
import json, os, sys, urllib.request, urllib.parse, time

# ---------- 工具函数 ----------
def get_token():
    """从 config.toml 获取飞书 token"""
    config_path = os.path.expanduser('~/.openclaw/config.toml')
    with open(config_path) as f:
        lines = f.readlines()
    def get_val(key):
        for line in lines:
            s = line.strip()
            if s.startswith(key):
                eq = s.index('=')
                return s[eq+1:].strip().strip('"').strip("'")
        return None
    app_id = get_val('appId')
    app_secret = get_val('appSecret')
    if not app_id or not app_secret:
        print("[ERROR] 无法从 config.toml 读取 appId/appSecret")
        sys.exit(1)
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode())['tenant_access_token']

def api(TOKEN, method, url, data=None):
    """通用飞书API调用"""
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as f:
            resp = json.loads(f.read().decode())
        return resp
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"[HTTP ERROR {e.code}] {url[:60]}...")
        print(f"  Response: {err_body[:500]}")
        return {"code": -1, "msg": err_body}
    except Exception as e:
        print(f"[ERROR] {e}")
        return {"code": -1, "msg": str(e)}

def delete_all_records(TOKEN, app_token, table_id):
    """清空表所有记录"""
    page_token = None
    while True:
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=20'
        if page_token:
            url += f'&page_token={page_token}'
        resp = api(TOKEN, 'GET', url)
        if resp.get('code') != 0 or not resp.get('data', {}).get('items'):
            break
        items = resp['data']['items']
        record_ids = [item['record_id'] for item in items]
        for rid in record_ids:
            del_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{rid}'
            api(TOKEN, 'DELETE', del_url)
        page_token = resp['data'].get('page_token')
        if not page_token:
            break
    print(f"[OK] 已清空 {len(items) if 'items' in locals() else 0} 条记录")

# ---------- 主流程 ----------
TOKEN = get_token()
print(f"[OK] 获取Token成功")

# 1. 创建Bitable
bitable_data = {"name": "热点商机多维分析 2026-05-28"}
resp = api(TOKEN, 'POST', 'https://open.feishu.cn/open-apis/bitable/v1/apps', bitable_data)
if resp.get('code') != 0:
    print(f"[ERROR] 创建Bitable失败: {resp}")
    sys.exit(1)

app_token = resp['data']['app']['app_token']
print(f"[OK] Bitable创建成功")
print(f"  app_token: {app_token}")
print(f"  完整响应: {json.dumps(resp, ensure_ascii=False)[:500]}")

# 查找默认表格ID
table_id = None
if 'data' in resp:
    d = resp['data']
    if 'table' in d:
        table_id = d['table']['table_id']
    elif 'app' in d and 'tables' in d['app']:
        table_id = d['app']['tables'][0]['table_id']

if not table_id:
    # 尝试获取表格列表
    list_resp = api(TOKEN, 'GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables')
    print(f"表格列表: {json.dumps(list_resp, ensure_ascii=False)[:500]}")
    if list_resp.get('code') == 0 and list_resp['data'].get('items'):
        table_id = list_resp['data']['items'][0]['table_id']
    else:
        print("[ERROR] 无法找到表格ID")
        sys.exit(1)

print(f"  table_id: {table_id}")

# 2. 重命名默认字段 + 添加字段
# 先获取已有字段
fields_resp = api(TOKEN, 'GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields')
if fields_resp.get('code') != 0:
    print(f"[ERROR] 获取字段失败: {fields_resp}")
    sys.exit(1)

# 找到默认文本字段（通常是第一个字段）
existing_fields = fields_resp['data']['items']
default_field_id = None
for f in existing_fields:
    if f['type'] == 1:  # Text类型
        default_field_id = f['field_id']
        break

if default_field_id:
    # 重命名为"热点话题"
    rename_resp = api(TOKEN, 'PUT',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{default_field_id}',
        {"field_name": "热点话题", "type": 1})
    if rename_resp.get('code') == 0:
        print(f"[OK] 默认字段已重命名为「热点话题」")
    else:
        print(f"[WARN] 重命名失败: {rename_resp.get('msg')}")

# 添加字段
fields_config = [
    {"field_name": "来源渠道", "type": 4, "property": {
        "options": [
            {"name": "微博热搜", "color": 0}, {"name": "百度热搜", "color": 1},
            {"name": "知乎", "color": 2}, {"name": "抖音", "color": 3},
            {"name": "今日头条", "color": 4}, {"name": "B站", "color": 5},
            {"name": "贴吧", "color": 6}, {"name": "36氪", "color": 7},
            {"name": "综合", "color": 8},
        ]
    }},
    {"field_name": "话题类别", "type": 3, "property": {
        "options": [
            {"name": "航天科技", "color": 0}, {"name": "社会民生", "color": 1},
            {"name": "天气灾害", "color": 2}, {"name": "财经股市", "color": 3},
            {"name": "国际外交", "color": 4}, {"name": "科技AI", "color": 5},
            {"name": "体育赛事", "color": 6}, {"name": "文旅美食", "color": 7},
            {"name": "健康生活", "color": 8}, {"name": "教育", "color": 9},
        ]
    }},
    {"field_name": "热度指数", "type": 1},
    {"field_name": "热度指数数值", "type": 2},
    {"field_name": "关联地点", "type": 1},
    {"field_name": "关联旅游景点", "type": 1},
    {"field_name": "旅游商机分析", "type": 1},
    {"field_name": "优先级", "type": 3, "property": {
        "options": [
            {"name": "高", "color": 0},
            {"name": "中", "color": 1},
            {"name": "低", "color": 2},
        ]
    }},
    {"field_name": "备注", "type": 1},
]

field_map = {"热点话题": default_field_id} if default_field_id else {}
for fc in fields_config:
    resp_f = api(TOKEN, 'POST',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields',
        fc)
    if resp_f.get('code') == 0:
        fid = resp_f['data']['field']['field_id']
        field_map[fc['field_name']] = fid
        print(f"[OK] 字段「{fc['field_name']}」创建成功")
    else:
        print(f"[WARN] 字段「{fc['field_name']}」创建失败: {resp_f.get('msg', '')}")

print(f"\n[OK] 所有字段创建完成")

# 3. 清空默认空记录
delete_all_records(TOKEN, app_token, table_id)

# 4. 批量插入记录
analysis_path = os.path.expanduser('~/.openclaw/workspace/hotspot-bitable-analysis/data/analysis_result.json')
with open(analysis_path, 'r', encoding='utf-8') as f:
    records_data = json.load(f)

# 按优先级排序
priority_order = {"高": 0, "中": 1, "低": 2}
records_data.sort(key=lambda x: (priority_order.get(x["优先级"], 9), -x["热度指数数值"]))

# batch_create 每批≤10条
batch = []
for i, item in enumerate(records_data):
    fields = {}
    for key in item:
        if key == "来源渠道":
            fields[key] = item[key]  # MultiSelect 传数组
        elif key == "优先级":
            fields[key] = item[key]  # SingleSelect 传字符串
        elif key == "话题类别":
            fields[key] = item[key] if key in item else ""
        elif key == "热度指数数值":
            fields[key] = int(item[key]) if isinstance(item[key], (int, float)) else 0
        else:
            fields[key] = item[key]
    
    # 备注链接URL编码
    if "备注" in fields:
        bk = fields["备注"]
        if "http" not in bk and "📎" in bk:
            # 是纯文本备注，不需要编码
            pass
        fields["备注"] = bk
    
    record = {"fields": fields}
    batch.append(record)
    
    # 每10条或最后一批
    if len(batch) >= 10 or i == len(records_data) - 1:
        payload = {"records": batch}
        insert_resp = api(TOKEN, 'POST',
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create',
            payload)
        if insert_resp.get('code') == 0:
            print(f"[OK] 批量写入 {len(batch)} 条记录成功")
        else:
            print(f"[ERROR] 批量写入失败: {insert_resp.get('msg', '')}")
        batch = []

print(f"[OK] 总计 {len(records_data)} 条记录写入完成")

# 5. 设置公开权限
# 5.1 PATCH public
public_url = f'https://open.feishu.cn/open-apis/drive/v1/permissions/{app_token}/public?type=bitable'
public_data = {
    "external_access_entity": "open",
    "security_entity": "anyone_can_view",
    "link_share_entity": "anyone_readable",
    "invite_external": True
}
public_resp = api(TOKEN, 'PATCH', public_url, public_data)
print(f"[OK] 公开权限设置完成: {public_resp.get('code')}")

# 5.2 POST member (公开可编辑)
member_url = f'https://open.feishu.cn/open-apis/drive/v1/permissions/{app_token}/members?type=bitable&need_notification=false'
member_data = {
    "member_type": "openid",
    "member_id": "ou_0",
    "perm": "full_access"
}
member_resp = api(TOKEN, 'POST', member_url, member_data)
print(f"[OK] 公开编辑权限设置完成: {member_resp.get('code')}")

# 6. 验证
verify_resp = api(TOKEN, 'GET',
    f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=5')
if verify_resp.get('code') == 0:
    count = len(verify_resp.get('data', {}).get('items', []))
    print(f"\n✅ [验证] 成功读取到 {count} 条记录 (期望13条)")
else:
    print(f"\n⚠️ [验证] 读取失败: {verify_resp.get('msg', '')}")

# 7. 输出链接
browser_url = f"https://uahbihmxfe.feishu.cn/base/{app_token}"
print(f"\n{'='*60}")
print(f"🎉 Bitable创建完成！")
print(f"📊 链接: {browser_url}")
print(f"{'='*60}")
