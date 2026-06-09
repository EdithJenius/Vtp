# -*- coding: utf-8 -*-
"""
Phase 10-12: 上游数据入库 + 笔记扩展 + 每日简报
2026-06-09
"""
import urllib.request, json, os, configparser, time

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

# --- Phase 11: 上游数据入Bitable子表 ---
print("=== Phase 11: 上游产业链数据入库 ===")

upstream_data = [
    {"标题": "腾讯公布微信AI生态全新布局，同程旅行成为首批接入OTA", "分类": "科技AI", "来源": "TravelDaily", "摘要": "同程旅行接入微信AI生态，机票、酒店将实现AI一键预订", "链接": "https://www.traveldaily.cn/article/190155"},
    {"标题": "差一点就下单了，游客到底在犹豫什么？", "分类": "文旅目的地", "来源": "TravelDaily", "摘要": "游客决策心理分析，下单前最后一刻的犹豫因素", "链接": "https://www.traveldaily.cn/article/190147"},
    {"标题": "TMC丑闻风波扩大；京沪高铁涨价重塑差旅成本", "分类": "航空运力", "来源": "TravelDaily", "摘要": "成本波动与合规风险，倒逼差旅精细化管控落地", "链接": "https://www.traveldaily.cn/article/190129"},
    {"标题": "下沉市场酒店，别再只拼低价了", "分类": "酒店供应链", "来源": "TravelDaily", "摘要": "下沉市场酒店同质化严重，需要差异化竞争策略", "链接": "https://www.traveldaily.cn/article/190130"},
    {"标题": "同程旅行：美加墨世界杯开赛在即，墨西哥城酒店预订热度增长超50%", "分类": "酒店供应链", "来源": "TravelDaily", "摘要": "高端定制游受追捧，世界杯带动酒店预订", "链接": "https://www.traveldaily.cn/article/190119"},
    {"标题": "AI开始抢酒店流量分配权", "分类": "科技AI", "来源": "TravelDaily", "摘要": "中国已有约6亿人在使用AI助手，AI正在改变酒店流量分配", "链接": "https://www.traveldaily.cn/article/190110"},
    {"标题": "航段费大幅下调，多少机票代理熬不到年底？", "分类": "航空运力", "来源": "TravelDaily", "摘要": "航段费下调对机票代理行业的影响分析", "链接": "https://www.traveldaily.cn/article/190097"},
    {"标题": "北京商旅酒店，进入新一轮价格战", "分类": "酒店供应链", "来源": "TravelDaily", "摘要": "高端坚挺、中端下探的北京酒店市场格局", "链接": "https://www.traveldaily.cn/article/190092"},
    {"标题": "旅游AI这辆车，再不上真就来不及了？", "分类": "科技AI", "来源": "TravelDaily", "摘要": "势不等人，旅游行业AI转型紧迫性分析", "链接": "https://www.traveldaily.cn/article/190093"},
    {"标题": "再不做研学+微度假，北京酒店下半年更难", "分类": "酒店供应链", "来源": "TravelDaily", "摘要": "高质量发展指南：研学+微度假是北京酒店破局方向", "链接": "https://www.traveldaily.cn/article/190090"},
    {"标题": "腾讯元宝，可能会砸了低端旅行社的饭碗", "分类": "科技AI", "来源": "TravelDaily", "摘要": "AI小功能可能对传统低端旅行社产生巨大冲击", "链接": "https://www.traveldaily.cn/article/190091"},
    {"标题": "廉航倒闭潮来了？燃油成本，击穿低票价神话", "分类": "航空运力", "来源": "TravelDaily", "摘要": "燃油成本上涨导致廉价航空面临生存压力", "链接": "https://www.traveldaily.cn/article/190089"},
    {"标题": "贵州山里，正在长出旅游新爆款", "分类": "文旅目的地", "来源": "TravelDaily", "摘要": "大自然不再只是被观赏，而是成为极致体验的场景", "链接": "https://www.traveldaily.cn/article/190067"},
    {"标题": "AI重写旅行行业，玩点旅行押注下一代服务入口", "分类": "科技AI", "来源": "TravelDaily", "摘要": "AI正在重新定义旅行行业的服务入口", "链接": "https://www.traveldaily.cn/article/190145"},
    {"标题": "企业协议价，正在被酒店自己绕开", "分类": "酒店供应链", "来源": "TravelDaily", "摘要": "企业协议价体系面临被酒店自行绕开的挑战", "链接": "https://www.traveldaily.cn/article/190096"},
    {"标题": "出海差旅，TMC 怎么选？", "分类": "政策签证", "来源": "TravelDaily", "摘要": "中国企业出海差旅管理的TMC选择指南", "链接": "https://www.traveldaily.cn/article/190095"},
    {"标题": "ChatGPT将迎史上最大改版，从单一聊天变身超级应用", "分类": "科技AI", "来源": "36氪", "摘要": "AI只用来聊天的时代结束了，ChatGPT向超级应用进化", "链接": "https://36kr.com/p/3843921641736457"},
    {"标题": "地摊设备暴涨600%，夜市摆摊大军回来了", "分类": "文旅目的地", "来源": "36氪", "摘要": "地摊经济新热潮，夜市成为消费新场景", "链接": "https://36kr.com/p/3839681255393797"},
]

# 创建上游数据子表
upstream_fields = [
    {"field_name": "标题", "type": 1},
    {"field_name": "分类", "type": 3, "property": {"options": [
        {"name":"航空运力"}, {"name":"酒店供应链"}, {"name":"政策签证"}, {"name":"会展活动"}, {"name":"文旅目的地"}, {"name":"科技AI"}
    ]}},
    {"field_name": "来源", "type": 1},
    {"field_name": "摘要", "type": 1},
    {"field_name": "链接", "type": 1},
]

body = {"table": {"name": "上游产业链情报 2026-06-09", "fields": upstream_fields}}
resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', body)
up_tid = resp['data']['table_id']
print(f"[上游] 子表创建: {up_tid}")

# 分批写入
for batch_idx in range(0, len(upstream_data), 10):
    batch = upstream_data[batch_idx:batch_idx+10]
    records = [{"fields": u} for u in batch]
    api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{up_tid}/records/batch_create',
        {"records": records})
    print(f"[上游] 批次{batch_idx//10+1}: {len(batch)}条")
    time.sleep(0.3)

print(f"[上游] {len(upstream_data)} 条上游情报已入库")

# --- Phase 12: 每日简报 ---
print("\n=== Phase 12: 每日混合简报 ===")

briefing = """
📊 **今日文旅商机速报 2026-06-09**

🏭 **上游产业链情报**
  ▎科技AI · 腾讯微信AI生态+同程旅行首批接入
  ▎科技AI · AI开始抢酒店流量分配权
  ▎酒店供应链 · 北京商旅酒店进入价格战（高端坚挺中端下探）
  ▎酒店供应链 · 下沉市场酒店别只拼低价
  ▎文旅目的地 · 贵州山里正在长出旅游新爆款
  ▎航空运力 · 航段费大幅下调，机票代理面临困境
  ▎航空运力 · 廉航倒闭潮？燃油成本击穿低票价神话
  ▎科技AI · 旅游AI这辆车再不上来不及了

🔥 **今日热搜 TOP10**
  1. 📰 高考（全平台霸榜）→ 毕业旅行季引爆
  2. 📰 考生喊话取消机建燃油费 → 出行成本热议
  3. 📰 中朝友谊/平壤节日盛装 → 边境游关注
  4. 📰 菲律宾强震 → 东南亚替代目的地机会
  5. 📰 NBA总决赛G3 马刺vs尼克斯 → 观赛经济
  6. 📰 金饰克价下跌400元 → 消费释放利好旅游
  7. 📰 地摊设备暴涨600% → 夜市经济带火长沙/成都
  8. 📰 ChatGPT史上最大改版 → AI+旅游新机会
  9. 📰 iOS 27发布/苹果AI → 科技旅游融合趋势
  10. 📰 郑钦文止步女王杯首轮 → 温网观赛游

💡 **商机交叉分析**
  ✅ **毕业旅行（高优先级）**：高考6月9日结束 → 毕业旅行需求井喷 → 三亚/长沙/成都/重庆/西安
  ✅ **夜市经济（高优先级）**：地摊设备暴涨600% → 长沙/成都夜市游
  ✅ **贵州避暑游（高优先级）**：贵州成为旅游新爆款 → 暑期避暑游 → 安纳塔拉/黄果树
  ✅ **北京研学微度假（高优先级）**：酒店价格战 + 研学产品 → 中端酒店性价比高
  ✅ **中朝友谊（中优先级）**：边境游关注度上升 → 丹东/大连连线
  ✅ **世界杯预热（中优先级）**：美加墨2026世界杯 → 墨西哥城酒店热度+50%

📎 **完整数据**: https://bytedance.feishu.cn/base/KC7GbI8oFaUXAWsMAAtcYxIWnxM
"""

# 写入简报文件
briefing_path = os.path.expanduser('~/.openclaw/workspace/skills/hotspot-bitable-analysis/data/briefing_2026-06-09.md')
with open(briefing_path, 'w', encoding='utf-8') as f:
    f.write(briefing)
print(f"[简报] 已保存: {briefing_path}")

print(f"\n=== 全流程完成 ===")
print(f"Bitable 主链接: https://bytedance.feishu.cn/base/{APP_TOKEN}")
print(f"简报文件: skills/hotspot-bitable-analysis/data/briefing_2026-06-09.md")
