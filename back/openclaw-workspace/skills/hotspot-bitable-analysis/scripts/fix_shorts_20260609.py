# -*- coding: utf-8 -*-
"""修正YouTube Shorts链接格式"""
import urllib.request, urllib.parse, json, os, configparser, time

def get_auth_token():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.expanduser('~/.openclaw/config.toml'))
    aid = cfg['provider.feishu']['appId'].strip('"')
    sec = cfg['provider.feishu']['appSecret'].strip('"')
    bd = json.dumps({"app_id": aid, "app_secret": sec}).encode()
    rq = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=bd, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(rq) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_auth_token()
APP_TOKEN = 'K-C7Gb-I8oFaUXAWsMAAtcYxIWnxM'.replace('-', '')
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

shorts_kw = {
    'recvm0xyOGs1p9': 'Atlantis Sanya water park tour',
    'recvm0xyOG93ho': 'underwater hotel room ocean',
    'recvm0xyOGr7ZR': 'Sanya luxury resort comparison',
    'recvm0xyOG8wjT': 'Atlantis Sanya resort tour',
    'recvm0xyOGbj9r': 'Grand Hyatt Changsha hotel tour',
    'recvm0xyOGME84': 'Changsha travel vlog',
    'recvm0xyOGtFo5': 'luxury hotel review China',
    'recvm0xyOGftJa': 'Anantara Guiyang resort',
    'recvm0xyOGnrof': 'Guiyang China travel vlog',
    'recvm0xyOGwmmV': 'Guizhou China travel guide',
}

count = 0
for rec in records:
    rid = rec['record_id']
    fields = rec.get('fields', {})
    old_links = fields.get('素材参考链接', '')

    eng = shorts_kw.get(rid)
    if not eng:
        continue

    lines = old_links.split('\n')
    new_lines = []
    for line in lines:
        if '[YouTube Shorts]' in line:
            q = PQ(eng)
            new_lines.append(f'https://www.youtube.com/results?search_query={q}&sp=EgIoAQ%253D%253D  # [YouTube Shorts] {eng}')
        else:
            new_lines.append(line)

    new_links = '\n'.join(new_lines)
    resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}',
               {'fields': {'素材参考链接': new_links}})
    if resp.get('code') == 0:
        count += 1
        print(f'OK {eng[:30]}')
    else:
        print(f'FAIL {rid}')
    time.sleep(0.3)

print(f'Done: {count}')
