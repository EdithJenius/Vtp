---
name: hotspot-bitable-analysis
description: "全网热点调研 → 旅游商机分析 → Feishu Bitable 自动创建与填充"
---

# 热点商机多维分析 Skill

每日自动：爬取多平台热搜 → 交叉验证 → 旅游商机分析 → 创建/刷新 Bitable。

## 触发词

- "整理热点" / "热点分析" / "今日热点"
- "另起一个多维表格"
- "做一遍热点调研"

## 前提

需要安装 OpenCLI 并连接 Chrome 扩展（见 `references/OpenCLI使用手册.md`）。

## ⚠️ 核心原则（血的教训）

### 原则1：永远使用选项名称，不是 optID

**插入 SingleSelect / MultiSelect 字段值时：**
- ✅ 使用选项**名称（中文）**，如 `"微博热搜"`、`"高"`、`"社会民生"`
- ❌ 不要使用选项 ID（如 `"opt6mByzqo"`），API 会将其当作新选项名称创建乱码选项

```python
# ✅ 正确
"来源渠道": ["微博热搜", "百度热搜"]   # MultiSelect 传数组
"优先级": "高"                          # SingleSelect 传字符串

# ❌ 错误
"来源渠道": ["opt6mByzqo", "optTzXkli7"]
"优先级": "optcTwW4fI"
```

### 原则2：备注中的链接必须URL编码

Weibo 分享链接中的中文话题名必须用 `urllib.parse.quote()` 编码：

```python
import urllib.parse

# ✅ 正确：topic 用 %23 包裹，中文用 quote 编码
url = 'https://s.weibo.com/weibo?q=' + urllib.parse.quote('#雷军回应武契奇说小米车漂亮但买不起#')

# ❌ 错误：直接拼接中文字符
url = 'https://s.weibo.com/weibo?q=%23雷军回应武契奇说小米车漂亮但买不起%23'  # 跳转不了！
```

**其他平台链接格式参考：**
| 平台 | 链接格式 |
|------|----------|
| 微博 | `https://s.weibo.com/weibo?q=` + `urllib.parse.quote('#话题名#')` |
| 百度 | `https://www.baidu.com/s?wd=` + `urllib.parse.quote('搜索词')` |
| 头条 | 直接从 opencli 输出的 url 字段获取 |
| 知乎 | 直接从 opencli 输出的 url 字段获取 |
| 抖音 | 官方无固定链接，标注「抖音热点词: xxx」即可 |
| B站 | 直接从 opencli 输出的 url 字段获取 |
| 36氪 | 直接从 opencli 输出的 url 字段获取 |
| 贴吧 | 直接从 opencli 输出的 url 字段获取 |

### 原则3：全部用Python，不要用Bash

❌ 不要用 Bash 写数据处理/API调用脚本，原因：
- `declare -A` 在 zsh 中不兼容（shell = /bin/zsh）
- 多行 heredoc 中的 `$TOKEN` 变量容易产生空值或错误代换
- 字符串处理和 JSON 解析在 Bash 中极其脆弱

✅ 统一用纯 Python 脚本，token 在 Python 内部获取：
```python
import urllib.request, json

# 在 Python 内部获取 token，不依赖 shell 变量
r = urllib.request.urlopen(urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=b'{"app_id":"cli_aa870c0ca5e15cd6","app_secret":"jfof8OwjPLORVhWrc5d08bEQzegcdGUE"}',
    headers={'Content-Type': 'application/json'}
))
TOKEN = json.loads(r.read())['tenant_access_token']
```

### 原则4：每次批量操作后验证

batch_create / batch_delete 返回 code=0 不代表数据真的写入了。
**必须再用 GET 查询验证**，尤其是 token 快过期时可能返回假成功：

```python
# 验证记录数
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/records?page_size=20',
    headers={'Authorization': f'Bearer {TOKEN}'}
)
items = json.loads(urllib.request.urlopen(req).read()).get('data',{}).get('items') or []
print(f'实际记录数: {len(items)}条')
for r in items:
    print(f'  - {r.get("fields",{}).get("热点话题","")[:30]}')
```

### 原则5：出现错误重试时，注意去重

脚本中途失败会留下部分已写入的数据。重跑前必须先清理，否则重复。

```python
# 重试策略：每次重跑前，先删除该表所有记录再重新插入
def delete_all_records(table_id):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{table_id}/records?page_size=50',
        headers={'Authorization': f'Bearer {TOKEN}'}
    )
    items = json.loads(urllib.request.urlopen(req).read()).get('data',{}).get('items') or []
    for r in items:
        rid = r['record_id']
        del_req = urllib.request.Request(f'.../{rid}', method='DELETE', headers=...)
        urllib.request.urlopen(del_req)
```

### 原则6：在脚本第一行获取新token

不要复用旧 token（即使还"没过期"）。每段脚本开始时重新获取：
```python
# 第一件事：获取token
TOKEN = get_tenant_token()  # 内部调用 auth/v3/tenant_access_token
```
用 `~/.openclaw/config.toml` 读取 appSecret：
```python
import configparser, os
config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId']
APP_SECRET = config['provider.feishu']['appSecret']
```

### ⚠️ 数据类型

| 字段名 | API 类型 | 插入值格式 |
|--------|---------|-----------|
| 热点话题 | 文本 (type=1) | 字符串 |
| 来源渠道 | 多选 (type=4) | `["选项名1", "选项名2"]` |
| 话题类别 | 单选 (type=3) | `"选项名"` |
| 热度指数 | 文本 (type=1) | 字符串 |
| 热度指数数值 | 数字 (type=2) | 整数 |
| 关联地点 | 文本 (type=1) | 字符串 |
| 关联旅游景点 | 文本 (type=1) | 字符串 |
| 旅游商机分析 | 文本 (type=1) | 字符串 |
| 优先级 | 单选 (type=3) | `"高"` / `"中"` / `"低"` |
| 备注 | 文本 (type=1) | 补充说明 + 原文链接（📎格式）|

## 工作流

### Step 1: 抓取热点数据（多平台全覆盖）

数据源，按可用性排序：

#### 1A. OpenCLI（首选，结构化）

```bash
# ═══ 国内热点平台 ═══

# 微博热搜
opencli weibo hot --limit 30 -f json

# 今日头条热榜 ✅ 已验证稳定
opencli toutiao hot -f json --limit 20

# 抖音热搜（热点词）✅ 已验证稳定
opencli douyin hashtag hot --limit 30 -f json

# 知乎热榜
opencli zhihu hot --limit 20 -f json

# 贴吧热榜 ✅ 已验证稳定
opencli tieba hot --limit 20 -f json

# 36氪热榜 ✅ 已验证稳定
opencli 36kr hot -f json --limit 20

# B站热门
opencli bilibili hot --limit 20 -f json

# 小红书 — 旅游相关搜索（推荐用 xhs 工具）
xhs search "旅游" --sort popular --json
# 备选: opencli xiaohongshu search "旅游" --limit 10 -f json

# ═══ 国际热点平台 ═══

# Twitter/X — 全球趋势（需在Chrome中登录 x.com）
opencli twitter trending -f json --limit 15
```

#### 1B. 网页/API 抓取（OpenCLI 不可用时）

```bash
# 百度热搜 — web_fetch 稳定可用
# 微博热搜 — OpenCLI 优先
# Tophub 聚合 — 易触发 Cloudflare验证(403)，间隔使用
```

| 平台 | 推荐获取方式 | 稳定度 |
|------|-------------|--------|
| 微博热搜 | `opencli weibo hot` | ✅ 已验证 |
| 百度热搜 | `web_fetch https://top.baidu.com/board?tab=realtime` | ✅ 稳定 |
| **今日头条** | `opencli toutiao hot` | ✅ 已验证 |
| **抖音** | `opencli douyin hashtag hot` | ✅ 已验证 |
| 知乎热榜 | `opencli zhihu hot` / Tophub | ✅ 已验证 |
| **贴吧** | `opencli tieba hot` | ✅ 已验证 |
| **36氪** | `opencli 36kr hot` | ✅ 已验证 |
| **Twitter/X** | `opencli twitter trending`（需登录）| ✅ 已验证 |
| B站 | `opencli bilibili hot` | ✅ 已验证 |
| 小红书 | `opencli xiaohongshu search` | ✅ 已验证 |

**提取要点：** 话题标题、热度指数/数值、来源平台、简要描述、附原文链接（📎格式）

### Step 2: 交叉验证（跨平台合并）

同一条热点出现在多个平台时，**合并为一条记录**，来源渠道标记所有出现平台。

原理：
```
微博热搜 → "盒马郑重道歉" (116万)
百度热搜 → "盒马粉木耳包装惹争议" (752万)
   ↓ 交叉验证
合并为一条：盒马粉木耳包装引争议后郑重道歉
来源渠道：["微博热搜", "百度热搜"]
热度指数：微博 #1/116万 + 百度 #4/752万
```

### Step 3: 旅游商机分析

每条热点按以下维度分析：

| 维度 | 说明 |
|------|------|
| 关联地点 | 事件发生的城市/区域 |
| 关联旅游景点 | 可借势推广的景区/目的地 |
| 旅游商机分析 | 具体产品/活动建议，用 ⭐ 标记高价值 |
| 优先级 | 高(热点+旅游强关联) / 中(可关注) / 低(仅信息参考) |

### Step 4: 创建 Bitable

**API 端点：** `https://open.feishu.cn/open-apis/bitable/v1/apps`

```mermaid
flowchart LR
  A[获取 Tenant Token] --> B[创建 Bitable]
  B --> C[创建字段 + 配置选项]
  C --> D[删除默认空记录]
  D --> E[批量插入记录]
  E --> F[验证记录数]
  F --> G[设置公开权限]
  G --> H[添加用户权限]
```

#### 4.1 获取 Token

```python
# ⚠️ 重要：每次获取 token，不要复用上次的过期 token
import urllib.request, json, configparser, os

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId']
APP_SECRET = config['provider.feishu']['appSecret']

r = urllib.request.urlopen(urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={'Content-Type': 'application/json'}
))
TOKEN = json.loads(r.read())['tenant_access_token']
print(f'Token: {TOKEN[:20]}...')
```

#### 4.2 创建 Bitable

```bash
curl -s -X POST 'https://open.feishu.cn/open-apis/bitable/v1/apps' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"热点商机多维分析 YYYY-MM-DD"}'
```

返回：`app_token`（Bitable ID）和 `default_table_id`

#### 4.3 字段结构（最终版）

创建顺序建议：
1. 重命名默认主字段为「热点话题」
2. 删除默认的其他字段（单选、日期、附件）
3. 逐个创建自定义字段

```python
# 字段创建 API 调用
字段「来源渠道」→ type=4（多选）, options=[微博热搜,百度热搜,知乎热榜,抖音,小红书,B站,综合,今日头条,贴吧,36氪]
字段「话题类别」→ type=3（单选）, options=[航天科技,社会民生,天气灾害,财经股市,国际外交,科技AI,体育赛事,文旅美食,健康生活,教育]
字段「热度指数」→ type=1（文本）
字段「热度指数数值」→ type=2（数字）
字段「关联地点」→ type=1（文本）
字段「关联旅游景点」→ type=1（文本）
字段「旅游商机分析」→ type=1（文本, 长文本）
字段「优先级」→ type=3（单选）, options=[高,中,低]
字段「备注」→ type=1（文本）
```

创建字段 API：
```bash
# 重命名主字段（需要传 type）
curl -s -X PUT "$BASE/fldXXX" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"field_name":"热点话题","type":1}'

# 删除默认字段
curl -s -X DELETE "$BASE/fldYYY" -H "Authorization: Bearer $TOKEN"

# 创建文本字段
curl -s -X POST "$BASE" -H "Authorization: Bearer $TOKEN" \
  -d '{"field_name":"热度指数","type":1}'

# 创建数字字段
curl -s -X POST "$BASE" -H "Authorization: Bearer $TOKEN" \
  -d '{"field_name":"热度指数数值","type":2}'

# 创建单选字段（type=3）
curl -s -X POST "$BASE" -H "Authorization: Bearer $TOKEN" \
  -d '{"field_name":"优先级","type":3,"property":{"options":[
    {"name":"高","color":0},{"name":"中","color":1},{"name":"低","color":2}
  ]}}'

# 创建多选字段（type=4，重要！）
curl -s -X POST "$BASE" -H "Authorization: Bearer $TOKEN" \
  -d '{"field_name":"来源渠道","type":4,"property":{"options":[
    {"name":"微博热搜","color":0},{"name":"百度热搜","color":1},
    {"name":"知乎热榜","color":2},{"name":"抖音","color":3},
    {"name":"小红书","color":4},{"name":"B站","color":5},
    {"name":"综合","color":6},{"name":"今日头条","color":7},
    {"name":"贴吧","color":8},{"name":"36氪","color":9}
  ]}}'
```

#### 4.4 删除默认空记录

新建 Bitable 默认自带 10 条空记录，需要删除：

```python
# 逐一删除（batch_delete 易出错，建议单条删除）
for rid in empty_record_ids:
    curl -s -X DELETE "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP/tables/$TABLE/records/$rid" \
      -H "Authorization: Bearer $TOKEN"
```

#### 4.5 验证记录是否写入（关键！）

```python
# 每次插入后，立即 GET 读取验证
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TABLE}/records?page_size=20',
    headers={'Authorization': f'Bearer {TOKEN}'}
)
items = json.loads(urllib.request.urlopen(req).read()).get('data',{}).get('items') or []
print(f'实际写入 {len(items)} 条')
for r in items:
    topic = r.get('fields',{}).get('热点话题','')[:30]
    print(f'  - {topic}')
```

> 如果返回 0 条，请检查 token 是否有效（重新获取 token 再试）。
> 已验证：token 过期时 API 仍可能返回 code=0 但不写入数据。
> 所以必须**用 GET 读取验证**，不能只看 code。

### Step 5: 批量插入记录

**⚠️ 关键：使用选项名称（中文）而不是选项 ID**

```python
# MultiSelect 字段：传字符串数组
"来源渠道": ["微博热搜", "百度热搜"]

# SingleSelect 字段：传字符串
"话题类别": "社会民生"
"优先级": "高"

# Text 字段：传字符串
"热点话题": "盒马粉木耳包装引争议后郑重道歉"

# Number 字段：传数字
"热度指数数值": 1160000
```

**API 调用：**

```bash
POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create
Body: {
  "records": [
    {"fields": {"热点话题": "...", "来源渠道": ["微博热搜"], ...}},
    ...
  ]
}
```

限制：每批最多 10 条。

### Step 6: 设置权限

永乐要求：**所有 Bitable 设为公开可编辑**。

```bash
# 公开可编辑
curl -s -X PATCH "https://open.feishu.cn/open-apis/drive/v1/permissions/$APP_TOKEN/public?type=bitable" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "external_access_entity": "open",
    "security_entity": "anyone_can_edit",
    "comment_entity": "anyone_can_edit",
    "copy_entity": "anyone_can_edit",
    "link_share_entity": "anyone_readable",
    "invite_external": true,
    "link_share": true
  }'

# 添加管理员权限
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/permissions/$APP_TOKEN/members?type=bitable&need_notification=false" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"member_type":"openid","member_id":"ou_b098a77a8b7869d14ccd6e34b7af3583","perm":"full_access"}'
```

——

### Step 7: 创建热点深度分析子表

对主表中**高/中优先级**的热点话题，按涉及地区创建独立的子表（sheet）进行深度分析。

#### 7.1 确定需要深挖的热点

筛选条件：
- 优先级为「高」或「中」
- 有明确关联地点（城市/区域/国家）
- 有旅游商业转化价值

#### 7.2 创建子表

```python
# 创建子表 API（需至少1个字段）
POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables
Body: {
  "table": {
    "name": "地区名·热点关键词概括",
    "fields": [{"field_name": "名称", "type": 1}]
  }
}
```

#### 7.3 子表字段结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 名称 | Text | 主字段，酒店/景点/美食/活动名称 |
| 类别 | Select | 酒店/景点/美食/活动/行程推荐/交通 |
| 推荐理由 | Text | 为什么推荐 + 与热点的关联 |
| 参考价格 | Text | 价格区间 |
| 关联热度 | Text | 对应的热点话题 |
| 详情/链接 | Text | 补充信息 |
| 备注 | Text | 标注已入库/待拓展 |

类别选项：
```json
[
  {"name":"酒店","color":0}, {"name":"景点","color":1},
  {"name":"美食","color":2}, {"name":"活动","color":3},
  {"name":"行程推荐","color":4}, {"name":"交通","color":5}
]
```

#### 7.4 子表数据填充策略

每个子表包含：
- **4-6家五星酒店**（优先从酒店资源表匹配，见 Step 8）
- **3-5个景点**（当地核心地标）
- **2-3种美食**（在地特色）
- **1-2个活动**（文化体验）
- **1条行程推荐**（组合产品方案）

#### 7.5 子表去重注意事项

子表数据通过 `batch_create` 写入，脚本重跑时会重复写入。
**每次重跑前必须删除子表全部已有记录：**

```python
# 删除子表全部记录（避重）
def clear_table(table_id):
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{table_id}/records?page_size=50'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
    items = json.loads(urllib.request.urlopen(req).read()).get('data',{}).get('items') or []
    for r in items:
        rid = r['record_id']
        del_req = urllib.request.Request(f'.../{rid}', method='DELETE', headers=...)
        urllib.request.urlopen(del_req)
```

---

### Step 8: 酒店资源匹配（对接资源表）

现有酒店资源表位于飞书在线表格：
`https://scn07fc4ixwd.feishu.cn/sheets/PEK7srUqBhbfE7tVW4scdhNwnah?sheet=f4ba18`

#### 8.1 读取资源表

```python
# 使用飞书 Sheets API 读取
SPREADSHEET_TOKEN = "***"
SHEET_ID = "f4ba18"  # sheet 名「酒店（用于朋友圈）」

GET https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{token}/values/{sheet_id}!A3:H237
```

列结构：A=序号, B=产出人, C=入表日期, D=酒店名称, E=配图, F=朋友圈文案, G=详细礼遇, H=备注

#### 8.2 匹配逻辑

```
酒店名称 → 检查是否包含子表地区关键字 → 若匹配则采用资源表中的真实价格和礼遇
                                 → 若不匹配则执行 Step 9 补充通用推荐
```

#### 8.3 替换规则

- ✅ **资源表中有的酒店** → 替换为真实合作价格/礼遇，标注「已入库」
- ⚠️ **资源表中没有的酒店** → 保持通用推荐，标注「⚠️待拓展」

---

### Step 9: 五星酒店补充（资源表缺失时）

当资源表中某地区无合作酒店时，补充**至少5家当地真实五星酒店**作为推荐。

#### 9.1 收集渠道

- 国际连锁五星（万豪/希尔顿/凯悦/洲际/雅高等）
- 国内高端品牌
- 当地地标性豪华酒店

#### 9.2 数据格式

每条酒店记录包含：
- 名称（品牌+城市名）
- 推荐理由（卖点：位置/设计/服务/景观）
- 参考价格（区间）
- 备注（集团品牌/适合客群）

#### 9.3 示例（天津）

| 酒店 | 理由 | 价格 |
|------|------|------|
| 天津丽思卡尔顿 | 顶奢No.1·英式城堡·海河景观 | 1500-3000/晚 |
| 天津四季酒店 | 核心区·五大道旁 | 1200-2500/晚 |
| 天津康莱德 | 希尔顿顶奢·新开业 | 1000-2000/晚 |
| 天津海河悦榕庄 | 河景SPA度假 | 1300-2500/晚 |
| 天津香格里拉 | 海河第一排 | 800-1800/晚 |

---

### Step 10: 地区文旅符号调研

创建独立的「地区文旅符号调研」子表，对所有涉及地区进行**8维度深度分析**。

#### 10.1 创建子表

```python
POST /open-apis/bitable/v1/apps/{app_token}/tables
Body: {"table": {"name": "地区文旅符号调研", "fields": [...]}}
```

#### 10.2 字段结构

| 字段名 | 类型 | 内容说明 |
|--------|------|----------|
| 地区名称 | Text(主) | 城市/区域/国家名称 |
| 关联热点 | Text | 对应的热点话题及热度 |
| 基础信息 | Text(长) | 地理位置·气候·交通·人口·文化背景 |
| 金字招牌 | Text(长) | 最知名的旅游名片·标志性景点·美食·文化符号 |
| 市井风情 | Text(长) | 当地烟火气·生活方式·方言·民间习俗·日常节奏 |
| 视觉资产 | Text(长) | 标志性色彩·建筑风格·自然景观·摄影标签 |
| 季节限定 | Text(长) | 最佳旅行季节·时令特色·节庆活动·天气提示 |
| 避坑槽点 | Text(长) | 常见雷区·消费陷阱·交通不便·安全提醒 |
| 商业闭环 | Text(长) | 可落地的旅游产品思路·酒店+景点+美食+活动组合方案 |

#### 10.3 八大维度分析要点

```
1️⃣ 基础信息   → 快速定位：在哪？怎么去？什么气候？
2️⃣ 金字招牌   → 非去不可的理由：什么最出名？
3️⃣ 市井风情   → 本地人怎么生活：烟火气、接地气的体验
4️⃣ 视觉资产   → 出片点：色彩、建筑、自然景观的视觉符号
5️⃣ 季节限定   → 什么时间去最好：节庆、花期、渔汛、天气
6️⃣ 避坑槽点   → 别踩什么雷：宰客、人多、路况、高反
7️⃣ 商业闭环   → 怎么赚钱：产品组合、套餐设计、转化路径
```

#### 10.4 调研地区列表

覆盖所有主表中涉及的地点：
- 高优先级热点地点（必做）
- 新增酒店产品所在城市（必做）
- 跨平台交叉验证中出现的地点（酌情）

---

### Step 11: 小红书笔记素材分析

针对子表中的酒店/景点，搜集小红书笔记数据，建立素材库供内容创作使用。

#### 11.1 创建笔记分析子表

```python
POST /open-apis/bitable/v1/apps/{app_token}/tables
Body: {"table": {"name": "笔记分析-地区名", "fields": [...]}}
```

#### 11.2 字段结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 笔记标题 | Text(主) | 笔记标题 |
| 笔记链接 | Text | `https://www.xiaohongshu.com/explore/{note_id}?xsec_token=...` 带 xsec_token 的链接，否则会跳首页 |
| 发布日期 | Text | note_card.time 毫秒时间戳转为 YYYY-MM-DD |
| 点赞评论收藏 | Text | 互动数据汇总，如 `👍1167 💬23 ⭐89` |
| 笔记完整文案 | Text(长) | 完整正文内容 |
| 话题 | Text | `#话题1 #话题2` 格式 |
| 封面图片 | Text | 封面图URL（image_list[0].info_list WB_DFT） |
| 笔记类型 | Select | 图文/视频，通过 note_card.video 是否存在判断 |
| 账号类型 | Select | 干货攻略 / 客户成交案例 / 避坑指南 / KOS人设 |
| 关联酒店/景点 | Text | 对应子表中的资源名称 |
| 备注 | Text | 作者主页链接：`https://www.xiaohongshu.com/user/profile/{user_id}` |

#### 11.3 安装与前置准备

```bash
# 安装 xhs 工具（推荐，走反向工程API，更稳定）
# 需要 Python >= 3.10，uv 会自动下载
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv tool install xiaohongshu-cli

# 登录（从浏览器提取cookie）
xhs login --cookie-source chrome
# 验证登录状态
xhs status
```

#### 11.4 搜索与采集流程

```bash
# 1. 小红书关键词搜索（按热度排序）
xhs search "四姑娘山 攻略" --sort popular --json

# 2. 通过短索引读取笔记详情（搜索后自动缓存结果列表）
xhs read 1 --json       # 读取第1条
xhs read 2 --json       # 读取第2条

# 3. 直接通过 note_id 读取
xhs read <note_id> --json

# 4. 构建完整分享链接
# https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_search
# ⚠️ 必须带 xsec_token，否则链接打开后几秒会跳转到首页
```

**返回数据字段：**
| 字段 | 路径 | 说明 |
|------|------|------|
| 标题 | `note_card.title` | 笔记标题 |
| 文案 | `note_card.desc` | 完整正文（含话题标签） |
| 话题 | `note_card.tag_list[].name` | 标签数组 |
| 点赞 | `note_card.interact_info.liked_count` | 点赞数 |
| 收藏 | `note_card.interact_info.collected_count` | 收藏数 |
| 评论 | `note_card.interact_info.comment_count` | 评论数 |
| 作者 | `user.nickname` | 作者昵称 |
| 发布时间 | note_card.time | 毫秒时间戳 → datetime.fromtimestamp(ts/1000).strftime("%Y-%m-%d") |

**搜索关键词建议：**
- 酒店/景点名称 + 攻略/评测/避坑/体验
- 区域名称 + 旅游路线/行程/推荐
- 竞品关键词（同类酒店/景点对比）

#### 11.5 账号类型判定规则

| 类型 | 判定条件 |
|------|----------|
| 干货攻略 | 攻略/路线/推荐类内容，信息量大 |
| 客户成交案例 | 住客真实体验/预订分享，含价格/服务细节 |
| 避坑指南 | 标题含"避坑""避雷""不要""后悔"等 |
| KOS人设 | 博主个人IP突出，有固定风格/粉丝群 |

#### 11.6 数据录入

```python
# 批量写入笔记分析子表
POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create
Body: {
  "records": [
    {"fields": {
      "笔记标题": "...",
      "笔记链接": "https://www.xiaohongshu.com/explore/{id}?xsec_token={token}&xsec_source=pc_search",
      "点赞评论收藏": "👍1167 💬23 ⭐89",
      "账号类型": "干货攻略",
      "笔记类型": "图文",
      "关联酒店/景点": "四姑娘山"
    }}
  ]
}
```

---

## 完整流程速查

```
1.  获取 Token → Python 内部调用 auth/v3/tenant_access_token/internal
2.  创建 Bitable → POST bitable/v1/apps → 得到 app_token + table_id
3.  配置主表字段 → 重命名/删除默认/创建字段 + 选项
4.  删除主表默认空记录 → 逐个 DELETE records/{id}
5.  批量插入热点数据 → batch_create（用中文选项名）
6.  验证写入 → GET records 检查数量
7.  设置权限 → 公开可编辑 + 添加用户
8.  创建深度分析子表 → 筛选高/中优先级热点
9.  酒店资源匹配 → 从飞书资源表读取并匹配
10. 五星酒店补充 → 无合作酒店地区补充5-8家
11. 文旅符号调研子表 → 8维度分析每个地区
12. 输出链接给永乐
```

## 历史错误记录（每题必看）

### 🐛 2026-05-27 已踩坑点

1. **备注链接无法跳转**
   - 原因：Weibo 链接中直接拼接了未编码的中文
   - 修复：`urllib.parse.quote('#话题名#')` 编码中文

2. **子表内容重复两倍**
   - 原因：脚本因超时被 SIGTERM 后，第二次执行时第一次的部分数据已写入
   - 修复：重跑前 delete_all_records() 清空目标子表

3. **batch_create 返回 code=0 但数据没写进去**
   - 原因：token 已过期（但还在 2h 窗口内），API 返回假成功
   - 修复：脚本第一行先获取新 token，batch_create 后 GET 验证

4. **Bash 脚本中 config.toml 的 appSecret 被...截断**
   - 原因：`grep` 输出中 token 因...显示截断，实际值不完整
   - 修复：用 Python 读取 config，手动 split('"') 解析行内容

5. **declare -A 在 zsh 中报 bad substitution**
   - 原因：shell 是 zsh，不支持 bash 的关联数组语法
   - 修复：全部改用 Python dict

6. **酒店名称错字：石头记 → 石头纪**
   - 原因：酒店正确名称是「腾冲石头纪」，误写为「石头记」
   - 修复：统一替换字段选项+所有记录内容+子表名；注意核对酒店官方名称

7. **正文含具体金额被要求删除**
   - 原因：笔记文案中写了具体房价/人均消费数字
   - 修复：统一改为「打折优惠」「限时优惠」「有活动」等模糊表述，突出优惠概念不写具体价

8. **字段类型 Text→Select 后数据自动保留**
   - 经验：Text 转 SingleSelect 时，若已有文本值与选项名一致，API 会自动映射，无需手动更新记录

## 注意事项

### Token 管理
- 有效期约 2 小时（expire≈6000-7000秒）
- 同一 token 在有效期内重复请求返回相同值
- token 过期后 API 返回 `code: 99991668`，需重新获取
- 在 Python 脚本中用 `configparser` 从 `~/.openclaw/config.toml` 自动读取 secret

### 插入数据注意事项
- **永远使用中文选项名**（不是 optID）
- Python 脚本中中文引号（双引号" "）会与字符串定界符冲突 → 使用英文双引号或转义
- 字符串中避免直接包含中文双引号，用单引号或转义替代
- 每条记录必须在备注中附原文链接（📎 来源+URL），便于跳转查看
- `records/batch_create` 每批最多 10 条
- MultiSelect 字段值传 `["选项1", "选项2"]`（数组）
- SingleSelect 字段值传 `"选项名"`（字符串）
- 新建子表后记得删除默认空记录（如有）

### 数据源可用性（2026-05-27 实测）

**✅ 已验证稳定（OpenCLI 直连）：**
- `opencli weibo hot` — 微博热搜（JSON 结构含 url/category/hot_value）
- `opencli toutiao hot` — 今日头条热榜（JSON，带 hot_value/url/image）
- `opencli douyin hashtag hot` — 抖音热点词（JSON，含 view_count）
- `opencli zhihu hot` — 知乎热榜（JSON，含 heat/answers）
- `opencli tieba hot` — 贴吧热榜（JSON，含 discussions）
- `opencli 36kr hot` — 36氪热榜（JSON，含 url/title）
- `opencli bilibili hot` — B站热门（JSON，含 play/danmaku）

**✅ 稳定（网页抓取）：**
- `web_fetch https://top.baidu.com/board?tab=realtime` — 百度热搜（readability 提取）

**⚠️ 受限：**
- Tophub 会触发 Cloudflare 验证（403），间隔使用
- web_search 依赖 SearXNG 配置
- OTA 平台（携程/Booking等）有反爬限制
- 飞书 Sheets API 稳定可用（读取酒店资源表）

**📌 登录要求：**
- `public` — 直接可用（36氪/百度）
- `cookie` — 需在Chrome登录（微博/知乎/抖音/B站/贴吧/Twitter/今日头条）

### 子表命名规范

```
格式：城市·热点关键词概括
示例：天津·帕梅拉美食之旅
     塞尔维亚·中塞免签出境游
     川西·稻城亚丁替代路线
     上海·白玉兰影视打卡游
     青岛·崂山AI假新闻景区推广
```

### 酒店信息标注规范

| 来源 | 标注 |
|------|------|
| 资源表中已入库 | 标注「已入库」+ 具体礼遇/价格 |
| 通用推荐待拓展 | 标注「⚠️待拓展」 |
| 补充的五星酒店 | 标注集团品牌 + 参考价格区间 |

### 笔记内容创作守则

#### 8大内容品类

| 品类 | 定位 | 标题风格 | 文案调性 |
|------|------|---------|---------|
| 💎 高净值度假客/蜜月 | 品牌溢价·品质感 | ✨/🌅 emoji·情绪流 | 📸🍽️🛁 小标题分段·细节描写 |
| 💼 商务实效型 | B端转化·新客群 | 标题含｜·结论前置 | 📋💼🎯📊 数据化·专业客观 |
| ⚡ 实时红利截流型 | 急迫转化·评论区引流 | 标题含⚠️🔥⏰ | ✅清单+⚠️提醒+💬评论区互动钩子 |
| 🌿 种草型范流量号 | 泛流量拉新·收藏导向 | 散文式·情绪第一 | 短句留白·零广告感·情绪流>信息流 |
| 📖 干货价值类 | 信息密度·强收藏 | 「全攻略」「一篇讲透」 | 🏠🍽️🎯🚗分段·可收藏 |
| 🛠️ 教程攻略类 | 实用教程·转发 | 「手把手」「秘籍公开」 | Step-by-step编号📱💡🎁📝 |
| ⚠️ 避坑类 | 中立可信·高信任 | 含⚠️「拔草帖」「真心话」 | ✅❌对比·先说缺点再说优点 |
| 🏢 行业垂直类 | 专业壁垒·深度阅读 | 「产品拆解」「N年常青」 | 🏗️📐🎯专业视角·行业分析 |

#### 核心规则
- ❌ **正文不写具体金额/价格数字**，用「打折优惠」「限时优惠」替代
- ✅ 每个品类针对同一资源写一篇，形成内容矩阵
- ✅ 每篇标注「对标爆款风格」：参考的小红书爆款笔记类型
- ✅ 引用话题15-20个，覆盖精准+泛流量标签
- ✅ 笔记标题要有情绪钩子/行动号召

## 文件结构

```
hotspot-bitable-analysis/
  SKILL.md              # 本文件（完整工作流）
  scripts/
    insert_records.py   # 主表记录插入脚本模板
```
