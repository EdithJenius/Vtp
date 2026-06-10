# -*- coding: utf-8 -*-
"""
公众号风格拆解引擎（Style Analyzer）
输入：mp.weixin.qq.com 文章正文文本
输出：12维度风格画像
"""
import json, re, os
from collections import Counter

class StyleAnalyzer:
    def __init__(self, article_text, title="", account_name="", author=""):
        self.text = article_text
        self.title = title
        self.account_name = account_name
        self.author = author
        self.report = {}

    def analyze_all(self):
        """执行全部12维度分析"""
        self.report["基础信息"] = self._analyze_basic()
        self.report["标题风格"] = self._analyze_title()
        self.report["开头策略"] = self._analyze_opening()
        self.report["正文结构"] = self._analyze_structure()
        self.report["语气调性"] = self._analyze_tone()
        self.report["视觉格式"] = self._analyze_visual()
        self.report["选词偏好"] = self._analyze_vocab()
        self.report["结尾模式"] = self._analyze_ending()
        self.report["转化手法"] = self._analyze_conversion()
        self.report["人设定位"] = self._analyze_persona()
        return self.report

    def _analyze_basic(self):
        return {
            "公众号": self.account_name or "未知",
            "作者/IP": self.author or "未知",
            "文章标题": self.title or "未知",
            "正文字数": len(self.text),
            "段落数": self.text.count("\n") + 1,
        }

    def _analyze_title(self):
        title = self.title
        if not title:
            return {"error": "无标题"}
        has_emoji = bool(re.findall(r'[\U0001F300-\U0001FFFF\u2600-\u27BF]', title))
        return {
            "标题": title,
            "长度": len(title),
            "含Emoji": has_emoji,
            "标题结构": self._classify_title(title),
            "钩子类型": self._detect_hook(title),
        }

    def _classify_title(self, title):
        if re.search(r'\d+', title):
            return "数字型"
        if any(kw in title for kw in ["吗", "?", "？", "为什么", "怎么"]):
            return "疑问型"
        if any(kw in title for kw in ["!", "！", "绝了", "必", "别"]):
            return "感叹型"
        if re.search(r'vs|对比|还是', title):
            return "对比型"
        if "去之前" in title or "后悔" in title:
            return "反转型"
        return "陈述型"

    def _detect_hook(self, title):
        hooks = []
        if re.search(r'\d+', title):
            hooks.append("数字钩子")
        if any(kw in title for kw in ["隐藏", "秘密", "不知道", "不会告诉"]):
            hooks.append("揭秘钩子")
        if any(kw in title for kw in ["吗", "?", "？"]):
            hooks.append("疑问钩子")
        if any(kw in title for kw in ["免费", "好价", "优惠", "省钱"]):
            hooks.append("利益钩子")
        if any(kw in title for kw in ["绝了", "爆", "必看", "太"]):
            hooks.append("情绪钩子")
        if "vs" in title.lower() or "对比" in title:
            hooks.append("对比钩子")
        return hooks or ["无典型钩子"]

    def _analyze_opening(self):
        """分析前200字"""
        opening = self.text[:200]
        first_sentence = self.text.split("。")[0] if "。" in self.text else self.text[:50]
        paras = [p.strip() for p in self.text.split("\n") if p.strip()]
        intro_paras = paras[:3] if paras else []

        # 判断开头类型
        opening_type = "未知"
        if any(kw in first_sentence for kw in ["如果你", "当你", "想象", "有没有"]):
            opening_type = "场景代入型"
        elif any(kw in first_sentence for kw in ["为什么", "怎么", "吗"]):
            opening_type = "痛点提问型"
        elif any(kw in first_sentence for kw in ["绕不开", "都知道", "众所周知"]):
            opening_type = "共识建立型"
        elif "先Po" in first_sentence or "先看" in first_sentence or "先说" in first_sentence:
            opening_type = "开门见山型(先放商品)"
        elif any(kw in first_sentence for kw in ["最近", "今天", "昨天"]):
            opening_type = "时效引入型"

        return {
            "首句(前50字)": first_sentence[:50],
            "开头类型": opening_type,
            "铺垫字数": len(opening),
            "第几句进入正题": self._find_entry_point(),
        }

    def _find_entry_point(self):
        """找到开头到出现商品/核心信息前的字数"""
        entry_kw = ["先Po", "套餐", "价格", "购买", "这次", "优惠"]
        for kw in entry_kw:
            idx = self.text.find(kw)
            if 0 < idx < 500:
                return idx
        return "软性引入(无硬转折)"

    def _analyze_structure(self):
        paras = [p.strip() for p in self.text.split("\n") if p.strip()]
        if not paras:
            return {"error": "无段落"}

        para_lengths = [len(p) for p in paras]
        avg_len = sum(para_lengths) / len(para_lengths)

        if avg_len < 50:
            rhythm = "快节奏（短段落密集）"
        elif avg_len < 150:
            rhythm = "中节奏"
        else:
            rhythm = "慢节奏（长段落铺陈）"

        # 检查分隔符
        has_separators = any(p in self.text for p in ["---", "***", "——"])
        # 检查小标题
        subtitles = [p for p in paras if len(p) < 30 and p.startswith(("说", "接", "再", "关")) or p.endswith("：")]
        # 检查emoji分段
        emoji_paras = [p for p in paras if re.search(r'[\U0001F300-\U0001FFFF]', p) and len(p) < 100]

        return {
            "总段落数": len(paras),
            "平均段长": int(avg_len),
            "节奏感": rhythm,
            "使用分隔符": has_separators,
            "小标题分段": len(subtitles) > 0,
            "Emoji分段": len(emoji_paras) > 0,
        }

    def _analyze_tone(self):
        text = self.text[:1000]
        exclamation = text.count("！") + text.count("!")
        question = text.count("？") + text.count("?")
        emoji_count = len(re.findall(r'[\U0001F300-\U0001FFFF\u2600-\u27BF]', text))

        # 人称偏好
        i_count = text.count("我")
        you_count = text.count("你")
        we_count = text.count("我们")

        tone = "中"
        if exclamation > 5:
            tone = "高（情绪饱满）"
        elif exclamation < 2:
            tone = "低（克制冷静）"

        return {
            "感叹号/千字": exclamation,
            "问号/千字": question,
            "Emoji密度/千字": emoji_count,
            "正式度": "口语化" if (i_count + you_count) > 10 else "半正式",
            "人称偏好": "第二人称(你)" if you_count > i_count else "第一人称(我)",
            "语气词": self._detect_particles(text),
        }

    def _detect_particles(self, text):
        particles = ["啊", "吗", "呢", "哦", "呗", "吧", "嘛", "啦"]
        found = [p for p in particles if p in text]
        return found if found else ["无典型语气词"]

    def _analyze_visual(self):
        text = self.text[:2000]
        emoji_total = len(re.findall(r'[\U0001F300-\U0001FFFF\u2600-\u27BF]', text))
        return {
            "Emoji总数(前2000字)": emoji_total,
            "标点偏好": self._detect_punctuation(text),
            "重点标记": "加粗使用" if "**" in text else "无加粗",
        }

    def _detect_punctuation(self, text):
        pref = []
        if "——" in text:
            pref.append("破折号")
        if "..." in text or "…" in text:
            pref.append("省略号")
        if "！" in text:
            pref.append("感叹号")
        if "\"" in text or "「" in text:
            pref.append("引号")
        return pref

    def _analyze_vocab(self):
        words = re.findall(r'[\u4e00-\u9fff]{2,4}', self.text[:2000])
        counter = Counter(words)
        top20 = counter.most_common(20)
        return {"高频词(Top20)": [w for w, c in top20]}

    def _analyze_ending(self):
        ending = self.text[-300:] if len(self.text) > 300 else self.text
        has_guide = "关注" in ending or "在看" in ending or "转发" in ending
        has_bio = "作者" in ending or "主理人" in ending or "博主" in ending
        has_cta = any(kw in ending for kw in ["点击", "左下角", "阅读原文", "链接"])
        return {
            "引导关注": has_guide,
            "个人签名": has_bio,
            "CTA按钮": has_cta,
        }

    def _analyze_conversion(self):
        """检测转化手法"""
        text = self.text
        methods = []
        if "淘口令" in text or "淘宝" in text:
            methods.append("淘宝/淘口令")
        if "购买" in text or "下单" in text:
            methods.append("直接购买引导")
        if "不约可退" in text or "过期自动退" in text:
            methods.append("无风险承诺(不约可退)")
        if "有效期" in text:
            methods.append("有效期提示")
        if "补差" in text:
            methods.append("补差价说明")
        if "券" in text or "满减" in text:
            methods.append("优惠券攻略")
        return methods or ["无显性转化"]

    def _analyze_persona(self):
        """人设定位分析"""
        bio_start = self.text.find("我是")
        bio_text = ""
        if bio_start >= 0 and bio_start > len(self.text) - 500:
            bio_text = self.text[bio_start:bio_start+100]

        return {
            "作者自述": bio_text.strip() if bio_text else "未在文末找到自述",
        }

    def to_markdown(self):
        """输出可读的风格画像报告"""
        lines = []
        lines.append(f"# 📋 公众号风格画像报告")
        lines.append(f"**{self.account_name}** | 作者: {self.author} | 文章: {self.title}\n")

        for section, data in self.report.items():
            lines.append(f"## {section}\n")
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        lines.append(f"- **{k}**: {', '.join(v)}")
                    else:
                        lines.append(f"- **{k}**: {v}")
            elif isinstance(data, list):
                for item in data:
                    lines.append(f"- {item}")
            else:
                lines.append(f"- {data}")
            lines.append("")

        return "\n".join(lines)

    def save_report(self, path):
        """保存报告到文件"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_markdown())
        # 同时保存JSON版本
        json_path = path.replace('.md', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        return path


# ===== 快捷使用 =====
if __name__ == "__main__":
    # 测试
    sample = "这是测试文章。如果你想去杭州，绕不开两个地方。先Po商品，这个套餐太划算了。不约可退哦。"
    analyzer = StyleAnalyzer(sample, title="测试标题", account_name="测试号")
    report = analyzer.analyze_all()
    print(analyzer.to_markdown())
