#!/usr/bin/env python3
"""Step 1-4 Full: Create Bitable + Insert hotspot data"""
import urllib.request, json, configparser, os, time

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config.get('provider.feishu', 'appId').strip('"')
APP_SECRET = config.get('provider.feishu', 'appSecret').strip('"')

body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=body, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']

H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
print(f"Token: {TOKEN[:20]}...")

# Create Bitable
req = urllib.request.Request('https://open.feishu.cn/open-apis/bitable/v1/apps',
    data=json.dumps({"name": "热点商机多维分析 2026-06-04 16时"}).encode(), headers=H)
with urllib.request.urlopen(req) as f:
    r = json.loads(f.read().decode())
APP = r['data']['app']['app_token']
TABLE = r['data']['app']['default_table_id']
print(f"Bitable: {APP}")
print(f"Table: {TABLE}")

# Delete default records
url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/records?page_size=50"
req = urllib.request.Request(url, headers=H)
with urllib.request.urlopen(req) as f:
    recs = json.loads(f.read().decode())
for item in (recs.get('data', {}).get('items') or []):
    rid = item['record_id']
    req = urllib.request.Request(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/records/{rid}", method='DELETE', headers=H)
    urllib.request.urlopen(req)

# Get fields, rename default, delete extras
url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/fields"
req = urllib.request.Request(url, headers=H)
with urllib.request.urlopen(req) as f:
    fields_data = json.loads(f.read().decode())
existing = {f['field_name']: f['field_id'] for f in fields_data['data']['items']}

text_f = next((f for f in fields_data['data']['items'] if f['field_name'] == '文本'), None)
if text_f:
    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/fields/{text_f['field_id']}",
        data=json.dumps({"field_name": "热点话题", "type": 1}).encode(), method='PUT', headers=H)
    urllib.request.urlopen(req)

for fname in ['单选', '日期', '附件']:
    if fname in existing:
        try:
            req = urllib.request.Request(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/fields/{existing[fname]}", method='DELETE', headers=H)
            urllib.request.urlopen(req)
        except: pass

# Create fields
fields_config = [
    {"field_name": "来源渠道", "type": 4, "property": {"options": [{"name":"微博热搜"},{"name":"百度热搜"},{"name":"知乎热榜"},{"name":"今日头条"},{"name":"B站热门"},{"name":"贴吧"},{"name":"36氪"},{"name":"上游-环球旅讯"}]}},
    {"field_name": "话题类别", "type": 3, "property": {"options": [{"name":"文旅美食"},{"name":"社会民生"},{"name":"财经股市"},{"name":"科技AI"},{"name":"体育赛事"},{"name":"娱乐综艺"},{"name":"天气灾害"},{"name":"教育"},{"name":"国际外交"}]}},
    {"field_name": "热度指数", "type": 1},
    {"field_name": "热度指数数值", "type": 2},
    {"field_name": "关联地点", "type": 1},
    {"field_name": "关联旅游景点", "type": 1},
    {"field_name": "旅游商机分析", "type": 1},
    {"field_name": "优先级", "type": 3, "property": {"options": [{"name":"高"},{"name":"中"},{"name":"低"}]}},
    {"field_name": "备注", "type": 1},
]
for f in fields_config:
    if f['field_name'] in existing: continue
    body = {"field_name": f['field_name'], "type": f['type']}
    if 'property' in f: body['property'] = f['property']
    req = urllib.request.Request(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/fields",
        data=json.dumps(body).encode(), headers=H, method='POST')
    try:
        with urllib.request.urlopen(req) as f2:
            r = json.loads(f2.read().decode())
        if r.get('code') == 0: print(f"  + {f['field_name']}")
        else: print(f"  ? {f['field_name']}: {r.get('msg','')}")
    except urllib.error.HTTPError as e:
        print(f"  ! {f['field_name']}: HTTP {e.code}")
    time.sleep(0.3)

# Insert records
records = [
    {"热点话题": "独库公路通车引爆新疆旅游热（搜索量暴涨166%）",
     "来源渠道": ["上游-环球旅讯"], "话题类别": "文旅美食",
     "热度指数": "同程旅行数据/行业新闻", "热度指数数值": 166,
     "关联地点": "新疆", "关联旅游景点": "独库公路",
     "旅游商机分析": "⭐旺季前重磅信号！独库公路是新疆旅游大动脉，通车即引爆搜索量。\n→ 新疆旅游产品（伊犁/喀纳斯/独库公路线）可提前占位\n→ 端午+暑假双窗口叠加，高优先级",
     "优先级": "高",
     "备注": "同程旅行数据：独库公路开通当日搜索量环比增长166%"},
    {"热点话题": "新加坡航空开通杭州至新加坡往返航线",
     "来源渠道": ["上游-环球旅讯"], "话题类别": "文旅美食",
     "热度指数": "行业动态", "关联地点": "杭州/新加坡", "关联旅游景点": "新加坡",
     "旅游商机分析": "⭐新航线=新流量入口！杭州直飞新加坡，华东市场东南亚出行更方便。\n→ 可推「杭州-新加坡」+「新马连线」度假产品\n→ 对标华东亲子游/蜜月市场",
     "优先级": "高", "备注": "新加坡航空开通杭州-新加坡航线"},
    {"热点话题": "天津南站凯悦嘉轩酒店启幕",
     "来源渠道": ["上游-环球旅讯"], "话题类别": "文旅美食",
     "热度指数": "行业动态", "关联地点": "天津", "关联旅游景点": "",
     "旅游商机分析": "⭐新酒店开业带来天津旅游热度。凯悦嘉轩定位中高端商旅。\n→ 天津周末游/商务出行产品可打包\n→ 配合端午假期周边游",
     "优先级": "中", "备注": "天津南站凯悦嘉轩酒店开业"},
    {"热点话题": "端午火车票明日开售",
     "来源渠道": ["百度热搜"], "话题类别": "文旅美食",
     "热度指数": "百度热搜多榜", "关联地点": "全国", "关联旅游景点": "",
     "旅游商机分析": "⭐时效性极高！端午出行窗口已开启。\n→ 短途/周边游产品紧急上线窗口\n→ 适合做「3天2晚」轻度假产品\n→ 重点：2-3小时高铁圈目的地",
     "优先级": "高", "备注": "端午出行高峰即将到来"},
    {"热点话题": "欧洲多国高温警报→国内避暑旅游利好",
     "来源渠道": ["今日头条"], "话题类别": "天气灾害",
     "热度指数": "头条热榜", "关联地点": "欧洲/国内避暑地",
     "关联旅游景点": "新疆/云南/贵州/长白山",
     "旅游商机分析": "欧洲高温=国内避暑目的地利好。\n→ 新疆（正逢独库通车）、云南、贵州、长白山等避暑目的地\n→ 推「避暑+草原」组合产品",
     "优先级": "中", "备注": "头条热榜#30"},
    {"热点话题": "杭州天价面馆从388元涨到2188元引热议",
     "来源渠道": ["微博热搜", "百度热搜"], "话题类别": "文旅美食",
     "热度指数": "微博33.8万/百度热榜14位", "热度指数数值": 338764,
     "关联地点": "杭州", "关联旅游景点": "",
     "旅游商机分析": "杭州本地话题热度高，可借势做杭州旅游/美食内容。\n→ 杭州周末游/美食攻略\n→ 高端餐饮vs旅游消费话题",
     "优先级": "中", "备注": "微博+百度热搜双上榜"},
    {"热点话题": "高考临近→毕业旅行窗口开启",
     "来源渠道": ["今日头条"], "话题类别": "教育",
     "热度指数": "头条745万热度", "热度指数数值": 7450860,
     "关联地点": "全国", "关联旅游景点": "三亚/成都/云南/厦门/长沙",
     "旅游商机分析": "⭐高考结束=毕业旅行潮。\n→ 推「毕业旅行」主题产品（三亚/成都/长沙等年轻人目的地）\n→ 性价比优先，适合经济档亲子/毕业团",
     "优先级": "高", "备注": "高考安检话题持续热搜"},
]

for rec in records:
    body = json.dumps({"fields": rec}).encode()
    req = urllib.request.Request(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/records",
        data=body, headers=H, method='POST')
    try:
        with urllib.request.urlopen(req) as f:
            r = json.loads(f.read().decode())
        if r.get('code') == 0: print(f"  ✓ {rec['热点话题'][:25]}...")
        else: print(f"  ? {rec['热点话题'][:20]}: {r.get('msg','')[:40]}")
    except Exception as e: print(f"  ✗ {rec['热点话题'][:20]}: {str(e)[:40]}")
    time.sleep(0.3)

# Set permissions
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/drive/v1/permissions/{APP}/public?type=bitable",
    data=json.dumps({"link_share_entity": "anyone_readable"}).encode(), headers=H, method='PATCH')
with urllib.request.urlopen(req) as f:
    json.loads(f.read().decode())

print(f"\n✅ 完成!")
print(f"🔗 https://bytedance.feishu.cn/base/{APP}")
print(f"APP_TOKEN: {APP}")
