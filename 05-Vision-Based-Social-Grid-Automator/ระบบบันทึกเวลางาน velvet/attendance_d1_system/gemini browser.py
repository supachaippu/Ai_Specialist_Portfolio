import streamlit as st
import os
import json
import subprocess
import sys

# --- CONFIG MANAGEMENT ---
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generator_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- WORKER CONTENT (Server Side) ---
WORKER_CONTENT = """export default {
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
};"""

SCHEMA_CONTENT = """CREATE TABLE IF NOT EXISTS employees (
    uid TEXT PRIMARY KEY,
    nickname TEXT NOT NULL,
    thai_name TEXT,
    role TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_key TEXT,
    is_suspicious INTEGER DEFAULT 0,
    check_note TEXT,
    FOREIGN KEY(uid) REFERENCES employees(uid)
);"""

# --- HTML TEMPLATE (FIXED: LOGIN HANG + VISUAL DEBUGGER + GPS OCR) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{SHOP_NAME_TH}} Check-in</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Sarabun:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script charset="utf-8" src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <style>
        :root { --primary: #06C755; --bg: #0f172a; --card: #ffffff; --text: #1e293b; }
        body { font-family: 'Outfit', 'Sarabun', sans-serif; background: radial-gradient(circle at top left, #063c1a, #0f172a); margin: 0; padding: 15px; color: var(--text); display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 420px; animation: fadeIn 0.5s ease-out; padding-bottom: 50px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { color: #fff; font-size: 1.5rem; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .line-badge { background: #06C755; color: white; padding: 2px 10px; border-radius: 50px; font-size: 0.6rem; font-weight: 800; display: inline-block; margin-top: 5px; }
        
        .app-card { background: var(--card); border-radius: 24px; padding: 20px; box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5); text-align: center; }
        
        .user-profile { display: flex; flex-direction: column; align-items: center; margin-bottom: 15px; background: #f8fafc; padding: 10px; border-radius: 18px; border: 1px solid #e2e8f0; }
        .profile-img { width: 50px; height: 50px; border-radius: 50%; border: 3px solid var(--primary); margin-bottom: 5px; background: #eee; object-fit: cover; }
        
        .upload-box { border: 2px dashed #cbd5e1; border-radius: 18px; height: 160px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f1f5f9; margin-bottom: 15px; cursor: pointer; position: relative; overflow: hidden; transition: 0.2s; }
        .upload-box:active { transform: scale(0.98); background: #e2e8f0; }
        
        .info-box { background: #1e293b; color: #fff; padding: 15px; border-radius: 18px; margin-bottom: 15px; display: none; text-align: center; }
        
        .btn { border: none; padding: 12px; border-radius: 14px; width: 100%; font-size: 1rem; font-weight: 800; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:disabled { background: #94a3b8; opacity: 0.7; cursor: not-allowed; }
        .btn-secondary { background: #f1f5f9; color: #64748b; margin-top: 8px; font-size: 0.8rem; }

        .loader-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; color: white; }
        .spinner { border: 4px solid rgba(255,255,255,0.1); border-top: 4px solid var(--primary); border-radius: 50%; width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin-bottom: 15px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Debug Console (Visible on screen) */
        #debugConsole { position: fixed; bottom: 0; left: 0; width: 100%; height: 80px; background: rgba(0,0,0,0.85); color: #00ff00; font-family: monospace; font-size: 10px; overflow-y: auto; padding: 10px; box-sizing: border-box; z-index: 10000; border-top: 1px solid #333; display: none; }

        /* Tabs */
        .tab-btn-group { display: flex; gap: 8px; margin-bottom: 15px; background: rgba(255,255,255,0.1); padding: 4px; border-radius: 12px; }
        .tab-btn { flex: 1; padding: 8px; border-radius: 8px; border: none; background: transparent; color: #fff; font-weight: 600; cursor: pointer; font-size: 0.9rem; }
        .tab-btn.active { background: #fff; color: var(--bg); }

        #historyArea { display: none; }
        .log-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 10px; }
        .log-table th { text-align: left; padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0; }
        .log-table td { padding: 8px; border-bottom: 1px solid #f1f5f9; }
    </style>
</head>
<body>
    <div id="loadingOverlay" class="loader-overlay">
        <div class="spinner"></div>
        <div id="loadingText" style="text-align:center; margin-bottom:20px;">กำลังเชื่อมต่อ...</div>
        
        <button id="bypassBtn" onclick="activateManualMode()" style="display:none; background:transparent; border:1px solid #fff; color:#fff; padding:8px 16px; border-radius:50px; font-size:0.8rem; cursor:pointer;">
            ⚠️ รอนานเกินไป? กดตรงนี้เพื่อเข้าใช้งาน
        </button>
    </div>

    <div id="debugConsole"></div>

    <div class="container">
        <div class="header"><h1>{{SHOP_NAME_TH}}</h1><div class="line-badge">STAFF CHECKIN V2.1</div></div>
        
        <div class="tab-btn-group">
            <button id="tabIn" class="tab-btn active" onclick="switchTab('in')">ลงเวลา</button>
            <button id="tabHist" class="tab-btn" onclick="switchTab('hist')">ประวัติ</button>
        </div>

        <div class="app-card">
            <div id="mainApp">
                <div class="user-profile">
                    <img id="lineImg" class="profile-img" src="">
                    <div id="lineName" style="font-weight:700; font-size:1rem; color:#1e293b;">...</div>
                    <div id="d1Nick" style="font-size:0.8rem; color:var(--primary); font-weight:800; margin-top:2px;">(กำลังโหลด)</div>
                    <button onclick="openMultiSelect()" style="background:none; border:none; color:#64748b; font-size:0.75rem; cursor:pointer; margin-top:5px; text-decoration:underline;">
                       <i class="fa-solid fa-user-plus"></i> เพิ่มเพื่อนลงเวลาด้วย (<span id="selectedCount">1</span>)
                    </button>
                </div>
                
                <div id="attendanceArea" style="opacity:0.5; pointer-events:none; transition:0.3s;">
                    <input type="file" id="fileInput" hidden accept="image/*">
                    <div class="upload-box" onclick="document.getElementById('fileInput').click()">
                        <div id="placeholder" style="text-align:center;">
                            <i class="fa-solid fa-camera" style="font-size:1.8rem; color:#94a3b8; margin-bottom:8px;"></i>
                            <p style="font-size:0.8rem; color:#64748b; margin:0;">ถ่ายรูปจาก<br><b>Timestamp Camera</b></p>
                        </div>
                        <img id="previewImg" style="width:100%; height:100%; object-fit:cover; display:none;">
                    </div>

                    <div id="infoBox" class="info-box">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                            <div style="border-right:1px solid rgba(255,255,255,0.2);">
                                <span style="font-size:0.6rem; opacity:0.7;">DATE</span>
                                <span id="detectedDate" style="display:block; font-size:1rem; font-weight:800; color:#4ade80;">--</span>
                            </div>
                            <div>
                                <span style="font-size:0.6rem; opacity:0.7;">TIME</span>
                                <span id="detectedTime" style="display:block; font-size:1rem; font-weight:800; color:#4ade80;">--</span>
                            </div>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary" id="submitBtn" disabled onclick="saveLog()">
                        บันทึกเวลาเข้างาน
                    </button>
                </div>
            </div>

            <div id="historyArea">
                <div style="display:flex; gap:10px; margin-bottom:10px;">
                    <button class="btn btn-secondary" onclick="fetchLogs()" style="margin:0;"><i class="fa-solid fa-rotate"></i></button>
                    <button class="btn btn-secondary" onclick="downloadExcel()" style="margin:0; flex:1;">โหลด Excel</button>
                </div>
                <div style="max-height:350px; overflow-y:auto;">
                    <table class="log-table">
                        <tbody id="logTableBody"><tr><td style="text-align:center;">แตะรีเฟรชเพื่อดูข้อมูล</td></tr></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <div id="regModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:2000; align-items:center; justify-content:center; padding:20px;">
        <div style="background:#fff; border-radius:24px; padding:30px; width:100%; max-width:320px; text-align:center;">
            <h3 style="margin:0 0 15px 0; color:var(--text);">👋 พนักงานใหม่?</h3>
            <p style="font-size:0.9rem; color:#64748b; margin-bottom:15px;">กรุณาใส่ชื่อเล่น (ภาษาอังกฤษ)</p>
            <input type="text" id="regNick" placeholder="Ex. Somchai" style="width:100%; padding:12px; border:2px solid #e2e8f0; border-radius:12px; font-size:1.1rem; text-align:center; box-sizing:border-box; margin-bottom:15px;">
            <button class="btn btn-primary" onclick="doRegister()">ลงทะเบียนเริ่มใช้งาน</button>
        </div>
    </div>

    <div id="multiModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:2000; align-items:center; justify-content:center; padding:20px;">
        <div style="background:#fff; border-radius:24px; padding:20px; width:100%; max-width:350px; height:80vh; display:flex; flex-direction:column;">
            <h3 style="margin:0 0 10px 0; text-align:center;">เลือกเพื่อนร่วมงาน</h3>
            <input type="text" id="empSearch" placeholder="🔍 ค้นหา..." oninput="renderEmployeeList(this.value)" style="padding:10px; border:1px solid #ccc; border-radius:8px; width:100%; box-sizing:border-box; margin-bottom:10px;">
            <div id="employeeChecklist" style="flex:1; overflow-y:auto; border:1px solid #f1f5f9; margin-bottom:10px;"></div>
            <div style="display:flex; gap:10px;">
                <button class="btn btn-secondary" onclick="document.getElementById('multiModal').style.display='none'">ปิด</button>
                <button class="btn btn-primary" onclick="confirmSelection()">ยืนยัน</button>
            </div>
        </div>
    </div>

    <script>
        // --- CORE UTILS: PREVENT HANGING ---
        // 1. Visible Logger
        function log(msg) {
            console.log(msg);
            const c = document.getElementById('debugConsole');
            const t = document.getElementById('loadingText');
            if(c) { c.style.display = 'block'; c.innerHTML += `> ${msg}<br>`; c.scrollTop = c.scrollHeight; }
            if(t) t.innerText = msg;
        }

        // 2. Fetch with Timeout (The Anti-Freeze)
        async function fetchWithTimeout(resource, options = {}) {
            const { timeout = 8000 } = options;
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeout);
            try {
                const response = await fetch(resource, { ...options, signal: controller.signal });
                clearTimeout(id);
                return response;
            } catch (error) {
                clearTimeout(id);
                throw error;
            }
        }

        // --- CONFIG & STATE ---
        const LIFF_ID = "{{LIFF_ID}}";
        const API_BASE = "{{WORKER_URL}}"; 
        let USER_ID = null;
        let MY_NICKNAME = "Guest";
        let SELECTED_ITEMS = [];
        let DETECTED_ISO = null;
        let ALL_EMPLOYEES = [];

        // --- MAIN ENTRY POINT ---
        window.onload = async () => {
            log("System Start...");
            
            // Safety: Show bypass button after 3 seconds if nothing happens
            setTimeout(() => {
                const btn = document.getElementById('bypassBtn');
                if(btn && document.getElementById('loadingOverlay').style.display !== 'none') {
                    btn.style.display = 'block';
                    log("⚠️ Taking too long? Try Manual Mode.");
                }
            }, 3000);

            if (!LIFF_ID || LIFF_ID.length < 5) {
                alert("❌ ยังไม่ได้ตั้งค่า LIFF ID");
                showLoad(false); return;
            }

            try {
                log("1/4 Init LIFF...");
                // Race LIFF init against a 5s timeout
                await Promise.race([
                    liff.init({ liffId: LIFF_ID }),
                    new Promise((_, reject) => setTimeout(() => reject(new Error("LIFF Init Timeout")), 5000))
                ]);

                if (!liff.isLoggedIn()) {
                    log("Redirecting to Login...");
                    liff.login();
                    return;
                }

                log("2/4 Get Profile...");
                const profile = await liff.getProfile().catch(e => {
                    log("⚠️ Profile failed: " + e.message);
                    return { userId: "UNKNOWN_" + Date.now(), displayName: "Unknown", pictureUrl: "" };
                });

                USER_ID = profile.userId;
                document.getElementById('lineImg').src = profile.pictureUrl || "https://cdn-icons-png.flaticon.com/512/1077/1077114.png";
                document.getElementById('lineName').innerText = profile.displayName;

                await checkUserInDB();

            } catch (err) {
                log("❌ FATAL: " + err.message);
                // Don't leave user stuck. Allow manual mode.
                document.getElementById('bypassBtn').style.display = 'block';
                alert("เกิดข้อผิดพลาดในการเชื่อมต่อ: " + err.message + "\nกดปุ่ม 'เข้าใช้งาน' ด้านล่างได้เลยครับ");
            }
        };

        // --- MANUAL BYPASS MODE ---
        function activateManualMode() {
            const manualNick = prompt("ระบบเชื่อมต่ออัตโนมัติมีปัญหา\nกรุณาใส่ชื่อเล่นภาษาอังกฤษเพื่อเข้าใช้งาน:");
            if(manualNick) {
                USER_ID = "MANUAL_" + manualNick.replace(/\s/g, '');
                MY_NICKNAME = manualNick;
                onLoginSuccess(manualNick);
            }
        }

        // --- DB CHECK ---
        async function checkUserInDB() {
            log("3/4 Checking DB...");
            try {
                // Ensure API_BASE is valid
                let targetUrl = API_BASE.startsWith('http') ? API_BASE : `https://${API_BASE}`;
                
                const r = await fetchWithTimeout(`${targetUrl}/api/check_uid?uid=${USER_ID}`, { timeout: 6000 });
                if(!r.ok) throw new Error(`Server Error ${r.status}`);
                
                const data = await r.json();
                if (data.success) {
                    onLoginSuccess(data.nickname);
                } else {
                    log("New User. Registering...");
                    document.getElementById('loadingOverlay').style.display = 'none';
                    document.getElementById('regModal').style.display = 'flex';
                }
            } catch (e) {
                log("⚠️ DB Check Failed: " + e.message);
                // If DB check fails, assume manual registration needed or network down
                // Instead of hanging, ask for manual input
                activateManualMode();
            }
        }

        function onLoginSuccess(nickname) {
            MY_NICKNAME = nickname;
            SELECTED_ITEMS = [{uid: USER_ID, nickname: MY_NICKNAME}];
            document.getElementById('d1Nick').innerText = nickname;
            document.getElementById('selectedCount').innerText = "1";
            
            // Unlock UI
            const area = document.getElementById('attendanceArea');
            area.style.opacity = "1";
            area.style.pointerEvents = "auto";
            showLoad(false);
            log("✅ Ready!");
            
            // Hide debug console after 2s if successful
            setTimeout(() => { document.getElementById('debugConsole').style.display = 'none'; }, 2000);
        }

        async function doRegister() {
            const nick = document.getElementById('regNick').value.trim();
            if(!nick) return alert("Please enter nickname");
            
            showLoad("Registering...");
            try {
                let targetUrl = API_BASE.startsWith('http') ? API_BASE : `https://${API_BASE}`;
                await fetchWithTimeout(`${targetUrl}/api/register`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ uid: USER_ID, nickname: nick })
                });
                document.getElementById('regModal').style.display = 'none';
                onLoginSuccess(nick);
            } catch(e) {
                alert("Register Failed: " + e.message);
                showLoad(false);
            }
        }

        // --- MULTI SELECT ---
        async function openMultiSelect() {
            showLoad("Loading Staff...");
            try {
                let targetUrl = API_BASE.startsWith('http') ? API_BASE : `https://${API_BASE}`;
                const r = await fetchWithTimeout(`${targetUrl}/api/get_employees`);
                if(r.ok) {
                    ALL_EMPLOYEES = await r.json();
                    renderEmployeeList();
                    document.getElementById('multiModal').style.display = 'flex';
                }
            } catch(e) { alert("Load Failed"); } 
            finally { showLoad(false); }
        }

        function renderEmployeeList(q = '') {
            const div = document.getElementById('employeeChecklist');
            div.innerHTML = '';
            const filter = ALL_EMPLOYEES.filter(e => e.nickname.toLowerCase().includes(q.toLowerCase()));
            filter.forEach(e => {
                const checked = SELECTED_ITEMS.find(i => i.uid === e.uid) ? 'checked' : '';
                div.innerHTML += `<label style="display:flex; align-items:center; padding:10px; border-bottom:1px solid #eee;">
                    <input type="checkbox" ${checked} onchange="toggleSel('${e.uid}', '${e.nickname}', this.checked)" style="width:20px; height:20px; margin-right:10px;">
                    ${e.nickname}
                </label>`;
            });
        }

        window.toggleSel = (uid, nick, checked) => {
            if(checked) { if(!SELECTED_ITEMS.find(i=>i.uid===uid)) SELECTED_ITEMS.push({uid, nickname:nick}); }
            else SELECTED_ITEMS = SELECTED_ITEMS.filter(i=>i.uid!==uid);
        };

        window.confirmSelection = () => {
            if(SELECTED_ITEMS.length === 0) SELECTED_ITEMS = [{uid:USER_ID, nickname:MY_NICKNAME}];
            document.getElementById('d1Nick').innerText = SELECTED_ITEMS.map(i=>i.nickname).join(", ");
            document.getElementById('selectedCount').innerText = SELECTED_ITEMS.length;
            document.getElementById('multiModal').style.display = 'none';
        };

        // --- OCR & SAVE (GPS CAMERA OPTIMIZED) ---
        document.getElementById('fileInput').onchange = async (e) => {
            const f = e.target.files[0]; if(!f) return;
            const url = URL.createObjectURL(f);
            document.getElementById('previewImg').src = url;
            document.getElementById('previewImg').style.display = 'block';
            document.getElementById('placeholder').style.display = 'none';

            showLoad("AI Analyzing...");
            try {
                // Dynamic Load
                if(typeof Tesseract === 'undefined') await loadScript('https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js');
                
                const img = new Image(); img.src = url; await new Promise(r=>img.onload=r);
                const worker = await Tesseract.createWorker('eng');
                await worker.setParameters({ tessedit_char_whitelist: '0123456789/:., ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' });
                
                // Canvas Prep (Bottom 30% + Invert Color)
                const cvs = document.createElement('canvas'); const ctx = cvs.getContext('2d');
                const w = img.width; const h = img.height;
                cvs.width = w; cvs.height = h * 0.35; // Take bottom 35%
                ctx.filter = 'invert(1) grayscale(1) contrast(2.0)'; // FIX FOR GPS CAMERA WHITE TEXT
                ctx.drawImage(img, 0, h * 0.65, w, h * 0.35, 0, 0, w, h * 0.35);

                const ret = await worker.recognize(cvs.toDataURL());
                const text = ret.data.text;
                log("OCR: " + text.replace(/\n/g, ' '));
                
                // Parse Date/Time (GPS Camera: MM/DD/YYYY)
                const dateMatch = text.match(/(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{4})/);
                const timeMatch = text.match(/(\d{1,2})[:\.](\d{1,2})[:\.](\d{1,2})/);

                if(dateMatch && timeMatch) {
                    let m = parseInt(dateMatch[1]); 
                    let d = parseInt(dateMatch[2]);
                    const y = parseInt(dateMatch[3]);
                    
                    // Swap if day > 12 (DD/MM case)
                    if(m > 12) { const tmp = m; m = d; d = tmp; }

                    let H = parseInt(timeMatch[1]);
                    const M = parseInt(timeMatch[2]);
                    const S = parseInt(timeMatch[3]);
                    
                    // PM adjustment if text contains PM
                    if(text.match(/PM/i) && H < 12) H += 12;
                    if(text.match(/AM/i) && H === 12) H = 0;

                    const finalY = y > 2400 ? y - 543 : y;
                    const dateObj = new Date(finalY, m-1, d, H, M, S);
                    
                    if(!isNaN(dateObj)) {
                        DETECTED_ISO = dateObj.toISOString();
                        document.getElementById('detectedDate').innerText = `${d}/${m}/${finalY}`;
                        document.getElementById('detectedTime').innerText = `${H}:${M}:${S}`;
                        document.getElementById('infoBox').style.display = 'block';
                        document.getElementById('submitBtn').disabled = false;
                        document.getElementById('submitBtn').innerText = "✅ ยืนยันบันทึกเวลา";
                        document.getElementById('submitBtn').style.background = "#06C755";
                    }
                } else {
                    alert("⚠️ อ่านเวลาไม่ชัด กรุณาถ่ายใหม่ให้เห็นแถบล่างชัดๆ");
                }
                await worker.terminate();
            } catch(e) { alert("OCR Fail: " + e.message); }
            finally { showLoad(false); }
        };

        window.saveLog = async () => {
            showLoad("Saving...");
            try {
                // Compress
                const img = document.getElementById('previewImg');
                const cvs = document.createElement('canvas');
                const ctx = cvs.getContext('2d');
                const scale = 1200 / img.naturalWidth;
                cvs.width = 1200; cvs.height = img.naturalHeight * scale;
                ctx.drawImage(img, 0, 0, cvs.width, cvs.height);
                const b64 = cvs.toDataURL('image/jpeg', 0.7);

                const uids = SELECTED_ITEMS.map(i => i.uid);
                let targetUrl = API_BASE.startsWith('http') ? API_BASE : `https://${API_BASE}`;
                
                await fetchWithTimeout(`${targetUrl}/api/log`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        uid: USER_ID,
                        uids: uids,
                        timestamp: DETECTED_ISO,
                        image: b64
                    })
                });
                alert("✅ บันทึกสำเร็จ!");
                switchTab('hist');
            } catch(e) { alert("Save Failed: " + e.message); }
            finally { showLoad(false); }
        };

        // --- HISTORY ---
        window.switchTab = (t) => {
            document.getElementById('mainApp').style.display = t==='in'?'block':'none';
            document.getElementById('historyArea').style.display = t==='hist'?'block':'none';
            document.getElementById('tabIn').className = t==='in'?'tab-btn active':'tab-btn';
            document.getElementById('tabHist').className = t==='hist'?'tab-btn active':'tab-btn';
            if(t==='hist') fetchLogs();
        };

        window.fetchLogs = async () => {
            const tbody = document.getElementById('logTableBody');
            tbody.innerHTML = '<tr><td style="text-align:center;">Loading...</td></tr>';
            try {
                let targetUrl = API_BASE.startsWith('http') ? API_BASE : `https://${API_BASE}`;
                const r = await fetchWithTimeout(`${targetUrl}/api/get_logs`);
                const d = await r.json();
                tbody.innerHTML = '';
                d.forEach(l => {
                    tbody.innerHTML += `<tr>
                        <td><b>${l.nickname}</b><br><span style="color:#64748b;font-size:0.7rem;">${new Date(l.timestamp).toLocaleString()}</span></td>
                    </tr>`;
                });
            } catch(e) { tbody.innerHTML = `<tr><td style="color:red;text-align:center;">โหลดไม่ได้ (${e.message})</td></tr>`; }
        };

        // --- UTILS ---
        function showLoad(msg) {
            const o = document.getElementById('loadingOverlay');
            if(msg === false) o.style.display = 'none';
            else { 
                o.style.display = 'flex'; 
                document.getElementById('loadingText').innerText = msg;
                // Reset bypass button timer
                document.getElementById('bypassBtn').style.display = 'none';
                setTimeout(() => {
                    if(o.style.display === 'flex') document.getElementById('bypassBtn').style.display = 'block';
                }, 3000);
            }
        }
        function loadScript(src) { return new Promise((r,j)=>{const s=document.createElement('script');s.src=src;s.onload=r;s.onerror=j;document.head.appendChild(s);}); }
    </script>
</body>
</html>
"""

def main():
    st.set_page_config(page_title="Velvet System V2.1", page_icon="🛡️")
    st.title("🛡️ Velvet Attendance V2.1 (Anti-Freeze)")
    st.markdown("### ระบบเวอร์ชันแก้ปัญหาค้าง + Debugger + ปุ่ม Bypass")
    
    config = load_config()
    
    with st.expander("⚙️ ตั้งค่า (Config)", expanded=True):
        shop_name = st.text_input("ชื่อร้าน", value=config.get("shop_name", "Velvet Shop"))
        liff_id = st.text_input("LIFF ID", value=config.get("liff_id", ""))
        worker_url = st.text_input("Worker URL", value=config.get("worker_url", ""))
        folder_name = st.text_input("Folder Name", value="velvet_v2_fixed")

    if st.button("🚀 สร้างไฟล์ใหม่ (Build)", type="primary"):
        if not worker_url or not liff_id:
            st.error("กรุณากรอกข้อมูลให้ครบ")
            return

        # Auto-Fix URL
        final_url = worker_url.strip().strip("/")
        if not final_url.startswith("http"): final_url = "https://" + final_url

        save_config({"shop_name": shop_name, "liff_id": liff_id, "worker_url": final_url})
        
        # Prepare HTML
        html_out = HTML_TEMPLATE.replace("{{SHOP_NAME_TH}}", shop_name)\
                                .replace("{{LIFF_ID}}", liff_id)\
                                .replace("{{WORKER_URL}}", final_url)
        
        # Write Files
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_name)
        os.makedirs(out_dir, exist_ok=True)
        
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f: f.write(html_out)
        with open(os.path.join(out_dir, "worker.js"), "w", encoding="utf-8") as f: f.write(WORKER_CONTENT)
        with open(os.path.join(out_dir, "schema.sql"), "w", encoding="utf-8") as f: f.write(SCHEMA_CONTENT)
        
        st.success(f"✅ เรียบร้อย! ไฟล์อยู่ที่โฟลเดอร์ `{folder_name}`")
        st.warning("⚠️ อย่าลืม Copy โค้ดใน worker.js ไปอัปเดตใน Cloudflare Worker ด้วยนะครับ (สำคัญมาก)")

if __name__ == "__main__":
    try:
        from streamlit.runtime import exists as st_exists
        if st_exists(): main()
        else: subprocess.Popen([sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)])
    except: pass