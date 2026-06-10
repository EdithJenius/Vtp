# 🦾 Jarvis 完整备份 - 2026-06-10

> 此 MacBook Pro 已归还原主。此备份用于在新电脑上还原 Jarvis 全部配置和信息。

## 备份结构

```
back/
├── README.md                         ← 本说明文件
├── openclaw-workspace/               ← ~/.openclaw/workspace/ 完整备份
│   ├── AGENTS.md / SOUL.md          ← Jarvis 人格和身份
│   ├── MEMORY.md                     ← 长时记忆（重要！）
│   ├── USER.md / IDENTITY.md        ← 用户信息
│   ├── HEARTBEAT.md                 ← 心跳检测
│   ├── TOOLS.md                     ← 工具配置
│   ├── memory/                      ← 每日记忆日志
│   ├── skills/                      ← 自定义技能
│   ├── projects/                    ← 项目文件
│   ├── archive/                     ← 历史归档
│   └── ...其他辅助文件
├── openclaw-config/                  ← ~/.openclaw/ 配置
│   ├── config.yaml
│   ├── accounts.json
│   ├── .env
│   └── plugins/
├── stome/Grav/                       ← Obsidian 知识库（已上传）
└── .gitignore
```

## 🔧 在新电脑上还原完整 Jarvis

### 前置条件
- 安装 [Node.js](https://nodejs.org/) ≥ 18
- 安装 Git
- 配置好 SSH 密钥（从旧电脑 `~/.ssh/` 复制）

### 步骤

```bash
# 1. 克隆仓库
git clone git@github.com:EdithJenius/Vtp.git
cd Vtp

# 2. 安装 OpenClaw
npm install -g openclaw

# 3. 还原 OpenClaw 配置
mkdir -p ~/.openclaw
cp -R back/openclaw-config/* ~/.openclaw/
cp .env ~/.openclaw/ 2>/dev/null  # 如果存在

# 4. 还原工作区（替换默认 workspace）
cd ~/.openclaw
mv workspace workspace.bak 2>/dev/null  # 备份旧的
ln -s /path/to/Vtp/back/openclaw-workspace workspace
# 或直接复制:
# cp -R /path/to/Vtp/back/openclaw-workspace ~/.openclaw/workspace

# 5. 启动 Gateway
openclaw gateway start
```

### 额外还原项（手动）
| 项目 | 位置 | 说明 |
|------|------|------|
| SSH 密钥 | `~/.ssh/` | 从旧电脑复制 `id_ed25519` / `id_rsa` |
| Git 配置 | `~/.gitconfig` | 从旧电脑复制 |
| Obsidian | `stome/Grav/` | 拷贝到新电脑 `/Applications/stome/Grav/` |
| YouTube 素材 | 需重新下载 | `xhs_downloads/` 太大未备份 |
| Python venv | 需重新创建 | `xiaohongshu-cli/.venv` 未备份 |

## ⚠️ 提醒
- 新电脑首次启动 OpenClaw 后，Jarvis 需要重新连接飞书、微信等渠道
- MEMORY.md 已包含所有长时记忆，AGENTS.md/SOUL.md 包含人格配置
- 还原后 Jarvis 应该能认出你并继续正常工作 🦾
