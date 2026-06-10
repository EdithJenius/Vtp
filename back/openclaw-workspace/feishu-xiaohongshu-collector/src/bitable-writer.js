// Feishu Bitable Writer
// Pushes extracted Xiaohongshu note data to a Feishu multi-dimensional table

import axios from 'axios';

class FeishuBitableWriter {
  constructor({ appId, appSecret }) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.token = null;
    this.tokenExpiry = 0;
  }

  // Get tenant access token (auto-cached)
  async getToken() {
    if (this.token && Date.now() < this.tokenExpiry) return this.token;

    const resp = await axios.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
      app_id: this.appId,
      app_secret: this.appSecret
    });

    this.token = resp.data.tenant_access_token;
    this.tokenExpiry = Date.now() + (resp.data.expire || 7200) * 1000 - 60000;
    return this.token;
  }

  // Upload image to Feishu drive and return file token
  async uploadImage(imageUrl) {
    const token = await this.getToken();
    
    // Download image
    const imgResp = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    const buffer = Buffer.from(imgResp.data);

    // Upload to Feishu Drive
    const formData = new FormData();
    formData.append('file', new Blob([buffer]), 'image.jpg');
    
    const uploadResp = await axios.post(
      'https://open.feishu.cn/open-apis/drive/v1/medias/upload_all',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    return uploadResp.data?.data?.file_token || null;
  }

  // Add a record to the Bitable
  async addRecord(appToken, tableId, noteData) {
    const token = await this.getToken();

    // Upload images (first 3 as preview)
    const imageTokens = [];
    if (noteData.images && noteData.images.length > 0) {
      for (let i = 0; i < Math.min(3, noteData.images.length); i++) {
        try {
          const ft = await this.uploadImage(noteData.images[i]);
          if (ft) imageTokens.push(ft);
        } catch (e) {
          console.warn(`Failed to upload image ${i}: ${e.message}`);
        }
      }
    }

    // Build fields payload
    const fields = {
      '笔记ID': noteData.noteId || '',
      '标题': noteData.title || '',
      '正文': noteData.desc || '',
      '链接': noteData.noteUrl || '',
      '作者': noteData.author || '',
      '点赞': noteData.likes || 0,
      '收藏': noteData.collects || 0,
      '评论': noteData.comments || 0,
    };

    // Add images if uploaded
    if (imageTokens.length > 0) {
      fields['图片'] = imageTokens.map(ft => ({
        file_token: ft
      }));
    }

    // Add video URL if exists
    if (noteData.videoUrl) {
      fields['视频'] = noteData.videoUrl;
    }

    // Add tags
    if (noteData.tagList && noteData.tagList.length > 0) {
      fields['标签'] = noteData.tagList.join(', ');
    }

    // Write to Bitable
    const resp = await axios.post(
      `https://open.feishu.cn/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records`,
      { fields },
      { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } }
    );

    return resp.data?.data?.record;
  }

  // Check if note already exists (prevent duplicates)
  async findExisting(appToken, tableId, noteId) {
    const token = await this.getToken();
    
    const resp = await axios.post(
      `https://open.feishu.cn/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records/search`,
      {
        field_name: '笔记ID',
        value: noteId
      },
      { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } }
    );

    return resp.data?.data?.items?.length > 0;
  }
}

export default FeishuBitableWriter;
