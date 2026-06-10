#! /usr/bin/env node
// 小红书笔记提取器 v2 - 支持 URL 格式自适应 + 自动推送飞书
// 使用持久化 profile (需先运行 login)

import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE_DIR = '/Users/edy/.xhs-profile';
const COOKIE_FILE = '/Users/edy/.xhs-cookies.json';

// 解析小红书 URL，提取 noteId 和 xsec_token
function parseXhsUrl(url) {
  // discovery/item/{id}?xsec_token=xxx
  let match = url.match(/discovery\/item\/([a-f0-9]+)/);
  if (match) {
    const noteId = match[1];
    const xsecMatch = url.match(/xsec_token=([^&]+)/);
    const xsecSource = url.match(/xsec_source=([^&]+)/);
    return {
      noteId,
      url: `https://www.xiaohongshu.com/discovery/item/${noteId}?source=webshare&xhsshare=pc_web${xsecMatch ? `&xsec_token=${xsecMatch[1]}` : ''}${xsecSource ? `&xsec_source=${xsecSource[1]}` : ''}`
    };
  }
  // explore/{id}
  match = url.match(/explore\/([a-f0-9]+)/);
  if (match) {
    const noteId = match[1];
    const xsecMatch = url.match(/xsec_token=([^&]+)/);
    const xsecSource = url.match(/xsec_source=([^&]+)/);
    return {
      noteId,
      url: `https://www.xiaohongshu.com/discovery/item/${noteId}?source=webshare&xhsshare=pc_web${xsecMatch ? `&xsec_token=${xsecMatch[1]}` : ''}${xsecSource ? `&xsec_source=${xsecSource[1]}` : ''}`
    };
  }
  return null;
}

// 登录（首次使用）
async function login() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: false,
    args: [`--user-data-dir=${PROFILE_DIR}`, '--no-sandbox', '--window-size=850,750']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 850, height: 750 });

  await page.goto('https://www.xiaohongshu.com/login', { waitUntil: 'networkidle2', timeout: 20000 });

  console.log('\n' + '='.repeat(50));
  console.log('🔐 请用小红书 App 扫描屏幕上的二维码登录');
  console.log('='.repeat(50));

  for (let i = 0; i < 120; i++) {
    await new Promise(r => setTimeout(r, 1000));
    if (!page.url().includes('/login')) {
      console.log('\n✅ 登录成功！按 Ctrl+C 关闭窗口');
      console.log('📦 登录状态已保存，以后不需要再登录');
      break;
    }
    if (i % 10 === 9) console.log(`   ⏳ ${i + 1}秒...`);
  }
  // Don't close - let user see the page
}

// 提取笔记
async function extract(noteUrl) {
  const parsed = parseXhsUrl(noteUrl);
  if (!parsed) {
    console.error('❌ 无法识别小红书链接格式');
    console.log('   支持的格式:');
    console.log('   https://www.xiaohongshu.com/explore/xxx');
    console.log('   https://www.xiaohongshu.com/discovery/item/xxx');
    return null;
  }

  console.log(`📝 笔记ID: ${parsed.noteId}`);
  console.log(`🚀 启动 Chrome...`);

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [`--user-data-dir=${PROFILE_DIR}`, '--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  // Anti-detection
  await page.evaluateOnNewDocument(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });

  console.log(`📥 加载笔记页面...`);
  await page.goto(parsed.url, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 4000));

  const finalUrl = page.url();
  if (finalUrl.includes('login')) {
    console.log('❌ 需要重新登录（Session 过期）');
    console.log('   请运行: node xhs.mjs login');
    await browser.close();
    return null;
  }
  if (finalUrl.includes('404')) {
    console.log('⚠️  该笔记暂时无法访问（可能已删除或需要分享链接）');
  }

  const data = await page.evaluate(() => {
    try {
      const s = window.__INITIAL_STATE__;
      const map = s?.note?.noteDetailMap;
      if (!map) return null;

      const key = Object.keys(map).filter(k => k !== 'undefined')[0];
      if (!key) return null;

      const note = map[key]?.note;
      if (!note) return null;

      return {
        noteId: note.noteId || '',
        title: note.title || '',
        desc: note.desc || '',
        author: note.user?.nickname || '',
        avatar: note.user?.avatar || '',
        images: (note.imageList || []).map(img => {
          const info = img.infoList || [];
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
        tags: (note.tagList || []).map(t => t.name),
        time: note.time || 0,
        noteUrl: `https://www.xiaohongshu.com/explore/${note.noteId}`
      };
    } catch(e) {
      return { error: e.message };
    }
  });

  if (data && !data.error) {
    console.log('\n' + '━'.repeat(50));
    console.log('  📋 提取结果');
    console.log('━'.repeat(50));
    console.log(`  📝 标题: ${data.title || '(无)'}`);
    console.log(`  👤 作者: ${data.author || '(无)'}`);
    console.log(`  📄 正文:\n${(data.desc || '').substring(0, 500)}`);
    console.log(`  🖼️ 图片: ${data.images.length} 张`);
    if (data.video?.url) {
      console.log(`  🎬 视频: ${(data.video.duration / 60).toFixed(1)} 分钟`);
      console.log(`     链接: ${data.video.url.substring(0, 80)}...`);
    }
    console.log(`  ❤️ ${data.likes} 赞 | 💾 ${data.collects} 藏 | 💬 ${data.comments} 评`);
    if (data.tags?.length) console.log(`  🏷️ 标签: ${data.tags.join(', ')}`);
    console.log('━'.repeat(50));

    // 保存 JSON 文件方便后续处理
    const outFile = `/Users/edy/.openclaw/workspace/feishu-xiaohongshu-collector/output/${data.noteId}.json`;
    fs.mkdirSync(path.dirname(outFile), { recursive: true });
    fs.writeFileSync(outFile, JSON.stringify(data, null, 2));
    console.log(`💾 已保存到: ${outFile}`);
  } else {
    console.log('❌ 提取失败:', JSON.stringify(data));
  }

  await browser.close();
  return data;
}

// ===== CLI =====
async function main() {
  const cmd = process.argv[2];

  if (!cmd || cmd === 'login') {
    await login();
  } else {
    const url = cmd.startsWith('http') ? cmd : process.argv[3] || cmd;
    if (!url || !url.includes('xiaohongshu')) {
      console.log('\n用法:');
      console.log('  node xhs.mjs login                    # 首次登录（扫码）');
      console.log('  node xhs.mjs <小红书链接>             # 提取笔记');
      console.log('\n示例:');
      console.log('  node xhs.mjs "https://www.xiaohongshu.com/explore/6a09a21e..."');
      process.exit(1);
    }
    await extract(url);
  }
}

main().catch(err => {
  console.error('❌', err.message);
  process.exit(1);
});
