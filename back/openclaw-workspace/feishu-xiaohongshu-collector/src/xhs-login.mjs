#! /usr/bin/env node
// 小红书一键登录 + Cookie 持久化
// 运行后：打开登录页 → 你扫码 → 自动保存 Cookie → 一劳永逸

import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE_DIR = path.join(process.env.HOME || '/tmp', '.xhs-login-profile');
const COOKIE_FILE = path.join(process.env.HOME || '/tmp', '.xhs-cookies.json');

async function loginXiaohongshu() {
  console.log('🚀 启动 Chrome...');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: false,  // 需要显示扫码页面
    args: [
      `--user-data-dir=${PROFILE_DIR}`,
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--window-size=800,700'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 800, height: 700 });
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  );

  // 打开登录页
  console.log('📱 打开小红书登录页...');
  await page.goto('https://www.xiaohongshu.com/login', {
    waitUntil: 'networkidle2',
    timeout: 20000
  });

  console.log('\n' + '='.repeat(50));
  console.log('🔐 请用小红书 App 扫描屏幕上的二维码登录');
  console.log('   (打开小红书 → 扫一扫 → 扫码登录)');
  console.log('='.repeat(50));

  // 等待登录成功（检测 URL 变化或 cookie 出现）
  let loggedIn = false;
  for (let i = 0; i < 120; i++) {  // 最多等 2 分钟
    await new Promise(r => setTimeout(r, 1000));
    
    const currentUrl = page.url();
    const cookies = await page.cookies();
    const hasSession = cookies.some(c => 
      c.name.includes('session') || c.name.includes('sid') || c.name === 'a1'
    );

    // 登录后 URL 会跳走，或者 session cookie 会出现
    if (!currentUrl.includes('/login') && currentUrl.includes('xiaohongshu')) {
      loggedIn = true;
      console.log(`\n✅ 登录成功！`);
      break;
    }
    if (hasSession) {
      loggedIn = true;
      console.log(`\n✅ 检测到登录态！`);
      break;
    }

    if (i % 10 === 9) {
      console.log(`   ⏳ 等待扫码中... (${i + 1}秒)`);
    }
  }

  if (!loggedIn) {
    console.log('\n❌ 登录超时，请重新运行');
    await browser.close();
    process.exit(1);
  }

  // 保存 cookies
  const allCookies = await page.cookies();
  const xhsCookies = allCookies.filter(c => 
    c.domain.includes('xiaohongshu') || c.domain.includes('xhscdn')
  );
  
  fs.writeFileSync(COOKIE_FILE, JSON.stringify(xhsCookies, null, 2));
  console.log(`💾 Cookie 已保存到: ${COOKIE_FILE}`);
  console.log(`   📊 共 ${xhsCookies.length} 条 Cookie`);

  await browser.close();
  console.log('🔒 浏览器已关闭');
  console.log('\n🎉 登录完成！以后提取笔记不再需要扫码啦~');
  return xhsCookies;
}

// ========================================
// 提取笔记（使用已保存的 Cookie）
// ========================================
async function extractNote(noteUrl, cookies) {
  console.log(`\n📥 正在提取笔记: ${noteUrl}`);

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [
      `--user-data-dir=${PROFILE_DIR}`,
      '--no-sandbox'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // 注入 Cookie
  if (cookies && cookies.length > 0) {
    await page.setCookie(...cookies.map(c => ({
      name: c.name,
      value: c.value,
      domain: c.domain,
      path: c.path || '/',
      httpOnly: c.httpOnly || false,
      secure: c.secure || false,
      sameSite: c.sameSite || 'Lax'
    })));
  }

  await page.goto(noteUrl, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2000));

  const finalUrl = page.url();
  if (finalUrl.includes('login')) {
    console.log('❌ Cookie 过期，请重新运行登录');
    await browser.close();
    return null;
  }

  // 提取笔记数据
  const data = await page.evaluate(() => {
    try {
      const state = window.__INITIAL_STATE__;
      const noteMap = state?.note?.noteDetailMap;
      if (!noteMap) return null;
      
      const note = Object.values(noteMap)[0]?.note;
      if (!note) return null;

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
          duration: note.video.duration || 0
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

  if (data) {
    console.log(`  📝 标题: ${data.title || '(无)'}`);
    console.log(`  👤 作者: ${data.author || '(无)'}`);
    console.log(`  📄 正文: ${(data.desc || '').substring(0, 200)}`);
    console.log(`  🖼️ 图片: ${data.images?.length || 0} 张`);
    if (data.video?.url) console.log(`  🎬 视频: ${(data.video.duration / 60).toFixed(1)} 分钟`);
    console.log(`  ❤️ ${data.likes}赞 | 💾${data.collects}藏 | 💬${data.comments}评`);
    if (data.tags?.length) console.log(`  🏷️ 标签: ${data.tags.join(', ')}`);
  }

  await browser.close();
  return data;
}

// ========================================
// CLI 入口
// ========================================
async function main() {
  const command = process.argv[2] || 'login';

  if (command === 'login') {
    await loginXiaohongshu();
  } 
  else if (command === 'extract' || command.startsWith('http')) {
    const url = command === 'extract' ? process.argv[3] : command;
    if (!url) {
      console.log('用法: node xhs-login.mjs <小红书链接>');
      process.exit(1);
    }
    
    // 读取 Cookie
    let cookies = null;
    if (fs.existsSync(COOKIE_FILE)) {
      cookies = JSON.parse(fs.readFileSync(COOKIE_FILE, 'utf-8'));
      console.log(`🍪 已加载 ${cookies.length} 条 Cookie`);
    } else {
      console.log('⚠️  未找到 Cookie 文件，请先运行登录: node xhs-login.mjs login');
      process.exit(1);
    }

    const data = await extractNote(url, cookies);
    if (data && data.error) {
      console.error('❌ 提取失败:', data.error);
    } else if (data) {
      console.log('\n✅ 提取完成！');
    }
  }
  else {
    console.log(`
用法:
  node xhs-login.mjs login          # 首次登录（扫码）
  node xhs-login.mjs <笔记链接>      # 提取笔记
    `);
  }
}

main().catch(err => {
  console.error('❌', err.message);
  process.exit(1);
});
