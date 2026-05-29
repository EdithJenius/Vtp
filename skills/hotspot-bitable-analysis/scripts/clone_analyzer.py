#!/usr/bin/env python3
"""
clone_analyzer.py — 对标克隆模块

功能：接收一条小红书笔记链接（或手动粘贴的文案），分析其结构特征：
- 标题模式（有无emoji、长度、钩子类型）
- 段落编排（段长、分隔方式）
- 语气调性（正式/口语/情绪）
- emoji密度和类型
- 是否有分节/列表/对比
- 输出结构特征描述

使用方式:
    from clone_analyzer import analyze_text, analyze_url, StructureProfile

    # 手动粘贴文案分析
    profile = analyze_text("标题\n\n正文内容...")

    # URL分析（可能不完整）
    profile = analyze_url("https://www.xiaohongshu.com/...")

    # 获取结构摘要
    summary = profile.to_dict()
"""

import re
import json


class StructureProfile:
    """文本结构特征分析结果"""
    
    def __init__(self, title="", body=""):
        self.title = title
        self.body = body
        self.title_length = len(title)
        self.has_title_emoji = bool(re.search(r'[\U0001F300-\U0001F9FF\u2600-\u27FF]', title))
        self.title_emojis = re.findall(r'[\U0001F300-\U0001F9FF\u2600-\u27FF\u2934-\u2935]', title)
        
        # 钩子类型
        self.hook_type = self._classify_hook(title)
        
        # 段落分析
        self.paragraphs = self._split_paragraphs(body)
        self.paragraph_count = len(self.paragraphs)
        self.avg_paragraph_length = sum(len(p) for p in self.paragraphs) / max(len(self.paragraphs), 1)
        
        # emoji分析
        self.body_emojis = re.findall(r'[\U0001F300-\U0001F9FF\u2600-\u27FF\u2934-\u2935]', body)
        self.emoji_density = len(self.body_emojis) / max(len(body), 1)
        self.emoji_types = self._classify_emojis(self.body_emojis)
        
        # 语气分析
        self.tone = self._detect_tone(body)
        
        # 结构特征
        self.has_section_headers = bool(re.search(r'^[^\n]{1,20}[：:]', body, re.MULTILINE))
        self.has_bullet_points = bool(re.search(r'[•·\-*] |\d+[\.\)] ', body))
        self.has_contrast = bool(
            re.search(r'(优缺点|对比|vs|VS|VS|一方面|另一方面|✅|❌|以前|现在|但是|然而)', body)
        )
        self.has_list = bool(re.search(r'\d\.\s', body))
        self.has_question = bool(re.search(r'[？?]\n|^[Qq][：:]|[？?]$', body, re.MULTILINE))
        
        # 分段特征
        self.section_indicator = self._detect_section_indicator(body)
        
        # 字数统计
        self.char_count = len(body.replace("\n", "").replace(" ", "").replace("#", ""))
    
    def _classify_hook(self, title):
        """分类标题钩子类型"""
        hook_patterns = {
            "emoji情感钩子": r'[\U0001F300-\U0001F9FF\u2600-\u27FF].{0,10}(震撼|绝了|哭|笑|美|爱|值得|后悔|感动)',
            "数字钩子": r'\d+(个|天|年|步|招|种|款|点)',
            "对比钩子": r'(之前|之后|vs|VS|vs|前|后)',
            "疑问钩子": r'[？?]',
            "紧迫钩子": r'(⚠|🔥|⏰|抓紧|马上|最后|紧急)',
            "悬念钩子": r'(没想到|竟然|居然|原来|发现|揭秘)',
            "攻略钩子": r'(攻略|指南|教程|合集|全|篇)',
            "情感钩子": r'(后悔|哭了|震撼|绝美|治愈|温柔|浪漫|好想)',
        }
        for hook_type, pattern in hook_patterns.items():
            if re.search(pattern, title):
                return hook_type
        return "直白型"
    
    def _split_paragraphs(self, text):
        """智能分段"""
        lines = text.split('\n')
        paragraphs = []
        current = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current:
                    paragraphs.append('\n'.join(current))
                    current = []
            else:
                current.append(stripped)
        if current:
            paragraphs.append('\n'.join(current))
        return paragraphs if paragraphs else [text]
    
    def _classify_emojis(self, emojis):
        """分类emoji类型"""
        categories = {"情绪类": 0, "物品类": 0, "动作类": 0, "符号类": 0, "其他": 0}
        emotion_emoji = set("😊😍😂🤩😭😅🤔😏😌😤😡🥺😴🤗😉🙃😘🥰😎🤓")
        item_emoji = set("📱💻📸🎁🛁🍽️🍜☕🎵🏠📖💡🔍🎯🏨🌅✨🌿🌸🏔️🌊🌙💎🛎️🧳🎒👗👠🧴🌂🕶️")
        action_emoji = set("🚗✈️🚄🚶‍♂️🏃💃📝📋✅❌💬👇👉🔼🔽↗️↘️")
        symbol_emoji = set("⭐🌟⚡🔥⚠️⏰💢💯♨️📌🔗💕💖💗💓")
        
        for e in emojis:
            if e in emotion_emoji:
                categories["情绪类"] += 1
            elif e in item_emoji:
                categories["物品类"] += 1
            elif e in action_emoji:
                categories["动作类"] += 1
            elif e in symbol_emoji:
                categories["符号类"] += 1
            else:
                categories["其他"] += 1
        return categories
    
    def _detect_tone(self, text):
        """检测语气调性"""
        formal_indicators = [
            '数据', '调查', '统计', '分析', '产品', '行业', 
            '报告', '方案', '建议', '评估', '指标', '维度'
        ]
        conversational_indicators = [
            '说实话', '其实', '但是呢', '毕竟', '反正', '就是', 
            '然后', '真的', '对了', '好吧', '不过', '话说', 
            '我个人', '感觉', '可能', '有点', '稍微'
        ]
        emotional_indicators = [
            '啊', '呀', '哇', '哦', '呢', '嘛', '～', '~',
            '哭了', '绝了', '太', '好', '超', '巨', '无敌',
            '心', '爱', '哭', '笑'
        ]
        
        text_lower = text
        formal_score = sum(text_lower.count(w) for w in formal_indicators)
        conv_score = sum(text_lower.count(w) for w in conversational_indicators)
        emo_score = sum(text_lower.count(w) for w in emotional_indicators)
        
        if formal_score > conv_score and formal_score > emo_score:
            return "正式/专业"
        elif emo_score > formal_score and emo_score > conv_score:
            return "情绪/感性"
        else:
            return "口语/亲切"
    
    def _detect_section_indicator(self, text):
        """检测分段标识方式"""
        if re.search(r'^[^\n]{1,30}[：:]', text, re.MULTILINE):
            return "中文字标题+冒号"
        if re.search(r'^[•·\-*] ', text, re.MULTILINE):
            return "无序列表"
        if re.search(r'^\d+[\.\)] ', text, re.MULTILINE):
            return "有序列表"
        if re.search(r'^【[^】]+】', text, re.MULTILINE):
            return "【】括号标题"
        if re.search(r'^[A-Z][a-z]+：', text, re.MULTILINE):
            return "英文字母+冒号"
        return "自然换行分段"
    
    def to_dict(self):
        """输出结构特征字典"""
        return {
            "标题分析": {
                "标题": self.title,
                "长度": self.title_length,
                "含emoji": self.has_title_emoji,
                "标题emoji": self.title_emojis,
                "钩子类型": self.hook_type,
            },
            "段落编排": {
                "段落数": self.paragraph_count,
                "平均段长(字)": round(self.avg_paragraph_length, 1),
                "总字数": self.char_count,
                "分段方式": self.section_indicator,
                "有分节标题": self.has_section_headers,
                "有列表": self.has_list,
                "有对比结构": self.has_contrast,
                "有问答模式": self.has_question,
            },
            "语气调性": {
                "语气": self.tone,
                "有bullet清单": self.has_bullet_points,
            },
            "emoji使用": {
                "正文emoji总数": len(self.body_emojis),
                "emoji密度(个/100字)": round(self.emoji_density * 100, 1),
                "类型分布": self.emoji_types,
            },
            "结构摘要": self.summarize()
        }
    
    def summarize(self):
        """生成人类可读的结构摘要"""
        parts = []
        
        # 标题特征
        hook_desc = f"标题类型：{self.hook_type}，"
        hook_desc += f"{'含' if self.has_title_emoji else '不含'}emoji，"
        hook_desc += f"长度{self.title_length}字"
        parts.append(hook_desc)
        
        # 段落特征
        para_desc = f"共{self.paragraph_count}段，平均每段{round(self.avg_paragraph_length)}字"
        if self.has_section_headers:
            para_desc += "，有分节标题"
        if self.has_contrast:
            para_desc += "，有对比结构"
        if self.has_bullet_points:
            para_desc += "，有清单列表"
        if self.has_question:
            para_desc += "，有问答格式"
        parts.append(para_desc)
        
        # emoji特征
        emoji_desc = f"正文emoji {len(self.body_emojis)}个，密度{round(self.emoji_density * 100, 1)}个/100字"
        dominant = max(self.emoji_types, key=self.emoji_types.get)
        emoji_desc += f"，以{dominant}为主"
        parts.append(emoji_desc)
        
        # 语气
        parts.append(f"语气：{self.tone}")
        
        return "｜".join(parts)


def analyze_text(text):
    """
    分析手动粘贴/传入的文案结构特征
    
    Args:
        text: 完整的笔记文案（含标题，标题和正文用\n\n分隔）
              如果第一行较短则视为标题
    
    Returns:
        StructureProfile 对象
    """
    lines = text.strip().split('\n')
    
    # 尝试分离标题和正文
    title = ""
    body = text
    
    if len(lines) > 1:
        first = lines[0].strip()
        if len(first) < 80 and not first.startswith('#'):
            # 第一行可能是标题
            second = lines[1].strip()
            if not second:
                title = first
                body = '\n'.join(lines[2:])
    
    if not title:
        title = lines[0][:50] if lines else ""
    
    return StructureProfile(title, body)


def analyze_url(url):
    """
    通过URL获取笔记并分析（由于小红书限制，可能无法完整抓取）
    
    返回:
        profile: StructureProfile 或 None
        提示信息
    """
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) '
                              'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as f:
            html = f.read().decode('utf-8', errors='replace')
        
        # 尝试提取正文（小红书的页面结构不公开）
        # 仅做基础尝试
        texts = re.findall(r'<p[^>]*>(.*?)</p>', html)
        content = '\n'.join(texts) if texts else html[:5000]
        
        profile = analyze_text(content)
        return profile, f"从URL提取{len(content)}字符，可能不完整"
    
    except Exception as e:
        return None, f"URL分析失败：{str(e)}"


def clone_structure_to_guide(profile, hotel_name, category):
    """
    将克隆的结构特征转为内容生成指引
    
    Args:
        profile: StructureProfile 对象
        hotel_name: 酒店名称
        category: 内容品类
    
    Returns:
        dict: 生成指引，可传给 note_generator
    """
    d = profile.to_dict()
    return {
        "clone_source": True,
        "clone_title_style": {
            "has_emoji": d["标题分析"]["含emoji"],
            "emoji": d["标题分析"]["标题emoji"],
            "hook_type": d["标题分析"]["钩子类型"],
            "length_approx": d["标题分析"]["长度"],
        },
        "clone_paragraph_style": {
            "paragraph_count": d["段落编排"]["段落数"],
            "avg_length": d["段落编排"]["平均段长(字)"],
            "has_sections": d["段落编排"]["有分节标题"],
            "has_contrast": d["段落编排"]["有对比结构"],
            "has_bullets": profile.has_bullet_points,
            "has_list": d["段落编排"]["有列表"],
            "section_indicator": d["段落编排"]["分段方式"],
        },
        "clone_tone": d["语气调性"]["语气"],
        "clone_emoji_style": {
            "density": d["emoji使用"]["emoji密度(个/100字)"],
            "dominant_type": max(d["emoji使用"]["类型分布"], key=d["emoji使用"]["类型分布"].get),
        },
        "structure_summary": d["结构摘要"],
        "hotel_name": hotel_name,
        "category": category,
    }


if __name__ == "__main__":
    # 测试
    sample_text = """成都W酒店全攻略｜房型、餐饮、周边一篇讲透

🏠 房型怎么选
来成都W住过三次，每次选不同房型。这次把体验汇总一下。
基础房型性价比最高，落地窗看339电视塔。
套房空间大，浴室泡澡能看夜景。

🍽️ 吃什么
早餐的担担面绝了，一定要试。
酒吧有DJ打碟，氛围感拉满。

总结：第一次来成都住W不会后悔。"""

    profile = analyze_text(sample_text)
    print("=== 结构分析结果 ===")
    print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
    print("\n=== 结构摘要 ===")
    print(profile.summarize())
    
    # 测试克隆指引
    guide = clone_structure_to_guide(profile, "成都W酒店", "干货价值类")
    print("\n=== 克隆生成指引 ===")
    print(json.dumps(guide, ensure_ascii=False, indent=2))
