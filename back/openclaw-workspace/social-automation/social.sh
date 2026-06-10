#!/usr/bin/env bash
# Jarvis 社交平台自动化 - 一站式工具入口
# 用法: ./social.sh <command>

SOCIAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="/tmp/xhs-venv"

# 确保虚拟环境激活
source "$VENV_DIR/bin/activate" 2>/dev/null || {
    echo "❌ 虚拟环境未找到，请先安装工具"
    exit 1
}

case "${1:-help}" in
    # 小红书
    xhs-search)
        shift; xhs search "$@" ;;
    xhs-hot)
        xhs hot --yaml ;;
    xhs-feed)
        xhs feed --yaml ;;
    xhs-read)
        shift; xhs read "$@" --yaml ;;
    xhs-whoami)
        xhs whoami --yaml ;;
    
    # 抖音 - 使用 Cookie 的自定义脚本
    douyin-status)
        python3 -c "
import json
with open('$SOCIAL_DIR/douyin_cookies.json') as f:
    c = json.load(f)
print(f'🎵 抖音 Cookie 状态: {len(c)} 条')
print(f'    sessionid: {c.get(\"sessionid\", \"❌\")[:20]}...')
print(f'    登录时间: {c.get(\"login_time\", \"?\")}')
" ;;
    
    # 微博
    weibo-status)
        python3 -c "
import json
with open('$SOCIAL_DIR/weibo_cookies.json') as f:
    c = json.load(f)
print(f'🐦 微博 Cookie 状态: {len(c)} 条')
print(f'    SUB: {c.get(\"SUB\", \"❌\")[:30]}...')
" ;;
    
    # 状态总览
    status|dashboard)
        echo "╔══════════════════════════════════════╗"
        echo "║   🦾 Jarvis Social Automation       ║"
        echo "╠══════════════════════════════════════╣"
        echo "║  平台     │ 工具    │ 登录状态       ║"
        echo "╟───────────┼─────────┼────────────────╢"
        
        # 检查小红书
        if xhs whoami --yaml 2>/dev/null | grep -q "guest: false"; then
            NICK=$(xhs whoami --yaml 2>/dev/null | grep "nickname:" | cut -d' ' -f2)
            echo "║  小红书   │ xhs     │ ✅ $NICK      ║"
        else
            echo "║  小红书   │ xhs     │ ❌ 未登录      ║"
        fi
        
        # 检查抖音
        python3 -c "
import json
try:
    with open('$SOCIAL_DIR/douyin_cookies.json') as f:
        c = json.load(f)
    has_session = bool(c.get('sessionid', ''))
    print(f'║  抖音     │ -       │ {\"✅ 已登录\" if has_session else \"❌ 未登录\"}        ║')
except: print('║  抖音     │ -       │ ❌ 无 Cookie   ║')
"
        
        # 检查微博
        python3 -c "
import json
try:
    with open('$SOCIAL_DIR/weibo_cookies.json') as f:
        c = json.load(f)
    has_sub = bool(c.get('SUB', ''))
    print(f'║  微博     │ -       │ {\"✅ 已登录\" if has_sub else \"❌ 未登录\"}        ║')
except: print('║  微博     │ -       │ ❌ 无 Cookie   ║')
"
        
        # 检查 Twitter
        python3 -c "
import json
try:
    import browser_cookie3
    cj = browser_cookie3.chrome(domain_name='twitter.com')
    count = len(list(cj))
    print(f'║  Twitter  │ twitter │ ✅ Cookie {count}条  ║')
except: print('║  Twitter  │ twitter │ ❌ 未配置      ║')
"
        
        echo "╚══════════════════════════════════════╝"
        ;;
    
    # 一键采集 (demo)
    collect)
        echo "📡 一键采集所有平台热门数据..."
        echo "--- 小红书热门 ---"
        xhs hot --yaml | grep -E "display_title:|nickname:|liked_count:" | head -15
        echo ""
        echo "--- Twitter 时间线 (最近3条) ---"
        twitter feed --limit 3 --compact 2>/dev/null || echo "Twitter 未登录"
        ;;
    
    help|*)
        echo "🦾 Jarvis Social Automation"
        echo ""
        echo "用法: ./social.sh <command>"
        echo ""
        echo "📱 小红书:"
        echo "  xhs-search <query>  搜索笔记"
        echo "  xhs-hot             热门推荐"
        echo "  xhs-feed            推荐流"
        echo "  xhs-read <id>       读取笔记"
        echo "  xhs-whoami          个人信息"
        echo ""
        echo "🎵 抖音 (基础):"
        echo "  douyin-status       查看登录状态"
        echo ""
        echo "🐦 微博 (基础):"
        echo "  weibo-status        查看登录状态"
        echo ""
        echo "📊 系统:"
        echo "  status|dashboard    显示状态面板"
        echo "  collect             一键采集热门数据"
        echo ""
        echo "💡 先运行: source activate.sh"
        ;;
esac
