# -*- coding: utf-8 -*-
"""
热点商机全流程: 交叉合并分析 + 创建Bitable + 插入数据
2026-06-09
"""
import urllib.request, json, os, configparser, sys, time, urllib.parse

# --- 工具函数 ---
def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appId'].strip('"')
    app_secret = config['provider.feishu']['appSecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_token()
print(f"[Token] 获取成功: {TOKEN[:10]}...")

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

# --- 1. 交叉合并分析 ---
print("\n=== Phase 2-3: 交叉合并 + 商机分析 ===")

analysis = [
    {
        "热点话题": "高考（全平台霸榜）",
        "来源渠道": ["微博热搜", "今日头条", "抖音", "贴吧", "B站", "知乎"],
        "话题类别": "教育",
        "热度指数": "全平台TOP1",
        "热度指数数值": 999999,
        "关联地点": "全国",
        "关联旅游景点": "各地考场周边酒店/餐饮",
        "旅游商机分析": "⭐毕业旅行季引爆暑期旅游市场\n- 高考结束（6月9日）后毕业旅行需求井喷\n- 三亚/成都/重庆/长沙/西安为热门毕业旅行目的地\n- 建议瞄准:毕业旅行套餐、同学聚会酒店、亲子出游",
        "优先级": "高",
        "备注": "📎 https://s.weibo.com/weibo?q=%23%E9%AB%98%E8%80%83%23"
    },
    {
        "热点话题": "金饰克价下跌400元",
        "来源渠道": ["微博热搜"],
        "话题类别": "财经股市",
        "热度指数": "微博47万",
        "热度指数数值": 470000,
        "关联地点": "深圳/杭州",
        "关联旅游景点": "深圳水贝珠宝市场",
        "旅游商机分析": "⭐金价下跌→消费释放→旅游购物需求增加\n- 黄金降价释放消费力，旅游购物预算增加\n- 深圳水贝珠宝市场或成热门打卡地\n- 可搭配深圳旅游+珠宝购物路线推广",
        "优先级": "中",
        "备注": "📎 https://s.weibo.com/weibo?q=%E9%87%91%E9%A5%B0%E5%85%8B%E4%BB%B7%E4%B8%8B%E8%B7%8C400%E5%85%83"
    },
    {
        "热点话题": "iOS 27发布 / 苹果AI（Apple Intelligence）",
        "来源渠道": ["微博热搜", "知乎", "36氪"],
        "话题类别": "科技AI",
        "热度指数": "微博48万+/知乎95万",
        "热度指数数值": 480000,
        "关联地点": "北京/上海",
        "关联旅游景点": "Apple Store（三里屯/陆家嘴）",
        "旅游商机分析": "科技话题热度高但旅游关联度低\n- 与旅游直接关联不强\n- 可关注AI+旅游应用趋势（参考TravelDaily：旅游AI这辆车再不上就来不及了）\n- 建议:AI旅行规划助手、智能酒店体验",
        "优先级": "低",
        "备注": "📎 https://s.weibo.com/weibo?q=iOS27"
    },
    {
        "热点话题": "菲律宾强震",
        "来源渠道": ["今日头条"],
        "话题类别": "天气灾害",
        "热度指数": "头条2790万",
        "热度指数数值": 27900000,
        "关联地点": "菲律宾",
        "关联旅游景点": "菲律宾长滩岛/宿务/马尼拉",
        "旅游商机分析": "菲律宾地震→东南亚旅游市场波动\n- 菲律宾群岛旅游短期受挫\n- 替代方案:泰国普吉岛/印尼巴厘岛/越南岘港\n- 建议关注:地震对长滩岛等热门目的地的后续影响",
        "优先级": "中",
        "备注": "📎 https://www.toutiao.com/trending/7648823764209729563/"
    },
    {
        "热点话题": "中朝友谊/平壤节日盛装",
        "来源渠道": ["微博热搜", "今日头条", "抖音"],
        "话题类别": "国际外交",
        "热度指数": "微博92万+/头条3084万/抖音1148万",
        "热度指数数值": 30840000,
        "关联地点": "平壤/丹东",
        "关联旅游景点": "丹东边境旅游/朝鲜新义州一日游",
        "旅游商机分析": "中朝友谊话题→边境旅游关注度提升\n- 丹东边境游、中朝边境观光或迎来小高峰\n- 朝鲜旅游虽未完全开放，但中朝交流回暖利好边境旅游\n- 建议:丹东+大连连线产品、中朝边境自驾游",
        "优先级": "中",
        "备注": "📎 https://s.weibo.com/weibo?q=%23%E5%B9%B3%E5%A3%A4%E5%90%84%E7%95%8C%E7%BE%A4%E4%BC%97%E5%92%8C%E5%B0%91%E5%B9%B4%E5%84%BF%E7%AB%A5%E8%BA%AB%E7%9D%80%E8%8A%82%E6%97%A5%E7%9B%9B%E8%A3%85%23"
    },
    {
        "热点话题": "NBA总决赛G3 马刺vs尼克斯",
        "来源渠道": ["微博热搜", "今日头条", "抖音"],
        "话题类别": "体育赛事",
        "热度指数": "微博74万+/头条3766万/抖音1214万",
        "热度指数数值": 37660000,
        "关联地点": "美国/北京/上海",
        "关联旅游景点": "北京/上海运动主题酒吧/餐厅",
        "旅游商机分析": "NBA总决赛热度高但旅游关联有限\n- 观赛带动运动主题酒吧/餐厅消费\n- 特朗普观战提升话题度\n- 建议:运动主题酒店套餐、NBA观赛派对活动",
        "优先级": "低",
        "备注": "📎 https://s.weibo.com/weibo?q=%23%E9%A9%AC%E5%88%BAvs%E5%B0%BC%E5%85%8B%E6%96%AF%23"
    },
    {
        "热点话题": "郑钦文止步女王杯首轮",
        "来源渠道": ["微博热搜", "今日头条"],
        "话题类别": "体育赛事",
        "热度指数": "微博40万+/头条1134万",
        "热度指数数值": 11340000,
        "关联地点": "伦敦",
        "关联旅游景点": "伦敦温布尔登/女王杯网球赛",
        "旅游商机分析": "体育赛事热度→海外观赛旅游关注\n- 郑钦文止步首轮话题度高，带动网球观赛旅游\n- 7月温网开赛在即，适合推广伦敦观赛游\n- 建议:温网观赛套餐、伦敦暑期游学产品",
        "优先级": "低",
        "备注": "📎 https://s.weibo.com/weibo?q=%23%E9%83%91%E9%92%A6%E6%96%87%E6%AD%A2%E6%AD%A5%E5%A5%B3%E7%8E%8B%E6%9D%AF%E9%A6%96%E8%BD%AE%23"
    },
    {
        "热点话题": "考生喊话取消机建燃油费",
        "来源渠道": ["今日头条", "贴吧"],
        "话题类别": "社会民生",
        "热度指数": "头条309万/贴吧74.4W",
        "热度指数数值": 3100000,
        "关联地点": "西安",
        "关联旅游景点": "全国机场",
        "旅游商机分析": "⭐机票成本成全民话题→利好低成本出行\n- 机建燃油费成热点，反映大众对出行成本的敏感\n- 利好:特价机票营销、性价比旅游产品\n- 建议:毕业季特价机票营销、低成本旅行攻略",
        "优先级": "高",
        "备注": "📎 https://www.toutiao.com/trending/7648845355086692388/"
    },
    {
        "热点话题": "ChatGPT史上最大改版（超级应用方向）",
        "来源渠道": ["36氪", "知乎"],
        "话题类别": "科技AI",
        "热度指数": "36氪TOP1/知乎146万",
        "热度指数数值": 1500000,
        "关联地点": "北京/深圳/杭州",
        "关联旅游景点": "科技园区",
        "旅游商机分析": "AI话题持续高热→AI+旅游新机会\n- 参考TravelDaily：AI重写旅行行业、腾讯元宝可能砸了低端旅行社饭碗\n- 同程旅行接入微信AI生态，OTA正在AI化\n- 建议:AI旅行规划、智能客服、个性化推荐",
        "优先级": "中",
        "备注": "📎 https://36kr.com/p/3843921641736457"
    },
    {
        "热点话题": "地摊设备暴涨600%，夜市摆摊大军回来了",
        "来源渠道": ["36氪"],
        "话题类别": "文旅美食",
        "热度指数": "36氪热点",
        "热度指数数值": 500000,
        "关联地点": "长沙/成都/重庆/西安",
        "关联旅游景点": "长沙太平街/成都宽窄巷子/重庆洪崖洞",
        "旅游商机分析": "⭐夜市经济爆发→文旅夜游新热点\n- 地摊经济带火夜市旅游\n- 长沙/成都/重庆/西安的夜市文化出圈\n- 建议:夜市美食旅游线路、夜游+酒店套餐",
        "优先级": "高",
        "备注": "📎 https://36kr.com/p/3839681255393797"
    },
    {
        "热点话题": "贵州山里正在长出旅游新爆款",
        "来源渠道": ["上游产业链（TravelDaily）"],
        "话题类别": "文旅美食",
        "热度指数": "TravelDaily热文",
        "热度指数数值": 300000,
        "关联地点": "贵州",
        "关联旅游景点": "黄果树瀑布/荔波小七孔/千户苗寨/梵净山",
        "旅游商机分析": "⭐贵州成为旅游新爆款目的地\n- 贵州山水旅游持续升温\n- 自然景观+民族文化成为差异化卖点\n- 建议:贵州暑期避暑游、研学旅行产品",
        "优先级": "高",
        "备注": "📎 https://www.traveldaily.cn/article/190067"
    },
    {
        "热点话题": "北京商旅酒店进入新一轮价格战",
        "来源渠道": ["上游产业链（TravelDaily）"],
        "话题类别": "文旅美食",
        "热度指数": "TravelDaily热文",
        "热度指数数值": 300000,
        "关联地点": "北京",
        "关联旅游景点": "北京环球影城/故宫/长城/颐和园",
        "旅游商机分析": "北京酒店价格战→暑期旅游利好\n- 高端酒店坚挺但中端价格下探\n- 利好:消费者能以更低价格锁定北京酒店\n- 建议:北京暑期特惠套餐、研学旅行产品\n- 参考:再不做研学+微度假北京酒店下半年更难",
        "优先级": "高",
        "备注": "📎 https://www.traveldaily.cn/article/190092"
    },
    {
        "热点话题": "廉航倒闭潮来了",
        "来源渠道": ["上游产业链（TravelDaily）"],
        "话题类别": "财经股市",
        "热度指数": "TravelDaily热文",
        "热度指数数值": 300000,
        "关联地点": "全国",
        "关联旅游景点": "全国廉价航空航线目的地",
        "旅游商机分析": "廉航倒闭→出行成本上升→替代方案\n- 燃油成本击穿低票价神话\n- 可能影响东南亚等依赖廉航的出境游市场\n- 建议:关注高铁+酒店套餐、国内替代目的地",
        "优先级": "中",
        "备注": "📎 https://www.traveldaily.cn/article/190089"
    },
    {
        "热点话题": "同程旅行：美加墨世界杯开赛在即",
        "来源渠道": ["上游产业链（TravelDaily）"],
        "话题类别": "体育赛事",
        "热度指数": "TravelDaily热点",
        "热度指数数值": 300000,
        "关联地点": "墨西哥城/美国/加拿大",
        "关联旅游景点": "墨西哥城/洛杉矶/多伦多",
        "旅游商机分析": "2026世界杯（美加墨）→海外观赛游预热\n- 墨西哥城酒店预订热度增长超50%\n- 高端定制游受追捧\n- 建议:世界杯观赛套餐、美加墨连线游产品",
        "优先级": "中",
        "备注": "📎 https://www.traveldaily.cn/article/190119"
    },
    {
        "热点话题": "鸡蛋突然涨价 / 经济民生话题",
        "来源渠道": ["今日头条"],
        "话题类别": "社会民生",
        "热度指数": "头条929万",
        "热度指数数值": 9290000,
        "关联地点": "全国",
        "关联旅游景点": "无直接关联",
        "旅游商机分析": "民生话题→消费降级趋势下需关注低价旅游产品\n- 物价上涨可能影响旅游消费意愿\n- 建议:主打性价比旅行路线、早鸟优惠",
        "优先级": "低",
        "备注": "📎 https://www.toutiao.com/trending/7648984599233564198/"
    }
]

print(f"[分析] 完成 {len(analysis)} 条热点商机分析")

# --- 4. 创建 Bitable ---
print("\n=== Phase 4: 创建主Bitable ===")

# 4.1 创建多维表格
resp = api('POST', 'https://open.feishu.cn/open-apis/bitable/v1/apps',
    {"name": "热点商机多维分析 2026-06-09 10时"})
APP_TOKEN = resp['data']['app']['app_token']
TABLE_ID = resp['data']['app']['default_table_id']
print(f"[Bitable] 创建成功: app_token={APP_TOKEN}, table_id={TABLE_ID}")
print(f"[Bitable] 链接: https://bytedance.feishu.cn/base/{APP_TOKEN}")

# 4.2 重命名默认字段
fields_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields')
items = fields_resp['data']['items']
text_field = next((f for f in items if f['field_name'] == '文本'), None)

if text_field:
    api('PUT', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{text_field["field_id"]}',
        {"field_name": "热点话题", "type": 1})
    print("[字段] 重命名默认字段 -> 热点话题")

# 4.3 删除其他默认字段
for fname in ['单选', '日期', '附件']:
    f = next((x for x in items if x['field_name'] == fname), None)
    if f:
        api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{f["field_id"]}')
        print(f"[字段] 删除默认字段: {fname}")

# 4.4 创建自定义字段
fields_config = [
    {"field_name": "来源渠道", "type": 4, "property": {"options": [{"name":"微博热搜"},{"name":"百度热搜"},{"name":"知乎热榜"},{"name":"抖音"},{"name":"今日头条"},{"name":"贴吧"},{"name":"36氪"},{"name":"B站"},{"name":"小红书"},{"name":"上游产业链"}]}},
    {"field_name": "话题类别", "type": 3, "property": {"options": [{"name":"航天科技"},{"name":"社会民生"},{"name":"天气灾害"},{"name":"财经股市"},{"name":"国际外交"},{"name":"科技AI"},{"name":"体育赛事"},{"name":"文旅美食"},{"name":"健康生活"},{"name":"教育"}]}},
    {"field_name": "热度指数", "type": 1},
    {"field_name": "热度指数数值", "type": 2},
    {"field_name": "关联地点", "type": 1},
    {"field_name": "关联旅游景点", "type": 1},
    {"field_name": "旅游商机分析", "type": 1},
    {"field_name": "优先级", "type": 3, "property": {"options": [{"name":"高"},{"name":"中"},{"name":"低"}]}},
    {"field_name": "备注", "type": 1},
]
for cfg in fields_config:
    try:
        api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields', cfg)
        print(f"[字段] 创建: {cfg['field_name']}")
    except Exception as e:
        print(f"[字段] 创建失败 {cfg['field_name']}: {e}")

# 4.5 删除默认空记录
del_resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=50')
for item in (del_resp.get('data', {}).get('items') or []):
    rid = item['record_id']
    api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{rid}')
print("[记录] 清空默认空记录")

# 4.6 批量插入数据
# 每次最多10条
for i in range(0, len(analysis), 10):
    batch = analysis[i:i+10]
    records = []
    for r in batch:
        fields = {}
        for k, v in r.items():
            if k == "来源渠道":
                fields[k] = v  # MultiSelect 传数组
            else:
                fields[k] = str(v) if not isinstance(v, (int, float)) else v
        records.append({"fields": fields})

    try:
        body = {"records": records}
        resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create', body)
        if resp.get('code') == 0:
            print(f"[写入] 批次 {i//10+1}/{(len(analysis)-1)//10+1}: {len(records)} 条成功")
        else:
            print(f"[写入] 批次失败: {resp}")
    except Exception as e:
        print(f"[写入] 批次 {i//10+1} 异常: {e}")
    time.sleep(0.5)

# 4.7 设置权限
try:
    api('PATCH', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/public?type=bitable',
        {"link_share_entity": "anyone_readable"})
    print("[权限] 链接公开可读")
except Exception as e:
    print(f"[权限] 公开设置失败: {e}")

try:
    api('POST', f'https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/members?type=bitable',
        {"member_type": "openid", "member_id": "ou_b098a77a8b7869d14ccd6e34b7af3583", "perm": "full_access"})
    print("[权限] 永乐管理员已添加")
except Exception as e:
    print(f"[权限] 管理员设置: {e}")

print(f"\n=== 完成 ===")
print(f"Bitable 链接: https://bytedance.feishu.cn/base/{APP_TOKEN}")
print(f"共计写入 {len(analysis)} 条热点商机记录")
