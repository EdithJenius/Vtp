#!/usr/bin/env python3
"""
坦桑尼亚·素材自动切割 + EDL/FCPXML 时间线导出脚本

功能：
1. 从 Bitable 读取素材匹配表的 20 个镜头
2. 按章节自动切割主视频为独立片段
3. 命名格式：产品简称_画面内容_起始时间.mp4
4. 自动生成 EDL (CMX3600) + FCPXML + 批导入CSV

使用方法：
  python3 auto_cut_and_edl.py [--dry-run]

前置条件：
  - 主视频已下载到 ../raw/tanzania_serengeti_4k.mp4
  - 飞书 API 凭证可用
"""

import urllib.request
import json
import time
import os
import subprocess
import re
from pathlib import Path

# ─── 飞书配置 ───
APP_ID = "cli_aa870c0ca5e15cd6"
APP_SECRET = "jfof8OwjPLORVhWrc5d08bEQzegcdGUE"
APP_TOKEN = "DGFnboTGEauc2QsoA2WcJ58Dnsf"
MATERIAL_TABLE = "tblo90MvAb4EKMeo"  # ⑤ 素材匹配

# ─── 路径配置 ───
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "raw"
CLIPS_DIR = BASE_DIR / "clips"
OUT_DIR = BASE_DIR / "timeline"
FFMPEG = "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"

# ─── 产品标识 ───
PRODUCT_SHORT = "坦桑尼亚狂野海岛"

# ─── API 工具 ───
def api_call(method, url, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data, ensure_ascii=False).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

def get_token():
    r = api_call("POST", "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", {
        "app_id": APP_ID, "app_secret": APP_SECRET
    })
    return r.get("tenant_access_token", "")

def get_all_records(token, table_id):
    all_recs = []
    page_token = None
    while True:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records?page_size=500"
        if page_token:
            url += f"&page_token={page_token}"
        r = api_call("GET", url, token=token)
        data = r.get("data", {})
        items = data.get("items", [])
        all_recs.extend(items)
        if not data.get("has_more"):
            break
        page_token = data.get("page_token", "")
        time.sleep(0.2)
    return all_recs

# ─── 从画面分割字段解析章节时间 ───
def parse_chapter_time(chapter_text):
    """从 '[00:00-05:59] (359s) 狂野坦桑尼亚 - Wild Tanzania' 解析时间"""
    m = re.match(r'\[(\d+):(\d+)-(\d+):(\d+)\]', chapter_text)
    if not m:
        return None, None
    start_sec = int(m.group(1)) * 60 + int(m.group(2))
    end_sec = int(m.group(3)) * 60 + int(m.group(4))
    return start_sec, end_sec

def seconds_to_timecode(s):
    """秒 → 时:分:秒:帧 (25fps)"""
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}:00"

def seconds_to_hms(s):
    """秒 → HHMMSS"""
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}{m:02d}{sec:02d}"

def sanitize_filename(name):
    """清理文件名中的非法字符"""
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    name = name.strip()[:30]  # 截断过长
    return name

# ─── 主流程 ───
def main(dry_run=False):
    TOKEN = get_token()
    print("🔑 Token 获取成功")
    
    # 1. 获取素材记录
    print("\n📥 读取素材匹配表...")
    records = get_all_records(TOKEN, MATERIAL_TABLE)
    print(f"   共 {len(records)} 条记录")
    
    # 2. 解析每个镜头的起始/结束时间
    parsed = []
    for rec in records:
        fields = rec.get("fields", {})
        shot_num = int(fields.get("镜头编号", 0))
        desc = fields.get("画面描述", "")
        chapter_text = fields.get("画面分割", "") or ""
        material_type = fields.get("素材类型", "")
        
        start_sec, end_sec = parse_chapter_time(chapter_text)
        
        if start_sec is not None and chapter_text:
            parsed.append({
                "shot_num": shot_num,
                "desc": desc,
                "type": material_type,
                "start_sec": start_sec,
                "end_sec": end_sec,
                "duration": end_sec - start_sec,
                "chapter_raw": chapter_text
            })
    
    print(f"\n   成功解析 {len(parsed)} 个镜头的时间信息")
    
    # 3. 检查原始视频
    source_video = RAW_DIR / "tanzania_serengeti_4k.mp4"
    if not source_video.exists():
        print(f"\n⚠️  主视频未下载完成: {source_video}")
        print(f"   将生成时间线文件，但没有实际切割")
        has_source = False
    else:
        has_source = True
        print(f"\n✅ 主视频就绪: {source_video.name}")
    
    # 4. 生成切割脚本
    print("\n\n─── 4. 自动切割脚本 ───")
    cut_commands = []
    clip_paths = []
    
    for item in parsed:
        desc_clean = sanitize_filename(item["desc"])
        time_str = f"{seconds_to_hms(item['start_sec'])}_{seconds_to_hms(item['end_sec'])}"
        clip_name = f"{PRODUCT_SHORT}_{desc_clean}_{time_str}.mp4"
        clip_path = CLIPS_DIR / clip_name
        
        clip_paths.append(clip_path)
        
        if has_source and not dry_run and item["duration"] > 0:
            cut_commands.append({
                "source": str(source_video),
                "output": str(clip_path),
                "start": item["start_sec"],
                "duration": item["duration"],
                "shot_num": item["shot_num"],
                "desc": item["desc"]
            })
        
        print(f"  #{item['shot_num']:2d}  {clip_name}")
    
    # 5. 执行切割（如有来源视频）
    if cut_commands and not dry_run:
        print(f"\n   🔪 开始切割 {len(cut_commands)} 个片段...")
        CLIPS_DIR.mkdir(parents=True, exist_ok=True)
        
        for cmd in cut_commands:
            out = cmd["output"]
            if os.path.exists(out):
                print(f"  ⏭  #{cmd['shot_num']}: 已存在，跳过")
                continue
            
            result = subprocess.run([
                FFMPEG, "-i", cmd["source"],
                "-ss", str(cmd["start"]),
                "-t", str(cmd["duration"]),
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                "-y", out
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                size = os.path.getsize(out) / 1024 / 1024
                print(f"  ✅ #{cmd['shot_num']}: {size:.0f}MB")
            else:
                print(f"  ❌ #{cmd['shot_num']}: {result.stderr[-200:]}")
        
        print(f"\n   ✅ 切割完成！片段保存在: {CLIPS_DIR}")
    
    # 6. 生成代理文件（低码率预览版）
    if cut_commands and not dry_run:
        proxy_dir = CLIPS_DIR / "_proxy"
        proxy_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n   🎬 生成代理文件 (720p, 2Mbps)...")
        
        for cmd in cut_commands:
            orig = cmd["output"]
            proxy = proxy_dir / f"proxy_{os.path.basename(orig)}"
            if os.path.exists(str(proxy)):
                continue
            subprocess.run([
                FFMPEG, "-i", orig,
                "-vf", "scale=1280:720",
                "-c:v", "libx264", "-preset", "fast", "-b:v", "2M",
                "-c:a", "aac", "-b:a", "64k",
                "-y", str(proxy)
            ], capture_output=True)
            size = os.path.getsize(str(proxy)) / 1024 / 1024
            print(f"     {proxy.name}: {size:.0f}MB")
        print(f"   ✅ 代理文件目录: {proxy_dir}")
    
    # 7. 生成 EDL (CMX3600 格式)
    print("\n\n─── 7. 生成 EDL (CMX3600) ───")
    edl_lines = [
        f"TITLE: {PRODUCT_SHORT} 自动生成时间线",
        "FCM: NON-DROP FRAME",
        ""
    ]
    
    for i, item in enumerate(parsed):
        tc_start = seconds_to_timecode(item["start_sec"])
        tc_end = seconds_to_timecode(item["end_sec"])
        dur_sec = item["duration"]
        tc_dur = seconds_to_timecode(dur_sec)
        
        # EDL 格式: 编号 源磁带 音频声道 编辑类型 转场 源入点 源出点 时间线入点 时间线出点
        edl_lines.append(f"{i+1:03d}  AX       V     C        {tc_start} {tc_end} {tc_dur} {tc_dur}")
        
        clip_name = f"{PRODUCT_SHORT}_{sanitize_filename(item['desc'])}_{seconds_to_hms(item['start_sec'])}_{seconds_to_hms(item['end_sec'])}.mp4"
        if has_source:
            edl_lines.append(f"* FROM CLIP NAME: {clip_name}")
        edl_lines.append(f"* COMMENT: #{item['shot_num']} {item['desc']} ({item['type']})")
        edl_lines.append("")
    
    edl_content = "\n".join(edl_lines)
    
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    edl_path = OUT_DIR / f"{PRODUCT_SHORT}_timeline.edl"
    edl_path.write_text(edl_content, encoding="utf-8")
    print(f"  ✅ EDL: {edl_path}")
    print(f"     共 {len(parsed)} 条素材片段")
    
    # 8. 生成导入CSV（Premiere Pro 批导入用）
    print("\n\n─── 8. 生成批导入 CSV ───")
    csv_lines = ["镜头编号,文件名,时长(秒),素材类型,画面描述,入点,出点"]
    for item in parsed:
        clip_name = f"{PRODUCT_SHORT}_{sanitize_filename(item['desc'])}_{seconds_to_hms(item['start_sec'])}_{seconds_to_hms(item['end_sec'])}.mp4"
        csv_lines.append(
            f"{item['shot_num']},{clip_name},{item['duration']},{item['type']},"
            f"{item['desc']},{seconds_to_timecode(item['start_sec'])},{seconds_to_timecode(item['end_sec'])}"
        )
    
    csv_path = OUT_DIR / f"{PRODUCT_SHORT}_batch_import.csv"
    csv_path.write_text("\n".join(csv_lines), encoding="utf-8")
    print(f"  ✅ CSV: {csv_path}")
    
    # 9. 生成 FCPXML 简化版
    print("\n\n─── 9. 生成 FCPXML (Final Cut Pro) ───")
    
    # 简单的FCPXML骨架（标准格式）
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    fcpxml = ET.Element("fcpxml", version="1.10")
    resources = ET.SubElement(fcpxml, "resources")
    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", name=f"{PRODUCT_SHORT} 自动编排")
    project = ET.SubElement(event, "project", name=f"{PRODUCT_SHORT} 时间线")
    sequence = ET.SubElement(project, "sequence", duration=f"{len(parsed)*5*25}/s")
    
    spine = ET.SubElement(sequence, "spine")
    
    for item in parsed:
        dur_frames = int(item["duration"] * 25)  # 25fps
        offset_frames = int((item["start_sec"]) * 25)
        
        clip_name = f"{PRODUCT_SHORT}_{sanitize_filename(item['desc'])}_{seconds_to_hms(item['start_sec'])}_{seconds_to_hms(item['end_sec'])}.mp4"
        
        clip = ET.SubElement(spine, "clip",
            name=clip_name,
            duration=f"{dur_frames}/s",
            start=f"{offset_frames}/s",
            offset=f"0/25"
        )
        ET.SubElement(clip, "note").text = f"#{item['shot_num']} {item['desc']}"
    
    rough = ET.tostring(fcpxml, encoding="unicode")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    
    fcpxml_path = OUT_DIR / f"{PRODUCT_SHORT}_timeline.fcpxml"
    fcpxml_path.write_text(pretty, encoding="utf-8")
    print(f"  ✅ FCPXML: {fcpxml_path}")
    
    # 10. 打印总结
    print(f"\n\n{'='*60}")
    print("📋 总结")
    print(f"{'='*60}")
    print(f"  切割片段: {len([c for c in cut_commands])} 个 ({CLIPS_DIR})")
    print(f"  代理文件: 720p, 2Mbps ({CLIPS_DIR}/_proxy/)")
    print(f"  EDL 时间线: {edl_path}")
    print(f"  批导入CSV: {csv_path}")
    print(f"  FCPXML: {fcpxml_path}")
    print(f"      - 导入方式: 文件 → 导入 → XML (Premiere Pro)")
    print(f"                  文件 → 导入 → FCPXML (Final Cut Pro)")
    print(f"                  文件 → 导入 → EDL (DaVinci Resolve)")
    print(f"{'='*60}")

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
