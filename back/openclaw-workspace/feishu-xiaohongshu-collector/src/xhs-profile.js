// Try using user's existing Chrome profile (with cookies)
import puppeteer from 'puppeteer-core';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const USER_DATA_DIR = '/Users/edy/Library/Application Support/Google/Chrome';

async function tryWithProfile() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: false, // Need to see if login pops up
    args: [`--user-data-dir=${USER_DATA_DIR}`, '--no-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // First check if we're logged in
  await page.goto('https://www.xiaohongshu.com', { waitUntil: 'networkidle2', timeout: 15000 });
  console.log(`📄 Current: ${page.url()}`);
  
  // Check cookies for XHS
  const cookies = await page.cookies();
  const xhsCookies = cookies.filter(c => c.domain.includes('xiaohongshu'));
  console.log(`🍪 XHS cookies: ${xhsCookies.length > 0 ? xhsCookies.map(c => `${c.name}=${c.value.substring(0, 20)}...`).join(', ') : 'NONE (need login)'}`);

  // Check login state
  const loginState = await page.evaluate(() => {
    return document.querySelector('.login-btn, [class*="login"]') ? 'NOT logged in (login button found)' : 'Page loaded - checking...';
  });
  console.log(`🔐 Login state: ${loginState}`);

  // Try going to the specific note
  const NOTE_URL = 'https://www.xiaohongshu.com/explore/6a09a21e0000000006021774';
  await page.goto(NOTE_URL, { waitUntil: 'networkidle2', timeout: 15000 });
  console.log(`📍 Note page: ${page.url()}`);

  // Wait for content
  await new Promise(r => setTimeout(r, 3000));

  // Try extract
  const result = await page.evaluate(() => {
    try {
      const state = window.__INITIAL_STATE__;
      if (state?.note?.noteDetailMap) {
        const note = Object.values(state.note.noteDetailMap)[0]?.note;
        if (note) {
          return {
            title: note.title,
            desc: note.desc,
            author: note.user?.nickname,
            images: (note.imageList || []).map(i => i.urlDefault || i.url),
            likes: note.interactInfo?.likedCount,
            collects: note.interactInfo?.collectedCount,
            comments: note.interactInfo?.commentCount,
          };
        }
      }
      // Check if redirected to login
      return { error: 'noteDetailMap not found', url: window.location.href };
    } catch(e) {
      return { error: e.message };
    }
  });

  console.log(`\n✅ Result: ${JSON.stringify(result, null, 2)}`);

  await browser.close();
  console.log('🔒 Closed');
}

tryWithProfile().catch(err => {
  console.error(`❌ ${err.message}`);
  process.exit(1);
});
