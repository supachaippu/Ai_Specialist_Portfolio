import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox
import os
import json
import webbrowser
import random
import colorsys
import re

# ==============================================================================
# 1. HTML TEMPLATE (UI: V23 | LOGIC: V36)
# ==============================================================================
HTML_RAW = r"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>__SHOP__</title>
    <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            /* DYNAMIC VARIABLES */
            --bg-color: __BG_COLOR__;
            --card-grad-start: __GRAD_START__;
            --card-grad-end: __GRAD_END__;
            --text-main: __TEXT_MAIN__;
            --text-sub: __TEXT_SUB__;
            --accent: __ACCENT__;
            
            /* SHAPE VARIABLES (Default to V23 style if not overridden) */
            --radius: __RADIUS__;
            --shadow: __SHADOW__;
            --border: __BORDER__;
        }

        body {
            font-family: 'Prompt', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            -webkit-tap-highlight-color: transparent;
            overflow-x: hidden;
        }

        /* --- LAYOUT ENGINE CSS --- */
        __LAYOUT_CSS__

        /* --- STANDARD UI COMPONENTS (V23 Style Preserved) --- */
        .glass-input {
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: var(--radius);
            padding: 12px;
            width: 100%;
            color: var(--text-main);
            outline: none;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .glass-input:focus { border-color: var(--accent); background: rgba(0,0,0,0.5); }

        .btn-action {
            background: var(--accent);
            color: #000;
            font-weight: bold;
            padding: 14px;
            border-radius: var(--radius);
            width: 100%;
            border: none;
            font-size: 16px;
            box-shadow: 0 0 10px var(--accent);
        }
        
        .hidden { display: none !important; }
        
        .file-upload {
            border: 2px dashed rgba(255,255,255,0.3);
            border-radius: var(--radius);
            padding: 20px;
            text-align: center;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .file-upload.has-img { border-style: solid; border-color: var(--accent); padding: 0; overflow: hidden; }
        .preview-img { width: 100%; height: 200px; object-fit: cover; }

        .type-btn {
            flex: 1; padding: 12px; border-radius: var(--radius); border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05); color: #aaa; transition: all 0.2s;
        }
        .type-btn.active {
            background: var(--accent); color: #000; font-weight: bold; border-color: var(--accent); box-shadow: 0 0 10px var(--accent);
        }

        .swal2-popup { background: #1e293b !important; color: white !important; border: 1px solid rgba(255,255,255,0.1); border-radius: 20px !important; }
        .swal2-title { color: var(--accent) !important; }
        .swal2-confirm { background-color: var(--accent) !important; color: black !important; font-weight: bold !important; border-radius: 10px !important; }
        .swal2-cancel { background-color: #334155 !important; color: white !important; border-radius: 10px !important; }
    </style>
</head>
<body class="p-6 max-w-md mx-auto w-full relative">

    <div id="loading" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 backdrop-blur-sm">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-t-transparent" style="border-color: var(--accent);"></div>
        <p class="mt-4 text-sm" style="color: var(--text-sub);">Connecting...</p>
    </div>

    <div class="flex justify-between items-center mb-8">
        <div onclick="secretTap()">
            <h1 class="text-2xl font-bold select-none cursor-pointer" style="color: var(--accent);">__SHOP__</h1>
            <p class="text-xs select-none" style="color: var(--text-sub);">Nightlife System</p>
        </div>
        <div class="flex gap-2">
            <button id="btn-staff-switch" onclick="toggleStaffMode()" class="hidden text-xs bg-white/10 px-3 py-1 rounded-full border border-white/5 text-gray-300 flex items-center gap-1"><span>🔄</span> Staff Mode</button>
            <button onclick="verifyManager()" class="opacity-50 hover:opacity-100 p-2">⚙️</button>
        </div>
    </div>

    <div id="view-customer" class="hidden animate-fade-in">
        <div class="flex items-center gap-4 mb-6 bg-white/5 p-4 rounded-2xl border border-white/10">
            <img id="user-img" class="w-12 h-12 rounded-full border-2" style="border-color: var(--accent);" src="">
            <div><p class="text-xs" style="color: var(--text-sub);">Welcome,</p><h2 id="user-name" class="font-bold text-lg truncate w-48">Guest</h2></div>
        </div>

        <div id="menu-container" class="menu-layout">
            <div onclick="show('view-booking')" class="btn-menu menu-item-1">
                <span class="icon">📅</span>
                <div class="text-wrap">
                    <span class="label">จองโต๊ะ</span>
                    <span class="sub-label">Reservation</span>
                </div>
            </div>
            <div onclick="show('view-wallet'); startWalletSync();" class="btn-menu menu-item-2">
                <span class="icon">🥃</span>
                <div class="text-wrap">
                    <span class="label">My Wallet</span>
                    <span class="sub-label">ฝากเหล้า / เช็ครายการ</span>
                </div>
            </div>
        </div>
    </div>

    <div id="view-staff" class="hidden space-y-4">
        <div class="bg-blue-900/20 p-3 rounded-lg border border-blue-500/30 text-center mb-4"><span class="text-blue-400 font-bold text-sm">🔵 STAFF WORKING MODE</span></div>
        <div class="grid grid-cols-2 gap-4">
            <div onclick="openDepositFlow()" class="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center cursor-pointer flex flex-col items-center justify-center"><span class="text-3xl block mb-2">📥</span><span class="font-bold text-white">รับฝาก</span></div>
            <div onclick="openWithdrawScanner()" class="bg-gray-800 border border-red-900 rounded-xl p-4 text-center cursor-pointer flex flex-col items-center justify-center" style="background: linear-gradient(135deg, #3f1010, #1a0505);"><span class="text-3xl block mb-2">📤</span><span class="font-bold text-red-400">เบิกออก</span></div>
        </div>
    </div>

    <div id="view-wallet" class="hidden">
        <div class="flex justify-between mb-4">
            <button onclick="stopWalletSync(); show('view-customer')" class="text-sm flex items-center gap-1" style="color: var(--text-sub);">← Back</button>
            <button onclick="manualClaimInput()" class="text-xs bg-[var(--accent)] text-black px-3 py-1 rounded-full font-bold">🔑 กรอกรหัสรับของ</button>
        </div>
        <h2 class="text-xl font-bold mb-4">🍾 My Collection</h2>
        <div class="text-sm font-bold text-[var(--accent)] border-b border-white/10 pb-2 mb-4">📦 รายการคงเหลือ (Active)</div><div id="wallet-active" class="space-y-4 pb-4 min-h-[100px]"></div>
        <div class="text-sm font-bold text-gray-500 border-b border-white/10 pb-2 mb-4 mt-8">🕒 ประวัติการเบิก (History)</div><div id="wallet-history" class="space-y-2 pb-24 opacity-60"></div>
    </div>

    <div id="view-booking" class="hidden">
        <div class="flex justify-between mb-4"><h2 class="text-xl font-bold">📝 จองโต๊ะ</h2><button onclick="show('view-customer')">✕</button></div>
        <div class="bg-white/5 p-6 rounded-2xl border border-white/10 space-y-3">
            <input type="text" id="bk-name" placeholder="ชื่อผู้จอง" class="glass-input"><input type="tel" id="bk-phone" placeholder="เบอร์โทรติดต่อ" class="glass-input">
            <div class="flex gap-2"><input type="date" id="bk-date" class="glass-input"><input type="time" id="bk-time" value="20:00" class="glass-input"></div>
            <input type="text" id="bk-pax" placeholder="จำนวนคน" class="glass-input"><button onclick="submitBooking()" class="btn-action mt-2">ยืนยันการจอง</button>
        </div>
    </div>

    <div id="modal-deposit" class="fixed inset-0 z-[70] hidden flex-col bg-black overflow-y-auto p-4">
        <div class="flex justify-between mb-4"><h2 class="text-xl font-bold text-white">📸 ฝากของ</h2><button onclick="closeModal('modal-deposit')" class="text-gray-400">✕</button></div>
        <label class="file-upload" id="dep-img-area"><input type="file" accept="image/*" capture="environment" id="dep-file" class="hidden" onchange="previewDepositImage(this)"><div id="dep-placeholder"><div class="text-4xl mb-2">📷</div><p class="text-sm text-gray-400">แตะเพื่อเปิดกล้อง</p></div><img id="dep-preview" class="hidden preview-img"></label>
        <div class="flex justify-end mb-4"><label class="text-xs text-gray-400 underline cursor-pointer">เลือกรูปจากอัลบั้ม<input type="file" accept="image/*" class="hidden" onchange="previewDepositImage(this)"></label></div>
        <div class="space-y-3"><div class="flex gap-2"><button onclick="setDepType('liquor')" id="btn-type-liquor" class="type-btn active">🥃 เหล้า</button><button onclick="setDepType('beer')" id="btn-type-beer" class="type-btn">🍺 เบียร์</button></div><input list="drink-list" id="dep-brand" placeholder="ค้นหายี่ห้อ..." class="glass-input"><datalist id="drink-list"></datalist><input id="dep-amount" type="number" placeholder="จำนวน / %" class="glass-input"><input id="dep-remark" placeholder="หมายเหตุ" class="glass-input"><button onclick="submitDeposit()" class="btn-action">บันทึกรายการ</button></div>
    </div>

    <div id="modal-deposit-success" class="fixed inset-0 z-[80] hidden flex items-center justify-center bg-black/95 p-6">
        <div class="bg-gray-900 w-full rounded-2xl p-6 text-center border border-green-500/30 overflow-y-auto max-h-screen">
            <div class="text-5xl mb-2">⏳</div><h2 class="text-2xl font-bold text-white mb-1">รอลูกค้ารับของ</h2><p class="text-gray-400 text-xs mb-4">ให้ลูกค้าสแกน QR หรือกรอกรหัสด้านล่าง</p>
            <div class="bg-white/10 rounded-xl p-4 mb-4"><span id="success-code" class="text-6xl font-mono font-bold tracking-widest text-green-400">0000</span><p class="text-xs text-gray-500 mt-2">รหัสสำหรับลูกค้า</p></div>
            <div class="bg-white p-3 rounded-xl w-fit mx-auto mb-4"><div id="success-qr"></div></div>
            <button id="btn-copy-link" onclick="copyClaimLink()" class="w-full bg-blue-600/30 text-blue-400 border border-blue-500/50 py-2 rounded-lg mb-6 text-sm">📋 คัดลอกลิ้งค์ส่งให้ลูกค้า</button>
            <button onclick="show('view-staff'); stopStaffCheck();" class="btn-action bg-gray-700 text-white">ปิดหน้าต่าง</button>
        </div>
    </div>

    <div id="modal-withdraw" class="fixed inset-0 z-[70] hidden flex-col bg-black p-4"><div class="flex justify-between mb-4"><h2 class="text-xl font-bold text-white">📤 สแกนเพื่อเบิก</h2><button onclick="closeModal('modal-withdraw')" class="text-gray-400">✕</button></div><div id="reader" class="rounded-xl overflow-hidden mb-4 border border-white/20 bg-black min-h-[250px]"></div><label class="block text-center mb-4"><span class="text-xs text-gray-400 bg-white/10 px-3 py-1 rounded-full cursor-pointer">📂 อัปโหลดรูป QR</span><input type="file" accept="image/*" class="hidden" onchange="cleanFromFile(this)"></label><div class="flex gap-2"><input id="manual-code" placeholder="รหัส 4 หลัก" class="glass-input text-center text-xl tracking-widest font-mono"><button onclick="manualWithdraw()" class="btn-action w-auto px-6">เบิก</button></div></div>

    <div id="view-manager" class="hidden"><div class="flex justify-between items-center mb-4"><h2 class="text-xl font-bold text-white">👑 Dashboard</h2><button onclick="location.reload()" class="text-xs bg-red-900 text-red-200 px-3 py-1 rounded">Logout</button></div><div class="flex gap-2 mb-4 bg-white/5 p-1 rounded-xl"><button onclick="switchMgrTab('stock')" class="flex-1 py-2 rounded-lg text-sm font-bold bg-white/10">📦 Stock</button><button onclick="switchMgrTab('users')" class="flex-1 py-2 rounded-lg text-sm text-gray-400 hover:text-white">👥 Staff</button><button onclick="switchMgrTab('logs')" class="flex-1 py-2 rounded-lg text-sm text-gray-400 hover:text-white">📜 Logs</button></div><div id="mgr-tab-stock" class="space-y-4"><div class="bg-white/5 p-3 rounded-xl border border-white/10 flex flex-wrap gap-2"><div class="flex w-full gap-2"><input id="filter-brand" placeholder="🔍 ค้นหา..." class="bg-black/30 text-white text-sm px-3 py-2 rounded-lg flex-1 outline-none border border-white/10"><button onclick="filterStock()" class="bg-[var(--accent)] text-black px-4 py-2 rounded-lg font-bold">ค้นหา</button></div><select id="filter-expiry" onchange="filterStock()" class="bg-black/30 text-white text-sm px-3 py-2 rounded-lg outline-none border border-white/10"><option value="all">📅 วันหมดอายุ</option><option value="7">⚠️ < 7 วัน</option><option value="14">⚠️ < 14 วัน</option></select><select id="filter-pct" onchange="filterStock()" class="bg-black/30 text-white text-sm px-3 py-2 rounded-lg outline-none border border-white/10"><option value="all">📊 ปริมาณ</option><option value="low">🔴 น้อย</option><option value="mid">🟡 กลาง</option><option value="high">🟢 เยอะ</option></select></div><div id="stock-list" class="space-y-2 h-[400px] overflow-y-auto pb-10">Loading Stock...</div></div><div id="mgr-tab-users" class="hidden space-y-4"><div class="bg-white/5 p-4 rounded-xl border-l-4 border-yellow-500"><h3 class="text-yellow-500 font-bold mb-2">Pending</h3><div id="pending-list" class="space-y-2 text-sm"></div></div><div class="bg-white/5 p-4 rounded-xl border-l-4 border-green-500"><h3 class="text-green-500 font-bold mb-2">Active</h3><div id="active-list" class="space-y-2 text-sm"></div></div></div><div id="mgr-tab-logs" class="hidden bg-white/5 p-2 rounded-xl h-[500px] overflow-y-auto"><div id="logs-list" class="space-y-4 text-xs">Loading...</div></div></div>
    
    <div id="view-staff-register" class="fixed inset-0 z-[65] hidden flex items-center justify-center bg-black/90 p-6"><div class="bg-[#1e293b] w-full max-w-xs p-6 rounded-2xl border border-white/10 text-center"><h2 class="text-xl font-bold mb-2 text-white">New Staff</h2><input type="text" id="reg-name" placeholder="ชื่อเล่น" class="glass-input text-center"><button onclick="registerStaff()" class="btn-action mt-2">ส่งคำขอ</button><button onclick="show('view-customer')" class="text-gray-500 text-sm mt-4">ยกเลิก</button></div></div>
    <div id="view-staff-waiting" class="fixed inset-0 z-[65] hidden flex flex-col items-center justify-center bg-black"><div class="text-6xl mb-4">⏳</div><h2 class="text-xl font-bold text-white">รอการอนุมัติ</h2><p id="my-uid-display" class="mt-6 bg-white/10 p-2 rounded text-xs font-mono select-all text-gray-300"></p><button onclick="show('view-customer')" class="mt-8 text-gray-500 underline">กลับหน้าหลัก</button></div>

    <script>
        const CFG = { liff: "__LIFF__", worker: "__WORKER__", shop: "__SHOP__", r2: "__R2_URL__", hold: "__HOLD_TIME__" };
        let profile={}, html5QrcodeScanner=null, depType='liquor', walletInterval=null, isStaffMode=false, staffUser=null, qrTimer=null, qrPoll=null, staffCheckInterval=null, allStockData=[], secretTapCount=0, currentClaimLink="";
        const DRINKS = ["Chang", "Singha", "Leo", "Heineken", "Tiger", "Budweiser", "Hoegaarden", "Hoegaarden Rosée", "Stella Artois", "San Miguel", "San Miguel Light", "Federbräu", "Snowy Weizen", "Copper", "Corona", "Asahi", "Carlsberg", "Regency", "SangSom", "Blend 285", "Blend 285 Signature", "Hong Thong", "Meridian", "Johnnie Walker Red", "Johnnie Walker Black", "Johnnie Walker Double Black", "Johnnie Walker Gold", "Johnnie Walker Blue", "Chivas Regal 12", "Chivas Regal 18", "Jack Daniel’s", "Jameson", "Ballantine's", "Monkey Shoulder", "Absolut Vodka", "Grey Goose", "Suntory Kakubin", "Bombay Sapphire", "Jose Cuervo", "Penfolds Bin 2", "Penfolds Bin 389", "Penfolds Bin 407", "Yellow Tail", "Jacob's Creek", "Casillero del Diablo", "Mont Gras", "Robert Mondavi", "Concha y Toro", "Silver Oak", "Sutter Home", "Berri Estates"];

        // --- MOCK DATA FOR PREVIEW MODE (V32 Feature) ---
        const MOCK_STOCK = [
            { item_name: "Regency", item_type: "liquor", amount: 60, deposit_code: "0001", expiry_date: new Date(new Date().getTime() + 5*24*60*60*1000), owner_name: "ลูกค้า A" },
            { item_name: "Leo", item_type: "beer", amount: 3, deposit_code: "0002", expiry_date: new Date(new Date().getTime() + 20*24*60*60*1000), owner_name: "ลูกค้า B" },
            { item_name: "Black Label", item_type: "liquor", amount: 25, deposit_code: "0003", expiry_date: new Date(new Date().getTime() + 2*24*60*60*1000), owner_name: "ลูกค้า C" }
        ];

        function isPreviewMode() { return location.protocol === 'file:' || location.href.includes("preview_temp.html") || CFG.worker === ""; }

        function compressImage(file, quality=0.7, maxWidth=800) {
            return new Promise((resolve) => {
                const reader = new FileReader(); reader.readAsDataURL(file);
                reader.onload = (e) => {
                    const img = new Image(); img.src = e.target.result;
                    img.onload = () => {
                        const cvs = document.createElement('canvas');
                        let w = img.width, h = img.height;
                        if(w > maxWidth) { h = Math.round((h*maxWidth)/w); w = maxWidth; }
                        cvs.width = w; cvs.height = h;
                        cvs.getContext('2d').drawImage(img, 0, 0, w, h);
                        resolve(cvs.toDataURL('image/jpeg', quality));
                    };
                };
            });
        }

        async function main() {
            try {
                const dl = document.getElementById('drink-list');
                DRINKS.forEach(d => { const op = document.createElement('option'); op.value = d; dl.appendChild(op); });
                await liff.init({ liffId: CFG.liff });
                
                // --- PREVIEW MODE HANDLER ---
                if (!liff.isLoggedIn()) {
                    if (isPreviewMode()) {
                        profile = { userId: "PREVIEW", displayName: "Test User", pictureUrl: "https://via.placeholder.com/150" };
                        show('view-customer');
                        document.getElementById('loading').classList.add('hidden');
                        return;
                    }
                    liff.login({ redirectUri: window.location.href });
                    return;
                }
                
                profile = await liff.getProfile();
                document.getElementById('user-img').src = profile.pictureUrl;
                document.getElementById('user-name').innerText = profile.displayName;
                document.getElementById('bk-date').valueAsDate = new Date();
                
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.get('action') === 'register') { show('view-staff-register'); document.getElementById('loading').classList.add('hidden'); return; }
                if (urlParams.get('claim_id')) await claimDeposit(urlParams.get('claim_id'));
                
                checkRole();
            } catch (e) { 
                if(isPreviewMode()) {
                    profile = { userId: "PREVIEW", displayName: "Test User", pictureUrl: "https://via.placeholder.com/150" };
                    document.getElementById('user-img').src = profile.pictureUrl;
                    document.getElementById('user-name').innerText = profile.displayName;
                    show('view-customer');
                    document.getElementById('loading').classList.add('hidden');
                } else { Swal.fire('Error', e.message, 'error'); }
            }
        }

        async function checkRole() {
            try {
                if (isPreviewMode()) { document.getElementById('loading').classList.add('hidden'); show('view-customer'); return; }
                const res = await fetch(CFG.worker + "/api/me?uid=" + profile.userId);
                const data = await res.json();
                document.getElementById('loading').classList.add('hidden');
                if (data.status === 'pending') { show('view-staff-waiting'); document.getElementById('my-uid-display').innerText = profile.userId; }
                else if (data.role === 'staff' || data.role === 'manager') { staffUser = data; document.getElementById('btn-staff-switch').classList.remove('hidden'); sessionStorage.setItem('staffName', data.name); isStaffMode = true; updateModeUI(); }
                else { show('view-customer'); }
            } catch (e) { Swal.fire("Connect Error", "Check Worker URL", "error"); }
        }

        function show(id) { document.querySelectorAll('[id^="view-"], [id^="modal-"]').forEach(el => { el.classList.add('hidden'); el.classList.remove('flex'); }); const t = document.getElementById(id); t.classList.remove('hidden'); if(id.startsWith('modal-')) t.classList.add('flex'); window.scrollTo(0,0); }
        function toggleStaffMode() { isStaffMode = !isStaffMode; updateModeUI(); }
        function updateModeUI() { const btnText = document.getElementById('staff-mode-text'); if (btnText) { btnText.innerText = isStaffMode ? "Switch to Personal" : "Back to Work"; show(isStaffMode ? 'view-staff' : 'view-customer'); } }
        function closeModal(id) { show(isStaffMode ? 'view-staff' : 'view-customer'); if(html5QrcodeScanner) { html5QrcodeScanner.clear(); html5QrcodeScanner = null; } }
        function secretTap() { secretTapCount++; if (secretTapCount >= 5) { show('view-staff-register'); secretTapCount = 0; } }

        async function submitBooking() { 
            const d = { n: document.getElementById('bk-name').value, p: document.getElementById('bk-phone').value, date: document.getElementById('bk-date').value, time: document.getElementById('bk-time').value, pax: document.getElementById('bk-pax').value };
            if(!d.n || !d.p || !d.pax) return Swal.fire("แจ้งเตือน", "กรุณากรอกข้อมูลให้ครบ", "warning");
            const msg = `✨ RESERVATION CONFIRMED ✨\n━━━━━━━━━━━━━━━━━━\n${CFG.shop}\n👤 ชื่อผู้จอง: ${d.n}\n📅 วันที่: ${d.date}\n👥 จำนวน: ${d.pax}\n📞 ติดต่อ: ${d.p}\n⏰ เวลา: ${d.time}\n\nกรุณามารับโต๊ะก่อนเวลา ${CFG.hold} น.\nเพื่อรักษาสิทธิ์ของท่าน\n━━━━━━━━━━━━━━━━━━`;
            if(liff.isInClient()) { await liff.sendMessages([{type:'text', text:msg}]); liff.closeWindow(); } else { Swal.fire("Simulated", msg, "info").then(()=> show('view-customer')); }
        }

        function openDepositFlow() { document.getElementById('dep-file').value = ""; document.getElementById('dep-preview').src = ""; document.getElementById('dep-preview').classList.add('hidden'); document.getElementById('dep-placeholder').classList.remove('hidden'); document.getElementById('dep-img-area').classList.remove('has-img'); document.getElementById('dep-brand').value = ""; document.getElementById('dep-amount').value = ""; document.getElementById('dep-remark').value = ""; setDepType('liquor'); show('modal-deposit'); }
        function previewDepositImage(input) { if (input.files && input.files[0]) { const reader = new FileReader(); reader.onload = function(e) { document.getElementById('dep-preview').src = e.target.result; document.getElementById('dep-preview').classList.remove('hidden'); document.getElementById('dep-placeholder').classList.add('hidden'); document.getElementById('dep-img-area').classList.add('has-img'); }; reader.readAsDataURL(input.files[0]); } }
        function setDepType(t) { depType = t; document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active')); document.getElementById('btn-type-'+t).classList.add('active'); document.getElementById('dep-amount').placeholder = (t === 'liquor') ? "จำนวนเหลือ (%)" : "จำนวน (ขวด)"; }

        async function submitDeposit() {
            const file = document.getElementById('dep-file').files[0] || document.querySelector('input[type="file"]:not(#dep-file)').files[0];
            const brand = document.getElementById('dep-brand').value; const amt = document.getElementById('dep-amount').value; const remark = document.getElementById('dep-remark').value;
            if(!file) return Swal.fire("แจ้งเตือน", "กรุณาถ่ายรูป", "warning");
            if(!brand || !amt) return Swal.fire("แจ้งเตือน", "กรอกข้อมูลให้ครบ", "warning");
            const btn = document.querySelector('#modal-deposit .btn-action'); const oldText = btn.innerText; btn.innerText = "กำลังย่อรูป..."; btn.disabled = true;
            
            // Preview Mode Mock
            if(isPreviewMode()) {
                setTimeout(() => {
                    show('modal-deposit-success');
                    document.getElementById('success-code').innerText = "0001";
                    btn.innerText = oldText; btn.disabled = false;
                }, 1000);
                return;
            }

            const base64Img = await compressImage(file);
            btn.innerText = "กำลังบันทึก...";

            try {
                const res = await fetch(CFG.worker + "/api/deposit", { method: 'POST', body: JSON.stringify({ staff_name: sessionStorage.getItem('staffName') || 'Staff', item_name: brand, item_type: depType, amount: amt, remarks: remark, image: base64Img }) });
                const data = await res.json();
                show('modal-deposit-success'); document.getElementById('success-code').innerText = data.code;
                document.getElementById('success-qr').innerHTML = ""; 
                currentClaimLink = `https://liff.line.me/${CFG.liff}?claim_id=${data.deposit_id}`;
                new QRCode(document.getElementById("success-qr"), { text: currentClaimLink, width: 128, height: 128 });
                startStaffCheck(data.deposit_id);
            } catch(e) { Swal.fire("Error", "Save Failed: " + e, "error"); } finally { btn.innerText = oldText; btn.disabled = false; }
        }

        function copyClaimLink() {
            if(navigator.clipboard) { navigator.clipboard.writeText(currentClaimLink); Swal.fire({ toast: true, position: 'top', icon: 'success', title: 'คัดลอกลิ้งค์แล้ว', showConfirmButton: false, timer: 1500 }); } 
            else { prompt("Copy link:", currentClaimLink); }
        }

        function startStaffCheck(depositId) {
            if(staffCheckInterval) clearTimeout(staffCheckInterval);
            let attempt = 0;
            const check = async () => {
                attempt++;
                try {
                    const res = await fetch(CFG.worker + "/api/check-deposit?id=" + depositId); const data = await res.json();
                    if (data.claimed) { Swal.fire({ title: '✅ เรียบร้อย!', text: 'ลูกค้าได้รับของแล้ว', icon: 'success' }).then(() => show('view-staff')); return; }
                } catch(e) {}
                let delay = 2000; if(attempt > 10) delay = 5000; if(attempt > 20) delay = 10000; if(attempt < 40) staffCheckInterval = setTimeout(check, delay); 
            }; check();
        }
        function stopStaffCheck() { if(staffCheckInterval) clearTimeout(staffCheckInterval); }

        function openWithdrawScanner() { show('modal-withdraw'); startScanner(); }
        function startScanner() { const config = { fps: 10, qrbox: { width: 250, height: 250 }, aspectRatio: 1.0 }; html5QrcodeScanner = new Html5Qrcode("reader"); html5QrcodeScanner.start({ facingMode: "environment" }, config, (decodedText) => { processWithdraw(decodedText); }, (errorMessage) => { }).catch(err => { document.getElementById('reader').innerHTML = "<p class='text-red-500 text-center pt-10'>ไม่สามารถเปิดกล้องได้<br>โปรดใช้การอัปโหลดรูป หรือ กรอกรหัส</p>"; }); }
        async function cleanFromFile(input) { if (input.files.length === 0) return; const imageFile = input.files[0]; const html5QrCode = new Html5Qrcode("reader"); try { const decodedText = await html5QrCode.scanFile(imageFile, true); processWithdraw(decodedText); } catch (err) { Swal.fire("Error", "สแกนไม่พบ QR Code", "error"); } }
        async function manualWithdraw() { processWithdraw(document.getElementById('manual-code').value); }
        async function processWithdraw(code) {
            if(html5QrcodeScanner) { try { await html5QrcodeScanner.stop(); } catch(e){} html5QrcodeScanner = null; }
            const result = await Swal.fire({ title: 'ยืนยันการเบิก?', text: "รหัสรายการ: " + code, icon: 'question', showCancelButton: true, confirmButtonText: 'ยืนยัน', cancelButtonText: 'ยกเลิก' });
            if(!result.isConfirmed) { closeModal('modal-withdraw'); return; }
            
            if(isPreviewMode()) { Swal.fire("สำเร็จ", "เบิกเรียบร้อย (Simulation)", "success").then(()=> closeModal('modal-withdraw')); return; }

            const res = await fetch(CFG.worker + "/api/withdraw", { method: 'POST', body: JSON.stringify({ code, staff: sessionStorage.getItem('staffName') }) });
            const d = await res.json();
            if(d.success) { Swal.fire("สำเร็จ", "เบิกเรียบร้อยแล้ว", "success").then(()=> closeModal('modal-withdraw')); } 
            else { Swal.fire("ผิดพลาด", d.message, "error").then(()=> closeModal('modal-withdraw')); }
        }

        async function manualClaimInput() {
            const { value: code } = await Swal.fire({ title: 'กรอกรหัสรับของ', text: 'ดูเลข 4 หลักจากหน้าจอพนักงาน', input: 'text', inputPlaceholder: '0000', inputAttributes: { maxlength: 4, autocapitalize: 'off', autocorrect: 'off' }, showCancelButton: true });
            if (code) {
                if(isPreviewMode()) { Swal.fire({title:'สำเร็จ!', text:'เข้ากระเป๋าเรียบร้อย (Simulation)', icon:'success'}).then(()=> window.location.reload()); return; }
                try {
                    const res = await fetch(CFG.worker + "/api/claim", { method: 'POST', body: JSON.stringify({ code: code, uid: profile.userId, name: profile.displayName }) });
                    const d = await res.json();
                    if(d.success) Swal.fire({title:'สำเร็จ!', text:'เข้ากระเป๋าเรียบร้อย', icon:'success'}).then(()=> window.location.href = window.location.pathname);
                    else Swal.fire("ผิดพลาด", d.message || "รหัสไม่ถูกต้อง", "error");
                } catch(e) { Swal.fire("Error", "Connection Error", "error"); }
            }
        }

        async function claimDeposit(id) {
            try {
                const res = await fetch(CFG.worker + "/api/claim", { method: 'POST', body: JSON.stringify({ id, uid: profile.userId, name: profile.displayName }) });
                const d = await res.json();
                if(d.success) Swal.fire({ title: 'สำเร็จ!', text: 'รายการถูกเพิ่มในกระเป๋าของคุณแล้ว', icon: 'success', confirmButtonText: 'เปิดกระเป๋า' }).then(() => { window.location.href = window.location.pathname; });
                else Swal.fire("เสียใจด้วย", "รายการนี้ถูกรับไปแล้ว หรือไม่ถูกต้อง", "error").then(() => window.location.href = window.location.pathname);
            } catch(e) { Swal.fire("Error", "Connect error", "error"); }
        }

        function startWalletSync() { loadMyWallet(); if(walletInterval) clearInterval(walletInterval); walletInterval = setInterval(loadMyWallet, 5000); }
        function stopWalletSync() { if(walletInterval) clearInterval(walletInterval); }
        function getProgressColor(amount) { if(amount <= 30) return 'bg-red-500'; if(amount <= 70) return 'bg-yellow-500'; return 'bg-green-500'; }

        async function loadMyWallet() {
            try {
                if(isPreviewMode()) return; // Skip sync in preview
                const res = await fetch(CFG.worker + "/api/my-wallet?uid=" + profile.userId); const data = await res.json();
                const activeDiv = document.getElementById('wallet-active'); const historyDiv = document.getElementById('wallet-history');
                let activeHtml = "", historyHtml = "";
                data.forEach(item => {
                    const createdDate = new Date(item.created_at).toLocaleDateString('th-TH');
                    if (item.status === 'active') {
                        const days = Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
                        const daysText = days > 0 ? `${days} วัน` : "หมดอายุ";
                        const colorClass = days <= 5 ? 'text-red-400' : 'text-green-400';
                        let imgUrl = (CFG.r2 && CFG.r2.length > 5) ? CFG.r2 + "/" + item.image_key : CFG.worker + "/api/image/" + item.image_key;
                        let visual = item.item_type === 'liquor' ? `<div class="flex items-center gap-2 mt-2"><div class="flex-1 bg-gray-700 h-2 rounded-full overflow-hidden"><div class="${getProgressColor(item.amount)} h-full" style="width: ${Math.min(item.amount, 100)}%"></div></div><span class="text-xs font-bold text-[var(--accent)]">${item.amount}%</span></div>` : `<div class="mt-2 text-right"><span class="text-xl font-bold text-[var(--accent)]">x ${item.amount}</span> <span class="text-xs">ขวด</span></div>`;
                        activeHtml += `<div class="bg-white/5 p-4 rounded-xl border border-white/10 relative overflow-hidden"><div class="flex gap-4"><div class="w-20 h-24 bg-black rounded-lg overflow-hidden shrink-0"><img src="${imgUrl}" class="w-full h-full object-cover" onclick="viewImage('${imgUrl}')"></div><div class="flex-1 min-w-0"><div class="flex justify-between items-start"><div><h3 class="font-bold text-lg truncate">${item.item_name}</h3><p class="text-xs text-gray-400">${item.remarks || '-'}</p></div><span class="bg-white/10 text-xs px-2 py-1 rounded font-mono">${item.deposit_code}</span></div>${visual}<div class="mt-2 flex justify-between items-end"><p class="text-xs ${colorClass}">⏳ เหลือ ${daysText}</p></div></div></div><div class="flex gap-2 mt-3 pt-3 border-t border-white/10"><button onclick="showWithdrawQR('${item.deposit_code}', '${item.id}')" class="flex-1 bg-red-500/10 text-red-400 py-2 rounded text-sm border border-red-500/30">เบิกออก</button><button onclick="shareItem('${item.id}','${item.item_name}', '${imgUrl}', '${daysText}')" class="flex-1 bg-blue-500/10 text-blue-400 py-2 rounded text-sm border border-blue-500/30">โอนสิทธิ์</button></div></div>`;
                    } else if (item.status === 'withdrawn') {
                        historyHtml += `<div class="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/10 grayscale"><div class="text-xs text-gray-400"><div>${item.item_name}</div><div class="text-[10px] opacity-70">ฝากเมื่อ: ${createdDate}</div></div><div class="text-xs font-bold text-red-500 border border-red-500 px-2 py-1 rounded">เบิกแล้ว</div></div>`;
                    }
                });
                if (activeDiv.innerHTML !== activeHtml) activeDiv.innerHTML = activeHtml;
                if (historyDiv.innerHTML !== historyHtml) historyDiv.innerHTML = historyHtml;
            } catch(e) { console.log(e); }
        }

        function showWithdrawQR(code, itemId) {
            let timeLeft = 30;
            Swal.fire({
                title: 'Scan Code: ' + code, html: `<div class="flex justify-center my-4 p-4 bg-white rounded-xl"><div id="wd-qr"></div></div><p class="text-gray-400 text-sm">QR หมดอายุใน <span id="qr-countdown" class="text-red-500 font-bold text-xl">30</span> วิ</p><p class="text-xs text-gray-500 mt-2">ยื่นให้พนักงานสแกน</p>`, showConfirmButton: false, showCloseButton: true,
                didOpen: () => {
                    new QRCode(document.getElementById("wd-qr"), { text: code, width: 200, height: 200 });
                    qrTimer = setInterval(() => { timeLeft--; const el = document.getElementById('qr-countdown'); if(el) el.innerText = timeLeft; if(timeLeft <= 0) { clearInterval(qrTimer); clearInterval(qrPoll); Swal.close(); Swal.fire("หมดเวลา", "QR Code หมดอายุ กรุณากดใหม่", "warning"); } }, 1000);
                    let pollAttempt = 0;
                    const pollWithdraw = async () => {
                        pollAttempt++; const res = await fetch(CFG.worker + "/api/my-wallet?uid=" + profile.userId); const data = await res.json();
                        if (!data.find(i => i.id == itemId && i.status === 'active')) { clearInterval(qrTimer); clearInterval(qrPoll); Swal.fire("สำเร็จ", "รายการถูกเบิกเรียบร้อยแล้ว", "success").then(() => loadMyWallet()); }
                        let delay = 2000; if(pollAttempt>10) delay=5000; if(pollAttempt>30) delay=10000; if(timeLeft > 0) qrPoll = setTimeout(pollWithdraw, delay);
                    }; pollWithdraw();
                }, willClose: () => { clearInterval(qrTimer); clearInterval(qrPoll); }
            });
        }

        function viewImage(url) { Swal.fire({ imageUrl: url, imageAlt: 'Bottle Image', showConfirmButton: false, background: '#000', padding: '0' }); }
        async function shareItem(id, name, imgUrl, daysLeft) { const link = `https://liff.line.me/${CFG.liff}?claim_id=${id}`; if(liff.isApiAvailable('shareTargetPicker')) { await liff.shareTargetPicker([{type:"flex", altText: "มีคนโอนสิทธิ์เครื่องดื่มให้คุณ", contents: {type: "bubble", hero: {type: "image", url: imgUrl, size: "full", aspectRatio: "20:13", aspectMode: "cover", action: { type: "uri", uri: link }}, body: {type: "box", layout: "vertical", contents: [{type: "text", text: "🎁 โอนสิทธิ์: " + name, weight: "bold", size: "xl", color: "#EAB308"},{type: "text", text: "⏳ เหลือเวลาอีก " + daysLeft, size: "xs", color: "#aaaaaa", margin: "sm"}]}, footer: {type: "box", layout: "vertical", spacing: "sm", contents: [{type: "button", style: "primary", height: "sm", action: {type: "uri", label: "กดรับสิทธิ์", uri: link}, color: "#EAB308"}]}}}]); } else prompt("Copy Link", link); }

        async function verifyManager() {
            const { value: pass } = await Swal.fire({ title: 'Manager Login', input: 'password', inputPlaceholder: 'Enter password', showCancelButton: true });
            if (pass) {
                // MOCK MANAGER LOGIN
                if(isPreviewMode()) {
                    show('view-manager'); 
                    allStockData = MOCK_STOCK; // Load Mock Data
                    filterStock();
                    document.getElementById('logs-list').innerHTML = "<div class='text-center opacity-50'>Mock Logs Loaded</div>";
                    return;
                }

                const res = await fetch(CFG.worker + "/api/login", { method: 'POST', body: JSON.stringify({ pass }) });
                const d = await res.json();
                if(d.success) { show('view-manager'); loadManagerData(); loadHistoryLogs(); loadManagerStock(); } 
                else Swal.fire("ผิดพลาด", "รหัสผ่านไม่ถูกต้อง", "error");
            }
        }
        
        function switchMgrTab(tab) {
            ['stock','users','logs'].forEach(t => document.getElementById('mgr-tab-'+t).classList.add('hidden'));
            document.getElementById('mgr-tab-'+tab).classList.remove('hidden');
        }
        
        async function loadManagerStock() {
            const res = await fetch(CFG.worker + "/api/manager-stock");
            allStockData = await res.json(); 
            filterStock(); 
        }
        
        function filterStock() {
            const brandTxt = document.getElementById('filter-brand').value.toLowerCase();
            const expiryVal = document.getElementById('filter-expiry').value;
            const pctVal = document.getElementById('filter-pct').value;
            const now = new Date();

            const filtered = allStockData.filter(item => {
                if (brandTxt && !item.item_name.toLowerCase().includes(brandTxt)) return false;
                const expDate = new Date(item.expiry_date);
                const diffDays = Math.ceil((expDate - now) / (1000 * 60 * 60 * 24));
                if (expiryVal === '7' && diffDays > 7) return false;
                if (expiryVal === '14' && diffDays > 14) return false;
                if (pctVal !== 'all' && item.item_type === 'liquor') {
                    if (pctVal === 'low' && item.amount > 30) return false;
                    if (pctVal === 'mid' && (item.amount <= 30 || item.amount > 70)) return false;
                    if (pctVal === 'high' && item.amount <= 70) return false;
                }
                return true;
            });

            const list = document.getElementById('stock-list'); list.innerHTML = "";
            filtered.forEach(item => {
                let visual = "";
                if(item.item_type === 'liquor') {
                    const barColor = getProgressColor(item.amount);
                    visual = `<div class="w-24 h-2 bg-gray-700 rounded-full overflow-hidden mt-1"><div class="${barColor} h-full" style="width:${item.amount}%"></div></div>`;
                } else visual = `<span class="text-xs font-bold text-white">x${item.amount}</span>`;
                
                const days = Math.ceil((new Date(item.expiry_date) - now) / (1000 * 60 * 60 * 24));
                const daysHtml = days <= 7 ? `<span class='text-red-500 font-bold'>⚠️ ${days} วัน</span>` : `${days} วัน`;
                let imgUrl = (CFG.r2 && CFG.r2.length > 5) ? CFG.r2 + "/" + item.image_key : CFG.worker + "/api/image/" + item.image_key;
                if(isPreviewMode()) imgUrl = "https://via.placeholder.com/50"; // Mock Image

                const owner = item.owner_name ? item.owner_name : (item.owner_uid ? item.owner_uid.substring(0,8)+"..." : "Unknown");

                list.innerHTML += `
                <div class="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/10">
                    <img src="${imgUrl}" class="w-12 h-12 rounded object-cover bg-black" onclick="viewImage('${imgUrl}')">
                    <div class="flex-1">
                        <div class="font-bold">${item.item_name}</div>
                        <div class="text-xs text-gray-400">Code: ${item.deposit_code} | 👤 ${owner}</div>
                        <div class="text-xs text-yellow-500 mt-1">📝 Note: ${item.remarks || '-'}</div>
                    </div>
                    <div class="text-right">
                        ${visual}
                        <div class="text-xs mt-1 text-gray-400">Exp: ${daysHtml}</div>
                    </div>
                </div>`;
            });
        }

        async function loadManagerData() {
            const res = await fetch(CFG.worker + "/api/manager-list"); const data = await res.json();
            const pList = document.getElementById('pending-list'); pList.innerHTML = ""; data.pending.forEach(s => { pList.innerHTML += `<div class="flex justify-between py-2 border-b border-white/10"><span>${s.name}</span><button onclick="staffAction('approve','${s.user_id}','${s.name}')" class="text-green-400 font-bold">✓</button></div>`; });
            const aList = document.getElementById('active-list'); aList.innerHTML = ""; data.active.forEach(s => { aList.innerHTML += `<div class="flex justify-between py-2 border-b border-white/10"><span>${s.name}</span><button onclick="staffAction('remove','${s.user_id}','${s.name}')" class="text-red-400 font-bold">✕</button></div>`; });
        }
        async function loadHistoryLogs() {
            const res = await fetch(CFG.worker + "/api/logs"); const data = await res.json();
            const list = document.getElementById('logs-list'); list.innerHTML = "";
            data.logs.forEach(l => {
                const color = l.action === 'deposit' ? 'text-blue-400' : (l.action === 'withdraw' ? 'text-red-400' : 'text-gray-400');
                const date = new Date(l.created_at).toLocaleString('th-TH');
                let imgHTML = l.image_key ? `<div class="mt-1"><img src="${(CFG.r2 && CFG.r2.length > 5) ? CFG.r2 + "/" + l.image_key : CFG.worker + "/api/image/" + l.image_key}" class="h-12 rounded border border-white/20" onclick="viewImage(this.src)" onerror="this.parentElement.style.display='none'"></div>` : "";
                list.innerHTML += `<div class="py-3 border-b border-white/5"><div class="flex justify-between"><strong class="${color} uppercase">${l.action}</strong><span class="opacity-50">${date}</span></div><div class="text-gray-300 mt-1">${l.details}</div>${imgHTML}<div class="text-xs opacity-50 mt-1">by ${l.staff_name}</div></div>`;
            });
        }
        async function staffAction(action, uid, name) { const c = await Swal.fire({ title: 'ยืนยัน?', icon: 'warning', showCancelButton: true }); if(c.isConfirmed) { await fetch(CFG.worker + "/api/staff-action", { method: 'POST', body: JSON.stringify({ action, uid, name }) }); loadManagerData(); } }
        async function registerStaff() { const name = document.getElementById('reg-name').value; if(!name) return Swal.fire("แจ้งเตือน", "ใส่ชื่อ", "warning"); await fetch(CFG.worker + "/api/register", { method: 'POST', body: JSON.stringify({ uid: profile.userId, name: name }) }); Swal.fire("สำเร็จ", "ส่งคำขอแล้ว!", "success").then(() => location.reload()); }

        main();
    </script>
</body>
</html>"""

# ==============================================================================
# 2. WORKER CODE (V37 - SEQUENTIAL ID 0001 + LOGGING)
# ==============================================================================
WORKER_RAW = r"""
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const corsHeaders = { 
      "Access-Control-Allow-Origin": "*", 
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS", 
      "Access-Control-Allow-Headers": "Content-Type" 
    };
    
    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

    async function addLog(action, staff, details, imgKey = null) {
        try { 
            await env.DB.prepare("INSERT INTO logs (action, staff_name, details, image_key) VALUES (?, ?, ?, ?)").bind(action, staff, details, imgKey).run(); 
        } catch(e){}
    }

    try {
        if (path.startsWith("/api/image/")) {
            const key = path.split('/').pop(); 
            const object = await env.BUCKET.get(key);
            if (!object) return new Response('Not Found', { status: 404 });
            const headers = new Headers(); 
            object.writeHttpMetadata(headers); 
            headers.set('etag', object.httpEtag);
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
            if (body.pass === "__MGR_PASS__") return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
            return new Response(JSON.stringify({ success: false }), { headers: corsHeaders });
        }
        
        if (path === "/api/register" && request.method === "POST") {
            const body = await request.json(); 
            await env.DB.prepare("INSERT OR IGNORE INTO staff_access (user_id, name, status) VALUES (?, ?, 'pending')").bind(body.uid, body.name).run();
            return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
        }
        
        if (path === "/api/deposit" && request.method === "POST") {
            const body = await request.json();
            const imgString = body.image.split(',')[1]; 
            const imgBuffer = Uint8Array.from(atob(imgString), c => c.charCodeAt(0)); 
            const filename = `dep_${Date.now()}.jpg`;
            await env.BUCKET.put(filename, imgBuffer);
            
            // --- SEQUENTIAL CODE LOGIC (0001, 0002, ...) ---
            const lastItem = await env.DB.prepare("SELECT deposit_code FROM deposits ORDER BY id DESC LIMIT 1").first();
            let nextNum = 1;
            if (lastItem && lastItem.deposit_code) {
                const parsed = parseInt(lastItem.deposit_code, 10);
                if (!isNaN(parsed)) nextNum = parsed + 1;
            }
            const code = nextNum.toString().padStart(4, '0');
            // -----------------------------------------------

            const res = await env.DB.prepare(`INSERT INTO deposits (deposit_code, staff_name, item_name, item_type, amount, remarks, image_key, status, expiry_date) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_claim', date('now', '+30 days')) RETURNING id`).bind(code, body.staff_name, body.item_name, body.item_type, body.amount, body.remarks, filename).first();
            await addLog('deposit', body.staff_name, `Deposit: ${body.item_name} (${code})`, filename);
            return new Response(JSON.stringify({ deposit_id: res.id, code: code }), { headers: corsHeaders });
        }
        
        if (path === "/api/check-deposit") {
            const id = url.searchParams.get('id');
            const res = await env.DB.prepare("SELECT owner_uid FROM deposits WHERE id = ?").bind(id).first();
            return new Response(JSON.stringify({ claimed: !!(res && res.owner_uid) }), { headers: corsHeaders });
        }
        
        if (path === "/api/claim" && request.method === "POST") {
            const body = await request.json();
            const ownerName = body.name || null;
            let res;
            if (body.code) {
                res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE deposit_code = ? AND status = 'pending_claim'").bind(body.uid, ownerName, body.code).run();
            } else {
                res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE id = ? AND status != 'withdrawn'").bind(body.uid, ownerName, body.id).run();
            }
            if(res.meta.changes > 0) return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
            return new Response(JSON.stringify({ success: false, message: "Invalid code or item already claimed" }), { headers: corsHeaders });
        }
        
        if (path === "/api/my-wallet") {
            const uid = url.searchParams.get('uid');
            const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_uid = ? ORDER BY created_at DESC").bind(uid).all();
            return new Response(JSON.stringify(res.results), { headers: corsHeaders });
        }
        
        if (path === "/api/withdraw" && request.method === "POST") {
            const body = await request.json();
            const item = await env.DB.prepare("SELECT * FROM deposits WHERE deposit_code = ? AND status = 'active'").bind(body.code).first();
            if (!item) return new Response(JSON.stringify({ success: false, message: "Code not found" }), { headers: corsHeaders });
            if (item.image_key) { await env.BUCKET.delete(item.image_key); }
            await env.DB.prepare("UPDATE deposits SET status = 'withdrawn' WHERE id = ?").bind(item.id).run();
            await addLog('withdraw', body.staff, `Withdrew: ${item.item_name} (Code: ${body.code})`, item.image_key);
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
            if (body.action === 'approve') {
                await env.DB.prepare("UPDATE staff_access SET status = 'active' WHERE user_id = ?").bind(body.uid).run();
                await addLog('approve', 'Manager', `Approved Staff: ${body.name}`);
            } else if (body.action === 'remove') {
                await env.DB.prepare("DELETE FROM staff_access WHERE user_id = ?").bind(body.uid).run();
                await addLog('remove', 'Manager', `Removed Staff: ${body.name}`);
            }
            return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
        }
    } catch(e) { return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders }); }
    return new Response("API Ready v37", { headers: corsHeaders });
  },

  async scheduled(event, env, ctx) {
    const query = `SELECT * FROM deposits WHERE status = 'active' AND (expiry_date = date('now', '+7 days') OR expiry_date = date('now', '+3 days') OR expiry_date = date('now', '+1 days'))`;
    const results = await env.DB.prepare(query).all();
    const items = results.results;
    if (items.length === 0) return;
    const userItems = {};
    items.forEach(item => { if (!item.owner_uid) return; if (!userItems[item.owner_uid]) userItems[item.owner_uid] = []; userItems[item.owner_uid].push(item); });
    for (const [uid, list] of Object.entries(userItems)) { await sendLinePush(uid, list, env.LINE_TOKEN); }
  }
};

async function sendLinePush(uid, items, token) {
    if (!token) return;
    const bubbles = items.map(item => {
        const daysLeft = Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
        const color = daysLeft <= 1 ? "#ef4444" : (daysLeft <= 3 ? "#f97316" : "#eab308");
        return {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    { "type": "text", "text": "⚠️ แจ้งเตือนวันหมดอายุ", "weight": "bold", "color": color, "size": "sm" },
                    { "type": "text", "text": item.item_name, "weight": "bold", "size": "xl", "margin": "md", "wrap": true },
                    { "type": "text", "text": `จะหมดอายุในอีก ${daysLeft} วัน`, "size": "sm", "color": "#aaaaaa", "margin": "sm" }
                ]
            },
            "footer": {
                "type": "box", "layout": "vertical",
                "contents": [
                    { "type": "button", "style": "primary", "action": { "type": "uri", "label": "เปิดกระเป๋า", "uri": "https://liff.line.me/__LIFF__" }, "color": color }
                ]
            }
        };
    });

    await fetch("https://api.line.me/v2/bot/message/push", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
        body: JSON.stringify({
            "to": uid,
            "messages": [{ "type": "flex", "altText": "แจ้งเตือนวันหมดอายุ", "contents": { "type": "carousel", "contents": bubbles } }]
        })
    });
}
"""

# ==============================================================================
# 3. PYTHON UI CONTROLLER
# ==============================================================================
class AppGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nightlife System Builder V37 (The Final Merge)")
        self.geometry("1100x850")
        
        self.vars = { 
            'bg_color': '#0f172a', 'grad_start': '#1e3a8a', 'grad_end': '#172554', 
            'text_main': '#ffffff', 'text_sub': '#94a3b8', 'accent': '#EAB308',
            'radius': '16px', 'shadow': '0 4px 15px rgba(0,0,0,0.3)', 'border': '1px solid rgba(255,255,255,0.1)'
        }
        
        # 8 PRESET LAYOUTS (Standard V23 as Default)
        self.LAYOUTS = {
            "Standard (Original)": ".menu-layout { display: flex; flex-direction: column; gap: 15px; } .btn-menu { width: 100%; padding: 30px 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; aspect-ratio: 2.5/1; } .icon { font-size: 40px; margin-bottom: 10px; }",
            
            "Grid (2 Columns)": ".menu-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; } .btn-menu { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; aspect-ratio: 1/1; } .icon { margin-bottom: 8px; font-size: 35px; } .text-wrap { text-align: center; }",
            
            "Wide List (Row)": ".menu-layout { display: flex; flex-direction: column; gap: 12px; } .btn-menu { display: flex !important; flex-direction: row !important; align-items: center; justify-content: flex-start !important; padding: 20px 25px !important; text-align: left !important; } .icon { margin-bottom: 0; margin-right: 25px; font-size: 32px; } .text-wrap { text-align: left; } .label { font-size: 18px; } .sub-label { font-size: 14px; }",
            
            "Large Tiles (1 Col)": ".menu-layout { display: flex; flex-direction: column; gap: 20px; } .btn-menu { padding: 50px 20px !important; } .icon { font-size: 60px; margin-bottom: 15px; } .label { font-size: 28px; }",
            
            "Circle Icons (3 Col)": ".menu-layout { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; } .btn-menu { aspect-ratio: 1/1 !important; border-radius: 50% !important; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 10px; } .icon { font-size: 30px; margin-bottom: 5px; } .label { font-size: 10px; } .sub-label { display: none; }",
            
            "Dense Grid (3 Col)": ".menu-layout { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; } .btn-menu { padding: 15px 5px !important; } .icon { font-size: 25px; } .label { font-size: 12px; } .sub-label { font-size: 9px; }",
            
            "Hero Header": ".menu-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; } .menu-item-1 { grid-column: 1 / -1; aspect-ratio: 2/1; background: linear-gradient(45deg, var(--accent), #fff) !important; color: #000 !important; } .menu-item-1 .label { color: #000 !important; font-size: 24px; } .menu-item-1 .sub-label { color: #333 !important; } .menu-item-1 .icon { font-size: 50px; }",
            
            "Alternating List": ".menu-layout { display: flex; flex-direction: column; gap: 15px; } .menu-item-2 { flex-direction: row-reverse !important; text-align: right !important; } .btn-menu { display: flex !important; flex-direction: row !important; align-items: center; justify-content: space-between !important; padding: 25px; } .icon { font-size: 30px; margin: 0; }",
            
            "Minimal Text": ".menu-layout { display: flex; flex-direction: column; gap: 0px; background: rgba(255,255,255,0.05); border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); } .btn-menu { border-radius: 0 !important; background: transparent !important; border: none !important; border-bottom: 1px solid rgba(255,255,255,0.1) !important; box-shadow: none !important; flex-direction: row !important; justify-content: flex-start !important; padding: 20px !important; } .btn-menu:last-child { border-bottom: none !important; } .icon { font-size: 24px; margin-right: 20px; margin-bottom: 0; } .text-wrap { text-align: left; }"
        }

        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=2); self.grid_rowconfigure(0, weight=1)
        self.setup_ui(); self.load_config(); self.update_preview_ui()

    def setup_ui(self):
        left = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent"); left.grid(row=0, column=0, sticky="nsew"); left.grid_rowconfigure(1, weight=1); left.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(left, text="🛠️ App Config", font=("Prompt", 20, "bold")).grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.scroll = ctk.CTkScrollableFrame(left, fg_color="transparent"); self.scroll.grid(row=1, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.scroll, text="1. Theme Colors", font=("Prompt", 16, "bold"), text_color="#EAB308").pack(anchor="w", padx=20, pady=(10,5))
        c_grid = ctk.CTkFrame(self.scroll, fg_color="transparent"); c_grid.pack(fill="x", padx=20)
        self.create_color_btn(c_grid, "Background", 'bg_color', 0); self.create_color_btn(c_grid, "Grad Start", 'grad_start', 1)
        self.create_color_btn(c_grid, "Grad End", 'grad_end', 2); self.create_color_btn(c_grid, "Accent", 'accent', 3)
        ctk.CTkButton(self.scroll, text="🎲 Random Color", command=self.randomize_colors, height=40, fg_color="#4F46E5").pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.scroll, text="2. Layout Style", font=("Prompt", 16, "bold"), text_color="#EAB308").pack(anchor="w", padx=20, pady=(20,5))
        self.combo_layout = ctk.CTkComboBox(self.scroll, values=list(self.LAYOUTS.keys()), command=self.update_preview_ui)
        self.combo_layout.set("Standard (Original)")
        self.combo_layout.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.scroll, text="3. Settings", font=("Prompt", 16, "bold"), text_color="#EAB308").pack(anchor="w", padx=20, pady=(20,5))
        self.entries = {}
        for k, h in [("Shop Name", "ชื่อร้าน"), ("LIFF ID", "165xxxx-xxxx"), ("Worker URL", "Cloudflare Worker"), ("Manager Password", "รหัสผ่าน"), ("R2 Public URL", "Optional"), ("Channel Access Token", "Line Messaging API"), ("Hold Table Time", "เวลาหลุดจอง (เช่น 20:30)")]:
            ctk.CTkLabel(self.scroll, text=k, anchor="w", text_color="#ccc").pack(fill="x", padx=20)
            e = ctk.CTkEntry(self.scroll, placeholder_text=h); e.pack(fill="x", padx=20, pady=(0, 10)); self.entries[k] = e
            if k == "Shop Name": e.bind("<KeyRelease>", self.update_preview_text)
        
        ctk.CTkButton(self.scroll, text="📋 Paste Config", command=self.ask_paste, fg_color="#333", height=30).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(left, text="🚀 GENERATE APP", command=self.build, height=60, fg_color="#10B981", font=("Prompt", 18, "bold")).grid(row=2, column=0, sticky="ew", padx=20, pady=20)

        self.preview = ctk.CTkFrame(self, fg_color="#000", corner_radius=0); self.preview.grid(row=0, column=1, sticky="nsew", rowspan=3)
        ctk.CTkLabel(self.preview, text="Preview V37", text_color="#555").pack(pady=20)
        
        self.btn_real_preview = ctk.CTkButton(self.preview, text="👁️ OPEN REAL PREVIEW", command=self.open_live_preview, height=50, fg_color="#EAB308", text_color="black", font=("Arial", 16, "bold"))
        self.btn_real_preview.pack(padx=20, pady=10, fill="x")

        self.phone = ctk.CTkFrame(self.preview, width=375, height=667, corner_radius=30, fg_color="#fff", border_width=8, border_color="#333"); self.phone.place(relx=0.5, rely=0.55, anchor="center"); self.phone.pack_propagate(False)
        self.p_header = ctk.CTkLabel(self.phone, text="SHOP NAME", font=("Arial", 20, "bold")); self.p_header.pack(pady=(40, 5))
        self.p_card = ctk.CTkFrame(self.phone, height=120, corner_radius=15); self.p_card.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(self.p_card, text="🥃 My Wallet", font=("Arial", 16, "bold"), text_color="white").place(relx=0.1, rely=0.2)
        self.p_bar_fill = ctk.CTkFrame(self.p_card, height=8, width=100, fg_color="yellow"); self.p_bar_fill.place(relx=0.1, rely=0.6)

    def create_color_btn(self, parent, label, key, row):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        btn = ctk.CTkButton(parent, text="", width=60, command=lambda: self.pick_color(key)); btn.grid(row=row, column=1, sticky="e", padx=5); setattr(self, f"btn_{key}", btn)
    def pick_color(self, key):
        c = colorchooser.askcolor(color=self.vars[key])[1]; 
        if c: self.vars[key] = c; self.update_preview_ui()
    def randomize_colors(self):
        h = random.random(); self.vars['bg_color'] = self.hsv(h, 0.6, 0.15); self.vars['grad_start'] = self.hsv(h + 0.05, 0.8, 0.6); self.vars['grad_end'] = self.hsv(h - 0.05, 0.6, 0.3); self.vars['accent'] = self.hsv(h + 0.5, 0.9, 1.0); self.update_preview_ui()
    def hsv(self, h, s, v): r,g,b = colorsys.hsv_to_rgb(h%1, s, v); return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
    def ask_paste(self):
        t = ctk.CTkInputDialog(text="Paste:", title="Fill").get_input()
        if t: 
            p = {'LIFF ID':r'(\d{10}-\w{8})', 'Worker URL':r'(https?://[\w\-\.]+\.workers\.dev)'}
            for k,r in p.items():
                m = re.search(r, t); 
                if m: self.entries[k].delete(0, "end"); self.entries[k].insert(0, m.group(1))
    
    def update_preview_ui(self, event=None):
        for k, v in self.vars.items(): 
            try: getattr(self, f"btn_{k}").configure(fg_color=v) 
            except: pass
        self.phone.configure(fg_color=self.vars['bg_color']); self.p_header.configure(text_color=self.vars['accent']); self.p_card.configure(fg_color=self.vars['grad_start']); self.p_bar_fill.configure(fg_color=self.vars['accent'])
        layout = self.combo_layout.get()
        if "List" in layout: self.p_card.configure(height=80, width=300)
        elif "Tile" in layout or "Hero" in layout: self.p_card.configure(height=180, width=300)
        elif "Dense" in layout or "Circle" in layout: self.p_card.configure(height=100, width=100)
        elif "Grid (2 Columns)" in layout: self.p_card.configure(height=120, width=140)
        else: self.p_card.configure(height=100, width=300)

    def update_preview_text(self, event): self.p_header.configure(text=self.entries["Shop Name"].get())
    
    def open_live_preview(self):
        layout_key = self.combo_layout.get(); layout_css = self.LAYOUTS.get(layout_key, "")
        shop = self.entries["Shop Name"].get() or "PREVIEW SHOP"
        path = os.path.abspath("preview_temp.html")
        radius = self.vars.get('radius', '16px')
        shadow = self.vars.get('shadow', '0 4px 15px rgba(0,0,0,0.3)')
        border = self.vars.get('border', '1px solid rgba(255,255,255,0.1)')
        
        html = HTML_RAW.replace("__SHOP__", shop).replace("__BG_COLOR__", self.vars['bg_color']).replace("__GRAD_START__", self.vars['grad_start']).replace("__GRAD_END__", self.vars['grad_end']).replace("__TEXT_MAIN__", self.vars['text_main']).replace("__TEXT_SUB__", self.vars['text_sub']).replace("__ACCENT__", self.vars['accent']).replace("__RADIUS__", radius).replace("__SHADOW__", shadow).replace("__BORDER__", border).replace("__LIFF__", "").replace("__WORKER__", "").replace("__R2_URL__", "").replace("__HOLD_TIME__", "").replace("__LAYOUT_CSS__", layout_css)
        with open(path, "w", encoding="utf-8") as f: f.write(html)
        webbrowser.open(f"file://{path}")

    def build(self):
        shop = self.entries["Shop Name"].get().strip(); mgr = self.entries["Manager Password"].get().strip(); w_url = self.entries["Worker URL"].get().strip()
        liff_id = self.entries["LIFF ID"].get().strip(); line_token = self.entries["Channel Access Token"].get().strip(); hold_time = self.entries["Hold Table Time"].get().strip()
        
        if not shop or not mgr or not w_url: return messagebox.showerror("Error", "Missing Fields")
        if not w_url.startswith("http"): w_url = "https://" + w_url
        if w_url.endswith("/"): w_url = w_url[:-1]

        layout_key = self.combo_layout.get(); layout_css = self.LAYOUTS.get(layout_key, "")
        radius = self.vars.get('radius', '16px')
        shadow = self.vars.get('shadow', '0 4px 15px rgba(0,0,0,0.3)')
        border = self.vars.get('border', '1px solid rgba(255,255,255,0.1)')

        html = HTML_RAW.replace("__SHOP__", shop).replace("__BG_COLOR__", self.vars['bg_color']).replace("__GRAD_START__", self.vars['grad_start']).replace("__GRAD_END__", self.vars['grad_end']).replace("__TEXT_MAIN__", self.vars['text_main']).replace("__TEXT_SUB__", self.vars['text_sub']).replace("__ACCENT__", self.vars['accent']).replace("__RADIUS__", radius).replace("__SHADOW__", shadow).replace("__BORDER__", border).replace("__LIFF__", liff_id).replace("__WORKER__", w_url).replace("__R2_URL__", self.entries["R2 Public URL"].get()).replace("__HOLD_TIME__", hold_time).replace("__LAYOUT_CSS__", layout_css)
        worker_code = WORKER_RAW.replace("__MGR_PASS__", mgr).replace("__LIFF__", liff_id)

        folder = f"Output_{shop.replace(' ', '_')}"
        if not os.path.exists(folder): os.makedirs(folder)
        with open(f"{folder}/index.html", "w", encoding="utf-8") as f: f.write(html)
        with open(f"{folder}/worker.js", "w", encoding="utf-8") as f: f.write(worker_code)
        
        wrangler_content = f"""name = "nightlife-app"\nmain = "worker.js"\ncompatibility_date = "2023-10-30"\n\n[vars]\nLINE_TOKEN = "{line_token}"\n\n[[d1_databases]]\nbinding = "DB"\ndatabase_name = "nightlife-db"\ndatabase_id = "YOUR_D1_ID_HERE"\n\n[[r2_buckets]]\nbinding = "BUCKET"\nbucket_name = "nightlife-bucket"\n\n[triggers]\ncrons = ["0 7 * * *"]"""
        with open(f"{folder}/wrangler.toml", "w", encoding="utf-8") as f: f.write(wrangler_content)

        d_save = {k: v.get() for k,v in self.entries.items()}; d_save['colors'] = self.vars; d_save['layout'] = layout_key
        with open("config.json", "w") as f: json.dump(d_save, f)
        messagebox.showinfo("Success", "Generated!"); webbrowser.open(folder)

    def load_config(self):
        if os.path.exists("config.json"):
            try: 
                d = json.load(open("config.json")); 
                for k,v in d.items(): 
                    if k in self.entries: self.entries[k].insert(0,v)
                if 'colors' in d: self.vars.update(d['colors'])
                if 'layout' in d: self.combo_layout.set(d['layout'])
                if 'radius' not in self.vars: self.vars['radius'] = '16px'
                if 'shadow' not in self.vars: self.vars['shadow'] = '0 4px 15px rgba(0,0,0,0.3)'
                if 'border' not in self.vars: self.vars['border'] = '1px solid rgba(255,255,255,0.1)'
                self.update_preview_ui()
            except: pass

if __name__ == "__main__": app = AppGenerator(); app.mainloop()