# -*- coding: utf-8 -*-
"""创建酒店关键词库 + 用差异化关键词重写所有素材链接"""
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
PQ = urllib.parse.quote

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

# =============================================
# 酒店关键词库：每家酒店5套差异化关键词组合
# =============================================
# 每套5条链接, 来源: pexels/unsplash/xhs/pinterest/douyin
# 每家酒店4套, 对应4篇笔记的不同角度

keyword_repo = {
    "三亚亚特兰蒂斯酒店": {
        "angle_干货": [
            ("亚特兰蒂斯 酒店 隐藏攻略", "xhs"),
            ("Atlantis Sanya hotel guide tips", "pexels"),
            ("三亚亚特兰蒂斯 水世界 游玩", "douyin"),
            ("Sanya luxury resort aerial view", "unsplash"),
            ("亚特兰蒂斯 度假村 航拍", "pinterest"),
        ],
        "angle_种草": [
            ("亚特兰蒂斯 海底套房 梦幻", "xhs"),
            ("underwater hotel room luxury", "pexels"),
            ("亚特兰蒂斯 水族馆 鲨鱼 海底", "douyin"),
            ("ocean aquarium bedroom design", "unsplash"),
            ("海底酒店 水族馆 打卡", "pinterest"),
        ],
        "angle_测评": [
            ("亚特兰蒂斯 艾迪逊 对比测评", "xhs"),
            ("EDITION Sanya hotel design", "pexels"),
            ("三亚 亚特兰蒂斯 vs 艾迪逊", "douyin"),
            ("modern minimalist hotel architecture", "unsplash"),
            ("三亚 海棠湾 酒店 对比", "pinterest"),
        ],
        "angle_行业": [
            ("复星旅文 亚特兰蒂斯 营收", "xhs"),
            ("luxury resort business model", "pexels"),
            ("三亚 亚特兰蒂斯 年收入 揭秘", "douyin"),
            ("resort complex architecture design", "unsplash"),
            ("度假酒店 商业模式 分析", "pinterest"),
        ],
    },
    "长沙君悦酒店": {
        "angle_截流": [
            ("长沙君悦 江景房 入住攻略", "xhs"),
            ("Grand Hyatt Changsha river view", "pexels"),
            ("长沙 君悦酒店 暑期 价格", "douyin"),
            ("Changsha skyline night cityscape", "unsplash"),
            ("长沙 湘江 高端酒店 推荐", "pinterest"),
        ],
        "angle_日程": [
            ("长沙 君悦酒店 24小时 vlog", "xhs"),
            ("Changsha city travel itinerary", "pexels"),
            ("长沙 君悦酒店 一日游 攻略", "douyin"),
            ("infinity pool rooftop city view", "unsplash"),
            ("长沙 五一广场 太平街 夜市", "pinterest"),
        ],
        "angle_反差": [
            ("长沙君悦 性价比 真实体验", "xhs"),
            ("luxury hotel room panoramic window", "pexels"),
            ("长沙 君悦酒店 值不值 测评", "douyin"),
            ("night view city skyline luxury", "unsplash"),
            ("高端酒店 性价比 测评 推荐", "pinterest"),
        ],
        "angle_通用": [
            ("长沙君悦 高空酒吧 湘江", "xhs"),
            ("Grand Hyatt Changsha lobby bar", "pexels"),
            ("长沙 君悦 下午茶 泳池", "douyin"),
            ("urban luxury hotel interior design", "unsplash"),
            ("长沙 国金中心 IFS 打卡", "pinterest"),
        ],
    },
    "贵阳安纳塔拉度假酒店": {
        "angle_科普": [
            ("贵阳安纳塔拉 泰式 度假介绍", "xhs"),
            ("Anantara Guiyang Thai resort", "pexels"),
            ("贵州 安纳塔拉 避暑 度假村", "douyin"),
            ("mountain forest luxury resort", "unsplash"),
            ("泰式度假酒店 贵州 推荐", "pinterest"),
        ],
        "angle_真实": [
            ("贵阳安纳塔拉 真实入住 评价", "xhs"),
            ("mountain pool resort China", "pexels"),
            ("贵阳 安纳塔拉 体验 优缺点", "douyin"),
            ("Guizhou green mountain landscape", "unsplash"),
            ("贵阳 周边 度假 民宿 对比", "pinterest"),
        ],
        "angle_问答": [
            ("贵州避暑 旅游 攻略 行前", "xhs"),
            ("Guizhou travel summer cool", "pexels"),
            ("贵州 避暑 自驾 暑假 亲子", "douyin"),
            ("misty mountain bamboo forest", "unsplash"),
            ("贵州 黄果树 荔波 苗寨", "pinterest"),
        ],
        "angle_通用": [
            ("安纳塔拉 SPA 贵州 山景", "xhs"),
            ("Anantara spa treatment room", "pexels"),
            ("贵阳 安纳塔拉 泳池 下午茶", "douyin"),
            ("tropical resort infinity waterfall", "unsplash"),
            ("贵州 高端 度假 酒店 小众", "pinterest"),
        ],
    },
}

# 笔记内容角度映射：标题 → angle_key
title_to_angle = {
    "三亚亚特兰蒂斯必看8项隐藏福利": "angle_干货",
    "住进海底世界是什么体验": "angle_种草",
    "亚特兰蒂斯vs艾迪逊 毕业选哪个": "angle_测评",
    "三亚亚特兰蒂斯凭什么年收20亿": "angle_行业",
    "毕业旅行抓紧！暑期长沙房价马上翻倍": "angle_截流",
    "24h在长沙君悦 纯吃纯玩vlog": "angle_日程",
    "去之前觉得贵 退房时发现赚了": "angle_反差",
    "贵州避暑酒店为什么选安纳塔拉": "angle_科普",
    "在贵阳安纳塔拉躺了三天 说说真实的体验": "angle_真实",
    "去贵州避暑前先看这8个问题": "angle_问答",
}

# 获取笔记库记录
TID = 'tblonmLDmyR1Qo0u'
resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records?page_size=50')
records = resp.get('data',{}).get('items') or []
print(f"获取到 {len(records)} 条笔记记录")

# =============================================
# 创建「酒店关键词库」子表
# =============================================
print("\n=== 创建酒店关键词库子表 ===")

kw_fields = [
    {"field_name": "酒店名称", "type": 1},
    {"field_name": "内容角度", "type": 1},
    {"field_name": "关键词组合", "type": 1},
    {"field_name": "关联笔记标题", "type": 1},
]

body = {"table": {"name": "酒店关键词库", "fields": kw_fields}}
resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', body)
kw_tid = resp['data']['table_id']
print(f"关键词库表创建: {kw_tid}")

# 填充关键词表
kw_records = []
for hotel, angles in keyword_repo.items():
    for angle_key, sets in angles.items():
        # 找关联笔记
        related_note = ""
        for nt, ak in title_to_angle.items():
            if ak == angle_key and hotel in nt or (hotel == "三亚亚特兰蒂斯酒店" and "亚特兰蒂斯" in nt and ak == angle_key):
                related_note = nt
            elif hotel == "长沙君悦酒店" and "君悦" in nt and ak == angle_key:
                related_note = nt
            elif hotel == "贵阳安纳塔拉度假酒店" and "安纳塔拉" in nt and ak == angle_key:
                related_note = nt

        kw_lines = []
        for kw, src in sets:
            kw_lines.append(f"[{src}] {kw}")
        kw_records.append({
            "fields": {
                "酒店名称": hotel,
                "内容角度": angle_key.replace("angle_", ""),
                "关键词组合": "\n".join(kw_lines),
                "关联笔记标题": related_note,
            }
        })

# batch写入
for i in range(0, len(kw_records), 10):
    batch = kw_records[i:i+10]
    resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{kw_tid}/records/batch_create', {"records": batch})
    if resp.get('code') == 0:
        print(f"  关键词表写入批次 {i//10+1}: {len(batch)}条")
    time.sleep(0.3)
print(f"关键词库完成: {len(kw_records)} 条")

# =============================================
# 用差异化关键词重写所有笔记的素材链接
# =============================================
print("\n=== 重写笔记素材链接 ===")

count = 0
for rec in records:
    fields = rec.get('fields', {})
    rid = rec['record_id']
    title = fields.get('笔记标题', '')
    hotel = fields.get('酒店名称', '')

    # 找对应的关键词组合
    hotel_repo = keyword_repo.get(hotel)
    if not hotel_repo:
        print(f"  ⚠️ [{title[:20]}] 未找到酒店关键词库")
        continue

    # 匹配角度
    matched_angle = None
    for nt, ak in title_to_angle.items():
        if nt in title:
            matched_angle = ak
            break

    if not matched_angle:
        matched_angle = "angle_通用"
    kw_sets = hotel_repo.get(matched_angle)
    if not kw_sets:
        # 兜底用第一个
        kw_sets = list(hotel_repo.values())[0]

    # 构建5条链接
    lines = []
    sources_order = ["pexels", "unsplash", "xhs", "pinterest", "douyin"]
    for i, src in enumerate(sources_order):
        matched = [s for s in kw_sets if s[1] == src]
        kw = matched[0][0] if matched else kw_sets[i % len(kw_sets)][0]
        q = PQ(kw)

        if src == "pexels":
            link = f"https://www.pexels.com/zh-cn/search/{q}/"
        elif src == "unsplash":
            link = f"https://unsplash.com/s/photos/{q}"
        elif src == "xhs":
            link = f"https://www.xiaohongshu.com/search_result?keyword={q}&source=web_search_result_notes"
        elif src == "pinterest":
            link = f"https://www.pinterest.com/search/pins/?q={q}"
        elif src == "douyin":
            link = f"https://www.douyin.com/search/{q}"

        src_name = {"pexels":"Pexels","unsplash":"Unsplash","xhs":"小红书","pinterest":"Pinterest","douyin":"抖音"}[src]
        lines.append(f"{link}  # [{src_name}] {kw}")

    new_links = "\n".join(lines)
    resp = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TID}/records/{rid}',
               {'fields': {'素材参考链接': new_links}})
    if resp.get('code') == 0:
        count += 1
        print(f"  ✅ [{title[:22]}] {matched_angle} ×5条")
    else:
        print(f"  ❌ [{title[:22]}] {resp.get('msg','')}")
    time.sleep(0.3)

print(f"\n=== 完成 ===")
print(f"酒店关键词库: {kw_tid}")
print(f"笔记链接重写: {count}/{len(records)} 条")
