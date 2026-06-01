#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 4-6: 痛点分析 → 讲解流程 → 文案产出
基于对标视频+行程数据，生成脚本内容并写入子表
"""
import json, os, urllib.request, configparser, sys, time

def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appid'].strip('"')
    app_secret = config['provider.feishu']['appsecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_token()
print("TOKEN_OK", flush=True)

def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
    if data: headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as f:
            return json.loads(f.read().decode())
    except Exception as e:
        return {'code': -1, 'msg': str(e)[:80]}

APP = 'CURybXQlma9Yu0sMtUHcBw5unqd'

# ===== ② 痛点分析 =====
PAIN_TID = 'tblEg4VbBucvjBjy'
print('写入痛点分析...', flush=True)

pains = [
    {"痛点描述": "去非洲Safari预算不透明，不知道到底要花多少钱", "来源视频": "普通人如何去非洲Safari？", "目标人群": "首次考虑非洲旅行、对价格敏感的用户", "解决方案": "给出透明报价区间+明细，拆解3-5w不同预算方案", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "优先级": "高"},
    {"痛点描述": "怕选错月份去，看不到动物大迁徙", "来源视频": "大迁徙不是全年都有", "目标人群": "第一次去东非、对动物迁徙规律不了解的游客", "解决方案": "科普迁徙时间线+旺季7-9月推荐+全年各月看点", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "优先级": "高"},
    {"痛点描述": "签证、疫苗、机票等行前准备太繁琐", "来源视频": "坦桑尼亚Safari攻略01", "目标人群": "自由行小白、第一次去非洲的人", "解决方案": "一站式行前清单：签证/黄皮书/行李/保险全包", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "优先级": "中"},
    {"痛点描述": "担心Safari的住宿条件差、不卫生", "来源视频": "坦桑尼亚Singita三酒店测评", "目标人群": "对住宿品质有要求的中高端游客", "解决方案": "展示各酒店实拍图+等级分类+价格分段推荐", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "优先级": "中"},
    {"痛点描述": "不知道怎么选旅行社/地接，怕被坑", "来源视频": "坦桑尼亚Safari计划和报价", "目标人群": "自由行但缺乏经验、怕被宰的游客", "解决方案": "报价对比方法论+旅行社筛选标准+避坑口诀", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "优先级": "高"},
    {"痛点描述": "坦桑尼亚vs肯尼亚不知道怎么选", "来源视频": "人均3w 非洲肯坦10天", "目标人群": "在肯尼亚和坦桑尼亚之间纠结的游客", "解决方案": "两国对比:Safari体验/价格/签证/旺季差异速览", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅", "优先级": "中"},
]

for p in pains:
    r = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{PAIN_TID}/records', {'fields': p})
    time.sleep(0.2)
print(f'  痛点分析: {len(pains)} 条写入', flush=True)

# ===== ③ 讲解流程 =====
FLOW_TID = 'tblQkzrmwMTf3kTw'
print('写入讲解流程...', flush=True)

flows = [
    {"流程步骤": 1, "环节标题": "钩子开场——坦桑尼亚Safari到底要花多少钱", "核心内容": "抛出价格痛点，用具体数字吸引注意力。3万？5万？还是10万？今天拆给你看", "对应痛点": "预算不透明、怕贵", "建议画面": "塞伦盖蒂草原航拍全景+价格数字弹出", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"流程步骤": 2, "环节标题": "什么时候去最好——动物大迁徙时间线", "核心内容": "科普7-9月旺季+各月看点。角马过河只在特定月份，去错了什么都看不到", "对应痛点": "怕选错月份看不到动物", "建议画面": "动物大迁徙实拍+月份时间线动画", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"流程步骤": 3, "环节标题": "行程怎么走——12天从乞力马扎罗到塞伦盖蒂", "核心内容": "按天拆解路线：塔兰吉雷→恩戈罗恩戈罗→塞伦盖蒂→曼亚拉湖，每天看什么", "对应痛点": "路线复杂不知道怎么规划", "建议画面": "路线地图动画+各国家公园实拍", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"流程步骤": 4, "环节标题": "住哪里——草原上的野奢酒店有多绝", "核心内容": "推荐3个价位段酒店：经济型/中端/野奢，各有什么特色，适合什么人", "对应痛点": "住宿条件担心、不知道怎么选", "建议画面": "各酒店房间实拍+航拍+价格标注", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"流程步骤": 5, "环节标题": "行前准备清单——签证黄皮书机票一网打尽", "核心内容": "最全checklist：电子签/黄热病疫苗/航班/保险/行李清单", "对应痛点": "行前准备太繁琐", "建议画面": "清单卡片式排版+逐项打勾动画", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"流程步骤": 6, "环节标题": "避坑指南+价格透明——你的钱花在哪了", "核心内容": "Safari费用拆解：门票/住宿/越野车/向导各多少钱，选旅行社的避坑方法", "对应痛点": "怕被坑、不知道怎么选旅行社", "建议画面": "费用饼图+对比表格", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
    {"流程步骤": 7, "环节标题": "结尾——为什么坦桑尼亚值得去一次", "核心内容": "情感升华：不是看动物，是看地球本来的样子。给用户一个非去不可的理由", "对应痛点": "犹豫不决、需要最后推一把", "建议画面": "夕阳下的塞伦盖蒂+用户感动瞬间混剪", "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅"},
]

for f in flows:
    r = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{FLOW_TID}/records', {'fields': f})
    time.sleep(0.2)
print(f'  讲解流程: {len(flows)} 条写入', flush=True)

# ===== ④ 文案产出 =====
SCRIPT_TID = 'tblUfhsd7yGq5DYe'
print('写入文案...', flush=True)

script_body = (
    "【坦桑尼亚Safari到底要花多少钱？这条视频给你拆明白】\n\n"
    "#钩子开场\n"
    "你猜去一趟坦桑尼亚Safari要花多少钱？\n"
    "3万？5万？10万？\n"
    "今天我用一条视频给你拆得明明白白\n\n"
    "#什么时候去\n"
    "首先，选对时间比什么都重要\n"
    "动物大迁徙每年7-9月是黄金期\n"
    "角马过马拉河这种场面，错过了就得等一年\n"
    "其他月份也不是不能去，但看点不一样\n\n"
    "#12天怎么走\n"
    "我们的路线是这样的：\n"
    "第1天飞到乞力马扎罗机场\n"
    "阿鲁沙休整一天\n"
    "然后一路塔兰吉雷看大象群和猴面包树\n"
    "恩戈罗恩戈罗火山口追狮子犀牛\n"
    "塞伦盖蒂连住几天深度Safari\n"
    "再去马拉河边等一场天河之渡\n"
    "最后经过曼亚拉湖看树上狮群\n"
    "全程12天，每一天都是视觉轰炸\n\n"
    "#住哪里\n"
    "住宿这块我按价位分了三个档：\n"
    "经济型营地：干净舒服，性价比高\n"
    "中端Lodge：草原上的小木屋，有热水有电\n"
    "野奢帐篷：帐篷里配浴缸，推开窗就是长颈鹿\n"
    "丰俭由人，提前说预算我们来匹配\n\n"
    "#行前准备\n"
    "坦桑尼亚电子签，提前两周办\n"
    "黄热病疫苗提前10天打，记得带黄皮书\n"
    "带件外套，草原早晚温差大\n"
    "防晒！赤道附近的太阳不是开玩笑的\n\n"
    "#避坑指南\n"
    "选旅行社要看是不是正规注册的\n"
    "报价含不含国家公园门票要问清楚\n"
    "越野车是不是4x4，有没有顶棚可以站起来看\n"
    "这些细节不注意，到了那边就会多花冤枉钱\n\n"
    "#结尾\n"
    "最后想说一句\n"
    "去坦桑尼亚Safari\n"
    "不是去看动物的\n"
    "是去看地球本来的样子\n"
    "当你站在塞伦盖蒂草原上\n"
    "夕阳把整片天空染成金色\n"
    "你会觉得这趟旅程每一分钱都值\n\n"
    "想要详细行程单的评论区扣1\n"
    "我发给你 📩"
)

article = {
    "文案标题": "坦桑尼亚Safari到底要花多少钱？12天全程拆解",
    "口播正文": script_body,
    "版本": "V1.0",
    "时长预估": "约60秒",
    "风格定位": "干货科普+种草型，口播+画面穿插",
    "关联产品": "坦桑尼亚12天10晚 Safari 野奢之旅",
    "状态": "待审核"
}

r = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{SCRIPT_TID}/records', {'fields': article})
if r.get('code') == 0:
    print(f'  文案产出: 1 条写入', flush=True)
else:
    print(f'  文案写入失败: {r.get("msg","")[:80]}', flush=True)

print(f'\nURL: https://q7yllltm5t.feishu.cn/base/{APP}', flush=True)
