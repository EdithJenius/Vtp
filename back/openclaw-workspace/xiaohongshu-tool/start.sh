#!/bin/bash
# 启动内容工坊
cd "$(dirname "$0")"
echo "🚀 启动小红书内容工坊..."
python3 server.py &
sleep 2
open http://127.0.0.1:8899
echo "✅ 已打开 http://127.0.0.1:8899"
