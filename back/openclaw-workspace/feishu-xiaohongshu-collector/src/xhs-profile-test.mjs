import puppeteer from 'puppeteer-core';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const USER_DATA_DIR = '/Users/edy/Library/Application Support/Google/Chrome';

async function main() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [`--user-data-dir=${USER_DATA_DIR}`, '--no-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  // Go to XHS homepage to check login state
  await page.goto('https://www.xiaohongshu.com', { waitUntil: 'networkidle2', timeout: 20000 });
  
  const cookies = await page.cookies();
  const hasSession = cookies.some(c => c.name.includes('session') || c.name.includes('token') || c.name.includes('sid'));
  console.log(`🍪 Has session cookie: ${hasSession}`);
  console.log(`🍪 Total XHS cookies: ${cookies.filter(c => c.domain.includes('xiao')).length}`);

  // Try the note
  const NOTE_URL = 'https://www.xiaohongshu.com/explore/6a09a21e0000000006021774';
  await page.goto(NOTE_URL, { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 3000));

  const finalUrl = page.url();
  console.log(`📍 Final URL: ${finalUrl}`);

  if (finalUrl.includes('login')) {
    console.log('❌ Redirected to login - XHS requires authentication');
    // Get QR code for manual login
    const qrImg = await page.$eval('img[src*="qrcode"]', img => img.src).catch(() => null);
    if (qrImg) console.log(`📱 Login QR: ${qrImg.substring(0, 100)}...`);
  } else {
    const data = await page.evaluate(() => {
      const s = window.__INITIAL_STATE__;
      const m = s?.note?.noteDetailMap;
      if (m) {
        const n = Object.values(m)[0]?.note;
        return n ? { title: n.title, desc: n.desc?.substring(0, 200), author: n.user?.nickname, images: n.imageList?.length, video: !!n.video, likes: n.interactInfo?.likedCount } : null;
      }
      return null;
    });
    console.log(`✅ Note data:`, JSON.stringify(data, null, 2));
  }

  await browser.close();
}
main().catch(e => { console.error(e.message); process.exit(1); });
