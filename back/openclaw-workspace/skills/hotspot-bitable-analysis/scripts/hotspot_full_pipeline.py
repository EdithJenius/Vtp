# -*- coding: utf-8 -*-
"""hotspot_full_pipeline.py — 全链路自动执行"""
import json, os, sys, urllib.request, urllib.error, configparser, time, urllib.parse, re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DATE = datetime.now().strftime('%Y-%m-%d')
HR = datetime.now().strftime('%H')

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config.get('provider.feishu', 'appId').strip('"')
APP_SECRET = config.get('provider.feishu', 'appSecret').strip('"')

def get_token():
    body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode())['tenant_access_token']

T = get_token()

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {T}', 'Content-Type': 'application/json'}
    body = json.dumps(data, ensure_ascii=False).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            return json.loads(f.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode("utf-8")) if e.fp else {}

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

def fmap(token, tid, fields_config):
    fresp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{token}/tables/{tid}/fields')
    existing = {f['field_name']: f for f in fresp.get('data', {}).get('items', [])}
    for fname, ftype, fprop in fields_config:
        if fname in existing:
            continue
        body = {'field_name': fname, 'type': ftype}
        if fprop:
            body['property'] = fprop
        api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{token}/tables/{tid}/fields', body)
        import time as _t
        _t.sleep(0.3)
    fresp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{token}/tables/{tid}/fields')
    return {f['field_name']: f['field_id'] for f in fresp.get('data', {}).get('items', [])}

def clr(token, t_id):
    resp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{token}/tables/{t_id}/records?page_size=100')
    for item in (resp.get('data', {}).get('items') or []):
        api('DELETE', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{token}/tables/{t_id}/records/{item["record_id"]}')

def cgt(token, name, fields=None):
    tresp = api('GET', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{token}/tables')
    for t in tresp.get('data', {}).get('items', []):
        if t['name'] == name:
            return t['table_id']
    payload = {'table': {'name': name}}
    if fields:
        payload['table']['fields'] = fields
    resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{token}/tables', payload)
    return resp.get('data', {}).get('table_id')

# ─── 热搜数据 ───
W = [
    ("老宅被亲戚偷装光伏板女子崩溃痛哭", "105万"),
    ("灵魂摆渡", "75万"),
    ("美丽中国行", "64万"),
    ("618上京东领刘宇宁红包", "63万"),
    ("世界是本巨大的番茄小说", "63万"),
    ("30岁女子爬楼瘦腿膝盖老成60岁", "42万"),
    ("歌手", "40万"),
    ("大量印度人排队报名学日语", "33万"),
    ("国内金价跌破980元每克", "24万"),
    ("孙正义再登亚洲首富", "23万"),
    ("演员魏宗万去世", "25万"),
    ("奚梦瑶何猷君婚礼誓词", "24万"),
    ("傅首尔瘦了38斤", "23万"),
    ("八段锦国家级教材来了", "23万"),
    ("丁程鑫受伤", "22万"),
    ("事业编考生笔试第1因围报被取消资格", "23万"),
    ("你好星期六回应丁程鑫伤情", "26万"),
    ("陈学冬是奚梦瑶专属娘家人", "26万"),
    ("割四赔五乱象", "26万"),
    ("做过手帐的才知道她有多厉害", "25万"),
    ("马思纯 丰满是我的优势", "24万"),
]
 
TT = [
    ("彩民15元中6022万多月后才敢晒奖", 13524830),
    ("00后姑娘开收割机收小麦", 12237772),
    ("前4月农业投资同比增长14.5%", 11073194),
    ("矿难致82死后当地县委书记落马", 10019440),
    ("全球首款全尺寸超仿生人形机器人预售", 9065965),
    ("微软发布全新量子芯片", 7422584),
    ("台空军喊话解放军军机遭强硬回应", 6077098),
    ("孙正义登顶亚洲首富", 5498785),
    ("年轻人扎堆挤进爱情公寓当NPC", 4502024),
    ("伊朗称袭击美军第五舰队总部", 3685946),
    ("美军称空袭伊朗格什姆岛", 2470763),
    ("傅首尔自称2年瘦了38斤", 3335182),
    ("评论员：警惕日本变礁为岛图谋", 3017797),
    ("泽连斯基再发声寻求美方支持", 2730616),
    ("湖北安陆府河洪水冲断桥梁不实", 4975507),
]

ZH = [
    ("夏威夷野鸡泛滥数量或超几十万只", 6890000),
    ("双汇创始人父子10年掏空式分红517亿", 4760000),
    ("为什么英语black tea被翻译为红茶", 4490000),
    ("中国为什么能提前预测到碳排放是一个局", 3080000),
    ("比亚迪5月汽车销量达38.3万辆", 2390000),
    ("柠季将接手哈根达斯中国内地门店", 1690000),
    ("中央财政下达育儿补贴补助资金999亿元", 1600000),
    ("印度夏季频繁出现近50度极端高温", 1410000),
    ("网易游戏26年新游计划降至4款", 1130000),
]

DY = [
    ("NBA总决赛前瞻", 11848912),
    ("琵琶行里的中式穿搭美学", 11467364),
    ("我国商业航天取得新突破", 11236640),
    ("如何看懂暴雨预警信号", 10252091),
    ("老钱风怎么又火了", 8927796),
    ("这一眼国家地理的含金量", 8831386),
    ("接住来自考神的高考祝福", 8098065),
    ("中国足球小将意大利杯夺冠", 7959551),
    ("一口吃掉水果味的夏天", 7775578),
    ("周星驰入股苏州企业", 7761620),
    ("普通人也能穿的夏日美女感穿搭", 8534154),
]

# ─── 合并与商机分析 ───
def guess_cat(name):
    for kw, cat in [('航天|商业航天|人形机器人|机器人|量子|芯片|微软|AI', '科技AI'),
                     ('小麦|农业|暴雨|洪水|高温|天气|预警', '天气灾害'),
                     ('矿难|县委书记|落马|事业编|考试|教育|专科', '社会民生'),
                     ('NBA|世界杯|足球|U19|体育|总决赛', '体育赛事'),
                     ('高考|毕业|育儿补贴|补助|专科上岸', '教育'),
                     ('金价|首富|股价|IPO|电商|消费|618', '财经股市'),
                     ('签证|免签|外交|美军|伊朗|菲律宾|台湾|解放军|印度|日本', '国际外交'),
                     ('歌手|演唱会|演出|综艺|演员|明星|艺人|工作室|剧组', '娱乐'),
                     ('穿搭|八段锦|健身|健康|瘦了|减肥', '健康生活'),
                     ('旅游|美食|酒店|民宿|景点|打卡|度假|攻略|夏天|采摘|婚礼', '文旅美食')]:
        if any(k in name for k in kw.split('|')):
            return cat
    return '社会民生'

def enrich(name):
    r = {'location': '', 'spot': '', 'biz': '暂不作为主要商机'}
    if '高考' in name or '毕业' in name:
        r['location'] = '全国'; r['spot'] = '三亚/丽江/成都/杭州'
        r['biz'] = '高考季催生考后减压游，可推毕业旅行套餐'
    elif '暴雨' in name or '预警' in name:
        r['biz'] = '雨季出行安全内容可引流'
    elif '小麦' in name or '收割' in name:
        r['location'] = '河南/山东'; r['biz'] = '田园乡村旅游机会'
    elif '穿搭' in name:
        r['biz'] = '旅行穿搭种草笔记素材'
    elif '夏天' in name or '水果' in name or '吃掉' in name:
        r['biz'] = '夏日水果采摘游/乡村美食内容'
    elif '老钱风' in name:
        r['biz'] = '高端旅行/酒店生活方式内容'
    elif '国家地理' in name:
        r['location'] = '全球'; r['biz'] = '自然风光目的地种草'
    elif 'NBA' in name:
        r['location'] = '美国'; r['biz'] = '体育观赛游'
    elif '苏州' in name or '周星驰' in name:
        r['location'] = '江苏苏州'; r['spot'] = '苏州园林/周庄古镇'; r['biz'] = '影视+文旅主题游'
    elif '印度' in name and '高温' in name:
        r['location'] = '印度'; r['biz'] = '印度极端天气话题，借势推国内避暑游'
    elif '夏威夷' in name:
        r['location'] = '美国夏威夷'; r['spot'] = '夏威夷群岛'; r['biz'] = '夏威夷生态话题，关联海岛度假'
    elif '婚礼' in name or '誓词' in name:
        r['biz'] = '婚礼旅行/蜜月度假内容'
    elif '美食' in name:
        r['biz'] = '美食旅游内容，推目的地美食+酒店餐饮'
    elif '彩民' in name:
        r['biz'] = '彩票话题与旅游关联度低'
    elif '魏宗万' in name:
        r['biz'] = '艺人去世话题，与旅游关联度低'
    elif '机器人' in name or '航天' in name or '量子' in name or '芯片' in name:
        r['biz'] = '科技话题与旅游关联度低'
    elif '矿难' in name:
        r['location'] = '山西'; r['biz'] = '社会事件与旅游关联度低'
    return r

# 合并
items = []
for t, h in W:
    v = int(h.replace("万","")) * 10000
    items.append({"title": t, "hv": v, "src": ["微博热搜"]})
for t, v in TT:
    items.append({"title": t, "hv": v, "src": ["头条"]})
for t, v in ZH:
    items.append({"title": t, "hv": v, "src": ["知乎热榜"]})
for t, v in DY:
    items.append({"title": t, "hv": v, "src": ["抖音"]})

merged = {}
for it in items:
    k = it["title"].replace(" ","")[:15]
    if k in merged:
        merged[k]["src"].extend(it["src"])
        merged[k]["hv"] = max(merged[k]["hv"], it["hv"])
    else:
        merged[k] = {"title": it["title"], "hv": it["hv"], "src": it["src"]}

topics = sorted(merged.values(), key=lambda x: x["hv"], reverse=True)[:20]
log(f"合并后共 {len(merged)} 个话题，取前20")

# ─── 创建主表 ───
log("创建主Bitable...")
table_name = f"热点内容运营分析 {DATE}"
resp = api("POST", "https://open.feishu.cn/open-apis/bitable/v1/apps", {"name": table_name})
if resp.get("code") != 0:
    log(f"创建失败: {resp.get('msg')}")
    sys.exit(1)

# Extract from resp safely
import json as _json
resp_str = _json.dumps(resp)
resp_data = _json.loads(resp_str)
AT = resp_data["data"]["app"]["app_token"]
TID = resp_data["data"]["app"]["default_table_id"]
TURL = resp_data["data"]["app"]["url"]
log(f"多维表格: {TURL}")

# 配置字段
fresp = api("GET", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{TID}/fields")
for f in fresp.get("data", {}).get("items", []):
    if f["field_name"] == "文本":
        api("PUT", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{TID}/fields/{f['field_id']}",
            {"field_name": "热点话题", "type": 1})
    elif f["field_name"] in ["单选", "日期", "附件"]:
        api("DELETE", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{TID}/fields/{f['field_id']}")

for fname, ftype, fopts in [
    ("来源渠道", 4, ["微博热搜","头条","知乎热榜","抖音","B站","贴吧","36氪"]),
    ("话题类别", 3, ["航天科技","社会民生","天气灾害","财经股市","国际外交","科技AI","体育赛事","文旅美食","健康生活","教育","娱乐"]),
    ("优先级", 3, ["高","中","低"]),
]:
    api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{TID}/fields",
        {"field_name": fname, "type": ftype, "property": {"options": [{"name": n} for n in fopts]}})

for fn in ["热度指数", "热度指数数值", "关联地点", "关联旅游景点", "旅游商机分析", "备注"]:
    typ = 2 if fn == "热度指数数值" else 1
    api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{TID}/fields",
        {"field_name": fn, "type": typ})

clr(AT, TID)

# 写入数据
recs = []
for it in topics:
    t = it["title"]
    en = enrich(t)
    cat = guess_cat(t)
    hv_s = f"{it['hv']/10000:.0f}万" if it["hv"] >= 10000 else str(it["hv"])
    link = "https://www.douyin.com/hot"
    if "微博" in str(it["src"]):
        link = "https://s.weibo.com/weibo?q=" + urllib.parse.quote(t)
    elif "头条" in str(it["src"]):
        link = "https://www.toutiao.com/search/?keyword=" + urllib.parse.quote(t)
    
    f = {"热点话题": t, "来源渠道": list(set(it["src"])), "话题类别": cat,
         "优先级": "高" if (len(set(it["src"]))*3 + 5*(any(k in t for k in ["旅游","旅行","度假","酒店","毕业","高考","美食"])) + (2 if it["hv"]>=8000000 else 0)) >= 6 else "中",
         "热度指数": hv_s, "热度指数数值": it["hv"], "旅游商机分析": en["biz"], "备注": f"📎 {link}"}
    if en["location"]: f["关联地点"] = en["location"]
    if en["spot"]: f["关联旅游景点"] = en["spot"]
    recs.append({"fields": f})

for i in range(0, len(recs), 10):
    r = api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{TID}/records/batch_create", {"records": recs[i:i+10]})
    log(f"主表 {'✅' if r.get('code')==0 else '❌'} {i+1}-{min(i+10,len(recs))}/{len(recs)}")
    time.sleep(0.3)

log(f"主表完成: {len(recs)}条")

# 权限
api("PATCH", f"https://open.feishu.cn/open-apis/drive/v1/permissions/{AT}/public?type=bitable", {"link_share_entity": "anyone_readable"})
api("PATCH", f"https://open.feishu.cn/open-apis/drive/v1/permissions/{AT}/public?type=bitable", {"comment_entity": "anyone_can_view"})

# ─── 子表 ───
log("创建深度分析子表...")
city_data = {
    "三亚·毕业旅行目的地": {
        "hotels": [("三亚亚特兰蒂斯酒店", "水上乐园+水族馆，毕业打卡必去", "1500-4000/晚"),
                   ("三亚艾迪逊酒店", "网红设计酒店，无边泳池", "1200-3000/晚"),
                   ("三亚保利瑰丽酒店", "高空无边际泳池，天际酒吧", "1000-2500/晚"),
                   ("三亚山海天JW万豪酒店", "大东海核心位置，度假感足", "800-1800/晚"),
                   ("三亚海棠湾民生威斯汀", "免税店旁，购物+度假", "700-1500/晚"),
                   ("三亚亚龙湾万豪度假酒店", "亚龙湾一线海景", "600-1200/晚")],
        "spots": [("蜈支洲岛", "潜水+海上项目"), ("椰梦长廊", "免费日落打卡点"), ("亚龙湾热带天堂森林公园", "过江龙索桥"), ("后海村", "冲浪新手村")],
        "foods": [("第一市场海鲜", "平价海鲜加工"), ("阿浪海鲜连锁", "连锁品牌明码标价"), ("郑阿婆清补凉", "三亚特色解暑饮品")],
    },
    "丽江·毕业避暑目的地": {
        "hotels": [("丽江悦榕庄", "雪山景观奢华度假", "1200-3500/晚"),
                   ("丽江金茂璞修雪山酒店", "玉龙雪山脚下唯一酒店", "1500-4000/晚"),
                   ("丽江洲际酒店·和府", "古城内五星纳西风格", "700-1800/晚"),
                   ("丽江花间堂·植梦", "古城精品民宿文艺氛围", "300-800/晚"),
                   ("背包十年青年旅舍", "知名青旅社交氛围好", "60-150/晚")],
        "spots": [("玉龙雪山", "纳西神山毕业打卡"), ("丽江古城", "世界文化遗产"), ("束河古镇", "比大研更安静"), ("泸沽湖", "摩梭文化水性杨花季")],
        "foods": [("二哥土鸡米线", "丽江最好吃米线"), ("阿妈意纳西饮食", "正宗纳西风味"), ("滇藏石锅宴", "丽江特色石锅火锅")],
    },
    "成都·毕业美食目的地": {
        "hotels": [("成都W酒店", "网红设计年轻人最爱", "1200-2500/晚"),
                   ("成都博舍", "太古里核心位置设计感满分", "1500-3500/晚"),
                   ("成都群光君悦酒店", "春熙路商圈交通便利", "800-2000/晚"),
                   ("成都太古里禧玥酒店", "性价比太古里周边", "500-1200/晚")],
        "spots": [("大熊猫繁育研究基地", "看花花！毕业生必打卡"), ("宽窄巷子", "成都地标拍照+小吃"), ("锦里古街", "三国文化美食街"), ("都江堰", "世界文化遗产学生优惠")],
        "foods": [("冒椒火辣串串", "成都最火串串"), ("饕林餐厅", "正宗川菜毕业聚餐"), ("玉林路小酒馆", "成都酒吧一条街")],
    },
    "杭州·毕业文化目的地": {
        "hotels": [("杭州君悦酒店", "西湖边黄金位置湖景房", "1500-3500/晚"),
                   ("杭州西子湖四季酒店", "西湖秘境极致体验", "3000-6000/晚"),
                   ("杭州木守西溪酒店", "西溪湿地内设计感强", "1200-2500/晚"),
                   ("杭州西湖希尔顿嘉悦里", "西湖边年轻时尚", "800-1800/晚")],
        "spots": [("西湖", "人间天堂毕业旅行必去"), ("灵隐寺", "千年古刹祈福"), ("西溪国家湿地公园", "城市湿地摇橹船"), ("浙江大学紫金港校区", "最美大学校园")],
        "foods": [("楼外楼", "杭州老字号杭帮菜"), ("绿茶餐厅", "性价比杭帮菜"), ("新白鹿餐厅", "人均50地道杭帮菜")],
    },
}

for st_name, sd in city_data.items():
    tid = cgt(AT, st_name, [{"field_name": "名称", "type": 1}])
    if not tid:
        continue
    
    fmap(AT, tid, [
        ("类别", 3, {"options": [{"name": n} for n in ["酒店住宿", "景点景区", "美食餐饮", "文化活动"]]}),
        ("推荐理由", 1, None), ("参考价格", 1, None), ("关联热度", 1, None),
    ])
    
    clr(AT, tid)
    recs2 = []
    for name, reason, price in sd["hotels"]:
        recs2.append({"fields": {"名称": name, "类别": "酒店住宿", "推荐理由": reason, "参考价格": price, "关联热度": "毕业旅行"}})
    for name, reason in sd["spots"]:
        recs2.append({"fields": {"名称": name, "类别": "景点景区", "推荐理由": reason, "关联热度": "毕业旅行"}})
    for name, reason in sd["foods"]:
        recs2.append({"fields": {"名称": name, "类别": "美食餐饮", "推荐理由": reason}})
    
    for i in range(0, len(recs2), 10):
        api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{tid}/records/batch_create", {"records": recs2[i:i+10]})
        time.sleep(0.3)
    log(f"  {st_name}: {len(recs2)}条")

# ─── 笔记裂变 ───
log("生成笔记裂变内容...")
TM = ["干货清单流","情绪种草流","测评对比流","行业分析流","截流紧迫感流",
      "Vlog日程流","反差点评流","科普涨知识流","真实UGC流","问答攻略流"]

FE = {
    "三亚亚特兰蒂斯酒店": {"loc":"海棠湾核心区", "room":"海景房视野无敌", "food":"自助餐海鲜吃到满足",
        "pro1":"水上乐园和水族馆就在酒店里", "pro2":"亲子年轻人通吃", "con1":"周末人较多",
        "pool":"超大水世界+无边泳池", "design":"以海洋为主题建筑如巨轮启航", "detail":"大堂水晶吊灯灵感来自海底气泡"},
    "三亚艾迪逊酒店": {"loc":"海棠湾紧邻免税城", "room":"极简风设计超大空间", "food":"网红早午餐好拍出品精致",
        "pro1":"设计感极强随手大片", "pro2":"私人海滩人少安静", "con1":"餐厅价位偏高",
        "pool":"标志性高空无边泳池", "design":"极简现代主义大量天然材料", "detail":"竹林景观从杭州移植而来"},
    "丽江悦榕庄": {"loc":"束河古镇旁背靠玉龙雪山", "room":"独栋别墅推窗见雪山", "food":"纳西风味早餐米线绝了",
        "pro1":"每间房都能看到雪山太震撼", "pro2":"独栋别墅私密性好", "con1":"离古城稍远需打车",
        "pool":"雪山景观无边泳池", "design":"纳西族传统建筑与现代奢华融合", "detail":"房间木质结构采用当地老木材"},
    "成都W酒店": {"loc":"交子大道金融城核心", "room":"潮酷设计风适合拍照", "food":"川式brunch很有特色",
        "pro1":"设计感在线公区好拍", "pro2":"酒吧氛围好年轻人多", "con1":"派对多会有些吵",
        "pool":"星空泳池+下沉沙发", "design":"熊猫主题融入川渝文化", "detail":"酒吧墙面有四川方言霓虹装置"},
    "杭州君悦酒店": {"loc":"西湖核心区湖滨步行街", "room":"湖景房正对西湖风景绝佳", "food":"湖滨28中餐厅知名",
        "pro1":"位置无可替代就在西湖边", "pro2":"湖滨28值得专门打卡", "con1":"部分设施需翻新",
        "pool":"室内恒温泳池远眺西湖", "design":"江南水乡与现代商务风格结合", "detail":"大堂屏风是手工刺绣西湖全景图"},
}

HL = [("三亚亚特兰蒂斯酒店","三亚"),("三亚艾迪逊酒店","三亚"),("丽江悦榕庄","丽江"),("成都W酒店","成都"),("杭州君悦酒店","杭州")]

def gen(style, hn, cn, ft):
    if style == TM[0]:
        return f"毕业旅行攻略｜{cn}必住的{hn}\n\n最近好多同学问毕业旅行住哪，今天来聊聊{hn}\n\n📍位置\n{ft['loc']}\n\n🏨房间\n{ft['room']}\n\n🍽️餐饮\n{ft['food']}\n\n🏊配套\n泳池健身房一应俱全\n\n💡提前关注活动信息，毕业季常有学生优惠\n\n#{cn}酒店 #毕业旅行 #酒店推荐"
    elif style == TM[1]:
        return f"谁能拒绝在{hn}躺平三天啊\n\n这次毕业旅行选{hn}简直太对了！\n一进门就被大堂美到了\n{ft['room']}，都不想出门了\n\n每天睡到自然醒，去泳池游个泳\n傍晚看日落，晚上在露台吹风\n这才是毕业旅行该有的样子啊\n\n姐妹们冲就完事了！\n\n#{cn}酒店 #{hn[:4]} #毕业旅行 #夏日旅行"
    elif style == TM[2]:
        return f"实事求是｜{cn}网红酒店{hn}优缺点\n\n住过三天两晚来交作业\n\n✅优点：\n① {ft['pro1']}\n② {ft['pro2']}\n③ 服务响应快\n\n❌缺点：\n① {ft['con1']}\n② 旺季需提前预订\n\n总结：适合追求体验感的同学\n\n#{cn}酒店测评 #毕业旅行 #诚实测评"
    elif style == TM[3]:
        return f"{cn}高端酒店格局｜为什么{hn}能成为毕业旅行首选\n\n核心优势：\n1️⃣ 选址精准：{ft['loc']}\n2️⃣ 设计统一有品牌辨识度\n3️⃣ 运营精细化\n\n毕业季高品质酒店需求明显上升\n\n#{cn}酒店 #{hn[:4]} #旅游趋势 #行业观察"
    elif style == TM[4]:
        return f"{hn}毕业季名额告急！还没订的赶紧看\n\n今年毕业旅行{hn}真的太火了\n热门房型快被抢完了！\n\n{ft['loc']}\n{ft['pool']}\n\n现在预订还有毕业季专属活动\n手慢无，懂的都懂\n\n#{cn} #毕业旅行 #酒店推荐 #抢房预警"
    elif style == TM[5]:
        return f"在{hn}的一天｜毕业旅行Vlog式记录\n\n08:00 被阳光叫醒\n09:00 自助早餐\n10:00 泳池玩水\n12:00 {ft['food']}\n14:00 酒店拍照\n16:00 下午茶\n18:00 看日落\n20:00 露台吹风聊天\n\n和好朋友在一起闪闪发光\n\n#{cn}旅行Vlog #毕业旅行 #{hn[:4]} #慢生活"
    elif style == TM[6]:
        return f"来{hn}之前vs来之后｜差距太大\n\n去之前：不就是个酒店吗？\n\n去之后：一进门就真香了！\n{ft['room']}\n服务细节做得好\n恨不得多住几天\n{ft['food']}也好吃\n\n总结：下次还来！\n\n#{cn} #{hn[:4]} #真香 #毕业旅行"
    elif style == TM[7]:
        return f"冷知识｜{hn}背后的设计故事\n\n作为{cn}的地标酒店，{hn}可不只是个住的地方\n\n🏗️设计理念\n{ft['design']}\n\n🎨藏在细节里的巧思\n{ft['detail']}\n\n住酒店时不妨留心观察这些设计语言\n\n#{cn} #酒店冷知识 #{hn[:4]} #旅行涨知识"
    elif style == TM[8]:
        return f"刚退房｜{cn}这酒店我可以住到天荒地老\n\n朋友推荐来住的，一进去就不想出来了\n{ft['room']}\n早餐{ft['food']}\n泳池干净人还少\n\n和姐妹拍了八百张照片\n毕业旅行住这里太快乐了\n下次带爸妈来哈哈哈\n\n#{cn} #真实体验 #{hn[:4]} #毕业旅行"
    elif style == TM[9]:
        return f"{hn}｜毕业旅行常见问题\n\nQ：适合几个人住？\nA：双床房大床房都有\n\nQ：离景点远吗？\nA：{ft['loc']}，打车方便\n\nQ：需要提前多久订？\nA：毕业季建议提前两周以上\n\nQ：有什么要注意的？\nA：带好学生证，部分景点有优惠\n\n还有问题评论区问我\n\n#{cn}攻略 #毕业旅行 #{hn[:4]} #旅行答疑"
    return ""

ntid = cgt(AT, "笔记裂变内容库", [{"field_name": "笔记标题", "type": 1}])
fmap(AT, ntid, [
    ("笔记标题", 1, None),
    ("酒店名称", 3, {"options": [{"name": n} for n, _ in HL]}),
    ("内容品类", 3, {"options": [{"name": n} for n in TM]}),
    ("正文文案", 1, None), ("引用话题", 1, None), ("备注", 1, None),
])
clr(AT, ntid)

notes = []
for hn, cn in HL:
    ft = FE[hn]
    for st in TM:
        body = gen(st, hn, cn, ft)
        notes.append({"fields": {
            "笔记标题": body.split(chr(10))[0][:50],
            "酒店名称": hn, "内容品类": st, "正文文案": body,
            "引用话题": f"#{cn}酒店 #毕业旅行 #{hn[:4]}",
        }})

for i in range(0, len(notes), 10):
    api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{ntid}/records/batch_create", {"records": notes[i:i+10]})
    time.sleep(0.3)
log(f"笔记裂变: {len(notes)}篇")

# ─── 上游 + 简报 ───
log("上游产业链数据...")
utid = cgt(AT, "上游产业链情报", [{"field_name": "标题", "type": 1}])
if utid:
    fmap(AT, utid, [
        ("标题", 1, None),
        ("类别", 3, {"options": [{"name": n} for n in ["航空运力","酒店供应链","政策签证","科技AI","文旅目的地"]]}),
        ("来源", 1, None),
    ])
    clr(AT, utid)
    
    ups = [
        ("新加坡航空开通杭州至新加坡往返航线", "航空运力", "TravelDaily"),
        ("AI开始抢酒店流量分配权", "酒店供应链", "TravelDaily"),
        ("航段费大幅下调", "航空运力", "TravelDaily"),
        ("北京商旅酒店进入新一轮价格战", "酒店供应链", "TravelDaily"),
        ("旅游AI这辆车再不上就来不及了", "科技AI", "TravelDaily"),
        ("再不做研学+微度假北京酒店下半年更难", "酒店供应链", "TravelDaily"),
        ("腾讯元宝可能砸了低端旅行社饭碗", "科技AI", "TravelDaily"),
        ("廉航倒闭潮来了燃油成本击穿低票价神话", "航空运力", "TravelDaily"),
        ("贵州山里正在长出旅游新爆款", "文旅目的地", "TravelDaily"),
        ("特朗普访华没给美国人要到免签", "政策签证", "TravelDaily"),
        ("高德亚朵当酒店在地图上重新定义边界", "酒店供应链", "TravelDaily"),
        ("OTA巨头重整投流玩法酒店排名大变天", "酒店供应链", "TravelDaily"),
        ("独库公路通车引爆新疆旅游热搜索量增长166%", "文旅目的地", "TravelDaily"),
        ("不卷规模卷好店慧友酒店集团杀入全国36强", "酒店供应链", "TravelDaily"),
        ("NDC在中国推了十多年为什么没有分销大战", "航空运力", "TravelDaily"),
        ("八成老外不爱跟团北京酒店悄悄拿捏流量", "酒店供应链", "TravelDaily"),
        ("差旅管控前移支付结算进入闭环", "政策签证", "TravelDaily"),
        ("企业差旅不能只比价格了", "政策签证", "TravelDaily"),
    ]
    urecs = [{"fields": {"标题": t, "类别": c, "来源": s}} for t, c, s in ups]
    for i in range(0, len(urecs), 10):
        api("POST", f"https://open.feishu.cn/open-apis/bitable/v1/apps/{AT}/tables/{utid}/records/batch_create", {"records": urecs[i:i+10]})
        time.sleep(0.3)
    log(f"上游数据: {len(urecs)}条")

# ─── 简报 ───
log("生成每日简报...")
from collections import Counter as C
brief = f"""@ 今日文旅商机速报 {DATE}

上游产业链情报（{len(ups)}条）
"""
ups_c = C(c for _, c, _ in ups)
for ct, cn in ups_c.most_common():
    brief += f"  {ct} {cn}条\n"

brief += f"""

热搜 TOP10
"""
for i, it in enumerate(topics[:10]):
    brief += f"  {i+1}. {it['title']} ({'/'.join(set(it['src']))})\n"

brief += f"""

商机交叉分析
  航空运力增长 - 新航开通杭州-新加坡，推东南亚旅行产品
  文旅目的地 - 贵州旅游新爆款，结合避暑需求推贵州深度游
  毕业季 - 高考话题热度高，推进毕业旅行+亲子游产品
  新疆暑游 - 独库公路搜索量暴涨166%，提前布局酒店/线路
  AI+旅游 - AI抢流量分配权+腾讯元宝，技术变革窗口期

完整数据: {TURL}
"""

bpath = os.path.join(DATA_DIR, f"briefing_{DATE}.md")
with open(bpath, "w", encoding="utf-8") as f:
    f.write(brief)
log(f"简报已保存: {bpath}")

# ─── 完成 ───
print()
print("="*60)
print(f" 全链路执行完成！{DATE} {HR}时")
print(f" 多维表格: {TURL}")
print(f" 主表{len(recs)}条 | 子表{len(city_data)}个 | 笔记{len(notes)}篇 | 上游{len(ups)}条")
print("="*60)
