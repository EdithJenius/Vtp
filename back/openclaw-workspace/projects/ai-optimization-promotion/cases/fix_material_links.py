#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复素材匹配表的链接为可搜索链接
"""
import json, os, urllib.request, configparser, sys, time

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
MAT_TID = 'tblWrFdFaVs2tUrD'

resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records?page_size=50')
records = resp.get('data', {}).get('items', [])
print(f'获取 {len(records)} 条', flush=True)

updates = {
    "塞伦盖蒂草原航拍全景（开场）": "https://www.xiaohongshu.com/search_result?keyword=塞伦盖蒂 航拍",
    "角马过马拉河实拍（天河之渡）": "https://www.xiaohongshu.com/search_result?keyword=角马过河 马拉河",
    "动物大迁徙时间线动画/信息图": "https://www.xiaohongshu.com/search_result?keyword=动物大迁徙 月份 时间",
    "塔兰吉雷猴面包树+象群": "https://www.xiaohongshu.com/search_result?keyword=Tarangire 大象 猴面包树",
    "恩戈罗恩戈罗火山口全景+狮子": "https://www.xiaohongshu.com/search_result?keyword=Ngorongoro 火山口 狮子",
    "塞伦盖蒂大草原上的斑马角马群": "https://www.xiaohongshu.com/search_result?keyword=塞伦盖蒂 斑马 角马",
    "草原野奢酒店房间/帐篷内部": "https://www.xiaohongshu.com/search_result?keyword=Singita 野奢 帐篷",
    "行前准备清单卡片式排版": "https://www.xiaohongshu.com/search_result?keyword=非洲Safari 行前准备",
    "Safari越野车+向导实拍": "https://www.xiaohongshu.com/search_result?keyword=非洲Safari 越野车",
    "夕阳下的塞伦盖蒂金色草原": "https://www.xiaohongshu.com/search_result?keyword=塞伦盖蒂 日落",
}

fixed = 0
for rec in records:
    rid = rec['record_id']
    desc = rec.get('fields', {}).get('画面描述', '')
    if desc in updates:
        url = updates[desc]
        r = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records/{rid}',
                {'fields': {'素材链接/路径': url, '素材来源': '小红书'}})
        if r.get('code') == 0:
            fixed += 1
            print(f'  + {desc[:16]}...', flush=True)
        time.sleep(0.3)

print(f'修复: {fixed}/{len(records)}', flush=True)
