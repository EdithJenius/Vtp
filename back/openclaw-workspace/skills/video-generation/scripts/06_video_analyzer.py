#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频智能分析脚本:
1. 获取 YouTube 章节信息
2. FFmpeg 场景检测 → 自动切分片段
3. 抽帧生成缩略图索引
4. 更新 Bitable 素材表
"""
import json, os, sys, subprocess, time, re

YT = "/Library/Frameworks/Python.framework/Versions/3.12/bin/yt-dlp"
FFMPEG = "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"
FFPROBE = FFMPEG  # use ffmpeg for probe too

# ===== 测试视频（之前下的Serengeti 1小时视频）=====
video_path = os.path.expanduser("~/.openclaw/workspace/xhs_downloads/yt_safari/tanzania_720p_full.mp4")
video_url = "https://www.youtube.com/watch?v=DEAcPVg8V7U"

if not os.path.exists(video_path):
    print("下载测试视频...")
    subprocess.run([YT, "--no-check-certificate", "-f", "18", "-o", video_path, video_url], timeout=300)

print(f"视频: {video_path}")
print(f"大小: {os.path.getsize(video_path)/1024/1024:.0f} MB", flush=True)

# ===== 1. 获取元数据 + 章节信息 =====
print("\n=== 1. 获取章节信息 ===", flush=True)
# ffmpeg -i 输出已包含章节和时长信息

# 用 ffmpeg 读取元数据获取章节
meta_result = subprocess.run([FFMPEG, "-i", video_path], capture_output=True, text=True, timeout=30)
stderr = meta_result.stderr

# 提取章节信息
chapters = []
chapter_pattern = re.compile(r"Chapter #(\d+):(\d+): start (\d+\.?\d*), end (\d+\.?\d*)")
title_pattern = re.compile(r"title\s+:\s(.+)")

lines = stderr.split("\n")
i = 0
while i < len(lines):
    m = chapter_pattern.search(lines[i])
    if m:
        ch = {"start": float(m.group(3)), "end": float(m.group(4)), "title": f"片段 {len(chapters)+1}"}
        if i+1 < len(lines):
            tm = title_pattern.search(lines[i+1])
            if tm:
                ch["title"] = tm.group(1).strip()
                i += 1
        chapters.append(ch)
    i += 1

# 提取时长
duration = 0
dur_match = re.search(r"Duration: (\d+):(\d+):(\d+)\.(\d+)", stderr)
if dur_match:
    h, m, s, _ = dur_match.groups()
    duration = int(h)*3600 + int(m)*60 + int(s)

print(f"视频时长: {duration//3600}:{(duration%3600)//60}:{duration%60}", flush=True)

if chapters:
    print(f"发现 {len(chapters)} 个章节:", flush=True)
    for ch in chapters:
        print(f"  {fmt_time(ch['start'])} - {fmt_time(ch['end'])}: {ch['title']}", flush=True)
else:
    print("无章节信息，将使用场景检测", flush=True)

def fmt_time(sec):
    s = float(sec)
    return f"{int(s//60)}:{int(s%60):02d}"

# ===== 2. FFmpeg 场景检测 =====
print("\n=== 2. 场景检测 ===", flush=True)
scene_threshold = 0.3  # 灵敏度：越低越敏感

result = subprocess.run(
    [FFMPEG, "-i", video_path, "-filter:v",
     f"select='gt(scene,{scene_threshold})',showinfo",
     "-f", "null", "-"],
    capture_output=True, text=True, timeout=120)

# 解析场景变更时间点
scene_times = []
for line in result.stderr.split("\n"):
    if "pts_time:" in line:
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1))
            if t > 2:  # 跳过开头几秒
                scene_times.append(t)

scene_times = sorted(set([round(t, 1) for t in scene_times]))
print(f"检测到 {len(scene_times)} 个场景切换点", flush=True)

# ===== 3. 构建场景片段列表 =====
print("\n=== 3. 构建片段列表 ===", flush=True)
segments = []

# 如果有章节，用章节划分
if chapters:
    for ch in chapters:
        dur = float(ch["end"]) - float(ch["start"])
        if dur > 10:  # 只保留10秒以上的片段
            segments.append({
                "start": fmt_time(ch["start"]),
                "end": fmt_time(ch["end"]),
                "duration": f"{dur:.0f}s",
                "title": ch["title"],
                "type": "章节"
            })
else:
    # 用场景检测时间点合并成片段
    prev = 0
    for t in scene_times:
        dur = t - prev
        if 15 < dur < 600:  # 15秒~10分钟的片段
            segments.append({
                "start": fmt_time(prev),
                "end": fmt_time(t),
                "duration": f"{dur:.0f}s",
                "title": f"场景 {len(segments)+1}",
                "type": "场景"
            })
        prev = t

print(f"共 {len(segments)} 个片段:", flush=True)
for s in segments[:20]:
    print(f"  {s['start']} - {s['end']} ({s['duration']}): {s['title']}", flush=True)
if len(segments) > 20:
    print(f"  ... 还有 {len(segments)-20} 个片段", flush=True)

# ===== 4. 抽帧生成缩略图索引 =====
print("\n=== 4. 生成缩略图索引 ===", flush=True)
thumb_dir = os.path.join(os.path.dirname(video_path), "thumbs")
os.makedirs(thumb_dir, exist_ok=True)

# 每30秒抽一帧
interval = 30
frame_count = max(int(duration / interval), 1) if duration > 0 else 1

print(f"视频总长 {duration:.0f}s，每{interval}s抽帧，约{frame_count}张", flush=True)

# 抽取关键帧（前5张示例）
for i in range(min(5, frame_count)):
    t = i * interval
    out = os.path.join(thumb_dir, f"frame_{i:04d}_{t}s.jpg")
    if not os.path.exists(out):
        subprocess.run([FFMPEG, "-ss", str(t), "-i", video_path,
                        "-vframes", "1", "-q:v", "2", out],
                       capture_output=True, timeout=30)
    print(f"  [{fmt_time(t)}] thumb_{i:04d}.jpg", flush=True)

print(f"\n✅ 分析完成!", flush=True)
print(f"缩略图目录: {thumb_dir}", flush=True)
print(f"""
📊 分析结果:
   视频全长: {fmt_time(duration)}
   章节数: {len(chapters)}
   场景切换点: {len(scene_times)}个
   生成片段: {len(segments)}个
   缩略图: 每{interval}s一张
""", flush=True)
