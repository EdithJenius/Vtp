#!/bin/bash
# Jarvis Social Automation - 一键激活环境
# 使用: source ~/.openclaw/workspace/social-automation/activate.sh

SOCIAL_DIR="$HOME/.openclaw/workspace/social-automation"
VENV_DIR="/tmp/xhs-venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    export SOCIAL_AUTOMATION_DIR="$SOCIAL_DIR"
    export XHS_COOKIE="$SOCIAL_DIR/xiaohongshu_cookies.json"
    export DOUYIN_COOKIE="$SOCIAL_DIR/douyin_cookies.json"
    export WEIBO_COOKIE="$SOCIAL_DIR/weibo_cookies.json"
    
    echo "🦾 Jarvis Social Automation 已激活"
    echo ""
    echo "📱 可用工具:"
    echo "  xhs      - 小红书 CLI"
    echo "  twitter  - Twitter/X CLI"
    echo "  bili     - 哔哩哔哩 CLI"
    echo ""
    echo "📦 Cookie 已就绪:"
    echo "  小红书 ✅ | 抖音 ✅ | 微博 ✅"
    echo ""
    echo "💡 快速使用:"
    echo "  xhs search '关键词'        # 小红书搜索"
    echo "  xhs hot                    # 小红书热门"
    echo "  twitter feed               # Twitter 时间线"
    echo "  bili                       # B站工具"
    echo "  source deactivate          # 退出环境"
else
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
fi
