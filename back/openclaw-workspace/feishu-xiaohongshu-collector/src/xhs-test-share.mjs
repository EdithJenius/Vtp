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

  // Test 1: Get a note from the home feed to verify extraction works
  console.log('📥 Test 1: Fetch from homepage feed...');
  await page.goto('https://www.xiaohongshu.com', { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 3000));

  const feedNote = await page.evaluate(() => {
    const s = window.__INITIAL_STATE__;
    if (s?.feed?.noteList?.length > 0) {
      const n = s.feed.noteList[0];
      return { id: n.id || n.noteId, title: n.displayTitle };
    }
    return null;
  });
  
  if (feedNote) {
    console.log(`✅ Home feed note found: ${feedNote.id} - ${feedNote.title}`);
    
    // Now try to open this note
    const noteUrl = `https://www.xiaohongshu.com/explore/${feedNote.id}`;
    console.log(`\n📥 Test 2: Open note from feed: ${noteUrl}`);
    await page.goto(noteUrl, { waitUntil: 'networkidle2', timeout: 20000 });
    await new Promise(r => setTimeout(r, 3000));
    
    console.log(`📍 ${page.url()}`);
    
    if (!page.url().includes('404') && !page.url().includes('login')) {
      const detail = await page.evaluate(() => {
        const s = window.__INITIAL_STATE__;
        const map = s?.note?.noteDetailMap;
        if (!map) return null;
        const k = Object.keys(map).filter(k => k !== 'undefined');
        if (k.length > 0) {
          const note = map[k[0]]?.note;
          return note ? {
            title: note.title,
            desc: (note.desc || '').substring(0, 100),
            author: note.user?.nickname,
            images: note.imageList?.length,
            likes: note.interactInfo?.likedCount,
            collects: note.interactInfo?.collectedCount,
          } : null;
        }
        return null;
      });
      if (detail) {
        console.log(`\n✅ NOTE EXTRACTION WORKS!`);
        console.log(JSON.stringify(detail, null, 2));
      } else {
        console.log('❌ Could not extract detail from fetched note');
      }
    } else {
      console.log('❌ Could not load note page');
    }
  } else {
    console.log('❌ No feed notes found');
  }

  await browser.close();
}
run().catch(e => console.error(e.message));
