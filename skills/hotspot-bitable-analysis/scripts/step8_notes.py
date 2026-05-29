#!/usr/bin/env python3
"""
Step 8-10: 笔记裂变内容库 — 模板化创作引擎（升级版）

=== 新特性 ===
✅ 10个风格模板可选用（note_templates.py）
✅ 对标克隆模式（clone_analyzer.py）
✅ 自动过合规校验（xiaohongshu_compliance.py）
✅ 向后兼容：原有8品类维度保留，每个品类可选不同模板

=== 使用方式 ===

方式1：按模板生成（指定品类+模板）
    python3 step8_notes.py --generate --hotel "成都W酒店" --category "干货价值类" --template "干货/清单流"

方式2：按模板批量生成（8品类×默认模板，原有模式）
    python3 step8_notes.py --full --hotel "成都W酒店"

方式3：按克隆特征生成
    python3 step8_notes.py --clone --hotel "成都W酒店" --category "种草型范流量号"

方式4：查看可用模板
    python3 step8_notes.py --list-templates

方式5：查看品类推荐模板
    python3 step8_notes.py --recommend --category "干货价值类"

方式6：分析对标文案结构
    python3 step8_notes.py --analyze --text "你的文案内容"

方式7：完整流程（创建表+生成+写入）
    python3 step8_notes.py --all --hotel "成都W酒店" --template "干货/清单流"
"""

import json
import urllib.request
import urllib.error
import os
import sys
import time
import re
import configparser

# ===== 加载新模块 =====
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from note_templates import TEMPLATES, CATEGORY_TEMPLATE_MAP, get_recommended_templates, list_templates, template_summary
from note_generator import NoteGenerator, DEFAULT_HOTEL_INFO
from xiaohongshu_compliance import audit_and_fix, audit_report

# ===== 配置 =====
config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId'].strip('"')
APP_SECRET = config['provider.feishu']['appSecret'].strip('"')

def get_token():
    body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode())['tenant_access_token']

TOKEN = get_token()
print(f"[Token] OK")

# ===== 常量 =====
MAIN_TOKEN = "ZdpRbPT2qaGsBvsqiNucQX1Knwh"
CATEGORIES = list(CATEGORY_TEMPLATE_MAP.keys())  # 8品类
GEN = NoteGenerator()

# ===== 飞书API =====
def api(method, url, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    if data:
        payload = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        payload = None
    r = urllib.request.Request(url, data=payload, method=method, headers=headers)
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode())


# ===== 内容生成引擎（核心） =====

def generate_by_template(hotel_name, hotel_info, category, template_name):
    """
    方式1：按模板生成一条笔记
    
    Args:
        hotel_name: 酒店名称
        hotel_info: 酒店信息字典
        category: 内容品类
        template_name: 模板名称
    
    Returns:
        dict: {笔记标题, 正文文案, 引用话题, 对标爆款风格, 备注}
    """
    note = GEN.generate(hotel_name, hotel_info, category, template_name)
    note["酒店名称"] = hotel_name
    note["内容品类"] = category
    note["对标爆款风格"] = f"模板：{template_name}"
    note["备注"] = f"使用{template_name}模板生成"
    return note


def generate_by_clone(hotel_name, hotel_info, category, clone_text=""):
    """
    方式2：从克隆分析生成笔记
    
    Args:
        hotel_name: 酒店名称
        hotel_info: 酒店信息字典
        category: 内容品类
        clone_text: 对标文案（可直接粘贴的文本）
    
    Returns:
        dict: {笔记标题, 正文文案, 引用话题, 对标爆款风格, 备注}
    """
    from clone_analyzer import analyze_text, clone_structure_to_guide
    
    profile = analyze_text(clone_text)
    clone_guide = clone_structure_to_guide(profile, hotel_name, category)
    
    note = GEN.generate_from_clone(hotel_name, hotel_info, category, clone_guide)
    note["酒店名称"] = hotel_name
    note["内容品类"] = category
    note["备注"] = f"对标克隆（来源分析：{profile.summarize()}）"
    return note


def generate_full_matrix(hotel_name, hotel_info, template_override=None):
    """
    方式3：生成8品类完整矩阵（向后兼容原step8_notes）
    
    每个品类使用推荐模板（可手动覆盖为统一模板）
    
    Args:
        hotel_name: 酒店名称
        hotel_info: 酒店信息字典
        template_override: 统一使用的模板名（None=每个品类用推荐模板）
    
    Returns:
        list[dict]: 8条笔记
    """
    notes = []
    for cat in CATEGORIES:
        if template_override:
            tmpl = template_override
        else:
            recommended = get_recommended_templates(cat)
            tmpl = recommended[0] if recommended else "干货/清单流"
        
        note = generate_by_template(hotel_name, hotel_info, cat, tmpl)
        notes.append(note)
    
    return notes


# ===== 原有的硬编码内容（向后兼容） =====
# 以下内容在2026-05-29已生成为有效笔记，保留作为回退/参考

LEGACY_NOTES_CREATOR = {
    "成都W酒店": {
        "高净值度假客/蜜月": {
            "title": "🌅 当老外第一次住进成都W酒店，直接被震撼到说不出话",
            "summary": "带意大利朋友入住体验，外国人视角+酒店控"
        },
        "商务实效型": {
            "title": "成都出差住W酒店｜3天2晚全体验｜值不值看完你就知道",
            "summary": "数据化评分，商务出差实测"
        },
        "实时红利截流型": {
            "title": "⚠️ 老外都抢着来成都了！端午想订成都W酒店的抓紧看",
            "summary": "紧迫感标题+评论区钩子"
        }
    },
    "丽江悦榕庄": {
        "种草型范流量号": {
            "title": "丽江的夏天是20°C的，悦榕庄的院子里有一整个雪山",
            "summary": "散文体，情绪第一"
        },
        "干货价值类": {
            "title": "丽江悦榕庄全攻略｜房型、餐饮、活动一篇讲透",
            "summary": "分段+评分+信息密度高"
        }
    }
}


# ===== 主流酒店信息库（可扩展） =====

HOTEL_DB = {
    "成都W酒店": {
        "location": "成都",
        "features": ["潮牌设计", "高空夜景", "太古里旁", "DJ酒吧", "担担面早餐"],
        "vibe": "潮流时尚",
        "audience": "年轻潮人/情侣/商务",
        "price_range": "中高端",
        "highlights": "339电视塔景观、高空泳池、周末DJ"
    },
    "北京国贸大酒店": {
        "location": "北京",
        "features": ["CBD核心", "高空观景", "购物配套", "商务中心"],
        "vibe": "高端商务",
        "audience": "商务人士/旅客/家庭",
        "price_range": "高端",
        "highlights": "国贸CBD全景、央视大楼景观"
    },
    "丽江悦榕庄": {
        "location": "丽江",
        "features": ["雪山景观", "庭院别墅", "SPA温泉", "纳西风格"],
        "vibe": "自然度假",
        "audience": "度假客/蜜月/家庭",
        "price_range": "高端",
        "highlights": "玉龙雪山全景、悦榕SPA"
    },
    "广州花园酒店": {
        "location": "广州",
        "features": ["岭南园林", "旋转楼梯", "瀑布餐厅", "早茶"],
        "vibe": "岭南风情",
        "audience": "商务/家庭/游客",
        "price_range": "中高端",
        "highlights": "岭南园林设计、经典粤式早茶"
    },
    "黑河国际饭店": {
        "location": "黑河",
        "features": ["边境景观", "俄式风情", "江景房", "性价比"],
        "vibe": "边境特色",
        "audience": "边境游/小众/性价比",
        "price_range": "经济型",
        "highlights": "黑龙江景观、对望俄罗斯"
    },
    "稻城亚丁日松贡布酒店": {
        "location": "稻城·亚丁",
        "features": ["藏式风格", "高原景观", "雪山近景", "景区配套"],
        "vibe": "藏地自然",
        "audience": "自然爱好者/探险/摄影",
        "price_range": "中高端",
        "highlights": "亚丁景区最近高端酒店"
    },
    "腾冲石头纪": {
        "location": "腾冲",
        "features": ["火山石建筑", "温泉入户", "隐世度假", "设计师酒店"],
        "vibe": "隐世禅意",
        "audience": "高净值度假客/养生/蜜月",
        "price_range": "高端",
        "highlights": "隈研吾设计、火山石温泉"
    },
    "上海浦东丽思卡尔顿": {
        "location": "上海",
        "features": ["陆家嘴核心", "外滩景观", "高空酒吧", "名品购物"],
        "vibe": "奢华都市",
        "audience": "商务/高净值/名流",
        "price_range": "奢享",
        "highlights": "外滩+陆家嘴双景观"
    }
}


# ===== 飞书表操作 =====

def create_notes_table():
    """创建笔记裂变内容库表（如已存在则复用）"""
    print("\n=== 创建/获取笔记裂变内容库表 ===")
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_TOKEN}/tables'
    
    # 尝试查找已有表
    resp = api('GET', url)
    tables = resp.get('data', {}).get('items', [])
    for t in tables:
        if t['name'] == '笔记裂变内容库':
            print(f"  [Table] Found existing: {t['table_id']}")
            return t['table_id']
    
    # 创建新表
    body_data = {"table": {"name": "笔记裂变内容库", "fields": [
        {"field_name": "笔记标题", "type": 1},
    ]}}
    resp = api('POST', url, body_data)
    table_id = resp['data']['table_id']
    print(f"  [Table] Created: {table_id}")
    
    # 创建其他字段
    fields_config = [
        ("酒店名称", 3, {"options": [{"name": h} for h in HOTEL_DB.keys()]}),
        ("内容品类", 3, {"options": [{"name": c} for c in CATEGORIES]}),
        ("正文文案", 1, None),
        ("引用话题", 1, None),
        ("对标爆款风格", 1, None),
        ("备注", 1, None),
        ("使用模板", 1, None),
    ]
    
    for fname, ftype, fprop in fields_config:
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_TOKEN}/tables/{table_id}/fields'
        payload = {"field_name": fname, "type": ftype}
        if fprop:
            payload["property"] = fprop
        r = api('POST', url, payload)
        if r.get('code') == 0:
            print(f"  [Field] Created: {fname}")
        else:
            print(f"  [Field] {fname}: {r.get('msg', 'OK')}")
    
    return table_id


def delete_existing_records(table_id):
    """删除表中已有记录（避免重复）"""
    resp = api('GET',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_TOKEN}/tables/{table_id}/records?page_size=50')
    items = resp.get('data', {}).get('items')
    if items:
        for item in items:
            rid = item['record_id']
            api('DELETE',
                f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_TOKEN}/tables/{table_id}/records/{rid}')
        print(f"  [Clean] Deleted {len(items)} old records")
    else:
        print(f"  [Clean] No old records to delete")


def batch_insert_notes(table_id, notes):
    """批量插入笔记记录"""
    print(f"\n=== 批量插入 {len(notes)} 条笔记 ===")
    inserted = 0
    for i in range(0, len(notes), 10):
        batch = notes[i:i+10]
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_TOKEN}/tables/{table_id}/records/batch_create'
        payload = json.dumps({"records": [{"fields": r} for r in batch]}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='POST',
            headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json; charset=utf-8'})
        try:
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read())
            n = len(result.get('data', {}).get('records', []))
            print(f"  Batch {i//10+1}: Inserted {n} records")
            inserted += n
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300]
            print(f"  Batch {i//10+1}: Error {e.code}: {err}")
        time.sleep(0.5)
    print(f"[Insert] Total: {inserted}/{len(notes)}")
    return inserted


def verify_records(table_id):
    """验证笔记记录完整性"""
    print("\n=== 验证笔记 ===")
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{MAIN_TOKEN}/tables/{table_id}/records?page_size=50'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
    with urllib.request.urlopen(req) as f:
        verify = json.loads(f.read().decode())
    
    items = verify.get('data', {}).get('items', [])
    hotel_set = set()
    cat_set = set()
    issues = 0
    
    for item in items:
        fields = item.get('fields', {})
        hotel = fields.get('酒店名称', '')
        title = fields.get('笔记标题', '')[:30]
        cat = fields.get('内容品类', '')
        body = fields.get('正文文案', '')
        
        if hotel:
            hotel_set.add(hotel)
        else:
            print(f"  ⚠️ 酒店名称为空: {title}")
            issues += 1
        
        if cat:
            cat_set.add(cat)
        
        if body:
            # 验证合规性
            _, violations = audit_and_fix(body)
            if violations:
                print(f"  ⚠️ {title[:20]} 有 {len(violations)} 处违禁词残留")
                issues += 1
    
    print(f"  [Verify] {len(items)} records, "
          f"{len(hotel_set)} hotels: {hotel_set}, "
          f"{len(cat_set)} categories")
    if issues == 0:
        print("  ✅ 全部验证通过！")
    return issues


# ===== 合规处理 =====

def apply_compliance(notes):
    """对笔记列表统一做合规校验"""
    print("\n=== 合规校验 ===")
    for note in notes:
        body_text = note.get("正文文案", "")
        if body_text:
            clean_body, violations = audit_and_fix(body_text)
            if violations:
                print(f"  [合规] {note.get('笔记标题','')[:20]} - {len(violations)}处替换: {violations}")
            note["正文文案"] = clean_body
    return notes


# ===== 主流程控制 =====

def run_full_pipeline(hotel_name, template_override=None):
    """
    完整流程：创建表 → 生成 → 合规 → 写入 → 验证
    
    Args:
        hotel_name: 酒店名称
        template_override: 可选，统一使用的模板名
    
    Returns:
        bool: 是否成功
    """
    info = HOTEL_DB.get(hotel_name)
    if not info:
        print(f"[Error] 未找到酒店信息: {hotel_name}")
        print(f"  可用酒店: {list(HOTEL_DB.keys())}")
        return False
    
    print(f"===== 笔记裂变内容库 - {hotel_name} =====")
    
    # 1. 生成8品类笔记
    print(f"\n[生成] 使用{'默认推荐模板' if not template_override else template_override}")
    notes = generate_full_matrix(hotel_name, info, template_override)
    for n in notes:
        print(f"  [{n['内容品类']}] {n['笔记标题'][:40]}...")
    
    # 2. 合规校验
    notes = apply_compliance(notes)
    
    # 3. 飞书写入
    table_id = create_notes_table()
    delete_existing_records(table_id)
    inserted = batch_insert_notes(table_id, notes)
    
    # 4. 验证
    issues = verify_records(table_id)
    
    print(f"\n{'='*50}")
    print(f"URL: https://bytedance.feishu.cn/base/{MAIN_TOKEN}")
    print(f"Status: {'✅ 成功' if issues == 0 else f'⚠️ {issues}个问题'}")
    return issues == 0


def run_single_note(hotel_name, category, template_name):
    """生成单条笔记并打印"""
    info = HOTEL_DB.get(hotel_name)
    if not info:
        print(f"[Error] 未找到酒店信息: {hotel_name}")
        return
    
    note = generate_by_template(hotel_name, info, category, template_name)
    print(f"\n{'='*60}")
    print(f"📝 标题：{note['笔记标题']}")
    print(f"🏨 酒店：{note['酒店名称']}")
    print(f"📂 品类：{note['内容品类']}")
    print(f"📋 模板：{note['对标爆款风格']}")
    print(f"\n📄 正文：\n{note['正文文案'][:500]}{'...' if len(note['正文文案'])>500 else ''}")
    print(f"\n🏷️ 标签：{note['引用话题'][:200]}...")


def run_clone_generation(hotel_name, category, clone_text):
    """根据克隆特征生成笔记"""
    info = HOTEL_DB.get(hotel_name)
    if not info:
        print(f"[Error] 未找到酒店信息: {hotel_name}")
        return
    
    note = generate_by_clone(hotel_name, info, category, clone_text)
    print(f"\n{'='*60}")
    print(f"📝 标题：{note['笔记标题']}")
    print(f"📂 品类：{note['内容品类']}")
    print(f"🎯 克隆特征：{note['对标爆款风格'][:100]}")
    print(f"\n📄 正文指引：\n{note['正文文案'][:500]}")


def list_available_templates():
    """列出所有可用模板"""
    print(template_summary())
    print("\n=== 品类→推荐模板映射 ===")
    for cat, tmpls in CATEGORY_TEMPLATE_MAP.items():
        print(f"  {cat}")
        for t in tmpls:
            print(f"    → {t}")


def recommend_for_category(category):
    """推荐指定品类适合的模板"""
    recommended = get_recommended_templates(category)
    print(f"📂 品类：{category}")
    print(f"🎯 推荐模板：")
    for i, t in enumerate(recommended, 1):
        tmpl = TEMPLATES.get(t, {})
        print(f"  {i}. {t}")
        print(f"     {tmpl.get('description', '')[:60]}")
        print(f"     标题风格：{tmpl.get('title_style', '')[:40]}")
        print(f"     语气调性：{tmpl.get('tone', '')}")


def analyze_text_structure(text):
    """分析文案结构"""
    from clone_analyzer import analyze_text
    profile = analyze_text(text)
    import json
    print("\n=== 结构分析报告 ===")
    print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
    print(f"\n📊 结构摘要：{profile.summarize()}")


# ===== 命令行入口 =====

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='笔记裂变内容库生成引擎')
    
    # 模式选择
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--generate', action='store_true', help='单篇按模板生成')
    mode.add_argument('--full', action='store_true', help='8品类全量生成（默认）')
    mode.add_argument('--clone', action='store_true', help='对标克隆生成')
    mode.add_argument('--list-templates', action='store_true', help='列出所有模板')
    mode.add_argument('--recommend', action='store_true', help='品类推荐模板')
    mode.add_argument('--analyze', action='store_true', help='分析文案结构')
    mode.add_argument('--all', action='store_true', help='完整流程（创建表+生成+写入）')
    
    # 参数
    parser.add_argument('--hotel', type=str, default='', help='酒店名称')
    parser.add_argument('--category', type=str, default='', help='内容品类')
    parser.add_argument('--template', type=str, default='', help='模板名称')
    parser.add_argument('--text', type=str, default='', help='对标文案内容（手动粘贴）')
    parser.add_argument('--file', type=str, default='', help='从文件读取对标文案')
    
    args = parser.parse_args()
    
    # 默认行为：如果什么都没传，走演示模式
    has_mode = any([args.generate, args.full, args.clone, args.list_templates,
                    args.recommend, args.analyze, args.all])
    
    if not has_mode:
        # 演示模式：展示系统能力
        print("""
╔════════════════════════════════════════════════╗
║   笔记裂变内容库 — 模板化创作引擎 v2.0         ║
║                                                ║
║   10个风格模板 ｜ 对标克隆模式 ｜ 自动合规      ║
╚════════════════════════════════════════════════╝
        """)
        print("可用命令（示例）：")
        print("  --list-templates           # 查看所有模板")
        print("  --recommend --category '干货价值类'  # 品类推荐")
        print("  --generate --hotel '成都W酒店' --category '干货价值类' --template '干货/清单流'")
        print("  --full --hotel '成都W酒店'  # 8品类全量")
        print("  --clone --hotel '成都W酒店' --category '种草型范流量号' --text '文案...'")
        print("  --all --hotel '成都W酒店'   # 完整流程写入飞书")
        print("  --analyze --text '文案...'  # 结构分析")
        
        # 列出核心统计
        print(f"\n📊 核心统计")
        print(f"  模板：{len(TEMPLATES)}个")
        print(f"  品类：{len(CATEGORIES)}个")
        print(f"  酒店：{len(HOTEL_DB)}家")
        print(f"  示例笔记：10条（见 data/note_examples.json）")
        sys.exit(0)
    
    if args.list_templates:
        list_available_templates()
        sys.exit(0)
    
    if args.recommend:
        if not args.category:
            print("请指定 --category")
            sys.exit(1)
        recommend_for_category(args.category)
        sys.exit(0)
    
    if args.analyze:
        text = args.text
        if args.file and os.path.exists(args.file):
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        if not text:
            print("请提供文案（--text 或 --file）")
            sys.exit(1)
        analyze_text_structure(text)
        sys.exit(0)
    
    if args.generate:
        if not args.hotel or not args.category or not args.template:
            print("需要 --hotel, --category, --template 三个参数")
            print(f"可用模板: {list(TEMPLATES.keys())}")
            print(f"可用品类: {CATEGORIES}")
            print(f"可用酒店: {list(HOTEL_DB.keys())}")
            sys.exit(1)
        run_single_note(args.hotel, args.category, args.template)
        sys.exit(0)
    
    if args.clone:
        text = args.text
        if args.file and os.path.exists(args.file):
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        if not text:
            print("需要 --text（对标文案内容）或 --file（读文件）")
            sys.exit(1)
        if not args.hotel or not args.category:
            print("需要 --hotel 和 --category")
            sys.exit(1)
        run_clone_generation(args.hotel, args.category, text)
        sys.exit(0)
    
    if args.full or args.all:
        if not args.hotel:
            print("需要 --hotel 指定酒店名称")
            print(f"可选: {list(HOTEL_DB.keys())}")
            sys.exit(1)
        
        if args.full:
            # 仅生成不写入飞书
            info = HOTEL_DB.get(args.hotel)
            if not info:
                print(f"未找到酒店: {args.hotel}")
                sys.exit(1)
            notes = generate_full_matrix(args.hotel, info, args.template or None)
            notes = apply_compliance(notes)
            print(f"\n已生成 {len(notes)} 篇笔记:")
            for n in notes:
                print(f"  [{n['内容品类']}] {n['笔记标题'][:50]}")
                print(f"    模板: {n['对标爆款风格']}")
        else:
            # 完整流程
            success = run_full_pipeline(args.hotel, args.template or None)
            sys.exit(0 if success else 1)
