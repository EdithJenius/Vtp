import puppeteer from 'puppeteer';

const url = process.argv[2];
if (!url) { console.log("用法: node /tmp/extract_xhs.mjs <小红书链接>"); process.exit(1); }

const browser = await puppeteer.launch({
  headless: true,
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  
  // 设置 Cookie 来复用小红书登录态
  // 尝试从已有浏览器获取 cookie
  console.log(`⏳ 打开页面: ${url}`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  
  await new Promise(r => setTimeout(r, 3000));
  
  // 提取内容
  const data = await page.evaluate(() => {
    // 尝试从 window.__INITIAL_STATE__ 获取
    try {
      const el = document.querySelector('script#__NEXT_DATA__');
      if (el) {
        const json = JSON.parse(el.textContent);
        return json;
      }
    } catch(e) {}
    
    // 从 meta 获取
    const title = document.querySelector('meta[name="description"]')?.content || '';
    const ogTitle = document.querySelector('meta[property="og:title"]')?.content || '';
    
    return { title: ogTitle || document.title, desc: title };
  });
  
  console.log(JSON.stringify({ url, data }, null, 2));
  
} catch(e) {
  console.error('Error:', e.message);
} finally {
  await browser.close();
}
