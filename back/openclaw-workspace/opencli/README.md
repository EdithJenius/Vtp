# OpenCLI 快速入门

> 一句话：**让任何网站变成你的命令行。零配置，AI 原生。**

---

## 一、是什么

OpenCLI 是一个**浏览器桥接命令行工具**——你在 Chrome 里登录了某个网站，OpenCLI 就能通过浏览器扩展直接操作它，不需要 API Key，不需要爬虫。

```
你的终端 → opencli weibo hot → Chrome扩展 → 微博网页 → 返回热搜数据
```

---

## 二、安装与检查

```bash
# 确认已安装
which opencli

# 诊断浏览器连接
opencli doctor
```

如果 `doctor` 报错，需要在 Chrome 中安装 OpenCLI 浏览器扩展并保持运行。

---

## 三、基础用法

```bash
# 查看所有可用的站点和命令（150个平台）
opencli list

# 查看某个站点有哪些命令
opencli bilibili --help

# 查看某个命令的详细用法
opencli bilibili hot --help

# 执行命令
opencli weibo hot
opencli zhihu hot
opencli bilibili hot

# JSON 格式输出（便于 AI 处理）
opencli bilibili hot -f json

# CSV 格式输出（便于导入表格）
opencli bilibili hot -f csv

# 限制返回数量
opencli bilibili hot --limit 5
```

---

## 四、常用站点速查

### 热点监控
```bash
opencli weibo hot         # 微博热搜
opencli zhihu hot         # 知乎热榜
opencli bilibili hot      # B站热门
opencli toutiao hot       # 今日头条热榜
opencli 36kr hot          # 36氪热榜
```

### 内容采集
```bash
opencli xiaohongshu note <笔记链接>      # 小红书笔记详情
opencli xiaohongshu search "旅游"        # 小红书关键词搜索
opencli bilibili video <BV号>            # B站视频信息
opencli bilibili summary <BV号>          # B站视频AI总结
```

### 出行查询
```bash
opencli 12306 trains 北京 上海 2026-05-26    # 查火车
opencli 12306 price G123 北京 上海             # 查票价
opencli ctrip flight PEK SHA 2026-05-26      # 查机票
opencli ctrip hotel-search 天津 2026-05-26    # 查酒店
```

---

## 五、登录要求

| 标签 | 含义 |
|------|------|
| `public` | 无需登录，直接可用 |
| `cookie` | 需在 Chrome 中登录该网站 |
| `ui` | 需通过 UI 自动化，浏览器窗口可见 |

---

## 六、高级技巧

```bash
# 指定 Chrome 配置（多个登录帐号场景）
opencli --profile work weibo hot
opencli --profile personal xiaohongshu note ...

# 拉取小红书笔记内容用于营销素材
opencli xiaohongshu note https://www.xiaohongshu.com/explore/xxx -f json

# 获取 B站视频 AI 总结（省去看视频的时间）
opencli bilibili summary BV1xx411c7mD
```

---

## 七、相关文档

| 文件 | 说明 |
|------|------|
| `OpenCLI_平台大全.md` | 150个平台的完整命令列表 |
| `~/.openclaw/workspace/skills/opencli-usage/SKILL.md` | OpenCLI 用法技能文档 |
| `~/.openclaw/workspace/skills/opencli-browser/SKILL.md` | 浏览器自动化操作指南 |
| `~/.openclaw/workspace/skills/opencli-adapter-author/SKILL.md` | 编写新站点适配器指南 |
