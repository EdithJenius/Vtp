#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v2: 利用 YouTube 章节信息 + 抽帧缩略图做素材智能切割
"""
import json, os, sys, subprocess, re

YT = "/Library/Frameworks/Python.framework/Versions/3.12/bin/yt-dlp"
FFMPEG = "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"

def fmt_time(sec):
    return f"{int(sec//3600):02d}:{int(sec%3600//60):02d}:{int(sec%60):02d}" if sec >= 3600 else f"{int(sec//60):02d}:{int(sec%60):02d}"

# ===== 测试用视频 =====
test_videos = [
    {"title": "Tanzania Serengeti 4K", "url": "https://www.youtube.com/watch?v=DEAcPVg8V7U", "path": os.path.expanduser("~/.openclaw/workspace/xhs_downloads/yt_safari/tanzania_720p_full.mp4")},
]

rv = test_videos[0]
print(f"📹 {rv['title']}", flush=True)
print(f"🔗 {rv['url']}", flush=True)

# ===== 1. 从 YouTube 获取章节信息 =====
print(f"\n=== 1. 获取章节信息 ===", flush=True)
result = subprocess.run([YT, "--no-check-certificate", "--dump-json", rv["url"]],
                        capture_output=True, text=True, timeout=60)
d = json.loads(result.stdout.strip().split("\n")[0])
youtube_chapters = d.get("chapters", [])

if youtube_chapters:
    print(f"✅ YouTube 提供 {len(youtube_chapters)} 个章节:", flush=True)
    for ch in youtube_chapters:
        print(f"  {fmt_time(ch['start_time'])} - {fmt_time(ch['end_time'])} ({ch['end_time']-ch['start_time']:.0f}s): {ch['title']}", flush=True)
else:
    print("⚠️ 无章节信息", flush=True)

# ===== 2. 下载视频（如果还没有）=====
video_path = rv["path"]
if not os.path.exists(video_path):
    print("\n=== 下载视频 ===", flush=True)
    subprocess.run([YT, "--no-check-certificate", "-f", "18", "-o", video_path, rv["url"]], timeout=300)
    print("下载完成", flush=True)

# ===== 3. 抽帧生成缩略图 =====
print(f"\n=== 2. 按章节抽关键帧 ===", flush=True)
thumb_dir = os.path.join(os.path.dirname(video_path), "thumbs_chapters")
os.makedirs(thumb_dir, exist_ok=True)

if youtube_chapters:
    for ch in youtube_chapters:
        mid_time = (ch["start_time"] + ch["end_time"]) / 2
        title_clean = re.sub(r'[^\w\s-]', '', ch["title"])[:20]
        thumb_file = os.path.join(thumb_dir, f"{title_clean}_{int(mid_time)}s.jpg")
        if not os.path.exists(thumb_file):
            subprocess.run([FFMPEG, "-ss", str(mid_time), "-i", video_path,
                           "-vframes", "1", "-q:v", "3", "-vf", "scale=320:180", thumb_file],
                          capture_output=True, timeout=30)
        print(f"  [{fmt_time(mid_time)}] {ch['title'][:30]}: {os.path.basename(thumb_file)}", flush=True)

# ===== 4. 输出分析报告 =====
print(f"\n{'='*60}", flush=True)
print(f"📊 分析报告", flush=True)
print(f"{'='*60}", flush=True)

if youtube_chapters:
    print(f"\n推荐素材片段:", flush=True)
    for ch in youtube_chapters:
        dur = ch["end_time"] - ch["start_time"]
        print(f"  [{fmt_time(ch['start_time'])} → {fmt_time(ch['end_time'])}] ({dur:.0f}s)", flush=True)
        print(f"    📝 {ch['title']}", flush=True)
        print(f"    📎 缩略图: thumbs_chapters/{re.sub(r'[^\w\s-]', '', ch['title'])[:20]}_{int((ch['start_time']+ch['end_time'])/2)}s.jpg", flush=True)

print(f"\n✅ 分析完成！共 {len(youtube_chapters) if youtube_chapters else 0} 个片段", flush=True)
print(f"缩略图目录: {thumb_dir}", flush=True)
