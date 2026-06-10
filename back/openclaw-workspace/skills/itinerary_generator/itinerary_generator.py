# -*- coding: utf-8 -*-
"""
itinerary_generator.py — 「X天X晚地图版攻略」通用模板生成器

输入目的地列表、天数、风格，一键输出：
  - 视频口播脚本（带章节时间标记）
  - 地图路线描述
  - 每天详细行程
  - 酒店/景点推荐
  - 话题标签

用法:
  python3 itinerary_generator.py --days 7 --destinations "吉隆坡,仙本那,亚庇" --title "马来西亚双城+海岛"

参数:
  --days         总天数 (必填)
  --destinations 目的地，逗号分隔，按行程顺序 (必填)
  --title        视频标题 (可选，默认取目的地链)
  --style        风格: 地图版攻略 / 穷游攻略 / 深度游攻略 (默认: 地图版攻略)
  --people       人群: 毕业旅行 / 情侣 / 亲子 / 朋友 (默认: 通用)
  --budget       预算档位: 经济型 / 舒适型 / 轻奢型 (默认: 舒适型)
  --json         输出JSON格式
"""
import json, sys, os, argparse
from datetime import datetime

# ─── 目的地知识库（可扩展） ───
DESTINATION_DB = {
    # 东南亚
    "吉隆坡": {"country": "马来西亚", "visa": "免签30天", "currency": "马币RM", "lang": "马来语/英语/华语",
        "hotels": [("吉隆坡双子塔附近无边泳池酒店", "双子塔景观/无边泳池/性价比高"),
                          ("武吉免登区四星级酒店", "购物区核心/交通便利")],
        "default_spots": ["双子塔(KLCC)", "独立广场", "吉隆坡塔", "武吉免登购物区"],
        "default_activities": ["KLCC空中桥梁观景", "阿罗街夜市美食", "双子塔水族馆"]},
    "仙本那": {"country": "马来西亚", "visa": "免签30天", "currency": "马币RM",
        "hotels": [("水屋度假村", "海上木屋/浮潜出门即达/网红打卡"),
                          ("仙本那镇经济型酒店", "出海方便/价格亲民")],
        "default_spots": ["卡帕莱岛", "马布岛", "敦沙卡兰海洋公园"],
        "default_activities": ["深潜/浮潜", "海上玻璃船", "海鲜市场"]},
    "亚庇": {"country": "马来西亚", "visa": "免签30天", "currency": "马币RM",
        "hotels": [("丹绒亚路海滩度假村", "日落观赏/海滩直通"),
                          ("亚庇市中心酒店", "加雅街美食/出行方便")],
        "default_spots": ["丹绒亚路海滩日落", "神山国家公园", "沙巴大学", "加雅街"],
        "default_activities": ["世界TOP3日落观赏", "神山ATV体验", "红树林萤火虫"]},
    "泗水": {"country": "印度尼西亚", "visa": "落地签35美元", "currency": "印尼盾IDR",
        "hotels": [("泗水泳池酒店", "泳池景观/近BROMO出发地"),
                          ("玛琅市区酒店", "文化氛围/殖民建筑")],
        "default_spots": ["赛武瀑布", "蓝棉瀑布", "BROMO火山"],
        "default_activities": ["BROMO火山日出登山", "赛武瀑布涉水徒步", "马达将军瀑布"]},
    "巴厘岛": {"country": "印度尼西亚", "visa": "落地签35美元", "currency": "印尼盾IDR",
        "hotels": [("库塔海景度假酒店", "冲浪海滩/日落酒吧/年轻人聚集"),
                          ("乌布稻田民宿", "梯田景观/瑜伽/慢生活")],
        "default_spots": ["佩尼达岛", "乌鲁瓦图断崖", "乌布皇宫/梯田", "海神庙"],
        "default_activities": ["佩尼达岛浮潜", "滑翔伞体验", "ATV越野", "乌布SPA"]},
    "曼谷": {"country": "泰国", "visa": "免签60天", "currency": "泰铢THB",
        "hotels": [("暹罗区五星酒店", "购物中心核心/泳池景观"),
                          ("考山路经济型酒店", "背包客天堂/夜市热闹")],
        "default_spots": ["大皇宫", "卧佛寺", "郑王庙", "暹罗商圈"],
        "default_activities": ["水上市场", "泰式按摩", "Asiatique夜市"]},
    "普吉岛": {"country": "泰国", "visa": "免签60天", "currency": "泰铢THB",
        "hotels": [("卡伦海滩度假村", "安静沙滩/适合度假"),
                          ("芭东海滩酒店", "夜生活丰富/年轻人首选")],
        "default_spots": ["皮皮岛", "皇帝岛", "攀牙湾", "卡塔观景台"],
        "default_activities": ["跳岛浮潜", "丛林飞跃", "泰拳表演"]},
    "清迈": {"country": "泰国", "visa": "免签60天", "currency": "泰铢THB",
        "hotels": [("古城内精品酒店", "寺庙环绕/文艺氛围"),
                          ("尼曼路设计师酒店", "网红店聚集/拍照出片")],
        "default_spots": ["素贴山双龙寺", "清迈古城", "夜间动物园", "大象营"],
        "default_activities": ["泰式烹饪课", "丛林飞跃", "周末夜市"]},

    # 国内
    "三亚": {"country": "中国", "visa": "国内游", "currency": "人民币CNY",
        "hotels": [("三亚海棠湾度假酒店", "一线海景/免税店近"),
                          ("亚龙湾亲子度假村", "沙滩细软/家庭友好")],
        "default_spots": ["蜈支洲岛", "亚龙湾热带天堂森林公园", "南山文化旅游区"],
        "default_activities": ["免税店购物", "潜水/水上项目", "海滩日落"]},
    "丽江": {"country": "中国", "visa": "国内游", "currency": "人民币CNY",
        "hotels": [("丽江古城内精品民宿", "纳西风格/古城中心"),
                          ("束河古镇度假酒店", "安静/雪山景观")],
        "default_spots": ["玉龙雪山", "丽江古城", "泸沽湖", "束河古镇"],
        "default_activities": ["雪山索道", "古城漫步", "泸沽湖划船"]},
    "成都": {"country": "中国", "visa": "国内游", "currency": "人民币CNY",
        "hotels": [("春熙路商圈酒店", "市中心/交通便利"),
                          ("太古里设计酒店", "潮人聚集/网红打卡")],
        "default_spots": ["大熊猫基地", "宽窄巷子", "锦里", "都江堰"],
        "default_activities": ["看花花!", "川菜美食", "人民公园喝茶"]},
    "杭州": {"country": "中国", "visa": "国内游", "currency": "人民币CNY",
        "hotels": [("西湖边景观酒店", "湖景房/西湖核心"),
                          ("西溪湿地特色酒店", "安静/自然风光")],
        "default_spots": ["西湖", "灵隐寺", "西溪湿地", "龙井村"],
        "default_activities": ["西湖骑行", "龙井品茶", "宋城千古情"]},

    # 日韩
    "东京": {"country": "日本", "visa": "电子签", "currency": "日元JPY",
        "hotels": [("新宿商务酒店", "交通枢纽/购物便利"),
                          ("浅草寺附近日式旅馆", "传统体验/性价比")],
        "default_spots": ["浅草寺", "涩谷SKY", "秋叶原", "筑地市场"],
        "default_activities": ["迪士尼乐园", "温泉体验", "和服体验"]},
    "大阪": {"country": "日本", "visa": "电子签", "currency": "日元JPY",
        "hotels": [("心斋桥商圈酒店", "购物核心/道顿堀步行"),
                          ("环球影城周边酒店", "乐园游玩方便")],
        "default_spots": ["大阪城公园", "道顿堀", "通天阁", "环球影城"],
        "default_activities": ["USJ超级任天堂世界", "大阪烧体验", "蟹道乐"]},
    "首尔": {"country": "韩国", "visa": "电子旅行许可K-ETA", "currency": "韩元KRW",
        "hotels": [("明洞商圈酒店", "购物核心/地铁便利"),
                          ("弘大创意酒店", "年轻人文化/K-POP")],
        "default_spots": ["景福宫", "北村韩屋村", "南山塔", "明洞"],
        "default_activities": ["韩服体验", "K-POP舞蹈课", "汗蒸房"]},
}

# ─── 模板引擎 ───

def generate_script(params):
    """生成完整视频脚本"""
    days = params["days"]
    dests = params["destinations"]
    style = params.get("style", "地图版攻略")
    people = params.get("people", "通用")
    budget = params.get("budget", "舒适型")
    title = params["title"]
    
    dest_info = [DESTINATION_DB.get(d, {}) for d in dests]
    missing = [d for d, info in zip(dests, dest_info) if not info]
    
    lines = []
    lines.append(f"🎬 标题: {title} 《{days}天{days-1}晚{style}》")
    lines.append(f"👥 适用人群: {people} | 💰 预算: {budget}")
    lines.append(f"🗺️ 路线: {' → '.join(dests)}")
    if missing:
        lines.append(f"⚠️ 以下目的地暂未入库，将使用智能填充: {', '.join(missing)}")
    lines.append("")
    
    # ── 引言 ──
    dest_names = "、".join(dests)
    countries = list(set(info.get("country", "未知") for info in dest_info if info))
    country_str = "、".join(countries)
    lines.append("─── 引言 ───")
    visa_summary = "、".join(set(info.get("visa", "") for info in dest_info if info))
    lines.append(f"🎙️: 「{days}天的{'、'.join(dests)}之旅，带你体验{country_str}的不同魅力！"
                 f"从{'到'.join([dests[0], dests[-1]])}，一路玩过去！")
    lines.append(f"📌 签证信息: {visa_summary}")
    if len(countries) > 1:
        lines.append(f"🌏 跨国路线，一次玩遍{country_str}!")
    lines.append("")
    
    # ── 每天行程 ──
    days_per_dest = max(1, days // len(dests))
    day_counter = 1
    
    for idx, (dest, dest_name) in enumerate(zip(dest_info, dests)):
        is_last = idx == len(dests) - 1
        days_here = days - (len(dests) - 1) * days_per_dest if is_last else days_per_dest
        
        lines.append(f"─── {dest_name} ───")
        
        if dest:
            lines.append(f"📍 {dest_name}（{dest['country']} | {dest.get('visa','')} | {dest.get('currency','')}）")
            lines.append(f"🗣️ 语言: {dest.get('lang', '英语为主')}")
        else:
            lines.append(f"📍 {dest_name}")
        
        lines.append(f"🎙️: 「第{day_counter}-{day_counter+days_here-1}天，来到{dest_name}」")
        
        # 交通衔接
        if idx == 0:
            lines.append(f"✈️ 抵达: 飞抵{dest_name}机场，前往酒店入住")
        else:
            prev = dests[idx-1]
            lines.append(f"🚗 交通: 从{prev}前往{dest_name}（飞机约1-3h / 高铁约2-4h）")
        
        # 酒店
        if dest:
            h = dest["hotels"][0]
            lines.append(f"🏨 推荐酒店: {h[0]} — {h[1]}")
            if len(dest["hotels"]) > 1:
                h2 = dest["hotels"][1]
                lines.append(f"🏨 备选: {h2[0]} — {h2[1]}")
        else:
            lines.append(f"🏨 推荐酒店: {dest_name}中心区域酒店/民宿（建议提前预订）")
        
        # 行程安排
        lines.append(f"📋 行程安排:")
        for d in range(day_counter, day_counter + days_here):
            if day_counter == d:
                lines.append(f"  第{d}天 | 抵达+市区游览 | 入住休息")
            elif d == day_counter + days_here - 1 and not is_last:
                lines.append(f"  第{d}天 | 上午游览 → 下午前往下一站")
            elif d == day_counter + days_here - 1:
                lines.append(f"  第{d}天 | 自由活动+返程")
            else:
                lines.append(f"  第{d}天 | 深度游览+特色体验")
        
        # 景点
        if dest:
            spots = dest["default_spots"]
            lines.append(f"🏞️ 必去景点: {' | '.join(spots)}")
            acts = dest["default_activities"]
            lines.append(f"🎯 特色体验: {' | '.join(acts)}")
        else:
            lines.append(f"🏞️ 推荐探索: 当地地标景点+特色街区+美食街")
        
        day_counter += days_here
        lines.append("")
    
    # ── 地图路线 ──
    lines.append("─── 🗺️ 地图路线 ───")
    lines.append(f"📌 路线总览: {' → '.join(dests)}")
    for i in range(len(dests)-1):
        dist = "飞机1-3小时" if i < 2 else "车程1-2小时"
        lines.append(f"  {dests[i]} —— {dist} ——> {dests[i+1]}")
    lines.append("💡 建议在地图上标注每个城市的位置，用箭头/线条连接路线")
    lines.append("💡 可以在地图上标注: 每个城市的1-2个核心景点图标")
    lines.append("")
    
    # ── 结语 ──
    lines.append("─── 结语 ───")
    total_cost_hint = "经济型3000+/人" if budget == "经济型" else "舒适型5000+/人" if budget == "舒适型" else "轻奢型8000+/人"
    lines.append(f"🎙️: 「{days}天{days-1}晚「{'」到「'.join([dests[0], dests[-1]])}」的旅行，"
                 f"{total_cost_hint}左右就能搞定！")
    lines.append("想要具体行程和报价的评论区留言👇")
    
    # 话题标签
    tags = [f"#{d}" for d in dests]
    tags.append(f"#{days}天{days-1}晚攻略")
    tags.append(f"#{style}")
    tags.append(f"#{'旅游攻略'}")
    if len(countries) == 1:
        tags.append(f"#{countries[0]}旅游")
    else:
        tags.extend([f"#{c}旅游" for c in countries])
    tags.extend(["#旅行推荐官", "#暑假去哪玩"])
    lines.append(f"\n📱 话题标签: {' '.join(tags)}")
    
    return "\n".join(lines)

def generate_json(params):
    """生成结构化JSON"""
    days = params["days"]
    dests = params["destinations"]
    style = params.get("style", "地图版攻略")
    people = params.get("people", "通用")
    budget = params.get("budget", "舒适型")
    title = params["title"]
    
    dest_info = []
    for d in dests:
        info = DESTINATION_DB.get(d, {})
        if info:
            dest_info.append(info)
        else:
            dest_info.append({"country": "未知", "visa": "请查询", "currency": "",
                             "hotels": [("待推荐", "")], "default_spots": ["待补充"],
                             "default_activities": ["待补充"]})
    
    countries = list(set(info["country"] for info in dest_info if info))
    days_per = max(1, days // len(dests))
    
    chapters = []
    day_idx = 1
    for idx, (dest, info) in enumerate(zip(dests, dest_info)):
        is_last = idx == len(dests) - 1
        days_here = days - (len(dests)-1)*days_per if is_last else days_per
        
        chapter = {
            "title": dest,
            "days": list(range(day_idx, day_idx + days_here)),
            "country": info["country"],
            "visa": info.get("visa", ""),
            "currency": info.get("currency", ""),
            "hotels": [{"name": h[0], "feature": h[1]} for h in info.get("hotels", [("待推荐","")])],
            "spots": info.get("default_spots", []),
            "activities": info.get("default_activities", []),
            "transport_to_next": f"飞机/高铁" if not is_last else None,
        }
        chapters.append(chapter)
        day_idx += days_here
    
    result = {
        "title": f"{title} 《{days}天{days-1}晚{style}》",
        "days": days,
        "nights": days - 1,
        "style": style,
        "people": people,
        "budget": budget,
        "route": " → ".join(dests),
        "countries": countries,
        "chapters": chapters,
        "tags": [f"#{d}" for d in dests] + [f"#{days}天{days-1}晚攻略", f"#{style}", "#旅游攻略",
                 *([f"#{c}旅游" for c in countries]), "#旅行推荐官", "#暑假去哪玩"],
    }
    return result

# ─── CLI ───
def main():
    parser = argparse.ArgumentParser(description="「地图版攻略」模板生成器")
    parser.add_argument("--days", type=int, required=True, help="总天数")
    parser.add_argument("--destinations", type=str, required=True, help="目的地，逗号分隔")
    parser.add_argument("--title", type=str, help="视频标题")
    parser.add_argument("--style", type=str, default="地图版攻略", choices=["地图版攻略", "穷游攻略", "深度游攻略"])
    parser.add_argument("--people", type=str, default="通用", help="人群: 毕业旅行/情侣/亲子/朋友")
    parser.add_argument("--budget", type=str, default="舒适型", choices=["经济型", "舒适型", "轻奢型"])
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    
    args = parser.parse_args()
    dests = [d.strip() for d in args.destinations.split(",")]
    
    params = {
        "days": args.days,
        "destinations": dests,
        "title": args.title or "+".join(dests),
        "style": args.style,
        "people": args.people,
        "budget": args.budget,
    }
    
    if args.json:
        result = generate_json(params)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        script = generate_script(params)
        print(script)
        
        # 检查是否所有目的地都有数据
        missing = [d for d in dests if d not in DESTINATION_DB]
        if missing:
            print(f"\n⚠️ 以下目的地暂未收录知识库，建议补充: {', '.join(missing)}")

if __name__ == "__main__":
    main()
