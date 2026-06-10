import puppeteer from 'puppeteer-core';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE_DIR = '/Users/edy/.xhs-profile';

async function run() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [`--user-data-dir=${PROFILE_DIR}`, '--no-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  
  // Override webdriver detection
  await page.evaluateOnNewDocument(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  });

  // Use the full share URL from user
  const url = 'https://www.xiaohongshu.com/discovery/item/6a09a21e0000000006021774?source=webshare&xhsshare=pc_web&xsec_token=ABAnYd0UhsUU_bTrA34Ex8o4Lb1zTkOYY8fY-_MXqrV9E=&xsec_source=pc_share';
  console.log(`📥 ${url.substring(0, 80)}...`);
  
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 5000));
  
  console.log(`📍 ${page.url()}`);
  
  if (!page.url().includes('404')) {
    const data = await page.evaluate(() => {
      const s = window.__INITIAL_STATE__;
      const map = s?.note?.noteDetailMap;
      if (!map) return null;
      const key = Object.keys(map).filter(k => k !== 'undefined')[0];
      if (!key) return null;
      const note = map[key]?.note;
      if (!note) return null;
      return {
        title: note.title,
        desc: (note.desc || '').substring(0, 200),
        author: note.user?.nickname,
        images: note.imageList?.length,
        video: !!note.video,
        likes: note.interactInfo?.likedCount,
        collects: note.interactInfo?.collectedCount,
      };
    });
    if (data) {
      console.log(`\n✅ EXTRACTED!`);
      console.log(JSON.stringify(data, null, 2));
    } else {
      console.log('❌ No note data in state');
    }
  } else {
    console.log('❌ Note unavailable (404)');
  }
  
  await browser.close();
}
run().catch(e => console.error(e.message));
