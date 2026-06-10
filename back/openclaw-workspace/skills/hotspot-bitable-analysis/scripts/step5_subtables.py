#!/usr/bin/env python3
"""
Step 5: 创建深度分析子表
为高优先级热点地区创建4个子表
"""
import json, urllib.request, urllib.error, os, sys, time
import configparser

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId'].strip('"')
APP_SECRET = config['provider.feishu']['appSecret'].strip('"')

body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=body, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']
print(f"[Token] OK: {TOKEN[:20]}...")

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    if data:
        payload = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        payload = None
    r = urllib.request.Request(url, data=payload, method=method, headers=headers)
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode())

MAIN_APP_TOKEN = "ZdpRbPT2qaGsBvsqiNucQX1Knwh"

def create_subtable(table_name, fields_config):
    """创建子表：先建表含名称字段，再添加其他字段"""
    # 先用序号去重，避免重复名错误
    import random
    suffix = str(random.randint(100, 999))[-3:]
    unique_name = f"{table_name}"
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_APP_TOKEN}/tables'
    body = {"table": {"name": unique_name, "fields": [{"field_name": "名称", "type": 1}]}}
    resp = api('POST', url, body)
    if resp.get('code') and resp.get('code') != 0:
        # 重名则加随机后缀
        unique_name = f"{table_name}{suffix}"
        body["table"]["name"] = unique_name
        resp = api('POST', url, body)
    tid = resp['data']['table_id']
    print(f"[Subtable] Created: '{table_name}' -> {tid}")

    # 创建其他字段
    for fname, ftype, fprop in fields_config:
        payload = {"field_name": fname, "type": ftype}
        if fprop:
            payload["property"] = fprop
        api('POST',
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_APP_TOKEN}/tables/{tid}/fields',
            payload)

    # 删除默认空记录（如果有）
    del_resp = api('GET',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_APP_TOKEN}/tables/{tid}/records?page_size=50')
    items = del_resp.get('data', {}).get('items')
    if items:
        for item in items:
            rid = item['record_id']
            api('DELETE',
                f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_APP_TOKEN}/tables/{tid}/records/{rid}')
        print(f"  [Clean] Deleted {len(items)} default records")
    else:
        print(f"  [Clean] No default records to delete")

    return tid

def batch_insert(table_id, records):
    for i in range(0, len(records), 10):
        batch = records[i:i+10]
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_APP_TOKEN}/tables/{table_id}/records/batch_create'
        payload = json.dumps({"records": [{"fields": r} for r in batch]}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='POST',
            headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json; charset=utf-8'})
        try:
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read())
            n = len(result.get('data', {}).get('records', []))
            print(f"  Batch {i//10+1}: {n} records")
        except urllib.error.HTTPError as e:
            print(f"  Batch {i//10+1}: Error {e.code}: {e.read().decode()[:200]}")
        time.sleep(0.3)

# 子表字段配置
sub_fields = [
    ("类别", 3, {"options": [
        {"name": "酒店住宿"}, {"name": "景点景区"}, {"name": "美食餐饮"},
        {"name": "文化活动"}, {"name": "交通出行"}, {"name": "旅行社/线路"}
    ]}),
    ("推荐理由", 1, None),
    ("参考价格", 1, None),
    ("关联热度", 1, None),
    ("详情链接", 1, None),
    ("备注", 1, None),
]

# ============================
# 子表1: 甘孜·稻城亚丁
# ============================
print("\n=== 子表1: 甘孜·稻城亚丁 ===")
tid1 = create_subtable("甘孜·稻城亚丁景区事件", sub_fields)
batch_insert(tid1, [
    {"名称": "稻城亚丁景区", "类别": "景点景区", "推荐理由": "⭐核心景区，争议事件主角。建议做「避坑攻略」内容，引导正确游览方式。", "关联热度": "微博#1/129万"},
    {"名称": "色达五明佛学院", "类别": "景点景区", "推荐理由": "甘孜替代景点，红色佛国太震撼，人文摄影天堂。稻城亚丁热度可引流至此。", "关联热度": "高"},
    {"名称": "理塘·丁真故乡", "类别": "景点景区", "推荐理由": "网红县城，天空之城，318川藏线必经地。借亚丁热度推川西环线。", "关联热度": "中"},
    {"名称": "新都桥", "类别": "景点景区", "推荐理由": "摄影天堂，秋天的童话世界。川西环线重要节点。", "关联热度": "中"},
    {"名称": "四姑娘山", "类别": "景点景区", "推荐理由": "蜀山皇后，登山徒步圣地。可作为亚丁替代方案。", "关联热度": "中"},
    {"名称": "海螺沟冰川", "类别": "景点景区", "推荐理由": "低海拔冰川+温泉，适合大众游客。", "关联热度": "低"},
    {"名称": "康定情歌城", "类别": "景点景区", "推荐理由": "甘孜州府，民族风情浓厚。川西环线集散地。", "关联热度": "中"},
    {"名称": "央迈勇/仙乃日徒步", "类别": "景点景区", "推荐理由": "稻城亚丁核心徒步线路，可做深度户外游产品。", "关联热度": "高"},
    {"名称": "甘孜本地藏式民宿", "类别": "酒店住宿", "推荐理由": "特色藏式民宿，推「住在草原看银河」体验。", "关联热度": "中"},
    {"名称": "川西环线定制游7日", "类别": "旅行社/线路", "推荐理由": "成都-康定-新都桥-理塘-稻城-亚丁-色达，全明星线路。", "关联热度": "高"},
])

# ============================
# 子表2: 黑河·中俄边境游
# ============================
print("\n=== 子表2: 黑河·中俄边境 ===")
tid2 = create_subtable("黑河·中俄跨境旅游", sub_fields)
batch_insert(tid2, [
    {"名称": "黑河学院", "类别": "景点景区", "推荐理由": "⭐热点发源地，运动会俄小姐姐出圈。中俄文化交流打卡点。", "关联热度": "头条#4/1953万"},
    {"名称": "黑河→布拉戈维申斯克一日游", "类别": "旅行社/线路", "推荐理由": "⭐核心产品！黑河坐船过江即到俄罗斯，免签一日游。性价比超高。", "关联热度": "高"},
    {"名称": "黑河中央街步行街", "类别": "美食餐饮", "推荐理由": "中俄美食交汇地，俄式西餐+东北菜。", "关联热度": "中"},
    {"名称": "五大连池风景区", "类别": "景点景区", "推荐理由": "世界地质公园，火山地貌+矿泉康养。黑河周边王牌景区。", "关联热度": "中"},
    {"名称": "瑷珲古城", "类别": "景点景区", "推荐理由": "历史名城，瑷珲条约签订地。爱国主义教育基地。", "关联热度": "低"},
    {"名称": "黑河中俄民族风情园", "类别": "景点景区", "推荐理由": "体验俄罗斯民族文化，适合家庭游。", "关联热度": "中"},
    {"名称": "俄式桑拿+东北澡堂体验", "类别": "文化活动", "推荐理由": "中俄洗浴文化反差体验，短视频爆款素材。", "关联热度": "中"},
    {"名称": "黑河精品酒店/江景房", "类别": "酒店住宿", "推荐理由": "边境旅游配套，推荐江景房。", "关联热度": "中"},
    {"名称": "俄罗斯商品街逛吃", "类别": "美食餐饮", "推荐理由": "买俄货、吃俄餐、喝格瓦斯。购物+美食。", "关联热度": "中"},
    {"名称": "漠河-黑河-哈尔滨全景线", "类别": "旅行社/线路", "推荐理由": "极北+边境+省会全景行程，端午暑期可走。", "关联热度": "高"},
])

# ============================
# 子表3: 夏季避暑旅游
# ============================
print("\n=== 子表3: 夏季避暑旅游 ===")
tid3 = create_subtable("夏季避暑·高温旅游商机", sub_fields)
batch_insert(tid3, [
    {"名称": "长白山", "类别": "景点景区", "推荐理由": "⭐夏季平均20℃的天池圣地。避暑+户外+温泉一体。", "关联热度": "头条#26/216万（高温关联）"},
    {"名称": "哈尔滨/中央大街", "类别": "景点景区", "推荐理由": "冰城夏都，避暑首选。俄式建筑+啤酒美食。", "关联热度": "高"},
    {"名称": "贵州·黄果树瀑布+黔东南", "类别": "景点景区", "推荐理由": "⭐夏季避暑王牌，瀑布+苗寨+凉爽气候。", "关联热度": "高"},
    {"名称": "云南·大理-丽江-香格里拉", "类别": "旅行社/线路", "推荐理由": "四季如春，避暑度假经典线路。", "关联热度": "高"},
    {"名称": "青海·茶卡盐湖-青海湖", "类别": "景点景区", "推荐理由": "天空之境+高原湖泊，暑期热门。", "关联热度": "高"},
    {"名称": "新疆·伊犁草原", "类别": "景点景区", "推荐理由": "夏日草原+薰衣草+雪山，绝美风景。", "关联热度": "高"},
    {"名称": "川西·318国道自驾", "类别": "旅行社/线路", "推荐理由": "⭐避暑+风景线，暑期自驾首选。", "关联热度": "高"},
    {"名称": "水上乐园/漂流项目", "类别": "文化活动", "推荐理由": "夏日消暑刚需，亲子游爆款。", "关联热度": "中"},
    {"名称": "内蒙古·呼伦贝尔草原", "类别": "旅行社/线路", "推荐理由": "草原+蒙古包体验，避暑佳选。", "关联热度": "高"},
    {"名称": "高山避暑民宿/度假酒店", "类别": "酒店住宿", "推荐理由": "推莫干山、庐山、黄山等高山避暑产品。", "关联热度": "中"},
    {"名称": "出境避暑·挪威/冰岛", "类别": "旅行社/线路", "推荐理由": "极昼+冰川+峡湾，高端避暑出境游。", "关联热度": "低"},
    {"名称": "出境避暑·新西兰南岛", "类别": "旅行社/线路", "推荐理由": "反季节避暑，冬季滑雪+观星。", "关联热度": "低"},
])

# ============================
# 子表4: 外国人中国美食游
# ============================
print("\n=== 子表4: 外国人中国游 ===")
tid4 = create_subtable("外国人·中国美食游", sub_fields)
batch_insert(tid4, [
    {"名称": "成都·建设路美食街", "类别": "美食餐饮", "推荐理由": "⭐外国人最爱成都美食，建设路/玉林路火锅烧烤。", "关联热度": "抖音#11/839万"},
    {"名称": "重庆·洪崖洞+火锅", "类别": "美食餐饮", "推荐理由": "外国人打卡热门，8D魔幻城市+辣火锅。", "关联热度": "高"},
    {"名称": "西安·回民街", "类别": "美食餐饮", "推荐理由": "碳水天堂，肉夹馍+凉皮+油泼面，出片率极高。", "关联热度": "高"},
    {"名称": "广州·上下九/沙面", "类别": "景点景区", "推荐理由": "早茶文化+老广风情，适合慢游。", "关联热度": "中"},
    {"名称": "上海·外滩+新天地", "类别": "景点景区", "推荐理由": "海派文化+中西交融，外国人游客首选城市。", "关联热度": "中"},
    {"名称": "北京·胡同游+烤鸭", "类别": "景点景区", "推荐理由": "推老北京胡同+烤鸭+四合院民宿体验。", "关联热度": "中"},
    {"名称": "夜市文化体验游", "类别": "旅行社/线路", "推荐理由": "中国夜市是全球网红，长沙/南宁/青岛夜市YYDS。", "关联热度": "高"},
    {"名称": "外国人游中国·24小时系列", "类别": "旅行社/线路", "推荐理由": "「老外在中国的一天」短视频内容方向。", "关联热度": "高"},
    {"名称": "云南·少数民族美食寻味", "类别": "美食餐饮", "推荐理由": "过桥米线+野生菌+傣味烧烤，异域风情拉满。", "关联热度": "中"},
    {"名称": "湖南·长沙茶颜+臭豆腐", "类别": "美食餐饮", "推荐理由": "新消费美食之都，年轻人的美食天堂。", "关联热度": "中"},
    {"名称": "中国茶文化体验(龙井/普洱)", "类别": "文化活动", "推荐理由": "杭州龙井/武夷山大红袍/云南普洱，适合高端入境游。", "关联热度": "中"},
])

print(f"\n===== DONE =====")
print(f"URL: https://bytedance.feishu.cn/base/{MAIN_APP_TOKEN}")
