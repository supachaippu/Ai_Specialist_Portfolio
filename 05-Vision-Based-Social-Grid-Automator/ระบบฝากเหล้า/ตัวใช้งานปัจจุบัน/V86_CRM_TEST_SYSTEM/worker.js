
const CONFIG = { 
  MANAGER_PASSWORD: "7777",
  LINE_OA_TOKEN: "vnfhgghoPDvWOvqpPyZKdqmkgh5Y2uZRd6ugUbyRpJpNRzzTjpSwlpAmk479lUg5G38YQuJPKU/YaG+AYJlmjBG1anrmZqC6KpvJesRRa5eGaXs1ZgkzFKkCd/zicckoIhA/VgYMDIB92gNR9+45BwdB04t89/1O/w1cDnyilFU="
};

async function sendLineNotify(token, message) {
  return fetch("https://notify-api.line.me/api/notify", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: `message=${encodeURIComponent(message)}`
  });
}

export default {
  // ========== HTTP Requests ==========
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "*",
      "Access-Control-Allow-Headers": "*"
    };

    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    try {
      // 1. User Profile & Status
      if (path === "/api/me") {
        const uid = url.searchParams.get('uid');
        const user = await env.DB.prepare("SELECT * FROM user_profiles WHERE uid = ?").bind(uid).first();
        const staff = await env.DB.prepare("SELECT role, status FROM staff_access WHERE uid = ?").bind(uid).first();
        return new Response(JSON.stringify({
          phone: user ? user.phone : null,
          points: user ? user.points : 0,
          role: staff ? staff.role : 'customer',
          status: staff ? staff.status : null,
          name: user ? user.name : 'Guest'
        }), { headers: cors });
      }

      // 2. Auth & Registration
      if (path === "/api/staff-login" && request.method === "POST") {
        const { password } = await request.json();
        let correctPin = "7777";
        try {
          const settingsRes = await env.DB.prepare("SELECT value FROM settings WHERE key = 'pin_system'").first();
          if (settingsRes && settingsRes.value) correctPin = settingsRes.value;
        } catch (dbErr) {
          console.error("DB PIN Error:", dbErr.message);
        }

        if (password === correctPin) {
          return new Response(JSON.stringify({ success: true }), { headers: cors });
        }
        return new Response(JSON.stringify({ success: false, error: "รหัสผ่านไม่ถูกต้อง" }), { headers: cors });
      }

      // -- การขอสิทธิ์พนักงาน (Staff Request) --
      if (path === "/api/request-staff" && request.method === "POST") {
        const { uid, name } = await request.json();
        // เพิ่ม role 'staff' แต่ให้ status เป็น 'pending' ไปก่อน รออนุมัติ
        // หากเคยขอไปแล้วหรือเคยเป็น จะใช้ INSERT OR REPLACE เพื่ออัปเดตชื่อและ status
        await env.DB.prepare("INSERT OR REPLACE INTO staff_access (uid, name, role, status) VALUES (?, ?, 'staff', 'pending')")
          .bind(uid, name).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      // -- จัดการรายชื่อพนักงานและอนุมัติ (Manager) --
      if (path === "/api/staff-list" && request.method === "GET") {
        // ดึงมาทั้งคนที่ขอสิทธิ์มา (pending) และคนที่เป็นพนักงานอยู่แล้ว (active)
        const res = await env.DB.prepare("SELECT * FROM staff_access WHERE status IN ('active', 'pending') ORDER BY status DESC, role").all();
        return new Response(JSON.stringify(res.results || []), { headers: cors });
      }

      if (path === "/api/approve-staff" && request.method === "POST") {
        const { target_uid } = await request.json();
        await env.DB.prepare("UPDATE staff_access SET status = 'active' WHERE uid = ?").bind(target_uid).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/revoke-staff" && request.method === "POST") {
        const { target_uid } = await request.json();
        await env.DB.prepare("UPDATE staff_access SET status = 'inactive' WHERE uid = ?").bind(target_uid).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/link-phone" && request.method === "POST") {
        const { uid, phone, name } = await request.json();
        await env.DB.prepare("INSERT INTO user_profiles (uid, phone, name, points) VALUES (?, ?, ?, 50) ON CONFLICT(uid) DO UPDATE SET phone=excluded.phone, name=excluded.name")
          .bind(uid, phone, name).run();
        await env.DB.prepare("UPDATE deposits SET owner_uid = ? WHERE owner_phone = ? AND (owner_uid IS NULL OR owner_uid = '')")
          .bind(uid, phone).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/reset-me" && request.method === "POST") {
        const { uid } = await request.json();
        if (!uid) return new Response(JSON.stringify({ success: false }), { headers: cors });
        await env.DB.prepare("DELETE FROM user_profiles WHERE uid = ?").bind(uid).run();
        await env.DB.prepare("DELETE FROM staff_access WHERE uid = ?").bind(uid).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      // 3. Deposit & Wallet
      if (path === "/api/get-next-code") {
        const last = await env.DB.prepare("SELECT deposit_code FROM deposits WHERE deposit_code GLOB '[0-9]*' ORDER BY CAST(deposit_code AS INTEGER) DESC LIMIT 1").first();
        let nextCode = 10001;
        if (last && last.deposit_code) {
          nextCode = parseInt(last.deposit_code) + 1;
        }
        return new Response(JSON.stringify({ success: true, code: nextCode.toString() }), { headers: cors });
      }

      if (path === "/api/deposit" && request.method === "POST") {
        const form = await request.formData();
        const image = form.get('image');
        const phone = form.get('phone');
        const brand = form.get('brand');
        const amount = form.get('amount');
        const points = parseInt(form.get('points') || '0');
        const staff_uid = form.get('staff_uid');
        const deposit_code = form.get('deposit_code');

        if (!deposit_code) return new Response(JSON.stringify({ success: false, error: "Missing Deposit Code" }), { headers: cors });

        // Check for Collision
        const exists = await env.DB.prepare("SELECT id FROM deposits WHERE deposit_code = ? AND status != 'withdrawn'").bind(deposit_code).first();
        if (exists) {
          return new Response(JSON.stringify({ success: false, error: "รหัสซ้ำ (Duplicate) กรุณากดปุ่มรีเฟรชรหัสใหม่" }), { headers: cors });
        }

        const profile = await env.DB.prepare("SELECT uid, name FROM user_profiles WHERE phone = ?").bind(phone).first();
        const owner_uid = profile ? profile.uid : null;
        const depositor_name = profile ? profile.name : 'ไม่ระบุ';

        // คำนวณวันหมดอายุ 30 วัน
        const now = new Date();
        const expiry = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
        const expiry_date = expiry.toISOString().split('T')[0];

        let filename = null;
        if (image && image.size > 0) {
          filename = `v86_${Date.now()}.jpg`;
          await env.BUCKET.put(filename, image);
        }

        // Status is 'pending_claim' if no owner_uid, otherwise 'active'
        const status = owner_uid ? 'active' : 'pending_claim';

        await env.DB.prepare("INSERT INTO deposits (item_name, amount, owner_phone, owner_uid, image_key, status, staff_uid, depositor_name, expiry_date, deposit_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
          .bind(brand, amount, phone, owner_uid, filename, status, staff_uid, depositor_name, expiry_date, deposit_code).run();

        if (phone && points > 0 && owner_uid) {
          await env.DB.prepare("UPDATE user_profiles SET points = points + ? WHERE phone = ?").bind(points, phone).run();
          await env.DB.prepare("INSERT INTO point_logs (phone, amount, action, staff_uid) VALUES (?, ?, 'deposit', ?)")
            .bind(phone, points, staff_uid).run();
        }

        return new Response(JSON.stringify({ success: true, code: deposit_code }), { headers: cors });
      }

      if (path === "/api/claim" && request.method === "POST") {
        const { code, uid, name } = await request.json();
        // Claim the oldest pending bottle with this code
        const res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, depositor_name = ?, status = 'active' WHERE id = (SELECT id FROM deposits WHERE deposit_code = ? AND status = 'pending_claim' ORDER BY id ASC LIMIT 1)")
          .bind(uid, name, code).run();

        if (res.meta.changes > 0) {
          return new Response(JSON.stringify({ success: true }), { headers: cors });
        }
        return new Response(JSON.stringify({ success: false, error: "รหัสไม่ถูกต้อง หรือถูกคนอื่นรับไปแล้ว" }), { headers: cors });
      }

      if (path === "/api/my-wallet") {
        const uid = url.searchParams.get('uid');
        const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_uid = ? ORDER BY created_at DESC").bind(uid).all();
        const results = res.results.map(r => ({
          ...r,
          image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : null
        }));
        return new Response(JSON.stringify(results), { headers: cors });
      }

      // 4. CRM (Points & Rewards)
      // โหลดรายการของรางวัลทั้งหมด
      if (path === "/api/rewards") {
        const res = await env.DB.prepare("SELECT * FROM rewards_inventory WHERE status = 'active' ORDER BY points ASC").all();
        const results = res.results.map(r => ({
          ...r,
          image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : null
        }));
        return new Response(JSON.stringify(results), { headers: cors });
      }

      // สร้างของรางวัลใหม่ (สำหรับ Manager)
      if (path === "/api/create-reward" && request.method === "POST") {
        const form = await request.formData();
        const name = form.get('name');
        const points = parseInt(form.get('points') || '0');
        const image = form.get('image');

        if (!name || points <= 0) return new Response(JSON.stringify({ success: false, error: "Invalid data" }), { headers: cors });

        let imageKey = null;
        if (image && image.size > 0) {
          imageKey = `reward_${Date.now()}.jpg`;
          await env.BUCKET.put(imageKey, image);
        }

        try {
          await env.DB.prepare("INSERT INTO rewards_inventory (name, points, image_key) VALUES (?, ?, ?)")
            .bind(name, points, imageKey).run();
          return new Response(JSON.stringify({ success: true }), { headers: cors });
        } catch (dbErr) {
          return new Response(JSON.stringify({ success: false, error: dbErr.message }), { headers: cors });
        }
      }

      // ลบ/ซ่อน ของรางวัล (สำหรับ Manager)
      if (path === "/api/delete-reward" && request.method === "POST") {
        const data = await request.json();
        const rid = data.id || data.reward_id;
        if (!rid) return new Response(JSON.stringify({ success: false, error: "Missing ID" }), { headers: cors });
        await env.DB.prepare("UPDATE rewards_inventory SET status = 'inactive' WHERE id = ?").bind(rid).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      // ลูกค้ากดแลกแต้มรับคูปอง (เปลี่ยนเป็นให้คูปอง)
      if (path === "/api/redeem" && request.method === "POST") {
        const { uid, reward_id } = await request.json();
        const reward = await env.DB.prepare("SELECT * FROM rewards_inventory WHERE id = ? AND status = 'active'").bind(reward_id).first();
        if (!reward) return new Response(JSON.stringify({ success: false, error: "Reward not found" }), { headers: cors });

        const user = await env.DB.prepare("SELECT points, phone FROM user_profiles WHERE uid = ?").bind(uid).first();
        if (!user || user.points < reward.points) return new Response(JSON.stringify({ success: false, error: "Insufficient Points" }), { headers: cors });

        // ตัดแต้ม
        await env.DB.prepare("UPDATE user_profiles SET points = points - ? WHERE uid = ?").bind(reward.points, uid).run();

        // บันทึก Log
        await env.DB.prepare("INSERT INTO point_logs (phone, amount, action, staff_uid) VALUES (?, ?, ?, 'system')")
          .bind(user.phone, -reward.points, `redeem_${reward.name}`).run();

        // สร้างคูปองให้ลูกค้าเก็บไว้ใช้
        await env.DB.prepare("INSERT INTO user_coupons (owner_uid, reward_id, reward_name, reward_image_key, status) VALUES (?, ?, ?, ?, 'unused')")
          .bind(uid, reward.id, reward.name, reward.image_key).run();

        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      // โหลดคูปองของลูกค้า
      if (path === "/api/my-coupons") {
        const uid = url.searchParams.get('uid');
        const resUnused = await env.DB.prepare("SELECT * FROM user_coupons WHERE owner_uid = ? AND status = 'unused' ORDER BY created_at DESC").bind(uid).all();
        const resUsed = await env.DB.prepare("SELECT * FROM user_coupons WHERE owner_uid = ? AND status = 'used' ORDER BY used_at DESC").bind(uid).all();

        const formatData = (items) => items.map(r => ({
          ...r,
          image_url: r.reward_image_key ? `${url.origin}/api/image/${r.reward_image_key}` : null
        }));

        return new Response(JSON.stringify({
          unused: formatData(resUnused.results || []),
          used: formatData(resUsed.results || [])
        }), { headers: cors });
      }

      // พนักงานกดใช้คูปองให้ลูกค้า
      if (path === "/api/use-coupon" && request.method === "POST") {
        const { coupon_id, staff_uid } = await request.json();

        const coupon = await env.DB.prepare("SELECT * FROM user_coupons WHERE id = ? AND status = 'unused'").bind(coupon_id).first();
        if (!coupon) return new Response(JSON.stringify({ success: false, error: "Coupon already used or not found" }), { headers: cors });

        await env.DB.prepare("UPDATE user_coupons SET status = 'used', used_at = CURRENT_TIMESTAMP, used_by_staff = ? WHERE id = ?")
          .bind(staff_uid, coupon_id).run();

        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      // 5. Booking
      if (path === "/api/book-table" && request.method === "POST") {
        const { name, phone, date, time, pax } = await request.json();
        await env.DB.prepare("INSERT INTO bookings (name, phone, date, time, pax) VALUES (?, ?, ?, ?, ?)")
          .bind(name, phone, date, time, pax).run();

        // ส่ง LINE Notify แจ้งพนักงาน
        if (env.LINE_TOKEN) {
          const msg = `\n📅 จองโต๊ะใหม่!\nชื่อ: ${name}\nวันที่: ${date} เวลา ${time}\nจำนวน: ${pax} ท่าน\nโทร: ${phone || '-'}`;
          await sendLineNotify(env.LINE_TOKEN, msg);
        }

        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/bookings-list") {
        const res = await env.DB.prepare("SELECT * FROM bookings ORDER BY date ASC, time ASC LIMIT 50").all();
        return new Response(JSON.stringify(res.results), { headers: cors });
      }

      if (path === "/api/confirm-booking" && request.method === "POST") {
        const { booking_id, staff_uid } = await request.json();
        await env.DB.prepare("UPDATE bookings SET status = 'confirmed', confirmed_by = ? WHERE id = ?")
          .bind(staff_uid, booking_id).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      // 6. แจ้งเตือนวันหมดอายุ (manual trigger หรือ cron)
      if (path === "/api/notify-expiring") {
        const result = await notifyExpiringDeposits(env);
        return new Response(JSON.stringify(result), { headers: cors });
      }

      // แจ้งเตือนลูกค้าโดยตรงผ่าน Messaging API (Push Message)
      if (path === "/api/notify-deposit" && request.method === "POST") {
        const { deposit_id } = await request.json();
        const dep = await env.DB.prepare(
          "SELECT d.*, u.name as customer_name FROM deposits d LEFT JOIN user_profiles u ON d.owner_uid = u.uid WHERE d.id = ?"
        ).bind(deposit_id).first();

        if (!dep) return new Response(JSON.stringify({ success: false, error: "Not found" }), { headers: cors });

        if (!dep.owner_uid) {
          return new Response(JSON.stringify({ success: false, error: "ลูกค้ารายนี้ยังไม่ได้ผูกเบอร์กับ LINE (ไม่มี UID)" }), { headers: cors });
        }

        const today = new Date();
        const expiry = new Date(dep.expiry_date);
        const daysLeft = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));

        if (!env.LINE_OA_TOKEN) {
          return new Response(JSON.stringify({ success: false, error: "ยังไม่ได้ตั้งค่า LINE_OA_TOKEN ในระบบ" }), { headers: cors });
        }

        const urgencyColor = daysLeft <= 3 ? '#991b1b' : daysLeft <= 7 ? '#78350f' : '#1e3a8a';
        const urgencyText = daysLeft <= 1 ? '🚨 ด่วนมาก!' : daysLeft <= 3 ? '⚠️ ใกล้หมดมาก!' : '📢 แจ้งเตือน';

        const flexPayload = {
          type: "bubble", size: "mega",
          header: {
            type: "box", layout: "vertical",
            backgroundColor: urgencyColor, paddingAll: "20px",
            contents: [{ type: "text", text: `${urgencyText} เหล้าใกล้หมดอายุ!`, color: "#ffffff", weight: "bold", size: "lg" }]
          },
          body: {
            type: "box", layout: "vertical", spacing: "md",
            contents: [
              {
                type: "box", layout: "horizontal", contents: [
                  { type: "text", text: "เหล้า", color: "#aaaaaa", size: "md", flex: 2 },
                  { type: "text", text: dep.item_name || '-', weight: "bold", size: "md", flex: 4 }
                ]
              },
              {
                type: "box", layout: "horizontal", contents: [
                  { type: "text", text: "ปริมาณ", color: "#aaaaaa", size: "md", flex: 2 },
                  { type: "text", text: `${dep.amount || '?'}%`, weight: "bold", size: "md", flex: 4 }
                ]
              },
              {
                type: "box", layout: "horizontal", contents: [
                  { type: "text", text: "หมดอายุ", color: "#aaaaaa", size: "md", flex: 2 },
                  { type: "text", text: dep.expiry_date || '-', weight: "bold", size: "lg", color: daysLeft <= 7 ? "#ef4444" : "#111111", flex: 4 }
                ]
              },
              {
                type: "box", layout: "horizontal", contents: [
                  { type: "text", text: "เหลือ", color: "#aaaaaa", size: "md", flex: 2 },
                  { type: "text", text: `${daysLeft} วัน`, weight: "bold", size: "xl", color: daysLeft <= 3 ? "#ef4444" : "#f59e0b", flex: 4 }
                ]
              }
            ]
          },
          footer: {
            type: "box", layout: "vertical", backgroundColor: "#FEF3C7", paddingAll: "16px",
            contents: [{ type: "text", text: "⚠️ กรุณามาเบิกก่อนวันหมดอายุ", size: "sm", color: "#92400E", weight: "bold", align: "center" }]
          }
        };

        if (dep.image_key) {
          flexPayload.hero = {
            type: "image",
            url: `${url.origin}/api/image/${dep.image_key}`,
            size: "full",
            aspectRatio: "1:1",
            aspectMode: "cover"
          };
        }

        const flexMessage = {
          type: "flex",
          altText: `${urgencyText} เหล้าของคุณใกล้หมดอายุ อีก ${daysLeft} วัน`,
          contents: flexPayload
        };

        const pushRes = await fetch("https://api.line.me/v2/bot/message/push", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${env.LINE_OA_TOKEN}`
          },
          body: JSON.stringify({
            to: dep.owner_uid,
            messages: [flexMessage]
          })
        });

        if (!pushRes.ok) {
          const errText = await pushRes.text();
          return new Response(JSON.stringify({ success: false, error: "LINE API Error: " + errText }), { headers: cors });
        }

        return new Response(JSON.stringify({ success: true, daysLeft }), { headers: cors });
      }

      // บรอดแคสต์ของรางวัล (Promote Reward)
      if (path === "/api/promote-reward" && request.method === "POST") {
        const { reward_id, audience } = await request.json();
        const reward = await env.DB.prepare("SELECT * FROM rewards_inventory WHERE id = ?").bind(reward_id).first();
        if (!reward) return new Response(JSON.stringify({ success: false, error: "Not found" }), { headers: cors });

        if (!env.LINE_OA_TOKEN) {
          return new Response(JSON.stringify({ success: false, error: "ยังไม่ได้ตั้งค่า LINE_OA_TOKEN ในระบบ" }), { headers: cors });
        }

        let users;
        if (audience === 'eligible') {
          // คนที่มีแต้มถึง (points >= reward.points)
          users = await env.DB.prepare("SELECT uid FROM user_profiles WHERE uid IS NOT NULL AND uid != '' AND points >= ?").bind(reward.points).all();
        } else {
          // ทุกคนที่มี uid ผูกไว้
          users = await env.DB.prepare("SELECT uid FROM user_profiles WHERE uid IS NOT NULL AND uid != ''").all();
        }

        if (!users.results || users.results.length === 0) {
          return new Response(JSON.stringify({ success: false, error: "ไม่มีลูกค้าในระบบที่ตรงตามเงื่อนไข" }), { headers: cors });
        }

        const uids = users.results.map(u => u.uid);

        const liffUrl = `https://liff.line.me/2009020696-z6Zlyc90`;
        const flexPayload = {
          type: "bubble", size: "mega",
          header: {
            type: "box", layout: "vertical", backgroundColor: "#D97706", paddingAll: "20px",
            contents: [{ type: "text", text: "🎁 Siri Clubhouse แจกรางวัล!", color: "#FFFFFF", weight: "bold", size: "md", align: "center" }]
          },
          body: {
            type: "box", layout: "vertical", spacing: "md",
            contents: [
              { type: "text", text: reward.name, weight: "bold", size: "xl", align: "center", wrap: true },
              {
                type: "box", layout: "horizontal", margin: "md", contents: [
                  { type: "text", text: "ใช้แต้มแลกเพียง", color: "#AAAAAA", size: "sm", flex: 3 },
                  { type: "text", text: `${reward.points} แต้ม`, weight: "bold", size: "md", color: "#D97706", flex: 4 }
                ]
              }
            ]
          },
          footer: {
            type: "box", layout: "vertical", backgroundColor: "#FFFBEB", paddingAll: "16px",
            contents: [
              {
                type: "button",
                style: "primary",
                color: "#D97706",
                action: {
                  type: "uri",
                  label: "กดดูรางวัลอื่นๆ",
                  uri: liffUrl
                }
              }
            ]
          }
        };

        if (reward.image_key) {
          flexPayload.hero = {
            type: "image",
            url: `${url.origin}/api/image/${reward.image_key}`,
            size: "full",
            aspectRatio: "1:1",
            aspectMode: "cover",
            action: {
              type: "uri",
              uri: liffUrl
            }
          };
        }

        const flexMessage = {
          type: "flex",
          altText: `Siri Clubhouse แจกของรางวัล: ${reward.name} ใช้เพียง ${reward.points} แต้ม`,
          contents: flexPayload
        };

        // LINE Multicast API รองรับส่งพร้อมกันสูงสุด 500 uid ต่อ 1 request
        let successCount = 0;
        const chunkSize = 500;
        let lastError = null;

        for (let i = 0; i < uids.length; i += chunkSize) {
          const chunk = uids.slice(i, i + chunkSize);
          const pushRes = await fetch("https://api.line.me/v2/bot/message/multicast", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${env.LINE_OA_TOKEN}`
            },
            body: JSON.stringify({
              to: chunk,
              messages: [flexMessage]
            })
          });
          if (pushRes.ok) {
            successCount += chunk.length;
          } else {
            lastError = await pushRes.text();
          }
        }

        if (successCount === 0 && lastError) {
          return new Response(JSON.stringify({ success: false, error: "LINE API Error: " + lastError }), { headers: cors });
        }

        return new Response(JSON.stringify({ success: true, targetCount: uids.length, successCount }), { headers: cors });
      }


      // ดึงรายการ stock ทั้งหมด (สำหรับ staff logs)
      if (path === "/api/all-deposits") {
        const res = await env.DB.prepare(
          "SELECT d.*, u.name as customer_name FROM deposits d LEFT JOIN user_profiles u ON d.owner_uid = u.uid WHERE d.status = 'active' ORDER BY d.expiry_date ASC"
        ).all();
        const results = res.results.map(r => ({
          ...r,
          image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : null
        }));
        return new Response(JSON.stringify(results), { headers: cors });
      }

      // 7. Support endpoints
      if (path === "/api/staff-search") {
        const query = url.searchParams.get('phone') || url.searchParams.get('code');

        let user = null;
        let deposits = [];

        // Normalize query (strip non-digits for phone search)
        const cleanQuery = query ? query.replace(/\D/g, '') : null;

        // Check if query is 5-digit code or phone
        if (cleanQuery && /^\d{5}$/.test(cleanQuery) && query.length === 5) {
          const res = await env.DB.prepare(`
            SELECT d.*, u.name as customer_name 
            FROM deposits d 
            LEFT JOIN user_profiles u ON d.owner_uid = u.uid 
            WHERE d.deposit_code = ? AND d.status != 'withdrawn' 
            ORDER BY d.created_at DESC
          `).bind(cleanQuery).all();
          deposits = res.results.map(r => ({
            ...r,
            image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : null
          }));
        } else {
          // Normal phone search
          user = await env.DB.prepare("SELECT * FROM user_profiles WHERE phone = ?").bind(cleanQuery).first();

          const res = await env.DB.prepare(`
            SELECT d.*, u.name as customer_name 
            FROM deposits d 
            LEFT JOIN user_profiles u ON d.owner_uid = u.uid
            WHERE (d.owner_phone = ? OR (d.owner_uid = ? AND d.owner_uid IS NOT NULL)) 
            AND d.status != 'withdrawn' 
            ORDER BY d.created_at DESC
          `).bind(cleanQuery, user ? user.uid : null).all();

          deposits = res.results.map(r => ({
            ...r,
            image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : null
          }));
        }
        let coupons = [];
        let usedCoupons = [];
        if (user) {
          const cRes = await env.DB.prepare("SELECT * FROM user_coupons WHERE owner_uid = ? AND status = 'unused' ORDER BY created_at DESC").bind(user.uid).all();
          coupons = cRes.results.map(c => ({
            ...c,
            image_url: c.reward_image_key ? `${url.origin}/api/image/${c.reward_image_key}` : null
          }));

          const cuRes = await env.DB.prepare("SELECT * FROM user_coupons WHERE owner_uid = ? AND status = 'used' ORDER BY used_at DESC").bind(user.uid).all();
          usedCoupons = cuRes.results.map(c => ({
            ...c,
            image_url: c.reward_image_key ? `${url.origin}/api/image/${c.reward_image_key}` : null
          }));
        }
        return new Response(JSON.stringify({ user, deposits, coupons: user ? coupons : [], usedCoupons: user ? usedCoupons : [] }), { headers: cors });
      }

      // เพิ่มแต้มให้ลูกค้า (manual)
      if (path === "/api/add-points" && request.method === "POST") {
        const { phone, points, staff_uid, reason } = await request.json();
        if (!phone || !points) return new Response(JSON.stringify({ success: false, error: "Missing data" }), { headers: cors });
        const user = await env.DB.prepare("SELECT uid FROM user_profiles WHERE phone = ?").bind(phone).first();
        if (!user) return new Response(JSON.stringify({ success: false, error: "ไม่พบลูกค้าในระบบ" }), { headers: cors });
        await env.DB.prepare("UPDATE user_profiles SET points = points + ? WHERE phone = ?").bind(points, phone).run();
        await env.DB.prepare("INSERT INTO point_logs (phone, amount, action, staff_uid) VALUES (?, ?, ?, ?)")
          .bind(phone, points, reason || 'manual_add', staff_uid).run();
        const updated = await env.DB.prepare("SELECT points FROM user_profiles WHERE phone = ?").bind(phone).first();
        return new Response(JSON.stringify({ success: true, newTotal: updated.points }), { headers: cors });
      }

      if (path === "/api/staff-withdraw" && request.method === "POST") {
        const { deposit_id, staff_uid } = await request.json();

        // ลบรูปออกจาก R2 Bucket เพื่อประหยัดพื้นที่
        const dep = await env.DB.prepare("SELECT image_key FROM deposits WHERE id = ?").bind(deposit_id).first();
        if (dep && dep.image_key) {
          await env.BUCKET.delete(dep.image_key);
        }

        await env.DB.prepare("UPDATE deposits SET status = 'withdrawn', withdrawn_at = CURRENT_TIMESTAMP, withdrawn_by = ? WHERE id = ?")
          .bind(staff_uid, deposit_id).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/verify-manager" && request.method === "POST") {
        const { pin } = await request.json();
        // Securely check PIN on server side
        if (pin === "7777") {
          return new Response(JSON.stringify({ success: true }), { headers: cors });
        }
        return new Response(JSON.stringify({ success: false, error: "รหัสไม่ถูกต้อง" }), { headers: cors });
      }

      if (path.startsWith("/api/image/")) {
        const key = path.split('/').pop();
        const obj = await env.BUCKET.get(key);
        if (!obj) return new Response("Not Found", { status: 404 });
        return new Response(obj.body, { headers: { "Content-Type": "image/jpeg", ...cors } });
      }

    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: cors });
    }
  },

  // ========== Cron Trigger (รายวัน 09:00 UTC+7) ==========
  async scheduled(event, env, ctx) {
    ctx.waitUntil(notifyExpiringDeposits(env));
  }
};

// ฟังก์ชันแจ้งเตือนเหล้าใกล้หมดอายุ
async function notifyExpiringDeposits(env) {
  const today = new Date().toISOString().split('T')[0];
  const notifyDays = [14, 7, 3, 1];
  let totalSent = 0;

  for (const days of notifyDays) {
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + days);
    const targetStr = targetDate.toISOString().split('T')[0];

    const res = await env.DB.prepare(
      "SELECT d.*, u.name as customer_name FROM deposits d LEFT JOIN user_profiles u ON d.owner_uid = u.uid WHERE d.expiry_date = ? AND d.status = 'active'"
    ).bind(targetStr).all();

    for (const dep of res.results) {
      if (env.LINE_TOKEN) {
        const urgency = days === 1 ? '🚨 วันนี้วันสุดท้าย!' : days <= 3 ? '⚠️ ใกล้หมดอายุมาก!' : '📢 แจ้งเตือนล่วงหน้า';
        const msg = `\n${urgency}\nเหล้าชื่อ: ${dep.item_name}\nเจ้าของ: ${dep.customer_name || dep.owner_phone}\nหมดอายุ: ${dep.expiry_date} (อีก ${days} วัน)\nปริมาณคงเหลือ: ${dep.amount}%\n\n📞 กรุณาติดต่อลูกค้าหรือมาเบิกก่อนหมดอายุ`;
        await sendLineNotify(env.LINE_TOKEN, msg);
        totalSent++;
      }
    }
  }

  return { success: true, sent: totalSent, date: today };
}
