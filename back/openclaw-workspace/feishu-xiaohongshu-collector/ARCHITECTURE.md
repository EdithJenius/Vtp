# ====================================================
# 小红书笔记 → 飞书多维表格 采集器 完整项目
# ====================================================

📁 feishu-xiaohongshu-collector/
├── README.md                    # 项目说明
├── package.json                 # 依赖配置
├── .env.example                 # 环境变量模板
└── src/
    ├── bot.js                   # 飞书机器人入口（监听消息→提取→写入）
    ├── extractor.js             # 小红书笔记提取器（Puppeteer方案）
    ├── simple-collector.js      # 简化版提取器（web_fetch方案，无需Puppeteer）
    ├── bitable-writer.js        # 飞书多维表格写入器
    └── cli.js                   # 命令行测试工具

## 三种使用方式

### 方式一：简化版（推荐先试）
```bash
# 无需安装 Puppeteer，直接通过页面源数据提取
node src/simple-collector.js https://www.xiaohongshu.com/explore/xxxxx
```

### 方式二：完整版（需安装 Puppeteer）
```bash
npm install
node src/cli.js https://www.xiaohongshu.com/explore/xxxxx --push
```

### 方式三：飞书机器人（自动处理）
```bash
# 配置好 .env 后
npm start
# 然后在飞书里把链接发给机器人即可
```

## 多维表格字段设计

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 笔记ID | 文本 | 小红书笔记唯一ID |
| 标题 | 文本 | 笔记标题 |
| 正文 | 文本 | 笔记文本内容 |
| 图片 | 附件(多图) | 高清图片预览（前3张） |
| 视频 | 文本/URL | 视频链接地址 |
| 视频文案 | 文本 | 自动语音转写（待实现） |
| 链接 | 链接 | 原文链接 |
| 作者 | 文本 | 发布者昵称 |
| 标签 | 文本 | 笔记标签 |
| 点赞 | 数字 | 点赞数 |
| 收藏 | 数字 | 收藏数 |
| 评论 | 数字 | 评论数 |
| 采集时间 | 日期 | 自动记录采集时间 |

## 小红书链接提取原理

```
Method A (推荐): Puppeteer 渲染页面
  → 打开小红书笔记页面
  → 等待 SPA 渲染完成
  → 提取 window.__INITIAL_STATE__ JSON
  → 解析笔记标题/正文/图片/视频/互动数据

Method B (备选): 页面元数据提取
  → 使用 og:title, og:image 等 Meta 标签
  → 提取页面中的 JSON 数据片段
  → 获取部分笔记内容

Method C (视频文案): 待实现
  → 提取视频 URL
  → 调用语音识别 API 转写文案
  → 或提取视频内嵌字幕
```

## 飞书机器人搭建步骤

### 1. 创建飞书应用
1. 打开 https://open.feishu.cn/app
2. 创建企业自建应用 → "小红书笔记采集"
3. 开启权限:
   - `im:message` - 消息读写
   - `im:message:send_as_bot` - 以机器人身份发送消息
   - `bitable:app` - 多维表格读写
   - `drive:drive` - 云文档（上传图片）
4. 发布应用

### 2. 配置事件订阅
- 事件: `im.message.receive_v1`
- 回调地址: `https://你的域名/webhook/event`
- 配置 Verify Token

### 3. 创建多维表格
- 新建一张多维表格
- 按上方字段设计创建各列
- 复制 app_token（URL中的）
- 复制 table_id

### 4. 部署运行
```bash
# 本地运行
npm run simple

# 云服务器运行
npm run start
```

## 替代方案

如果觉得自建服务器麻烦，也可以使用：
1. **飞书多维表格「高级权限」插件** — 飞书原生支持网页抓取
2. **简道云/明道云** — 低代码平台，有现成爬虫插件
3. **Python + Feishu SDK** — 用 Python 重写，部署更轻量
