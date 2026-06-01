#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3b: 将对标视频写入子表
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
        return {'code': -1, 'msg': str(e)[:80]}

APP = 'CURybXQlma9Yu0sMtUHcBw5unqd'
SUB_TID = 'tblwKXR1dSZvZuCC'

videos = [
    {"视频标题": "普通人如何去非洲Safari？需要多少钱？", "来源平台": "小红书", "作者": "拉格Lagreen", "点赞数": 1367, "关联痛点": "去非洲Safari太贵、不知道怎么规划", "视频链接": "https://www.xiaohongshu.com/search_result/69b5b613000000001a027678", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "高赞问答型，用户最关心的价格问题"},
    {"视频标题": "人均3w！非洲肯坦10天safari看动物大迁徙", "来源平台": "小红书", "作者": "跟滕老师去旅行", "点赞数": 1813, "关联痛点": "人均预算、行程是否值得、怕走错路线", "视频链接": "https://www.xiaohongshu.com/search_result/6a105fbe00000000070298f7", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "1813赞高爆款，10天行程对标参考"},
    {"视频标题": "人均3w！非洲肯坦10天safari看动物大迁徙2", "来源平台": "小红书", "作者": "跟滕老师去旅行", "点赞数": 575, "关联痛点": "坦桑尼亚段行程细节、过境问题", "视频链接": "https://www.xiaohongshu.com/search_result/6a1426aa000000000803d2ea", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "上集续篇，覆盖坦桑尼亚国家公园"},
    {"视频标题": "坦桑尼亚Safari攻略01 | 预订+准备", "来源平台": "小红书", "作者": "小小王同学", "点赞数": 249, "关联痛点": "行前准备繁琐、不知道订什么", "视频链接": "https://www.xiaohongshu.com/search_result/68eb5c9e0000000004016f4e", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "行前攻略类，收藏型内容"},
    {"视频标题": "坦桑尼亚Safari计划和报价", "来源平台": "小红书", "作者": "高山流水", "点赞数": 84, "关联痛点": "Safari报价不透明、如何选旅行社", "视频链接": "https://www.xiaohongshu.com/search_result/69faeb7300000000370348ee", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "报价对比型，转化潜力高"},
    {"视频标题": "坦桑尼亚：最狂野的国家！非洲丨动物世界", "来源平台": "小红书", "作者": "两颗太阳Show", "点赞数": 302, "关联痛点": "动物大迁徙什么季节看、去哪里看", "视频链接": "https://www.xiaohongshu.com/search_result/6937866d000000001e0114f1", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "风光种草型，画面感强"},
    {"视频标题": "大迁徙不是全年都有，第一次东非别选错月份", "来源平台": "小红书", "作者": "小易爱非洲", "点赞数": 12, "关联痛点": "第一次去东非怕选错时间、看不到动物", "视频链接": "https://www.xiaohongshu.com/search_result/6a0693b0000000003601c286", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "科普型干货，解决选时间痛点"},
    {"视频标题": "坦桑尼亚Safari费用及体验测评", "来源平台": "小红书", "作者": "Ling07", "点赞数": 6, "关联痛点": "Safari全花费、性价比对比", "视频链接": "https://www.xiaohongshu.com/search_result/6a1d1c4d0000000038036bcc", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "备注": "费用全解析"},
]

ok = 0
for v in videos:
    r = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{SUB_TID}/records',
            {'fields': v})
    if r.get('code') == 0:
        ok += 1
        print(f'  + {v["视频标题"][:20]}...', flush=True)

print(f'\n对标视频库: {ok}/{len(videos)} 条写入', flush=True)
print(f'URL: https://q7yllltm5t.feishu.cn/base/{APP}', flush=True)
