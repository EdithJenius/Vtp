#!/usr/bin/env python3
"""
note_generator.py — 核心笔记生成引擎

接收参数：(酒店信息, 目标品类, 模板名或克隆特征)
- 如果选模板 → 按模板结构填充内容
- 如果选克隆 → 按克隆结构填充内容
- 输出完整的标题+正文+话题标签
- 自动调用 xiaohongshu_compliance 做合规校验

使用方式:
    from note_generator import NoteGenerator
    
    gen = NoteGenerator()
    
    # 方式1：按模板生成
    note = gen.generate(
        hotel_name="成都W酒店",
        hotel_info={"location": "成都", "features": ["潮牌", "夜景"], "score": 4.5},
        category="干货价值类",
        template_name="干货/清单流"
    )
    
    # 方式2：按克隆特征生成
    note = gen.generate_from_clone(
        hotel_name="成都W酒店",
        hotel_info=hotel_info,
        category="种草型范流量号",
        clone_guide=clone_guide_dict
    )
    
    # 方式3：快速批量生成
    notes = gen.batch_generate(hotel_info, 8_categories_default)
"""

import json
import os
import sys
import random

# 加载模板库
from note_templates import TEMPLATES, CATEGORY_TEMPLATE_MAP, get_recommended_templates

# 加载合规校验
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xiaohongshu_compliance import audit_and_fix

# ====== 酒店信息模板（示例） ======
DEFAULT_HOTEL_INFO = {
    "成都W酒店": {
        "location": "成都",
        "city": "成都",
        "features": ["潮牌设计", "高空夜景", "太古里旁", "DJ酒吧", "担担面早餐"],
        "vibe": "潮流时尚",
        "audience": "年轻潮人/情侣/商务",
        "price_range": "中高端",
        "highlights": "339电视塔景观、高空泳池、周末DJ"
    },
    "北京国贸大酒店": {
        "location": "北京",
        "city": "北京",
        "features": ["CBD核心", "高空观景", "购物配套", "商务中心"],
        "vibe": "高端商务",
        "audience": "商务人士/旅客/家庭",
        "price_range": "高端",
        "highlights": "国贸CBD全景、央视大楼景观、连接国贸商城"
    },
    "丽江悦榕庄": {
        "location": "丽江",
        "city": "丽江",
        "features": ["雪山景观", "庭院别墅", "SPA温泉", "纳西风格"],
        "vibe": "自然度假",
        "audience": "度假客/蜜月/家庭",
        "price_range": "高端",
        "highlights": "玉龙雪山全景、悦榕SPA、纳西文化体验"
    },
    "广州花园酒店": {
        "location": "广州",
        "city": "广州",
        "features": ["岭南园林", "旋转楼梯", "瀑布餐厅", "早茶"],
        "vibe": "岭南风情",
        "audience": "商务/家庭/游客",
        "price_range": "中高端",
        "highlights": "岭南园林设计、经典粤式早茶、环市东路"
    },
    "黑河国际饭店": {
        "location": "黑河",
        "city": "黑河",
        "features": ["边境景观", "俄式风情", "江景房", "性价比"],
        "vibe": "边境特色",
        "audience": "边境游/小众/性价比",
        "price_range": "经济型",
        "highlights": "黑龙江景观、对望俄罗斯、中俄跨境游"
    },
    "稻城亚丁日松贡布酒店": {
        "location": "稻城·亚丁",
        "city": "稻城",
        "features": ["藏式风格", "高原景观", "雪山近景", "景区配套"],
        "vibe": "藏地自然",
        "audience": "自然爱好者/探险/摄影",
        "price_range": "中高端",
        "highlights": "亚丁景区最近高端酒店、藏式风格、高原纯氧"
    },
    "腾冲石头纪": {
        "location": "腾冲",
        "city": "腾冲",
        "features": ["火山石建筑", "温泉入户", "隐世度假", "设计师酒店"],
        "vibe": "隐世禅意",
        "audience": "高净值度假客/养生/蜜月",
        "price_range": "高端",
        "highlights": "隈研吾设计、火山石温泉、云峰山景观"
    },
    "上海浦东丽思卡尔顿": {
        "location": "上海",
        "city": "上海",
        "features": ["陆家嘴核心", "外滩景观", "高空酒吧", "名品购物"],
        "vibe": "奢华都市",
        "audience": "商务/高净值/名流",
        "price_range": "奢享",
        "highlights": "外滩+陆家嘴双景观、Flair顶层酒吧、ifc购物中心"
    }
}


# ====== 话题标签库 ======
CATEGORY_HASHTAGS = {
    "高净值度假客/蜜月": ["高端酒店", "度假", "蜜月", "酒店控", "奢华体验", "情侣出游", "旅行日常"],
    "商务实效型": ["商务酒店", "出差", "差旅攻略", "商务出行", "办公", "酒店推荐", "城市商务"],
    "实时红利截流型": ["限时优惠", "节假日", "预订攻略", "预警", "出行提醒", "旺季", "抢订"],
    "种草型范流量号": ["慢生活", "旅行日记", "治愈", "生活方式", "氛围感", "周末去哪儿", "打卡"],
    "干货价值类": ["全攻略", "酒店攻略", "旅行攻略", "干货", "收藏", "指南", "经验分享"],
    "教程攻略类": ["教程", "省钱攻略", "预订技巧", "干货", "薅羊毛", "手把手", "秘籍"],
    "避坑类": ["避坑", "真实测评", "拔草", "良心话", "实话实说", "经验", "注意事项"],
    "行业垂直类": ["行业分析", "旅游行业", "酒店管理", "深度", "观察", "趋势", "运营"],
}

GENERAL_HASHTAGS = [
    "旅游", "旅行", "酒店", "住宿", "打卡", "推荐", 
    "假期", "出行", "攻略", "探店", "生活", 
    "宝藏", "小众", "热门", "网红"
]


class NoteGenerator:
    """核心笔记生成引擎"""
    
    def __init__(self, hotel_info_db=None):
        self.hotel_info_db = hotel_info_db or DEFAULT_HOTEL_INFO
    
    def generate(self, hotel_name, hotel_info, category, template_name):
        """
        按模板结构生成一篇完整笔记
        
        Args:
            hotel_name: 酒店名称
            hotel_info: 酒店信息字典（包含location, features, highlights等）
            category: 内容品类（如"干货价值类"）
            template_name: 模板名称（如"干货/清单流"）
        
        Returns:
            dict: 包含笔记标题、正文文案、引用话题的字典
        """
        template = TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"未知模板: {template_name}，可选: {list(TEMPLATES.keys())}")
        
        # 由模板结构和酒店信息生成内容
        template['_name'] = template_name
        note = self._fill_template(
            template=template,
            hotel_name=hotel_name,
            hotel_info=hotel_info,
            category=category
        )
        
        # 生成话题标签
        hashtags = self._generate_hashtags(hotel_name, hotel_info, category)
        note["引用话题"] = hashtags
        
        # 合规校验
        note["正文文案"], violations = audit_and_fix(note["正文文案"])
        
        return note
    
    def generate_from_clone(self, hotel_name, hotel_info, category, clone_guide):
        """
        根据克隆特征生成笔记
        
        Args:
            hotel_name: 酒店名称
            hotel_info: 酒店信息字典
            category: 内容品类
            clone_guide: clone_analyzer.clone_structure_to_guide() 的输出
        
        Returns:
            dict: 包含笔记标题、正文文案、引用话题的字典
        """
        # 根据克隆特征标记本次生成模式
        style_notes = f"对标克隆风格：{clone_guide.get('structure_summary', '')}"
        
        clone_title = clone_guide.get("clone_title_style", {})
        clone_para = clone_guide.get("clone_paragraph_style", {})
        clone_tone = clone_guide.get("clone_tone", "口语/亲切")
        clone_emoji = clone_guide.get("clone_emoji_style", {})
        
        # 构建生成上下文
        features_str = "，".join(hotel_info.get("features", []))
        highlights_str = hotel_info.get("highlights", "")
        
        # 根据克隆特征构造内容生成指引
        structure_desc = self._build_clone_structure_desc(clone_para, clone_title, clone_tone, clone_emoji)
        
        note = {
            "笔记标题": self._make_clone_title(hotel_name, hotel_info, clone_title, clone_tone),
            "正文文案": f"【克隆结构参考】{structure_desc}\n\n"
                       f"【酒店】{hotel_name} | {hotel_info.get('location', '')}\n"
                       f"【特色】{features_str}\n"
                       f"【亮点】{highlights_str}\n"
                       f"以上为生成参考信息，实际AI填充时将按克隆结构展开。",
            "对标爆款风格": style_notes,
        }
        
        # 生成标签
        hashtags = self._generate_hashtags(hotel_name, hotel_info, category)
        note["引用话题"] = hashtags
        
        # 合规校验
        note["正文文案"], violations = audit_and_fix(note["正文文案"])
        
        return note
    
    def batch_generate(self, hotel_name, hotel_info, categories=None):
        """
        为一家酒店批量生成8品类笔记（每个品类推荐的最优模板）
        
        Args:
            hotel_name: 酒店名称
            hotel_info: 酒店信息字典
            categories: 品类列表，默认8个品类
        
        Returns:
            list[dict]: 笔记列表
        """
        if categories is None:
            categories = list(CATEGORY_TEMPLATE_MAP.keys())
        
        notes = []
        for cat in categories:
            recommended = get_recommended_templates(cat)
            # 选推荐模板中的第一个
            tmpl_name = recommended[0] if recommended else "干货/清单流"
            
            note = self.generate(hotel_name, hotel_info, cat, tmpl_name)
            note["酒店名称"] = hotel_name
            note["内容品类"] = cat
            note["对标爆款风格"] = f"模板：{tmpl_name}"
            notes.append(note)
        
        return notes
    
    def _fill_template(self, template, hotel_name, hotel_info, category):
        """根据模板结构填充笔记内容"""
        
        features = hotel_info.get("features", [])
        highlights = hotel_info.get("highlights", "")
        location = hotel_info.get("location", "")
        vibe = hotel_info.get("vibe", "")
        
        tmpl_name = template.get("_name", "") or template.get("name", "")
        
        # 构建标题
        title = self._make_title(template, hotel_name, hotel_info, category)
        
        # 构建正文大纲占位（实际使用时AI会根据结构填充具体内容）
        body_parts = []
        
        # 结构说明
        structure_guide = "\n".join(template["structure"])
        
        body = (
            f"【模板：{tmpl_name}】\n"
            f"【酒店】{hotel_name}（{location}）\n"
            f"【特色】{'、'.join(features)}\n"
            f"【品类】{category}\n\n"
            f"按以下结构生成：\n{structure_guide}\n\n"
            f"标题风格：{template['title_style']}\n"
            f"语气调性：{template['tone']}\n"
            f"emoji规则：{template['emoji_rule']}\n"
            f"段落长度：{template['paragraph_length']}"
        )
        
        return {"笔记标题": title, "正文文案": body}
    
    def _make_title(self, template, hotel_name, hotel_info, category):
        """根据模板风格构造标题"""
        
        location = hotel_info.get("location", "")
        
        title_patterns = {
            "干货/清单流": f"{hotel_name}全攻略｜一篇讲透房型、餐饮、周边",
            "情绪种草流": random.choice([
                f"在{hotel_name}住了一晚，我理解了什么叫{random.choice(['治愈', '浪漫', '松弛', '腔调'])}",
                f"{location}最{random.choice(['温柔', '美好', '值得', '出片'])}的地方，是{hotel_name}",
            ]),
            "测评对比流": f"{hotel_name}亲测｜到底值不值｜3天2晚真实体验",
            "行业分析流": f"从{location}酒店市场看{random.choice(['高端住宿', '度假经济', '文旅趋势'])}｜{hotel_name}的产品逻辑",
            "截流紧迫感流": f"⚠️{location}最近太火了！想订{hotel_name}的名额抓紧看",
            "Vlog日程流": f"在{hotel_name}的24小时｜从早到晚都干了什么",
            "反差点评流": f"去{hotel_name}之前：不就是个酒店吗 去之后：真香",
            "科普涨知识流": f"第一次住{hotel_name}？{random.choice(['90%的人不知道', '这5件事一定要知道', '看完这篇再去'])}",
            "真实UGC流": f"真诚分享｜在{hotel_name}住了2天的真实感受（不带滤镜）",
            "问答攻略流": f"关于{hotel_name}，你最想知道的{random.choice(['10个', '8个', '6个'])}问题一次解答",
        }
        
        tmpl_key = template.get("_name", "")
        return title_patterns.get(tmpl_key, f"{hotel_name}入住体验分享")
    
    def _make_clone_title(self, hotel_name, hotel_info, clone_title_style, clone_tone):
        """根据克隆特征构造标题"""
        
        has_emoji = clone_title_style.get("has_emoji", False)
        hook_type = clone_title_style.get("hook_type", "直白型")
        length_approx = clone_title_style.get("length_approx", 20)
        
        # 根据钩子类型生成对应标题
        if hook_type == "emoji情感钩子":
            return f"🌅 在{hotel_name}住了一晚，被震撼到说不出话"
        elif hook_type == "数字钩子":
            return f"{hotel_name}的5个隐藏玩法，第3个没多少人知道"
        elif hook_type == "对比钩子":
            return f"去{hotel_name}之前vs之后，差别有多大"
        elif hook_type == "紧迫钩子":
            return f"⚠️ {hotel_name}马上要涨价了，还没订的抓紧"
        elif hook_type == "攻略钩子":
            return f"{hotel_name}全攻略｜一篇讲透所有你想知道的"
        elif hook_type == "情感钩子":
            return f"在{hotel_name}，我找到了理想中度假的样子"
        else:
            return f"{hotel_name}｜{hotel_info.get('location', '')}的宝藏住宿体验"
    
    def _build_clone_structure_desc(self, clone_para, clone_title, clone_tone, clone_emoji):
        """构建克隆结构描述文本"""
        parts = []
        parts.append(f"段落：{clone_para.get('paragraph_count', '?')}段")
        parts.append(f"分段方式：{clone_para.get('section_indicator', '自然分段')}")
        if clone_para.get("has_sections"):
            parts.append("有分节标题")
        if clone_para.get("has_contrast"):
            parts.append("有对比结构")
        if clone_para.get("has_list"):
            parts.append("有列表")
        parts.append(f"语气：{clone_tone}")
        parts.append(f"emoji密度：{clone_emoji.get('density', 0)}个/100字")
        return "｜".join(parts)
    
    def _generate_hashtags(self, hotel_name, hotel_info, category):
        """生成15-20个话题标签"""
        location = hotel_info.get("location", "")
        
        # 基础标签（酒店+地点）
        base_tags = [
            f"#{hotel_name}",
            f"#{location}旅游",
            f"#{location}酒店",
        ]
        
        # 品类标签
        cat_tags = CATEGORY_HASHTAGS.get(category, [])
        cat_tags = [f"#{t}" for t in cat_tags[:5]]
        
        # 通用标签
        general = random.sample(GENERAL_HASHTAGS, min(8, len(GENERAL_HASHTAGS)))
        general = [f"#{t}" for t in general]
        
        # 组合去重
        all_tags = base_tags + cat_tags + general
        seen = set()
        unique_tags = []
        for tag in all_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
        # 裁剪到15-20个
        if len(unique_tags) > 20:
            unique_tags = unique_tags[:20]
        
        return " ".join(unique_tags)


# ====== 便捷函数 ======

def generate_note(hotel_name, category, template_name, hotel_info=None, hotel_info_db=None):
    """便捷单篇笔记生成接口"""
    db = hotel_info_db or DEFAULT_HOTEL_INFO
    
    if hotel_info is None:
        hotel_info = db.get(hotel_name, {
            "location": "",
            "features": [],
            "highlights": "",
            "vibe": ""
        })
    
    gen = NoteGenerator(hotel_info_db=db)
    return gen.generate(hotel_name, hotel_info, category, template_name)


def generate_all_for_hotel(hotel_name, hotel_info=None, hotel_info_db=None):
    """为一家酒店生成所有品类的笔记"""
    db = hotel_info_db or DEFAULT_HOTEL_INFO
    
    if hotel_info is None:
        hotel_info = db.get(hotel_name, {
            "location": "",
            "features": [],
            "highlights": "",
            "vibe": ""
        })
    
    gen = NoteGenerator(hotel_info_db=db)
    return gen.batch_generate(hotel_name, hotel_info)


if __name__ == "__main__":
    gen = NoteGenerator()
    
    # 测试单篇
    print("=== 单篇生成测试 ===")
    note = gen.generate("成都W酒店", DEFAULT_HOTEL_INFO["成都W酒店"], 
                         "干货价值类", "干货/清单流")
    print(f"标题: {note['笔记标题']}")
    print(f"正文({len(note['正文文案'])}字): {note['正文文案'][:200]}...")
    print(f"标签: {note['引用话题'][:100]}...")
    
    # 测试批量
    print("\n=== 批量生成测试（成都W酒店） ===")
    notes = gen.batch_generate("成都W酒店", DEFAULT_HOTEL_INFO["成都W酒店"])
    for n in notes:
        print(f"  [{n['内容品类']}] {n['笔记标题']}")
    
    print(f"\n共生成 {len(notes)} 篇笔记")
