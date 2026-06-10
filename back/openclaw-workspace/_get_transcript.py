#!/usr/bin/env python3
"""
尝试从 Douyin 视频页面提取字幕/口播文案
方法：模拟浏览器请求调用 Douyin API
"""
import json, urllib.request, ssl, re, os, time

ctx = ssl._create_unverified_context()
COOKIE_FILE = os.path.expanduser("~/.openclaw/workspace/_dy_cookies.txt")

# 先从 Chrome 导出 douyin cookies 到文件
os.system('''
python3 -c "
import http.cookiejar, os, platform
# Try to get from a browser-saved cookie jar
cj = http.cookiejar.MozillaCookieJar()
try:
    cj.load(''' + repr(COOKIE_FILE).replace("'", "\"") + ''')
    print('loaded', len(cj))
except:
    print('no cookies yet')
" 2>/dev/null
''')

# 直接使用 opencli browser 执行 fetch 并返回结果
# eval 返回空，因为 fetch 是异步的...
# 改用同步 XMLHttpRequest
print("\n=== 尝试通过浏览器同步获取 ===")
