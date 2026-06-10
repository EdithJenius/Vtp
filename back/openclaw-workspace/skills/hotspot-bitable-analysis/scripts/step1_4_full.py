#!/usr/bin/env python3
"""
热点商机多维分析 2026-05-29 完整流程
Step 1-4: 采集→分析→创建Bitable→插入数据
"""
import json, urllib.request, urllib.error, os, sys, time, re, urllib.parse
import configparser

# ===== 1. 获取Token =====
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
    """Flyweight API call with token"""
    headers = {'Authorization': f'Bearer {TOKEN}'}
    if data:
        if isinstance(data, str):
            payload = data.encode('utf-8')
        else:
            payload = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        payload = None
    r = urllib.request.Request(url, data=payload, method=method, headers=headers)
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode())

# ===== 2. 创建Bitable =====
bitable_name = "热点商机多维分析 2026-05-29 09时"
resp = api('POST', 'https://open.feishu.cn/open-apis/bitable/v1/apps', {"name": bitable_name})
APP_TOKEN = resp['data']['app']['app_token']
TABLE_ID = resp['data']['app']['default_table_id']
print(f"[Bitable] Created: {APP_TOKEN}, table: {TABLE_ID}")

# ===== 3. 查看现有字段 =====
fields_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields')
existing_fields = fields_resp.get('data', {}).get('items', [])
print(f"[Fields] {len(existing_fields)} existing fields:")
for f in existing_fields:
    print(f"  {f['field_id']}: {f['field_name']} (type={f['type']})")

# ===== 4. 重命名默认字段'文本'为'热点话题' =====
text_field = next((f for f in existing_fields if f['field_name'] == '文本'), None)
if text_field:
    api('PUT',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{text_field["field_id"]}',
        {"field_name": "热点话题", "type": 1})
    print("[Field] Renamed '文本' -> '热点话题'")

# ===== 5. 删除不需要的默认字段（单选、日期、附件） =====
for f in existing_fields:
    if f['field_name'] in ('单选', '日期', '附件'):
        api('DELETE',
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{f["field_id"]}')
        print(f"[Field] Deleted: {f['field_name']}")

# ===== 6. 创建目标字段 =====
fields_config = [
    ("来源渠道", 4, {"options": [
        {"name": "微博热搜"}, {"name": "百度热搜"}, {"name": "知乎热榜"},
        {"name": "抖音"}, {"name": "小红书"}, {"name": "B站"}, {"name": "综合"},
        {"name": "头条"}, {"name": "贴吧"}, {"name": "36氪"}
    ]}),
    ("话题类别", 3, {"options": [
        {"name": "航天科技"}, {"name": "社会民生"}, {"name": "天气灾害"},
        {"name": "财经股市"}, {"name": "国际外交"}, {"name": "科技AI"},
        {"name": "体育赛事"}, {"name": "文旅美食"}, {"name": "健康生活"}, {"name": "教育"}
    ]}),
    ("热度指数", 1, None),
    ("热度指数数值", 2, None),
    ("关联地点", 1, None),
    ("关联旅游景点", 1, None),
    ("旅游商机分析", 1, None),
    ("优先级", 3, {"options": [
        {"name": "高"}, {"name": "中"}, {"name": "低"}
    ]}),
    ("备注", 1, None),
]

for fname, ftype, fprop in fields_config:
    payload = {"field_name": fname, "type": ftype}
    if fprop:
        payload["property"] = fprop
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields'
    r = api('POST', url, payload)
    if r.get('code') == 0:
        print(f"[Field] Created: {fname}")
    else:
        print(f"[Field] Error {fname}: {r.get('msg')}")

# ===== 7. 删除默认空记录 =====
del_resp = api('GET',
    f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=50')
items = del_resp.get('data', {}).get('items', [])
for item in items:
    rid = item['record_id']
    api('DELETE',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{rid}')
print(f"[Clean] Deleted {len(items)} default records")

# ===== 8. 分析数据 =====
records = [
    {
        "热点话题": "甘孜通报稻城亚丁景区违规封堵省道",
        "来源渠道": ["微博热搜", "抖音"],
        "话题类别": "文旅美食",
        "热度指数": "微博#1/129万 + 抖音#20/777万",
        "热度指数数值": 7775024,
        "关联地点": "甘孜·稻城亚丁",
        "关联旅游景点": "稻城亚丁景区",
        "旅游商机分析": "⭐ 景区事件引爆关注，虽然负面但带来巨大流量。可借势推出「避坑攻略」「真实测评」类内容，引导用户关注周边未踩雷景点（香格里拉、康定、色达等）。甘孜全域旅游可趁热度推广。",
        "优先级": "高",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('甘孜通报稻城亚丁景区违规封堵省道')}"
    },
    {
        "热点话题": "黑河学院运动会放眼望去全是俄小姐姐",
        "来源渠道": ["头条"],
        "话题类别": "文旅美食",
        "热度指数": "头条#4/1953万",
        "热度指数数值": 19537616,
        "关联地点": "黑河·黑龙江",
        "关联旅游景点": "黑河、中俄边境、俄罗斯风情",
        "旅游商机分析": "⭐ 黑河中俄跨境旅游热点：俄罗斯元素引发大量关注。可推「黑河→俄罗斯布拉戈维申斯克一日游」「中俄边境小众游」「黑河留学体验」等产品。搭配暑期中俄跨境旅游线路。",
        "优先级": "高",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('黑河学院运动会俄小姐姐')}"
    },
    {
        "热点话题": "多元业态融合 拓展夏季消费新空间",
        "来源渠道": ["头条"],
        "话题类别": "文旅美食",
        "热度指数": "头条#3/2159万",
        "热度指数数值": 21592405,
        "关联地点": "全国",
        "关联旅游景点": "避暑旅游、夜间经济、文旅消费",
        "旅游商机分析": "⭐ 官方助推夏季消费，利好文旅。可结合「端午小长假+暑期游」推广避暑旅游产品：草原游、海滨游、山川徒步。重点推新疆、青海、云南、贵州等避暑目的地。",
        "优先级": "高",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('夏季消费新空间')}"
    },
    {
        "热点话题": "未来五年将出现史上最热一年",
        "来源渠道": ["头条"],
        "话题类别": "天气灾害",
        "热度指数": "头条#26/216万",
        "热度指数数值": 2164829,
        "关联地点": "全国（影响旅游业）",
        "关联旅游景点": "避暑胜地、水上乐园、山岳景区",
        "旅游商机分析": "⭐ 高温预警带动避暑旅游需求：东北（长白山、哈尔滨）、云南（大理、丽江）、贵州（黄果树、黔东南）、川西（稻城亚丁）、青海（茶卡盐湖）成热门。可推「清凉一夏」「避暑圣地」套餐。",
        "优先级": "高",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('史上最热一年避暑')}"
    },
    {
        "热点话题": "外国人的中国胃觉醒了",
        "来源渠道": ["抖音"],
        "话题类别": "文旅美食",
        "热度指数": "抖音#11/839万",
        "热度指数数值": 8394025,
        "关联地点": "全国",
        "关联旅游景点": "美食街、夜市、网红餐厅",
        "旅游商机分析": "⭐ 外国人在中国美食探店成流量密码。可推「外国人游中国」「老外带你吃当地美食」内容，借势推广国内旅游地和特色美食体验。重点城市：成都、重庆、西安、广州、长沙。",
        "优先级": "高",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('外国人中国胃觉醒')}"
    },
    {
        "热点话题": "高温难求生,印留子光速撤离",
        "来源渠道": ["贴吧"],
        "话题类别": "天气灾害",
        "热度指数": "贴吧#1/288万讨论",
        "热度指数数值": 2880000,
        "关联地点": "印度",
        "关联旅游景点": "出境游（避开印度高温）",
        "旅游商机分析": "印度极端高温（50℃+），反向利好国内避暑旅游和替代出境目的地（俄罗斯、北欧、瑞士、新西兰南岛）。可推「逃离高温」系列出境游产品：俄罗斯、挪威、冰岛。",
        "优先级": "中",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('印度高温避暑')}"
    },
    {
        "热点话题": "疲劳驾驶认定新规6月实施",
        "来源渠道": ["抖音"],
        "话题类别": "社会民生",
        "热度指数": "抖音#5/1039万",
        "热度指数数值": 10394113,
        "关联地点": "全国",
        "关联旅游景点": "自驾游",
        "旅游商机分析": "疲劳驾驶新规影响自驾游群体。可推「自驾游安全攻略」「服务区+酒店停靠推荐」「跟团游替代方案」。利好跟团游、定制游。",
        "优先级": "中",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('疲劳驾驶新规自驾游')}"
    },
    {
        "热点话题": "三夏大规模小麦机收全面展开",
        "来源渠道": ["微博"],
        "话题类别": "社会民生",
        "热度指数": "微博#3/69万",
        "热度指数数值": 690000,
        "关联地点": "河南/山东/安徽等",
        "关联旅游景点": "乡村游、农业旅游",
        "旅游商机分析": "夏收季节可关联「乡村田园旅游」「农事体验游」，推河南、山东、安徽的乡村民宿和农业旅游目的地。",
        "优先级": "中",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('三夏小麦机收')}"
    },
    {
        "热点话题": "菲律宾近1月抓扣150余名中国公民",
        "来源渠道": ["头条"],
        "话题类别": "国际外交",
        "热度指数": "头条#2/2386万",
        "热度指数数值": 23863298,
        "关联地点": "菲律宾",
        "关联旅游景点": "替代出境游目的地",
        "旅游商机分析": "菲律宾安全事件影响出境游信心。可推替代海岛目的地：泰国普吉、印尼巴厘岛、马尔代夫、海南三亚。利好国内高端海岛游。",
        "优先级": "中",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('菲律宾中国公民')}"
    },
    {
        "热点话题": "阿根廷公布世界杯名单：梅西领衔",
        "来源渠道": ["头条", "微博"],
        "话题类别": "体育赛事",
        "热度指数": "头条#29/160万 + 微博#2/82万",
        "热度指数数值": 1603745,
        "关联地点": "阿根廷",
        "关联旅游景点": "阿根廷旅游、南美旅游",
        "旅游商机分析": "梅西+世界杯热带动南美旅游关注度。适合推「阿根廷定制游」「南美足球朝圣之旅」等高端出境产品。但南美线路单价高、周期长，适合小众高端。",
        "优先级": "低",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('阿根廷世界杯名单')}"
    },
    {
        "热点话题": "男子每天睡足7小时3年脑梗2次",
        "来源渠道": ["头条"],
        "话题类别": "健康生活",
        "热度指数": "头条#10/1072万",
        "热度指数数值": 10722471,
        "关联地点": "无",
        "关联旅游景点": "康养旅游",
        "旅游商机分析": "健康类热点可关联「康养旅游」「养生度假」产品。推温泉疗养、森林康养、中医养生旅游目的地。轻关联，建议低调借势。",
        "优先级": "低",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('康养旅游健康生活方式')}"
    },
    {
        "热点话题": "国足新一期集训名单公布",
        "来源渠道": ["抖音"],
        "话题类别": "体育赛事",
        "热度指数": "抖音#6/1030万",
        "热度指数数值": 10308673,
        "关联地点": "中国",
        "关联旅游景点": "体育旅游",
        "旅游商机分析": "国足集训带动体育旅游关注。可推「足球主题夏令营」「体育训练基地+旅游套餐」。关联性一般，低优先级。",
        "优先级": "低",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('国足集训名单')}"
    },
    {
        "热点话题": "杭州查封小区代孕窝点：立案调查",
        "来源渠道": ["头条"],
        "话题类别": "社会民生",
        "热度指数": "头条#21/356万",
        "热度指数数值": 3569200,
        "关联地点": "杭州",
        "关联旅游景点": "杭州（弱关联）",
        "旅游商机分析": "社会新闻，与旅游弱关联。杭州作为旅游城市长时间有热度，可顺带推杭州周边游产品。",
        "优先级": "低",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('杭州社会新闻')}"
    },
    {
        "热点话题": "官方通报亚丁景区封堵省道收费",
        "来源渠道": ["抖音"],
        "话题类别": "文旅美食",
        "热度指数": "抖音#20/777万",
        "热度指数数值": 7775024,
        "关联地点": "甘孜·稻城亚丁",
        "关联旅游景点": "稻城亚丁、甘孜全域",
        "旅游商机分析": "同亚丁景区事件，景区管理争议引发全网关注。可做「川西小众替代景点」攻略：色达、理塘、新都桥、四姑娘山、海螺沟。负面事件反而可以做成正面内容。",
        "优先级": "高",
        "备注": f"链接：https://s.weibo.com/weibo?q={urllib.parse.quote('稻城亚丁封堵省道')}"
    },
    {
        "热点话题": "92岁老艺术家手搓AI写了封情书",
        "来源渠道": ["抖音"],
        "话题类别": "文旅美食",
        "热度指数": "抖音#17/780万",
        "热度指数数值": 7804510,
        "关联地点": "无",
        "关联旅游景点": "无（泛流量）",
        "旅游商机分析": "温情故事，适合做正能量旅游内容背景素材。低优先级，但可参考讲故事的文案风格。",
        "优先级": "低",
        "备注": f"链接：https://www.douyin.com/hot"
    },
]

# ===== 9. 批量插入 =====
def send_batch(batch):
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create'
    payload = json.dumps({"records": [{"fields": r} for r in batch]}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST',
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json; charset=utf-8'})
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        if result.get('code') == 0:
            return len(result.get('data', {}).get('records', [])), None
        else:
            return 0, result.get('msg')
    except urllib.error.HTTPError as e:
        return 0, f'HTTP {e.code}: {e.read().decode()[:500]}'

inserted = 0
for i in range(0, len(records), 10):
    batch = records[i:i+10]
    n, err = send_batch(batch)
    if err:
        print(f"Batch {i//10+1}: Error - {err}")
    else:
        print(f"Batch {i//10+1}: Inserted {n} records")
    inserted += n
    time.sleep(0.5)

print(f"\n[Insert] {inserted}/{len(records)} records inserted")

# ===== 10. 验证 =====
verify_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=5'
req = urllib.request.Request(verify_url, headers={'Authorization': f'Bearer {TOKEN}'})
with urllib.request.urlopen(req) as f:
    verify = json.loads(f.read().decode())
items = verify.get('data', {}).get('items', [])
print(f"[Verify] Table has {len(items)}+ records in first page")
for item in items:
    print(f"  - {item.get('fields', {}).get('热点话题', 'N/A')[:30]}")

# ===== 11. 设置公开权限 =====
pub_url = f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/public?type=bitable'
pub_body = json.dumps({
    "external_access_entity": "open",
    "security_entity": "anyone_can_view",
    "link_share_entity": "anyone_readable",
    "copy_entity": "anyone_can_copy",
    "comment_entity": "anyone",
}).encode()
req = urllib.request.Request(pub_url, data=pub_body, method='PATCH',
    headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
urllib.request.urlopen(req)
print("[Permission] Set to public")

# POST member
member_url = f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/members?type=bitable&need_notification=false'
member_body = json.dumps({
    "member_type": "openid",
    "member_id": "ou_b098a77a8b7869d14ccd6e34b7af3583",
    "perm": "full_access"
}).encode()
req = urllib.request.Request(member_url, data=member_body, method='POST',
    headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
urllib.request.urlopen(req)
print("[Permission] Member added")

print(f"\n===== DONE =====")
print(f"Bitable: {bitable_name}")
print(f"App Token: {APP_TOKEN}")
print(f"URL: https://bytedance.feishu.cn/base/{APP_TOKEN}")
