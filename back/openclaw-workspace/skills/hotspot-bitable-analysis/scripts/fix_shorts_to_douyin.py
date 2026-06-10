# -*- coding: utf-8 -*-
"""替换YouTube Shorts → 抖音搜索"""
import urllib.request, urllib.parse, json, os, configparser, time

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser('~/.openclaw/config.toml'))
aid = cfg['provider.feishu']['appId'].strip('"')
sec = cfg['provider.feishu']['appSecret'].strip('"')
bd = json.dumps({"app_id": aid, "app_secret": sec}).encode()
rq = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=bd, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(rq) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']

APP_TOKEN = 'KC7GbI8oFaUXAWsMAAtcYxIWnxM'
TID = 'tblonmLDmyR1Qo0u'
PQ = urllib.parse.quote

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records?page_size=50')
records = resp.get('data',{}).get('items') or []

douyin_kw = {
    'recvm0xyOGs1p9': '三亚亚特兰蒂斯酒店攻略',
    'recvm0xyOG93ho': '亚特兰蒂斯海底套房',
    'recvm0xyOGr7ZR': '三亚亚特兰蒂斯vs艾迪逊',
    'recvm0xyOG8wjT': '三亚亚特兰蒂斯航拍',
    'recvm0xyOGbj9r': '长沙君悦酒店住宿',
    'recvm0xyOGME84': '长沙君悦酒店vlog',
    'recvm0xyOGtFo5': '长沙君悦酒店入住体验',
    'recvm0xyOGftJa': '贵阳安纳塔拉度假酒店',
    'recvm0xyOGnrof': '贵阳安纳塔拉入住体验',
    'recvm0xyOGwmmV': '贵州避暑旅游攻略',
}

count = 0
for rec in records:
    rid = rec['record_id']
    fields = rec.get('fields', {})
    old_links = fields.get('素材参考链接', '')

    kw = douyin_kw.get(rid)
    if not kw:
        continue

    lines = old_links.split('\n')
    new_lines = []
    for line in lines:
        if '[YouTube Shorts]' in line:
            q = PQ(kw)
            new_lines.append(f'https://www.douyin.com/search/{q}  # [抖音] {kw}')
        else:
            new_lines.append(line)

    new_links = '\n'.join(new_lines)
    resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}',
               {'fields': {'素材参考链接': new_links}})
    if resp.get('code') == 0:
        count += 1
        print(f'✅ {kw}')
    else:
        print(f'❌ {rid}')
    time.sleep(0.3)

print(f'\n完成: {count}/10 条 Shorts → 抖音')
