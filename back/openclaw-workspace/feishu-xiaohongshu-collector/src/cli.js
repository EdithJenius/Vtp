// CLI Tool - 手动测试小红书笔记提取 + 飞书推送
// 用法: node src/cli.js <小红书链接>

import { extractNote } from './extractor.js';
import FeishuBitableWriter from './bitable-writer.js';
import dotenv from 'dotenv';

dotenv.config();

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.log(`
🔗 用法: node src/cli.js <小红书笔记链接>

示例:
  node src/cli.js https://www.xiaohongshu.com/explore/xxxxxxxxx

可选参数:
  --push   提取后自动推送到飞书多维表格
    `);
    process.exit(1);
  }

  const shouldPush = process.argv.includes('--push');

  console.log('⏳ 正在提取小红书笔记...');
  console.log(`  链接: ${url}`);

  try {
    // Step 1: 提取笔记内容
    console.log('\n📥 Step 1: 内容提取');
    const noteData = await extractNote(url);
    
    console.log(`  ✅ 标题: ${noteData.title || '(无标题)'}`);
    console.log(`  ✅ 作者: ${noteData.author || '(未知)'}`);
    console.log(`  ✅ 正文: ${(noteData.desc || '').substring(0, 100)}...`);
    console.log(`  ✅ 图片: ${noteData.images?.length || 0} 张`);
    console.log(`  ✅ 视频: ${noteData.videoUrl ? '有' : '无'}`);
    console.log(`  ✅ 标签: ${noteData.tagList?.join(', ') || '(无)'}`);
    console.log(`  ✅ 互动: ${noteData.likes}赞 / ${noteData.collects}藏 / ${noteData.comments}评`);

    // Step 2: 推送到飞书多维表格
    if (shouldPush) {
      console.log('\n📤 Step 2: 推送到飞书多维表格');
      
      const writer = new FeishuBitableWriter({
        appId: process.env.FEISHU_APP_ID,
        appSecret: process.env.FEISHU_APP_SECRET
      });

      // 检查是否已存在
      const exists = await writer.findExisting(
        process.env.BITABLE_APP_TOKEN,
        process.env.BITABLE_TABLE_ID,
        noteData.noteId
      );

      if (exists) {
        console.log('  ℹ️ 该笔记已在表格中，跳过');
      } else {
        const record = await writer.addRecord(
          process.env.BITABLE_APP_TOKEN,
          process.env.BITABLE_TABLE_ID,
          noteData
        );
        console.log(`  ✅ 已写入表格，记录ID: ${record?.record_id}`);
      }
    }

    console.log('\n✨ 完成!');

  } catch (error) {
    console.error(`\n❌ 失败: ${error.message}`);
    process.exit(1);
  }
}

main();
