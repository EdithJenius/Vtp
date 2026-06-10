// Simple Xiaohongshu Collector (Minimal Version)
// 不需要 Puppeteer，使用 web_fetch + 页面源数据提取
// "实在不行就只获取笔记内容"

async function extractNoteSimple(noteUrl) {
  const noteId = noteUrl.match(/xiaohongshu\.com\/(?:explore|discovery\/item)\/([a-f0-9]+)/)?.[1];
  if (!noteId) throw new Error('无效的小红书链接');

  // 尝试从不同源获取笔记内容
  const sources = [
    { url: `https://www.xiaohongshu.com/explore/${noteId}`, label: 'web' },
  ];

  // 使用第三方解析服务作为备选
  const proxiedUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(sources[0].url)}`;

  try {
    const response = await fetch(proxiedUrl);
    const html = await response.text();
    
    // 尝试从 HTML 中提取 JSON 数据
    const patterns = [
      /<script>window\.__INITIAL_STATE__\s*=\s*({.+?});?\s*<\/script>/,
      /"noteDetailMap":({[^}]+})/,
      /"note":({.+?}),"share/,
      /"title":"([^"]+)"/,
      /"desc":"([^"]+)"/,
    ];

    const result = {
      noteId,
      title: '',
      desc: '',
      images: [],
      author: '',
      videoUrl: '',
      likes: 0,
      collects: 0,
      comments: 0,
      noteUrl: `https://www.xiaohongshu.com/explore/${noteId}`,
      tagList: [],
      source: 'simple'
    };

    // Extract title from meta tags
    const titleMatch = html.match(/<meta[^>]*property="og:title"[^>]*content="([^"]+)"/);
    if (titleMatch) result.title = titleMatch[1];

    // Extract description
    const descMatch = html.match(/<meta[^>]*name="description"[^>]*content="([^"]+)"/);
    if (descMatch) result.desc = descMatch[1].substring(0, 500);

    // Extract images from og:image
    const imgMatch = html.match(/<meta[^>]*property="og:image"[^>]*content="([^"]+)"/g);
    if (imgMatch) {
      result.images = imgMatch.map(m => m.match(/content="([^"]+)"/)[1]);
    }

    // Try to find video
    const videoMatch = html.match(/video[^>]*src="([^"]+)"/);
    if (videoMatch) result.videoUrl = videoMatch[1];

    // Try to extract more from inline JSON
    const jsonMatch = html.match(/window\.__INITIAL_STATE__\s*=\s*({.+?});?\s*</);
    if (jsonMatch) {
      try {
        const state = JSON.parse(jsonMatch[1]);
        const noteMap = state?.note?.noteDetailMap;
        if (noteMap) {
          const noteData = Object.values(noteMap)[0]?.note;
          if (noteData) {
            result.title = noteData.title || result.title;
            result.desc = noteData.desc || result.desc;
            result.author = noteData.user?.nickname || '';
            result.images = noteData.imageList?.map?.(i => i.urlDefault) || result.images;
            result.likes = noteData.interactInfo?.likedCount || 0;
            result.collects = noteData.interactInfo?.collectedCount || 0;
            result.comments = noteData.interactInfo?.commentCount || 0;
          }
        }
      } catch(e) {
        // JSON parse failed, continue with meta data
      }
    }

    return result;

  } catch (error) {
    throw new Error(`提取失败: ${error.message}`);
  }
}

// === CLI test ===
async function main() {
  const url = process.argv[2];
  if (!url) {
    console.log('用法: node src/simple-collector.js <小红书笔记链接>');
    process.exit(1);
  }
  
  console.log(`⏳ 正在提取: ${url}`);
  try {
    const data = await extractNoteSimple(url);
    console.log('\n📋 提取结果:');
    console.log(`  标题: ${data.title || '(无)'}`);
    console.log(`  作者: ${data.author || '(无)'}`);
    console.log(`  正文: ${(data.desc || '').substring(0, 200)}...`);
    console.log(`  图片: ${data.images.length} 张`);
    console.log(`  视频: ${data.videoUrl || '(无)'}`);
    console.log(`  点赞: ${data.likes} | 收藏: ${data.collects} | 评论: ${data.comments}`);
  } catch (e) {
    console.error(`❌ ${e.message}`);
  }
}

// Run if called directly
if (process.argv[1]?.endsWith('simple-collector.js')) {
  main();
}

export { extractNoteSimple };
