#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 7: 素材匹配 — 文案每个镜头对应的素材
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

materials = [
    {"镜头编号": 1, "画面描述": "塞伦盖蒂草原航拍全景（开场）", "对应文案": "你猜去一趟坦桑尼亚Safari要花多少钱？", "素材来源": "小红书搜索'塞伦盖蒂 航拍'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 2, "画面描述": "角马过马拉河实拍（天河之渡）", "对应文案": "角马过马拉河这种场面，错过了就得等一年", "素材来源": "小红书搜索'角马过河 马拉河'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 3, "画面描述": "动物大迁徙时间线动画/信息图", "对应文案": "7-9月是黄金期，其他月份看点不一样", "素材来源": "AI生成/自行制作", "素材链接/路径": "需制作", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 4, "画面描述": "塔兰吉雷猴面包树+象群", "对应文案": "塔兰吉雷看大象群和猴面包树", "素材来源": "小红书搜索'Tarangire 大象'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 5, "画面描述": "恩戈罗恩戈罗火山口全景+狮子", "对应文案": "恩戈罗恩戈罗火山口追狮子犀牛", "素材来源": "小红书搜索'Ngorongoro 火山口'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 6, "画面描述": "塞伦盖蒂大草原上的斑马角马群", "对应文案": "塞伦盖蒂连住几天深度Safari", "素材来源": "小红书搜索'塞伦盖蒂 safari'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 7, "画面描述": "草原野奢酒店房间/帐篷内部", "对应文案": "野奢帐篷里配浴缸，推开窗就是长颈鹿", "素材来源": "小红书搜索'Singita 野奢酒店'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 8, "画面描述": "行前准备清单卡片式排版", "对应文案": "电子签提前两周办，黄热病疫苗提前10天打", "素材来源": "AI生成/自行制作", "素材链接/路径": "需制作", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 9, "画面描述": "Safari越野车+向导实拍", "对应文案": "越野车是不是4x4，有没有顶棚可以站起来看", "素材来源": "小红书搜索'非洲safari 越野车'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"镜头编号": 10, "画面描述": "夕阳下的塞伦盖蒂金色草原", "对应文案": "夕阳把整片天空染成金色，每一分钱都值", "素材来源": "小红书搜索'塞伦盖蒂 日落'", "素材链接/路径": "待搜索下载", "是否已下载": "否", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
]

ok = 0
for m in materials:
    r = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{MAT_TID}/records', {'fields': m})
    if r.get('code') == 0: ok += 1
    time.sleep(0.2)

print(f'素材匹配: {ok}/{len(materials)} 条写入', flush=True)
print(f'URL: https://q7yllltm5t.feishu.cn/base/{APP}', flush=True)
