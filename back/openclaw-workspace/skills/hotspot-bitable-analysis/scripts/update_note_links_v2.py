# -*- coding: utf-8 -*-
"""
重写: 更新笔记裂变内容库的素材参考链接（每条3-5条）
修正 data.record.fields 路径 + 用PQ缩写避免长行
"""
import urllib.request, json, os, configparser, urllib.parse, time

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

# 获取记录
resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records?page_size=50')
records = resp.get('data',{}).get('items') or []
print(f"共 {len(records)} 条记录")

# 多维关键词
link_sources = {
    "三亚亚特兰蒂斯必看8项隐藏福利": [
        ("Atlantis Sanya hotel", "pexels"),
        ("亚特兰蒂斯水世界", "xhs"),
        ("亚特兰蒂斯海洋套房", "baidu"),
        ("Sanya luxury resort water park", "unsplash"),
        ("亚特兰蒂斯酒店真实测评", "youtube"),
    ],
    "住进海底世界是什么体验": [
        ("underwater ocean hotel room", "pexels"),
        ("亚特兰蒂斯海底套房实拍", "xhs"),
        ("ocean view luxury suite interior", "unsplash"),
        ("三亚海底酒店入住体验", "youtube"),
        ("亚特兰蒂斯失落的空间水族馆", "baidu"),
    ],
    "亚特兰蒂斯vs艾迪逊": [
        ("亚特兰蒂斯和艾迪逊对比", "xhs"),
        ("Sanya EDITION hotel architecture", "unsplash"),
        ("三亚亚特兰蒂斯酒店全攻略", "baidu"),
        ("三亚艾迪逊酒店评测", "youtube"),
        ("三亚海棠湾酒店推荐", "pexels"),
    ],
    "三亚亚特兰蒂斯凭什么年收20亿": [
        ("亚特兰蒂斯度假综合体航拍", "xhs"),
        ("luxury resort aerial drone China", "pexels"),
        ("复星旅文 亚特兰蒂斯 营收", "baidu"),
        ("Sanya Atlantis resort complex", "unsplash"),
        ("三亚高端酒店行业分析", "youtube"),
    ],
    "毕业旅行抓紧暑期长沙房价": [
        ("长沙君悦酒店江景房", "xhs"),
        ("Grand Hyatt Changsha exterior", "pexels"),
        ("长沙五一广场周边酒店", "baidu"),
        ("Changsha city skyline night view", "unsplash"),
        ("长沙暑期旅游住宿攻略", "youtube"),
    ],
    "24h在长沙君悦": [
        ("长沙君悦酒店无边泳池", "xhs"),
        ("Grand Hyatt Changsha infinity pool", "pexels"),
        ("长沙湘江风光带夜景", "unsplash"),
        ("长沙太平街夜市美食合集", "baidu"),
        ("长沙君悦酒店入住vlog", "youtube"),
    ],
    "去之前觉得贵退房时发现赚了": [
        ("长沙君悦江景客房", "xhs"),
        ("Grand Hyatt Changsha room interior", "pexels"),
        ("长沙性价比五星酒店推荐", "baidu"),
        ("Changsha luxury hotel panoramic view", "unsplash"),
        ("长沙君悦酒店真实评价", "youtube"),
    ],
    "贵州避暑酒店为什么选安纳塔拉": [
        ("贵州安纳塔拉度假酒店", "xhs"),
        ("Anantara Guiyang mountain resort", "pexels"),
        ("贵州避暑度假酒店推荐", "baidu"),
        ("Guiyang luxury resort forest", "unsplash"),
        ("贵阳安纳塔拉酒店介绍", "youtube"),
    ],
    "在贵阳安纳塔拉躺了三天": [
        ("贵阳安纳塔拉真实入住体验", "xhs"),
        ("Guiyang Anantara resort pool", "pexels"),
        ("贵州山地度假SPA酒店", "baidu"),
        ("Mountain forest resort China", "unsplash"),
        ("贵阳安纳塔拉度假Vlog", "youtube"),
    ],
    "去贵州避暑前先看这8个问题": [
        ("贵州避暑旅游全攻略", "xhs"),
        ("Guizhou summer travel nature", "pexels"),
        ("贵州黄果树荔波小七孔", "baidu"),
        ("Guizhou green mountain landscape", "unsplash"),
        ("贵州避暑自驾游路线推荐", "youtube"),
    ],
}

def build_links(kw_sets):
    lines = []
    for kw, source in kw_sets:
        q = PQ(kw)
        if source == "pexels":
            url = f"https://www.pexels.com/zh-cn/search/{q}/"
        elif source == "unsplash":
            url = f"https://unsplash.com/s/photos/{q}"
        elif source == "youtube":
            url = f"https://www.youtube.com/results?search_query={q}"
        elif source == "xhs":
            url = f"https://www.xiaohongshu.com/search_result?keyword={q}&source=web_search_result_notes"
        else:
            url = f"https://www.baidu.com/s?wd={q}"
        lines.append(f"{url}  # [{source}] {kw}")
    return "\n".join(lines)

count = 0
for rec in records:
    fields = rec.get('fields', {})
    title = fields.get('笔记标题', '')
    rid = rec['record_id']

    matched = None
    for k in link_sources:
        if k in title:
            matched = k
            break

    if matched:
        links = build_links(link_sources[matched])
        resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}',
                   {"fields": {"素材参考链接": links}})
        if resp.get('code') == 0:
            count += 1
            print(f"  ✅ [{title[:22]}] {len(link_sources[matched])}条")
        else:
            print(f"  ❌ [{title[:22]}] {resp.get('msg','')}")
        time.sleep(0.3)
    else:
        print(f"  ⚠️ [{title[:22]}] 未匹配")

print(f"\n完成！更新 {count}/{len(records)} 条，各3-5条链接")
print("来源: Pexels / Unsplash / YouTube / 小红书 / 百度")
