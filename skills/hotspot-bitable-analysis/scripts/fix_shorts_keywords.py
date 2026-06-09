# -*- coding: utf-8 -*-
"""修复YouTube Shorts关键词：中文→英文"""
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
PQ = urllib.parse.quote
APP_TOKEN = 'KC7GbI8oFaUXAWsMAAtcYxIWnxM'
TID = 'tblonmLDmyR1Qo0u'

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

# 只更新shorts源：中文→英文关键词
shorts_fixes = {
    'recvm0xyOGs1p9': 'Atlantis Sanya water park tour',
    'recvm0xyOG93ho': 'underwater hotel room ocean',
    'recvm0xyOGr7ZR': 'Sanya EDITION vs Atlantis hotel',
    'recvm0xyOG8wjT': 'Atlantis Sanya resort tour',
    'recvm0xyOGbj9r': 'Grand Hyatt Changsha hotel tour',
    'recvm0xyOGME84': 'Changsha travel vlog Grand Hyatt',
    'recvm0xyOGtFo5': 'Grand Hyatt Changsha review',
    'recvm0xyOGftJa': 'Anantara Guiyang resort tour',
    'recvm0xyOGnrof': 'Guiyang resort travel vlog',
    'recvm0xyOGwmmV': 'Guizhou China travel guide',
}

count = 0
for rid, eng_kw in shorts_fixes.items():
    # 先GET现有链接
    resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}')
    old_links = resp.get('data',{}).get('record',{}).get('fields',{}).get('素材参考链接', '')
    
    # 替换shorts行
    lines = old_links.split('\n')
    new_lines = []
    for line in lines:
        if '[YouTube Shorts]' in line:
            q = PQ(eng_kw)
            new_lines.append(f'https://www.youtube.com/results?search_query={q}&sp=CAMSBAgEEAE%253D  # [YouTube Shorts] {eng_kw}')
        else:
            new_lines.append(line)
    
    new_links = '\n'.join(new_lines)
    resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}',
               {'fields': {'素材参考链接': new_links}})
    if resp.get('code') == 0:
        count += 1
        print(f'✅ {rid[:20]} → {eng_kw}')
    else:
        print(f'❌ {rid} → {resp.get("msg","")}')
    time.sleep(0.3)

print(f'\n修复完成: {count}/10 条 Shorts 关键词已换为英文')
