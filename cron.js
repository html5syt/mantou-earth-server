// 使用环境变量配置以下参数：
// - GITHUB_REPO: GitHub仓库名称（格式：owner/repo）
// - GITHUB_PAT: GitHub个人访问令牌(PAT)
// - EVENT_TYPE: 要触发的事件类型（默认：'cloudflare-trigger'）
// - CLIENT_PAYLOAD: 可选的自定义JSON数据（字符串格式）

export default {
  async scheduled(event, env, ctx) {
    // 构造GitHub API URL
    const url = `https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`;
    
    // 准备请求负载
    const payload = {
      event_type: env.EVENT_TYPE || 'cloudflare-trigger',
      client_payload: env.CLIENT_PAYLOAD ? JSON.parse(env.CLIENT_PAYLOAD) : {}
    };

    try {
      // 发送POST请求到GitHub API
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.GITHUB_PAT}`,
          'User-Agent': 'Cloudflare-Worker',
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      // 检查响应状态
      if (response.status >= 200 && response.status < 300) {
        console.log(`✅ Dispatch triggered successfully for ${env.GITHUB_REPO}`);
      } else {
        const error = await response.text();
        throw new Error(`GitHub API error: ${response.status} - ${error}`);
      }
    } catch (error) {
      console.error(`❌ Dispatch failed: ${error.message}`);
      // 可以选择将错误转发到外部服务
    }
  }
};