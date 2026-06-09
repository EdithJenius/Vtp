# -*- coding: utf-8 -*-
"""
公众号内容生成引擎（Content Generator）
输入：风格画像 + 选题/产品信息
输出：完整公众号文章
"""
import json, os, re

class ContentGenerator:
    def __init__(self, style_profile_path=None):
        self.profile = {}
        if style_profile_path:
            self.load_profile(style_profile_path)

    def load_profile(self, path):
        """加载风格画像（JSON或MD）"""
        if path.endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                self.profile = json.load(f)
        else:
            # 从Markdown提取关键信息（简化版）
            self.profile_path = path

    def generate(self, topic, product_info=None):
        """按加载的风格生成正文"""
        if not self.profile:
            return "请先加载风格画像"

        profile = self.profile
        # 关键风格参数
        use_persona = profile.get("语气调性", {}).get("人称偏好", "第一人称")
        tone = profile.get("语气调性", {}).get("正式度", "口语化")
        opening_type = profile.get("开头策略", {}).get("开头类型", "场景代入型")
        conversion = profile.get("转化手法", [])

        # 构建正文
        paras = []

        # 1. 开头（按风格类型）
        if "场景代入" in opening_type:
            paras.append(f"如果你想去{topic}，绕不开XXX这个地方。但如果你想安静的度假，我会选择...")
        elif "开门见山" in opening_type:
            paras.append(f"先Po商品\n{topic}套餐详情...")

        # 2. 正文拆解（按风格分段）
        paras.append(f"\n接下来，详细聊聊{topic}。")

        # 3. 转化
        if "淘口令" in str(conversion):
            paras.append(f"\n购买淘口令：...\n套餐不约可退、过期自动退，大家可以放心囤货。")

        # 4. 结尾
        paras.append(f"\n如果你喜欢旅行，别忘记关注+置顶公众号哦！")

        return "\n\n".join(paras)

    def generate_title(self, topic, count=5):
        """按风格的标题模式生成候选标题"""
        titles = []
        templates = [
            f"去{topic}之前，这3个坑我先替你踩了",
            f"住过5次{topic}，告诉你这2个隐藏服务",
            f"{topic} vs XXX，同价位我选前者",
            f"如果你只有2天假期，我建议你来{topic}",
            f"去之前觉得贵，退房时发现赚了",
        ]
        for i in range(min(count, len(templates))):
            titles.append(templates[i])
        return titles


# ===== 嬉游专属生成器 =====
class XiYouGenerator(ContentGenerator):
    """嬉游风格专用生成器，按嬉游行文公式生成"""

    def generate(self, hotel_name, location, price_info, highlights, buy_link, extra_info=""):
        """
        hotel_name: 酒店全称
        location: 位置/城市
        price_info: dict {套餐名: {价格, 包含内容, 有效期, 补差政策}}
        highlights: list of (标题, 内容)
        buy_link: 购买链接/口令
        extra_info: 额外信息
        """
        paras = []

        # === 1. 场景开头 ===
        paras.append(f"去{location}，绕不开两个地方，XXX和XXX。"
                     f"但如果你想安静的度假，我会选择{hotel_name}。"
                     f"这家酒店正门对着XXX，被XXX包围，藏在{location}最禅意的那片山水里。"
                     f"\n熟悉{location}酒店圈的应该都知道，这家酒店火了多年。"
                     f"位置好、设计好、餐饮也棒，而这次，性价比也挺高的。")

        # === 2. 先Po商品 ===
        for name, info in price_info.items():
            p_para = (f"先Po商品\n"
                      f"{hotel_name}{name}，{info.get('包含', '')}，{info.get('价格', '')}元"
                      f"\n有效期至{info.get('有效期', '')}，{info.get('补差', '节假日不加价')}"
                      f"\n\n购买淘口令：{buy_link}"
                      f"\n套餐不约可退、过期自动退、不核销可随时退，大家可以放心囤货。"
                      f"\n和日历比，差价真的很大哦。")
            paras.append(p_para)

        # === 3. 背景/背书 ===
        paras.append(f"接下来，详细聊聊{hotel_name}。"
                     f"\n先把基本情况交代清楚。"
                     f"\n全名叫{hotel_name}，XXX年开业，到现在已经是第X个年头了。"
                     f"\n设计师请的是XXX，XXX御用设计师。")

        # === 4. 产品细节拆解 ===
        for title, content in highlights:
            paras.append(f"\n{title}\n{content}")

        # === 5. 价格/购买再次强调 ===
        paras.append(f"\n节假日、暑期、周末都不加价哦。")

        # === 6. 结尾 ===
        paras.append(f"\n如果你喜欢旅行，别忘记关注+置顶公众号哦！"
                     f"\n我是急速菜菜，嬉游公众号主理人，旅行博主。"
                     f"\n善于把旅行和航空、酒店、信用卡结合在一起。"
                     f"\n让你更聪明地去旅行！")

        return "\n\n".join(paras)
