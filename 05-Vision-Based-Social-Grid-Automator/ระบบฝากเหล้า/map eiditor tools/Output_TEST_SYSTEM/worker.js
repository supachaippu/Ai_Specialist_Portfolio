
export default {
    async fetch(request, env, ctx) {
      const url = new URL(request.url);
      const path = url.pathname;
      const corsHeaders = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" };
      if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });
  
      async function addLog(action, staff, details, imgKey = null) {
          try { await env.DB.prepare("INSERT INTO logs (action, staff_name, details, image_key) VALUES (?, ?, ?, ?)").bind(action, staff, details, imgKey).run(); } catch(e){}
      }

      async function validateStaff(uid) {
          if(!uid) return null;
          return await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ? AND status = 'active'").bind(uid).first();
      }
  
      try {
          if (path.startsWith("/api/image/")) {
              const key = path.split('/').pop(); 
              const object = await env.BUCKET.get(key);
              if (!object) return new Response('Not Found', { status: 404 });
              const headers = new Headers(); object.writeHttpMetadata(headers); headers.set('etag', object.httpEtag);
              headers.set('Cache-Control', 'public, max-age=31536000, immutable'); 
              return new Response(object.body, { headers });
          }
          if (path === "/api/me") {
              const uid = url.searchParams.get('uid'); 
              const user = await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ?").bind(uid).first();
              if (!user) return new Response(JSON.stringify({ role: 'customer' }), { headers: corsHeaders });
              return new Response(JSON.stringify({ role: user.role, status: user.status, name: user.name }), { headers: corsHeaders });
          }
          if (path === "/api/login" && request.method === "POST") {
              const body = await request.json();
              if (body.pass === "8484") return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
              return new Response(JSON.stringify({ success: false }), { headers: corsHeaders });
          }
          if (path === "/api/register" && request.method === "POST") {
              const body = await request.json(); 
              await env.DB.prepare("INSERT OR IGNORE INTO staff_access (user_id, name, status) VALUES (?, ?, 'pending')").bind(body.uid, body.name).run();
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }

          if (path === "/api/deposit" && request.method === "POST") {
              const formData = await request.formData();
              const image = formData.get('image');
              const staffUid = formData.get('staff_uid');
              const itemName = formData.get('item_name');
              const itemType = formData.get('item_type');
              const amount = formData.get('amount');
              const remarks = formData.get('remarks') || "";

              const staff = await validateStaff(staffUid);
              if (!staff) return new Response(JSON.stringify({ success: false, message: "Unauthorized Staff" }), { headers: corsHeaders });

              const filename = `dep_${Date.now()}_${Math.floor(Math.random()*1000)}.jpg`; 
              await env.BUCKET.put(filename, image);
              
              const res = await env.DB.prepare(`INSERT INTO deposits (staff_name, item_name, item_type, amount, remarks, image_key, status, expiry_date) VALUES (?, ?, ?, ?, ?, ?, 'pending_claim', date('now', '+30 days')) RETURNING id`).bind(staff.name, itemName, itemType, amount, remarks, filename).first();
              
              const id = res.id;
              const suffix = Math.floor(Math.random() * 10);
              const idPart = (id % 10000).toString().padStart(4, '0');
              const code = idPart + String(suffix);
              
              await env.DB.prepare("UPDATE deposits SET deposit_code = ? WHERE id = ?").bind(code, id).run();

              await addLog('deposit', staff.name, `Deposit: ${itemName} (${code})`, filename);
              return new Response(JSON.stringify({ success: true, deposit_id: id, code: code }), { headers: corsHeaders });
          }

          if (path === "/api/check-deposit") {
              const id = url.searchParams.get('id'); const res = await env.DB.prepare("SELECT owner_uid FROM deposits WHERE id = ?").bind(id).first();
              return new Response(JSON.stringify({ claimed: !!(res && res.owner_uid) }), { headers: corsHeaders });
          }
          if (path === "/api/claim" && request.method === "POST") {
              const body = await request.json(); const ownerName = body.name || null; let res;
              if (body.code) res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE id = (SELECT id FROM deposits WHERE deposit_code = ? AND status = 'pending_claim' ORDER BY id ASC LIMIT 1)").bind(body.uid, ownerName, body.code).run();
              else res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE id = ? AND status != 'withdrawn'").bind(body.uid, ownerName, body.id).run();
              
              if(res.meta.changes > 0) return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
              return new Response(JSON.stringify({ success: false, message: "Invalid code or item already claimed" }), { headers: corsHeaders });
          }
          if (path === "/api/my-wallet") {
              const uid = url.searchParams.get('uid'); const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_uid = ? ORDER BY created_at DESC").bind(uid).all();
              return new Response(JSON.stringify(res.results), { headers: corsHeaders });
          }
          if (path === "/api/withdraw" && request.method === "POST") {
              const body = await request.json();
              const staff = await validateStaff(body.staff_uid);
              if (!staff) return new Response(JSON.stringify({ success: false, message: "Unauthorized Staff" }), { headers: corsHeaders });

              const item = await env.DB.prepare("SELECT * FROM deposits WHERE deposit_code = ? AND status = 'active'").bind(body.code).first();
              if (!item) return new Response(JSON.stringify({ success: false, message: "Code not found" }), { headers: corsHeaders });
              
              await env.DB.prepare("UPDATE deposits SET status = 'withdrawn' WHERE id = ?").bind(item.id).run();
              if (item.image_key) { ctx.waitUntil(env.BUCKET.delete(item.image_key).catch(err => console.log("R2 Delete Error:", err))); }

              await addLog('withdraw', staff.name, `Withdrew: ${item.item_name} (Code: ${body.code})`, item.image_key);
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }
          if (path === "/api/manager-list") {
              const pending = await env.DB.prepare("SELECT * FROM staff_access WHERE status = 'pending'").all();
              const active = await env.DB.prepare("SELECT * FROM staff_access WHERE status = 'active'").all();
              return new Response(JSON.stringify({ pending: pending.results, active: active.results }), { headers: corsHeaders });
          }
          if (path === "/api/logs") {
              const logs = await env.DB.prepare("SELECT * FROM logs ORDER BY created_at DESC LIMIT 50").all();
              return new Response(JSON.stringify({ logs: logs.results }), { headers: corsHeaders });
          }
          if (path === "/api/manager-stock") {
              const stock = await env.DB.prepare("SELECT * FROM deposits WHERE status = 'active' ORDER BY expiry_date ASC").all();
              return new Response(JSON.stringify(stock.results), { headers: corsHeaders });
          }
          if (path === "/api/staff-action" && request.method === "POST") {
              const body = await request.json();
              if (body.action === 'approve') { await env.DB.prepare("UPDATE staff_access SET status = 'active' WHERE user_id = ?").bind(body.uid).run(); await addLog('approve', 'Manager', `Approved Staff: ${body.name}`); }
              else if (body.action === 'remove') { await env.DB.prepare("DELETE FROM staff_access WHERE user_id = ?").bind(body.uid).run(); await addLog('remove', 'Manager', `Removed Staff: ${body.name}`); }
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }
          if (path === "/api/test-push" && request.method === "POST") {
              const body = await request.json();
              if (!env.LINE_TOKEN) return new Response(JSON.stringify({ success: false, message: "No LINE Token" }), { headers: corsHeaders });
              const bubble = { "type": "bubble", "body": { "type": "box", "layout": "vertical", "contents": [ { "type": "text", "text": "🔔 Test Notification", "weight": "bold", "color": "#1DB446" } ] } };
              await fetch("https://api.line.me/v2/bot/message/push", { method: "POST", headers: { "Content-Type": "application/json", "Authorization": "Bearer " + env.LINE_TOKEN }, body: JSON.stringify({ "to": body.uid, "messages": [{ "type": "flex", "altText": "Test", "contents": { "type": "carousel", "contents": [bubble] } }] }) });
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }
      } catch(e) { return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders }); }
      return new Response("API Ready v85.2", { headers: corsHeaders });
    },
    async scheduled(event, env, ctx) {
      const query = `SELECT * FROM deposits WHERE status = 'active' AND (expiry_date = date('now', '+7 days') OR expiry_date = date('now', '+3 days') OR expiry_date = date('now', '+1 days'))`;
      const results = await env.DB.prepare(query).all();
      if (results.results.length === 0) return;
      const userItems = {};
      results.results.forEach(item => { if (item.owner_uid) { if (!userItems[item.owner_uid]) userItems[item.owner_uid] = []; userItems[item.owner_uid].push(item); } });
      for (const [uid, list] of Object.entries(userItems)) { await sendLinePush(uid, list, env.LINE_TOKEN); }
    }
};
async function sendLinePush(uid, items, token) {
    if (!token) return;
    const bubbles = items.map(item => {
        const days = Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
        const color = days <= 1 ? "#ef4444" : "#f97316";
        return { "type": "bubble", "body": { "type": "box", "layout": "vertical", "contents": [ { "type": "text", "text": "⚠️ Expiry Warning", "weight": "bold", "color": color }, { "type": "text", "text": item.item_name, "size": "xl", "wrap": true }, { "type": "text", "text": `Expires in ${days} days`, "size": "sm", "color": "#aaaaaa" } ] } };
    });
    await fetch("https://api.line.me/v2/bot/message/push", { method: "POST", headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token }, body: JSON.stringify({ "to": uid, "messages": [{ "type": "flex", "altText": "Expiry Warning", "contents": { "type": "carousel", "contents": bubbles } }] }) });
}
