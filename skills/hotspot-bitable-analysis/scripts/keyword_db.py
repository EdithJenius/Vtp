# -*- coding: utf-8 -*-
"""
酒店关键词库 · 本地检索分析模块

用法:
    from keyword_db import KeywordDB
    db = KeywordDB()
    
    # 查某酒店某个品类可用的关键词
    kw = db.lookup("三亚亚特兰蒂斯酒店", "干货/清单流")
    # → {"pexels": "Atlantis Sanya...", "xhs": "亚特兰蒂斯 隐藏攻略", ...}
    
    # 查某酒店还有哪些品类没用过
    free = db.find_free_angles("长沙君悦酒店")
    # → ["干货/清单流", "情绪种草流", ...]
    
    # 标记某个品类已用
    db.mark_used("三亚亚特兰蒂斯酒店", "干货/清单流", "笔记标题")
    
    # 查某酒店最缺的品类（还没写的）
    gaps = db.find_gaps(["三亚亚特兰蒂斯酒店"])
    # → [{"hotel": "三亚亚特兰蒂斯酒店", "unused": [...], "used": [...]}]
    
    # 构建链接文本
    links = db.build_links("三亚亚特兰蒂斯酒店", "干货/清单流")
    # → "https://www.pexels.com/...\\nhttps://..."
"""
import json, os, urllib.parse

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'references', 'keyword_db.json')
ALL_ANGLES = ["干货/清单流", "情绪种草流", "测评对比流", "行业分析流",
              "截流紧迫感流", "Vlog日程流", "反差点评流", "科普涨知识流",
              "真实UGC流", "问答攻略流"]

_SOURCE_ORDER = ["pexels", "unsplash", "xhs", "pinterest", "douyin"]
_SOURCE_LABELS = {
    "pexels": "Pexels", "unsplash": "Unsplash", "xhs": "小红书",
    "pinterest": "Pinterest", "douyin": "抖音"
}

class KeywordDB:
    def __init__(self, path=None):
        self.path = path or DB_PATH
        self._load()

    def _load(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def resolve_hotel(self, name_or_alias):
        """通过名称或别名找到标准酒店名"""
        hotels = self.data.get('hotels', {})
        if name_or_alias in hotels:
            return name_or_alias
        for hname, hdata in hotels.items():
            if name_or_alias in hdata.get('aliases', []):
                return hname
        return None

    def lookup(self, hotel_name, angle):
        """查某酒店某品类的完整关键词配置"""
        hkey = self.resolve_hotel(hotel_name)
        if not hkey:
            return None
        angles = self.data['hotels'][hkey].get('angles', {})
        info = angles.get(angle)
        if not info:
            return None
        return {
            "hotel": hkey,
            "angle": angle,
            "keywords": info['keywords'],
            "used": info.get('used', False),
            "last_note": info.get('last_note', ''),
        }

    def find_free_angles(self, hotel_name):
        """返回该酒店所有未使用的品类"""
        hkey = self.resolve_hotel(hotel_name)
        if not hkey:
            return []
        angles = self.data['hotels'][hkey].get('angles', {})
        return [a for a, info in angles.items() if not info.get('used', False)]

    def find_used_angles(self, hotel_name):
        """返回该酒店已使用的品类"""
        hkey = self.resolve_hotel(hotel_name)
        if not hkey:
            return []
        angles = self.data['hotels'][hkey].get('angles', {})
        return [(a, info['last_note']) for a, info in angles.items() if info.get('used', False)]

    def mark_used(self, hotel_name, angle, note_title=""):
        """标记某个品类已使用"""
        hkey = self.resolve_hotel(hotel_name)
        if not hkey:
            return False
        angles = self.data['hotels'][hkey].get('angles', {})
        if angle in angles:
            angles[angle]['used'] = True
            angles[angle]['last_note'] = note_title
            self._save()
            return True
        return False

    def mark_unused(self, hotel_name, angle):
        """取消标记（重写时用）"""
        hkey = self.resolve_hotel(hotel_name)
        if not hkey:
            return False
        angles = self.data['hotels'][hkey].get('angles', {})
        if angle in angles:
            angles[angle]['used'] = False
            angles[angle]['last_note'] = ""
            self._save()
            return True
        return False

    def find_gaps(self, hotel_names=None):
        """找所有酒店的品类缺口"""
        hotels = self.data.get('hotels', {})
        if hotel_names:
            hotels = {k: v for k, v in hotels.items()
                      if k in hotel_names or any(a in hotel_names for a in [k] + v.get('aliases', []))}

        gaps = []
        for hname, hdata in hotels.items():
            angles = hdata.get('angles', {})
            used = [(a, info.get('last_note','')) for a, info in angles.items() if info.get('used')]
            unused = [a for a, info in angles.items() if not info.get('used')]
            gaps.append({
                "hotel": hname,
                "total": len(angles),
                "used_count": len(used),
                "unused_count": len(unused),
                "used": used,
                "unused": unused,
            })
        return gaps

    def build_links(self, hotel_name, angle):
        """生成该酒店+品类的完整素材链接文本（5条）"""
        info = self.lookup(hotel_name, angle)
        if not info:
            return ""

        lines = []
        for src in _SOURCE_ORDER:
            kw = info['keywords'].get(src)
            if not kw:
                continue
            q = urllib.parse.quote(kw)
            label = _SOURCE_LABELS.get(src, src)

            if src == "pexels":
                url = f"https://www.pexels.com/zh-cn/search/{q}/"
            elif src == "unsplash":
                url = f"https://unsplash.com/s/photos/{q}"
            elif src == "xhs":
                url = f"https://www.xiaohongshu.com/search_result?keyword={q}&source=web_search_result_notes"
            elif src == "pinterest":
                url = f"https://www.pinterest.com/search/pins/?q={q}"
            elif src == "douyin":
                url = f"https://www.douyin.com/search/{q}"
            else:
                url = f"https://www.baidu.com/s?wd={q}"

            lines.append(f"{url}  # [{label}] {kw}")

        return "\n".join(lines)

    def suggest_angles(self, note_title, hotel_name):
        """根据笔记标题和酒店名推荐最合适的品类"""
        title_lower = note_title.lower()
        # 关键词匹配
        keyword_map = {
            "干货": "干货/清单流",
            "清单": "干货/清单流",
            "种草": "情绪种草流",
            "治愈": "情绪种草流",
            "测评": "测评对比流",
            "对比": "测评对比流",
            "vs": "测评对比流",
            "行业": "行业分析流",
            "财报": "行业分析流",
            "年收": "行业分析流",
            "抓紧": "截流紧迫感流",
            "涨价": "截流紧迫感流",
            "抢": "截流紧迫感流",
            "vlog": "Vlog日程流",
            "24h": "Vlog日程流",
            "一天": "Vlog日程流",
            "去之前": "反差点评流",
            "不值": "反差点评流",
            "后悔": "反差点评流",
            "为什么": "科普涨知识流",
            "科普": "科普涨知识流",
            "冷知识": "科普涨知识流",
            "真实": "真实UGC流",
            "素人": "真实UGC流",
            "实话": "真实UGC流",
            "问题": "问答攻略流",
            "避坑": "问答攻略流",
            "攻略": "问答攻略流",
        }
        for keyword, angle in keyword_map.items():
            if keyword in title_lower:
                return angle
        return None

    def list_hotels(self):
        """列出关键词库中所有酒店"""
        return list(self.data.get('hotels', {}).keys())


# ===== 快捷测试 =====
if __name__ == "__main__":
    db = KeywordDB()

    print("=== 酒店列表 ===")
    for h in db.list_hotels():
        print(f"  {h}")

    print("\n=== 三亚亚特兰蒂斯·干货品类关键词 ===")
    info = db.lookup("三亚亚特兰蒂斯酒店", "干货/清单流")
    if info:
        for k, v in info['keywords'].items():
            print(f"  {k}: {v}")

    print("\n=== 品类缺口分析 ===")
    gaps = db.find_gaps()
    for g in gaps:
        print(f"  {g['hotel']}: {g['used_count']}/10 已用, 剩余 {g['unused_count']} 个")

    print("\n=== 构建链接测试 ===")
    links = db.build_links("三亚亚特兰蒂斯酒店", "干货/清单流")
    print(links[:200])
