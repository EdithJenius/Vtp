# -*- coding: utf-8 -*-
"""优化主数据表: 关联地点/景点 改为具体城市,拒绝「全国」"""
import urllib.request, json, os, configparser

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.openclaw/config.toml"))
app_token = None

def get_token():
    global app_token
    aid = cfg["provider.feishu"]["appId"].strip('"')
    sec = cfg["provider.feishu"]["appSecret"].strip('"')
    body = json.dumps({"app_id": aid, "app_secret": sec}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as f:
        app_token = json.loads(f.read().decode())["tenant_access_token"]

get_token()

def call_api(method, url, body=None):
    h = {"Authorization": "Bearer " + app_token, "Content-Type": "application/json"}
    d = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=d, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=15) as f:
        return json.loads(f.read().decode())

APP = "Pnk9bARvQaVUh5sUMjIcyhF8n4b"
TID = "tblV1Sh6E2hQmt9F"

r = call_api("GET", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TID}/records?page_size=50")
items = r.get("data", {}).get("items") or []

# 话题名 -> (新关联地点, 新关联景点, 新商机分析(可选))
updates = {
    "菲律宾群岛7.9级地震": (
        "菲律宾(隐患);推荐避险:昆明/大理/丽江",
        "昆明滇池、大理古城、丽江古城",
        "菲律宾地震+海啸预警,沿海海岛游(长滩/宿务)短期退订潮。替代方案:国内避暑游——云南线(昆明-大理-丽江)6-8月气温20-25°C,适合暑期出游"
    ),
    "2026高考（历史/物理/作文/数学）": (
        "三亚、成都、重庆、长沙、西安、大理",
        "三亚蜈支洲岛、成都大熊猫基地、长沙橘子洲、西安大唐不夜城",
        None
    ),
    "女孩考完数学自信估分149到150": (
        "北京、西安、曲阜",
        "清华大学/北京大学、西安古城墙、曲阜三孔",
        "学霸人设+考试逆袭话题。可借势推「名校研学营」「学霸同款线路」:北京清北研学/西安历史研学/曲阜国学夏令营"
    ),
    "NBA总决赛G3 / 马刺vs尼克斯": (
        "观赛:美国纽约;国内替代:成都、新疆、云南",
        "纽约麦迪逊广场花园、成都凤凰山体育公园、新疆天山户外徒步",
        "NBA总决赛带动体育旅游。国内替代方向:成都户外运动(骑行/徒步)、新疆山地探险、云南高原训练营"
    ),
    "上海最有性价比的旅游 骑行": (
        "上海、成都、杭州、厦门",
        "上海浦东滨江骑行道、成都绿道、杭州西湖骑行线、厦门环岛路",
        None
    ),
    "燃油车价格雪崩 / 地摊设备暴涨600%": (
        "长沙、重庆、成都、西安、广州、柳州",
        "长沙太平街夜市、重庆解放碑夜市、成都玉林路、西安回民街",
        "消费降级+地摊经济爆发→「穷游」「性价比旅行」需求上升。推介夜市美食主题:长沙/重庆/成都/西安/柳州(低消费高体验)"
    ),
    "发现外星生命须立即通报联合国": (
        "宁夏中卫·沙坡头、青海茶卡盐湖、西藏阿里、云南丽江",
        "沙坡头星空营地、茶卡盐湖星空之境、阿里天文台、丽江高美古天文台",
        "外星话题借势→「暗夜星空旅游」正当时。暑期亲子观星研学:宁夏沙坡头/青海茶卡/云南丽江/西藏阿里"
    ),
    "AI开始抢酒店流量分配权 / 腾讯元宝砸低端旅行社饭碗": (
        "杭州、深圳、北京、上海",
        "杭州阿里/文远知行科技园、深圳腾讯滨海大厦、北京中关村、上海张江AI园区",
        "AI+旅游行业趋势。①关注AI旅游创新产品②AI工具培训③「AI如何帮旅行社转型」内容输出。推荐城市:杭州(阿里)/深圳(腾讯)/北京(百度)"
    ),
    "美加墨世界杯开赛在即，墨西哥城酒店热度+50%": (
        "墨西哥城、洛杉矶、纽约、多伦多",
        "阿兹特克体育场、SoFi体育场、大都会体育场",
        None
    ),
    "贵州山里长出旅游新爆款": (
        "贵州榕江、黔东南、铜仁、兴义",
        "榕江村超球场、肇兴侗寨、梵净山、万峰林",
        None
    ),
    "北京商旅酒店进入价格战 / 再不做研学+微度假更难": (
        "北京",
        "故宫、中国科技馆、清华大学、首钢园",
        None
    ),
    "男子夜班关闭门窗体温飙41度去世": (
        "推荐避险:六盘水、贵阳、昆明、大理、长白山",
        "六盘水乌蒙大草原、贵阳天河潭、大理洱海、长白山天池",
        "高温安全事件→避暑游刚需。推荐:六盘水(中国凉都19°C)/贵阳/昆明/大理/长白山。推避暑亲子套餐"
    ),
    "地摊设备暴涨600%，夜市摆摊大军回来": (
        "长沙、重庆、成都、西安、南宁",
        "长沙四方坪夜市、重庆较场口夜市、成都建设巷夜市、西安洒金桥夜市",
        None
    ),
    "清洁低碳氢煤混烧技术重大突破": (
        "合肥、深圳、酒泉",
        "合肥科学岛、深圳新能源科技展、酒泉卫星发射中心",
        "科技类话题,关联度较低。可做科技研学/科普内容素材:合肥科学岛/深圳新能源/酒泉航天城"
    ),
    "韩国股市 / A股行情": (
        "韩国(汇率优势);国内替代:济州岛、首尔",
        "济州岛汉拿山、首尔明洞",
        "关注韩元汇率变化。如有汇率优势可推韩国短线出境游(济州岛免签/首尔购物)。国内替代:海南免税购物"
    ),
}

count = 0
for item in items:
    fld = item.get("fields", {})
    topic = fld.get("热点话题", "")
    if topic in updates:
        new_loc, new_spots, new_analysis = updates[topic]
        rid = item["record_id"]
        fields = {"关联地点": new_loc, "关联旅游景点": new_spots}
        if new_analysis:
            fields["旅游商机分析"] = new_analysis
        call_api("PUT",
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TID}/records/{rid}",
            {"fields": fields})
        count += 1
        print(f"  ✓ {topic[:20]:20s} → {new_loc[:30]}")

print(f"\n更新完成: {count}/{len(items)}条")
