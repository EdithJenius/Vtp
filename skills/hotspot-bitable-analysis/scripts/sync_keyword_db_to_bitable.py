# -*- coding: utf-8 -*-
"""用关键词库重写所有笔记链接 + 同步使用状态"""
import urllib.request, urllib.parse, json, os, configparser, sys, time

sys.path.insert(0, os.path.dirname(__file__))
from keyword_db import KeywordDB

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser('~/.openclaw/config.toml'))
aid = cfg['provider.feishu']['appId'].strip('"')
sec = cfg['provider.feishu']['appSecret'].strip('"')
bd = json.dumps({"app_id": aid, "app_secret": sec}).encode()
rq = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=bd, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(rq) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']

# 从本地JSON读取APP_TOKEN
tokens_path = os.path.join(os.path.dirname(__file__), '..', 'references', 'bitable_tokens.json')
with open(tokens_path, 'r') as f:
    tokens_data = json.load(f)
APP_TOKEN = tokens_data['bitable_token']

TID = 'tblonmLDmyR1Qo0u'

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records?page_size=50')
records = resp.get('data',{}).get('items') or []

db = KeywordDB()

title_angle_map = {
    "三亚亚特兰蒂斯必看8项隐藏福利": "干货/清单流",
    "住进海底世界是什么体验": "情绪种草流",
    "亚特兰蒂斯vs艾迪逊 毕业选哪个": "测评对比流",
    "三亚亚特兰蒂斯凭什么年收20亿": "行业分析流",
    "毕业旅行抓紧！暑期长沙房价马上翻倍": "截流紧迫感流",
    "24h在长沙君悦 纯吃纯玩vlog": "Vlog日程流",
    "去之前觉得贵 退房时发现赚了": "反差点评流",
    "贵州避暑酒店为什么选安纳塔拉": "科普涨知识流",
    "在贵阳安纳塔拉躺了三天 说说真实的体验": "真实UGC流",
    "去贵州避暑前先看这8个问题": "问答攻略流",
}

print("=== 步骤1: 标记已使用品类 → 关键词库 ===")
for rec in records:
    fields = rec.get('fields', {})
    title = fields.get('笔记标题', '')
    hotel = fields.get('酒店名称', '')
    angle = next((a for nt, a in title_angle_map.items() if nt in title), None)
    if angle and hotel:
        ok = db.mark_used(hotel, angle, title)
        if ok:
            print(f"  [ok] {hotel} -> {angle}")

print("\n=== 步骤2: 用关键词库重写所有素材链接 ===")
for rec in records:
    rid = rec['record_id']
    fields = rec.get('fields', {})
    title = fields.get('笔记标题', '')
    hotel = fields.get('酒店名称', '')
    angle = next((a for nt, a in title_angle_map.items() if nt in title), None)
    if not angle:
        angle = db.suggest_angles(title, hotel)
    if not angle:
        print(f"  [?] {title[:20]} 无法匹配品类")
        continue
    links = db.build_links(hotel, angle)
    if not links:
        print(f"  [?] {title[:20]} 关键词为空")
        continue
    resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}',
               {"fields": {"素材参考链接": links}})
    if resp.get('code') == 0:
        print(f"  [ok] {title[:20]} {angle} - 5条")
    else:
        print(f"  [xx] {title[:20]} {resp.get('msg','')}")
    time.sleep(0.3)

print("\n=== 步骤3: 品类缺口分析 ===")
for g in db.find_gaps():
    print(f"  {g['hotel']}: {g['used_count']}/10 -> 还剩 {g['unused_count']} 个品类")

print("\n完成！")
