#!/usr/bin/env python3
"""
小红书内容合规自动校验模块
用法: 
  from xiaohongshu_compliance import audit_and_fix, audit_report
  clean_text, violations = audit_and_fix(raw_body)
"""
REPLACEMENT_TABLE = [
    ("全网首发", "新鲜出炉"), ("全网第一", "口碑领先"),
    ("销量冠军", "很多人选择"), ("绝无仅有", "很少见"),
    ("独一无二", "很有特色"), ("不会错", "值得考虑"),
    ("闭眼入", "值得入手"), ("百分百", "基本上"),
    ("最好的", "很好的"), ("最便宜的", "性价比很高的"),
    ("最贵的", "品质很好的"), ("性价比之王", "性价比很高"),
    ("最好", "很好"), ("最美", "很美"), ("第一", "很不错"),
    ("首选", "值得看"), ("唯一", "少见"), ("顶级", "很出色"),
    ("最强", "很优秀"), ("极致", "很到位"), ("巅峰", "高水平"),
    ("绝对", "通常"), ("必入", "可以入"), ("必买", "可以考虑"),
    ("一定", "大概率"), ("立刻见效", "坚持会有变化"),
    ("马上变白", "长期会提亮"), ("三天见效", "坚持用会有改善"),
    ("一周变美", "长期会有变化"), ("一用就白", "坚持使用"),
    ("一抹就瘦", "配合坚持"), ("效果惊人", "效果不错"),
    ("效果显著", "效果可以"), ("根治", "改善"),
    ("永不复发", "很好缓解"), ("包治百病", "有辅助作用"),
    ("神效", "好效果"), ("奇迹", "惊喜"), ("神奇", "很棒"),
    ("秒杀", "很受欢迎"), ("全网最低", "很划算"),
    ("跳楼价", "超值优惠"), ("亏本卖", "优惠活动"),
    ("免费送", "福利赠送"), ("治疗", "改善"),
    ("疗程", "护理周期"), ("医生推荐", "很多人推荐"),
    ("医院同款", "专业护理"), ("消炎", "舒缓"),
    ("止痛", "缓解不适"), ("杀菌", "清洁"),
    ("减肥", "体重管理"), ("瘦身", "身材管理"),
    ("美白", "提亮肤色"), ("淡斑", "均匀肤色"),
    ("祛痘", "改善痘痘肌"), ("抗衰老", "初抗老"),
    ("抗皱", "淡化纹路"), ("排毒", "净化"),
    ("加微信", "关注我"), ("加V", "关注"),
    ("私信我", ""), ("私聊我", ""),
    ("戳我", ""), ("点我头像", ""),
    ("主页有", ""), ("懂的都懂", "你明白的"),
    ("下单", "入手"), ("付款", "安排"),
    ("正品保证", "品质有保障"), ("专柜品质", "做工很好"),
    ("代购", ""), ("拼单", ""), ("团购", ""),
    ("震惊", "真的很棒"), ("出大事了", "发现一个"),
    ("紧急通知", "提醒一下"), ("千万别错过", "可以看看"),
    ("微信", ""), ("VX", ""), ("wechat", ""),
    ("二维码", ""), ("手机号", ""), ("转账", ""),
    ("最火", "很受欢迎"), ("好评如潮", "反馈不错"),
    ("保证", "建议"), ("副作用", "注意事项"),
    ("美白针", ""), ("溶脂", ""),
]

def audit_and_fix(text):
    if not isinstance(text, str) or not text.strip():
        return text, []
    violations = []
    sorted_rules = sorted(REPLACEMENT_TABLE, key=lambda x: -len(x[0]))
    for forbidden, replacement in sorted_rules:
        if forbidden in text:
            if replacement:
                text = text.replace(forbidden, replacement)
                violations.append(f"{forbidden}")
            else:
                text = text.replace(forbidden, "")
                violations.append(f"{forbidden}")
    return text, violations

def audit_report(text):
    clean, violations = audit_and_fix(text)
    return {"clean": clean, "violations": violations, "count": len(violations)}

if __name__ == "__main__":
    test = "这款效果惊人，三天见效，全网最低价！加微信私聊我"
    r = audit_report(test)
    print(f"原文: {test}")
    print(f"合规: {r['clean']}")
    print(f"替换: {r['violations']}")
