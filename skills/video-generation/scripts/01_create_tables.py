#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为坦桑尼亚剪辑自动化创建5个子表（对标视频库/痛点分析/讲解流程/文案产出/素材匹配）
"""
import json, os, urllib.request, configparser, sys

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
        return {'code': -1, 'msg': str(e)[:100]}

APP = 'CURybXQlma9Yu0sMtUHcBw5unqd'

def create_table(name, fields):
    resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables',
               {'table': {'name': name, 'fields': fields}})
    if resp.get('code') == 0:
        tid = resp['data']['table_id']
        print(f'  + {name}: {tid}', flush=True)
        return tid
    else:
        print(f'  X {name}: {resp.get("msg","")[:60]}', flush=True)
        return None

print('创建子表...', flush=True)

t1 = create_table('① 对标视频库', [
    {'field_name': '视频标题', 'type': 1},
    {'field_name': '来源平台', 'type': 3, 'property': {'options': [{'name': '小红书'}, {'name': '抖音'}]}},
    {'field_name': '作者', 'type': 1},
    {'field_name': '点赞数', 'type': 2},
    {'field_name': '关联痛点', 'type': 1},
    {'field_name': '视频链接', 'type': 1},
    {'field_name': '关联产品', 'type': 1},
    {'field_name': '备注', 'type': 1},
])

t2 = create_table('② 痛点分析', [
    {'field_name': '痛点描述', 'type': 1},
    {'field_name': '来源视频', 'type': 1},
    {'field_name': '目标人群', 'type': 1},
    {'field_name': '解决方案', 'type': 1},
    {'field_name': '关联产品', 'type': 1},
    {'field_name': '优先级', 'type': 3, 'property': {'options': [{'name': '高'}, {'name': '中'}, {'name': '低'}]}},
])

t3 = create_table('③ 讲解流程', [
    {'field_name': '流程步骤', 'type': 2},
    {'field_name': '环节标题', 'type': 1},
    {'field_name': '核心内容', 'type': 1},
    {'field_name': '对应痛点', 'type': 1},
    {'field_name': '建议画面', 'type': 1},
    {'field_name': '关联产品', 'type': 1},
])

t4 = create_table('④ 文案产出', [
    {'field_name': '文案标题', 'type': 1},
    {'field_name': '口播正文', 'type': 1},
    {'field_name': '版本', 'type': 1},
    {'field_name': '时长预估', 'type': 1},
    {'field_name': '风格定位', 'type': 1},
    {'field_name': '关联产品', 'type': 1},
    {'field_name': '状态', 'type': 3, 'property': {'options': [{'name': '待审核'}, {'name': '已通过'}, {'name': '需修改'}]}},
])

t5 = create_table('⑤ 素材匹配', [
    {'field_name': '镜头编号', 'type': 2},
    {'field_name': '画面描述', 'type': 1},
    {'field_name': '对应文案', 'type': 1},
    {'field_name': '素材来源', 'type': 1},
    {'field_name': '素材链接/路径', 'type': 1},
    {'field_name': '是否已下载', 'type': 3, 'property': {'options': [{'name': '是'}, {'name': '否'}]}},
    {'field_name': '关联产品', 'type': 1},
])

print(f'\nURL: https://q7yllltm5t.feishu.cn/base/{APP}', flush=True)
