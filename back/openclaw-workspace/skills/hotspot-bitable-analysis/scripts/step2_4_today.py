#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热点商机多维分析 2026-06-01 流程
Step 2-4: 交叉验证+去重+商机分析 → 创建Bitable → 插入数据
"""
import json, os, sys, time, re, urllib.request, urllib.parse, configparser

# ===== 工具函数 =====
def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appid'].strip('"')
    app_secret = config['provider.feishu']['appsecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=10) as f:
        return json.loads(f.read().decode())['tenant_access_token']

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    payload = None
    if data is not None:
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as f:
            return json.loads(f.read().decode())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.read().decode()[:300]}

# ===== 1. 获取Token =====
TOKEN = get_token()
print(f"[Token] OK: {TOKEN[:20]}...")

# ===== 2. 创建Bitable =====
bitable_name = "热点商机多维分析 2026-06-01 09时"
resp = api('POST', 'https://open.feishu.cn/open-apis/bitable/v1/apps', {"name": bitable_name})
if resp.get('code') != 0:
    print(f"[ERR] 创建Bitable失败: {resp}")
    sys.exit(1)
APP_TOKEN = resp['data']['app']['app_token']
TABLE_ID = resp['data']['app']['default_table_id']
print(f"[Bitable] ✅ Created: {APP_TOKEN}")
print(f"  Table: {TABLE_ID}")
print(f"  URL: https://q7yllltm5t.feishu.cn/base/{APP_TOKEN}")

# ===== 3. 查看现有字段 =====
fields_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields')
existing_fields = fields_resp.get('data', {}).get('items', [])
print(f"[Fields] 现有 {len(existing_fields)} 个字段")

# ===== 4. 重命名/删除默认字段 =====
text_field = next((f for f in existing_fields if f['field_name'] == '文本'), None)
if text_field:
    r = api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{text_field["field_id"]}',
            {"field_name": "热点话题", "type": 1})
    print(f"[Rename] 文本→热点话题: code={r.get('code')}")

for fname in ['单选', '日期', '附件']:
    f = next((x for x in existing_fields if x['field_name'] == fname), None)
    if f:
        r = api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{f["field_id"]}')
        print(f"[Del] {fname}: code={r.get('code')}")

# ===== 5. 创建字段（一次性配选项） =====
field_defs = [
    {"field_name": "来源渠道", "type": 4, "property": {"options": [
        {"name": "微博热搜"}, {"name": "百度热搜"}, {"name": "知乎热榜"},
        {"name": "抖音"}, {"name": "今日头条"}, {"name": "贴吧"}, {"name": "36氪"}, {"name": "B站"}
    ]}},
    {"field_name": "话题类别", "type": 3, "property": {"options": [
        {"name": "航天科技"}, {"name": "社会民生"}, {"name": "天气灾害"}, {"name": "财经股市"},
        {"name": "国际外交"}, {"name": "科技AI"}, {"name": "体育赛事"}, {"name": "文旅美食"},
        {"name": "健康生活"}, {"name": "教育"}, {"name": "互联网"}, {"name": "娱乐影音"}
    ]}},
    {"field_name": "热度指数", "type": 1},
    {"field_name": "热度指数数值", "type": 2},
    {"field_name": "关联地点", "type": 1},
    {"field_name": "关联旅游景点", "type": 1},
    {"field_name": "旅游商机分析", "type": 1},
    {"field_name": "优先级", "type": 3, "property": {"options": [
        {"name": "高"}, {"name": "中"}, {"name": "低"}
    ]}},
    {"field_name": "备注", "type": 1},
]

for fd in field_defs:
    r = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields', fd)
    status = "✅" if r.get('code') == 0 else "❌"
    print(f"[Field] {status} {fd['field_name']}: {r.get('code')}")

# ===== 6. 清理默认空记录 =====
init_records = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=50')
items = init_records.get('data', {}).get('items') or []
for item in items:
    rid = item['record_id']
    r = api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{rid}')
print(f"[Clean] 删除 {len(items)} 条空记录")

# ===== 7. 商机分析数据 =====
# 基于多平台热点数据交叉验证 + AI分析
records = [
    # === 高优先级（与旅游强相关） ===
    {
        "热点话题": "哈尔滨为何遭遇沙尘暴突袭 / 哈尔滨机场10架次航班延误",
        "来源渠道": ["今日头条", "知乎热榜"],
        "话题类别": "天气灾害",
        "热度指数": "头条1163万+知乎177万",
        "热度指数数值": 11629621,
        "关联地点": "哈尔滨",
        "关联旅游景点": "哈尔滨冰雪大世界、太阳岛、中央大街",
        "旅游商机分析": "⭐ 高优先级。哈尔滨沙尘暴突发引发全国关注，虽为负面但可借势切入「极端天气下的旅游保障」「沙尘暴后的哈尔滨恢复」「哈尔滨夏季旅游避暑」等话题。夏季哈尔滨是避暑胜地，可推「逃离沙尘暴·哈尔滨清凉游」",
        "优先级": "高",
        "备注": "📎https://www.toutiao.com/trending/7645598280218771506/"
    },
    {
        "热点话题": "印度高温冲至48.2℃ / 高温避暑旅游",
        "来源渠道": ["知乎热榜"],
        "话题类别": "天气灾害",
        "热度指数": "知乎198万热度",
        "热度指数数值": 1980000,
        "关联地点": "印度/全国",
        "关联旅游景点": "国内避暑目的地（长白山、承德、丽江、贵阳、六盘水）",
        "旅游商机分析": "⭐ 高优先级。印度极端高温新闻引发国内对高温/避暑话题关注。可借势推广「国内避暑胜地推荐」「高温天逃离计划」「长白山/承德避暑山庄夏日游」等产品线。端午节临近，暑期避暑游是刚需。",
        "优先级": "高",
        "备注": "📎https://www.zhihu.com/question/2044427993054017025"
    },
    {
        "热点话题": "6月1日起102项国家标准正式实施 / 速览6月新规",
        "来源渠道": ["今日头条", "抖音"],
        "话题类别": "社会民生",
        "热度指数": "头条1052万+抖音1089万",
        "热度指数数值": 10890174,
        "关联地点": "全国",
        "关联旅游景点": "",
        "旅游商机分析": "⭐ 高优先级。6月新规涉及旅游行业标准，包括新的酒店/景区标准。可借势制作「6月旅游新规解读」「端午出游必看新规」等内容。同时抖音「速览6月新规」话题热度破千万。",
        "优先级": "高",
        "备注": "📎https://www.toutiao.com/article/7645993849731252746"
    },
    {
        "热点话题": "六一儿童节 / 这才是六一该办的活动",
        "来源渠道": ["抖音", "微博"],
        "话题类别": "文旅美食",
        "热度指数": "抖音1106万+微博58万",
        "热度指数数值": 11063684,
        "关联地点": "全国",
        "关联旅游景点": "主题乐园（迪士尼、环球影城、方特、长隆）、亲子酒店",
        "旅游商机分析": "⭐ 高优先级。六一儿童节当天，亲子游、主题乐园话题热度极高。可借势推广「六一亲子游攻略」「主题乐园特惠门票」「亲子酒店推荐」等内容。临近端午，可策划「端午亲子游早鸟计划」。",
        "优先级": "高",
        "备注": "📎https://www.douyin.com/hot"
    },
    {
        "热点话题": "天涯社区正式恢复访问 / 天涯神帖 / 天涯复活1999元会员割韭菜",
        "来源渠道": ["微博热搜", "今日头条", "知乎热榜", "贴吧", "36氪"],
        "话题类别": "互联网",
        "热度指数": "微博282万+头条952万+知乎1184万+贴吧163万",
        "热度指数数值": 11840000,
        "关联地点": "海南三亚（天涯海角）",
        "关联旅游景点": "天涯海角游览区、三亚海滩",
        "旅游商机分析": "⭐ 高优先级。「天涯」社区恢复访问引发全网情怀热议，可借势「天涯海角」旅游景点做IP联动内容。推出「去天涯海角打卡·致敬互联网青春」「天涯重启·三亚情怀游」等文旅内容。",
        "优先级": "高",
        "备注": "📎https://s.weibo.com/weibo?q=%23%E5%A4%A9%E6%B6%AF%E7%A4%BE%E5%8C%BA%23"
    },
    # === 中优先级 ===
    {
        "热点话题": "新能源车为何买得起修不起",
        "来源渠道": ["今日头条"],
        "话题类别": "社会民生",
        "热度指数": "头条1285万",
        "热度指数数值": 12852719,
        "关联地点": "全国",
        "关联旅游景点": "",
        "旅游商机分析": "新能源车维修成本话题虽非旅游直接相关，但可借势延伸「新能源车自驾游充电指南」「新能源车长途旅行注意事项」等自驾游内容。暑期自驾游是热门主题。",
        "优先级": "中",
        "备注": "📎https://www.toutiao.com/trending/7646203612858682921/"
    },
    {
        "热点话题": "樊振东斩获德甲MVP / 樊振东助萨尔布吕肯成就三冠王",
        "来源渠道": ["微博热搜", "今日头条", "贴吧", "抖音"],
        "话题类别": "体育赛事",
        "热度指数": "微博25万+头条780万+贴吧82万+抖音771万",
        "热度指数数值": 7795568,
        "关联地点": "德国/国内",
        "关联旅游景点": "",
        "旅游商机分析": "樊振东德甲夺冠获多平台热议。可借势「体育旅游」「观赛游」方向，推广德国旅游线路或国内乒乓球赛事旅游。但关联度中等。",
        "优先级": "中",
        "备注": "📎https://www.toutiao.com/trending/7646203102810345010/"
    },
    {
        "热点话题": "网友偶遇货车载着神舟二十二号返回舱",
        "来源渠道": ["今日头条"],
        "话题类别": "航天科技",
        "热度指数": "头条862万",
        "热度指数数值": 8615435,
        "关联地点": "相关运输途经地",
        "关联旅游景点": "航天主题景点、文昌航天发射场",
        "旅游商机分析": "神舟返回舱运输引发关注。可借势推广「文昌航天发射场参观」「航天主题亲子游」等内容。海南文昌旅游+航天主题是亮点。",
        "优先级": "中",
        "备注": "📎https://www.toutiao.com/trending/7645270020892737542/"
    },
    {
        "热点话题": "美加墨世界杯来了你准备好了吗",
        "来源渠道": ["今日头条"],
        "话题类别": "体育赛事",
        "热度指数": "头条578万",
        "热度指数数值": 5775099,
        "关联地点": "美国/加拿大/墨西哥",
        "关联旅游景点": "",
        "旅游商机分析": "美加墨世界杯引发关注。可借势「世界杯观赛游」「北美旅游线路」推广。世界杯期间（2026年夏季）已有需求提前预订。",
        "优先级": "中",
        "备注": "📎https://www.toutiao.com/trending/7645096025753272346/"
    },
    {
        "热点话题": "老人点燃路边杨絮致20辆汽车被烧毁",
        "来源渠道": ["知乎热榜"],
        "话题类别": "社会民生",
        "热度指数": "知乎177万",
        "热度指数数值": 1770000,
        "关联地点": "北方城市",
        "关联旅游景点": "",
        "旅游商机分析": "杨絮火灾话题虽非旅游直接相关，但可借势延伸「春季旅游防火安全」「景区防火注意事项」等内容。",
        "优先级": "中",
        "备注": "📎https://www.zhihu.com/question/2044501400923496808"
    },
    {
        "热点话题": "何猷君奚梦瑶婚礼欢迎晚宴",
        "来源渠道": ["微博热搜"],
        "话题类别": "娱乐影音",
        "热度指数": "微博25万",
        "热度指数数值": 246249,
        "关联地点": "婚礼举办地",
        "关联旅游景点": "婚礼相关景点/酒店",
        "旅游商机分析": "明星婚礼引发关注。可借势推广「明星婚礼同款酒店」「婚礼蜜月游」等内容。奚梦瑶何猷君的婚礼地点/酒店将成为打卡热点。",
        "优先级": "中",
        "备注": "📎https://s.weibo.com/weibo?q=%23%E4%BD%95%E7%8C%B7%E5%90%9B%E5%A5%9A%E6%A2%A6%E7%91%B6%E5%A9%9A%E7%A4%BC%E6%AC%A2%E8%BF%8E%E6%99%9A%E5%AE%B4%23"
    },
    {
        "热点话题": "茶饮早餐大战 / 茶饮行业趋势",
        "来源渠道": ["36氪"],
        "话题类别": "文旅美食",
        "热度指数": "36氪热榜第2",
        "热度指数数值": 500000,
        "关联地点": "全国",
        "关联旅游景点": "茶饮文化旅游目的地",
        "旅游商机分析": "茶饮行业话题可借势做「城市茶饮地图」「网红茶饮探店之旅」等美食旅游内容。",
        "优先级": "中",
        "备注": "📎https://36kr.com/p/3832529606797193"
    },
    # === 低优先级 ===
    {
        "热点话题": "南京大学首位没有毕业论文的博士答辩通过",
        "来源渠道": ["知乎热榜"],
        "话题类别": "教育",
        "热度指数": "知乎207万",
        "热度指数数值": 2070000,
        "关联地点": "南京",
        "关联旅游景点": "",
        "旅游商机分析": "教育话题，旅游关联度低。可微小借势「南京高校研学游」。",
        "优先级": "低",
        "备注": "📎https://www.zhihu.com/question/2044477538424943494"
    },
    {
        "热点话题": "解放军代表质问：日本何时道歉",
        "来源渠道": ["今日头条"],
        "话题类别": "国际外交",
        "热度指数": "头条705万",
        "热度指数数值": 7053722,
        "关联地点": "日本/中国",
        "关联旅游景点": "",
        "旅游商机分析": "国际政治话题，对旅游影响负面（可能影响赴日旅游意愿）。可反向借势推广国内红色旅游/爱国主义旅游线路。",
        "优先级": "低",
        "备注": "📎https://www.toutiao.com/trending/7645476236138971177/"
    },
    {
        "热点话题": "景区辟谣游客在水源地洗澡",
        "来源渠道": ["抖音"],
        "话题类别": "社会民生",
        "热度指数": "抖音773万",
        "热度指数数值": 7730000,
        "关联地点": "未明确",
        "关联旅游景点": "",
        "旅游商机分析": "景区舆情话题，可借势做「文明旅游倡议」「景区环保指南」等内容。但主要是负面内容，需小心处理。",
        "优先级": "低",
        "备注": "📎https://www.douyin.com/hot"
    },
]

print(f"\n[Data] 准备插入 {len(records)} 条记录")

# ===== 8. 批量插入 =====
batch_size = 10
total = 0
for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    payload = {"records": [{"fields": r} for r in batch]}
    resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create', payload)
    if resp.get('code') == 0:
        total += len(batch)
        print(f"[Insert] ✅ 第{i//batch_size+1}批({len(batch)}条) OK")
    else:
        print(f"[Insert] ❌ 第{i//batch_size+1}批失败: {resp.get('msg','')[:100]}")
    time.sleep(0.5)

print(f"\n[Summary] 共写入 {total}/{len(records)} 条记录")

# ===== 9. 设置公开权限 =====
# 所有人可编辑
perm_resp = api('PATCH', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/public?type=bitable',
                {"external_access_entity": "open", "security_entity": "anyone_can_view", "comment_entity": "anyone_can_view", "share_entity": "anyone_can_view", "link_share_entity": "anyone_can_view", "invite_external": True})
print(f"[Permission] public: {perm_resp.get('code')}")

# 添加公开成员
member_resp = api('POST', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/members?type=bitable',
                  {"member_type": "openid", "member_id": "ou_0", "perm": "full_access"})
print(f"[Member] everyone: {member_resp.get('code')}")

print("\n" + "="*60)
print(f"✅ 完成! Bitable URL:")
print(f"https://q7yllltm5t.feishu.cn/base/{APP_TOKEN}")
print("="*60)
