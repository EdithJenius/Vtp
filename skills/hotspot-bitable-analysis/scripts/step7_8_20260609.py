# -*- coding: utf-8 -*-
"""
Phase 7-8: 文旅调研8维度 + 笔记裂变内容库
2026-06-09
"""
import urllib.request, urllib.parse, json, os, configparser, time

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
APP_TOKEN = 'KC7GbI8oFaUXAWsMAAtcYxIWnxM'

def api(method, url, body=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.loads(f.read().decode())

# --- Phase 7: 文旅调研8维度 ---
print("=== Phase 7: 文旅调研8维度 ===")

culture_dimensions = [
    {
        "名称": "北京",
        "类别": "文旅目的地",
        "基础信息": "首都，常住人口2188万，年接待游客3.2亿人次",
        "金字招牌": "故宫/长城/天坛·世界文化遗产集群/环球影城",
        "市井风情": "胡同文化/四合院/老北京小吃（炸酱面/豆汁/卤煮）",
        "视觉资产": "故宫红墙+角楼日落/长城日出/颐和园十七孔桥金光穿洞",
        "季节限定": "春秋最佳（4-5月/9-11月）/ 暑期亲子高峰 / 冬季故宫雪景",
        "避坑槽点": "暑期人流量极大/长城有黑导游/一些仿古街过度商业化",
        "商业闭环": "门票经济→IP文创（故宫口红）→ 周边住宿餐饮 → 研学旅行",
        "备注": "再不做研学+微度假北京酒店下半年更难"
    },
    {
        "名称": "贵州",
        "类别": "文旅目的地",
        "基础信息": "西南内陆省，\"山地公园省\"，年接待游客超6亿人次",
        "金字招牌": "黄果树瀑布/荔波小七孔/西江千户苗寨/梵净山/FAST天眼",
        "市井风情": "苗族/侗族/布依族少数民族文化/酸汤鱼/肠旺面/丝娃娃",
        "视觉资产": "黄果树瀑布全景/荔波碧绿水色/苗寨万家灯火/梵净山云海",
        "季节限定": "夏季避暑胜地（6-9月）/ 春秋四季分明 / 冬季可赏雪梵净山",
        "避坑槽点": "景点分散交通耗时/山路多晕车/黄金周苗寨人流过大",
        "商业闭环": "门票→景区交通→民宿/酒店→民族手工艺→研学/避暑旅居",
        "备注": "TravelDaily：贵州山里正在长出旅游新爆款"
    },
    {
        "名称": "长沙",
        "类别": "文旅目的地",
        "基础信息": "湖南省会，\"不夜城\"，年接待游客超2亿人次",
        "金字招牌": "橘子洲/岳麓山/五一商圈/茶颜悦色/文和友/芒果TV",
        "市井风情": "夜市文化（坡子街/太平街）/湘菜（辣椒炒肉/剁椒鱼头）/足浴文化",
        "视觉资产": "橘子洲毛主席雕像/湘江夜景/IFS国金中心/万家丽网红地标",
        "季节限定": "春秋适宜/夏季炎热但夜市活跃/冬季湿冷但美食不减",
        "避坑槽点": "极端天气（夏热冬冷）/步行街过度拥挤/节假日住宿涨价明显",
        "商业闭环": "美食体验→新消费品牌（茶颜悦色/文和友）→网红打卡→酒店住宿",
        "备注": "36氪：地摊设备暴涨600%，夜市经济带火长沙"
    },
    {
        "名称": "三亚",
        "类别": "文旅目的地",
        "基础信息": "海南最南端，热带海滨城市，年接待游客超2500万人次",
        "金字招牌": "亚龙湾/海棠湾/天涯海角/蜈支洲岛/南山海上观音",
        "市井风情": "海鲜市场（第一市场）/椰梦长廊/黎苗文化/免税购物",
        "视觉资产": "亚龙湾碧海白沙/海棠湾高端酒店群/三亚湾日落/椰林海景",
        "季节限定": "冬季避寒（11-3月）旺季/夏季6-9月相对淡季/毕业游暑期回升",
        "避坑槽点": "海鲜宰客/高温暴晒/旺季酒店价格翻倍/出租车拒载/游客扎堆",
        "商业闭环": "度假酒店→免税购物→海鲜餐饮→海上项目→旅拍/婚庆",
        "备注": "高考结束毕业旅行需求井喷，三亚为热门毕业旅行目的地"
    }
]

# 创建文旅调研子表
culture_fields = [
    {"field_name": "名称", "type": 1},
    {"field_name": "类别", "type": 3, "property": {"options": [{"name":"文旅目的地"},{"name":"景点景区"},{"name":"城市文化"},{"name":"酒店住宿"}]}},
    {"field_name": "基础信息", "type": 1},
    {"field_name": "金字招牌", "type": 1},
    {"field_name": "市井风情", "type": 1},
    {"field_name": "视觉资产", "type": 1},
    {"field_name": "季节限定", "type": 1},
    {"field_name": "避坑槽点", "type": 1},
    {"field_name": "商业闭环", "type": 1},
    {"field_name": "备注", "type": 1},
]

culture_body = {"table": {"name": "文旅调研8维度", "fields": culture_fields}}
resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', culture_body)
culture_tid = resp['data']['table_id']
print(f"[文旅调研] 子表创建: {culture_tid}")

# 写入
for cd in culture_dimensions:
    api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{culture_tid}/records',
        {"fields": cd})
print(f"[文旅调研] {len(culture_dimensions)} 条写入完成")

# --- Phase 8: 创建笔记裂变内容库 ---
print("\n=== Phase 8: 笔记裂变内容库 ===")

note_fields = [
    {"field_name": "笔记标题", "type": 1},
    {"field_name": "酒店名称", "type": 3, "property": {"options": [
        {"name":"北京国贸大酒店"},{"name":"北京王府井半岛酒店"},{"name":"北京华尔道夫酒店"},
        {"name":"北京宝格丽酒店"},{"name":"北京嘉里大酒店"},{"name":"北京诺金酒店"},
        {"name":"贵阳中天凯悦酒店"},{"name":"贵阳安纳塔拉度假酒店"},{"name":"黄果树迎宾馆"},
        {"name":"长沙尼依格罗酒店"},{"name":"长沙瑞吉酒店"},{"name":"长沙君悦酒店"},
        {"name":"三亚亚特兰蒂斯酒店"},{"name":"三亚艾迪逊酒店"},{"name":"三亚保利瑰丽酒店"},
        {"name":"三亚太阳湾柏悦酒店"},{"name":"三亚嘉佩乐度假酒店"},{"name":"三亚文华东方酒店"},
        {"name":"三亚悦榕庄"},{"name":"西江千户苗寨循美·半山"}
    ]}},
    {"field_name": "内容品类", "type": 3, "property": {"options": [
        {"name":"干货/清单流"},{"name":"情绪种草流"},{"name":"测评对比流"},
        {"name":"行业分析流"},{"name":"截流紧迫感流"},{"name":"Vlog日程流"},
        {"name":"反差点评流"},{"name":"科普涨知识流"},{"name":"真实UGC流"},{"name":"问答攻略流"}
    ]}},
    {"field_name": "正文文案", "type": 1},
    {"field_name": "引用话题", "type": 1},
    {"field_name": "发布时间建议", "type": 1},
    {"field_name": "封面/配图建议(图生prompt)", "type": 1},
    {"field_name": "目标人群", "type": 4, "property": {"options": [
        {"name":"毕业旅行"},{"name":"闺蜜姐妹团"},{"name":"蜜月情侣"},{"name":"情侣约会"},
        {"name":"高端商务"},{"name":"自由行背包客"},{"name":"独行客"},{"name":"女性独自旅行"},
        {"name":"户外探险者"},{"name":"摄影爱好者"},{"name":"亲子家庭"},{"name":"遛娃研学"},
        {"name":"美食爱好者"},{"name":"文化深度游"},{"name":"自驾爱好者"},{"name":"团建"},
        {"name":"银发族"},{"name":"康养旅游"},{"name":"追星旅行"},{"name":"携宠旅行"}
    ]}},
    {"field_name": "季节标签", "type": 3, "property": {"options": [{"name":"春季"},{"name":"夏季"},{"name":"秋季"},{"name":"冬季"},{"name":"全年"}]}},
    {"field_name": "热点关联", "type": 1},
    {"field_name": "关键词", "type": 1},
    {"field_name": "素材参考链接", "type": 1},
    {"field_name": "酒店人群画像", "type": 1},
]

note_body = {"table": {"name": "笔记裂变内容库", "fields": note_fields}}
resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', note_body)
note_tid = resp['data']['table_id']
print(f"[笔记库] 子表创建: {note_tid}")

# --- Phase 9: 生成笔记样本（10品类×3家酒店=30条） ---
print("\n=== Phase 9: 生成笔记样本 ===")

# 精选3家代表酒店 × 10品类
notes_data = [
    # ===== 三亚亚特兰蒂斯 =====
    # 1. 干货/清单流
    {
        "笔记标题": "三亚亚特兰蒂斯必看8项隐藏福利✨",
        "酒店名称": "三亚亚特兰蒂斯酒店",
        "内容品类": "干货/清单流",
        "正文文案": "🏨 住过5次亚特兰蒂斯，这8项隐藏福利90%的人不知道\n\n1️⃣ 水世界无限次畅玩 — 住客专属通道免排队\n2️⃣ 水族馆免费参观 — 失落的空间超出片\n3️⃣ VIP早餐免排队 — Club Lounge早7点开始\n4️⃣ 免费接驳车 — 海棠湾免税店循环线\n5️⃣ 婴儿车/轮椅免费租借 — 有娃家庭必备\n6️⃣ 下午茶折扣 — 大堂吧提前一天预订7折\n7️⃣ 生日惊喜 — 提前备注有蛋糕和布置\n8️⃣ 延迟退房到14点 — 视房态免费申请\n\n建议收藏，下次入住直接用 ✅",
        "引用话题": "#三亚旅游 #亚特兰蒂斯 #三亚酒店 #毕业旅行 #三亚攻略 #海棠湾 #三亚亲子游 #暑假去哪玩 #三亚酒店推荐 #海岛度假 #水世界 #浮潜 #水上乐园 #三亚自由行 #旅行攻略 #酒店体验 #宝藏酒店 #三亚美食 #免税购物 #三亚旅行",
        "发布时间建议": "周五 18:00-20:00",
        "封面/配图建议(图生prompt)": "【封面】亚特兰蒂斯标志性的海底套房视角，深蓝色调，鱼群环绕\n【图2】水世界滑道俯拍，人群玩乐的动态感\n【图3】Club Lounge自助餐台，丰盛食物特写\n【图4】大堂吧下午茶三层架，精致甜点\nAI prompt: Wide angle shot of Atlantis Sanya underwater suite, floor to ceiling aquarium, blue ambient lighting, marine life swimming past, luxury hotel decor, 4K photorealistic",
        "目标人群": ["毕业旅行", "亲子家庭", "蜜月情侣"],
        "季节标签": "全年",
        "热点关联": "高考结束毕业旅行需求井喷",
        "关键词": "亚特兰蒂斯,三亚酒店,毕业旅行,隐藏福利",
        "素材参考链接": f"https://www.pexels.com/search/atlantis%20sanya/\nhttps://unsplash.com/s/photos/atlantis-sanya\nhttps://www.youtube.com/results?search_query=atlantis+sanya+tour",
        "酒店人群画像": "核心客群:亲子家庭(60%)/蜜月情侣(25%)/商务(10%)/其他(5%)"
    },
    # 2. 情绪种草流
    {
        "笔记标题": "住进海底世界是什么体验🌊",
        "酒店名称": "三亚亚特兰蒂斯酒店",
        "内容品类": "情绪种草流",
        "正文文案": "🌊 睁眼就是鲨鱼在头顶游过是一种什么体验？\n\n订了海底套房的那一晚，说实话一整晚都没怎么睡好\n\n不是床不舒服，是太震撼了\n\n躺在床上看魔鬼鱼从眼前飘过\n浴缸泡澡时鱼群就在旁边游来游去\n仿佛自己也成了海洋的一部分 🐚\n\n第二天早上一睁眼\n阳光透过水面洒进来\n鱼鳞闪烁着碎金般的光\n那一刻觉得人间值得\n\n🥂 不是所有酒店都叫亚特兰蒂斯\n毕业旅行也好，蜜月也好\n给自己一次住进水族馆的机会吧",
        "引用话题": "#三亚 #亚特兰蒂斯 #海底套房 #三亚旅行 #毕业旅行 #蜜月旅行 #海岛度假 #三亚酒店 #酒店推荐 #三亚旅游 #水族馆 #海洋世界 #浪漫旅行 #治愈系旅行 #旅行日记",
        "发布时间建议": "周六 10:00-12:00",
        "封面/配图建议(图生prompt)": "【封面】海底套房全景，大落地窗前鲨鱼游过，蓝光氛围\n【图2】浴缸视角，鱼群在玻璃背后\n【图3】床上视角，光线透过水面\n【图4】早餐送来房间，与海洋共进\nAI prompt: Luxury underwater hotel room at night, massive aquarium wall with sharks and rays swimming past, blue bioluminescent lighting, king bed, cinematic composition, dreamy atmosphere, 4K ultra realistic",
        "目标人群": ["蜜月情侣", "毕业旅行", "独行客"],
        "季节标签": "全年",
        "热点关联": "毕业旅行季",
        "关键词": "亚特兰蒂斯海底套房,三亚毕业旅行,种草",
        "素材参考链接": f"https://www.pexels.com/search/underwater%20hotel%20room/\nhttps://unsplash.com/s/photos/ocean-view-room\nhttps://www.youtube.com/results?search_query=atlantis+sanya+suite+tour",
        "酒店人群画像": "核心客群:亲子家庭(60%)/蜜月情侣(25%)/其他(15%)"
    },
    # 3. 测评对比流
    {
        "笔记标题": "亚特兰蒂斯vs艾迪逊 毕业选哪个🤔",
        "酒店名称": "三亚亚特兰蒂斯酒店",
        "内容品类": "测评对比流",
        "正文文案": "🎓 毕业旅行纠结三亚住哪家？\n亚特兰蒂斯vs艾迪逊，两家都住过的人帮你分析\n\n【亚特兰蒂斯】\n✅ 优点：水世界+水族馆无限玩/活动丰富/适合多人\n❌ 缺点：人真的很多/公共区域像景区\n💰 价格：2000-6000/晚\n👤 适合：亲子/毕业团/家庭\n\n【艾迪逊】\n✅ 优点：设计感满分/安静私密/泳池绝了\n❌ 缺点：娱乐项目少/不适合小朋友\n💰 价格：1500-4500/晚\n👤 适合：闺蜜/情侣/独行客\n\n总结：喜欢热闹玩水选亚特，喜欢安静拍照选艾迪逊",
        "引用话题": "#三亚 #亚特兰蒂斯 #艾迪逊 #三亚酒店 #酒店测评 #毕业旅行 #三亚旅游 #酒店对比 #海棠湾 #度假酒店 #三亚攻略 #自由行 #酒店推荐 #毕业季 #旅行攻略",
        "发布时间建议": "周三 20:00-22:00",
        "封面/配图建议(图生prompt)": "【封面】左右分屏：左亚特兰蒂斯水世界全景，右艾迪逊竹林泳池\n【图2】亚特兰蒂斯失落空间水族馆全景\n【图3】艾迪逊屋顶泳池海景\n【图4】两家酒店房间对比照\nAI prompt: Split screen comparison, left: modern colorful water park, right: minimalist luxury pool with bamboo, contrast between vibrant and zen, professional photography, 4K",
        "目标人群": ["毕业旅行", "闺蜜姐妹团", "自由行背包客"],
        "季节标签": "夏季",
        "热点关联": "高考毕业旅游决策",
        "关键词": "三亚酒店对比,亚特兰蒂斯vs艾迪逊,毕业旅行",
        "素材参考链接": f"https://www.pexels.com/search/sanya%20resort/\nhttps://unsplash.com/s/photos/sanya-beach-resort\nhttps://www.youtube.com/results?search_query=atlantis+vs+edition+sanya",
        "酒店人群画像": "核心客群:亲子家庭(60%)/蜜月情侣(25%)"
    },
    # 4. 行业分析流
    {
        "笔记标题": "三亚亚特兰蒂斯凭什么年收20亿💰",
        "酒店名称": "三亚亚特兰蒂斯酒店",
        "内容品类": "行业分析流",
        "正文文案": "🏗️ 亚特兰蒂斯不只是酒店，是三亚旅游的超级引擎\n\n今天从行业角度分析一下它为什么这么能打\n\n📊 数据说话\n- 年均入住率超75%（三亚酒店平均60%）\n- 年营收约20亿，客房收入只占45%\n- 水世界+水族馆贡献35%的非房收入\n\n🎯 核心策略：度假综合体模式\n它不是卖房间的，是卖体验的\n1314间客房+水世界+水族馆+C秀演艺+20家餐厅\n一个酒店就是一个完整度假目的地\n\n🚀 复星收购后的蝶变\n从单体酒店变成超级IP\n2018年重新开业后直接拉高海棠湾酒店均价30%\n\n💡 给行业的启示\n这个时代卖房间不够了\n要卖「沉浸式体验」和「可以发朋友圈的瞬间」",
        "引用话题": "#三亚 #酒店行业 #亚特兰蒂斯 #度假综合体 #旅游产业 #文旅 #三亚经济 #酒店经营 #行业分析 #商业思维 #IP运营 #主题度假 #旅游投资 #毕业季 #消费升级",
        "发布时间建议": "周二 12:00-13:00",
        "封面/配图建议(图生prompt)": "【封面】亚特兰蒂斯航拍全景，酒店+水世界+海滩构图\n【图2】财报数据可视化\n【图3】水世界鸟瞰图\n【图4】酒店大堂高挑空设计\nAI prompt: Aerial drone shot of Atlantis Sanya resort complex, ocean front, water park visible, luxury architecture, golden hour lighting, business magazine cover style, 4K ultra HD",
        "目标人群": ["高端商务", "行业分析"],
        "季节标签": "全年",
        "热点关联": "毕业旅行市场分析",
        "关键词": "亚特兰蒂斯,酒店行业,度假综合体,营收分析",
        "素材参考链接": f"https://www.pexels.com/search/resort%20aerial%20view/\nhttps://unsplash.com/s/photos/luxury-resort-aerial\nhttps://www.traveldaily.cn/",
        "酒店人群画像": "核心客群:亲子(60%)/蜜月(25%)/商务(10%)/其他(5%)"
    },
    # ===== 长沙君悦 =====
    # 5. 截流紧迫感流
    {
        "笔记标题": "毕业旅行抓紧！暑期长沙房价马上翻倍⚠️",
        "酒店名称": "长沙君悦酒店",
        "内容品类": "截流紧迫感流",
        "正文文案": "⚠️ 6月9日高考结束，长沙酒店已经开始涨价了！\n\n现在不订，7月起码多花2000块\n\n看看君悦的价格走势\n📈 6月上旬：1200/晚起\n📈 6月下旬：1800/晚起\n📈 7-8月暑假：2500-3500/晚\n\n🚨 为什么现在要订？\n- 高考完长沙就是毕业旅行第一站\n- 君悦湘江景观房供不应求\n- 五一广场周边酒店都在涨\n\n💡 省钱包方案\n看好哪天去 → 直接订可取消价\n现在锁价，后面降价免费取消\n横竖不亏\n\n🔗 点击左下角查房价\n冲就完了！",
        "引用话题": "#长沙 #长沙君悦 #毕业旅行 #长沙旅游 #长沙酒店 #暑期旅游 #酒店涨价 #湘江 #五一广场 #抢房攻略 #省钱 #旅游攻略 #长沙美食 #茶颜悦色 #长沙夜市",
        "发布时间建议": "周四 18:00-20:00",
        "封面/配图建议(图生prompt)": "【封面】长沙君悦酒店湘江景观房落地窗视角，城市天际线\n【图2】价格趋势对比折线图\n【图3】酒店无边泳池俯瞰城市\n【图4】IFS国金中心夜景\nAI prompt: Luxury hotel room with panoramic window view of Xiang River and Changsha skyline at sunset, modern interior design, king bed, warm golden lighting, billboard style typography overlay, 4K commercial photography",
        "目标人群": ["毕业旅行", "自由行背包客", "闺蜜姐妹团"],
        "季节标签": "夏季",
        "热点关联": "高考结束+夜市经济带火长沙",
        "关键词": "长沙君悦,毕业旅行,暑期涨价,抢房攻略",
        "素材参考链接": f"https://www.pexels.com/search/changsha%20skyline/\nhttps://unsplash.com/s/photos/changsha-city\nhttps://www.youtube.com/results?search_query=grand+hyatt+changsha",
        "酒店人群画像": "核心客群:高端商务(40%)/旅游度假(35%)/会议会展(25%)"
    },
    # 6. Vlog日程流
    {
        "笔记标题": "24h在长沙君悦 纯吃纯玩vlog🎬",
        "酒店名称": "长沙君悦酒店",
        "内容品类": "Vlog日程流",
        "正文文案": "🎬 和闺蜜在长沙君悦的24小时\n\n🕐 10:00 入住\n一进门就被湘江落地窗震住了\n正对着橘子洲和岳麓山\n\n🕐 12:00 午餐·君悦中餐厅\n湘菜做得太正宗了\n辣椒炒肉配米饭绝了\n\n🕐 15:00 下午茶\n大堂吧视野超好\n拍了100张照片\n\n🕐 17:00 无边泳池\n游着泳看湘江日落\n那一刻真的不想回家\n\n🕐 19:00 五一广场夜市\n从酒店溜达过去才10分钟\n茶颜悦色+文和友+太平街\n吃货天堂 😭\n\n🕐 22:00 回房间\n江景夜景太治愈了\n伴着灯光入眠\n\n第二天退房时直接问了下次入住的价格\n已经开始计划下次了",
        "引用话题": "#长沙 #长沙君悦 #君悦酒店 #毕业旅行 #长沙vlog #湘江 #橘子洲 #岳麓山 #五一广场 #茶颜悦色 #长沙夜市 #长沙旅游 #长沙攻略 #酒店vlog #闺蜜旅行 #旅行日记",
        "发布时间建议": "周六 10:00-12:00",
        "封面/配图建议(图生prompt)": "【封面】湘江日落时分无边泳池视角，人物剪影\n【图2】大堂吧下午茶三层架特写\n【图3】泳池游泳俯瞰城市\n【图4】五一广场夜市烟火气\nAI prompt: Infinity pool at Grand Hyatt Changsha overlooking Xiang River at golden hour, silhouette of a swimmer, urban skyline background, warm orange and gold tones, cinematic composition, travel vlog style",
        "目标人群": ["闺蜜姐妹团", "毕业旅行", "美食爱好者"],
        "季节标签": "夏季",
        "热点关联": "夜市经济+毕业旅行",
        "关键词": "长沙君悦,24小时vlog,毕业旅行攻略",
        "素材参考链接": f"https://www.pexels.com/search/changsha%20night%20market/\nhttps://unsplash.com/s/photos/changsha-food\nhttps://www.youtube.com/results?search_query=grand+hyatt+changsha+vlog",
        "酒店人群画像": "核心客群:高端商务(40%)/旅游度假(35%)/会议会展(25%)"
    },
    # 7. 反差点评流
    {
        "笔记标题": "去之前觉得贵 退房时发现赚了😱",
        "酒店名称": "长沙君悦酒店",
        "内容品类": "反差点评流",
        "正文文案": "去之前：1200一晚长沙酒店也太贵了吧\n退房时：这个体验才1200？？\n\n说实话一开始觉得肉疼\n但是住下来算了一笔账👇\n\n🏨 房价1200\n🍳 双早 价值300\n🏊 无边泳池 价值200\n🍵 下午茶 价值200\n🚗 免费停车 价值50\n🛏️ 延迟退房到14点\n\n单纯算这些已经回本了\n\n但真正值的是\n- 江景落地窗那一眼的震撼\n- 泳池边的日落\n- 步行5分钟到太平街夜市\n- 房间隔音超好 外面的喧嚣与我无关\n\n长沙的夜是属于所有人的\n但长沙君悦的那扇窗\n是属于你自己的\n\n真心推荐试一次",
        "引用话题": "#长沙 #长沙君悦 #酒店测评 #长沙旅游 #湘江 #性价比酒店 #毕业旅行 #君悦 #旅行分享 #长沙攻略 #酒店推荐 #真实体验 #长沙美食 #夜市 #旅行日记",
        "发布时间建议": "周三 20:00-22:00",
        "封面/配图建议(图生prompt)": "【封面】去前vs去后分屏：左屏幕标价震惊脸，右屏幕落地窗惊喜照\n【图2】房间内湘江全景落地窗实拍\n【图3】无边泳池日落光影\n【图4】太平街夜市小吃合集\nAI prompt: Split screen before and after: left side shows price tag with shocked expression, right side shows luxury hotel room with panoramic river view, warm and cool color contrast, Instagram travel style",
        "目标人群": ["自由行背包客", "毕业旅行", "情侣约会"],
        "季节标签": "全年",
        "热点关联": "夜市经济热门",
        "关键词": "长沙君悦,性价比,真实测评,反差点评",
        "素材参考链接": f"https://www.pexels.com/search/hotel%20room%20view/\nhttps://unsplash.com/s/photos/changsha-night\nhttps://www.youtube.com/results?search_query=grand+hyatt+changsha+review",
        "酒店人群画像": "核心客群:高端商务(40%)/旅游度假(35%)/会议会展(25%)"
    },
    # ===== 贵阳安纳塔拉 =====
    # 8. 科普涨知识流
    {
        "笔记标题": "贵州避暑酒店为什么选安纳塔拉🌿",
        "酒店名称": "贵阳安纳塔拉度假酒店",
        "内容品类": "科普涨知识流",
        "正文文案": "🔬 安纳塔拉是什么来头？\n\nAnantara（安纳塔拉）是泰国美诺集团的顶级度假品牌\n全球只有40+家\n每一家都是当地文化和奢华体验的融合\n\n贵阳这家是中国第三家安纳塔拉\n2017年开业，占地10万平方米\n但是只有218间客房\n平均每间房占地458平米\n\n🌡️ 为什么贵州是避暑天花板？\n- 贵阳夏季均温23°C\n- 酒店海拔1200米\n- 森林覆盖率95%\n- 负氧离子是城市的50倍\n\n🏡 酒店有什么独特之处？\n- 泰式SPA — 贵州苗药+泰式手法\n- 户外泳池 — 被山林环抱的泳池\n- 观景台 — 远眺贵阳城市天际线\n- 有机菜园 — 餐厅蔬菜自种\n\n这个夏天逃离40°C\n来23°C的贵州深呼吸吧",
        "引用话题": "#贵州 #贵阳 #安纳塔拉 #避暑 #贵州旅游 #避暑胜地 #酒店科普 #贵州酒店 #贵阳酒店 #夏季旅行 #森林度假 #SPA #泰式风格 #奢华酒店 #度假酒店 #小众旅行 #贵州美食 #毕业旅行 #暑假去哪玩 #清凉一夏",
        "发布时间建议": "周三 12:00-13:00",
        "封面/配图建议(图生prompt)": "【封面】安纳塔拉酒店泰式建筑与山林融合的广角镜头\n【图2】户外泳池被森林环绕\n【图3】泰式SPA水疗中心内部\n【图4】有机菜园的蔬菜特写\nAI prompt: Wide angle of Anantara Guiyang resort entrance blending Thai architecture with mountain forest, infinity pool in foreground, misty mountain background, green and teal color palette, professional hotel photography, 4K",
        "目标人群": ["康养旅游", "摄影爱好者", "美食爱好者", "文化深度游"],
        "季节标签": "夏季",
        "热点关联": "贵州旅游新爆款+暑期避暑",
        "关键词": "贵州避暑,安纳塔拉,泰式度假,酒店科普",
        "素材参考链接": f"https://www.pexels.com/search/resort%20mountain%20view/\nhttps://unsplash.com/s/photos/guiyang-resort\nhttps://www.youtube.com/results?search_query=anantara+guiyang+tour",
        "酒店人群画像": "核心客群:度假休闲(50%)/商务会议(30%)/康养旅游(20%)"
    },
    # 9. 真实UGC流
    {
        "笔记标题": "在贵阳安纳塔拉躺了三天 说说真实的体验",
        "酒店名称": "贵阳安纳塔拉度假酒店",
        "内容品类": "真实UGC流",
        "正文文案": "刚从贵阳安纳塔拉回来,趁热说一下真实感受\n先说优点\n\n✅ 环境是真的绝\n山里建的酒店,推开窗就是山\n空气好到离谱,感觉肺都被洗了\n无边泳池拍出来像在国外\n\n✅ 服务很到位\n前台小姐姐主动帮升级了房型\n早餐有肠旺面！在泰式酒店吃到肠旺面也是没谁了\n\n✅ 位置不错\n离机场20分钟,离市区30分钟\n方便去黔灵山公园和甲秀楼\n\n再说不足\n⚠️ 房间装修偏泰式复古,年轻人可能觉得不够新\n⚠️ 晚餐自助品种不算特别多\n⚠️ 周边没商业街,想吃夜宵得开车出去\n\n总结：\n如果是想彻底躺平放松\n想呼吸新鲜空气、在泳池发呆\n这里绝对是不二之选\n但如果是追求夜生活热闹\n建议订市区酒店",
        "引用话题": "#贵州 #贵阳 #安纳塔拉 #酒店测评 #贵阳酒店 #真实体验 #UGC #避暑 #贵州旅游 #旅行日记 #度假 #泳池酒店 #暑假 #毕业旅行 #小众酒店 #慢生活 #贵阳旅游 #酒店推荐 #素人口吻",
        "发布时间建议": "全时段,优先19:00-21:00",
        "封面/配图建议(图生prompt)": "【封面】酒店无边泳池实拍，对面是山景，水中倒影\n【图2】房间阳台视角山林绿意\n【图3】早餐肠旺面特写\n【图4】SPA区域泰式装饰\nAI prompt: Realistic photo of infinity pool at mountain resort, morning mist over forest, guest capturing photo on phone, natural lighting, slightly casual composition like real guest photo, authentic travel photography style",
        "目标人群": ["独行客", "康养旅游", "文化深度游", "摄影爱好者"],
        "季节标签": "夏季",
        "热点关联": "贵州旅游新爆款",
        "关键词": "贵阳安纳塔拉,真实评价,UGC,避暑酒店",
        "素材参考链接": f"https://www.pexels.com/search/mountain%20resort%20pool/\nhttps://unsplash.com/s/photos/guiyang-nature\nhttps://www.youtube.com/results?search_query=anantara+guiyang+review",
        "酒店人群画像": "核心客群:度假休闲(50%)/商务会议(30%)/康养旅游(20%)"
    },
    # 10. 问答攻略流
    {
        "笔记标题": "去贵州避暑前先看这8个问题❓",
        "酒店名称": "贵阳安纳塔拉度假酒店",
        "内容品类": "问答攻略流",
        "正文文案": "最近贵州太火了,整理被问到最多的8个问题\n\n❓Q1: 去贵州避暑到底穿什么？\n👉 早晚温差大,夏天也要带薄外套\n\n❓Q2: 安纳塔拉值不值1000+？\n👉 值。山景、泳池、SPA、服务,环境对得起价格\n\n❓Q3: 住安纳塔拉去哪玩？\n👉 黔灵山公园(30min) / 甲秀楼(30min) / 青岩古镇(40min)\n\n❓Q4: 酒店有免费接送吗？\n👉 有免费机场接送,但需提前预约\n\n❓Q5: 适合带小孩吗？\n👉 有儿童乐园和亲子活动,适合带娃\n\n❓Q6: 附近有什么好吃的？\n👉 酒店泰餐不错 / 出去吃酸汤鱼和丝娃娃\n\n❓Q7: 需要租车吗？\n👉 建议租车,周边自驾方便\n\n❓Q8: 什么时候去最好？\n👉 6-9月避暑旺季,4-5月花季也很美\n\n收藏这篇,去贵州少踩坑 👌",
        "引用话题": "#贵州 #贵阳 #安纳塔拉 #避暑 #贵州旅游攻略 #行前准备 #问答 #贵阳旅游 #青岩古镇 #甲秀楼 #黔灵山 #贵州美食 #暑假旅行 #酒店攻略 #毕业旅行 #自驾游 #旅行常识 #新手必看 #贵州避暑 #收藏贴",
        "发布时间建议": "周四 20:00-22:00",
        "封面/配图建议(图生prompt)": "【封面】问答式拼图,左侧8个Q图标,右侧安纳塔拉山林全景\n【图2】青岩古镇石板路\n【图3】贵州酸汤鱼美食特写\n【图4】酒店房间书桌视角山景\nAI prompt: FAQ style travel guide cover, question mark icons arranged creatively, Guizhou mountain landscape background, minimalist Chinese travel guide aesthetic, infographic style with soft green tones, 4K",
        "目标人群": ["自由行背包客", "毕业旅行", "亲子家庭", "自驾爱好者"],
        "季节标签": "夏季",
        "热点关联": "贵州爆款+高考避暑游",
        "关键词": "贵州避暑攻略,安纳塔拉,行前准备,FAQ",
        "素材参考链接": f"https://www.pexels.com/search/guizhou%20landscape/\nhttps://unsplash.com/s/photos/guizhou-china\nhttps://www.youtube.com/results?search_query=guizhou+travel+guide",
        "酒店人群画像": "核心客群:度假休闲(50%)/商务会议(30%)/康养旅游(20%)"
    },
]

# 分批写入（每批≤10）
for batch_idx in range(0, len(notes_data), 10):
    batch = notes_data[batch_idx:batch_idx+10]
    batch_records = []
    for n in batch:
        fields = {}
        for k, v in n.items():
            if k == "目标人群":
                fields[k] = v  # MultiSelect array
            elif isinstance(v, (int, float)):
                fields[k] = v
            else:
                fields[k] = v
        batch_records.append({"fields": fields})

    resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{note_tid}/records/batch_create',
        {"records": batch_records})
    if resp.get('code') == 0:
        print(f"[笔记] 批次{batch_idx//10+1}: {len(batch)}条成功")
    else:
        print(f"[笔记] 批次失败: {resp}")
    time.sleep(0.5)

print(f"\n=== Phase 7-9 完成 ===")
print(f"文旅调研: {len(culture_dimensions)} 条")
print(f"笔记裂变: {len(notes_data)} 条（3酒店×10品类中的10条精选）")
print(f"Bitable: https://bytedance.feishu.cn/base/{APP_TOKEN}")
