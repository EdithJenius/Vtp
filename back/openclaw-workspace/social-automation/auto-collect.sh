#!/usr/bin/env bash
# Jarvis 自动数据采集脚本 - 定时执行
# 由 cron 或 heartbeat 触发

SOCIAL_DIR="$HOME/.openclaw/workspace/social-automation"
DATA_DIR="$SOCIAL_DIR/data"
VENV_DIR="/tmp/xhs-venv"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$DATA_DIR"
source "$VENV_DIR/bin/activate" 2>/dev/null

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🦾 Jarvis Auto Collect: 开始采集"

# 1. 小红书热门
echo ">>> 小红书热门"
xhs hot --yaml > "$DATA_DIR/xhs_hot_$TIMESTAMP.yaml" 2>/dev/null
xhs feed --yaml > "$DATA_DIR/xhs_feed_$TIMESTAMP.yaml" 2>/dev/null

# 2. 小红书搜索 (行业关键词)
for kw in "AI工具" "内容运营" "新媒体"; do
    echo ">>> 小红书搜索: $kw"
    xhs search "$kw" --page 1 --yaml > "$DATA_DIR/xhs_search_${kw}_$TIMESTAMP.yaml" 2>/dev/null
    sleep 1
done

# 3. 汇总统计
echo ">>> 生成统计摘要"
python3 -c "
import os, json, glob, yaml

data_dir = '$DATA_DIR'
files = glob.glob(os.path.join(data_dir, 'xhs_hot_*.yaml'))
if files:
    latest = max(files, key=os.path.getctime)
    with open(latest) as f:
        data = yaml.safe_load(f)
    items = data.get('data', {}).get('items', [])
    print(f'  小红书热门: {len(items)} 条笔记')
    for item in items[:3]:
        nc = item.get('note_card', {})
        title = nc.get('display_title', '无标题')[:30]
        user = nc.get('user', {}).get('nickname', '匿名')
        likes = nc.get('interact_info', {}).get('liked_count', '?')
        print(f'    📌 [{likes}❤️] {title} - @{user}')

files2 = glob.glob(os.path.join(data_dir, 'xhs_search_*_*.yaml'))
print(f'  搜索记录: {len(files2)} 个文件')
" 2>/dev/null

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 采集完成"
