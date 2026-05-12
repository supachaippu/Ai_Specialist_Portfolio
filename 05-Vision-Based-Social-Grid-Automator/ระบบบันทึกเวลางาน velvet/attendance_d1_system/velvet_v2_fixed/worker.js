export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const corsHeaders = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        };

        if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

        try {
            if (url.pathname === "/" || url.pathname === "") {
                return new Response("✨ Velvet Attendance System Active (v2.0) ✅", { 
                    headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders } 
                });
            }

            // API: Check UID
            if (url.pathname === "/api/check_uid" && request.method === "GET") {
                const uid = url.searchParams.get("uid");
                if (!uid) return new Response(JSON.stringify({ success: false, error: "No UID" }), { headers: corsHeaders });
                
                // ใช้ try-catch ดัก Database Error ป้องกัน Worker ตายเงียบ
                try {
                    const user = await env.DB.prepare("SELECT nickname FROM employees WHERE uid = ?").bind(uid).first();
                    return new Response(JSON.stringify({ success: !!user, nickname: user?.nickname || "" }), { headers: corsHeaders });
                } catch (dbErr) {
                    return new Response(JSON.stringify({ success: false, error: "DB Error: " + dbErr.message }), { headers: corsHeaders });
                }
            }

            // API: Get All Employees
            if (url.pathname === "/api/get_employees" && request.method === "GET") {
                const employees = await env.DB.prepare("SELECT uid, nickname FROM employees ORDER BY nickname ASC").all();
                return new Response(JSON.stringify(employees.results), { headers: corsHeaders });
            }

            // API: Register
            if (url.pathname === "/api/register" && request.method === "POST") {
                const { uid, nickname } = await request.json();
                await env.DB.prepare("INSERT OR REPLACE INTO employees (uid, nickname) VALUES (?, ?)")
                    .bind(uid, nickname).run();
                return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
            }

            // API: Log Attendance
            if (url.pathname === "/api/log" && request.method === "POST") {
                const { uid, timestamp, image, is_suspicious, note, uids } = await request.json();
                
                let imageKey = null;
                if (image && env.PHOTOS) {
                    imageKey = `${uid}_${Date.now()}.jpg`;
                    const binaryImg = Uint8Array.from(atob(image.split(',')[1]), c => c.charCodeAt(0));
                    await env.PHOTOS.put(imageKey, binaryImg, {
                        contentType: 'image/jpeg',
                        customMetadata: { uploader: uid, timestamp: timestamp }
                    });
                }

                const targetUids = (uids && uids.length > 0) ? uids : [uid];
                const stmt = env.DB.prepare("INSERT INTO attendance_logs (uid, timestamp, image_key, is_suspicious, check_note) VALUES (?, ?, ?, ?, ?)");
                
                const batch = targetUids.map(targetId => {
                    const finalNote = (targetId !== uid) ? `[ลงเวลาแทนโดย ${uid}] ${note || ""}` : (note || "");
                    return stmt.bind(targetId, timestamp, imageKey, is_suspicious ? 1 : 0, finalNote);
                });

                await env.DB.batch(batch);
                return new Response(JSON.stringify({ success: true, count: targetUids.length }), { headers: corsHeaders });
            }

            // API: Get Logs (Auto-Healing)
            if (url.pathname === "/api/get_logs" && request.method === "GET") {
                try {
                    // สร้าง Column ที่ขาดให้อัตโนมัติ (กัน Error)
                    await env.DB.prepare("ALTER TABLE attendance_logs ADD COLUMN image_key TEXT").run().catch(()=>{});
                    await env.DB.prepare("ALTER TABLE attendance_logs ADD COLUMN is_suspicious INTEGER DEFAULT 0").run().catch(()=>{});
                    await env.DB.prepare("ALTER TABLE attendance_logs ADD COLUMN check_note TEXT").run().catch(()=>{});
                } catch(e) {}

                // ล้างข้อมูลเก่า 60 วัน
                try {
                    const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString();
                    await env.DB.prepare("DELETE FROM attendance_logs WHERE timestamp < ?").bind(sixtyDaysAgo).run();
                } catch (e) {}

                const logs = await env.DB.prepare(`
                    SELECT a.timestamp, COALESCE(e.nickname, a.uid) as nickname, a.is_suspicious, a.image_key, a.check_note
                    FROM attendance_logs a 
                    LEFT JOIN employees e ON a.uid = e.uid 
                    ORDER BY a.timestamp DESC 
                    LIMIT 150
                `).all();
                return new Response(JSON.stringify(logs.results), { headers: corsHeaders });
            }

            if (url.pathname === "/api/get_image" && request.method === "GET") {
                const key = url.searchParams.get("key");
                if (!key || !env.PHOTOS) return new Response("Not Found", { status: 404 });
                const object = await env.PHOTOS.get(key);
                if (!object) return new Response("Not Found", { status: 404 });
                const headers = new Headers();
                object.writeHttpMetadata(headers);
                headers.set("Access-Control-Allow-Origin", "*");
                headers.set("etag", object.httpEtag);
                return new Response(object.body, { headers });
            }

            return new Response("Not Found", { status: 404 });
        } catch (err) {
            return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
        }
    }
};