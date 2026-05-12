export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS, DELETE",
      "Access-Control-Allow-Headers": "Content-Type",
    };

// --- v140: Google Drive Webhook URL ---
// --- Google Drive Webhook URL (Put your GAS URL here) ---
const GAS_WEBHOOK_URL = "YOUR_GOOGLE_APPS_SCRIPT_URL"; 

    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

    try {
      const url = new URL(request.url);

      if (url.pathname.startsWith("/api/r2/")) {
        const key = url.pathname.replace("/api/r2/", "");
        const object = await env.blc_check_slide_r2.get(key);
        if (!object) return new Response("Not Found", { status: 404, headers: corsHeaders });
        const headers = new Headers(corsHeaders);
        object.writeHttpMetadata(headers);
        headers.set("etag", object.httpEtag);
        headers.set("Content-Type", "image/jpeg");
        return new Response(object.body, { headers });
      }

      if (url.pathname === "/api/slides" && request.method === "GET") {
        // v112 & v129: Silent Schema Fix
        try { await env.blc_check_slide_db.prepare("ALTER TABLE slides ADD COLUMN caption TEXT").run(); } catch(e) {}
        try { await env.blc_check_slide_db.prepare("ALTER TABLE slides ADD COLUMN group_name TEXT").run(); } catch(e) {}
        try { await env.blc_check_slide_db.prepare("ALTER TABLE slides ADD COLUMN is_backed_up INTEGER DEFAULT 0").run(); } catch(e) {}
        const { results } = await env.blc_check_slide_db.prepare("SELECT id, status, subject, caption, folder_name, group_name, opus_url, video_url, thumbnail, is_backed_up, logs FROM slides").all();
        return new Response(JSON.stringify(results), { headers: corsHeaders });
      }

      if (url.pathname === "/api/slides" && request.method === "POST") {
        const body = await request.json();
        const { clips, folder_name } = body;
        if (!clips || !folder_name) return new Response("Missing data", { status: 400, headers: corsHeaders });
        for (const c of clips) {
          const targetId = c.real_id || c.id;
          const { results } = await env.blc_check_slide_db.prepare("SELECT * FROM slides WHERE id = ?").bind(targetId).all();
          if (results.length === 0) {
            const time = new Date().toISOString();
            await env.blc_check_slide_db.prepare(
              "INSERT INTO slides (id, status, subject, folder_name, opus_url, video_url, logs) VALUES (?, ?, ?, ?, ?, ?, ?)"
            ).bind(targetId, 'EDIT', c.subject, folder_name, c.opus_url, c.video_url, JSON.stringify([{ time, user: 'Seed Master', msg: 'Imported v41' }])).run();
          }
        }
        return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
      }

      if (url.pathname === "/api/slides" && request.method === "DELETE") {
        const { ids } = await request.json();
        if (!ids || !ids.length) return new Response("Missing IDs", { status: 400, headers: corsHeaders });
        for (const id of ids) {
          await env.blc_check_slide_db.prepare("DELETE FROM slides WHERE id = ?").bind(id).run();
        }
        ctx.waitUntil(Promise.all(ids.map(id => env.blc_check_slide_r2.delete(`thumb_${id}.jpg`).catch(e => {}))));
        return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
      }

      if (url.pathname === "/api/update" && request.method === "POST") {
        const body = await request.json();
        const { id, ids, status, subject, caption, thumbnail, video_url, group_name, user, msg } = body;
        const time = new Date().toISOString();
        const targetIds = ids || [id];
        
        for (const targetId of targetIds) {
          const { results } = await env.blc_check_slide_db.prepare("SELECT * FROM slides WHERE id = ?").bind(targetId).all();
          let slide = results[0];
          if (!slide) {
            await env.blc_check_slide_db.prepare(
              "INSERT INTO slides (id, status, subject, folder_name, logs) VALUES (?, ?, ?, ?, ?)"
            ).bind(targetId, 'EDIT', 'New Slide', 'Manual', JSON.stringify([{ time, user: user || 'System', msg: 'Created' }])).run();
            const fresh = await env.blc_check_slide_db.prepare("SELECT * FROM slides WHERE id = ?").bind(targetId).all();
            slide = fresh.results[0];
          }
          let logs = JSON.parse(slide.logs || "[]");
          if (msg) logs.push({ time, user, msg });
          if (status && status !== slide.status) logs.push({ time, user, msg: `Status: ${slide.status} -> ${status}` });
          if (group_name && group_name !== slide.group_name) logs.push({ time, user, msg: `Group Tag: ${group_name}` });
          
          let finalThumb = thumbnail ? (thumbnail.startsWith("data:image") ? null : thumbnail) : slide.thumbnail;
          if (thumbnail && thumbnail.startsWith("data:image")) {
            const base64Data = thumbnail.split(",")[1];
            const binaryString = atob(base64Data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) bytes[i] = binaryString.charCodeAt(i);
            await env.blc_check_slide_r2.put(`thumb_${targetId}.jpg`, bytes, { httpMetadata: { contentType: "image/jpeg" } });
            finalThumb = `${url.origin}/api/r2/thumb_${targetId}.jpg`;
          }

          const finalStatus = status || slide.status;
          const finalSubject = subject || slide.subject;
          const finalCaption = (caption !== undefined) ? caption : (slide.caption || '');
          const finalVideo = video_url || slide.video_url;
          const finalGroup = (group_name !== undefined) ? group_name : (slide.group_name || null);

          await env.blc_check_slide_db.prepare(
            "UPDATE slides SET status = ?, subject = ?, caption = ?, thumbnail = ?, video_url = ?, group_name = ?, logs = ? WHERE id = ?"
          ).bind(finalStatus, finalSubject, finalCaption, finalThumb, finalVideo, finalGroup, JSON.stringify(logs), targetId).run();

          // --- v140: Trigger Google Drive Backup on APPROVED ---
          if (finalStatus === 'APPROVED' && GAS_WEBHOOK_URL && !GAS_WEBHOOK_URL.includes("ใส่_URL")) {
            const videoUrl = `${url.origin}/api/r2/video_${targetId}.mp4`;
            ctx.waitUntil(
              fetch(GAS_WEBHOOK_URL, {
                method: "POST",
                body: JSON.stringify({ id: targetId, folder_name: slide.folder_name, video_url: videoUrl })
              }).catch(e => console.error("Backup Fail:", e))
            );
          }

          // --- v123: Auto-Delete Video from R2 when moved to BOX ---
          if (finalStatus === 'ARCHIVED') {
            ctx.waitUntil(env.blc_check_slide_r2.delete(`video_${targetId}.mp4`).catch(e => {}));
          }
        }
        return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
      }

      // --- v129: Support Group Token (g=) or Project Token (p=) ---
      if (url.pathname === "/api/approval/slides" && request.method === "GET") {
        const pToken = url.searchParams.get("token");
        const gToken = url.searchParams.get("g");
        
        if (gToken) {
            let groupName;
            try { groupName = atob(gToken); } catch(e) { return new Response("Invalid Group Token", { status: 400, headers: corsHeaders }); }
            const { results } = await env.blc_check_slide_db.prepare(
                "SELECT id, status, subject, caption, folder_name, group_name, opus_url, video_url, thumbnail FROM slides WHERE group_name = ? AND status IN ('WAIT', 'APPROVED') ORDER BY updated_at DESC"
            ).bind(groupName).all();
            return new Response(JSON.stringify(results), { headers: corsHeaders });
        }

        if (!pToken) return new Response("Missing Token", { status: 400, headers: corsHeaders });
        
        let folderNamesStr;
        try { folderNamesStr = atob(pToken); } catch(e) { return new Response("Invalid Token", { status: 400, headers: corsHeaders }); }

        const folderNames = folderNamesStr.split(',').map(n => n.trim()).filter(n => n.length > 0);
        if (folderNames.length === 0) return new Response("No Projects Specified", { status: 400, headers: corsHeaders });

        const placeholders = folderNames.map(() => '?').join(',');
        const query = `SELECT id, status, subject, caption, folder_name, group_name, opus_url, video_url, thumbnail FROM slides WHERE folder_name IN (${placeholders}) AND status IN ('WAIT', 'APPROVED') ORDER BY updated_at DESC`;
        
        const { results } = await env.blc_check_slide_db.prepare(query).bind(...folderNames).all();
        return new Response(JSON.stringify(results), { headers: corsHeaders });
      }

      if (url.pathname === "/api/approval/action" && request.method === "POST") {
        const body = await request.json();
        const { id, action, caption, user, reason } = body; 
        const time = new Date().toISOString();
        
        const { results } = await env.blc_check_slide_db.prepare("SELECT * FROM slides WHERE id = ?").bind(id).all();
        const slide = results[0];
        if (!slide) return new Response("Not Found", { status: 404, headers: corsHeaders });
        
        let logs = JSON.parse(slide.logs || "[]");
        let newStatus = slide.status;
        let logMsg = "";

        if (action === 'APPROVE') {
            newStatus = 'APPROVED';
            logMsg = `✅ Client Approved: "${caption || ''}"`;
        } else if (action === 'REJECT') {
            newStatus = 'WAIT_SUB'; // Back to CAPTION
            logMsg = `❌ Client Rejected: ${reason || 'No reason'}`;
        } else if (action === 'UPDATE_CAPTION') {
            logMsg = `📝 Client updated caption`;
        }

        logs.push({ time, user: user || 'EXTERNAL CLIENT', msg: logMsg });

        await env.blc_check_slide_db.prepare(
            "UPDATE slides SET status = ?, caption = ?, logs = ? WHERE id = ?"
        ).bind(newStatus, caption !== undefined ? caption : slide.caption, JSON.stringify(logs), id).run();
        
        return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
      }

      // --- v116: Video Archiving Endpoints ---
      if (url.pathname === "/api/upload-video" && request.method === "POST") {
        const id = url.searchParams.get("id");
        if (!id) return new Response("Missing ID", { status: 400, headers: corsHeaders });
        
        const contentType = request.headers.get("Content-Type") || "video/mp4";
        const body = await request.arrayBuffer();
        
        await env.blc_check_slide_r2.put(`video_${id}.mp4`, body, {
            httpMetadata: { contentType: contentType }
        });
        
        const videoUrl = `${url.origin}/api/video/${id}`;
        return new Response(JSON.stringify({ success: true, videoUrl }), { headers: corsHeaders });
      }

      // --- v120: Download Proxy (Force Rename to ID.mp4) ---
      if (url.pathname === "/api/download-proxy") {
        const id = url.searchParams.get("id");
        const sourceUrl = url.searchParams.get("url");
        if (!id || !sourceUrl) return new Response("Missing ID or URL", { status: 400, headers: corsHeaders });

        const res = await fetch(sourceUrl, {
          headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" }
        });
        
        const headers = new Headers(corsHeaders);
        headers.set("Content-Type", "video/mp4");
        headers.set("Content-Disposition", `attachment; filename="${id}.mp4"`);
        
        return new Response(res.body, { headers });
      }

      if (url.pathname === "/api/archive-proxy") {
        const id = url.searchParams.get("id");
        const sourceUrl = url.searchParams.get("url");
        if (!id || !sourceUrl) return new Response("Missing ID or URL", { status: 400, headers: corsHeaders });

        try {
          const res = await fetch(sourceUrl, {
            headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" }
          });
          if (!res.ok) throw new Error("Source Video Fetch Failed");
          const body = await res.arrayBuffer();
          
          await env.blc_check_slide_r2.put(`video_${id}.mp4`, body, {
              httpMetadata: { contentType: "video/mp4" }
          });

          const internalUrl = `${url.origin}/api/video/${id}`;
          return new Response(JSON.stringify({ success: true, videoUrl: internalUrl }), { headers: corsHeaders });
        } catch (e) {
          return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders });
        }
      }

      if (url.pathname.startsWith("/api/video/")) {
        const id = url.pathname.split("/").pop();
        const object = await env.blc_check_slide_r2.get(`video_${id}.mp4`);
        
        if (!object) return new Response("Video Not Found in R2", { status: 404, headers: corsHeaders });

        const headers = new Headers(corsHeaders);
        object.writeHttpMetadata(headers);
        headers.set("etag", object.httpEtag);
        headers.set("Accept-Ranges", "bytes");
        headers.set("Content-Type", "video/mp4");
        
        return new Response(object.body, { headers });
      }

      // --- v141: New Endpoint for Google Drive Callback ---
      if (url.pathname === "/api/backup-callback" && request.method === "POST") {
        const { id } = await request.json();
        await env.blc_check_slide_db.prepare("UPDATE slides SET is_backed_up = 1 WHERE id = ?").bind(id).run();
        return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
      }

      return new Response("Not Found", { status: 404, headers: corsHeaders });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
    }
  },
};
