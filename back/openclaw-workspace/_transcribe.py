#!/usr/bin/env python3
"""使用 faster-whisper 将音频转写为文字"""
from faster_whisper import WhisperModel
import time

MODEL_SIZE = "tiny"  # tiny/base/small - tiny is fastest

print(f"加载模型: {MODEL_SIZE}...")
start = time.time()
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print(f"模型加载完成: {time.time()-start:.1f}s")

print("转写中...")
start = time.time()
segments, info = model.transcribe("/tmp/dy_audio.wav", language="zh", beam_size=5)
print(f"检测语言: {info.language} (概率: {info.language_probability:.2f})")
print(f"转写耗时: {time.time()-start:.1f}s")

print("\n" + "="*60)
print("📝 文案提取结果")
print("="*60)

full_text = []
for seg in segments:
    timestamp = f"[{int(seg.start//60):02d}:{int(seg.start%60):02d} - {int(seg.end//60):02d}:{int(seg.end%60):02d}]"
    line = f"{timestamp} {seg.text.strip()}"
    print(line)
    full_text.append(seg.text.strip())

print("\n" + "="*60)
print("📋 全文")
print("="*60)
print("\n".join(full_text))

# Save to file
with open("/tmp/dy_transcript.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(full_text))
print(f"\n已保存到: /tmp/dy_transcript.txt")
