#!/usr/bin/env python3
"""
Step 5: 创建深度分析子表 (高优先级热点地区)
2026-05-28
"""
import json, os, urllib.request, socket, sys
socket.setdefaulttimeout(15)

config_path = os.path.expanduser('~/.openclaw/config.toml')
with open(config_path) as f:
    lines = f.readlines()
def get_val(key):
    for line in lines:
        s = line.strip()
        if s.startswith(key):
            eq = s.index('=')
            return s[eq+1:].strip().strip('"').strip("'")
    return None
app_id = get_val('appId')
app_secret = get_val('appSecret')
body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=body, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']
print("[OK] Token")

APP_TOKEN = "C6omb1tXkav7YVswSogcQbO1nwe"

def api(method, url, data=None):
    h = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    b = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=b, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as f:
            return json.loads(f.read().decode())
    except urllib.error.HTTPError as e:
        return {"code": -1, "msg": e.read().decode()[:500]}

# 深度分析子表配置
sub_tables = [
    {
        "name": "广州·端午龙舟文化热点",
        "records": [
            {"名称": "猎德龙舟赛", "类别": "活动", "推荐理由": "广州最火龙舟赛事，端午文化核心IP", "参考价格": "免费观看", "关联热度": "772万+播放", "详情链接": "https://www.douyin.com/hashtag/2513732", "备注": "端午期间热度飙升"},
            {"名称": "珠江夜游", "类别": "景点", "推荐理由": "端午龙舟观赛+珠江夜景联动产品", "参考价格": "80-200元", "关联热度": "高", "详情链接": "", "备注": "可搭配龙舟主题套餐"},
            {"名称": "广州塔", "类别": "景点", "推荐理由": "广州地标，端午灯光秀", "参考价格": "150-298元", "关联热度": "高", "详情链接": "", "备注": "端午期间有特别活动"},
            {"名称": "广州花园酒店", "类别": "酒店", "推荐理由": "老牌五星，位置优越近龙舟赛道", "参考价格": "800-1500元/晚", "关联热度": "中", "详情链接": "", "备注": "适合家庭游客"},
            {"名称": "虾饺妹·泮溪酒家", "类别": "美食", "推荐理由": "地道广式早茶，端午特供粽子", "参考价格": "80-150元/人", "关联热度": "中", "详情链接": "", "备注": "端午文化美食体验"},
            {"名称": "广州地铁", "类别": "交通", "推荐理由": "端午赛区周边交通便利", "参考价格": "", "关联热度": "中", "详情链接": "", "备注": "龙舟赛区有临时交通管制"},
            {"名称": "沙面/永庆坊", "类别": "景点", "推荐理由": "广州历史文化街区，适合Citywalk", "参考价格": "免费", "关联热度": "中", "详情链接": "", "备注": "适合搭配龙舟行程"},
        ]
    },
    {
        "name": "塞尔维亚·武契奇访华热点",
        "records": [
            {"名称": "贝尔格莱德要塞", "类别": "景点", "推荐理由": "塞尔维亚地标，多瑙河与萨瓦河交汇", "参考价格": "免费", "关联热度": "高", "详情链接": "", "备注": "免签国必打卡景点"},
            {"名称": "贝尔格莱德凯悦酒店", "类别": "酒店", "推荐理由": "五星级酒店，位置优越", "参考价格": "600-1200元/晚", "关联热度": "高", "详情链接": "", "备注": "已入库酒店资源"},
            {"名称": "斯卡达利亚老街", "类别": "美食", "推荐理由": "贝尔格莱德最著名美食街", "参考价格": "100-200元/人", "关联热度": "中", "详情链接": "", "备注": "塞尔维亚传统美食"},
            {"名称": "木头村Drvengrad", "类别": "景点", "推荐理由": "著名导演库斯图里卡打造的电影村", "参考价格": "约50元", "关联热度": "中", "详情链接": "", "备注": "独特文化体验"},
            {"名称": "塞尔维亚葡萄酒庄园", "类别": "美食", "推荐理由": "巴尔干葡萄酒产区", "参考价格": "200-500元/人", "关联热度": "中", "详情链接": "", "备注": "高端定制游产品"},
            {"名称": "北京故宫/天安门", "类别": "景点", "推荐理由": "塞尔维亚总统访华接待地", "参考价格": "60元", "关联热度": "高", "详情链接": "", "备注": "商务接待路线"},
            {"名称": "北京国贸大酒店", "类别": "酒店", "推荐理由": "CBD核心，适合商务宾客", "参考价格": "1500-3000元/晚", "关联热度": "高", "详情链接": "", "备注": "高端商务酒店"},
        ]
    },
    {
        "name": "欧洲·极端高温避暑热点",
        "records": [
            {"名称": "瑞士因特拉肯", "类别": "景点", "推荐理由": "阿尔卑斯山避暑胜地，夏季均温20℃", "参考价格": "自由行1.5-3万", "关联热度": "高", "详情链接": "", "备注": "欧洲避暑首选"},
            {"名称": "挪威峡湾", "类别": "景点", "推荐理由": "北欧清凉仙境，夏季均温15-20℃", "参考价格": "跟团2-4万", "关联热度": "高", "详情链接": "", "备注": "极昼+峡湾双体验"},
            {"名称": "冰岛蓝湖温泉", "类别": "景点", "推荐理由": "冰与火之地，全年凉爽", "参考价格": "跟团3-5万", "关联热度": "中", "详情链接": "", "备注": "高端小众目的地"},
            {"名称": "法国尼斯/南法", "类别": "景点", "推荐理由": "南法海岸线，薰衣草季(6-7月)", "参考价格": "自由行1.5-3万", "关联热度": "高", "详情链接": "", "备注": "高温下南法海滨相对凉爽"},
            {"名称": "瑞士少女峰酒店", "类别": "酒店", "推荐理由": "欧洲之巅住宿体验", "参考价格": "2000-4000元/晚", "关联热度": "中", "详情链接": "", "备注": "高端酒店推荐"},
            {"名称": "意大利多洛米蒂", "类别": "景点", "推荐理由": "阿尔卑斯最美山脉，徒步天堂", "参考价格": "自由行2-4万", "关联热度": "中", "详情链接": "", "备注": "远离热浪"},
        ]
    },
    {
        "name": "全国·高考毕业旅行热点",
        "records": [
            {"名称": "成都", "类别": "景点", "推荐理由": "美食+国宝熊猫+年轻人最爱", "参考价格": "3-5天2000-4000元", "关联热度": "高", "详情链接": "", "备注": "毕业生首选目的地"},
            {"名称": "上海迪士尼", "类别": "景点", "推荐理由": "年轻人的童话世界", "参考价格": "门票475-799元", "关联热度": "高", "详情链接": "", "备注": "毕业季特别活动"},
            {"名称": "西安", "类别": "景点", "推荐理由": "历史文化+美食之都，性价比高", "参考价格": "3-5天1500-3000元", "关联热度": "高", "详情链接": "", "备注": "适合学生预算"},
            {"名称": "成都W酒店", "类别": "酒店", "推荐理由": "潮流设计酒店，年轻人最爱", "参考价格": "1200-2000元/晚", "关联热度": "中", "详情链接": "", "备注": "已入库酒店资源"},
            {"名称": "大理/丽江", "类别": "景点", "推荐理由": "文艺青年毕业旅行圣地", "参考价格": "5-7天3000-5000元", "关联热度": "高", "详情链接": "", "备注": "毕业季热门"},
            {"名称": "青岛/威海", "类别": "景点", "推荐理由": "海滨城市，夏季凉爽", "参考价格": "3-5天2000-3500元", "关联热度": "中", "详情链接": "", "备注": "性价比海滨目的地"},
            {"名称": "南京", "类别": "景点", "推荐理由": "高校云集，历史文化底蕴", "参考价格": "3-5天1500-3000元", "关联热度": "中", "详情链接": "", "备注": "适合高校游"},
        ]
    },
    {
        "name": "美食夜市·烟火气热点",
        "records": [
            {"名称": "长沙五一广场/太平街", "类别": "美食", "推荐理由": "网红夜市，长沙美食集中地", "参考价格": "50-150元/人", "关联热度": "高", "详情链接": "", "备注": "烟火气话题最佳取景地"},
            {"名称": "重庆解放碑/洪崖洞", "类别": "美食", "推荐理由": "8D魔幻夜市，夜景+美食", "参考价格": "50-200元/人", "关联热度": "高", "详情链接": "", "备注": "夜景美食双打卡"},
            {"名称": "西安回民街", "类别": "美食", "推荐理由": "千年美食街，西北美食大全", "参考价格": "30-100元/人", "关联热度": "高", "详情链接": "", "备注": "历史文化+美食体验"},
            {"名称": "成都建设巷", "类别": "美食", "推荐理由": "成都本地人最爱夜市", "参考价格": "30-100元/人", "关联热度": "中", "详情链接": "", "备注": "性价比极高"},
            {"名称": "上海锦江饭店", "类别": "酒店", "推荐理由": "淮海路商圈，离夜市近", "参考价格": "800-1500元/晚", "关联热度": "中", "详情链接": "", "备注": "城市中心酒店"},
            {"名称": "广州宝华路/上下九", "类别": "美食", "推荐理由": "西关美食一条街", "参考价格": "30-120元/人", "关联热度": "中", "详情链接": "", "备注": "老广味道"},
        ]
    },
]

# 类别选项
category_options = [
    {"name": "酒店", "color": 0}, {"name": "景点", "color": 1},
    {"name": "美食", "color": 2}, {"name": "活动", "color": 3},
    {"name": "购物", "color": 4}, {"name": "交通", "color": 5},
]

# 先获取已有表列表，避免重复创建
existing_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables')
existing_tables = {t['name']: t['table_id'] for t in existing_resp.get('data', {}).get('items', [])}
print(f"已有表: {list(existing_tables.keys())}")

for st in sub_tables:
    tname = st["name"]
    
    # 如果表已存在，删除重建
    if tname in existing_tables:
        # 删除旧表
        del_resp = api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{existing_tables[tname]}')
        print(f"[DEL] 删除旧表: {tname}")
    
    # 创建新表
    create_data = {
        "table": {
            "name": tname,
            "fields": [
                {"field_name": "名称", "type": 1},
                {"field_name": "类别", "type": 3, "property": {"options": category_options}},
                {"field_name": "推荐理由", "type": 1},
                {"field_name": "参考价格", "type": 1},
                {"field_name": "关联热度", "type": 1},
                {"field_name": "详情链接", "type": 1},
                {"field_name": "备注", "type": 1},
            ]
        }
    }
    
    create_resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', create_data)
    if create_resp.get('code') != 0:
        print(f"[ERROR] 创建表「{tname}」失败: {create_resp.get('msg', '')}")
        continue
    
    new_table_id = create_resp['data']['table_id']
    print(f"[OK] 创建表「{tname}」table_id={new_table_id}")
    
    # 批量插入记录
    records = [{"fields": r} for r in st["records"]]
    batches = [records[i:i+10] for i in range(0, len(records), 10)]
    for i, batch in enumerate(batches):
        payload = {"records": batch}
        ins_resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{new_table_id}/records/batch_create', payload)
        if ins_resp.get('code') == 0:
            print(f"  [OK] 插入 {len(batch)} 条记录")
        else:
            print(f"  [ERROR] 插入失败: {ins_resp.get('msg', '')[:100]}")
    
    # 删除默认空记录
    page_token = None
    while True:
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{new_table_id}/records?page_size=20'
        if page_token: url += f'&page_token={page_token}'
        r = api('GET', url)
        items = r.get('data', {}).get('items', [])
        if not items: break
        for item in items:
            api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{new_table_id}/records/{item["record_id"]}')
        page_token = r.get('data', {}).get('page_token')

print(f"\n🎉 所有子表创建完成！")
print(f"📊 链接: https://icns51dkxerg.feishu.cn/base/{APP_TOKEN}")
