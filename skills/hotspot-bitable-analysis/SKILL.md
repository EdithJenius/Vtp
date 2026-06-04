---
name: hotspot-bitable-analysis
description: "全网热点调研 → 旅游商机分析 → 笔记裂变内容库 → Feishu Bitable 全流程"
---

# 热点商机多维分析 Skill

> 一条龙：抓热搜 → 交叉验 → 商机析 → 主表库 → 深挖子表 → 文旅调研 → 笔记裂变 → 上游产业链 → 每日简报

## 触发词

- "整理热点" / "今日热点" / "热点分析"
- "做一遍热点调研"
- "生成笔记裂变"

## ⚠️ 核心原则

### 原则1：永远使用选项名称，不是 optID

```python
# ✅ 正确
"来源渠道": ["微博热搜", "百度热搜"]   # MultiSelect 传数组
"优先级": "高"                          # SingleSelect 传字符串

# ❌ 错误
"来源渠道": ["opt6mByzqo", "optTzXkli7"]
"优先级": "optcTwW4fI"
```

### 原则2：备注链接格式规范

```python
import urllib.parse
# ✅ 微博：url = 'https://s.weibo.com/weibo?q=' + urllib.parse.quote('话题名')
# ✅ 百度：url = 'https://www.baidu.com/s?wd=' + urllib.parse.quote('话题名')
# ✅ 抖音热门(无具体视频)：url = 'https://www.douyin.com/hot'
# ✅ 抖音热榜+具体视频：url = f'https://www.douyin.com/hot?modal_id={video_id}'
# ✅ 知乎/头条/B站/贴吧：直接用opencli返回的url字段
```

**核心原则：多平台话题只保留一条链接。**
优先级：微博 > 知乎 > 百度 > 头条 > B站 > 抖音 > 贴吧 > 36氪

### 原则3：全部用Python，不要用Bash

❌ Bash 不兼容：`declare -A` 在 zsh 报错、heredoc 变量空值、JSON 解析脆弱
✅ 统一 Python，token 在脚本内部获取

### 原则3b：写脚本文件，不用 heredoc/内联 Python

❌ `python3 -c "..."` 或 `python3 << 'EOF'` heredoc — 中文/特殊字符编码问题多
✅ 用 `write` 工具写 .py 文件到 scripts/ 目录，再 `exec` 运行

⚠️ 已知坑：heredoc 中 `json.l…())` 会被截断成含 `…` 字符的非法语法
✅ 务必写完整：`json.loads(f.read().decode())`

### 原则3c：Config解析用 configparser + strip 引号

```python
import configparser
config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId'].strip('"')
APP_SECRET = config['provider.feishu']['appSecret'].strip('"')
```

configparser 读取 TOML 的 `key = "value"` 格式时，引号会作为值的一部分保留，必须 strip。

❌ 用 `get_val()` 手写解析 — 遇到 `[section]` 头会失败
✅ 用 configparser 自动处理 section

### 原则4：每次操作后验证

code=0 不代表真写入！GET 再读一次确认。

### 原则5：重试必去重

脚本失败后重跑前，先 delete_all_records() 清空目标表。

### 原则6：每次拿新token

脚本第一行就重新获取，不复用。

### 原则6b：每个脚本独立获取 token

脚本第一行就重新获取，不复用。

```python
def get_token():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.openclaw/config.toml'))
    app_id = config['provider.feishu']['appId'].strip('"')
    app_secret = config['provider.feishu']['appSecret'].strip('"')
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode())['tenant_access_token']
```

**⚠️ 重要：不要用 `***` 或 `json.l…()` 的省略写法，必须写完整！**

### 原则7：Select字段选项先配好再写数据

❌ 先写数据再PUT修改options → 已有记录字段变NULL
✅ 创建字段时一次性配全所有选项，再写入数据

### 原则8：笔记产出后必须过合规校验

```python
from xiaohongshu_compliance import audit_and_fix
clean_body, violations = audit_and_fix(body)
if violations:
    print(f'[合规] {count}处替换')
```

### 原则9：每次写入链接必须做有效性检验

```python
# 写链接前验证是否可访问
import urllib.request
for link in all_links:
    try:
        req = urllib.request.Request(link, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as f:
            code = f.getcode()
            if code >= 400:
                print(f'[链接异常] {link[:50]}... HTTP {code}')
    except Exception as e:
        print(f'[链接异常] {link[:50]}... {str(e)[:30]}')
```

**已知链接坑和平台格式要求：**

| 平台 | 链接格式 | 验证状态 |
|------|---------|---------|
| 微博 | `https://s.weibo.com/weibo?q={URL编码话题}` | ✅ 可靠 |
| 百度 | `https://www.baidu.com/s?wd={URL编码话题}` | ✅ 可靠，HTTP 200 |
| 知乎 | opencli 返回的 `url` 字段直接使用 | ✅ 可靠 |
| 今日头条 | opencli 返回的 `url` 字段直接使用 | ✅ 可靠 |
| B站 | opencli 返回的 `url` 字段直接使用 | ✅ 可靠 |
| 贴吧 | opencli 返回的 `url` 字段直接使用 | ✅ 可靠 |
| 36氪 | opencli 返回的 `url` 字段直接使用 | ✅ 可靠 |
| **抖音** | **特殊处理**（见下方） | ⚠️ 需额外步骤 |

**抖音链接特殊处理（最重要）：**

抖音没有公开的Web话题/搜索页面，所有 `douyin.com` 下的深链接都有问题：
- `hashtag/{id}` → 404 ❌ 平台封锁
- `discover?keyword=` → 301跳转但不精准 ❌
- `video/{id}` → 仅对已知视频ID有效

**推荐的抖音链接方案：**
1. 如果话题在抖音热榜上 → 用 `https://www.douyin.com/hot`（热榜首页）
2. 如果需要指向具体视频 → `https://www.douyin.com/hot?modal_id={19位视频ID}`
3. 视频ID从 `discover?keyword={URL编码话题}` 页面中用正则 `r'(\d{19})'` 提取
4. 多个抖音话题可共用热榜首页 `hot` 链接

**多平台话题规则：**
- 用户要求：多平台话题只保留 **一条** 链接即可
- 优先级：微博 > 知乎 > 百度 > 头条 > B站 > 抖音 > 贴吧 > 36氪
- 抖音链接仅用于「抖音单源」话题（只有抖音一个来源的）
- 百度热搜 HTML 解析不稳定，需确认有内容再提取
- B站/知乎/头条/贴吧的 opencli 输出链接通常可靠
- 多平台话题只保留一条链接即可

---

## 工作流概览（完整链路12步）

```mermaid
flowchart TD
  A[Step0: 上游产业链采集] --> A1[Step1: 多平台热搜采集]
  A1 --> B[Step2: 交叉验证+合并]
  B --> C[Step3: 旅游商机分析]
  C --> D[Step4: 创建主Bitable+字段+权限]
  D --> E[Step5: 深度分析子表×N]
  E --> F[Step6: 酒店资源匹配]
  F --> G[Step7: 地区文旅符号调研]
  G --> H[Step8: 创建“笔记裂变内容库”表]
  H --> I[Step9: 生成笔记(10模板/对标克隆)]
  I --> J[Step10: 扩展到所有地区酒店]
  J --> J1[Step11: 上游数据入Bitable子表]
  J1 --> K[Step12: 每日混合简报]
  K --> L[Step13: 输出链接+更新Skill]
```

---

## Step 1-6: 热点分析流程（详见下方各节）

| 步骤 | 核心内容 | 产出 | 脚本 |
|------|---------|------|------|
| **Step 0** | 上游产业链采集（航空/酒店/政策/会展） | 上游信息JSON | route-analysis/scripts/step1_upstream_collect.py |
| **Step 1** | 8平台并行采集 | 微博/头条/知乎/抖音/B站/贴吧/36氪 | opencli命令 |
| **Step 2** | 跨平台合并重复话题+上游信息融合 | 去重后的热点+上游集合 | step0_upstream_feeder.py |
| **Step 3** | 逐条分析地点/景点/商机/优先级 | 带⭐商机清单 | 人工+AI |
| **Step 4** | 创建Bitable+字段+批量插入+公开权限 | 主数据表(15条) | step1_4_full.py |
| **Step 5** | 创建热点地区子表(酒店/景点/美食/活动) | 4+深度分析子表 | step5_subtables.py |
| **Step 6** | 飞书资源表读取+酒店匹配 | 已入库/待拓展标注 | — |

> 详细API参考下方「Step 4: 创建 Bitable」及后续章节

### 步调规范：地区子表必须有酒店信息

每个地区深度分析子表必须包含 **5-10家酒店信息**，记录：
- 名称（官方准确名称）
- 类别 =「酒店住宿」
- 推荐理由
- 参考价格（格式如 `800-2000/晚`）
- 关联热度

❌ 只放1-2家 → 用户一定会要求补全
✅ 每个地区5-10家，覆盖经济型~高端

---

## 笔记裂变内容库（v2 — 10模板 + 对标克隆）

在完成热点分析后，对涉及的热点地区酒店，生成**10种风格模板×每家酒店**的小红书风格笔记。

支持两种模式：
- **基础模式**：运营从10个模板库选一个，AI按模板结构填充内容
- **进阶模式**：运营给一条对标笔记链接/文案，AI拆解结构后套内容

### 10大风格模板

| # | 模板 | 定位 | 适用场景 |
|:-:|:----|:------|:---------|
| 1 | 📋 干货/清单流 | 信息密度高、收藏型 | 酒店攻略、必做清单 |
| 2 | 🌿 情绪种草流 | 感性体验、散文体 | 治愈系、生活方式 |
| 3 | ⚖️ 测评对比流 | 中立客观、优缺点 | 酒店测评、A vs B |
| 4 | 🏗️ 行业分析流 | 专业深度、数据 | 高端酒店、行业解读 |
| 5 | ⚡ 截流紧迫感流 | 促转化、限时感 | 限时优惠、节假日截流 |
| 6 | 🎬 Vlog日程流 | 分镜头叙事+时间线 | 沉浸式体验、24h记录 |
| 7 | 🔄 反差点评流 | 「去前vs去后」反差 | 反转剧情、流量钩子 |
| 8 | 🔬 科普涨知识流 | 专业壁垒、涨知识 | 酒店冷知识、行业科普 |
| 9 | 👤 真实UGC流 | 素人口吻、去营销感 | 像真人发的、接地气 |
| 10 | ❓ 问答攻略流 | FAQ形式、解决焦虑 | 行前准备、注意事项 |

### 对标克隆模式

运营提供一条小红书对标笔记（链接或粘贴文案），系统自动拆解：
- 标题模式（emoji规则、长度、钩子类型）
- 段落编排（段长、分隔方式）
- 语气调性（正式/口语/情绪）
- Emoji密度和类型
- 结构分段方式
- 然后以同样结构填入目标酒店内容

### 脚本调用

```bash
# 基础模式：选模板
python3 note_generator.py --hotel "成都W酒店" --template "情绪种草流" --category "高净值"

# 进阶模式：对标克隆
python3 note_generator.py --hotel "丽江悦榕庄" --clone "https://..." --category "种草型"
```

### 字段结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 笔记标题 | Text(主) | 带情绪钩子的标题，⚠️ **每家酒店每个品类必须用不同标题结构** |
| 酒店名称 | Select | 可扩展 |
| 内容品类 | Select | 10模板单选项 |
| 正文文案 | Text(长) | ❌无具体金额 |
| 引用话题 | Text | 15-20个#话题标签 |
| 备注 | Text | 核心卖点提炼 |
| **发布时间建议** | **Text** | **🆕 根据品类+目标人群推荐最佳发布时间** |
| **封面/配图建议** | **Text** | **🆕 封面设计/配图风格/点击率优化指导** |
| **目标人群** | **Select** | **🆕 高端商务/蜜月情侣/亲子家庭/毕业旅行/摄影爱好者/高端团建/自由行背包客/名人贵宾** |
| **季节标签** | **Select** | **🆕 春季/夏季/秋季/冬季/全年** |
| **热点关联** | **Text** | **🆕 关联的当前热点话题/事件** |
| **关键词** | **Text** | **🆕 SEO关键词（3-5个核心词）** |
| **热点标签** | **Text** | **🆕 蹭热度用的热门#标签（3-5个）** |
| **精准标签** | **Text** | **🆕 精准定位#标签（5-8个）** |
| **酒店人群画像** | **Text** | **🆕 历史住客画像分析** |

#### 字段详解：新字段使用说明

##### 发布时间建议
根据内容品类推荐最佳发布时间：

| 内容品类 | 最佳发布时间 | 理由 |
|:--------|:------------|:-----|
| 📋 干货清单流 | 周五 18:00-20:00 | 下班前收藏攻略型内容 |
| 🌿 情绪种草流 | 周五-周日 10:00-12:00 | 周末出行决策窗口 |
| ⚖️ 测评对比流 | 周二-周四 20:00-22:00 | 工作日晚上深度阅读高峰 |
| 🏗️ 行业分析流 | 周二-周四 12:00-13:00 | 午休碎片化阅读 |
| ⚡ 截流紧迫感流 | 周四 18:00-20:00 | 周末出行前决策期 |
| 🎬 Vlog日程流 | 周六-周日 10:00-12:00 | 周末沉浸式内容消费 |
| 🔄 反差点评流 | 周三 20:00-22:00 | 周中情绪宣泄高峰 |
| 🔬 科普涨知识流 | 周三 12:00-13:00 | 午休信息摄入 |
| 👤 真实UGC流 | 全时段，优先19:00-21:00 | 晚高峰流量池 |
| ❓ 问答攻略流 | 周四 20:00-22:00 | 出行前决策焦虑期 |

##### 封面/配图建议（针对高端群体优化）

| 内容品类 | 封面风格 | 点击率要素 |
|:--------|:---------|:----------|
| 测评对比流 | 左右对比图 / 分屏设计 | 直观呈现差异、数字标注、品牌Logo |
| 情绪种草流 | 单张大片感（日落/泳池/远景）| 留白构图、低饱和度、高级灰调 |
| 干货清单流 | 信息图拼贴 + 醒目标题字 | 要点一目了然、整齐排版 |
| 反差点评流 | 「去前vs去后」分屏 | 视觉反差大、情绪对比强 |

**面向高端群体的封面原则：**
- ❌ 不要用饱和度过高的渐变/炫光效果
- ❌ 不要用大字号白底红字促销感
- ✅ 用低饱和莫兰迪色系、留白构图
- ✅ 用品牌Logo/水印传递品质感
- ✅ 正文配图用实拍无滤镜，避免过度修图

##### 标题多样性策略（解决重复标题问题）

**⚠️ 核心规则：** 同一家酒店10篇笔记，**必须用10种不同标题结构**，不能只是换酒店名。

可用的标题结构库（每篇选不同）：

| # | 结构 | 示例 |
|:-:|:----|:----|
| 1 | 数字型 | 「住过5次XXX，告诉你这3个隐藏服务」|
| 2 | 身份圈层型 | 「商务出差选XXX的5个理由，最后1个太真实」|
| 3 | 对比型 | 「XXX vs YYY，同价位我选前者」|
| 4 | 反转型 | 「去之前觉得贵，退房时觉得赚了」|
| 5 | 痛点直击型 | 「去XXX最怕什么？这3个坑我替你踩了」|
| 6 | 场景代入型 | 「如果你只有2天假期，我建议你来XXX」|
| 7 | 偷懒攻略型 | 「不想做攻略？XXX保姆级入住指南请收好」|
| 8 | 揭秘型 | 「XXX员工不会告诉你的10个免费服务」|
| 9 | 对比反差型 | 「XXX的白天vs黑夜，完全是两个世界」|
| 10 | 限定款型 | 「XXX这个季节去，景色翻倍（附时间表）」|

**算法实现：** 生成笔记时，遍历结构库并按品类过滤可用结构，确保同一酒店不重复

### 内容发布数据观察（副表）

> 🆕 用于追踪已发布内容的流量表现

**创建方式：** 在热点Bitable中手动或脚本创建「内容发布数据观察」表

**表结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 笔记标题 | Text | 与笔记裂变内容库关联 |
| 酒店名称 | Select | 与主表一致 |
| 内容品类 | Select | 与主表一致 |
| 发布时间 | Date | 实际发布的时间 |
| 7日点赞 | Number | 发布后7天数据 |
| 7日收藏 | Number | 发布后7天数据 |
| 7日评论 | Number | 发布后7天数据 |
| 流量评级 | Select | 爆款🔥/良好👍/普通👌/不理想👎 |
| 备注 | Text | 复盘心得 |

**分析方法：** 按月统计→看哪类内容、哪家酒店、什么时间发效果最好

### 酒店人群画像

> 🆕 用于了解酒店住客结构 → 指导内容方向

**数据来源（按准确度排序）：**

| 来源 | 获取方式 | 可靠性 |
|:----|:---------|:------|
| 飞猪/携程用户评价分析 | web_fetch 携程/飞猪页面 → AI 提取高频词 | ⭐⭐⭐ 可行 |
| 小红书笔记评论区 | xhs read → 分析评论用户画像 | ⭐⭐⭐ 可行 |
| 酒店官方公众号/官网 | 酒店介绍中常提及主力客群 | ⭐⭐ 有限 |
| 专业旅游报告 | 搜索该酒店/品牌的最新客群报告 | ⭐ 偶尔有 |

**分析字段示例：**
```
🏨 三亚亚特兰蒂斯酒店
   👤 核心客群：亲子家庭（60%）/ 蜜月情侣（25%）/ 商务（10%）/ 其他（5%）
   📍 来源地：北上广深（70%）/ 新一线（20%）/ 海外（10%）
   💰 消费力：高净值（65%）/ 中高端（30%）/ 其他（5%）
   📊 数据来源：携程用户评价 + 小红书笔记综合估算
```

### 笔记生成原则

1. ❌ **正文不写具体金额**（只说「打折优惠」「限时优惠」「有活动」）
2. ✅ **每家酒店必须覆盖全部10品类**（干货/种草/测评/行业分析/截流/Vlog/反差/科普/UGC/问答）
3. ✅ **标题多样性策略**：同一家酒店的10篇笔记必须用10种不同标题结构（见上方标题结构库）
4. ✅ 正文用 `\n\n` 分段（双换行），段落内用 `\n` 换行，保持紧凑排版
5. ✅ **自动合规校验**：每条正文过后 xiaohongshu_compliance.py
6. ✅ 引用话题15-20个，覆盖精准+泛流量标签
7. ✅ 标题带 emoji 钩子 + 数字/反差/截流元素
8. ✅ 正文用emoji小标题分段

### 2026-05-30 已覆盖酒店（最新）

| 地区 | 主推酒店 | 品类覆盖 | 数据来源 |
|------|---------|:--------:|---------|
| 桂林·阳朔 | **阳朔悦榕庄** | 10/10 | 两广高温热点 |
| 三亚 | **三亚亚特兰蒂斯** | 10/10 | 毕业旅行热点 |
| 广州 | **广州花园酒店** | 10/10 | 两广高温热点 |
| 杭州 | **杭州君悦酒店** | 10/10 | 演唱会经济热点 |
| 丽江 | 丽江悦榕庄 | 8/8 | 夏季避暑热点 |
| 成都 | 成都W酒店 | 8/8 | 外国人美食游热点 |
| 北京 | 北京国贸大酒店 | 8/8 | 暑期旅游热点 |
| 长白山 | 长白山天沐温泉酒店 | 8/8 | 高温避暑热点 |

**新增酒店扩展步骤：**

1. 给「酒店名称」字段追加选项（PATCH field property.options）
2. 确定该酒店的10个品类内容风格方向
3. 按10品类模板各写一篇（正文用 `\n\n` 分段，带 emoji 标题）
4. batch_create 批量插入（每批≤10条）
5. 验证每篇的「酒店名称」字段非空

### ⚠️ 地区子表必须有酒店信息

每个地区深度分析子表（景点/美食/活动等）中，**必须包含 5-10 家酒店信息**，并记录：
- 酒店名称（准确官方名称，如「稻城亚丁日松贡布酒店」不是「日松贡布」）
- 类别标记为「酒店住宿」
- 推荐理由
- 参考价格（如`800-2000/晚`）
- 关联热度

❌ 只放1-2家酒店 → 用户会要求补全
✅ 每个地区5-10家，覆盖不同价位

---

## 上游产业链采集（新增模块）

### 采集源

| 优先级 | 源 | 覆盖内容 | 采集方式 | 稳定性 |
|:------:|:----|:---------|:---------|:------:|
| 🔴 必选 | 环球旅讯 TravelDaily | 中文旅游行业新闻 | web_fetch(首页) | ✅ 稳定 |
| 🔴 必选 | 新华网旅游频道 | 文旅政策/目的地新闻 | web_fetch | ⚠️ 有时空 |
| 🟡 进阶 | HotelNewsResource | 全球酒店行业新闻 | web_fetch | ⚠️ 仅标题 |
| 🟡 进阶 | RoutesOnline | 全球航线动态 | web_fetch | ⚠️ 待验证 |
| 🟡 进阶 | FlightGlobal | 航空产业新闻 | web_fetch | ⚠️ 待验证 |

**推荐：以环球旅讯 TravelDaily 为主力源**，内容优质、中文可读性强、覆盖全面。直接用 `web_fetch "https://www.traveldaily.cn/"` 即可获取最新文章列表。

### 脚本

```bash
# 上游采集
python3 route-analysis/scripts/step1_upstream_collect.py
# 上游数据转换为热点兼容格式（自动调用采集）
python3 step0_upstream_feeder.py
# 上游数据写入Bitable子表
python3 upstream_to_bitable.py
```

### 分类体系

上游信息分为4个类别：
- 航空运力（新航线、航司运力、机场扩建）
- 酒店供应链（品牌入驻、新开业、资产交易）
- 政策签证（免签、签证政策、出入境管理）
- 会展活动（大型展会、峰会排期）

## 每日混合简报（新增模块）

### 功能

结合上游产业链情报 + 全网热搜，每日生成一份「文旅商机速报」。

### 内容结构

```
📊 今日文旅商机速报 YYYY-MM-DD

🏭 上游产业链情报
  ▎航空运力 · N条
  ▎酒店供应链 · N条
  ▎政策签证 · N条

🔥 今日热搜 TOP10
  1. 📰 话题
  ...

💡 商机交叉分析
  ✅ 签证利好
  ✅ 运力增长
  ✅ 供给信号
📎 完整数据：https://...
```

### 脚本

```bash
python3 daily_briefing.py
```

### 自动化

可通过 cron 设置每日自动执行：
```
时间：每天 09:00 Asia/Shanghai
动作：采集上游+热搜 → 生成简报 → 发飞书
```

## 完整流程速查

```
┌─────────────────────────────────────────────────────────┐
│  第一阶段：上游+热点分析                               │
│  0. 上游产业链采集 (航空/酒店/政策/会展)               │
│  1. 多平台热搜采集 (opencli / web_fetch)                │
│  2. 交叉验证→去重→合并+上游融合                        │
│  3. 旅游商机分析→优先级评定                            │
│  4. 创建主Bitable→字段配置→批量插入→权限公开           │
│  5. 创建深度分析子表 (高/中优先级热点地区)              │
│  6. 地区文旅符号调研 (8维度×N地区)                     │
├─────────────────────────────────────────────────────────┤
│  第二阶段：笔记裂变                                    │
│  7. 创建"笔记裂变内容库"子表                            │
│  8. 选模板/对标克隆 → 生成10模板笔记                   │
│  9. batch_create写入→验证酒店名称非空                   │
│ 10. 扩展到所有覆盖地区（每家酒店8+篇）                 │
├─────────────────────────────────────────────────────────┤
│  第三阶段：上游入库+每日简报                          │
│ 11. 上游数据入Bitable子表                               │
│ 12. 每日混合简报（上游+热搜）                          │
│ 13. 输出链接给永乐                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Step 4: 创建 Bitable（详细API）

### 4.1 获取 Token

```python
import urllib.request, json, os, configparser

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.openclaw/config.toml'))
APP_ID = config['provider.feishu']['appId'].strip('"')  # TOML引号残留
APP_SECRET = config['provider.feishu']['appSecret'].strip('"')

body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=body, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as f:
    TOKEN = json.loads(f.read().decode())['tenant_access_token']
```

⚠️ **一定要 .strip('"') 去掉 TOML 引号**，否则 auth 失败。

### 4.2 创建 Bitable

```python
resp = json.loads(urllib.request.urlopen(
    urllib.request.Request('https://open.feishu.cn/open-apis/bitable/v1/apps',
        data=json.dumps({"name": "热点商机多维分析 YYYY-MM-DD HH时"}).encode(),
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
).read())
APP_TOKEN = resp['data']['app']['app_token']
TABLE_ID = resp['data']['app']['default_table_id']
```

**返回格式：**
```json
{
  "code": 0,
  "data": {
    "app": {
      "app_token": "xxx",
      "default_table_id": "xxx",
      "name": "热点商机多维分析...",
      "url": "https://..."
    }
  }
}
```

⚠️ `default_table_id` 在 `data.app` 下，不是 `data.default_table`。

### 4.3 字段结构

| 字段 | type | 说明 |
|------|------|------|
| 热点话题 | 1(Text) | 主字段，重命名默认字段 |
| 来源渠道 | 4(MultiSelect) | 微博/百度/知乎/抖音/小红书/B站/综合/头条/贴吧/36氪 |
| 话题类别 | 3(SingleSelect) | 航天科技/社会民生/天气灾害/财经股市/国际外交/科技AI/体育赛事/文旅美食/健康生活/教育 |
| 热度指数 | 1(Text) | 原始热度描述 |
| 热度指数数值 | 2(Number) | 整数热度 |
| 关联地点 | 1(Text) | 城市/区域 |
| 关联旅游景点 | 1(Text) | 可借势的景点 |
| 旅游商机分析 | 1(Text) | 长文本+⭐标记 |
| 优先级 | 3(SingleSelect) | 高/中/低 |
| 备注 | 1(Text) | 📎来源链接 |

### 4.4 配置字段

新Bitable默认有「文本」「单选」「日期」「附件」四个字段。

**重命名默认字段（用 PUT 不是 PATCH）：**
```python
fields_resp = json.loads(urllib.request.urlopen(
    urllib.request.Request(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields',
        headers={'Authorization': f'Bearer {TOKEN}'})
).read())
text_field = next((f for f in fields_resp['data']['items'] if f['field_name'] == '文本'), None)

body = json.dumps({"field_name": "热点话题", "type": 1}).encode()
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{text_field["field_id"]}',
    data=body, method='PUT',
    headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
urllib.request.urlopen(req)
```

**删除不需要的默认字段：**
```python
for fname in ['单选', '日期', '附件']:
    f = next((x for x in fields_resp['data']['items'] if x['field_name'] == fname), None)
    if f:
        req = urllib.request.Request(
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{f["field_id"]}',
            method='DELETE', headers={'Authorization': f'Bearer {TOKEN}'})
        urllib.request.urlopen(req)
```

**创建新字段时一次性配完选项：**
```python
body = json.dumps({
    "field_name": "来源渠道", "type": 4,  # MultiSelect
    "property": {"options": [
        {"name": "微博热搜"}, {"name": "百度热搜"}, {"name": "知乎热榜"},
        {"name": "抖音"}, {"name": "头条"}, {"name": "贴吧"}, {"name": "36氪"}
    ]}
}).encode()
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields',
    data=body, headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
urllib.request.urlopen(req)
```

### 4.5 删除空记录 → 插入 → 验证 → 权限

**关键：**
- 默认10条空记录，逐个 DELETE（items可能为None，需加保护）
- batch_create 每批≤10条
- 验证用 GET 读取（不只看 code）
- 权限：PATCH public + POST member
- ❌ 删除字段后的表可能 items=null（非空列表），需加 `or []` 保护

```python
del_resp = json.loads(urllib.request.urlopen(
    urllib.request.Request(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=50',
        headers={'Authorization': f'Bearer {TOKEN}'})
).read())
for item in (del_resp.get('data', {}).get('items') or []):
    rid = item['record_id']
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{rid}',
        method='DELETE', headers={'Authorization': f'Bearer {TOKEN}'})
    urllib.request.urlopen(req)
```

---

## 深度分析子表 / 文旅调研

### 子表创建API（重要！）

**创建子表时 body 必须包在 `table` 键下：**
```python
body = {"table": {
    "name": "甘孜·稻城亚丁景区事件",
    "fields": [{"field_name": "名称", "type": 1}]  # 初始字段
}}
resp = api('POST', f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables', body)
tid = resp['data']['table_id']
```
❌ 错误：`{"name": "..."}` → 返回 `WrongRequestBody (code 1254001)`
✅ 正确：必须包在 `{"table": {...}}` 中

### 子表字段结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 名称 | Text(1) | 主字段 |
| 类别 | Select(3) | 酒店住宿/景点景区/美食餐饮/文化活动/交通出行/旅行社·线路 |
| 推荐理由 | Text(1) | 长文本 |
| 参考价格 | Text(1) | 价格区间 |
| 关联热度 | Text(1) | 热度描述 |
| 详情链接 | Text(1) | URL |
| 备注 | Text(1) | 补充信息 |

### 文旅调研8维度

1. 基础信息（位置/规模/地位）
2. 金字招牌（核心吸引力）
3. 市井风情（本地文化特色）
4. 视觉资产（拍摄出片点）
5. 季节限定（什么季节最值得去）
6. 避坑槽点（常见投诉/坑）
7. 商业闭环（消费场景/变现路径）

### ⚠️ 新创建的表没有默认空记录

如果用 `POST /tables` 带 `fields` 参数创建，新表可能 `items=null` 而不是空数组。
在清理记录时必须加保护：
```python
items = del_resp.get('data', {}).get('items') or []
```

---

## 数据源配置

**已验证稳定：**
| 平台 | 命令 | 输出字段 |
|------|------|---------|
| 微博热搜 | `opencli weibo hot --limit 20 -f json` | ⚠️ 2026-05-28发现HTTP 404，备选: `web_fetch tophub.today/n/KqndgxeLl9` |
| 今日头条 | `opencli toutiao hot -f json --limit 15` | title/hot_value/rank/url |
| 抖音热点 | `opencli douyin hashtag hot --limit 20 -f json` | name/view_count/id |
| 知乎热榜 | `opencli zhihu hot --limit 15 -f json` | title/heat/answers/rank/url |
| 贴吧热榜 | `opencli tieba hot --limit 15 -f json` | title/discussions/url |
| 36氪热榜 | `opencli 36kr hot -f json --limit 15` | title/rank/url |
| B站热门 | `opencli bilibili hot --limit 15 -f json` | title/play/danmaku/bvid/url |
| 百度热搜 | `web_fetch https://top.baidu.com/board?tab=realtime` | ❌ readability 提取几乎总是空，建议放弃此源

---

## 🐛 踩坑记录（每次必读）

### 2026-05-27

1. **备注链接不能跳转** → `urllib.parse.quote('#话题#')` 编码中文
2. **子表内容重复两倍** → 重跑前 delete_all_records()
3. **batch_create 假成功** → code=0 但数据没写，需 GET 验证
4. **appSecret 被截断** → 用 Python parse config，不要 grep
5. **zsh 不兼容 declare -A** → 全部用 Python
6. **石头记→石头纪（错字）** → 酒店名核对官方名称
7. **正文含金额被退** → 只说「打折优惠」不写具体数字
8. **Text→Select 字段数据丢失** → 更新选项后需要写脚本重新填充所有记录的酒店名称
9. **PATCH 修改表名** → PUT 返回 404，要用 PATCH

### 2026-05-28

1. **每个脚本重复写 get_token()** → 抽取 feishu_utils.py 公共模块
2. **先写数据后改Select字段选项 → 数据变NULL** → 先创建完所有字段+选项，再写入数据
3. **微博 opencli 适配器404** → 需备选方案 Tophub 采集（`web_fetch tophub.today/n/KqndgxeLl9`）
4. **百度热搜 HTML 解析不稳定** → `web_fetch` readability 有时返回空，考虑备用源
5. **没有合规校验直接产出笔记** → 每条笔记产出后必须过 `xiaohongshu_compliance.audit_and_fix()`
6. **笔记覆盖不均** → 至少保证每家酒店4篇核心品类（高净值+种草+干货+避坑）
7. **Python heredoc 中 … 编码问题** → `json.l…())` 中 … 字符非法，必须写完整 `json.loads(f.read().decode())`
8. **子表创建脚本挂起** → 添加 timeout 和重试机制，避免长时间无响应
9. **抖音链接格式进化**：`hashtag/{id}`→404 → `discover?keyword=`→不准 → `video/{id}`→视频不对 → `hot?modal_id={id}`→终于正确
10. **先写数据后改链接格式** → 确保每条记录的链接字段都有内容，不要留空
11. **多平台只留一条链接** → 按优先级选一个平台的链接即可
12. **新Bitable命名含小时** → 多次执行时加小时区分：`热点商机多维分析 YYYY-MM-DD HH时`

### 2026-05-29

1. **Config解析方式升级** → 用 `configparser` 替代手写 `get_val()`，注意 `.strip('"')` 去 TOML 引号
2. **Bitable创建响应格式** → `resp['data']['app']['default_table_id']` 不在 `data.default_table` 下
3. **字段重命名用PUT不是PATCH** → PATCH `/bitable/v1/apps/{app}/tables/{table}/fields/{field}` 返回404，PUT才是正确方法
4. **子表创建body必须包`table`键** → `{"table": {"name": "...", "fields": [...]}}` 不能直接传 `{"name": "..."}`
5. **新表items可能为null** → 默认记录删除时需 `(resp.get('data', {}).get('items') or [])` 保护，否则 `TypeError: 'NoneType'`
6. **创建子表时带fields则无默认空记录** → 不用删除空记录，但也需要保护性判断
7. **表名不能重复** → 同名返回 `TableNameDuplicated (code 1254013)`，需加随机后缀处理
8. **地区子表必须有5-10家酒店** → 每个子表只放1-2家酒店不够，用户会要求补全到5-10家（含价格）
9. **笔记裂变库必须每个酒店8品类全覆蓋** → 只覆盖2-3品类不够，用户要求每家酒店8篇全品类
10. **权限comment_entity值** → `"anyone"` 无效，必须用 `"anyone_can_view"` 或 `"anyone_can_edit"`

### 2026-05-29（v2 重构）

1. **上游源不可靠** → 6个信息源中3个可用（新华网/文旅部/RoutesOnline/HotelNewsResource/FlightGlobal），环球旅讯仅静态部分，携程趋势/Booking/民航局JS不可抓
2. **上游数据入表** → 上游数据已格式化为热点兼容格式（step0_upstream_feeder.py），133条一次入Bitable子表成功
3. **热搜热度解析** → 知乎热度格式「673万热度」含空格，需做清理再转int
4. **飞书链接格式** → `[航线动态] Title (Source)` 会被飞书识别为笔记链接，需替换为 `✈️ 航线动态 · Title — Source`
5. **10模板库** → 模板定义在note_templates.py，每个模板含description/title_style/structure/emoji_rule/tone
6. **对标克隆** → clone_analyzer.py 支持链接输入和手动粘贴两种模式
7. **简报格式** → 飞书输出避免使用 `[]()` 配对，用 emoji 前缀+中文分隔
8. **grill-me** → 笔记裂变重构和上游信息拓宽的需求均通过grill-me流程确认后实施

### 2026-05-30

1. **Python文件中文编码** → 含中文的 .py 文件必须加 `# -*- coding: utf-8 -*-` 头，否则 SyntaxError: Non-UTF-8 code
2. **Python脚本不用 `***` 占位符** → 不能写 `TOKEN = ***` 或 `APP_SECRET = ***`，`***` 是 Python 的幂运算语法错误。必须用完整函数：`def get_token(): ...` → `TOKEN = get_token()`
3. **get_token() 统一写法** → 统一抽取成函数，每个脚本调用一次，不要 inline 缩写
4. **上游采集首选 TravelDaily** → `web_fetch "https://www.traveldaily.cn/"` 返回内容丰富稳定。HotelNewsResource 解析效果差，仅返回标题链接
5. **笔记批量生成用 Python dict 内联** → 用大列表+字典的结构比 heredoc 稳定。正文用 `\n` 换行符嵌入字符串，不要用多行引号
6. **飞书 interactive card 消息** → 用 `msg_type: "interactive"` 发送富文本卡片，比纯文本效果好。card 的 `header.template` 支持 `blue`/`indigo`/`green`/`red`/`purple`/`yellow`/`orange` 等主题色
7. **深度子表带 fields 创建时无默认空记录** → 不需要执行 DELETE 清理步骤，但如果删了旧记录再插入，先 GET 检查 items 是否为 None
8. **笔记裂变内容库重建策略** → 如果要完整替换，先 GET 所有现有记录逐个 DELETE，再 batch_create 新记录。不要试图用 PATCH 部分更新
9. **上游数据分类新类别** → 除了原有4类（航空运力/酒店供应链/政策签证/会展活动），建议增加「文旅目的地」和「科技AI」两个类别，覆盖目的地营销和AI+旅游话题
10. **酒店名称 Select 选项管理** → 先 PUT 更新 field 的 options 添加所有酒店名，再写入记录。如果记录中的酒店名不在选项列表中，数据写入后该字段会变空白
11. **笔记正文排版规范** → 飞书 Bitable 中多行文本用 `\n\n` 双换行分段，`\n` 单换行分行。emoji 开头的小标题效果较好。正文控制在 300-800 字之间

---

## 文件结构

```
hotspot-bitable-analysis/
  SKILL.md                               # 主文档（完整工作流）
  references/
    xiaohongshu-forbidden-words.md       # 小红书违禁词/合规替换速查表
  scripts/
    feishu_utils.py                      # 飞书API公共模块（get_token/api/batch_insert 等）
    insert_records.py                    # 主表记录插入模板
    xiaohongshu_compliance.py            # 小红书内容合规自动校验模块
    step1_4_full.py                      # 热搜采集+分析+创建Bitable+插入（全流程）
    step5_subtables.py                   # 深度分析子表
    note_templates.py                    # 10个风格模板定义库【v2新增】
    clone_analyzer.py                    # 对标克隆模块【v2新增】
    note_generator.py                    # 核心生成引擎（选模板/对标克隆→输出笔记）【v2新增】
    step8_notes.py                       # 笔记裂变内容生成（使用新引擎）【v2改造】
    step0_upstream_feeder.py             # 上游数据→热点格式转换【v2新增】
    upstream_to_bitable.py               # 上游数据写入Bitable子表【v2新增】
    daily_briefing.py                    # 每日混合简报生成【v2新增】
  data/
    raw_data.json                        # 原始热搜数据
    analysis_result.json                 # 商机分析结果
    upstream_feeder_{date}.json          # 上游格式化数据
    upstream_feeder_{date}_dedup.csv     # 上游去重CSV
    note_examples.json                   # 10模板示例笔记
    briefing_{date}.md                   # 每日简报

route-analysis/
  SKILL.md                               # 上游产业链深度分析Skill
  scripts/
    step1_upstream_collect.py            # 上游信息采集（6个信息源）
  data/
    upstream_collected_{date}.json       # 上游原始数据
```

### 合规校验模块用法

```python
# 在笔记生成脚本中引入
import sys
sys.path.append('skills/hotspot-bitable-analysis/scripts')
from xiaohongshu_compliance import audit_and_fix

# 每条正文产出后自动校验
for record in records:
    body = record["正文文案"]
    clean_body, violations = audit_and_fix(body)
    if violations:
        print(f'[合规] {record["笔记标题"][:20]} - {len(violations)}处替换')
    record["正文文案"] = clean_body
```

违禁词涵盖7大类：绝对化用语/夸大效果/医疗健康/营销引流/标题标签/私信评论/平台红线。详细替换表见 `references/xiaohongshu-forbidden-words.md`。
