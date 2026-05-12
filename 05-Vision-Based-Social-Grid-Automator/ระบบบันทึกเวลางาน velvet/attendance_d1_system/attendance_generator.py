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

# --- WORKER & SCHEMA TEMPLATES ---
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
                return new Response("✨ Velvet Attendance + R2 System Active ✅", { 
                    headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders } 
                });
            }

            if (url.pathname === "/api/check_uid" && request.method === "GET") {
                const uid = url.searchParams.get("uid");
                if (!uid || uid === "null" || uid === "undefined") {
                    return new Response(JSON.stringify({ success: false, error: "Invalid UID" }), { headers: corsHeaders });
                }
                const user = await env.DB.prepare("SELECT nickname FROM employees WHERE uid = ?").bind(uid).first();
                return new Response(JSON.stringify({ success: !!user, nickname: user?.nickname || "" }), { headers: corsHeaders });
            }

            if (url.pathname === "/api/get_employees" && request.method === "GET") {
                const employees = await env.DB.prepare("SELECT uid, nickname FROM employees ORDER BY nickname ASC").all();
                return new Response(JSON.stringify(employees.results), { headers: corsHeaders });
            }

            if (url.pathname === "/api/register" && request.method === "POST") {
                const { uid, nickname } = await request.json();
                if (!uid || !nickname) return new Response(JSON.stringify({ success: false }), { status: 400, headers: corsHeaders });
                await env.DB.prepare("INSERT OR REPLACE INTO employees (uid, nickname) VALUES (?, ?)")
                    .bind(uid, nickname).run();
                return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
            }

            if (url.pathname === "/api/log" && request.method === "POST") {
                const { uid, timestamp, image, is_suspicious, note, uids } = await request.json();
                
                let imageKey = null;
                if (image && env.PHOTOS) {
                    imageKey = `${uid}_${Date.now()}.jpg`;
                    const binaryImg = Uint8Array.from(atob(image.split(',')[1]), c => c.charCodeAt(0));
                    await env.PHOTOS.put(imageKey, binaryImg, {
                        contentType: 'image/jpeg',
                        customMetadata: { 
                            uploader: uid, 
                            timestamp: timestamp
                        }
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

            if (url.pathname === "/api/get_logs" && request.method === "GET") {
                const logs = await env.DB.prepare(`
                    SELECT a.timestamp, COALESCE(e.nickname, a.uid) as nickname, a.is_suspicious, a.image_key, a.check_note
                    FROM attendance_logs a 
                    LEFT JOIN employees e ON a.uid = e.uid 
                    ORDER BY a.timestamp DESC 
                    LIMIT 200
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
                return new Response(object.body, { headers });
            }

            return new Response("Not Found", { status: 404 });
        } catch (err) {
            return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
        }
    }
};"""

# --- HTML TEMPLATE (FIXED LOGIN UID + ROBUST OCR) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{SHOP_NAME_TH}} - Check-in System</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Sarabun:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script charset="utf-8" src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <style>
        :root { --primary: #06C755; --bg: #0f172a; --card: #ffffff; --text: #1e293b; }
        body { font-family: 'Outfit', 'Sarabun', sans-serif; background: radial-gradient(circle at top left, #063c1a, #0f172a); margin: 0; padding: 20px; color: var(--text); display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 420px; animation: fadeIn 0.8s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 { color: #fff; font-size: 1.8rem; margin: 0; }
        .line-badge { background: #06C755; color: white; padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; font-weight: 800; display: inline-block; margin-top: 5px; }
        .app-card { background: var(--card); border-radius: 30px; padding: 30px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); text-align: center; position: relative; overflow: hidden; }
        .user-profile { display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; background: #f8fafc; padding: 15px; border-radius: 24px; border: 1px solid #e2e8f0; }
        .profile-img { width: 60px; height: 60px; border-radius: 50%; border: 3px solid var(--primary); margin-bottom: 10px; background: #eee; object-fit: cover; }
        .upload-box { border: 2px dashed #cbd5e1; border-radius: 24px; height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f1f5f9; margin-bottom: 15px; cursor: pointer; position: relative; overflow: hidden; }
        .btn { border: none; padding: 15px; border-radius: 18px; width: 100%; font-size: 1rem; font-weight: 800; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-secondary { background: #f1f5f9; color: #64748b; margin-top: 10px; font-size: 0.85rem; }
        .btn-primary:disabled { background: #cbd5e1; opacity: 0.6; cursor: not-allowed; }
        .loader-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 2000; color: white; backdrop-filter: blur(8px); }
        .spinner { border: 4px solid rgba(255,255,255,0.1); border-top: 4px solid var(--primary); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 15px; }
        #historyArea { display: none; text-align: left; }
        .log-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 15px; }
        .log-table th { background: #f8fafc; padding: 10px; text-align: left; border-bottom: 2px solid #e2e8f0; color: #64748b; }
        .log-table td { padding: 10px; border-bottom: 1px solid #f1f5f9; }
        .tab-btn-group { display: flex; gap: 10px; margin-bottom: 20px; background: rgba(255,255,255,0.1); padding: 5px; border-radius: 15px; }
        .tab-btn { flex: 1; padding: 10px; border-radius: 10px; border: none; background: transparent; color: #fff; font-weight: 600; cursor: pointer; }
        .tab-btn.active { background: #fff; color: var(--bg); }
    </style>
</head>
<body>
    <div id="loadingOverlay" class="loader-overlay">
        <div class="spinner"></div>
        <div id="loadingText" style="text-align:center;">Connecting LINE...</div>
        <div id="bypassBtn" style="display:none; margin-top:20px;">
            <button onclick="checkD1Manual()" style="background:rgba(255,255,255,0.2); color:white; border:1px solid white; padding:8px 15px; border-radius:12px; font-size:0.8rem;">
                ใช้โหมด Manual (ไม่ผ่าน LINE)
            </button>
        </div>
    </div>
    
    <div class="container">
        <div class="header"><h1>{{SHOP_NAME_TH}}</h1><div class="line-badge">STAFF CHECKIN</div></div>
        <div class="tab-btn-group">
            <button id="tabIn" class="tab-btn active" onclick="switchTab('in')">ลงเวลา</button>
            <button id="tabHist" class="tab-btn" onclick="switchTab('hist')">ประวัติ</button>
        </div>
        <div class="app-card">
            <div id="mainApp">
                <div class="user-profile">
                    <img id="lineImg" class="profile-img" src="https://cdn-icons-png.flaticon.com/512/1077/1077114.png">
                    <div id="lineName" style="font-weight:700; font-size:1.1rem; color:#1e293b; margin-top:5px;">Loading...</div>
                    <div id="d1Nick" style="font-size:0.8rem; color:var(--primary); font-weight:600;">(รอรหัสพนักงาน...)</div>
                    <button class="btn" onclick="openMultiSelect()" style="font-size:0.75rem; background:#f1f5f9; color:#64748b; margin-top:8px; border-radius:10px; padding:5px 12px; border:1px solid #e2e8f0;">
                       <i class="fa-solid fa-users"></i> เลือกคนในรูป (<span id="selectedCount">1</span>)
                    </button>
                </div>
                <!-- UI เริ่มต้นจะล็อคไว้จนกว่าจะ Login สำเร็จ -->
                <div id="attendanceArea" style="opacity: 0.3; pointer-events: none;">
                    <div style="text-align:left; margin-bottom:10px; font-weight:600; font-size:0.85rem; color:#64748b;">
                        <i class="fa-solid fa-camera"></i> ถ่ายรูปแถบเวลาด้านล่าง
                    </div>
                    <input type="file" id="fileInput" hidden accept="image/*">
                    <div class="upload-box" onclick="document.getElementById('fileInput').click()">
                        <div id="placeholder" style="text-align:center;">
                            <i class="fa-solid fa-expand" style="font-size:2rem; color:#94a3b8; margin-bottom:10px;"></i>
                            <p style="font-size:0.85rem; color:#64748b;">กดเพื่อถ่ายภาพ</p>
                        </div>
                        <img id="previewImg" style="width:100%;height:100%;object-fit:cover;display:none;">
                    </div>
                    <div id="infoBox" style="background:#f8fafc; border:2px solid #e2e8f0; color:var(--text); padding:15px; border-radius:20px; display:none; margin-bottom:15px;">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                            <div style="border-right:1px solid #e2e8f0;">
                                <small style="font-size:0.6rem; color:#94a3b8;">DATE</small>
                                <span id="detectedDate" style="display:block; font-size:1rem; font-weight:800; color:var(--primary);">--/--/--</span>
                            </div>
                            <div>
                                <small style="font-size:0.6rem; color:#94a3b8;">TIME</small>
                                <span id="detectedTime" style="display:block; font-size:1rem; font-weight:800; color:var(--primary);">00:00:00</span>
                            </div>
                        </div>
                    </div>
                    <button class="btn btn-primary" id="submitBtn" disabled onclick="saveLog()">
                        <i class="fa-solid fa-check-circle"></i> บันทึกเวลาเข้างาน
                    </button>
                </div>
            </div>
            <div id="historyArea">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:15px;">
                   <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="downloadPDF()">PDF Report</button>
                   <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="downloadExcel()">Excel CSV</button>
                </div>
                <div style="max-height: 400px; overflow-y: auto;">
                    <table class="log-table">
                        <tbody id="logTableBody"><tr><td style="text-align:center;">แตะรีเฟรชเพื่อโหลดข้อมูล</td></tr></tbody>
                    </table>
                </div>
                <button class="btn btn-secondary" onclick="fetchLogs()" style="margin-top:15px;">
                    <i class="fa-solid fa-sync"></i> รีเฟรชข้อมูล
                </button>
            </div>
        </div>
    </div>
    
    <div id="regModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:2000;align-items:center;justify-content:center;padding:20px;">
        <div style="background:#fff;border-radius:30px;padding:35px;width:100%;max-width:350px;text-align:center;">
            <h2 style="color:var(--primary); margin-bottom:10px;">ยินดีต้อนรับ!</h2>
            <p style="margin-bottom:15px; font-size:0.9rem; color:#64748b;">กรุณาตั้งชื่อเล่น (ภาษาอังกฤษเท่านั้น)</p>
            <input type="text" id="regNick" placeholder="Ex. Somchai" 
                   style="width:100%;padding:15px;border-radius:15px;border:2px solid #e2e8f0;font-size:1.1rem;text-align:center;box-sizing:border-box;margin-bottom:15px;">
            <button class="btn btn-primary" onclick="doRegister()">ลงทะเบียนเริ่มใช้งาน</button>
        </div>
    </div>

    <div id="multiModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:2100;align-items:center;justify-content:center;padding:20px;">
        <div style="background:#fff;border-radius:24px;padding:20px;width:100%;max-width:350px;height:70vh;display:flex;flex-direction:column;">
            <h3 style="margin-bottom:10px; text-align:center;">เลือกใครบ้างในรูป?</h3>
            <input type="text" id="empSearch" placeholder="🔍 ค้นหาชื่อ..." oninput="renderEmployeeList(this.value)" style="width:100%; padding:10px; border-radius:10px; border:1px solid #ddd; margin-bottom:10px; box-sizing:border-box;">
            <div id="employeeChecklist" style="flex:1; overflow-y:auto; border:1px solid #eee; margin-bottom:15px;"></div>
            <div style="display:flex; gap:10px;">
                <button class="btn btn-secondary" onclick="document.getElementById('multiModal').style.display='none'">ยกเลิก</button>
                <button class="btn btn-primary" onclick="confirmSelection()">ตกลง</button>
            </div>
        </div>
    </div>

    <script>
        const LIFF_ID = "{{LIFF_ID}}";
        const API_BASE = "{{WORKER_URL}}";
        let USER_ID = localStorage.getItem('VELVET_UID') || null; 
        let MY_NICKNAME = localStorage.getItem('VELVET_NICK') || ""; 
        let ALL_EMPLOYEES = [];
        let SELECTED_ITEMS = []; 
        let DETECTED_ISO = null;

        const debugLog = (m) => { console.log("[LIFF]", m); const lt = document.getElementById('loadingText'); if(lt) lt.innerText = m; };

        // --- 1. LOGIN CORE ---
        async function initLIFF() {
            try {
                debugLog("Connecting to LINE...");
                
                // Safety Timeout: หาก LINE ค้าง 6 วิ ให้ขึ้นปุ่ม Manual
                const bypassTimer = setTimeout(() => {
                    if(!USER_ID) document.getElementById('bypassBtn').style.display = 'block';
                }, 6000);

                await liff.init({ liffId: LIFF_ID });
                if(!liff.isLoggedIn()) { liff.login(); return; }
                
                const profile = await liff.getProfile();
                USER_ID = profile.userId;
                localStorage.setItem('VELVET_UID', USER_ID);
                
                document.getElementById('lineImg').src = profile.pictureUrl || "https://cdn-icons-png.flaticon.com/512/1077/1077114.png";
                document.getElementById('lineName').innerText = profile.displayName;
                
                clearTimeout(bypassTimer);
                await checkD1();
            } catch (e) {
                console.error("LIFF Init Error:", e);
                debugLog("Error: " + e.message);
                if(!USER_ID) document.getElementById('bypassBtn').style.display = 'block';
            }
        }

        async function checkD1Manual() {
            const nick = prompt("กรุณาใส่ชื่อเล่นของคุณ (ภาษาอังกฤษ):");
            if(!nick) return;
            USER_ID = "MANUAL_" + nick.trim();
            MY_NICKNAME = nick.trim();
            localStorage.setItem('VELVET_UID', USER_ID);
            localStorage.setItem('VELVET_NICK', MY_NICKNAME);
            
            document.getElementById('lineName').innerText = MY_NICKNAME + " (Manual Mode)";
            await checkD1();
        }

        async function checkD1() {
            if(!USER_ID) return;
            showLoad("Verifying Identity...");
            try {
                const r = await fetch(`${API_BASE}/api/check_uid?uid=${USER_ID}`);
                const d = await r.json();
                if(d.success) {
                    MY_NICKNAME = d.nickname;
                    localStorage.setItem('VELVET_NICK', MY_NICKNAME);
                    SELECTED_ITEMS = [{uid: USER_ID, nickname: MY_NICKNAME}];
                    
                    document.getElementById('d1Nick').innerText = MY_NICKNAME;
                    document.getElementById('attendanceArea').style.opacity = "1";
                    document.getElementById('attendanceArea').style.pointerEvents = "auto";
                    showLoad(false);
                } else {
                    // ถ้าเป็น Manual แล้วยังไม่มีใน DB ให้สมัครให้อัตโนมัติ
                    if(USER_ID.startsWith("MANUAL_")) {
                        await registerUser(USER_ID, MY_NICKNAME);
                        await checkD1();
                    } else {
                        document.getElementById('regModal').style.display = 'flex';
                        showLoad(false);
                    }
                }
            } catch (e) {
                alert("🔴 Server Connection Error: " + e.message);
                showLoad(false);
            }
        }

        async function registerUser(uid, nick) {
            await fetch(`${API_BASE}/api/register`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ uid, nickname: nick })
            });
        }

        async function doRegister() {
            const nick = document.getElementById('regNick').value.trim();
            if(!/^[a-zA-Z0-9_]{2,20}$/.test(nick)) return alert("ใส่ชื่อเล่น 2-20 ตัวอักษร (A-Z, 0-9 เท่านั้น)");
            
            showLoad("Creating account...");
            try {
                await registerUser(USER_ID, nick);
                document.getElementById('regModal').style.display = 'none';
                await checkD1();
            } catch(e) { alert(e.message); showLoad(false); }
        }

        // --- 2. OCR & IMAGE ---
        document.getElementById('fileInput').onchange = async (e) => {
            const f = e.target.files[0]; if(!f) return;
            const url = URL.createObjectURL(f);
            document.getElementById('previewImg').src = url;
            document.getElementById('previewImg').style.display = 'block';
            document.getElementById('placeholder').style.display = 'none';
            
            showLoad("AI แกะข้อมูลเวลา...");
            try {
                if(typeof Tesseract === 'undefined') await loadScript('https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js');
                
                const img = new Image(); img.src = url; await new Promise(r=>img.onload=r);
                const worker = await Tesseract.createWorker('tha+eng');
                
                // Crop & Pre-process (Bottom 30% area)
                const cvs = document.createElement('canvas'); const ctx = cvs.getContext('2d');
                cvs.width = img.width; cvs.height = img.height * 0.35;
                ctx.drawImage(img, 0, img.height * 0.65, img.width, img.height * 0.35, 0, 0, img.width, cvs.height);
                
                // รอบที่ 1: ปกติ
                let res = await worker.recognize(cvs.toDataURL());
                let text = res.data.text;
                
                // รอบที่ 2: ถ้าอ่านได้น้อย ให้ลองกลับสี (สำหรับ GPS Camera ตัวหนังสือขาว)
                if(text.length < 15) {
                    ctx.filter = 'invert(1) grayscale(1) contrast(1.5)';
                    ctx.drawImage(img, 0, img.height * 0.65, img.width, img.height * 0.35, 0, 0, img.width, cvs.height);
                    res = await worker.recognize(cvs.toDataURL());
                    text += "\\n" + res.data.text;
                }
                
                parseOCR(text);
                await worker.terminate();
            } catch(e) { alert("AI Error: " + e.message); }
            finally { showLoad(false); }
        };

        function parseOCR(raw) {
            const text = raw.replace(/[\\\\n\\\\r]/g, ' ').replace(/\\\\s+/g, ' ');
            const dateRe = /(\\\\d{1,2})[\\\\/\\\\.-](\\\\d{1,2})[\\\\/\\\\.-](\\\\d{4})/;
            const timeRe = /(\\\\d{1,2})[:\\\\.](\\\\d{1,2})[:\\\\.](\\\\d{1,2})/;
            
            const dM = text.match(dateRe);
            const tM = text.match(timeRe);
            
            if(dM && tM) {
                let d = parseInt(dM[1]); let m = parseInt(dM[2]); let y = parseInt(dM[3]);
                if(m > 12) { let tmp = d; d = m; m = tmp; } // สลับ DD/MM หากพบค่าเดือน > 12
                
                let h = parseInt(tM[1]); let min = parseInt(tM[2]); let s = parseInt(tM[3]);
                if(text.includes("PM") && h < 12) h += 12;
                if(text.includes("AM") && h === 12) h = 0;
                
                const fy = y > 2400 ? y - 543 : y;
                const dObj = new Date(fy, m-1, d, h, min, s);
                if(!isNaN(dObj)) {
                    DETECTED_ISO = dObj.toISOString();
                    document.getElementById('detectedDate').innerText = `${d}/${m}/${fy}`;
                    document.getElementById('detectedTime').innerText = `${h.toString().padStart(2,'0')}:${min.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
                    document.getElementById('infoBox').style.display = 'block';
                    document.getElementById('submitBtn').disabled = false;
                    return;
                }
            }
            alert("⚠️ อ่านวันเวลาไม่ชัด! กรุณาถ่ายใหม่ให้เห็นแถบเวลาชัดเจนครับ");
        }

        async function saveLog() {
            showLoad("กำลังย่อรูปและบันทึก...");
            try {
                const img = document.getElementById('previewImg');
                const cvs = document.createElement('canvas'); const ctx = cvs.getContext('2d');
                const max = 1200; let w = img.naturalWidth; let h = img.naturalHeight;
                if(w > max) { h *= max/w; w = max; }
                cvs.width = w; cvs.height = h; ctx.drawImage(img, 0, 0, w, h);
                const b64 = cvs.toDataURL('image/jpeg', 0.7);

                const uids = SELECTED_ITEMS.map(i => i.uid);
                const r = await fetch(`${API_BASE}/api/log`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        uid: USER_ID, uids: uids, timestamp: DETECTED_ISO, image: b64, note: ""
                    })
                });
                if(r.ok) { alert("✅ บันทึกเวลาสำเร็จ!"); switchTab('hist'); }
                else throw new Error("Save Failed");
            } catch(e) { alert("Error: " + e.message); }
            finally { showLoad(false); }
        }

        // --- 3. UI UTILS ---
        function switchTab(t) {
            document.getElementById('mainApp').style.display = t==='in'?'block':'none';
            document.getElementById('historyArea').style.display = t==='hist'?'block':'none';
            document.getElementById('tabIn').className = t==='in'?'tab-btn active':'tab-btn';
            document.getElementById('tabHist').className = t==='hist'?'tab-btn active':'tab-btn';
            if(t==='hist') fetchLogs();
        }

        async function fetchLogs() {
            const body = document.getElementById('logTableBody');
            body.innerHTML = '<tr><td style="text-align:center;">Loading...</td></tr>';
            try {
                const r = await fetch(`${API_BASE}/api/get_logs`);
                const d = await r.json();
                body.innerHTML = '';
                d.forEach(l => {
                    body.innerHTML += `<tr>
                        <td><b>${l.nickname}</b><br><small style="color:#64748b;">${new Date(l.timestamp).toLocaleString('th-TH')}</small></td>
                    </tr>`;
                });
            } catch(e) { body.innerHTML = '<tr><td>Error loading data</td></tr>'; }
        }

        async function openMultiSelect() {
            showLoad("Loading Employees...");
            try {
                const r = await fetch(`${API_BASE}/api/get_employees`);
                ALL_EMPLOYEES = await r.json();
                renderEmployeeList();
                document.getElementById('multiModal').style.display = 'flex';
            } catch(e) { alert(e.message); } finally { showLoad(false); }
        }

        function renderEmployeeList(q = '') {
            const div = document.getElementById('employeeChecklist'); div.innerHTML = '';
            ALL_EMPLOYEES.filter(e => e.nickname.toLowerCase().includes(q.toLowerCase())).forEach(e => {
                const checked = SELECTED_ITEMS.find(i => i.uid === e.uid) ? 'checked' : '';
                div.innerHTML += `<label style="display:flex; padding:12px; border-bottom:1px solid #eee; align-items:center;">
                    <input type="checkbox" ${checked} onchange="toggleSel('${e.uid}', '${e.nickname}', this.checked)" style="width:20px; height:20px; margin-right:12px;">
                    <b>${e.nickname}</b>
                </label>`;
            });
        }

        window.toggleSel = (uid, nick, checked) => {
            if(checked) { if(!SELECTED_ITEMS.find(i=>i.uid===uid)) SELECTED_ITEMS.push({uid, nickname: nick}); }
            else { SELECTED_ITEMS = SELECTED_ITEMS.filter(i=>i.uid!==uid); }
        }

        window.confirmSelection = () => {
            if(SELECTED_ITEMS.length === 0) SELECTED_ITEMS = [{uid: USER_ID, nickname: MY_NICKNAME}];
            document.getElementById('d1Nick').innerText = SELECTED_ITEMS.map(i=>i.nickname).join(", ");
            document.getElementById('selectedCount').innerText = SELECTED_ITEMS.length;
            document.getElementById('multiModal').style.display = 'none';
        }

        function showLoad(msg) {
            const o = document.getElementById('loadingOverlay');
            if(msg === false) o.style.display = 'none';
            else { document.getElementById('loadingText').innerText = msg; o.style.display = 'flex'; }
        }

        function loadScript(src) { return new Promise((s,f)=>{const sc=document.createElement('script');sc.src=src;sc.onload=s;sc.onerror=f;document.head.appendChild(sc);}); }
        
        initLIFF();
    </script>
</body>
</html>
"""

def main():
    st.set_page_config(page_title="Velvet D1 Auto-Pack", page_icon="📦", layout="centered")
    st.title("📦 Velvet D1 Auto-Pack Generator")
    st.markdown("### สร้างระบบลงเวลา + จัดเก็บไฟล์แยกโฟลเดอร์ + จดจำค่าเดิม")

    config = load_config()

    with st.expander("🛠️ ข้อมูลร้านและการเชื่อมต่อ", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            shop_name = st.text_input("ชื่อร้าน (ไทย)", value=config.get("shop_name", "Velvet Shop"))
            liff_id = st.text_input("LINE LIFF ID", value=config.get("liff_id", ""))
        with col2:
            worker_url = st.text_input("Worker URL", value=config.get("worker_url", ""), placeholder="https://...")
            folder_name = st.text_input("ชื่อโฟลเดอร์สำหรับส่งออก", value=config.get("folder_name", "output_system"))
        
        st.info("💡 **การตั้งค่า Cloudflare:**\n1. ผูก D1 Database ชื่อตัวแปร **'DB'**\n2. ผูก R2 Bucket ชื่อตัวแปร **'PHOTOS'**")

    if st.button("🚀 สร้างและส่งออกไฟล์ทั้งหมด (Build & Save)", type="primary"):
        # Clean inputs
        s_name = shop_name.strip()
        w_url = worker_url.strip().strip("/")
        l_id = liff_id.strip()
        f_name = folder_name.strip()

        if not w_url or not l_id or not f_name:
            st.error("กรุณากรอกข้อมูลให้ครบทุกช่องครับ")
        else:
            # Save config for next time
            save_config({
                "shop_name": s_name,
                "worker_url": w_url,
                "liff_id": l_id,
                "folder_name": f_name
            })

            # Create output directory
            base_path = os.path.dirname(os.path.abspath(__file__))
            out_path = os.path.join(base_path, f_name)
            os.makedirs(out_path, exist_ok=True)

            # Generate contents
            final_html = HTML_TEMPLATE.replace("{{SHOP_NAME_TH}}", s_name)\
                                      .replace("{{WORKER_URL}}", w_url)\
                                      .replace("{{LIFF_ID}}", l_id)

            # Write files
            files = {
                "index.html": final_html,
                "worker.js": WORKER_CONTENT,
                "schema.sql": SCHEMA_CONTENT
            }

            for name, content in files.items():
                with open(os.path.join(out_path, name), "w", encoding="utf-8") as f:
                    f.write(content)

            st.success(f"✨ สำเร็จ! สร้างโฟลเดอร์ '{f_name}' เรียบร้อยแล้วที่:\n\n`{out_path}`")

if __name__ == "__main__":
    # ตรวจสอบว่ากำลังรันภายใต้ Streamlit หรือไม่
    try:
        from streamlit.runtime import exists as st_exists
        running_in_streamlit = st_exists()
    except ImportError:
        running_in_streamlit = False

    if running_in_streamlit:
        main()
    else:
        print("--- กำลังเปิดระบบ Attendance Generator (Cloud D1) กรุณารอสักครู่ ---")
        script_path = os.path.abspath(__file__)
        try:
            # ใช้ subprocess เพื่อเปิด streamlit run
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", script_path])
            print("\n✅ ระบบกำลังเปิดหน้าเว็บใน Browser... คุณสามารถย่อหน้าต่างนี้ลงได้ครับ")
        except Exception as e:
            print(f"❌ ไม่สามารถเปิดอัตโนมัติได้: {e}")
            print("กรุณารันด้วยคำสั่ง: streamlit run", script_path)