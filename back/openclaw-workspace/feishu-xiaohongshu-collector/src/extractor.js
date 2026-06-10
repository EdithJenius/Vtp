// Xiaohongshu Note Extractor
// Uses Puppeteer to render the SPA page and extract note data

import puppeteer from 'puppeteer';

// Helper: extract note ID from URL
function extractNoteId(url) {
  const match = url.match(/xiaohongshu\.com\/(?:explore|discovery\/item)\/([a-f0-9]+)/);
  return match ? match[1] : null;
}

// Wait for page to load, then attempt to extract data from the page source or API
async function extractNote(noteUrl) {
  const noteId = extractNoteId(noteUrl);
  if (!noteId) throw new Error('Invalid Xiaohongshu URL');

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    
    // Set viewport to desktop
    await page.setViewport({ width: 1280, height: 800 });

    // Navigate to the note page
    await page.goto(noteUrl, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // Method 1: Try to extract from __INITIAL_STATE__
    const initialData = await page.evaluate(() => {
      try {
        return window.__INITIAL_STATE__;
      } catch (e) {
        return null;
      }
    });

    if (initialData?.note) {
      return parseNoteData(initialData.note);
    }

    // Method 2: Scrape from DOM
    const domData = await page.evaluate(() => {
      const result = {};

      // Title
      const titleEl = document.querySelector('.title, .note-title, h1');
      result.title = titleEl?.textContent?.trim() || '';

      // Description/content
      const descEl = document.querySelector('.desc, .content, .note-text');
      result.desc = descEl?.textContent?.trim() || '';

      // Images
      const imgEls = document.querySelectorAll('img[src*="xhscdn.com"], img[class*="note-image"]');
      result.images = Array.from(imgEls).map(img => img.src);

      // Author
      const authorEl = document.querySelector('.username, .author-name, .name');
      result.author = authorEl?.textContent?.trim() || '';

      // Video
      const videoEl = document.querySelector('video source');
      if (videoEl?.src) {
        result.videoUrl = videoEl.src;
      }

      return result;
    });

    return domData;

  } finally {
    await browser.close();
  }
}

// If we got __INITIAL_STATE__ data, parse it properly
function parseNoteData(raw) {
  const noteDetail = raw.note?.noteDetailMap || {};
  const firstKey = Object.keys(noteDetail)[0];
  const note = noteDetail[firstKey]?.note;

  if (!note) return {};

  const imageList = note.imageList || [];
  const video = note.video;
  const interactInfo = note.interactInfo || {};

  return {
    noteId: note.noteId || '',
    title: note.title || '',
    desc: note.desc || '',
    author: note.user?.nickname || '',
    avatar: note.user?.avatar || '',
    images: imageList.map(img => img.infoList?.pop()?.url || img.urlDefault || ''),
    videoUrl: video?.media?.stream?.h264?.[0]?.masterUrl || video?.media?.stream?.h265?.[0]?.masterUrl || '',
    videoCover: video?.cover?.infoList?.pop()?.url || '',
    likes: interactInfo.likedCount || 0,
    collects: interactInfo.collectedCount || 0,
    comments: interactInfo.commentCount || 0,
    shareCount: interactInfo.shareCount || 0,
    time: note.time || 0,
    tagList: (note.tagList || []).map(t => t.name),
    noteUrl: `https://www.xiaohongshu.com/explore/${note.noteId}`
  };
}

// Extract video transcript via subtitle track or API
async function extractVideoTranscript(videoUrl) {
  if (!videoUrl) return '';
  // This would use a speech-to-text API or extract embedded subtitles
  // For now, returns placeholder
  return '';
}

export {
  extractNote,
  extractVideoTranscript,
  extractNoteId
};
