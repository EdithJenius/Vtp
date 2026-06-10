#!/usr/bin/env python3
"""
HeyGen API 集成模块 — 文本转数字人视频
集成到 video-generation 工坊

用法:
  # 设置 API Key
  export HEYGEN_API_KEY="your-key-here"

  # 用文案生成数字人口播视频
  python3 heygen_api.py generate --text "口播文案文本" --avatar "avatar_id" --voice "voice_id"

  # 列出可用形象
  python3 heygen_api.py list-avatars

  # 检查视频生成状态
  python3 heygen_api.py status --video-id "video_id"
"""
import json, os, time, sys, argparse

API_BASE = "https://api.heygen.com"

def get_headers():
    """获取请求头"""
    api_key = os.environ.get("HEYGEN_API_KEY", "")
    if not api_key:
        print("❌ 请设置 HEYGEN_API_KEY 环境变量")
        print("   export HEYGEN_API_KEY=\"your-api-key\"")
        sys.exit(1)
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

# ============ API 封装 ============

def list_avatars():
    """获取可用数字人形象列表"""
    import urllib.request
    headers = get_headers()
    req = urllib.request.Request(f"{API_BASE}/v1/avatars", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            data = json.loads(f.read().decode())
        print(f"✅ 共 {len(data.get('data',{}).get('avatars',[]))} 个数字人形象:")
        for av in data.get("data",{}).get("avatars",[]):
            print(f"  🧑 {av.get('avatar_name','?')} (id: {av.get('avatar_id','?')})")
            if av.get("preview_url"):
                print(f"     预览: {av['preview_url']}")
        return data
    except urllib.error.HTTPError as e:
        err = e.fp.read().decode("utf-8")
        print(f"❌ 获取形象列表失败: {err[:200]}")
        return None

def list_voices():
    """获取可用声音列表"""
    import urllib.request
    headers = get_headers()
    req = urllib.request.Request(f"{API_BASE}/v1/voices", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            data = json.loads(f.read().decode())
        voices = data.get("data",{}).get("voices",[])
        print(f"✅ 共 {len(voices)} 个声音:")
        for v in voices[:10]:  # 只显示前10
            print(f"  🎤 {v.get('voice_name','?')} (id: {v.get('voice_id','?')}) 语言:{v.get('language','?')}")
        if len(voices) > 10:
            print(f"  ... 等 {len(voices)} 个")
        return data
    except urllib.error.HTTPError as e:
        err = e.fp.read().decode("utf-8")
        print(f"❌ 获取声音列表失败: {err[:200]}")
        return None

def generate_video(text, avatar_id=None, voice_id=None, title="AI生成的视频"):
    """
    从文案生成数字人口播视频

    Args:
        text: 口播文案（纯文本）
        avatar_id: 数字人形象ID（默认使用第一个可用形象）
        voice_id: 声音ID（默认使用第一个中文声音）
        title: 视频标题
    """
    import urllib.request
    
    # 如果没有指定 avatar/voice，先获取列表自动选择
    if not avatar_id or not voice_id:
        avatars = list_avatars()
        voices = list_voices()
        if not avatar_id and avatars:
            avatars_list = avatars.get("data",{}).get("avatars",[])
            if avatars_list:
                avatar_id = avatars_list[0].get("avatar_id")
                print(f"  🧑 自动选择形象: {avatars_list[0].get('avatar_name','?')}")
        if not voice_id and voices:
            voices_list = voices.get("data",{}).get("voices",[])
            # 找中文声音
            zh_voices = [v for v in voices_list if "chinese" in v.get("language","").lower() or "zh" in v.get("language","").lower()]
            if zh_voices:
                voice_id = zh_voices[0].get("voice_id")
                print(f"  🎤 自动选择声音: {zh_voices[0].get('voice_name','?')}")
            elif voices_list:
                voice_id = voices_list[0].get("voice_id")
    
    if not avatar_id:
        print("❌ 没有可用的数字人形象")
        return None
    
    payload = {
        "caption": False,  # 是否显示字幕
        "title": title,
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id
            },
            "voice": {
                "type": "text",
                "input_text": text,
                "voice_id": voice_id or "default"
            },
            "background": {"type": "color", "value": "#FFFFFF"}
        }],
        "test": False,  # True = 免费测试模式（带水印）
        "callback_url": None
    }
    
    headers = get_headers()
    body = json.dumps(payload).encode()
    req = urllib.request.Request(f"{API_BASE}/v2/video/generate", data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as f:
            data = json.loads(f.read().decode())
        video_id = data.get("data",{}).get("video_id","")
        print(f"✅ 视频生成已提交! video_id: {video_id}")
        print(f"⏱ 生成通常需要 2-5 分钟")
        return video_id
    except urllib.error.HTTPError as e:
        err = e.fp.read().decode("utf-8")
        print(f"❌ 视频生成失败: {err[:300]}")
        return None

def check_status(video_id):
    """检查视频生成状态"""
    import urllib.request
    headers = get_headers()
    req = urllib.request.Request(f"{API_BASE}/v1/video_status.get?video_id={video_id}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            data = json.loads(f.read().decode())
        status = data.get("data",{}).get("status","unknown")
        video_url = data.get("data",{}).get("video_url","")
        if status == "completed":
            print(f"✅ 视频生成完成!")
            print(f"🔗 {video_url}")
        elif status == "processing":
            print(f"⏳ 生成中... (已等待)")
        elif status == "failed":
            print(f"❌ 生成失败: {data.get('data',{}).get('error','')}")
        else:
            print(f"⏳ 状态: {status}")
        return data
    except urllib.error.HTTPError as e:
        err = e.fp.read().decode("utf-8")
        print(f"❌ 查询失败: {err[:200]}")
        return None

def generate_with_script(script_file, avatar_id=None, voice_id=None, title=None):
    """从文案文件生成视频（整合进 video-generation 工坊）"""
    if not os.path.exists(script_file):
        print(f"❌ 文案文件不存在: {script_file}")
        return None
    with open(script_file, "r", encoding="utf-8") as f:
        text = f.read()
    if not title:
        base = os.path.basename(script_file)
        title = f"AI生成 - {os.path.splitext(base)[0]}"
    return generate_video(text, avatar_id, voice_id, title)

def wait_for_completion(video_id, timeout=300, interval=10):
    """轮询等待视频生成完成"""
    import time
    print(f"⏳ 等待视频生成 (最长{timeout}秒)...")
    waited = 0
    while waited < timeout:
        data = check_status(video_id)
        if not data:
            break
        status = data.get("data",{}).get("status","")
        if status == "completed":
            print(f"✅ 生成完成! 耗时 {waited} 秒")
            return data.get("data",{}).get("video_url","")
        elif status == "failed":
            print("❌ 生成失败")
            return None
        time.sleep(interval)
        waited += interval
    print("⏰ 超时")
    return None

# ============ CLI ============

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeyGen 数字人视频生成工具")
    parser.add_argument("action", choices=["list-avatars", "list-voices", "generate", "status", "script"],
                       help="操作类型")
    parser.add_argument("--avatar", help="数字人形象ID")
    parser.add_argument("--voice", help="声音ID")
    parser.add_argument("--text", help="口播文案内容")
    parser.add_argument("--script", help="文案文件路径")
    parser.add_argument("--video-id", help="视频ID（用于查询状态）")
    parser.add_argument("--title", default="AI Generated Video", help="视频标题")
    parser.add_argument("--wait", action="store_true", help="等待生成完成")
    
    args = parser.parse_args()
    
    if args.action == "list-avatars":
        list_avatars()
    elif args.action == "list-voices":
        list_voices()
    elif args.action == "generate":
        if not args.text and not args.script:
            print("请提供 --text 或 --script 参数")
            sys.exit(1)
        if args.text:
            vid = generate_video(args.text, args.avatar, args.voice, args.title)
        else:
            vid = generate_with_script(args.script, args.avatar, args.voice, args.title)
        if vid and args.wait:
            wait_for_completion(vid)
    elif args.action == "status":
        if not args.video_id:
            print("请提供 --video-id 参数")
            sys.exit(1)
        check_status(args.video_id)
    elif args.action == "script":
        if not args.script:
            print("请提供 --script 参数")
            sys.exit(1)
        vid = generate_with_script(args.script, args.avatar, args.voice, args.title)
        if vid and args.wait:
            wait_for_completion(vid)
