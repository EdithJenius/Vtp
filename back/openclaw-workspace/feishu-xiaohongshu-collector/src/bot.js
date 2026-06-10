// Feishu Bot - 小红书笔记采集器入口
// 监听飞书消息 → 提取小红书内容 → 写入多维表格

import express from 'express';
import crypto from 'crypto';
import { extractNote } from './extractor.js';
import FeishuBitableWriter from './bitable-writer.js';

const CONFIG = {
  appId: process.env.FEISHU_APP_ID || '',
  appSecret: process.env.FEISHU_APP_SECRET || '',
  verifyToken: process.env.FEISHU_VERIFY_TOKEN || '',
  bitableAppToken: process.env.BITABLE_APP_TOKEN || '',
  bitableTableId: process.env.BITABLE_TABLE_ID || '',
  port: process.env.PORT || 3000,
};

const writer = new FeishuBitableWriter({
  appId: CONFIG.appId,
  appSecret: CONFIG.appSecret
});

const app = express();
app.use(express.json());

// Feishu Event Callback Verification
app.get('/webhook/event', (req, res) => {
  const challenge = req.query.challenge;
  if (challenge) return res.json({ challenge });
  res.send('OK');
});

app.post('/webhook/event', async (req, res) => {
  const { challenge, header, event } = req.body;

  // Verification
  if (challenge) return res.json({ challenge });

  // Handle only message events
  if (header?.event_type === 'im.message.receive_v1') {
    const message = event?.message;
    const text = message?.content;
    
    // Parse content (may be JSON text)
    let content = '';
    try {
      const parsed = JSON.parse(text);
      content = parsed.text || '';
    } catch {
      content = text || '';
    }

    // Find Xiaohongshu URLs in the message
    const xhsUrls = content.match(/xiaohongshu\.com\/(?:explore|discovery\/item)\/[a-f0-9]+/g);
    
    if (xhsUrls && xhsUrls.length > 0) {
      const fullUrl = `https://www.${xhsUrls[0]}`;
      
      try {
        // Send "processing" reply
        await sendReply(event.message.message_id, '⏳ 正在提取小红书笔记...');
        
        // Step 1: Extract note data
        const noteData = await extractNote(fullUrl);
        
        // Step 2: Check if already exists
        const exists = await writer.findExisting(
          CONFIG.bitableAppToken,
          CONFIG.bitableTableId,
          noteData.noteId
        );
        
        if (exists) {
          await sendReply(event.message.message_id, 'ℹ️ 该笔记已在表格中，无需重复添加');
          return res.json({ code: 0 });
        }
        
        // Step 3: Push to Bitable
        const record = await writer.addRecord(
          CONFIG.bitableAppToken,
          CONFIG.bitableTableId,
          noteData
        );
        
        await sendReply(event.message.message_id, 
          `✅ 采集成功！\n📝 ${noteData.title || '无标题'}\n👤 ${noteData.author || '未知'}\n❤️ ${noteData.likes || 0} 赞 | 💾 ${noteData.collects || 0} 藏`);
        
      } catch (error) {
        console.error('Extraction failed:', error);
        await sendReply(event.message.message_id, `❌ 采集失败：${error.message}`);
      }
    }
  }

  res.json({ code: 0 });
});

// Helper: Send reply message via Feishu API
async function sendReply(messageId, content) {
  const token = await writer.getToken();
  const resp = await fetch(
    `https://open.feishu.cn/open-apis/im/v1/messages/${messageId}/reply`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: JSON.stringify({ text: content }),
        msg_type: 'text'
      })
    }
  );
  return resp.json();
}

app.listen(CONFIG.port, () => {
  console.log(`🤖 小红书采集机器人运行中 :${CONFIG.port}`);
});
