
        const MANAGER_PWD = "8888";
        export default {
          async fetch(request, env) {
            const url = new URL(request.url);
            const headers = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': '*', 'Access-Control-Allow-Headers': '*' };
            if (request.method === 'OPTIONS') return new Response(null, { headers });
            try {
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS bottles (id TEXT PRIMARY KEY, line_uid TEXT, brand TEXT, percent INTEGER, image_filename TEXT, status TEXT, created_at TEXT, updated_at TEXT, expire_date TEXT, claim_token TEXT, bottle_label TEXT, note TEXT, staff_name TEXT, points_awarded INTEGER DEFAULT 0)`).run();
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS staff_users (uid TEXT PRIMARY KEY, name TEXT, role TEXT, status TEXT, created_at TEXT)`).run();
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS user_points (uid TEXT PRIMARY KEY, points INTEGER)`).run();
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, actor_uid TEXT, actor_name TEXT, details TEXT, timestamp TEXT)`).run();
                const action = url.searchParams.get('action');
                const log = async (act, uid, name, det) => { await env.DB.prepare("INSERT INTO audit_logs (action, actor_uid, actor_name, details, timestamp) VALUES (?, ?, ?, ?, ?)").bind(act, uid, name, det, new Date().toISOString()).run(); };

                if (request.method === 'POST') {
                    if (!action) {
                        const fd = await request.formData();
                        const id = crypto.randomUUID(), token = crypto.randomUUID(), now = new Date().toISOString(), exp = new Date(Date.now() + 30*24*60*60*1000).toISOString();
                        await env.BUCKET.put(fd.get('image').name, fd.get('image'));
                        await env.DB.prepare(`INSERT INTO bottles (id, line_uid, brand, percent, image_filename, status, created_at, updated_at, expire_date, claim_token, bottle_label, note, staff_name, points_awarded) VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, 0)`).bind(id, '', fd.get('brand'), fd.get('percent'), fd.get('image').name, now, now, exp, token, fd.get('bottle_label'), fd.get('note'), fd.get('staff_name')).run();
                        await log('DEPOSIT', 'staff', fd.get('staff_name'), `Deposited ${fd.get('bottle_label')}`);
                        return new Response(JSON.stringify({ status: 'success', claimToken: token }), { headers });
                    }
                    if (action === 'claim') {
                        const b = await request.json();
                        const res = await env.DB.prepare("UPDATE bottles SET line_uid = ?, claim_token = NULL, updated_at = ? WHERE claim_token = ? AND status = 'active'").bind(b.lineUid, new Date().toISOString(), b.claimToken).run();
                        if (res.meta.changes > 0) { await env.DB.prepare(`INSERT INTO user_points (uid, points) VALUES (?, 10) ON CONFLICT(uid) DO UPDATE SET points = points + 10`).bind(b.lineUid).run(); return new Response(JSON.stringify({ status: 'success' }), { headers }); }
                        return new Response(JSON.stringify({ status: 'error', message: 'Item not found' }), { headers });
                    }
                    if (action === 'pickup') {
                        const b = await request.json();
                        const item = await env.DB.prepare("SELECT line_uid FROM bottles WHERE id = ?").bind(b.id).first();
                        await env.DB.prepare("UPDATE bottles SET status = 'picked_up', updated_at = ? WHERE id = ?").bind(new Date().toISOString(), b.id).run();
                        if(item && item.line_uid) await env.DB.prepare(`INSERT INTO user_points (uid, points) VALUES (?, 5) ON CONFLICT(uid) DO UPDATE SET points = points + 5`).bind(item.line_uid).run();
                        await log('PICKUP', 'staff', b.staff, `Picked up ${b.id}`);
                        return new Response(JSON.stringify({ status: 'success' }), { headers });
                    }
                    if (action === 'gen_token') {
                        const b = await request.json();
                        const t = crypto.randomUUID();
                        await env.DB.prepare("UPDATE bottles SET claim_token = ? WHERE id = ? AND line_uid = ?").bind(t, b.id, b.lineUid).run();
                        return new Response(JSON.stringify({ status: 'success', token: t }), { headers });
                    }
                    if (action === 'req_staff') {
                        const b = await request.json();
                        await env.DB.prepare("INSERT OR IGNORE INTO staff_users (uid, name, role, status, created_at) VALUES (?, ?, 'staff', 'pending', ?)").bind(b.uid, b.name, new Date().toISOString()).run();
                        return new Response('OK', {headers});
                    }
                    if (action === 'approve_staff') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Auth Fail', {headers});
                        const b = await request.json();
                        await env.DB.prepare("UPDATE staff_users SET status = 'active' WHERE uid = ?").bind(b.uid).run();
                        return new Response('OK', {headers});
                    }
                    if (action === 'delete_staff') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Auth Fail', {headers});
                        const b = await request.json();
                        await env.DB.prepare("DELETE FROM staff_users WHERE uid = ?").bind(b.uid).run();
                        return new Response('OK', {headers});
                    }
                    if (action === 'bulk_extend') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Auth Fail', {headers});
                        const b = await request.json();
                        for(const id of b.ids) { const item = await env.DB.prepare("SELECT expire_date FROM bottles WHERE id=?").bind(id).first(); if(item) { const newExp = new Date(new Date(item.expire_date).getTime() + 30*24*60*60*1000).toISOString(); await env.DB.prepare("UPDATE bottles SET expire_date=? WHERE id=?").bind(newExp, id).run(); } }
                        return new Response('OK', {headers});
                    }
                    if (action === 'promote_manager') {
                        const b = await request.json();
                        if(b.pwd === MANAGER_PWD) await env.DB.prepare("INSERT OR REPLACE INTO staff_users (uid, name, role, status, created_at) VALUES (?, ?, 'manager', 'active', ?)").bind(b.uid, b.name, new Date().toISOString()).run();
                        return new Response('OK', {headers});
                    }
                    if (request.method === 'POST' && action === 'check_status') {
                         const b = await request.json();
                         const item = await env.DB.prepare("SELECT status FROM bottles WHERE id = ?").bind(b.id).first();
                         return new Response(JSON.stringify({ status: 'success', itemStatus: item ? item.status : 'unknown' }), { headers });
                    }
                }

                if (request.method === 'GET') {
                    const uid = url.searchParams.get('uid');
                    if (uid && url.searchParams.get('type')) {
                         const type = url.searchParams.get('type');
                         let sql = "SELECT * FROM bottles WHERE line_uid = ? AND status = 'active' ORDER BY expire_date ASC";
                         if(type === 'history') sql = "SELECT * FROM bottles WHERE line_uid = ? AND status = 'picked_up' ORDER BY updated_at DESC LIMIT 20";
                         const res = await env.DB.prepare(sql).bind(uid).all();
                         return new Response(JSON.stringify(res.results), { headers });
                    }
                    if (action === 'get_points') {
                        const res = await env.DB.prepare("SELECT points FROM user_points WHERE uid = ?").bind(uid).first();
                        return new Response(JSON.stringify({ points: res ? res.points : 0 }), { headers });
                    }
                    if (action === 'check_staff') {
                        const user = await env.DB.prepare("SELECT role, status, name FROM staff_users WHERE uid = ?").bind(uid).first();
                        if(user && user.status === 'active') return new Response(JSON.stringify({ isStaff: true, role: user.role, name: user.name }), { headers });
                        return new Response(JSON.stringify({ isStaff: false }), { headers });
                    }
                    if (action === 'get_next_id') {
                        const nextId = Math.floor(1000 + Math.random() * 9000).toString();
                        return new Response(JSON.stringify({ nextId: nextId }), { headers });
                    }
                    if (action === 'list_staff') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Fail', {headers});
                        const res = await env.DB.prepare("SELECT * FROM staff_users").all();
                        return new Response(JSON.stringify(res.results), {headers});
                    }
                    if (action === 'list_stock') {
                         if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Fail', {headers});
                         const res = await env.DB.prepare("SELECT * FROM bottles WHERE status='active' ORDER BY expire_date ASC").all();
                         return new Response(JSON.stringify(res.results), {headers});
                    }
                    if (action === 'find_by_code') {
                        const code = url.searchParams.get('code');
                        const item = await env.DB.prepare("SELECT * FROM bottles WHERE bottle_label = ? AND status = 'active'").bind(code).first();
                        return new Response(JSON.stringify({ found: !!item, id: item?.id }), {headers});
                    }
                    if (action === 'audit_log') {
                         if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Fail', {headers});
                         const res = await env.DB.prepare("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50").all();
                         return new Response(JSON.stringify(res.results), {headers});
                    }
                }
                return new Response('404', { status: 404, headers });
            } catch (e) {
                return new Response(JSON.stringify({ error: e.message }), { status: 500, headers });
            }
          }
        };
        