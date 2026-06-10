# OpenCLI 完整使用手册

> 版本：v1.8.0 · 更新日期：2026-05-25
> 项目地址：https://github.com/jackwener/OpenCLI

---

## 一、OpenCLI 是什么

OpenCLI 是一个开源命令行工具，核心能力：**把任何网站变成 CLI 接口，让 AI agent 通过你的已登录浏览器操作网页。**

```
一句话：装一个 Chrome 扩展 + 一个 npm 包 = 用命令行操控所有网站
```

### 核心能力

| 能力 | 说明 |
|------|------|
| 🖥️ **CLI Hub** | 统一入口管理所有工具（gh/docker/lark-cli/小红书/B站/知乎…） |
| 🌐 **Browser Bridge** | Chrome 扩展桥接，通过你的已登录浏览器操作网页 |
| 🤖 **AI Agent 接口** | AI 可以直接通过 CLI 操作你的浏览器 |
| 📦 **100+ 适配器** | 小红书、B站、知乎、Twitter、LinkedIn 等都有现成命令 |
| 📥 **下载工具** | 支持小红书/B站/Twitter 等平台的图片/视频下载 |

---

## 二、安装

### 2.1 安装 CLI

```bash
npm install -g @jackwener/opencli
```

验证安装：

```bash
opencli --version
# 输出: 1.8.0
```

### 2.2 安装 Chrome 扩展

1. 打开 Chrome 浏览器
2. 前往 [Chrome Web Store](https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk)
3. 点击「添加至 Chrome」
4. 确认安装

### 2.3 验证连接

```bash
opencli doctor
```

正常输出示例：
```
opencli v1.8.0 doctor (node v24.15.0)

[OK] Daemon: running on port 19825 (v1.8.0)
[OK] Extension: connected (v1.0.15)

Profiles:
  • aqtgr7uk: connected v1.0.15
[OK] Connectivity: connected in 1.5s

Everything looks good!
```

### 2.4 登录目标平台

某些功能需要先登录目标网站。在 Chrome 中打开以下网站并登录：

| 平台 | 登录要求 | 影响的功能 |
|------|---------|-----------|
| 小红书 | 需要登录 | search / comments / notifications |
| B站 | 无需登录 | hot / search 可用，history 需登录 |
| 知乎 | 需要登录 | hot / search / question |
| Twitter/X | 需要登录 | trending / timeline / post |

---

## 三、命令结构

### 通用格式

```bash
opencli <平台> <命令> [选项]
```

### 通用选项

| 选项 | 简写 | 说明 |
|------|------|------|
| `--limit N` | `-n N` | 限制返回条数 |
| `--format <格式>` | `-f <格式>` | 输出格式：table(默认) / json / yaml / md / csv |
| `--output <目录>` | `-o <目录>` | 下载文件输出目录 |
| `--verbose` | `-v` | 详细输出 |

---

## 四、平台命令大全

### 4.1 小红书（xiaohongshu）

```bash
# 首页推荐流
opencli xiaohongshu feed --limit 10

# 搜索笔记
opencli xiaohongshu search "商务舱" --limit 20

# 查看笔记详情（需要完整URL，含 xsec_token）
opencli xiaohongshu note "https://www.xiaohongshu.com/search_result/xxx?xsec_token=xxx"

# 查看笔记评论（需要完整URL）
opencli xiaohongshu comments "https://www.xiaohongshu.com/search_result/xxx?xsec_token=xxx" --limit 10

# 查看用户主页笔记
opencli xiaohongshu user "用户ID" --limit 20

# 查看通知（需要登录）
opencli xiaohongshu notifications

# 下载笔记中的图片/视频
opencli xiaohongshu download "笔记URL" --output ./downloads

# 发布笔记（需要登录）
opencli xiaohongshu publish
```

**注意：** 笔记详情和评论需要传完整的带 `xsec_token` 的 URL。从搜索结果中复制即可。

### 4.2 B站（bilibili）

```bash
# 热门视频
opencli bilibili hot --limit 10

# 搜索
opencli bilibili search "商务" --limit 10

# 查看视频详情
opencli bilibili video BV1xxx

# 查看视频评论
opencli bilibili comments BV1xxx --limit 20

# 查看历史记录（需要登录）
opencli bilibili history --limit 10

# 下载视频
opencli bilibili download BV1xxx --output ./downloads

# 排行榜
opencli bilibili ranking --limit 10
```

### 4.3 知乎（zhihu）

```bash
# 热搜
opencli zhihu hot --limit 10

# 搜索
opencli zhihu search "商务舱" --limit 10

# 查看问题详情
opencli zhihu question "问题ID"

# 查看回答
opencli zhihu answer "回答ID"

# 收藏/点赞（需要登录）
opencli zhihu like "内容ID"
opencli zhihu favorite "内容ID"
```

### 4.4 Twitter / X

```bash
# 热门趋势
opencli twitter trending --limit 10

# 搜索
opencli twitter search "关键词" --limit 20

# 时间线
opencli twitter timeline --limit 20

# 查看用户推文
opencli twitter tweets "用户名" --limit 20

# 发推
opencli twitter post "内容"

# 下载媒体
opencli twitter download "用户名" --limit 10 --output ./downloads

# 查看通知
opencli twitter notifications --limit 20
```

### 4.5 其他平台

```bash
# HackerNews
opencli hackernews top --limit 10

# Reddit
opencli reddit hot --limit 10

# LinkedIn
opencli linkedin search "关键词" --limit 10

# 12306 查列车
opencli 12306 trains "北京" "上海" "2026-05-25"

# 1688 搜商品
opencli 1688 search "商务旅行箱" --limit 10
```

---

## 五、AI Agent 集成

### 5.1 安装 Skills

```bash
npx skills add jackwener/opencli
```

### 5.2 可用 Skills

| Skill | 用途 | 使用场景 |
|-------|------|---------|
| **opencli-browser** | AI 驱动浏览器操作 | 填表单、点按钮、提取数据 |
| **opencli-adapter-author** | 编写新网站适配器 | 自定义新平台命令 |
| **opencli-autofix** | 修复故障适配器 | 命令失效时自动修复 |
| **opencli-usage** | 命令参考 | 快速查看所有命令 |

### 5.3 在 CRM 中的使用场景

与 ValueTrips-CRM 结合的使用方案：

| 场景 | 命令 | 用途 |
|------|------|------|
| 竞品监测 | `opencli xiaohongshu search "航司卡"` | 监测小红书上的航司卡内容 |
| 热点捕捉 | `opencli bilibili hot \| opencli zhihu hot` | 捕捉今日热点，分析商机 |
| 评论分析 | `opencli xiaohongshu comments <URL>` | 分析用户对航司卡/商务舱的真实反馈 |
| 用户调研 | `opencli xiaohongshu search "蜜月 商务舱"` | 搜索蜜月出行相关需求 |
| 内容灵感 | `opencli xiaohongshu search "旅行 攻略"` | 参考热门笔记获取内容方向 |

---

## 六、输出格式

### 表格（默认）

```bash
opencli bilibili hot
```

### JSON（适合 AI 处理）

```bash
opencli bilibili hot -f json
```

### CSV（适合 Excel）

```bash
opencli bilibili hot -f csv
```

### Markdown

```bash
opencli bilibili hot -f md
```

---

## 七、进阶用法

### 7.1 多 Chrome 账号

```bash
# 列出已连接的 Chrome 账号
opencli profile list

# 重命名
opencli profile rename <id> work

# 使用指定账号
opencli --profile work browser state
```

### 7.2 输出到文件

```bash
opencli xiaohongshu search "商务舱" -f json > xhs_results.json
```

### 7.3 安装插件

```bash
# 安装社区插件
opencli plugin install github:user/opencli-plugin-xxx

# 查看已安装
opencli plugin list

# 更新所有插件
opencli plugin update --all
```

### 7.4 注册本地工具

```bash
# 把本地 CLI 工具注册到 OpenCLI
opencli external register lark-cli
opencli external register gh
```

---

## 八、环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENCLI_DAEMON_PORT` | 19825 | 守护进程端口 |
| `OPENCLI_PROFILE` | — | 指定 Chrome 账号 |
| `OPENCLI_WINDOW` | 默认 | 窗口模式（foreground/background）|
| `OPENCLI_VERBOSE` | false | 是否开启详细日志 |
| `OPENCLI_BROWSER_COMMAND_TIMEOUT` | 60 | 浏览器命令超时（秒）|

---

## 九、常见问题

**Q: `opencli doctor` 显示 Extension not connected？**
A: 检查 Chrome 扩展是否已开启。打开 `chrome://extensions` 确认 OpenCLI 扩展已启用。

**Q: search 返回 AUTH_REQUIRED？**
A: 在 Chrome 中打开该网站并登录即可。

**Q: note / comments 报错说需要完整URL？**
A: 从搜索结果或笔记列表复制完整的带 `xsec_token` 的 URL 传入。

**Q: 命令返回空数据？**
A: 可能是登录 session 过期了，在 Chrome 中重新登录目标网站。

**Q: 可以同时用多个 Chrome 账号吗？**
A: 可以。`opencli profile list` 查看已连接的 profiles，`opencli profile use <name>` 切换。

---

## 十、更新与卸载

```bash
# 更新到最新版
npm update -g @jackwener/opencli

# 更新 Chrome 扩展（Chrome 会自动更新）

# 卸载
npm uninstall -g @jackwener/opencli
# 同时在 chrome://extensions 中移除 OpenCLI 扩展
```

---

> 本文档对应 OpenCLI v1.8.0，更多信息请查看 [GitHub 项目](https://github.com/jackwener/OpenCLI)
