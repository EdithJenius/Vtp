# OpenCLI 支持平台大全

> 数据更新时间：2026-05-26
> 总计：**150 个站点**（859 个内置命令）+ **13 个外部 CLI**

---

## 一、平台分类速览

### 🔴 社交 / 社区（24个）

| 平台                      | 主要命令                                                                                                                                 | 登录要求          |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------- |
| **微博**                  | hot(热搜), feed(时间线), post, user, search, comments, delete, publish, favorites                                                         | ✅ Cookie      |
| **小红书**                 | feed(推荐流), note(笔记), search, user, comments, download, publish, creator-notes, creator-stats, notifications                          | ✅ Cookie      |
| **抖音**                  | user-videos, stats, publish, draft, hashtag, location, activities, delete                                                            | ✅ Cookie      |
| **B站**                  | hot(热门), video, search, comments, ranking, favorite, history, feed, summary(AI总结), download                                          | ✅ Cookie      |
| **知乎**                  | hot(热榜), question, answer, search, recommend, download, like, follow, comment, collection                                            | ✅ Cookie      |
| **Twitter/X**           | timeline, trending(趋势), search, profile, tweets, followers, post, reply, like, retweet, bookmark, download, dm, notifications, lists | ✅ Cookie + UI |
| **Reddit**              | frontpage, hot, popular, search, read, comment, reply, upvote, save, subscribe, user                                                 | ✅ Cookie      |
| **即刻(Jike)**            | feed, post, topic, search, user, comment, like, notifications, create, repost                                                        | ✅ Cookie + UI |
| **虎扑**                  | hot(热门), detail, search, reply, like, mentions                                                                                       | ✅ Public      |
| **豆瓣**                  | movie-hot, book-hot, top250, search, subject, download, reviews, marks                                                               | ✅ Cookie      |
| **Instagram**           | user, profile, followers, explore, search, like, comment, follow, download, story, reel, post, save                                  | ✅ Cookie + UI |
| **TikTok**              | explore, user, profile, search, like, comment, follow, download, live, notifications                                                 | ✅ Cookie      |
| **Facebook**            | feed, notifications, profile, search, friends, groups, events, memories, marketplace                                                 | ✅ Cookie      |
| **V2EX**                | hot(热门), latest, topic, nodes, member, notifications, replies, daily(签到)                                                             | ✅ Public      |
| **HackerNews**          | top, new, best, ask, show, jobs, search, read, user                                                                                  | ✅ Public      |
| **LinkedIn**            | timeline, people-search, search(职位), inbox, connect, salesnav                                                                        | ✅ Cookie + UI |
| **Bluesky**             | trending, feeds, profile, user, search, followers, following, thread                                                                 | ✅ Public      |
| **Discord**             | channels, servers, members, read, send, search, delete                                                                               | ✅ UI          |
| **知乎**                  | hot(热榜), question, answer, search                                                                                                    | ✅ Cookie      |
| **贴吧(Tieba)**           | hot, posts, read, search                                                                                                             | ✅ Public      |
| **一亩三分地(1point3acres)** | hot, forums, thread, search, user, notifications, latest                                                                             | ✅ Public      |
| **linux.do**            | feed, categories, topic, search, tags, user-posts                                                                                    | ✅ Cookie      |
| **即刻(Jike)**            | feed, post, topic, search                                                                                                            | ✅ Cookie      |
| **即刻(即刻)**              | feed, post, topic, search, notifications                                                                                             | ✅ Cookie      |

---

### 🛒 电商 / 购物（12个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **淘宝** | search, detail(详情), reviews, cart, add-cart | ✅ Cookie |
| **京东** | search, detail, item(详情+价格+规格), reviews, cart, add-cart | ✅ Cookie |
| **1688** | search, item, store, assets, download | ✅ Cookie |
| **小红书** | note, search, comments, publish | ✅ Cookie |
| **闲鱼** | search, item, chat, inbox, messages, reply, publish | ✅ Cookie |
| **什么值得买(SMZDM)** | search | ✅ Cookie |
| **Amazon** | search, product, offer, bestsellers, discussion, movers-shakers, new-releases | ✅ Cookie |
| **拼多多(Coupang)** | search, product, add-to-cart | ✅ Cookie |
| **Booking.com** | search(酒店) | ✅ Public |
| **携程(Ctrip)** | flight(机票搜索), hotel-search(酒店), hotel-suggest, search | ✅ Cookie |
| **大众点评** | search, shop(detail) | ✅ Cookie |
| **贝壳找房(KE)** | ershoufang(二手房), zufang(租房), xiaoqu(小区), chengjiao(成交) | ✅ Cookie |

---

### 💰 金融 / 投资 / 财经（14个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **东方财富** | quote(行情), kline(K线), rank(排行), sectors(板块), hot-rank, money-flow(资金流向), northbound(北向资金), longhu(龙虎榜), kuaixun(快讯), announcement(公告), convertible(可转债), etf, holders(股东) | ✅ Public |
| **雪球** | stock(行情), kline, hot(热门), hot-stock, search, watchlist, feed, comments, groups, fund | ✅ Cookie |
| **新浪财经** | news(快讯), stock(行情), rolling-news, stock-rank | ✅ Public |
| **同花顺** | hot-rank(热股榜) | ✅ Cookie |
| **通达信** | hot-rank(热搜榜) | ✅ Cookie |
| **Binance** | price, ticker, top, pairs, klines, depth, asks, gainers, losers, trades | ✅ Public |
| **CoinGecko** | top(市值排行), trending, coin, categories, derivatives, exchanges, global | ✅ Public |
| **Yahoo Finance** | quote | ✅ Cookie |
| **Barchart** | options(期权链), quote, greeks, flow(期权大单) | ✅ Cookie |
| **DefiLlama** | protocols(TVL排行), protocol | ✅ Public |
| **东方财富** | etf, convertible, holders | ✅ Public |
| **迈迈(Maimai)** | search-talents(人才搜索) | ✅ Cookie |
| **长桥(Longbridge)** | 外部CLI，需安装 | ✅ API |
| **Boss直聘** | search, joblist, detail, recommend, chatlist, chatmsg, greet, invite, resume, send, mark, stats, exchange, batchgreet | ✅ Cookie |

---

### 🎵 音乐 / 视频 / 娱乐（9个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **YouTube** | search, video, channel, comments, transcript(字幕), playlist, feed, history, like, subscribe | ✅ Cookie |
| **B站** | hot, video, search, comments, ranking, dynamic, favorite, history, feed, summary, download, subtitle | ✅ Cookie |
| **抖音** | user-videos, stats, publish, draft, hashtag, location | ✅ Cookie |
| **Spotify** | search, play, pause, next, prev, queue, volume, shuffle, repeat, status | ✅ OAuth |
| **Apple Podcasts** | search, top, episodes | ✅ Public |
| **Steam** | search, app, top-sellers | ✅ Public |
| **IMDb** | search, title, top, trending, reviews, person | ✅ Public |
| **TVmaze** | search, show | ✅ Public |
| **Pixiv** | search, ranking, illusts, user, detail, download | ✅ Cookie |

---

### 🤖 AI / 大模型 / 创作（15个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **ChatGPT** | ask, read, send, new, history, detail, image, status | ✅ Cookie |
| **Claude** | ask, read, send, new, history, detail, status | ✅ Cookie |
| **Gemini** | ask, image, new, deep-research | ✅ Cookie |
| **DeepSeek** | ask, read, send, new, history, detail, status | ✅ Cookie |
| **豆包(Doubao)** | ask, read, send, new, detail, history, meeting-summary, meeting-transcript | ✅ Cookie |
| **通义千问(Qwen)** | ask, read, send, new, history, detail, image, status | ✅ Cookie |
| **元宝(Yuanbao)** | ask, read, send, new, history, detail, status | ✅ Cookie |
| **Grok** | ask, read, send, new, history, detail, image, status | ✅ Cookie |
| **即梦AI(Jimeng)** | generate(文生图), history, new, workspaces | ✅ Cookie |
| **Suno** | generate(音乐生成), download, list, status | ✅ Cookie |
| **Yollomi** | generate(生图), edit(修图), remove-bg, upscale, restore, video(生视频), face-swap, background | ✅ Cookie |
| **NotebookLM** | list(笔记本), open, source-list, summary, note-list, notes-get, history | ✅ Cookie |
| **ChatWise** | ask, read, send, new, history, model, export, screenshot | ✅ UI |
| **Cursor** | ask, composer, read, send, new, history, model, export, extract-code | ✅ UI |
| **Codex** | ask, read, send, new, history, model, export, projects, extract-diff | ✅ UI |

---

### 📖 知识 / 学习 / 学术（16个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **维基百科** | search, summary, page, random, trending(热门阅读) | ✅ Public |
| **知乎** | hot, question, answer, search | ✅ Cookie |
| **arXiv** | search, paper, recent, author | ✅ Public |
| **Google Scholar** | search, profile, cite | ✅ Public |
| **PubMed** | search, article, author, citations, related | ✅ Public |
| **OpenReview** | search, paper, author, reviews, venue | ✅ Public |
| **百度学术** | search | ✅ Public |
| **万方数据** | search | ✅ Public |
| **中国知网(CNKI)** | search | ✅ Cookie |
| **豆瓣读书** | book-hot, top250, search, subject | ✅ Cookie |
| **OpenAlex** | search, work | ✅ Public |
| **MDN Web Docs** | search | ✅ Public |
| **Stack Overflow** | search, hot, read, tag, user, bounties, related, unanswered | ✅ Public |
| **DEV.to** | top, latest, tag, read, user | ✅ Public |
| **Medium** | feed, search, tag, user | ✅ Cookie |
| **Substack** | feed, publication, search | ✅ Public |

---

### 📰 资讯 / 新闻（13个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **微博热搜** | hot | ✅ Cookie |
| **百度热搜** | （web_fetch 抓取） | ✅ 网页 |
| **知乎热榜** | hot | ✅ Cookie |
| **今日头条(Toutiao)** | hot(热榜), articles | ✅ Public |
| **Google News** | news, trends, search | ✅ Public |
| **BBC News** | news, topic | ✅ Public |
| **Bloomberg** | main, markets, tech, economics, politics, opinions, feeds, news | ✅ Public |
| **Reuters(路透社)** | search, article-detail | ✅ Cookie |
| **36氪** | hot, news, search, article | ✅ Public |
| **HackerNews** | top, new, best, jobs, show, ask | ✅ Public |
| **新浪财经** | news(7x24快讯) | ✅ Public |
| **东财** | kuaixun(7x24快讯) | ✅ Public |
| **优设读报(UISDC)** | news(AI/设计新闻) | ✅ Public |

---

### 🏢 招聘 / 职场（4个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **Boss直聘** | search, joblist, detail, recommend, greet, invite, resume, chatlist, chatmsg, send, mark, stats, exchange | ✅ Cookie |
| **LinkedIn** | people-search, search(职位), inbox, timeline, connect | ✅ Cookie |
| **51Job(前程无忧)** | search, hot, detail, company | ✅ Cookie |
| **牛客(Nowcoder)** | hot, recommend, companies, jobs, experience, practice, search, salary, referral, topics | ✅ Public |

---

### 💻 开发者工具 / 技术（22个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **GitHub** | gh CLI(外部), issues, prs, repos | ✅ 外部CLI |
| **npm** | search, package, downloads | ✅ Public |
| **PyPI** | search, package, downloads | ✅ Public |
| **DockerHub** | search, image | ✅ Public |
| **Homebrew** | formula, cask, popular | ✅ Public |
| **Maven Central** | search, artifact | ✅ Public |
| **NuGet** | search, package | ✅ Public |
| **RubyGems** | search, gem | ✅ Public |
| **Crates.io** | search, crate | ✅ Public |
| **Packagist** | search, package | ✅ Public |
| **Flathub** | search, app | ✅ Public |
| **GoProxy** | module, versions | ✅ Public |
| **HuggingFace** | models, datasets, spaces, paper, top | ✅ Public |
| **Gitee** | search, trending, user | ✅ Public |
| **Stack Overflow** | search, hot, read, tag, user, bounties | ✅ Public |
| **arXiv** | search, paper, recent, author | ✅ Public |
| **DBLP** | search, paper, author, venue | ✅ Public |
| **RFC** | rfc(标准文档) | ✅ Public |
| **NVD(NIST)** | cve(漏洞查询) | ✅ Public |
| **OSV.dev** | query(漏洞), vulnerability | ✅ Public |
| **OpenFDA** | drug-label(药品标签), food-recall(食品召回) | ✅ Public |
| **Vercel / Cloudflare / Docker** | 外部CLI | ✅ 安装 |

---

### 🎓 生活 / 出行 / 其他（12个）

| 平台 | 主要命令 | 登录要求 |
|------|----------|---------|
| **12306** | trains(查车次), train(经停站), stations(车站搜索), price(票价), orders(订单), passengers(乘客), me | ✅ Public |
| **携程** | flight(机票), hotel-search, hotel-suggest, search | ✅ Cookie |
| **Booking.com** | search(酒店) | ✅ Public |
| **大众点评** | search, shop | ✅ Cookie |
| **贝壳找房** | ershoufang, zufang, xiaoqu, chengjiao | ✅ Cookie |
| **Wttr(天气)** | current, forecast | ✅ Public |
| **维基百科** | search, summary, page, random, trending | ✅ Public |
| **百度地图** | — | — |
| **学习通(Chaoxing)** | assignments(作业), exams(考试) | ✅ Cookie |
| **小鹅通** | courses, catalog, content, detail, play-url | ✅ Cookie |
| **Quark(夸克网盘)** | ls, mkdir, mv, rm, rename, save, share-tree | ✅ Cookie |
| **微信公众号** | download(导出文章), search, create-draft, drafts | ✅ Cookie |

---

### 🌍 外部 CLI（13个）

| CLI | 用途 | 状态 |
|-----|------|------|
| **discord-cli** | Discord 本地数据/消息 | ✅ 自动安装 |
| **docker** | Docker 容器管理 | ✅ 自动安装 |
| **dws** (钉钉工作台) | 钉钉消息/文档/日历/联系人 | ✅ 自动安装 |
| **gh** (GitHub CLI) | GitHub PR/Issue/Repo | ✅ 自动安装 |
| **lark-cli** (飞书) | 飞书消息/文档/表格/日历/任务(200+命令) | ✅ 已安装 |
| **longbridge** (长桥) | 港美股行情/交易 | ✅ 自动安装 |
| **ntn** (Notion) | Notion 页面/数据库/搜索 | ✅ 自动安装 |
| **obsidian** | Obsidian 笔记库管理 | ✅ 自动安装 |
| **tg-cli** (Telegram) | Telegram 本地消息/搜索 | ✅ 自动安装 |
| **vercel** | Vercel 部署/域名/环境变量 | ✅ 自动安装 |
| **wecom-cli** (企业微信) | 企业微信联系人/待办/会议/文档 | ✅ 自动安装 |
| **wrangler** | Cloudflare Workers/R2/D1 | ✅ 自动安装 |
| **wx-cli** (微信) | 微信本地消息/联系人/搜索 | ✅ 自动安装 |

---

## 二、旅游行业常用平台推荐

结合超值假期的业务，我推荐重点关注以下平台：

| 优先级 | 平台            | 理由               | 可用命令                                                        |
| --- | ------------- | ---------------- | ----------------------------------------------------------- |
| ⭐⭐⭐ | **小红书**       | 旅游种草主力，素材获取+趋势分析 | note, search, user, comments, download, feed, notifications |
| ⭐⭐⭐ | **B站**        | 旅游攻略视频，AI总结功能    | hot(热门), video, search, summary, favorite                   |
| ⭐⭐⭐ | **携程(Ctrip)** | 酒店/机票比价          | flight, hotel-search, hotel-suggest                         |
| ⭐⭐⭐ | **微博**        | 热搜监控，热点发现        | hot(热搜), feed, post, search                                 |
| ⭐⭐  | **抖音**        | 短视频旅行种草          | user-videos, hashtag, stats, publish                        |
| ⭐⭐  | **知乎**        | 深度旅游讨论           | hot(热榜), question, answer, search                           |
| ⭐⭐  | **12306**     | 火车票查询            | trains, train, stations, price                              |
| ⭐⭐  | **Instagram** | 国际目的地素材          | user, explore, search, download                             |
| ⭐⭐  | **微信公众号**     | 旅游推文导出           | download(导出文章), search                                      |
| ⭐   | **Twitter**   | 国际趋势监测           | trending, search, timeline                                  |
| ⭐   | **Booking**   | 国际酒店比价           | search                                                      |

---

## 三、登录要求说明

| 标签 | 含义 |
|------|------|
| `[public]` | 无需登录，直接可用 |
| `[cookie]` | 需在 Chrome 中登录该网站，OpenCLI 通过浏览器桥接使用登录态 |
| `[ui]` | 需通过 UI 自动化操作，浏览器必须可见 |
| `[intercept]` | 拦截网络请求获取数据 |
| `[local]` | 本地文件获取 |
| `[auto-install]` | 外部CLI，首次使用自动安装 |

---

## 四、常用命令速查

```bash
# 查看所有可用站点
opencli list

# 查看指定站点的命令
opencli <site> --help

# 查看某个命令的帮助
opencli <site> <command> --help

# 以 JSON 格式输出（方便 AI 分析）
opencli <site> <command> -f json

# 以 CSV 格式输出（方便导入表格）
opencli <site> <command> -f csv

# 诊断浏览器连接
opencli doctor

# 使用特定 Chrome 配置
opencli --profile <name> <site> <command>
```
