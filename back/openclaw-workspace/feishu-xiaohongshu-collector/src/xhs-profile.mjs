#! /usr/bin/env node
// 小红书提取器 - 使用持久化浏览器 profile
// 首次 login 后，session 保存在 profile 里，后续直接复用

import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE_DIR = path.join(process.env.HOME || '/tmp', '.xhs-profile');

const NOTE_URL = process.argv[2] || '';

async function login() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: false,
    args: [
      `--user-data-dir=${PROFILE_DIR}`,
      '--no-sandbox',
      '--window-size=850,750'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 850, height: 750 });

  console.log('📱 打开小红书登录页...');
  await page.goto('https://www.xiaohongshu.com/login', {
    waitUntil: 'networkidle2',
    timeout: 20000
  });

  console.log('\n' + '='.repeat(50));
  console.log('🔐 请用小红书 App 扫描屏幕上的二维码登录');
  console.log('   (小红书 → 扫一扫 → 扫码登录)');
  console.log('='.repeat(50));

  // 等待登录成功
  for (let i = 0; i < 120; i++) {
    await new Promise(r => setTimeout(r, 1000));
    const url = page.url();
    if (!url.includes('/login')) {
      console.log(`\n✅ 登录成功！浏览器将保持打开，按 Ctrl+C 关闭`);
      break;
    }
    if (i % 10 === 9) {
      console.log(`   ⏳ 等待扫码中... (${i + 1}秒)`);
    }
  }

  // 不要让浏览器自动关闭，保留 session
  console.log('\n💡 登录状态已保存在浏览器 profile 中');
  console.log('   以后提取笔记不需要再登录了');
}

async function extract(url) {
  if (!url) {
    console.log('❌ 请提供小红书笔记链接');
    process.exit(1);
  }

  console.log(`🚀 启动 Chrome...`);
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [
      `--user-data-dir=${PROFILE_DIR}`,
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  );

  console.log(`📥 加载笔记页面...`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  
  // 等待额外渲染
  await new Promise(r => setTimeout(r, 3000));

  const finalUrl = page.url();
  if (finalUrl.includes('login')) {
    console.log('❌ 需要重新登录（Session 过期）');
    console.log('   请运行: node src/xhs-profile.mjs login');
    await browser.close();
    return null;
  }

  console.log('✅ 页面加载完成, 提取数据...');

  const data = await page.evaluate(() => {
    try {
      const state = window.__INITIAL_STATE__;
      const noteMap = state?.note?.noteDetailMap;
      if (!noteMap) {
        return { error: 'noteDetailMap not found', hasState: !!state };
      }

      const note = Object.values(noteMap)[0]?.note;
      if (!note) return { error: 'note data not found in map' };

      return {
        noteId: note.noteId || '',
        title: note.title || '',
        desc: note.desc || '',
        author: note.user?.nickname || '',
        avatar: note.user?.avatar || '',
        images: (note.imageList || []).map(img => {
          const info = img.infoList || img.urlList || [];
          return info[info.length - 1]?.url || img.urlDefault || '';
        }).filter(Boolean),
        video: note.video ? {
          url: note.video.media?.stream?.h264?.[0]?.masterUrl || 
               note.video.media?.stream?.h265?.[0]?.masterUrl || '',
          cover: note.video.cover?.infoList?.[0]?.url || '',
          duration: note.video.duration || 0,
          caption: note.video.caption || ''
        } : null,
        likes: note.interactInfo?.likedCount || 0,
        collects: note.interactInfo?.collectedCount || 0,
        comments: note.interactInfo?.commentCount || 0,
        shareCount: note.interactInfo?.shareCount || 0,
        tags: (note.tagList || []).map(t => t.name),
        time: note.time || 0,
        noteUrl: `https://www.xiaohongshu.com/explore/${note.noteId}`
      };
    } catch(e) {
      return { error: e.message };
    }
  });

  if (data && !data.error) {
    console.log('\n' + '='.repeat(50));
    console.log('📋 提取结果');
    console.log('='.repeat(50));
    console.log(`  📝 标题: ${data.title || '(无)'}`);
    console.log(`  👤 作者: ${data.author || '(无)'}`);
    console.log(`  📄 正文:\n${(data.desc || '').substring(0, 500)}`);
    console.log(`\n  🖼️ 图片: ${data.images.length} 张`);
    if (data.images.length > 0) {
      data.images.slice(0, 3).forEach((img, i) => console.log(`     图${i+1}: ${img.substring(0, 80)}`));
    }
    if (data.video?.url) {
      console.log(`  🎬 视频: ${(data.video.duration / 60).toFixed(1)} 分`);
      console.log(`     地址: ${data.video.url.substring(0, 80)}...`);
    }
    console.log(`  ❤️ ${data.likes} 赞 | 💾 ${data.collects} 藏 | 💬 ${data.comments} 评`);
    if (data.tags?.length) console.log(`  🏷️ 标签: ${data.tags.join(', ')}`);
    console.log('='.repeat(50));
  } else {
    console.log('❌ 提取失败:', JSON.stringify(data));
  }

  await browser.close();
  return data;
}

// CLI
async function main() {
  const cmd = process.argv[2];

  if (!cmd || cmd === 'login') {
    await login();
  } else if (cmd === 'extract') {
    const url = process.argv[3];
    if (!url) {
      console.log('用法: node xhs-profile.mjs extract <小红书链接>');
      process.exit(1);
    }
    await extract(url);
  } else if (cmd.startsWith('http')) {
    await extract(cmd);
  } else {
    console.log('用法:');
    console.log('  node xhs-profile.mjs login           # 首次登录');
    console.log('  node xhs-profile.mjs <链接>          # 提取笔记');
    process.exit(1);
  }
}

main().catch(err => {
  console.error('❌', err.message);
  process.exit(1);
});
