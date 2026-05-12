
export default {
    async fetch(request, env, ctx) {
      const url = new URL(request.url);
      const path = url.pathname;
      const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, GET, OPTIONS", "Access-Control-Allow-Headers": "Content-Type, Authorization" };
      if (request.method === "OPTIONS") return new Response(null, { headers: cors });

      try {
        // --- 0. Image Proxy (if R2 is private) ---
        if (path.startsWith("/api/image/")) {
            const key = path.split('/').pop();
            const object = await env.BUCKET.get(key);
            if (!object) return new Response('Not Found', { status: 404 });
            const headers = new Headers(); object.writeHttpMetadata(headers); headers.set('etag', object.httpEtag);
            headers.set('Access-Control-Allow-Origin', '*');
            return new Response(object.body, { headers });
        }

        // --- 1. Customer Buy ---
        if (path === "/api/buy" && request.method === "POST") {
            const fd = await request.formData();
            const slipFile = fd.get('slip');
            if(!slipFile) return new Response(JSON.stringify({ success: false, msg: "Missing Slip" }), { headers: cors });

            // 1.1 Verify Slip with Thunder Solution API v2
            const thunderKey = "2d2f3241-dd8e-415b-9238-1fadf76c3664";
            const thunderFd = new FormData();
            thunderFd.append('image', slipFile); 
            thunderFd.append('checkDuplicate', 'true');
            thunderFd.append('matchAccount', 'false'); // Set to true if you registered account in Thunder Portal

            const thunderRes = await fetch("https://api.thunder.in.th/v2/verify/bank", {
                method: "POST",
                headers: { "Authorization": `Bearer ${thunderKey}` },
                body: thunderFd
            });
            const thunderData = await thunderRes.json();

            // Log details if not success for debugging
            if (!thunderData.success) {
                const errCode = thunderData.error?.code || "UNKNOWN_CODE";
                const errMsg = thunderData.error?.message || thunderData.message || "Unknown error";
                return new Response(JSON.stringify({ 
                    success: false, 
                    msg: `สลิปไม่ผ่านการตรวจสอบ [${errCode}]: ${errMsg}` 
                }), { headers: cors });
            }

            // 1.1.2 Security Check: Receiver Account & Duplicate Prevention
            const targetAccount = "6981106634";
            // Get account and filter only numbers
            const receiverAcc = (thunderData.data?.rawSlip?.receiver?.account?.bank?.account || "").replace(/[^0-9]/g, "");
            
            // Log for debugging (visible in Cloudflare Dashboard Logs)
            console.log(`[Slip Check] Target: ${targetAccount}, Detected: ${receiverAcc}`);

            // Robust matching:
            // 1. Full match
            // 2. Partial match (in case of masking like 69xxxx6634 -> 696634)
            const isMatch = receiverAcc === targetAccount || 
                            (receiverAcc.length >= 6 && 
                             receiverAcc.startsWith(targetAccount.slice(0, 2)) && 
                             receiverAcc.endsWith(targetAccount.slice(-4)));

            if (!isMatch) {
                return new Response(JSON.stringify({ 
                    success: false, 
                    msg: `สลิปนี้ไม่ได้โอนเข้าบัญชี ${targetAccount} (ตรวจพบในระบบ: ${receiverAcc || 'ไม่ระบุ'})` 
                }), { headers: cors });
            }

            if (thunderData.data?.isDuplicate) {
                return new Response(JSON.stringify({ 
                    success: false, 
                    msg: "สลิปนี้ถูกใช้งานไปแล้ว ไม่สามารถใช้ซ้ำได้" 
                }), { headers: cors });
            }

            // 1.2 Get Amount and Calculate Qty
            // Based on doc v2, amountInSlip is direct, otherwise check rawSlip.amount.amount
            const amount = parseFloat(thunderData.data?.amountInSlip || thunderData.data?.rawSlip?.amount?.amount || 0);
            
            // 1.2 Determine Price based on Zone and enforce limits
            const zone = fd.get('zone');
            const promoCode = (fd.get('promoCode') || "").trim().toUpperCase();
            let currentPrice = 599; // Default

            if (promoCode === 'HEE') {
                currentPrice = 399;
            } else if (zone === 'Test') {
                currentPrice = 1;
            } else if (zone === 'Early') {
                currentPrice = 399;
            } else if (zone === 'Online') {
                currentPrice = 499;
            } else if (zone === 'Door') {
                currentPrice = 599;
            }

            const calculatedQty = Math.floor(amount / currentPrice);
            if (calculatedQty <= 0) {
                return new Response(JSON.stringify({ 
                    success: false, 
                    msg: `ยอดเงิน ${amount} ฿ ไม่เพียงพอสำหรับราคาบัตรใบละ ${currentPrice} ฿` 
                }), { headers: cors });
            }

            // 1.2.1 Handle Early Limit (internal 30, but UI says 100)
            if (zone === 'Early') {
                const resLimit = await env.DB.prepare("SELECT COUNT(*) as count FROM deposits WHERE item_name = 'Early'").first();
                const currentCount = resLimit ? resLimit.count : 0;
                if (currentCount + calculatedQty > 30) {
                    return new Response(JSON.stringify({ 
                        success: false, 
                        msg: "ขออภัย บัตรโควต้า Early Ticket (100 ใบแรก) หมดลงแล้ว กรุณาติดต่อทีมงานที่ร้านหรือทางแชทเพื่อตรวจสอบหรือรับส่วนต่างคืนครับ" 
                    }), { headers: cors });
                }
            }

            // 1.3 Save to R2 and D1
            const filename = `slip_${Date.now()}_${Math.floor(Math.random()*1000)}.jpg`;
            await env.BUCKET.put(filename, slipFile);
            
            const stmts = [];
            for(let i=0; i<calculatedQty; i++) {
                const code = Math.floor(100000 + Math.random() * 900000).toString();
                stmts.push(
                    env.DB.prepare("INSERT INTO deposits (deposit_code, owner_uid, owner_name, owner_phone, item_name, price, image_key, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'active')")
                    .bind(code, fd.get('uid'), fd.get('name'), fd.get('phone'), fd.get('zone'), currentPrice, filename)
                );
            }
            await env.DB.batch(stmts);
            
            return new Response(JSON.stringify({ 
                success: true, 
                qty: calculatedQty, 
                amount: amount,
                price: currentPrice
            }), { headers: cors });
        }

        // --- 2. Wallet & Me ---
        if (path === "/api/wallet") {
            const uid = url.searchParams.get('uid');
            const res = await env.DB.prepare(`
                SELECT deposit_code, item_name, price, image_key, status, created_at, COUNT(*) as qty, SUM(CAST(price AS FLOAT)) as total_paid
                FROM deposits 
                WHERE owner_uid = ? 
                GROUP BY image_key, status
                ORDER BY created_at DESC
            `).bind(uid).all();
            return new Response(JSON.stringify(res.results), { headers: cors });
        }
        if (path === "/api/me") {
            const uid = url.searchParams.get('uid');
            const u = await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ? AND status = 'active'").bind(uid).first();
            return new Response(JSON.stringify(u || { role: 'customer' }), { headers: cors });
        }

        // --- 3. Staff System ---
        if (path === "/api/staff-req" && request.method === "POST") {
            const b = await request.json();
            await env.DB.prepare("INSERT OR IGNORE INTO staff_access (user_id, name, status, role) VALUES (?, ?, 'pending', 'staff')").bind(b.uid, b.name).run();
            return new Response(JSON.stringify({ success: true }), { headers: cors });
        }
        if (path === "/api/checkin" && request.method === "POST") {
            const b = await request.json();
            const staff = await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ? AND status = 'active'").bind(b.staff).first();
            if (!staff) return new Response(JSON.stringify({ success: false, msg: "Unauthorized Staff" }), { headers: cors });

            // FIX: Use 'deposit_code'
            const t = await env.DB.prepare("SELECT * FROM deposits WHERE deposit_code = ? AND status = 'active'").bind(b.code).first();
            if (!t) return new Response(JSON.stringify({ success: false, msg: "บัตรไม่ถูกต้อง หรือ ถูกใช้ไปแล้ว" }), { headers: cors });

            await env.DB.prepare("UPDATE deposits SET status = 'used' WHERE id = ?").bind(t.id).run();
            return new Response(JSON.stringify({ success: true }), { headers: cors });
        }

        // --- 4. Manager ---
        const checkManager = (req) => {
            const auth = req.headers.get("Authorization");
            return auth === "Bearer 0000"; // Simple auth for demo
        };

        if (path === "/api/login" && request.method === "POST") {
            const b = await request.json();
            const success = b.pass === "0000";
            return new Response(JSON.stringify({ success, token: success ? "0000" : null }), { headers: cors });
        }
        if (path === "/api/mgr/sales") {
            if (!checkManager(request)) return new Response("Unauthorized", { status: 401, headers: cors });
            const r = await env.DB.prepare(`
                SELECT image_key, owner_name, owner_phone, item_name, price, status, created_at, COUNT(*) as qty, SUM(CAST(price AS FLOAT)) as total_paid
                FROM deposits 
                WHERE status IN ('active', 'used') 
                GROUP BY image_key, owner_uid
                ORDER BY created_at DESC 
                LIMIT 100
            `).all();
            return new Response(JSON.stringify(r.results), { headers: cors });
        }
        if (path === "/api/mgr/staff") {
            if (!checkManager(request)) return new Response("Unauthorized", { status: 401, headers: cors });
            const r = await env.DB.prepare("SELECT * FROM staff_access").all();
            return new Response(JSON.stringify(r.results), { headers: cors });
        }
        if (path === "/api/staff-act" && request.method === "POST") {
            if (!checkManager(request)) return new Response("Unauthorized", { status: 401, headers: cors });
            const b = await request.json();
            if(b.act === 'approve') await env.DB.prepare("UPDATE staff_access SET status = 'active' WHERE user_id = ?").bind(b.uid).run();
            else await env.DB.prepare("DELETE FROM staff_access WHERE user_id = ?").bind(b.uid).run();
            return new Response(JSON.stringify({ success: true }), { headers: cors });
        }

        // --- System Info (Poster & Availability) ---
        if (path === "/api/poster") {
            const s = await env.DB.prepare("SELECT value FROM settings WHERE key = 'poster'").first();
            const earlyCount = await env.DB.prepare("SELECT COUNT(*) as count FROM deposits WHERE item_name = 'Early'").first();
            return new Response(JSON.stringify({ 
                poster: s ? s.value : null,
                early_count: earlyCount ? earlyCount.count : 0
            }), { headers: cors });
        }
        if (path === "/api/mgr/upload-poster" && request.method === "POST") {
            if (!checkManager(request)) return new Response("Unauthorized", { status: 401, headers: cors });
            const fd = await request.formData();
            const file = fd.get('poster');
            if(!file) return new Response(JSON.stringify({ success: false, msg: "No file" }), { headers: cors });
            
            const filename = `poster_${Date.now()}.jpg`;
            await env.BUCKET.put(filename, file);
            await env.DB.prepare("INSERT INTO settings (key, value) VALUES ('poster', ?) ON CONFLICT(key) DO UPDATE SET value = ?").bind(filename, filename).run();
            return new Response(JSON.stringify({ success: true, poster: filename }), { headers: cors });
        }

      } catch(e) { return new Response(JSON.stringify({ error: e.message }), { headers: cors }); }
      return new Response("API OK", { headers: cors });
    }
};
