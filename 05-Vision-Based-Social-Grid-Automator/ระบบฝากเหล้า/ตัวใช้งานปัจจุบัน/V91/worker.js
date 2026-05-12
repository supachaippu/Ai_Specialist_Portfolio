
const CONFIG = {
  // MANAGER_PASSWORD is loaded from Cloudflare Secret (env.MANAGER_PASSWORD) — not stored here
  SECRET_KEY: "v89_ultra_secret_2026",
  ALLOWED_ORIGIN: "https://v91-crm-test-web.pages.dev",
  LINE_OA_TOKEN: "vnfhgghoPDvWOvqpPyZKdqmkgh5Y2uZRd6ugUbyRpJpNRzzTjpSwlpAmk479lUg5G38YQuJPKU/YaG+AYJlmjBG1anrmZqC6KpvJesRRa5eGaXs1ZgkzFKkCd/zicckoIhA/VgYMDIB92gNR9+45BwdB04t89/1O/w1cDnyilFU="
};

// === RATE LIMITER (server-side only, invisible to clients) ===
// Uses in-memory Map per worker isolate. Per Cloudflare's architecture,
// each isolate handles many requests — this provides meaningful protection.
const _rateMap = new Map(); // key -> { count, resetAt }

function checkRateLimit(key, maxPerMinute = 30) {
  const now = Date.now();
  const windowMs = 60_000;
  let entry = _rateMap.get(key);
  if (!entry || now > entry.resetAt) {
    entry = { count: 0, resetAt: now + windowMs };
    _rateMap.set(key, entry);
  }
  entry.count++;
  // Cleanup old keys every ~200 requests to avoid memory growth
  if (_rateMap.size > 500) {
    for (const [k, v] of _rateMap) {
      if (now > v.resetAt) _rateMap.delete(k);
    }
  }
  return entry.count <= maxPerMinute;
}

// === CORS ===
function getCors(origin) {
  const allowed = [CONFIG.ALLOWED_ORIGIN, "http://localhost", "http://127.0.0.1"];
  const isAllowed = origin && (allowed.some(o => origin.startsWith(o)) || origin.endsWith(".pages.dev"));
  
  return {
    "Access-Control-Allow-Origin": isAllowed ? origin : CONFIG.ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-HTTP-Method-Override, x-requested-with",
    "Access-Control-Allow-Credentials": "true",
    "Vary": "Origin"
  };
}

function json(data, cors, status = 200) {
  return new Response(JSON.stringify(data), { 
    status, 
    headers: { 
      "Content-Type": "application/json;charset=UTF-8", 
      ...cors 
    } 
  });
}

// === AUTH HELPERS ===
async function verifyRole(uid, env, roles = ['manager', 'staff']) {
  if (!uid) return false;
  const s = await env.DB.prepare("SELECT role FROM staff_access WHERE uid=? AND status='active'").bind(uid).first();
  return s && roles.includes(s.role);
}

// === LINE HELPERS ===
async function notifyAdmins(env, message) {
  const token = env.LINE_CHANNEL_ACCESS_TOKEN || env.LINE_TOKEN || CONFIG.LINE_OA_TOKEN;
  if (!token) return;
  try {
    const rs = await env.DB.prepare("SELECT uid FROM staff_access WHERE role = 'manager' AND status = 'active'").all();
    const uids = rs.results.map(r => r.uid);
    if (uids.length > 0) {
      await broadcastLine(token, uids, [{ type: "text", text: message }]);
    }
  } catch (e) {
    console.error("Notify error:", e);
  }
}

async function broadcastLine(token, uids, messages) {
  if (!token || !uids?.length) return { success: false, error: "No token or recipients" };
  const results = [];
  for (let i = 0; i < uids.length; i += 500) {
    const chunk = uids.slice(i, i + 500);
    const r = await fetch("https://api.line.me/v2/bot/message/multicast", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ to: chunk, messages })
    });
    const body = await r.json();
    results.push({ ok: r.ok, status: r.status, body });
  }
  return { success: results.every(r => r.ok), detail: results };
}

function rewardFlex(name, points, imgUrl, origin) {
  // Ensure we have absolute HTTPS URLs
  let finalImgUrl = (imgUrl || "https://v91-crm-test-web.pages.dev/app_icon.png").replace("http://", "https://");
  if (finalImgUrl.startsWith("/")) {
    const base = origin.replace("http://", "https://");
    finalImgUrl = base + finalImgUrl;
  }

  const finalUri = origin.replace("http://", "https://");

  return {
    type: "flex",
    altText: `📢 แนะนำของรางวัล: ${name}`,
    contents: {
      type: "bubble",
      size: "mega",
      header: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: "⭐ SPECIAL REWARD",
            color: "#FFD700",
            size: "xs",
            weight: "bold"
          }
        ]
      },
      hero: {
        type: "image",
        url: finalImgUrl,
        size: "full",
        aspectRatio: "1:1",
        aspectMode: "cover",
        action: {
          type: "uri",
          uri: finalUri
        }
      },
      body: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: name || "REWARD ITEM",
            weight: "bold",
            size: "xl",
            wrap: true,
            color: "#FFFFFF"
          },
          {
            type: "box",
            layout: "horizontal",
            margin: "md",
            contents: [
              {
                type: "text",
                text: "Point required",
                size: "xs",
                color: "#AAAAAA",
                flex: 1
              },
              {
                type: "text",
                text: `${(points || 0).toLocaleString()} PTS`,
                color: "#FF6600",
                size: "md",
                weight: "bold",
                align: "end",
                flex: 0
              }
            ]
          },
          {
            type: "box",
            layout: "vertical",
            margin: "lg",
            spacing: "sm",
            contents: [
              {
                type: "box",
                layout: "horizontal",
                spacing: "sm",
                contents: [
                  {
                    type: "text",
                    text: "✓",
                    color: "#FFD700",
                    size: "sm",
                    flex: 0
                  },
                  {
                    type: "text",
                    text: "แลกได้ทันทีไม่ต้องรอรอบ",
                    color: "#CCCCCC",
                    size: "sm",
                    flex: 1
                  }
                ]
              },
              {
                type: "box",
                layout: "horizontal",
                spacing: "sm",
                contents: [
                  {
                    type: "text",
                    text: "✓",
                    color: "#FFD700",
                    size: "sm",
                    flex: 0
                  },
                  {
                    type: "text",
                    text: "สินค้าพรีเมียมจำนวนจำกัด",
                    color: "#CCCCCC",
                    size: "sm",
                    flex: 1
                  }
                ]
              }
            ]
          }
        ]
      },
      footer: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "button",
            action: {
              type: "uri",
              label: "คลิกเพื่อไปแลกแต้ม",
              uri: finalUri
            },
            style: "primary",
            color: "#FF6600"
          }
        ]
      },
      styles: {
        header: { backgroundColor: "#111111" },
        body: { backgroundColor: "#111111" },
        footer: { backgroundColor: "#111111" }
      }
    }
  };
}
function usedCouponFlex(userName, rewardName, timeStr) {
  return {
    type: "flex",
    altText: `🚩 ตรวจสอบสิทธิ์: ${rewardName}`,
    contents: {
      type: "bubble",
      size: "mega",
      header: {
        type: "box",
        layout: "vertical",
        backgroundColor: "#EAB308",
        contents: [
          {
            type: "text",
            text: "FOR STAFF ONLY / สำหรับพนักงาน",
            color: "#000000",
            size: "xxs",
            weight: "bold",
            align: "center"
          }
        ]
      },
      body: {
        type: "box",
        layout: "vertical",
        backgroundColor: "#111111",
        contents: [
          {
            type: "text",
            text: "🎫 ยืนยันการใช้สิทธิ์",
            weight: "bold",
            color: "#EAB308",
            size: "sm",
            align: "center"
          },
          {
            type: "box",
            layout: "vertical",
            margin: "xxl",
            spacing: "sm",
            contents: [
              {
                type: "text",
                text: rewardName || "ไม่ระบุรายการ",
                weight: "bold",
                size: "xxl",
                color: "#FFFFFF",
                wrap: true,
                align: "center"
              },
              {
                type: "text",
                text: "---------------------------------",
                color: "#333333",
                size: "xs",
                align: "center"
              }
            ]
          },
          {
            type: "box",
            layout: "vertical",
            margin: "lg",
            spacing: "md",
            contents: [
              {
                type: "box",
                layout: "horizontal",
                contents: [
                  { type: "text", text: "👤 ลูกค้า:", color: "#aaaaaa", size: "sm", flex: 2 },
                  { type: "text", text: userName || "ลูกค้า", wrap: true, color: "#ffffff", size: "sm", flex: 5, weight: "bold" }
                ]
              },
              {
                type: "box",
                layout: "horizontal",
                contents: [
                  { type: "text", text: "⏰ เวลา:", color: "#aaaaaa", size: "sm", flex: 2 },
                  { type: "text", text: timeStr || "-", wrap: true, color: "#ffffff", size: "sm", flex: 5, weight: "bold" }
                ]
              }
            ]
          },
          {
            type: "box",
            layout: "vertical",
            margin: "xxl",
            contents: [
              {
                type: "text",
                text: "กรุณาตรวจสอบชื่อของรางวัลให้ตรงกับสินค้าที่แจก",
                color: "#FF4444",
                size: "xxs",
                align: "center",
                wrap: true
              }
            ]
          }
        ]
      }
    }
  };
}
let _localReqCount = { date: '', count: 0 };

export default {
  async fetch(request, env, ctx) {
    const todayStr = new Date().toISOString().split('T')[0];
    if (_localReqCount.date !== todayStr) {
      _localReqCount.date = todayStr;
      _localReqCount.count = 0;
    }
    _localReqCount.count++;

    if (_localReqCount.count >= 50) {
      const inc = _localReqCount.count;
      _localReqCount.count = 0;

      const updateStats = async () => {
        try {
          const statsId = `req_${todayStr}`;
          const current = await env.DB.prepare("SELECT value FROM stats WHERE id=?").bind(statsId).first();
          if (current) {
            const newTotal = current.value + inc;
            await env.DB.prepare("UPDATE stats SET value=? WHERE id=?").bind(newTotal, statsId).run();
            // Notify if crossing 90,000
            if (current.value < 90000 && newTotal >= 90000) {
              await notifyAdmins(env, `⚠️ [SYSTEM ALERT]\n🚨 Cloudflare Workers Requests ทะลุ 90,000 ครั้งเข้าสู้ 90% ของโควต้าฟรีรายวันแล้วค่ะ!\nโปรดเตรียมสลับเซิร์ฟเวอร์สำรอง!!`);
            }
          } else {
            // First batch of the day (might miss first 50 requests if they span isolates, but close enough)
            await env.DB.prepare("INSERT INTO stats (id, value) VALUES(?,?)").bind(statsId, inc).run();
          }
        } catch (e) { }
      };

      if (ctx && ctx.waitUntil) {
        ctx.waitUntil(updateStats());
      } else {
        updateStats(); // Fallback
      }
    }

    const url = new URL(request.url);
    const p = url.pathname;
    const origin = request.headers.get("Origin") || "";
    const cors = getCors(origin);

    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    // === RATE LIMITING (hidden in worker — clients cannot bypass) ===
    // Use IP as base key; fall back to CF-connecting-ip or a generic key
    const clientIP = request.headers.get("CF-Connecting-IP") || request.headers.get("X-Real-IP") || "unknown";
    const rateLimitKey = `${clientIP}:${p}`;

    // Staff/write endpoints — stricter limit (15/min)
    const strictPaths = ["/api/deposit", "/api/staff-login", "/api/redeem", "/api/book-table", "/api/link-phone",
      "/api/buy-ticket", "/api/cancel-my-booking", "/api/broadcast", "/api/claim", "/api/use-coupon", "/api/staff-request"];
    const limit = strictPaths.includes(p) ? 15 : 60;

    if (!checkRateLimit(rateLimitKey, limit)) {
      return new Response(JSON.stringify({ success: false, error: "Too many requests. Please wait." }),
        { status: 429, headers: { "Content-Type": "application/json", "Retry-After": "60", ...cors } });
    }

    try {

      // ==================== CUSTOMER ====================

      // Profile
      if (p === "/api/me") {
        const uid = url.searchParams.get("uid");
        const user = await env.DB.prepare("SELECT * FROM user_profiles WHERE uid=?").bind(uid).first();
        const staff = await env.DB.prepare("SELECT role,status,name FROM staff_access WHERE uid=?").bind(uid).first();
        return json({
          phone: user?.phone || null,
          points: user?.points || 0,
          name: user?.name || "Guest",
          birthday: user?.birthday || null,
          role: staff?.role || "customer",
          status: staff?.status || "inactive",
          staffName: staff?.name || user?.name || "Guest"
        }, cors);
      }

      // Register / link phone
      if (p === "/api/link-phone" && request.method === "POST") {
        const { uid, phone, name, birthday } = await request.json();
        await env.DB.prepare("INSERT INTO user_profiles (uid,phone,name,points,birthday) VALUES(?,?,?,50,?) ON CONFLICT(uid) DO UPDATE SET phone=excluded.phone,name=excluded.name,birthday=COALESCE(excluded.birthday,birthday)")
          .bind(uid, phone, name, birthday || null).run();
        await env.DB.prepare("UPDATE deposits SET owner_uid=? WHERE owner_phone=? AND (owner_uid IS NULL OR owner_uid='')").bind(uid, phone).run();
        return json({ success: true }, cors);
      }

      // My wallet (customer's deposits + tickets)
      if (p === "/api/my-wallet") {
        const uid = url.searchParams.get("uid");
        // Get the customer's phone to also match deposits stored by phone before uid was linked
        const userProfile = await env.DB.prepare("SELECT phone FROM user_profiles WHERE uid=?").bind(uid).first();
        const phone = userProfile?.phone || "";
        // Update any deposits that match by phone but have no uid yet
        if (phone) {
          await env.DB.prepare("UPDATE deposits SET owner_uid=? WHERE owner_phone=? AND (owner_uid IS NULL OR owner_uid='')").bind(uid, phone).run();
        }
        const { results: deps } = await env.DB.prepare(
          "SELECT d.*, s.name as staff_name, w.name as withdrawn_by_name FROM deposits d LEFT JOIN staff_access s ON d.staff_uid=s.uid LEFT JOIN staff_access w ON d.withdrawn_by=w.uid WHERE d.owner_uid=? AND d.status IN ('active', 'withdrawn') ORDER BY d.created_at DESC"
        ).bind(uid).all();
        const { results: tickets } = await env.DB.prepare("SELECT * FROM concert_tickets WHERE uid=? AND status IN ('active', 'used') ORDER BY created_at DESC").bind(uid).all();
        const items = [
          ...deps.map(d => ({ ...d, image_url: d.image_key ? `${url.origin}/api/image/${d.image_key}` : null })),
          ...tickets.map(t => ({ id: `t${t.id}`, item_name: `\uD83C\uDFAB ${t.zone} Zone x${t.qty}`, amount: 100, status: t.status, created_at: t.created_at, expiry_date: null, image_url: null, signature: t.signature }))
        ];
        return json(items, cors);
      }

      // Staff request (for staff to register)
      if (p === "/api/staff-request" && request.method === "POST") {
        const { uid, name } = await request.json();
        const existing = await env.DB.prepare("SELECT uid FROM staff_access WHERE uid=?").bind(uid).first();
        if (!existing) {
          await env.DB.prepare("INSERT INTO staff_access (uid,name,role,status) VALUES(?,?,'staff','pending')").bind(uid, name).run();
        } else {
          await env.DB.prepare("UPDATE staff_access SET name=?, role='staff', status='pending' WHERE uid=?").bind(name, uid).run();
        }
        return json({ success: true }, cors);
      }

      // My coupons
      if (p === "/api/my-coupons") {
        const uid = url.searchParams.get("uid");
        const { results } = await env.DB.prepare(`
          SELECT r.*, w.image_key 
          FROM redemptions r 
          LEFT JOIN rewards w ON r.reward_id = w.id 
          WHERE r.uid=? 
          ORDER BY r.created_at DESC
        `).bind(uid).all();
        
        const mapped = results.map(c => ({
          ...c,
          image_url: c.image_key ? `${url.origin}/api/image/${c.image_key}` : null
        }));
        
        // Unused = available to stay in 'My Coupons'
        // Pending = waiting for staff to see
        const unused = mapped.filter(c => c.status === 'unused');
        const pending = mapped.filter(c => c.status === 'pending');
        return json({ unused, pending }, cors);
      }

      // Customer activates coupon (makes it visible to staff)
      if (p === "/api/claim" && request.method === "POST") {
        const { coupon_id, uid } = await request.json();
        await env.DB.prepare("UPDATE redemptions SET status='pending' WHERE id=? AND uid=?").bind(coupon_id, uid).run();
        return json({ success: true }, cors);
      }

      // Use coupon (customer self-uses)
      if (p === "/api/use-coupon" && request.method === "POST") {
        const { coupon_id, uid } = await request.json();
        await env.DB.prepare("UPDATE redemptions SET status='used' WHERE id=? AND uid=?").bind(coupon_id, uid).run();
        return json({ success: true }, cors);
      }

      // Rewards list
      if (p === "/api/rewards" && request.method === "GET") {
        const { results } = await env.DB.prepare("SELECT * FROM rewards ORDER BY created_at DESC").all();
        return json(results.map(r => ({ ...r, image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : null })), cors);
      }

      // Redeem reward (new endpoint for coupon generation)
      if (p === "/api/redeem-reward" && request.method === "POST") {
        const { reward_id, uid, phone, name } = await request.json();
        const rw = await env.DB.prepare("SELECT * FROM rewards WHERE id=?").bind(reward_id).first();
        if (!rw) return json({ success: false, error: 'ไม่พบของรางวัล' }, cors);
        const user = await env.DB.prepare("SELECT points FROM user_profiles WHERE uid=?").bind(uid).first();
        if (!user || user.points < rw.points) return json({ success: false, error: 'คะแนนไม่เพียงพอ' }, cors);

        await env.DB.prepare("UPDATE user_profiles SET points=points-? WHERE uid=?").bind(rw.points, uid).run();

        const couponCode = Math.random().toString(36).substring(2, 7).toUpperCase();
        await env.DB.prepare("INSERT INTO coupons (code, reward_id, reward_name, owner_uid, owner_phone, status, created_at) VALUES (?,?,?,?,?,?,?)")
          .bind(couponCode, rw.id, rw.name, uid, phone, 'active', new Date().toISOString()).run();

        return json({ success: true, couponCode }, cors);
      }

      // Claim a gift deposit
      if (p === "/api/claim-deposit" && request.method === "POST") {
        const { deposit_id, uid, phone, name } = await request.json();
        const dep = await env.DB.prepare("SELECT * FROM deposits WHERE id=? AND status='active'").bind(deposit_id).first();
        if (!dep) return json({ success: false, error: 'ไม่พบรายการฝากนี้ หรือรายการถูกเบิกไปแล้วค่ะ' }, cors);
        if (dep.owner_uid === uid) return json({ success: true, message: 'รายการนี้อยู่ในกระเป๋าของคุณอยู่แล้วค่ะ' }, cors);

        // Transfer ownership
        await env.DB.prepare("UPDATE deposits SET owner_uid=?, owner_phone=? WHERE id=?")
          .bind(uid, phone, deposit_id).run();

        return json({ success: true }, cors);
      }

      // Redeem reward (old endpoint, kept for compatibility if needed, but new one is redeem-reward)
      if (p === "/api/redeem" && request.method === "POST") {
        const { uid, reward_id } = await request.json();
        const user = await env.DB.prepare("SELECT points,phone FROM user_profiles WHERE uid=?").bind(uid).first();
        const reward = await env.DB.prepare("SELECT name,points FROM rewards WHERE id=?").bind(reward_id).first();
        if (!user || !reward) return json({ success: false, error: "ไม่พบข้อมูล" }, cors);
        if (user.points < reward.points) return json({ success: false, error: "แต้มไม่พอแลก" }, cors);
        await env.DB.prepare("UPDATE user_profiles SET points=points-? WHERE uid=?").bind(reward.points, uid).run();
        await env.DB.prepare("INSERT INTO redemptions (uid,reward_id,reward_name,points,status) VALUES(?,?,?,?,'unused')").bind(uid, reward_id, reward.name, reward.points).run();
        return json({ success: true }, cors);
      }

      // Book table (customer)
      if (p === "/api/book-table" && request.method === "POST") {
        const { name, phone, date, time, pax, uid, table_number } = await request.json();
        await env.DB.prepare("INSERT INTO bookings (name,phone,date,time,pax,status,uid,table_number) VALUES(?,?,?,?,?,'pending',?,?)")
          .bind(name, phone, date, time, pax, uid || null, table_number || null).run();
        return json({ success: true }, cors);
      }

      // My bookings (customer view) — returns upcoming + recent bookings for a UID
      if (p === "/api/my-bookings") {
        const uid = url.searchParams.get("uid");
        if (!uid) return json([], cors);
        // Return bookings not cancelled, ordered by date desc, limit 20
        const { results } = await env.DB.prepare(
          "SELECT id, name, date, time, pax, status, table_number, created_at FROM bookings WHERE uid=? AND status != 'cancelled' ORDER BY date DESC, time DESC LIMIT 20"
        ).bind(uid).all();
        return json(results || [], cors);
      }

      // Cancel my booking (customer can cancel their own pending booking)
      if (p === "/api/cancel-my-booking" && request.method === "POST") {
        const { booking_id, uid } = await request.json();
        if (!booking_id || !uid) return json({ success: false, error: "Missing params" }, cors);
        // Only allow cancelling their own pending bookings
        const bk = await env.DB.prepare("SELECT id FROM bookings WHERE id=? AND uid=? AND status='pending'").bind(booking_id, uid).first();
        if (!bk) return json({ success: false, error: "ไม่พบรายการ หรือไม่สามารถยกเลิกได้" }, cors);
        await env.DB.prepare("UPDATE bookings SET status='cancelled' WHERE id=?").bind(booking_id).run();
        return json({ success: true }, cors);
      }

      // Concert ticket count & status map
      if (p === "/api/concert-status") {
        const date = url.searchParams.get("date");
        const statusMap = {};

        // 1. Get Concert Tickets
        const { results: tickets } = await env.DB.prepare("SELECT zone, status FROM concert_tickets WHERE status IN ('paid', 'pending')").all();
        tickets.forEach(t => {
          statusMap[t.zone] = t.status === 'paid' ? 'occupied' : 'pending';
        });

        // 2. Get Normal Bookings for specific date
        const queryDate = date || new Date().toISOString().split('T')[0];
        const { results: bookings } = await env.DB.prepare("SELECT table_number, status FROM bookings WHERE date=? AND status != 'cancelled'").bind(queryDate).all();
        bookings.forEach(b => {
          if (b.table_number) {
            const nums = b.table_number.split(', ');
            nums.forEach(n => {
              statusMap[n.trim()] = b.status === 'confirmed' ? 'occupied' : 'pending';
            });
          }
        });

        return json(statusMap, cors);
      }

      // Buy ticket
      if (p === "/api/buy-ticket" && request.method === "POST") {
        const form = await request.formData();
        const uid = form.get("uid");
        const zone = form.get("zone");
        const qty = parseInt(form.get("qty") || "1");
        const total = parseInt(form.get("total") || "0");
        const slip = form.get("slip");
        let slip_key = null;
        if (slip && slip.size > 0) {
          slip_key = `slip_${Date.now()}.jpg`;
          await env.BUCKET.put(slip_key, slip.stream());
        }
        const signature = btoa(`${uid}-${zone}-${Date.now()}`).slice(0, 12);
        await env.DB.prepare("INSERT INTO concert_tickets (uid,zone,qty,total,slip_key,status,signature) VALUES(?,?,?,?,?,'pending',?)").bind(uid, zone, qty, total, slip_key, signature).run();
        await notifyAdmins(env, `\n🎫 ซื้อบัตรใหม่!\nZone: ${zone} x${qty}\nราคา: ${total} บาท\nUID: ${uid}`);
        return json({ success: true, signature }, cors);
      }

      // ==================== DEPOSIT CODE ====================
      if (p === "/api/get-next-code") {
        const last = await env.DB.prepare("SELECT id FROM deposits ORDER BY id DESC LIMIT 1").first();
        const nextId = (last?.id || 0) + 1;
        return json({ success: true, code: nextId.toString().padStart(5, "0") }, cors);
      }

      // ==================== STAFF ====================

      // Staff login
      if (p === "/api/staff-login" && request.method === "POST") {
        const { uid, password, name } = await request.json();
        const correctPassword = env.MANAGER_PASSWORD || "7777"; // fallback to 7777 if secret not set
        if (password === correctPassword) {
          await env.DB.prepare("INSERT OR REPLACE INTO staff_access (uid,name,role,status) VALUES(?,?,'manager','active')").bind(uid, name || "Manager").run();
          return json({ success: true, role: "manager" }, cors);
        }
        return json({ success: false, error: "รหัสผ่านไม่ถูกต้อง" }, cors);
      }

      // Deposit (staff records a new deposit)
      if (p === "/api/deposit" && request.method === "POST") {
        try {
          const form = await request.formData();
          const staff_uid = form.get("staff_uid");
          if (!staff_uid || !await verifyRole(staff_uid, env)) {
            return json({ success: false, error: "Unauthorized or missing Staff UID" }, cors, 403);
          }

          const phone = form.get("phone") || "";
          const brand = form.get("brand") || "";
          const amountStr = form.get("amount");
          const pointsStr = form.get("points");
          const deposit_code = form.get("deposit_code") || "";
          const image = form.get("image");

          if (!brand || !amountStr) {
            return json({ success: false, error: "Missing required fields (brand, amount)" }, cors, 400);
          }

          const amount = parseInt(amountStr);
          if (isNaN(amount) || amount < 1) {
            return json({ success: false, error: "Invalid amount" }, cors, 400);
          }

          const points = parseInt(pointsStr || "0");

          const profile = await env.DB.prepare("SELECT uid,name FROM user_profiles WHERE phone=?").bind(phone).first();
          const owner_uid = profile?.uid || null;
          const expiry_date = new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0];

          let image_key = null;
          if (image && image.size > 0) {
            image_key = `dep_${Date.now()}.jpg`;
            await env.BUCKET.put(image_key, image.stream());
          }

          await env.DB.prepare("INSERT INTO deposits (item_name,amount,owner_phone,owner_uid,image_key,status,staff_uid,depositor_name,expiry_date,deposit_code) VALUES(?,?,?,?,?,'active',?,?,?,?)")
            .bind(brand, amount, phone, owner_uid || null, image_key || null, staff_uid, profile?.name || "ไม่ระบุ", expiry_date, deposit_code).run();

          if (phone && points > 0) {
            await env.DB.prepare("UPDATE user_profiles SET points=points+? WHERE phone=?").bind(points, phone).run();
            await env.DB.prepare("INSERT INTO point_logs (phone,amount,action,staff_uid) VALUES(?,?,'deposit',?)").bind(phone, points, staff_uid).run();
          }
          return json({ success: true }, cors);
        } catch (e) {
          return json({ success: false, error: "Server Error: " + e.message }, cors, 500);
        }
      }

      // Search (by phone or 5-digit code)
      if (p === "/api/staff-search") {
        const phone = url.searchParams.get("phone");
        const code = url.searchParams.get("code");
        let user = null, deposits = [], coupons = [];
        
        if (phone) {
          user = await env.DB.prepare("SELECT * FROM user_profiles WHERE phone=?").bind(phone).first();
          const r = await env.DB.prepare("SELECT d.*, s.name as staff_name, w.name as withdrawn_by_name FROM deposits d LEFT JOIN staff_access s ON d.staff_uid=s.uid LEFT JOIN staff_access w ON d.withdrawn_by=w.uid WHERE (d.owner_phone=? OR d.deposit_code=?) AND d.status IN ('active', 'withdrawn')").bind(phone, phone).all();
          deposits = r.results;
          
          if (user) {
            const rc = await env.DB.prepare(`
              SELECT r.*, w.image_key 
              FROM redemptions r 
              LEFT JOIN rewards w ON r.reward_id = w.id 
              WHERE r.uid=? AND r.status='pending'
            `).bind(user.uid).all();
            coupons = rc.results;
          }
        } else if (code) {
          const r = await env.DB.prepare("SELECT d.*, s.name as staff_name, w.name as withdrawn_by_name FROM deposits d LEFT JOIN staff_access s ON d.staff_uid=s.uid LEFT JOIN staff_access w ON d.withdrawn_by=w.uid WHERE (d.deposit_code=? OR d.id=?) AND d.status IN ('active', 'withdrawn')").bind(code, parseInt(code) || 0).all();
          deposits = r.results;
          if (deposits[0]?.owner_phone) {
            user = await env.DB.prepare("SELECT * FROM user_profiles WHERE phone=?").bind(deposits[0].owner_phone).first();
            if (user) {
              const rc = await env.DB.prepare(`
                SELECT r.*, w.image_key 
                FROM redemptions r 
                LEFT JOIN rewards w ON r.reward_id = w.id 
                WHERE r.uid=? AND r.status='pending'
              `).bind(user.uid).all();
              coupons = rc.results;
            }
          }
        }
        
        const mappedDeposits = deposits.map(d => ({
          ...d,
          image_url: d.image_key ? `${url.origin}/api/image/${d.image_key}` : null
        }));
        
        const mappedCoupons = coupons.map(c => ({
          ...c,
          image_url: c.image_key ? `${url.origin}/api/image/${c.image_key}` : null
        }));
        
        return json({ user, deposits: mappedDeposits, coupons: mappedCoupons }, cors);
      }

      // Withdraw
      if (p === "/api/staff-withdraw" && request.method === "POST") {
        try {
          const { deposit_id, staff_uid } = await request.json();
          if (!deposit_id) return json({ success: false, error: "Missing deposit ID" }, cors, 400);
          if (!staff_uid || !await verifyRole(staff_uid, env)) return json({ success: false, error: "Unauthorized" }, cors, 403);

          await env.DB.prepare("UPDATE deposits SET status='withdrawn',withdrawn_at=CURRENT_TIMESTAMP,withdrawn_by=? WHERE id=?").bind(staff_uid, deposit_id).run();
          return json({ success: true }, cors);
        } catch (e) {
          return json({ success: false, error: "Server Error: " + e.message }, cors, 500);
        }
      }

      // All deposits (stock view)
      if (p === "/api/all-deposits") {
        const { results } = await env.DB.prepare("SELECT d.*,u.name as customer_name, s.name as staff_name, w.name as withdrawn_by_name FROM deposits d LEFT JOIN user_profiles u ON d.owner_uid=u.uid LEFT JOIN staff_access s ON d.staff_uid=s.uid LEFT JOIN staff_access w ON d.withdrawn_by=w.uid WHERE d.status='active' ORDER BY d.created_at DESC").all();
        const mapped = (results || []).map(d => ({
          ...d,
          image_url: d.image_key ? `${url.origin}/api/image/${d.image_key}` : null
        }));
        return json(mapped, cors);
      }

      // Staff list
      if (p === "/api/staff-list") {
        const { results } = await env.DB.prepare("SELECT uid,name,role,status FROM staff_access ORDER BY role,name").all();
        return json(results, cors);
      }

      // Approve staff
      if (p === "/api/approve-staff" && request.method === "POST") {
        const { uid } = await request.json();
        await env.DB.prepare("UPDATE staff_access SET status='active' WHERE uid=?").bind(uid).run();
        return json({ success: true }, cors);
      }

      // Revoke staff
      if (p === "/api/revoke-staff" && request.method === "POST") {
        const { uid } = await request.json();
        await env.DB.prepare("UPDATE staff_access SET status='inactive' WHERE uid=?").bind(uid).run();
        return json({ success: true }, cors);
      }

      // Bookings list
      if (p === "/api/bookings-list") {
        const { results } = await env.DB.prepare("SELECT * FROM bookings ORDER BY date DESC,time DESC").all();
        return json(results, cors);
      }

      // Confirm booking
      if (p === "/api/confirm-booking" && request.method === "POST") {
        const { id, staff_uid } = await request.json();
        if (!await verifyRole(staff_uid, env)) return json({ success: false, error: "Unauthorized" }, cors, 403);
        await env.DB.prepare("UPDATE bookings SET status='confirmed' WHERE id=?").bind(id).run();
        return json({ success: true }, cors);
      }

      // Rewards management (POST = create or delete)
      if (p === "/api/rewards" && request.method === "POST") {
        let data;
        const ct = request.headers.get("Content-Type") || "";
        if (ct.includes("json")) data = await request.json();
        else data = await request.formData();

        const isDelete = request.headers.get("X-HTTP-Method-Override") === "DELETE" || data?._method === "DELETE";
        if (isDelete) {
          const rid = data.id;
          const staff_uid = data.staff_uid;
          if (!await verifyRole(staff_uid, env, ["manager"])) return json({ success: false, error: "Manager Only" }, cors, 403);
          await env.DB.prepare("DELETE FROM rewards WHERE id=?").bind(rid).run();
          return json({ success: true }, cors);
        }

        const name = data.get ? data.get("name") : data.name;
        const points = parseInt((data.get ? data.get("points") : data.points) || "0");
        const image = data.get ? data.get("image") : null;
        const staff_uid = data.get ? data.get("staff_uid") : data.staff_uid;
        if (!await verifyRole(staff_uid, env, ["manager"])) return json({ success: false, error: "Manager Only" }, cors, 403);
        let image_key = null;
        if (image && image.size > 0) {
          image_key = `reward_${Date.now()}.jpg`;
          await env.BUCKET.put(image_key, image.stream());
        }
        await env.DB.prepare("INSERT INTO rewards (name,points,image_key) VALUES(?,?,?)").bind(name, points, image_key).run();
        return json({ success: true }, cors);
      }

      // Admin use coupon (Staff confirms use)
      if (p === "/api/admin/use-coupon" && request.method === "POST") {
        const { coupon_id, staff_uid } = await request.json();
        if (!await verifyRole(staff_uid, env, ["manager", "staff"])) return json({ success: false, error: "Unauthorized" }, cors, 403);
        
        // Delete record to save space
        await env.DB.prepare("DELETE FROM redemptions WHERE id=?").bind(coupon_id).run();
        return json({ success: true }, cors);
      }

      // ==================== CONCERT ADMIN ====================

      // Concert deposits list (admin)
      if (p === "/api/admin/concert-deposits") {
        const staff_uid = url.searchParams.get("staff_uid");
        if (!await verifyRole(staff_uid, env)) return json({ success: false, error: "Unauthorized" }, cors, 403);
        const { results } = await env.DB.prepare("SELECT t.*,u.name as customer_name FROM concert_tickets t LEFT JOIN user_profiles u ON t.uid=u.uid ORDER BY t.created_at DESC").all();
        return json(results.map(t => ({ ...t, image_url: t.slip_key ? `${url.origin}/api/image/${t.slip_key}` : null })), cors);
      }

      // Verify ticket (approve payment)
      if (p === "/api/admin/verify-ticket" && request.method === "POST") {
        const { ticket_id, staff_uid } = await request.json();
        if (!await verifyRole(staff_uid, env)) return json({ success: false, error: "Unauthorized" }, cors, 403);
        await env.DB.prepare("UPDATE concert_tickets SET status='paid' WHERE id=?").bind(ticket_id).run();
        return json({ success: true }, cors);
      }

      // Scan ticket (check-in)
      if (p === "/api/admin/scan-ticket" && request.method === "POST") {
        const { ticket_id, staff_uid } = await request.json();
        if (!await verifyRole(staff_uid, env)) return json({ success: false, error: "Unauthorized" }, cors, 403);
        const ticket = await env.DB.prepare("SELECT * FROM concert_tickets WHERE id=?").bind(ticket_id).first();
        if (!ticket) return json({ success: false, error: "ไม่พบบัตร" }, cors);
        if (ticket.status === "used") return json({ success: false, error: "บัตรถูกใช้ไปแล้ว" }, cors);
        await env.DB.prepare("UPDATE concert_tickets SET status='used',used_at=CURRENT_TIMESTAMP WHERE id=?").bind(ticket_id).run();
        return json({ success: true, ticket }, cors);
      }

      // Update concert event settings
      if (p === "/api/admin/concert-event" && request.method === "POST") {
        const form = await request.formData();
        const staff_uid = form.get("staff_uid");
        if (!await verifyRole(staff_uid, env, ["manager"])) return json({ success: false, error: "Manager Only" }, cors, 403);
        const title = form.get("title");
        const date = form.get("date");
        const poster = form.get("poster");
        let poster_key = null;
        if (poster && poster.size > 0) {
          poster_key = `poster_${Date.now()}.jpg`;
          await env.BUCKET.put(poster_key, poster.stream());
        }
        await env.DB.prepare("INSERT INTO concert_event (id,title,date,poster_key) VALUES(1,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,date=excluded.date,poster_key=COALESCE(excluded.poster_key,poster_key)")
          .bind(title, date, poster_key).run();
        return json({ success: true }, cors);
      }

      if (p === "/api/admin/add-points" && request.method === "POST") {
        try {
          const { phone, points, staff_uid, actor_name } = await request.json();
          if (!phone || points === undefined) return json({ success: false, error: "Missing required fields" }, cors, 400);

          const pts = parseInt(points);
          if (isNaN(pts) || pts <= 0) return json({ success: false, error: "Invalid points amount" }, cors, 400);

          if (!await verifyRole(staff_uid, env, ["manager", "staff"])) return json({ success: false, error: "Staff/Manager Required" }, cors, 403);
          const user = await env.DB.prepare("SELECT * FROM user_profiles WHERE phone=?").bind(phone).first();
          if (!user) return json({ success: false, error: "ไม่พบข้อมูลลูกค้านี้ในระบบ (รอให้ลูกค้าเข้าสู่ระบบผ่าน LINE อย่างน้อย 1 ครั้ง)" }, cors);
          await env.DB.prepare("UPDATE user_profiles SET points=points+? WHERE phone=?").bind(pts, phone).run();

          const loggerId = actor_name ? `${actor_name}` : staff_uid;
          await env.DB.prepare("INSERT INTO point_logs (phone,amount,action,staff_uid) VALUES(?,?,'add_points',?)").bind(phone, pts, loggerId).run();

          return json({ success: true }, cors);
        } catch (e) {
          return json({ success: false, error: "Server Error: " + e.message }, cors, 500);
        }
      }

      // ==================== DASHBOARD & ANALYTICS ====================
      if (p === "/api/admin/dashboard") {
        const staff_uid = url.searchParams.get("staff_uid");
        if (!await verifyRole(staff_uid, env, ["manager"])) return json({ success: false, error: "Manager Required" }, cors, 403);

        try {
          // 1. Owner Summary
          const bottles = await env.DB.prepare("SELECT COUNT(*) as total FROM deposits WHERE status='active'").first();
          const points = await env.DB.prepare("SELECT SUM(points) as total FROM user_profiles").first();
          const performance = await env.DB.prepare(`
            SELECT COALESCE(s.name, d.staff_uid) as staff_name, COUNT(*) as count 
            FROM deposits d 
            LEFT JOIN staff_access s ON d.staff_uid=s.uid 
            WHERE date(d.created_at) = date('now') 
            GROUP BY staff_name ORDER BY count DESC LIMIT 5
          `).all();

          // 2. CRM - Inactive (No activity > 21 days but has bottles)
          const inactive = await env.DB.prepare(`
            SELECT u.name, u.phone, u.points, COUNT(d.id) as bottle_count, MAX(d.created_at) as last_active 
            FROM user_profiles u 
            JOIN deposits d ON u.uid=d.owner_uid 
            WHERE d.status='active' 
            GROUP BY u.uid 
            HAVING last_active < date('now', '-21 days') 
            ORDER BY last_active DESC LIMIT 15
          `).all();

          // 3. CRM - Birthday (This week)
          const birthday = await env.DB.prepare(`
            SELECT name, phone, points, birthday 
            FROM user_profiles 
            WHERE birthday IS NOT NULL 
            AND strftime('%m-%d', birthday) BETWEEN strftime('%m-%d', 'now') AND strftime('%m-%d', 'now', '+7 days')
            ORDER BY strftime('%m-%d', birthday) LIMIT 15
          `).all();

          // 4. CRM - Whales (Top Points)
          const whales = await env.DB.prepare(`
            SELECT name, phone, points 
            FROM user_profiles 
            ORDER BY points DESC LIMIT 15
          `).all();

          return json({
            success: true,
            owner: {
              total_bottles: bottles.total || 0,
              total_points: points.total || 0,
              staff_performance: performance.results
            },
            crm: {
              inactive: inactive.results,
              birthday: birthday.results,
              whales: whales.results
            }
          }, cors);
        } catch (e) {
          return json({ success: false, error: e.message }, cors, 500);
        }
      }

      // ==================== BROADCAST / CRM ====================
      if (p === "/api/broadcast" && request.method === "POST") {
        let target, message, format, minPoints, reward, staff_uid, image, birthStart, birthEnd;

        const contentType = request.headers.get("content-type") || "";
        if (contentType.includes("multipart/form-data")) {
          const form = await request.formData();
          target = form.get("target");
          message = form.get("message");
          format = form.get("format");
          minPoints = parseInt(form.get("minPoints") || "0");
          staff_uid = form.get("staff_uid");
          image = form.get("image");
          birthStart = form.get("birthStart");
          birthEnd = form.get("birthEnd");
        } else {
          const data = await request.json();
          target = data.target;
          message = data.message;
          format = data.format;
          minPoints = data.minPoints;
          reward = data.reward;
          staff_uid = data.staff_uid;
          birthStart = data.birthStart;
          birthEnd = data.birthEnd;
        }

        if (!await verifyRole(staff_uid, env, ["manager"])) return json({ success: false, error: "Manager Required" }, cors, 403);
        const botToken = env.LINE_OA_TOKEN || CONFIG.LINE_OA_TOKEN;
        if (!botToken) return json({ success: false, error: "LINE_OA_TOKEN ยังไม่ได้ตั้งค่า กรุณาตั้งค่าใน Cloudflare Dashboard" }, cors);

        // Upload custom image if provided
        let customImageUrl = null;
        if (image && image.size > 0) {
          const imageKey = `broadcast_${Date.now()}.jpg`;
          await env.BUCKET.put(imageKey, image.stream());
          customImageUrl = `${url.origin}/api/image/${imageKey}`;
        }

        let query = "SELECT uid FROM user_profiles WHERE uid IS NOT NULL AND uid != ''";
        let params = [];
        if (target === "birthday") {
          const isDateRange = birthStart && birthStart.includes('-') && birthEnd && birthEnd.includes('-');
          if (isDateRange) {
            const startMD = birthStart.split('-').slice(1).join('-'); // MM-DD
            const endMD = birthEnd.split('-').slice(1).join('-'); // MM-DD
            query = "SELECT uid FROM user_profiles WHERE uid IS NOT NULL AND uid !=''";
            if (startMD <= endMD) {
              query += " AND strftime('%m-%d', birthday) BETWEEN ? AND ?";
              params.push(startMD, endMD);
            } else {
              query += " AND (strftime('%m-%d', birthday) >= ? OR strftime('%m-%d', birthday) <= ?)";
              params.push(startMD, endMD);
            }
          } else {
            query = "SELECT uid FROM user_profiles WHERE uid IS NOT NULL AND uid!='' AND strftime('%m',birthday)=strftime('%m','now')";
            if (birthStart && birthEnd) {
              query += " AND CAST(strftime('%d', birthday) AS INTEGER) BETWEEN ? AND ?";
              params.push(parseInt(birthStart), parseInt(birthEnd));
            }
          }
        } else if (target === "points") {
          query = "SELECT uid FROM user_profiles WHERE uid IS NOT NULL AND uid!='' AND points>=?";
          params = [minPoints || 0];
        } else if (target === "active_depositors") {
          query = "SELECT DISTINCT owner_uid as uid FROM deposits WHERE status='active' AND owner_uid IS NOT NULL AND owner_uid!=''";
        }
        const { results } = await env.DB.prepare(query).bind(...params).all();
        const uids = results.map(r => r.uid).filter(Boolean);
        if (!uids.length) return json({ success: false, error: `ไม่พบผู้รับ (${target})` }, cors);

        let messages = [];
        if (format === "flex") {
          if (reward) {
            messages.push(rewardFlex(reward.name, reward.points || 0, reward.img, url.origin));
          } else {
            messages.push({ type: "text", text: message || "📢 แจ้งจากทางร้านค่ะ" });
          }
        } else if (format === "image_text") {
          let imgUrl = (customImageUrl || reward?.img || "https://v90-crm-test-web.pages.dev/app_icon.png").replace("http://", "https://");
          if (imgUrl.startsWith("/")) imgUrl = url.origin.replace("http://", "https://") + imgUrl;
          
          messages.push({ 
            type: "image", 
            originalContentUrl: imgUrl, 
            previewImageUrl: imgUrl 
          });
          messages.push({ 
            type: "text", 
            text: (message || (reward ? `แนะนำของรางวัล: ${reward.name}` : "📢 แจ้งจากทางร้านค่ะ")).substring(0, 5000) 
          });
        } else {
          messages.push({ type: "text", text: (message || "📢 แจ้งจากทางร้านค่ะ").substring(0, 5000) });
        }
        const bc = await broadcastLine(botToken, uids, messages);
        // Removed broadcast log to chat
        // await notifyAdmins(env, `\n📢 Broadcast: ${target}\nจำนวน: ${uids.length} คน\nสำเร็จ: ${bc.success}`);
        
        let errorMessage = null;
        if (!bc.success) {
          errorMessage = bc.error || (bc.detail ? bc.detail.find(d => !d.ok)?.body?.message : "LINE API Error");
          if (bc.detail && !errorMessage) errorMessage = JSON.stringify(bc.detail);
        }
        
        return json({ success: bc.success, count: uids.length, detail: bc.detail, error: errorMessage }, cors);
      }

      // ==================== NOTIFICATIONS ====================
      if (p === "/api/notify-expiring") {
        await doExpiryNotify(env);
        return json({ success: true }, cors);
      }

      if (p === "/api/notify-deposit" && request.method === "POST") {
        const { deposit_id } = await request.json();
        const dep = await env.DB.prepare("SELECT d.*,u.name as customer_name,u.uid as owner_uid FROM deposits d LEFT JOIN user_profiles u ON d.owner_uid=u.uid WHERE d.id=?").bind(deposit_id).first();
        if (!dep) return json({ success: false, error: "ไม่พบข้อมูล" }, cors);
        const daysLeft = Math.ceil((new Date(dep.expiry_date) - new Date()) / 86400000);
        const botToken = env.LINE_OA_TOKEN || CONFIG.LINE_OA_TOKEN;
        if (dep.owner_uid && botToken) {
          await broadcastLine(botToken, [dep.owner_uid], [{
            type: "text",
            text: `⚠️ แจ้งเตือนจากร้านค่ะ!\n\nขวด "${dep.item_name}" ของคุณใกล้หมดอายุแล้ว\n📅 หมดอายุ: ${dep.expiry_date}\n⏳ เหลืออีก ${daysLeft} วัน\n\nแวะมาเบิกหรือต่ออายุได้เลยค่ะ 🙏`
          }]);
        }
        // Removed notification log to chat
        // await notifyAdmins(env, `\n📦 แจ้งลูกค้าแล้ว\nขวด: ${dep.item_name}\nเจ้าของ: ${dep.customer_name || dep.owner_phone}\nหมดอายุ: ${dep.expiry_date}`);
        return json({ success: true }, cors);
      }

      // ==================== IMAGE SERVE ====================
      if (p.startsWith("/api/image/")) {
        const key = p.split("/").pop();
        const obj = await env.BUCKET.get(key);
        if (!obj) return new Response("Not Found", { status: 404 });
        return new Response(obj.body, { headers: { "Content-Type": "image/jpeg", ...cors } });
      }

      return new Response("Not Found", { status: 404, headers: cors });

    } catch (e) {
      return json({ error: e.message, stack: e.stack }, getCors(request.headers.get("Origin") || ""), 500);
    }
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(doExpiryNotify(env));
    ctx.waitUntil(cleanupResources(env));
  }
};

async function doExpiryNotify(env) {
  for (const days of [15, 7, 3, 1]) {
    const target = new Date(Date.now() + days * 86400000).toISOString().split("T")[0];
    const { results } = await env.DB.prepare("SELECT d.*,u.name as customer_name FROM deposits d LEFT JOIN user_profiles u ON d.owner_uid=u.uid WHERE d.expiry_date=? AND d.status='active'").bind(target).all();
    const botToken = env.LINE_TOKEN || env.LINE_OA_TOKEN || CONFIG.LINE_OA_TOKEN;
    for (const dep of results) {
      if (botToken) {
        await fetch("https://notify-api.line.me/api/notify", {
          method: "POST",
          headers: { Authorization: `Bearer ${botToken}`, "Content-Type": "application/x-www-form-urlencoded" },
          body: `message=${encodeURIComponent(`\n⚠️ หมดอายุใน ${days} วัน!\nรหัส: ${dep.deposit_code || dep.id}\nขวด: ${dep.item_name}\nเจ้าของ: ${dep.customer_name || dep.owner_phone}\nหมดอายุ: ${dep.expiry_date}`)}`
        });
      }
    }
  }
}

async function cleanupResources(env) {
  try {
    // 1. Find withdrawn items older than 60 days to purge images & data
    const sixtyDaysAgo = new Date(Date.now() - 60 * 86400000).toISOString();
    const { results: oldItems } = await env.DB.prepare("SELECT id, image_key FROM deposits WHERE (status='withdrawn' AND withdrawn_at < ?) OR (status='active' AND expiry_date < ?)").bind(sixtyDaysAgo, sixtyDaysAgo).all();

    for (const item of oldItems) {
      if (item.image_key) {
        await env.BUCKET.delete(item.image_key); // Remove from R2
      }
      await env.DB.prepare("DELETE FROM deposits WHERE id = ?").bind(item.id).run(); // Remove from D1
    }

    console.log(`Cleanup completed: Purged ${oldItems.length} old deposit entries.`);
  } catch (e) {
    console.error("Cleanup Error:", e);
  }
}
