工具恢复了！搜到了很实用的信息 ✅

---

## 🎬 剪映/CapCut GitHub 项目调研结果

**目前没有剪映官方公开的 API**，但有社区逆向项目可以程序化控制剪映：

### ⭐ 项目一：pyCapCut / pyJianYingDraft（3.4k ⭐）
| 项目 | 地址 |
|:----|:----|
| **pyJianYingDraft** | https://github.com/GuanYixuan/pyJianYingDraft |
| **pyCapCut**（新版） | https://github.com/GuanYixuan/pyCapCut |

**能做什么：**
- ✅ 加载剪映草稿模板（.draft）
- ✅ 替换素材（视频/图片/音频）
- ✅ 修改文本内容（换文案）
- ✅ 批量导出（自动渲染）
- ✅ 添加字幕、特效、转场、滤镜
- ✅ 视频混合模式、蒙版、关键帧
- 🔄 pyCapCut（新版）正在开发中，支持最新版 CapCut

**限制：** ⚠️ 剪映 6+ 草稿文件加密，仅支持 5.9 及以下直接操作；pyCapCut 可能支持新版

### ⭐ 项目二：jianying-protocol-service（37 ⭐）
| 项目 | 地址 |
|:----|:----|
| **剪映协议服务** | https://github.com/qingpingwang/jianying-protocol-service |

**能做什么：**
- HTTP API（FastAPI）→ 像个中间件
- 程序化创建视频项目
- 阿里云 OSS 集成，自动下载素材
- 适合写一个简单的 Web 后端，然后前端/AI 调 API 生成视频

---

### 💡 结合你们业务的 Workflow 设想

```
你写的脚本文案
     ↓
HeyGen 数字人口播素材
     ↓
pyCapCut 自动组装视频：
  1. 加载草稿模板（片头+片尾+BGM）
  2. 替换 HeyGen 生成的口播视频
  3. 替换文本字幕（Whisper + 你的文案）
  4. 加贴纸/花字
  5. 批量导出
     ↓
人工审片 → 小红书发布
```

**这套流程一旦跑通，每天 3-4 条视频的后期工作可能压缩到 30 分钟内。**

要不要我先 Fork 试跑一下 **pyCapCut**，看看能不能和你们的工作流结合？🦾