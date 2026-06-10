// Debug script - check what XHS page shows with persisted profile
import puppeteer from 'puppeteer-core';
import fs from 'fs';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE_DIR = '/Users/edy/.xhs-profile';

async function debug() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [`--user-data-dir=${PROFILE_DIR}`, '--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');

  // Check cookies first
  await page.goto('https://www.xiaohongshu.com', { waitUntil: 'networkidle2', timeout: 15000 });
  const cookies = await page.cookies();
  const xhsCookies = cookies.filter(c => c.domain.includes('xiaohongshu'));
  console.log(`🍪 XHS Cookies: ${xhsCookies.length}`);
  xhsCookies.forEach(c => console.log(`   ${c.name}: ${c.value.substring(0, 20)}...`));

  // Now try the note
  const url = 'https://www.xiaohongshu.com/explore/6a09a21e0000000006021774';
  console.log(`\n📥 ${url}`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 5000));

  console.log(`📍 Final URL: ${page.url()}`);
  
  const stateCheck = await page.evaluate(() => {
    const s = window.__INITIAL_STATE__;
    if (!s) return { hasState: false };
    return {
      hasState: true,
      keys: Object.keys(s),
      hasNote: !!s.note,
      noteKeys: s.note ? Object.keys(s.note) : [],
      hasNoteDetail: !!(s.note?.noteDetailMap),
      detailKeys: s.note?.noteDetailMap ? Object.keys(s.note.noteDetailMap) : [],
    };
  });

  console.log(`\n🔍 State: ${JSON.stringify(stateCheck, null, 2)}`);

  // Screenshot
  await page.screenshot({ path: '/tmp/xhs-note-debug.png' });
  console.log('📸 Screenshot saved to /tmp/xhs-note-debug.png');

  // Also check if there's a login/qr code on screen
  const pageText = await page.evaluate(() => document.body?.innerText?.substring(0, 1000) || 'empty');
  console.log(`\n📄 Page text: ${pageText.substring(0, 500)}`);

  await browser.close();
}

debug().catch(console.error);
