"""
小红书内容工坊 - API Server
Jarvis 🤖 · 超值旅行 Value Trips
"""
import json
import os
import sys
import subprocess
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = Path(__file__).parent / 'index.html'
            with open(html, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b'{}'
        data = json.loads(body) if body else {}

        if self.path == '/api/fetch':
            result = self.handle_fetch(data)
        elif self.path == '/api/generate':
            result = self.handle_generate(data)
        else:
            result = {'error': 'not found'}

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

    def run_openclaw(self, task):
        """通过 OpenClaw CLI 执行任务"""
        cmd = [
            'openclaw', 'agent', 'run',
            '--message', json.dumps(task, ensure_ascii=False),
            '--json'
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return json.dumps({'error': 'timeout'})
        except Exception as e:
            return json.dumps({'error': str(e)})

    def handle_fetch(self, data):
        url = data.get('url', '')
        keywords = data.get('keywords', '')
        learn_points = data.get('learnPoints', '')

        prompt = f"""你是一个小红书内容分析专家。

任务：
1. 搜索与以下对标笔记相似的小红书爆款内容
2. 按「内容拆解模板」的5个维度分析：标题公式、选题逻辑、素材风格、金句手法、点击动机
3. 输出分析报告

对标笔记信息：
{'链接：' + url if url else ''}
{'关键词：' + keywords if keywords else ''}
{'学习重点：' + learn_points if learn_points else ''}

请用以下格式输出：
【相似笔记发现】（列出3-5篇类似方向的热门笔记及链接）
【标题共性分析】
【选题规律总结】
【可复用的手法】
【差异化切入建议】"""

        result = self.run_openclaw({
            'role': '小红书分析专家',
            'task': '抓取分析',
            'prompt': prompt
        })

        try:
            parsed = json.loads(result)
            return {
                'similar': parsed.get('similar', '分析完成'),
                'analysis': parsed.get('analysis', result),
                'count': parsed.get('count', 0)
            }
        except:
            return {
                'similar': result[:2000],
                'analysis': result,
                'count': 0
            }

    def handle_generate(self, data):
        learn_points = data.get('learnPoints', '')
        keywords = data.get('keywords', '')
        dimensions = data.get('dimensions', [])
        count = data.get('count', 3)

        dims_desc = '\n'.join([f'- {d}' for d in dimensions])

        prompt = f"""你是一个小红书爆款内容写手，擅长根据分析结果进行内容裂变。

已知对标笔记的学习要点：
{learn_points or '无'}

选题方向关键词：{keywords or '无'}

请从以下裂变维度出发，生成 {count} 篇不同角度的小红书笔记：

{dims_desc}

每篇笔记需包含：
1. 【标题】A/B 两个版本
2. 【正文】完整文案（300-500字）
3. 【标签】5-8个推荐标签
4. 【封面/配图建议】
5. 【发布时间建议】

要求：
- 口语化、有网感、不端着
- 开头3行必须抓住眼球
- 结尾有收藏/互动引导
- 每篇角度不同，不能雷同"""

        result = self.run_openclaw({
            'role': '小红书爆款写手',
            'task': '内容裂变',
            'prompt': prompt,
            'count': count,
            'dimensions': dimensions
        })

        try:
            parsed = json.loads(result)
            return {'content': parsed.get('content', result)}
        except:
            return {'content': result}

    def log_message(self, format, *args):
        pass  # 不输出到 stderr

def serve(port=8899):
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f"🚀 内容工坊服务启动: http://127.0.0.1:{port}")
    print(f"📂 打开 index.html 即可使用")
    server.serve_forever()

if __name__ == '__main__':
    serve()
