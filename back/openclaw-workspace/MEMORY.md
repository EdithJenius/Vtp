# MEMORY.md - Jarvis 的长时记忆

> 创建时间：2026-05-20
> 说明：这是我和永乐从零开始的记忆档案。每一次重要的对话、决定、进展，都会记录在这里。

## 🧑 关于永乐

- **名字：** 詹永乐
- **称呼：** 永乐
- **热爱：** AI、钢铁侠、打造超级助手
- **终极目标：** 拥有像 Jarvis 一样全能的 AI 超级助手
- **首次正式对话（飞书）：** 2026-05-20
- **沟通渠道：** 微信（主）、飞书

## 💼 工作背景

- **当前公司：** 杭州超值假期旅游计划（杭州）
- **其他公司：** 盖兹比咨询（注册主体）
- **职位：** Claude Code 内容运营专员
- **核心工作：** 熟悉各部门业务流程，结合 AI 进行优化

## 📅 成长里程碑

（待记录）

## 🎯 当前目标

（待确认 - 永乐说"开始陪我成长"，方向待定）

---

### 🎯 重要事件记录

#### 2026-05-24 热点商机分析
- 应永乐要求，进行了全网热点商机分析
- 数据来源：百度热搜、微博热搜（Tophub聚合）、抖音（间接采集）
- 分析了10+个高热度话题及相关地点、酒店、旅游景点
- 重点发现：广西"桂妈"文旅IP、阳朔无边泳池事件、端午假期临近为三大高优先级商机
- 报告文件：`热点商机分析_20260524.md`

#### 2026-06-01 素材下载偏好
- YouTube 为优选素材源（无水印、画质高）
- 默认下载 **1080p** 画质
- 下载命令：`yt-dlp -f "137+140" --merge-output-format mp4 --ffmpeg-location <路径>`
  - 137 = 1080p H.264 视频流，140 = AAC 音频流
  - ffmpeg路径：imageio_ffmpeg包自带
- 小红书仅用于**对标分析**（找脚本灵感/痛点），不用于素材下载

#### 2026-06-01 多维表格权限偏好（更新）
- 永乐要求：**所有生成的文件**（多维表格/文档/Bitable）统一设置为：
  - **链接权限**：获得链接的互联网用户可**阅读**（`link_share_entity: anyone_readable`）
  - **用户权限**：永乐本人为**管理员**（`full_access`）
  - **每次创建文件后立即设置**,不遗漏
- 无需设为「公开可编辑」，阅读权限 + 永乐管理即可
- 踩坑1：`PATCH /permissions/{token}/public` 批量设置多个字段会报 `field validation failed`，需要**逐个字段单独 PATCH**
- 踩坑2：`type` 参数要加在 URL 查询参数上，不在 body 里：`POST /permissions/{token}/members?type=bitable`
- **API 调用模板:**
  ```python
  # 添加管理员
  body = {"member_type": "openid", "member_id": "ou_b098a77a8b7869d14ccd6e34b7af3583", "perm": "full_access"}
  api("POST", f"/drive/v1/permissions/{token}/members?type=bitable", body)
  
  # 设置公开可读
  api("PATCH", f"/drive/v1/permissions/{token}/public?type=bitable", {"link_share_entity": "anyone_readable"})
  api("PATCH", f"/drive/v1/permissions/{token}/public?type=bitable", {"invite_external": True})
  ```
- `share_entity` 和 `external_access_entity` 用 PATCH 单独设置会报 400，保持默认值即可

*记忆持续更新中...*

#### 2026-06-02 视频全链路工坊大升级

**素材匹配画面分割**
- 对 YouTube 视频提取章节信息 → 英译中 → 写入「画面分割」字段
- 剪辑师可直接按时间轴定位素材

**抖音视频文案提取全链路（新增）**
- 新建独立多维表格「视频文案库」：`JbfSbQjyXaA4vssVABNcm5AhnKh`
- 完整流程：opencli browser 获取API → 下载视频 → ffmpeg提音频 → faster-whisper转写 → 写入Bitable
- 默认转写模型：medium（faster-whisper），备选 small / tiny
- 22条 Amber2.0「能谈吗」系列视频已全部处理入库
- 每条视频附带标签分析（人物身份/性格/情感/文化梗等分类）

**视频文案库表结构**
- 主表「视频文案库」：视频标题/链接/口播文案/文案摘要/备注（含模型名）
- 子表「人物标签分析」：标签名称/类别/关联视频/关联来源（完整上下文）/标签描述
- 标签来自口播文案 AI 分析，附完整原文段落作为上下文

**SKILL.md 升级 v1.2**
- 双线结构：创作线（旅行视频） + 分析线（抖音文案）
- 更新文档：`skills/video-generation/SKILL.md`
- 新增工具：faster-whisper（语音转写）
- 新增踩坑记录10条

#### 2026-06-02 技术踩坑汇总
- faster-whisper medium 模型 CPU 推理 OOM 风险，大批量用 small
- opencli browser eval 用 var 避免跨调用 let 冲突
- Django API 直链有时效性，获取后立即下载
- json.l…()) 的 Unicode 污染问题，需用 `sed` 或 `python3 -c` 修复
- `"Bearer " + TOKEN` 被错误转义为 `***`

## ⚠️ 重要行为规则

### Skill 文件操作权限
- **禁止**未经允许创建/修改/删除 skill 文件
- 只有永乐明确说「更新skill」「添加skill」时，才能操作 skills/ 目录下的文件
- 即使是创建空文件夹或骨架文档，也必须先问
- 把技能/方法论写在对话里就好，不要自作主张写进 SKILL.md
