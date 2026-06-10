#!/usr/bin/env python3
"""使用 faster-whisper base 模型提升准确率"""
from faster_whisper import WhisperModel
import time

MODEL_SIZE = "small"  # tiny → small 提升中文识别

print(f"加载模型: {MODEL_SIZE}...")
start = time.time()
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print(f"加载完成: {time.time()-start:.1f}s")

print("转写中...")
start = time.time()
segments, info = model.transcribe("/tmp/dy_audio.wav", language="zh", beam_size=5,
                                  vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))
print(f"检测语言: {info.language} (概率: {info.language_probability:.2f})")
print(f"耗时: {time.time()-start:.1f}s")

print("\n" + "="*60)
print("📝 文案（带时间戳）")
print("="*60)

full_text = []
for seg in segments:
    ts = f"[{int(seg.start//60):02d}:{int(seg.start%60):02d}.{int(seg.start%1*10)}]"
    line = f"{ts} {seg.text.strip()}"
    print(line)
    full_text.append(seg.text.strip())

print("\n" + "="*60)
print("📋 全文")
print("="*60)
joined = "\n".join(full_text)
print(joined)

with open("/tmp/dy_transcript_small.txt", "w", encoding="utf-8") as f:
    f.write(joined)
print(f"\n已保存到: /tmp/dy_transcript_small.txt")
