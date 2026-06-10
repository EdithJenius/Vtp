// Xiaohongshu note extractor using puppeteer-core + Chrome
import puppeteer from 'puppeteer-core';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const NOTE_URL = process.argv[2] || 'https://www.xiaohongshu.com/explore/6a09a21e0000000006021774';

async function extractXiaohongshuNote(url) {
  console.log(`🚀 启动 Chrome 浏览器...`);
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,  // 'new'
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // Set user agent to look like a normal browser
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  );

  console.log(`⏳ 打开笔记页面: ${url}`);

  try {
    await page.goto(url, {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    console.log('✅ 页面加载完成');
    
    // Wait a bit for async rendering
    await new Promise(r => setTimeout(r, 2000));

    // Method 1: Try to get __INITIAL_STATE__
    const result = await page.evaluate(() => {
      const data = {};

      // Try INITIAL_STATE
      try {
        const state = window.__INITIAL_STATE__;
        if (state?.note?.noteDetailMap) {
          const entries = Object.values(state.note.noteDetailMap);
          const note = entries[0]?.note;
          if (note) {
            data.title = note.title;
            data.desc = note.desc;
            data.author = note.user?.nickname;
            data.noteId = note.noteId;
            data.images = note.imageList?.map?.(img => {
              const info = img.infoList || img.urlList || [];
              return info[info.length - 1]?.url || img.urlDefault || img.url;
            }) || [];
            data.video = note.video ? {
              url: note.video.media?.stream?.h264?.[0]?.masterUrl || '',
              cover: note.video.cover?.infoList?.[0]?.url || '',
              duration: note.video.duration || 0
            } : null;
            data.likes = note.interactInfo?.likedCount || 0;
            data.collects = note.interactInfo?.collectedCount || 0;
            data.comments = note.interactInfo?.commentCount || 0;
            data.tags = note.tagList?.map?.(t => t.name) || [];
            data.time = note.time || 0;
            return { source: '__INITIAL_STATE__', ...data };
          }
        }
      } catch(e) {}

      // Fallback: extract from DOM
      const descEl = document.querySelector('.note-scroller .note .content, .note .desc, [class*="content"], [class*="desc"]');
      data.desc = descEl?.textContent?.trim() || '';

      const titleEl = document.querySelector('h1, .title, [class*="title"]');
      data.title = titleEl?.textContent?.trim() || document.title?.replace(' - 小红书', '') || '';

      const imgs = document.querySelectorAll('img[src*="xhscdn.com"], img[src*="sns-img"]');
      data.images = Array.from(imgs).map(i => i.src).filter(s => s && !s.includes('avatar'));

      const authorEl = document.querySelector('.username, [class*="name"] a, .author .name');
      data.author = authorEl?.textContent?.trim() || '';

      data.source = 'DOM';
      return data;
    });

    console.log('\n✅ 提取结果:');
    console.log(`  来源: ${result.source}`);
    console.log(`  标题: ${result.title || '(无)'}`);
    console.log(`  作者: ${result.author || '(无)'}`);
    console.log(`  正文: ${(result.desc || '').substring(0, 300)}`);
    console.log(`  图片: ${result.images?.length || 0} 张`);
    if (result.images?.length > 0) {
      result.images.slice(0, 3).forEach((img, i) => console.log(`    图${i+1}: ${img.substring(0, 80)}...`));
    }
    console.log(`  视频: ${result.video ? `有 (${(result.video.duration / 60).toFixed(1)}分)` : '无'}`);
    if (result.video?.url) console.log(`  视频URL: ${result.video.url.substring(0, 100)}...`);
    console.log(`  互动: ❤️${result.likes} | 💾${result.collects} | 💬${result.comments}`);
    if (result.tags?.length) console.log(`  标签: ${result.tags.join(', ')}`);

    return result;

  } catch (err) {
    console.error(`❌ 提取失败: ${err.message}`);
    throw err;
  } finally {
    await browser.close();
    console.log('\n🔒 浏览器已关闭');
  }
}

// Run
const url = process.argv[2] || NOTE_URL;
extractXiaohongshuNote(url).catch(err => {
  console.error(err);
  process.exit(1);
});
