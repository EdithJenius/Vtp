# -*- coding: utf-8 -*-
"""替换素材参考链接: 竖屏素材源（Pexels/Unsplash/小红书/Pinterest/YouTubeShorts）"""
import urllib.request, urllib.parse, json, os, configparser, time

def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appId'].strip('"')
    app_secret = config['provider.feishu']['appSecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_token()
APP_TOKEN = 'KC7GbI8oFaUXAWsMAAtcYxIWnxM'
TID = 'tblonmLDmyR1Qo0u'
PQ = urllib.parse.quote

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

all_links = {
    'recvm0xyOGs1p9': [
        ('Atlantis Sanya hotel exterior', 'pexels'),
        ('三亚亚特兰蒂斯水世界攻略', 'xhs'),
        ('亚特兰蒂斯酒店全景', 'pinterest'),
        ('亚特兰蒂斯失落的空间水族馆', 'shorts'),
        ('Sanya Atlantis resort luxury', 'unsplash'),
    ],
    'recvm0xyOG93ho': [
        ('underwater hotel bedroom ocean', 'pexels'),
        ('亚特兰蒂斯海底套房实拍测评', 'xhs'),
        ('海底套房 水族馆景观', 'pinterest'),
        ('海底套房入住体验', 'shorts'),
        ('underwater aquarium luxury hotel', 'unsplash'),
    ],
    'recvm0xyOGr7ZR': [
        ('三亚艾迪逊酒店泳池', 'pexels'),
        ('亚特兰蒂斯vs艾迪逊 怎么选', 'xhs'),
        ('EDITION hotel Sanya design', 'pinterest'),
        ('三亚海棠湾酒店对比', 'shorts'),
        ('Sanya EDITION hotel architecture', 'unsplash'),
    ],
    'recvm0xyOG8wjT': [
        ('aerial view luxury resort Sanya', 'pexels'),
        ('三亚亚特兰蒂斯酒店航拍', 'xhs'),
        ('奢华度假酒店设计', 'pinterest'),
        ('三亚亚特兰蒂斯酒店揭秘', 'shorts'),
        ('Sanya Atlantis resort aerial', 'unsplash'),
    ],
    'recvm0xyOGbj9r': [
        ('长沙君悦酒店夜景', 'pexels'),
        ('长沙君悦酒店入住真实体验', 'xhs'),
        ('长沙君悦酒店 interior', 'pinterest'),
        ('长沙暑期旅游住宿攻略', 'shorts'),
        ('Grand Hyatt Changsha night view', 'unsplash'),
    ],
    'recvm0xyOGME84': [
        ('长沙君悦酒店无边泳池', 'pexels'),
        ('长沙君悦酒店 湘江景观', 'xhs'),
        ('长沙网红酒店打卡', 'pinterest'),
        ('长沙君悦酒店一日vlog', 'shorts'),
        ('Changsha Grand Hyatt infinity pool', 'unsplash'),
    ],
    'recvm0xyOGtFo5': [
        ('长沙君悦酒店客房江景', 'pexels'),
        ('长沙君悦值不值得住', 'xhs'),
        ('长沙五星级酒店性价比', 'pinterest'),
        ('长沙君悦酒店入住实测', 'shorts'),
        ('luxury hotel room with river view', 'unsplash'),
    ],
    'recvm0xyOGftJa': [
        ('mountain resort Guiyang China', 'pexels'),
        ('贵阳安纳塔拉度假体验', 'xhs'),
        ('贵州避暑酒店推荐', 'pinterest'),
        ('贵阳安纳塔拉入住实拍', 'shorts'),
        ('Anantara Guiyang forest resort', 'unsplash'),
    ],
    'recvm0xyOGnrof': [
        ('贵阳安纳塔拉度假酒店泳池', 'pexels'),
        ('贵阳安纳塔拉真实入住', 'xhs'),
        ('贵州山地度假酒店', 'pinterest'),
        ('贵阳安纳塔拉度假vlog', 'shorts'),
        ('mountain spa resort Guizhou', 'unsplash'),
    ],
    'recvm0xyOGwmmV': [
        ('Guizhou green mountain waterfall', 'pexels'),
        ('贵州避暑旅游全攻略', 'xhs'),
        ('贵州黄果树瀑布', 'pinterest'),
        ('贵州避暑自驾游攻略', 'shorts'),
        ('Guizhou nature landscape China', 'unsplash'),
    ],
}

def build(kw_sets):
    lines = []
    for kw, src in kw_sets:
        q = PQ(kw)
        if src == 'pexels':
            lines.append(f'https://www.pexels.com/zh-cn/search/{q}/  # [Pexels] {kw}')
        elif src == 'unsplash':
            lines.append(f'https://unsplash.com/s/photos/{q}  # [Unsplash] {kw}')
        elif src == 'shorts':
            lines.append(f'https://www.youtube.com/results?search_query={q}&sp=CAMSBAgEEAE%253D  # [YouTube Shorts] {kw}')
        elif src == 'xhs':
            lines.append(f'https://www.xiaohongshu.com/search_result?keyword={q}&source=web_search_result_notes  # [小红书] {kw}')
        elif src == 'pinterest':
            lines.append(f'https://www.pinterest.com/search/pins/?q={q}  # [Pinterest] {kw}')
    return chr(10).join(lines)

count = 0
for rid, kw_sets in all_links.items():
    links = build(kw_sets)
    resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}',
               {'fields': {'素材参考链接': links}})
    if resp.get('code') == 0:
        count += 1
        srcs = ', '.join(set(s for _, s in kw_sets))
        print(f'✅ {count} → {srcs}')
    else:
        print(f'❌ {rid} → {resp.get("msg","")}')
    time.sleep(0.3)

print(f'\n更新完成: {count}/10 条')
print('来源分布: Pexels + Unsplash + 小红书 + Pinterest + YouTube Shorts（竖屏）')
