import puppeteer from 'puppeteer-core';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE_DIR = '/Users/edy/.xhs-profile';

// Let's try fetching from the discover page first, find a public note
async function run() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [`--user-data-dir=${PROFILE_DIR}`, '--no-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // First check we're logged in
  await page.goto('https://www.xiaohongshu.com', { waitUntil: 'networkidle2', timeout: 15000 });
  const isLoggedIn = !page.url().includes('login');
  console.log(`🔐 Logged in: ${isLoggedIn}`);

  // Now try the specific note
  const url = 'https://www.xiaohongshu.com/explore/6a09a21e0000000006021774';
  console.log(`\n📥 ${url}`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 4000));

  console.log(`📍 ${page.url()}`);

  // Try to get note data regardless of URL
  const state = await page.evaluate(() => {
    const s = window.__INITIAL_STATE__;
    if (!s) return { error: 'no state' };
    
    // Check all possible paths to note data
    const paths = {
      'note.noteDetailMap': s.note?.noteDetailMap ? Object.keys(s.note.noteDetailMap) : null,
      'note.firstNoteId': s.note?.firstNoteId,
      'feed.noteList': s.feed?.noteList?.length,
    };
    
    // Try feed for any note
    if (s.feed?.noteList?.length > 0) {
      const firstNote = s.feed.noteList[0];
      return {
        paths,
        feedNote: {
          id: firstNote.id || firstNote.noteId,
          title: firstNote.displayTitle || firstNote.title,
          user: firstNote.user?.nickname
        }
      };
    }
    
    return { paths };
  });

  console.log(`\n📋 State: ${JSON.stringify(state, null, 2)}`);

  await browser.close();
}
run().catch(e => console.error(e.message));
