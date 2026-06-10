# HeyGen API 接入调研笔记

> 调研时间：2026-06-02
> 背景：在 video-generation 工坊中接入 HeyGen AI数字人口播视频生成

---

## 一、HeyGen 是什么

HeyGen 是一个 AI 视频生成平台，核心能力是**文本/音频 → 数字人口播视频**。传入一段文案，它就能生成一个数字人形象对着镜头说话的视频。

---

## 二、API 能力总览

| 操作 | API 端点 | 说明 |
|:----|:---------|:-----|
| 列出数字人形象 | `GET /v1/avatars` | 查看账号下可用 Avatar |
| 列出可用声音 | `GET /v1/voices` | 可过滤中文声音 |
| 文本 → 视频 | `POST /v2/video/generate` | 🎯 核心接口 |
| 音频 → 视频 | `POST /v2/video/generate` + voice.type=audio | 传录音文件对口型 |
| 查询生成状态 | `GET /v1/video_status.get?video_id=xxx` | 轮询渲染进度 |
| 列模板 | `GET /v1/templates` | 复用模板快速出片 |

---

## 三、API 调用方式

### 鉴权

```bash
export HEYGEN_API_KEY="***"
```

请求头带 `X-Api-Key` 即可，无需 OAuth。

### 文本→视频 (核心)

```python
payload = {
    "caption": False,
    "title": "视频标题",
    "video_inputs": [{
        "character": {
            "type": "avatar",
            "avatar_id": "avatar_id_xxx"
        },
        "voice": {
            "type": "text",
            "input_text": "口播文案内容",
            "voice_id": "voice_id_xxx"
        },
        "background": {"type": "color", "value": "#FFFFFF"}
    }],
    "test": False,       # True = 带水印免费模式
}
POST https://api.heygen.com/v2/video/generate
```

### 查询状态

```
GET https://api.heygen.com/v1/video_status.get?video_id=xxx
```

返回 `status: completed` 时即可获取视频下载链接。

---

## 四、接入到 video-generation 工坊的方案

### 流程图

```
文案产出（④ 文案产出表）
   │
   ├→ ① 传统路线：素材匹配 + 画面分割 + 下载
   │
   └→ ② AI路线：HeyGen 文本→数字人口播视频
         选形象 → 选声音 → 提交API → 等待渲染 → 下载成品
```

### 已完成的脚本

路径：`skills/video-generation/scripts/heygen_api.py`

```bash
# 查看可用形象
python3 heygen_api.py list-avatars

# 查看可用声音
python3 heygen_api.py list-voices

# 从文案生成视频（单条）
python3 heygen_api.py generate --text "口播文案" --title "标题" --wait

# 从文案文件生成
python3 heygen_api.py script --script /tmp/transcript.txt --wait

# 查询状态
python3 heygen_api.py status --video-id "xxx"
```

---

## 五、人工网页创作 vs API 接入对比

| 环节 | 网页手动 | API 自动化 | 优化点 |
|:----|:---------|:----------|:------|
| 文案准备 | 手动复制粘贴 | 自动从文案库取 | ✅ 省搬运步骤 |
| 选形象 | 翻列表手动选 | 脚本自动选 | ✅ 批量省时间 |
| 填文案 | 粘到文本框 | 脚本传参 | ✅ 可循环 |
| 下载 | 手动点下载 | 自动下载到目录 | ✅ 省人工盯屏 |
| 批量处理 | ❌ 一条一条做 | ✅ for 循环 | ✅ 量越大优势越明显 |
| 流程打通 | ❌ 独立操作 | ✅ 文案→HeyGen→入库 | ✅ 数据不落地 |
| 精细调整 | ✅ 预览微调方便 | ⚠️ 需反复调参 | 网页胜出 |

**结论：单条用网页，多条上 API，先网页试效果再脚本固化。**

---

## 六、建议的上手路径

```
阶段1：网页手动跑 1-2 条 → 确认效果满意
          ↓
阶段2：API 单条验证 → curl / 脚本跑通
          ↓
阶段3：小批量 3-5 条 → 验证流程
          ↓
阶段4：全量批量 → 一梭子搞定
```

---

## 七、注意事项

| 注意点 | 说明 |
|:-------|:-----|
| API Key | 需要真实 Key，占位符 `"your-api-key-here"` 不可用 |
| 费用 | HeyGen 按视频时长计费，需关注额度 |
| 网络 | 国内可能需要代理才能访问 `api.heygen.com` |
| 生成时间 | 每条视频约 2-5 分钟渲染 |
| 刚开始不建议批量 | 调参没经验时批量跑，出问题排查困难 |

---

## 八、相关链接

- **脚本文件：** `skills/video-generation/scripts/heygen_api.py`
- **SKILL.md：** `skills/video-generation/SKILL.md` (v1.3)
- **视频文案库：** https://icns51dkxerg.feishu.cn/base/JbfSbQjyXaA4vssVABNcm5AhnKh
