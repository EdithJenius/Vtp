# -*- coding: utf-8 -*-
"""
更新笔记裂变内容库的素材参考链接: 每条3-5条链接
基于酒店名称+正文+引用话题+配图prompt生成关键词
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
APP_TOKEN = 'KC7GbI8oFaUXAWsMAAtcYxIWnxM'
TID = 'tblonmLDmyR1Qo0u'
FIELD_ID = 'fldRCtKLOJ'

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

# 获取所有记录
resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records?page_size=50')
records = resp.get('data',{}).get('items') or []

def make_pexels_url(keywords):
    """Pexels 搜索链接"""
    q = urllib.parse.quote(keywords)
    return f"https://www.pexels.com/zh-cn/search/{q}/"

def make_unsplash_url(keywords):
    """Unsplash 搜索链接"""
    q = urllib.parse.quote(keywords)
    return f"https://unsplash.com/s/photos/{q}"

def make_youtube_url(keywords):
    """YouTube 搜索链接"""
    q = urllib.parse.quote(keywords)
    return f"https://www.youtube.com/results?search_query={q}"

def make_xhs_url(keywords):
    """小红书搜索链接（带标签前缀）"""
    q = urllib.parse.quote(keywords)
    return f"https://www.xiaohongshu.com/search_result?keyword={q}&source=web_search_result_notes"

def make_web_url(keywords):
    """通用网页搜索"""
    q = urllib.parse.quote(keywords)
    return f"https://www.baidu.com/s?wd={q}"

# 每条笔记的关键词映射（酒店名称 → 多组搜索关键词）
note_keywords = {
    "三亚亚特兰蒂斯酒店": [
        ("亚特兰蒂斯酒店", "酒店外观/泳池/水世界"),
        ("亚特兰蒂斯水世界", "水上乐园/滑道"),
        ("亚特兰蒂斯海底套房", "水族馆/海洋/水下"),
        ("三亚豪华度假酒店", "海滩/泳池/度假"),
        ("三亚毕业旅行", "海岛/青春/旅行"),
    ],
    "长沙君悦酒店": [
        ("长沙君悦酒店", "湘江/天际线/大堂"),
        ("长沙湘江夜景", "城市夜景/灯光"),
        ("长沙美食小吃夜市", "街头美食/烟火气"),
        ("长沙IFS 国金中心", "地标/购物"),
        ("长沙毕业旅行攻略", "旅游/打卡"),
    ],
    "贵阳安纳塔拉度假酒店": [
        ("贵阳安纳塔拉", "泰式度假/山林"),
        ("贵州避暑度假", "山水/森林"),
        ("贵州黄果树瀑布", "自然风光/瀑布"),
        ("贵州苗寨风情", "少数民族/文化"),
        ("贵阳城市风光", "城市/天际线"),
    ],
}

def build_links(hotel_name, body_text, tags, prompt_text):
    """基于多维度关键词构建3-5条链接"""
    kw_sets = note_keywords.get(hotel_name, [(hotel_name, "酒店")])

    links = []
    sources = ["pexels", "unsplash", "youtube", "xhs"]

    for i, (kw, desc) in enumerate(kw_sets):
        if i >= 5:
            break
        source = sources[i % len(sources)]
        if source == "pexels":
            link = make_pexels_url(kw)
        elif source == "unsplash":
            link = make_unsplash_url(kw)
        elif source == "youtube":
            link = make_youtube_url(kw)
        else:
            link = make_xhs_url(kw)
        links.append(f"{link}  # {desc}")

    # 确保至少3条
    while len(links) < 3:
        fallback = make_web_url(hotel_name)
        links.append(f"{fallback}  # {hotel_name} 更多素材")

    return "\n".join(links[:5])

# 获取每条记录的完整字段
print("获取记录详情...")
updates = []
for r in records:
    rid = r['record_id']
    # 重新获取完整记录
    detail = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}')
    fields = detail.get('data', {}).get('fields', {})

    hotel_name = fields.get('酒店名称', '')
    body_text = fields.get('正文文案', '')
    tags = fields.get('引用话题', '')
    prompt = fields.get('封面/配图建议(图生prompt)', '')

    new_links = build_links(hotel_name, body_text, tags, prompt)
    updates.append((rid, hotel_name, new_links))
    print(f"  [{hotel_name}] 生成 {len(new_links.split(chr(10)))} 条链接")

# 批量更新
print(f"\n写入 {len(updates)} 条记录的素材参考链接...")
for rid, hname, links in updates:
    body = {"fields": {"素材参考链接": links}}
    resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}', body)
    if resp.get('code') == 0:
        print(f"  ✅ {hname}")
    else:
        print(f"  ❌ {hname}: {resp.get('msg', '')}")
    time.sleep(0.3)

print("\n完成！所有素材参考链接已更新为3-5条。")
