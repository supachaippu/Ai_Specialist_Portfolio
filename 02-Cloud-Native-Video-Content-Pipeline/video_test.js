export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const id = url.searchParams.get("id");
    
    if (!id) return new Response("Usage: ?id=CLIP_ID", { status: 200 });

    try {
      const { results } = await env.blc_check_slide_db.prepare("SELECT opus_url FROM slides WHERE id = ?").bind(id).all();
      const slide = results[0];
      if (!slide || !slide.opus_url) return new Response(`❌ ERROR: ID [${id}] not found`, { status: 404 });

      const fullOpusUrl = `${slide.opus_url}#${id}`;
      const res = await fetch(fullOpusUrl, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
      });
      const html = await res.text();
      
      // 1. Collect ALL mp4 URLs found in the HTML (JSON or Tags)
      const mp4Regex = /https:\/\/[^"'\s\\]+\.mp4[^"'\s\\]*/gi;
      let allUrls = html.match(mp4Regex) || [];
      
      // 2. Clean URLs (remove escapes like \/)
      allUrls = allUrls.map(u => u.replace(/\\\//g, '/').replace(/&amp;/g, '&'));
      
      // 3. Find the one that contains our ID
      let target = allUrls.find(u => u.toLowerCase().includes(id.toLowerCase()));
      
      // 4. If not found by ID, look for common preview patterns
      if (!target) {
        target = allUrls.find(u => u.includes('VIDEO_PREVIEW') || u.includes('preview'));
      }

      if (target) {
        return new Response(null, {
          status: 302,
          headers: { "Location": target, "Cache-Control": "no-cache", "Access-Control-Allow-Origin": "*" }
        });
      }
      
      return new Response(`❌ ERROR: Video Hunter Failed\n\nPage: ${fullOpusUrl}\n\nDiscovered MP4s (${allUrls.length}):\n${allUrls.join('\n')}\n\nHTML Snippet (Top 1000):\n${html.slice(0, 1000)}`, { 
          status: 404,
          headers: { "Content-Type": "text/plain; charset=utf-8" }
      });

    } catch (e) {
      return new Response(`❌ SYSTEM ERROR: ${e.message}`, { status: 500 });
    }
  }
}
