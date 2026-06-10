// Debug script - see what XHS page looks like after loading
import puppeteer from 'puppeteer-core';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const NOTE_URL = 'https://www.xiaohongshu.com/explore/6a09a21e0000000006021774?xsec_token=ABAnYd0UhsUU_bTrA34Ex8o4Lb1zTkOYY8fY-_MXqrV9E=&xsec_source=pc_share';

async function debug() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  );

  // Listen for navigation
  page.on('response', resp => {
    console.log(`  📡 ${resp.status()} ${resp.url().substring(0, 100)}`);
  });

  await page.goto(NOTE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
  
  console.log(`\n📍 Current URL: ${page.url()}`);
  console.log(`📄 Page title: ${await page.title()}`);

  // Screenshot
  await page.screenshot({ path: '/tmp/xhs-debug.png', fullPage: false });
  console.log('📸 Screenshot saved');

  // Check what's on the page
  const htmlSnippet = await page.evaluate(() => {
    return {
      bodyHTML: document.body?.innerHTML?.substring(0, 3000) || '',
      scripts: Array.from(document.querySelectorAll('script')).map(s => (s.textContent || '').substring(0, 200)).filter(t => t),
      metaTags: Array.from(document.querySelectorAll('meta[property^="og:"]')).map(m => `${m.getAttribute('property')}=${m.getAttribute('content')}`),
      links: Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => h).slice(0, 10)
    };
  });

  console.log(`\n🔍 HTML body (first 2000):`);
  console.log(htmlSnippet.bodyHTML.substring(0, 2000));
  
  console.log(`\n🔍 Meta OG tags: ${htmlSnippet.metaTags.length > 0 ? htmlSnippet.metaTags.join(', ') : 'NONE'}`);
  console.log(`\n🔍 Scripts found: ${htmlSnippet.scripts.length}`);

  // Try evaluate more
  const stateCheck = await page.evaluate(() => {
    return {
      hasInitState: typeof window.__INITIAL_STATE__ !== 'undefined',
      initStateKeys: window.__INITIAL_STATE__ ? Object.keys(window.__INITIAL_STATE__) : [],
      hasXHS: typeof window.__XHS__ !== 'undefined' || typeof window.xhs !== 'undefined',
      locationHref: window.location.href,
      htmlLang: document.documentElement.lang,
    };
  });
  console.log(`\n🔍 Window state:`, JSON.stringify(stateCheck, null, 2));

  await browser.close();
}

debug().catch(console.error);
