"""
热点商机多维分析 - Feishu Bitable 批量插入脚本模板

⚠️ 关键规则：
1. 使用选项名称（中文），不是 optID — 否则会创建乱码选项
2. MultiSelect（来源渠道）传字符串数组
3. SingleSelect（话题类别/优先级）传字符串
4. 每批最多 10 条

使用方法：
1. 获取新的 tenant_access_token
2. 创建 Bitable 并获取 app_token 和 table_id
3. 修改下方 TOKEN, APP_TOKEN, TABLE_ID
4. 填写 records 数组
5. 运行：python3 insert_records.py
"""

import json
import urllib.request
import urllib.error
import sys
import time

# ===== 配置区（每次使用时修改）=====
TOKEN = ""           # tenant_access_token
APP_TOKEN = ""       # 新 Bitable 的 app_token
TABLE_ID = ""        # 默认表的 table_id
# ================================

# ===== 数据 =====
# ✅ 选项值使用中文名称，不是 optID！
# ✅ 来源渠道传字符串数组（多选）
# ✅ 优先级/话题类别传字符串（单选）
records = [
    {
        "热点话题": "热点标题",
        "来源渠道": ["微博热搜", "百度热搜"],   # 多选，传数组
        "话题类别": "社会民生",                  # 单选，传字符串
        "热度指数": "微博 #1 / 116万",
        "热度指数数值": 1160000,                # 数字
        "关联地点": "关联城市",
        "关联旅游景点": "相关景区",
        "旅游商机分析": "商机分析内容",
        "优先级": "高",                          # 单选，传字符串
        "备注": "补充信息"
    },
    # 更多记录...
]

# ===== 来源渠道可用选项 =====
# 微博热搜、百度热搜、知乎热榜、抖音、小红书、B站、综合

# ===== 话题类别可用选项 =====
# 航天科技、社会民生、天气灾害、财经股市、国际外交
# 科技AI、体育赛事、文旅美食、健康生活、教育

# ===== 优先级可用选项 =====
# 高、中、低
# ===============================

# 先删除旧记录（如果存在）
def delete_all_records():
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=50"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        items = data.get("data", {}).get("items", [])
        for item in items:
            rid = item["record_id"]
            del_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{rid}"
            req = urllib.request.Request(del_url, method="DELETE")
            req.add_header("Authorization", f"Bearer {TOKEN}")
            urllib.request.urlopen(req)
        print(f"Deleted {len(items)} old records")
    except Exception as e:
        print(f"Delete skipped: {e}")

def send_batch(batch_records):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create"
    payload = json.dumps({"records": [{"fields": r} for r in batch_records]}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        if result.get("code") == 0:
            return len(result.get("data", {}).get("records", [])), None
        else:
            return 0, result.get("msg")
    except urllib.error.HTTPError as e:
        return 0, f"HTTP {e.code}: {e.read().decode()[:300]}"

# 主流程
delete_all_records()

inserted = 0
for i in range(0, len(records), 10):
    batch = records[i:i+10]
    n, err = send_batch(batch)
    if err:
        print(f"Batch {i//10+1}: Error - {err}")
        sys.exit(1)
    else:
        print(f"Batch {i//10+1}: Created {n} records")
    inserted += n
    time.sleep(0.5)

print(f"\nDone! {inserted}/{len(records)} records inserted.")
