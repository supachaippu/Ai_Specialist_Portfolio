import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox
import os
import json
import webbrowser
import random
import colorsys

# Setup Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# 1. HTML TEMPLATE (FULL LOGIC + GRADIENT UI)
# ==========================================
HTML_RAW = r"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__SHOP__</title>
    <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            /* Dynamic Colors from Python */
            --bg-color: __BG_COLOR__;
            --card-grad-start: __GRAD_START__;
            --card-grad-end: __GRAD_END__;
            --text-main: __TEXT_MAIN__;
            --text-sub: __TEXT_SUB__;
            --accent: __ACCENT__;
        }

        body {
            font-family: 'Prompt', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            -webkit-tap-highlight-color: transparent;
        }

        /* --- UI COMPONENTS --- */
        .btn-menu {
            background: linear-gradient(135deg, var(--card-grad-start), var(--card-grad-end));
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 25px 20px;
            margin-bottom: 15px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            display: block;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }
        .btn-menu:active { transform: scale(0.98); }
        
        .icon { font-size: 35px; margin-bottom: 8px; display: block; }
        .label { font-size: 18px; font-weight: bold; display: block; color: var(--text-main); }
        .sub-label { font-size: 13px; color: var(--text-sub); display: block; margin-top: 4px; }

        /* Input Style */
        .glass-input {
            background: rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 12px;
            width: 100%;
            color: var(--text-main);
            outline: none;
            margin-bottom: 10px;
        }
        .glass-input:focus { border-color: var(--accent); }

        /* Action Button */
        .btn-action {
            background: var(--accent);
            color: #000;
            font-weight: bold;
            padding: 12px;
            border-radius: 12px;
            width: 100%;
            text-align: center;
            box-shadow: 0 0 15px var(--accent);
        }

        /* Utility */
        .hidden { display: none !important; }
        .flex-center { display: flex; justify-content: center; align-items: center; }
        #reader video { border-radius: 16px; object-fit: cover; }
    </style>
</head>
<body class="p-6 max-w-md mx-auto w-full relative">

    <div id="loading" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 backdrop-blur-sm">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-t-transparent" style="border-color: var(--accent);"></div>
        <p class="mt-4 text-sm" style="color: var(--text-sub);">Loading...</p>
    </div>

    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-2xl font-bold" style="color: var(--accent);">__SHOP__</h1>
            <p class="text-xs" style="color: var(--text-sub);">Nightlife System</p>
        </div>
        <div class="flex gap-2">
             <button id="btn-staff-switch" onclick="switchMode()" class="hidden text-xs bg-white/10 px-3 py-1 rounded-full border border-white/5 text-gray-300">🔁 Staff</button>
             <button onclick="show('modal-login')" class="opacity-50 hover:opacity-100">⚙️</button>
        </div>
    </div>

    <div id="view-customer" class="hidden">
        <div class="flex items-center gap-4 mb-6 bg-white/5 p-4 rounded-2xl border border-white/10">
            <img id="user-img" class="w-12 h-12 rounded-full border-2" style="border-color: var(--accent);" src="">
            <div>
                <p class="text-xs" style="color: var(--text-sub);">Welcome,</p>
                <h2 id="user-name" class="font-bold text-lg truncate">Guest</h2>
            </div>
        </div>

        <div onclick="show('view-booking')" class="btn-menu">
            <span class="icon">📅</span>
            <span class="label">จองโต๊ะ</span>
            <span class="sub-label">สำรองที่นั่งล่วงหน้า</span>
        </div>

        <div onclick="show('view-wallet')" class="btn-menu">
            <span class="icon">🥃</span>
            <span class="label">ระบบฝากเหล้า</span>
            <span class="sub-label">เช็ครายการ / เบิก / โอน</span>
        </div>
    </div>

    <div id="view-staff" class="hidden space-y-4">
        <div class="grid grid-cols-2 gap-4">
            <div onclick="openDepositFlow()" class="btn-menu mb-0">
                <span class="icon">📥</span><span class="label">รับฝาก</span>
            </div>
            <div onclick="openWithdrawScanner()" class="btn-menu mb-0" style="background: linear-gradient(135deg, #3f1010, #1a0505); border-color: #ef4444;">
                <span class="icon">📤</span><span class="label text-red-400">เบิกออก</span>
            </div>
        </div>
        <div id="deposit-status-box" class="hidden p-4 rounded-xl border border-dashed text-center animate-pulse" style="border-color: var(--accent);">
            <p class="font-bold" style="color: var(--accent);">⏳ Waiting for customer...</p>
            <div class="bg-white p-2 rounded-xl w-fit mx-auto mt-3"><div id="deposit-qr-target"></div></div>
        </div>
    </div>

    <div id="view-wallet" class="hidden">
        <button onclick="show('view-customer')" class="text-sm mb-4 flex items-center gap-1" style="color: var(--text-sub);">← Back</button>
        <h2 class="text-xl font-bold mb-4">🍾 My Collection</h2>
        <div id="my-bottle-list" class="space-y-4 pb-20"></div>
    </div>

    <div id="view-booking" class="hidden">
        <div class="flex justify-between mb-4"><h2 class="text-xl font-bold">📝 จองโต๊ะ</h2><button onclick="show('view-customer')">✕</button></div>
        <div class="bg-white/5 p-6 rounded-2xl border border-white/10">
            <input type="text" id="bk-name" placeholder="ชื่อผู้จอง" class="glass-input">
            <input type="tel" id="bk-phone" placeholder="เบอร์โทร" class="glass-input">
            <div class="flex gap-2 mb-2">
                <input type="date" id="bk-date" class="glass-input">
                <input type="time" id="bk-time" value="20:00" class="glass-input">
            </div>
            <select id="bk-pax" class="glass-input bg-black"><option>1-4 คน</option><option>5-8 คน</option><option>9+ คน</option></select>
            <button onclick="submitBooking()" class="btn-action mt-2">ยืนยันการจอง</button>
        </div>
    </div>

    <div id="modal-deposit" class="fixed inset-0 z-[70] hidden flex-col bg-black p-4">
        <div class="flex justify-between mb-4"><h2 class="text-xl font-bold text-white">📸 ฝากของ</h2><button onclick="closeModal('modal-deposit')" class="text-gray-400">✕</button></div>
        <div class="bg-gray-900 rounded-xl overflow-hidden h-64 mb-4 relative">
            <video id="camera-feed" autoplay playsinline class="w-full h-full object-cover"></video>
            <canvas id="photo-canvas" class="hidden"></canvas>
        </div>
        <button onclick="takePhoto()" id="btn-snap" class="btn-action mb-4">ถ่ายรูป</button>
        <div id="deposit-form" class="hidden space-y-3">
            <div class="flex gap-2"><button onclick="setDepType('liquor')" class="flex-1 bg-gray-800 text-white py-3 rounded-xl border border-white/10">🥃 เหล้า</button><button onclick="setDepType('beer')" class="flex-1 bg-gray-800 text-white py-3 rounded-xl border border-white/10">🍺 เบียร์</button></div>
            <input id="dep-brand" placeholder="ยี่ห้อ (Brand)" class="glass-input">
            <input id="dep-amount" type="number" placeholder="จำนวน / %" class="glass-input">
            <button onclick="submitDeposit()" class="btn-action">บันทึกรายการ</button>
        </div>
    </div>

    <div id="modal-withdraw" class="fixed inset-0 z-[70] hidden flex-col bg-black p-4">
        <div class="flex justify-between mb-4"><h2 class="text-xl font-bold text-white">📤 สแกนเพื่อเบิก</h2><button onclick="closeModal('modal-withdraw')" class="text-gray-400">✕</button></div>
        <div id="reader" class="rounded-xl overflow-hidden mb-4 border border-white/20"></div>
        <p class="text-center text-gray-500 mb-2">- หรือ -</p>
        <input id="manual-code" placeholder="กรอกรหัส 4 หลัก" class="glass-input text-center text-xl tracking-widest">
        <button onclick="manualWithdraw()" class="btn-action mt-2">ยืนยันรหัส</button>
    </div>

    <div id="view-manager" class="hidden">
        <div class="flex justify-between items-center mb-4">
             <h2 class="text-xl font-bold text-white">👑 Manager Dashboard</h2>
             <button onclick="location.reload()" class="text-xs bg-red-900 text-red-200 px-3 py-1 rounded">Logout</button>
        </div>
        
        <div class="flex gap-2 mb-4 bg-white/5 p-1 rounded-xl">
            <button onclick="switchMgrTab('users')" class="flex-1 py-2 rounded-lg text-sm font-bold bg-white/10">Staff</button>
            <button onclick="switchMgrTab('logs')" class="flex-1 py-2 rounded-lg text-sm text-gray-400 hover:text-white">Logs</button>
        </div>

        <div id="mgr-tab-users" class="space-y-4">
            <div class="bg-white/5 p-4 rounded-xl border-l-4 border-yellow-500"><h3 class="text-yellow-500 font-bold mb-2">Pending</h3><div id="pending-list" class="space-y-2 text-sm"></div></div>
            <div class="bg-white/5 p-4 rounded-xl border-l-4 border-green-500"><h3 class="text-green-500 font-bold mb-2">Active</h3><div id="active-list" class="space-y-2 text-sm"></div></div>
        </div>

        <div id="mgr-tab-logs" class="hidden bg-white/5 p-2 rounded-xl h-96 overflow-y-auto">
            <div id="logs-list" class="space-y-2 text-xs">Loading...</div>
        </div>
    </div>

    <div id="modal-login" class="fixed inset-0 z-[60] hidden flex items-center justify-center bg-black/90 p-6">
        <div class="bg-[#1e293b] w-full max-w-xs p-6 rounded-2xl border border-white/10 relative">
            <button onclick="show('view-customer')" class="absolute top-2 right-4 text-gray-400">✕</button>
            <h3 class="text-xl font-bold text-center mb-4 text-white">Admin Login</h3>
            <input type="password" id="mgr-pass" class="glass-input text-center text-2xl tracking-widest" placeholder="••••">
            <button onclick="verifyManager()" class="btn-action mt-2">Login</button>
            <div class="text-center mt-4 border-t border-white/10 pt-4">
                <button onclick="show('view-staff-register')" class="text-xs text-gray-400 underline">พนักงานใหม่ลงทะเบียน</button>
            </div>
        </div>
    </div>

    <div id="view-staff-register" class="fixed inset-0 z-[65] hidden flex items-center justify-center bg-black/90 p-6">
        <div class="bg-[#1e293b] w-full max-w-xs p-6 rounded-2xl border border-white/10 text-center">
            <h2 class="text-xl font-bold mb-2 text-white">New Staff</h2>
            <p class="text-xs text-gray-400 mb-4">กรอกชื่อเล่นเพื่อขอสิทธิ์เข้าใช้งาน</p>
            <input type="text" id="reg-name" placeholder="ชื่อเล่น" class="glass-input text-center">
            <button onclick="registerStaff()" class="btn-action mt-2">ส่งคำขอ</button>
            <button onclick="show('view-customer')" class="text-gray-500 text-sm mt-4">ยกเลิก</button>
        </div>
    </div>

    <div id="view-staff-waiting" class="fixed inset-0 z-[65] hidden flex flex-col items-center justify-center bg-black">
        <div class="text-6xl mb-4">⏳</div>
        <h2 class="text-xl font-bold text-white">รอการอนุมัติ</h2>
        <p class="text-gray-400 text-sm mt-2">กรุณาแจ้งผู้จัดการร้าน</p>
        <p id="my-uid-display" class="mt-6 bg-white/10 p-2 rounded text-xs font-mono select-all text-gray-300"></p>
        <button onclick="show('view-customer')" class="mt-8 text-gray-500 underline">กลับหน้าหลัก</button>
    </div>

    <script>
        const CFG = { liff: "__LIFF__", worker: "__WORKER__", pass: "__PASS__" };
        let profile = {};
        let html5QrcodeScanner = null;
        let depType = 'liquor';

        // --- INIT ---
        async function main() {
            try {
                await liff.init({ liffId: CFG.liff });
                if (!liff.isLoggedIn()) { liff.login(); return; }
                profile = await liff.getProfile();
                
                document.getElementById('user-img').src = profile.pictureUrl;
                document.getElementById('user-name').innerText = profile.displayName;
                document.getElementById('bk-date').valueAsDate = new Date();
                
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.get('claim_id')) await claimDeposit(urlParams.get('claim_id'));
                
                checkRole();
            } catch (e) { alert("Init Error: " + e); }
        }

        async function checkRole() {
            try {
                const res = await fetch(CFG.worker + "/api/me?uid=" + profile.userId);
                const data = await res.json();
                document.getElementById('loading').classList.add('hidden');

                if (data.status === 'pending') {
                    show('view-staff-waiting');
                    document.getElementById('my-uid-display').innerText = profile.userId;
                } else if (data.role === 'staff' || data.role === 'manager') {
                    show('view-staff');
                    document.getElementById('btn-staff-switch').classList.remove('hidden');
                    sessionStorage.setItem('staffName', data.name);
                } else {
                    show('view-customer'); loadMyWallet();
                }
            } catch (e) { alert("Connection Error"); }
        }

        // --- NAVIGATION ---
        function show(id) {
            document.querySelectorAll('[id^="view-"], [id^="modal-"]').forEach(el => {
                el.classList.add('hidden'); el.classList.remove('flex');
            });
            const t = document.getElementById(id);
            t.classList.remove('hidden');
            if(id.startsWith('modal-')) t.classList.add('flex');
            window.scrollTo(0,0);
        }

        function switchMode() {
            const staffView = document.getElementById('view-staff');
            if (staffView.classList.contains('hidden')) show('view-staff');
            else show('view-customer');
        }

        function closeModal(id) {
            show(sessionStorage.getItem('staffName') ? 'view-staff' : 'view-customer');
            if(html5QrcodeScanner) html5QrcodeScanner.stop().catch(()=>{});
        }

        // --- MANAGER LOGIC ---
        async function verifyManager() {
            if(document.getElementById('mgr-pass').value === CFG.pass) {
                show('view-manager'); loadManagerData(); loadHistoryLogs();
            } else alert("รหัสผิด");
        }
        function switchMgrTab(tab) {
            document.getElementById('mgr-tab-users').classList.add('hidden');
            document.getElementById('mgr-tab-logs').classList.add('hidden');
            document.getElementById('mgr-tab-'+tab).classList.remove('hidden');
        }
        async function loadManagerData() {
            const res = await fetch(CFG.worker + "/api/manager-list");
            const data = await res.json();
            const pList = document.getElementById('pending-list'); pList.innerHTML = "";
            data.pending.forEach(s => {
                pList.innerHTML += `<div class="flex justify-between py-2 border-b border-white/10"><span>${s.name}</span><button onclick="staffAction('approve','${s.user_id}','${s.name}')" class="text-green-400 font-bold">✓</button></div>`;
            });
            const aList = document.getElementById('active-list'); aList.innerHTML = "";
            data.active.forEach(s => {
                aList.innerHTML += `<div class="flex justify-between py-2 border-b border-white/10"><span>${s.name}</span><button onclick="staffAction('remove','${s.user_id}','${s.name}')" class="text-red-400 font-bold">✕</button></div>`;
            });
        }
        async function loadHistoryLogs() {
            const res = await fetch(CFG.worker + "/api/logs");
            const data = await res.json();
            const list = document.getElementById('logs-list'); list.innerHTML = "";
            data.logs.forEach(l => {
                const color = l.action === 'deposit' ? 'text-blue-400' : (l.action === 'withdraw' ? 'text-red-400' : 'text-gray-400');
                const date = new Date(l.created_at).toLocaleString('th-TH');
                list.innerHTML += `<div class="py-2 border-b border-white/5"><div class="flex justify-between"><strong class="${color} uppercase">${l.action}</strong><span class="opacity-50">${date}</span></div><div class="text-gray-300">${l.details}</div><div class="text-xs opacity-50">by ${l.staff_name}</div></div>`;
            });
        }
        async function staffAction(action, uid, name) {
            if(!confirm("ยืนยัน?")) return;
            await fetch(CFG.worker + "/api/staff-action", { method: 'POST', body: JSON.stringify({ action, uid, name }) });
            loadManagerData();
        }
        async function registerStaff() {
            const name = document.getElementById('reg-name').value;
            if(!name) return alert("กรุณาใส่ชื่อ");
            await fetch(CFG.worker + "/api/register", { method: 'POST', body: JSON.stringify({ uid: profile.userId, name: name }) });
            alert("ส่งคำขอแล้ว! แจ้งผู้จัดการได้เลย"); location.reload();
        }

        // --- DEPOSIT FLOW ---
        function openDepositFlow() { show('modal-deposit'); startCamera(); }
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
                document.getElementById('camera-feed').srcObject = stream;
            } catch (err) { alert("Camera Error: " + err); }
        }
        function takePhoto() {
            const v = document.getElementById('camera-feed');
            const c = document.getElementById('photo-canvas');
            c.width = 800; c.height = v.videoHeight * (800 / v.videoWidth);
            c.getContext('2d').drawImage(v, 0, 0, c.width, c.height);
            v.srcObject.getTracks().forEach(t=>t.stop());
            document.getElementById('deposit-form').classList.remove('hidden');
        }
        function setDepType(t) { depType = t; }
        async function submitDeposit() {
            const brand = document.getElementById('dep-brand').value;
            const amt = document.getElementById('dep-amount').value;
            if(!brand) return alert("กรอกข้อมูลให้ครบ");
            
            document.querySelector('#deposit-form button:last-child').innerText = "กำลังบันทึก...";
            try {
                const res = await fetch(CFG.worker + "/api/deposit", {
                    method: 'POST', body: JSON.stringify({
                        staff_name: sessionStorage.getItem('staffName') || 'Staff',
                        item_name: brand, item_type: depType, amount: amt,
                        image: document.getElementById('photo-canvas').toDataURL('image/jpeg', 0.6)
                    })
                });
                const data = await res.json();
                show('view-staff');
                document.getElementById('deposit-status-box').classList.remove('hidden');
                
                const link = `https://liff.line.me/${CFG.liff}?claim_id=${data.deposit_id}`;
                document.getElementById('deposit-qr-target').innerHTML = "";
                new QRCode(document.getElementById("deposit-qr-target"), { text: link, width: 150, height: 150 });
                
                const poll = setInterval(async () => {
                    const r = await fetch(CFG.worker + `/api/check-deposit?id=${data.deposit_id}`);
                    const d = await r.json();
                    if(d.owner_uid) { clearInterval(poll); alert("ลูกค้ารับของแล้ว!"); location.reload(); }
                }, 3000);
            } catch(e) { alert("Error"); }
        }

        // --- WITHDRAW FLOW ---
        function openWithdrawScanner() { show('modal-withdraw'); startScanner(); }
        function startScanner() {
             html5QrcodeScanner = new Html5Qrcode("reader");
             html5QrcodeScanner.start({ facingMode: "environment" }, { fps: 10, qrbox: 250 }, (txt) => {
                html5QrcodeScanner.stop(); processWithdraw(txt);
            });
        }
        async function manualWithdraw() { processWithdraw(document.getElementById('manual-code').value); }
        async function processWithdraw(code) {
            if(!confirm("ยืนยันเบิกรายการ "+code+"?")) return startScanner();
            const res = await fetch(CFG.worker + "/api/withdraw", { method: 'POST', body: JSON.stringify({ code, staff: sessionStorage.getItem('staffName') }) });
            const d = await res.json();
            if(d.success) { alert("เบิกสำเร็จ!"); closeModal('modal-withdraw'); }
            else { alert(d.message); startScanner(); }
        }

        // --- WALLET & BOOKING ---
        async function claimDeposit(id) {
            if(!confirm("รับรายการนี้เข้ากระเป๋า?")) return;
            await fetch(CFG.worker + "/api/claim", { method: 'POST', body: JSON.stringify({ id, uid: profile.userId }) });
            alert("เรียบร้อย!"); window.location.href = window.location.pathname;
        }
        async function loadMyWallet() {
            const res = await fetch(CFG.worker + "/api/my-wallet?uid=" + profile.userId);
            const data = await res.json();
            const list = document.getElementById('my-bottle-list'); list.innerHTML = "";
            if(data.length === 0) list.innerHTML = "<div class='text-center py-10 opacity-50 border border-dashed rounded-xl border-white/20'>ไม่มีรายการฝาก</div>";
            data.forEach(item => {
                const days = Math.ceil((new Date(new Date(item.created_at).getTime()+30*86400000) - new Date())/86400000);
                list.innerHTML += `
                <div class="bg-white/5 p-4 rounded-xl border border-white/10 relative overflow-hidden">
                    <div class="absolute top-0 right-0 p-2 opacity-10 text-6xl grayscale">${item.item_type==='liquor'?'🥃':'🍺'}</div>
                    <div class="relative z-10 flex justify-between mb-4">
                        <div><span class="bg-white/10 text-xs px-2 py-1 rounded font-mono">${item.deposit_code}</span><h3 class="font-bold text-xl mt-1">${item.item_name}</h3><p class="text-xs opacity-70">หมดอายุใน ${days} วัน</p></div>
                        <div class="text-right"><span class="text-2xl font-bold" style="color: var(--accent);">${item.amount}</span><span class="text-xs block opacity-70">${item.item_type==='liquor'?'%':'ขวด'}</span></div>
                    </div>
                    <div class="flex gap-2 relative z-10">
                        <button onclick="showWithdrawQR('${item.deposit_code}')" class="flex-1 bg-red-500/10 text-red-400 py-2 rounded text-sm border border-red-500/30">เบิกออก</button>
                        <button onclick="shareItem('${item.id}','${item.item_name}')" class="flex-1 bg-blue-500/10 text-blue-400 py-2 rounded text-sm border border-blue-500/30">ส่งต่อ</button>
                    </div>
                </div>`;
            });
        }
        function showWithdrawQR(code) {
            const div = document.createElement('div');
            div.className = "fixed inset-0 z-[80] bg-black/95 flex flex-col items-center justify-center p-6";
            div.innerHTML = `<div class="bg-white p-4 rounded-xl mb-4"><div id="wd-qr"></div></div><p class="text-4xl font-mono font-bold text-white tracking-widest">${code}</p><button onclick="this.parentElement.remove()" class="mt-8 text-gray-500 underline">ปิด</button>`;
            document.body.appendChild(div);
            new QRCode(document.getElementById("wd-qr"), { text: code, width: 200, height: 200 });
        }
        async function shareItem(id, name) {
            const link = `https://liff.line.me/${CFG.liff}?claim_id=${id}`;
            if(liff.isApiAvailable('shareTargetPicker')) await liff.shareTargetPicker([{type:"flex", altText:"Gift", contents:{type:"bubble", body:{type:"box", layout:"vertical", contents:[{type:"text", text:"🎁 ส่งต่อความเมา", weight:"bold", size:"xl", align:"center", color:"#EAB308"},{type:"text", text:name, margin:"md", align:"center"},{type:"button", style:"primary", action:{type:"uri", label:"รับของ", uri:link}, margin:"lg", color:"#EAB308"}]}}}]);
            else prompt("Copy Link", link);
        }
        async function submitBooking() { 
            const d = { n: document.getElementById('bk-name').value, p: document.getElementById('bk-phone').value, date: document.getElementById('bk-date').value, time: document.getElementById('bk-time').value, pax: document.getElementById('bk-pax').value };
            if(!d.n || !d.p) return alert("กรอกข้อมูลให้ครบ");
            const msg = `📅 *จองโต๊ะใหม่*\n👤 ${d.n}\n📞 ${d.p}\n🗓 ${d.date} ${d.time}\n👥 ${d.pax}`;
            if(liff.isInClient()) { await liff.sendMessages([{type:'text', text:msg}]); liff.closeWindow(); }
            else { alert("Simulated: "+msg); show('view-customer'); }
        }

        main();
    </script>
</body>
</html>"""

# ==========================================
# 2. WORKER CODE (FULL VERSION - WITH LOGS)
# ==========================================
WORKER_RAW = r"""
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type",
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

    async function addLog(action, staff, details) {
        try { await env.DB.prepare("INSERT INTO logs (action, staff_name, details) VALUES (?, ?, ?)").bind(action, staff, details).run(); } catch(e){}
    }

    try {
        if (path === "/api/me") {
            const uid = url.searchParams.get('uid');
            const user = await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ?").bind(uid).first();
            if (!user) return new Response(JSON.stringify({ role: 'customer' }), { headers: corsHeaders });
            return new Response(JSON.stringify({ role: user.role, status: user.status, name: user.name }), { headers: corsHeaders });
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
            const code = Math.floor(Math.random()*65535).toString(16).toUpperCase().padStart(4, '0');
            const res = await env.DB.prepare(`
                INSERT INTO deposits (deposit_code, staff_name, item_name, item_type, amount, image_key, status, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, 'pending_claim', date('now', '+30 days')) RETURNING id
            `).bind(code, body.staff_name, body.item_name, body.item_type, body.amount, filename).first();
            await addLog('deposit', body.staff_name, `Deposit: ${body.item_name} (${code})`);
            return new Response(JSON.stringify({ deposit_id: res.id, code: code }), { headers: corsHeaders });
        }
        if (path === "/api/claim" && request.method === "POST") {
            const body = await request.json();
            await env.DB.prepare("UPDATE deposits SET owner_uid = ?, status = 'active' WHERE id = ?").bind(body.uid, body.id).run();
            return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
        }
        if (path === "/api/check-deposit") {
            const id = url.searchParams.get('id');
            const res = await env.DB.prepare("SELECT owner_uid FROM deposits WHERE id = ?").bind(id).first();
            return new Response(JSON.stringify(res), { headers: corsHeaders });
        }
        if (path === "/api/my-wallet") {
            const uid = url.searchParams.get('uid');
            const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_uid = ? AND status = 'active' ORDER BY created_at DESC").bind(uid).all();
            return new Response(JSON.stringify(res.results), { headers: corsHeaders });
        }
        if (path === "/api/withdraw" && request.method === "POST") {
            const body = await request.json();
            const item = await env.DB.prepare("SELECT * FROM deposits WHERE deposit_code = ? AND status = 'active'").bind(body.code).first();
            if (!item) return new Response(JSON.stringify({ success: false, message: "Not Found" }), { headers: corsHeaders });
            if (item.image_key) await env.BUCKET.delete(item.image_key);
            await env.DB.prepare("UPDATE deposits SET status = 'withdrawn' WHERE id = ?").bind(item.id).run();
            await addLog('withdraw', body.staff, `Withdrew: ${item.item_name} (${body.code})`);
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
    } catch(e) {
        return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders });
    }
    return new Response("API Ready", { headers: corsHeaders });
  }
};
"""

# ==========================================
# 3. PYTHON UI CONTROLLER
# ==========================================
class AppGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Web App Color Tuner")
        self.geometry("1000x700")
        
        # Default Colors (Midnight Blue Theme)
        self.vars = {
            'bg_color': '#0f172a',
            'grad_start': '#0e4296',
            'grad_end': '#1e293b',
            'text_main': '#ffffff',
            'text_sub': '#94a3b8',
            'accent': '#EAB308' # Gold
        }
        
        self.grid_columnconfigure(0, weight=1) # Controls
        self.grid_columnconfigure(1, weight=2) # Preview
        self.grid_rowconfigure(0, weight=1)

        self.setup_controls()
        self.setup_preview()
        self.load_config()
        self.update_preview_ui()

    def setup_controls(self):
        # Frame
        ctrl_frame = ctk.CTkFrame(self, corner_radius=0)
        ctrl_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        ctk.CTkLabel(ctrl_frame, text="🎨 Theme Controller", font=("Prompt", 20, "bold")).pack(pady=20)

        # 1. Color Pickers (Grid Layout inside Frame)
        grid_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10)
        
        self.create_color_btn(grid_frame, "Background", 'bg_color', 0)
        self.create_color_btn(grid_frame, "Card Gradient Start", 'grad_start', 1)
        self.create_color_btn(grid_frame, "Card Gradient End", 'grad_end', 2)
        self.create_color_btn(grid_frame, "Text Main", 'text_main', 3)
        self.create_color_btn(grid_frame, "Accent (Icon/Title)", 'accent', 4)

        # 2. Randomizer
        ctk.CTkButton(ctrl_frame, text="🎲 Randomize Colors (Gen)", command=self.randomize_colors, height=50, fg_color="#4F46E5", font=("Prompt", 16, "bold")).pack(fill="x", padx=20, pady=20)

        # 3. Inputs
        form_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=10)
        
        self.entries = {}
        for k in ["Shop Name", "LIFF ID", "Worker URL"]:
            ctk.CTkLabel(form_frame, text=k, anchor="w").pack(fill="x")
            e = ctk.CTkEntry(form_frame)
            e.pack(fill="x", pady=2)
            self.entries[k] = e
            if k == "Shop Name": e.bind("<KeyRelease>", self.update_preview_text)

        # Paste & Extract Button
        paste_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        paste_frame.pack(fill="x", padx=20, pady=5)
        self.txt_paste = ctk.CTkTextbox(paste_frame, height=0) # Hidden textbox used as buffer
        ctk.CTkButton(paste_frame, text="Paste Config Here to Auto-Fill", command=self.ask_paste, fg_color="#333", height=30).pack(fill="x")

        # 4. Build
        ctk.CTkButton(ctrl_frame, text="🚀 BUILD APP", command=self.build, height=50, fg_color="#10B981", font=("Prompt", 16, "bold")).pack(fill="x", side="bottom", padx=20, pady=20)

    def setup_preview(self):
        # Frame
        self.preview_area = ctk.CTkFrame(self, fg_color="#000", corner_radius=0)
        self.preview_area.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.preview_area, text="Real-time Mobile Preview", text_color="#555").pack(pady=10)

        # Phone Mockup
        self.phone = ctk.CTkFrame(self.preview_area, width=375, height=667, corner_radius=30, fg_color="#fff", border_width=8, border_color="#333")
        self.phone.place(relx=0.5, rely=0.5, anchor="center")
        self.phone.pack_propagate(False) # Strict size

        # --- Elements inside Phone (Simulating HTML) ---
        
        # Header
        self.p_header = ctk.CTkLabel(self.phone, text="🍾 SHOP NAME", font=("Arial", 24, "bold"))
        self.p_header.pack(pady=(40, 5))
        self.p_sub = ctk.CTkLabel(self.phone, text="Welcome, please select service", font=("Arial", 12))
        self.p_sub.pack(pady=(0, 30))

        # Card 1 (Booking)
        self.p_card1 = self.create_preview_card("📅", "Booking Table", "Reserve your seat")
        # Card 2 (Wallet)
        self.p_card2 = self.create_preview_card("🥃", "My Wallet", "Check deposit / Withdraw")

    def create_preview_card(self, icon, title, sub):
        card = ctk.CTkFrame(self.phone, height=100, corner_radius=15, border_width=1)
        card.pack(fill="x", padx=20, pady=10)
        card.pack_propagate(False)
        
        # Icon
        ctk.CTkLabel(card, text=icon, font=("Arial", 30), fg_color="transparent").place(relx=0.1, rely=0.5, anchor="w")
        # Text
        lbl_title = ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold"), fg_color="transparent")
        lbl_title.place(relx=0.35, rely=0.35, anchor="w")
        lbl_sub = ctk.CTkLabel(card, text=sub, font=("Arial", 12), fg_color="transparent")
        lbl_sub.place(relx=0.35, rely=0.65, anchor="w")
        
        # Store references to update colors later
        card.lbl_title = lbl_title
        card.lbl_sub = lbl_sub
        return card

    def create_color_btn(self, parent, label, key, row):
        ctk.CTkLabel(parent, text=label, anchor="w").grid(row=row, column=0, sticky="w", pady=5)
        btn = ctk.CTkButton(parent, text="", width=60, height=25, command=lambda: self.pick_color(key))
        btn.grid(row=row, column=1, sticky="e", padx=5)
        setattr(self, f"btn_{key}", btn)

    # --- LOGIC ---

    def pick_color(self, key):
        # Open persistent color chooser
        color = colorchooser.askcolor(color=self.vars[key])[1]
        if color:
            self.vars[key] = color
            self.update_preview_ui()

    def randomize_colors(self):
        # AI Color Logic (Complementary / Analogous)
        h = random.random()
        
        def hsv_to_hex(h, s, v):
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

        # Background: Very Dark
        self.vars['bg_color'] = hsv_to_hex(h, 0.6, 0.15)
        
        # Gradient: Analogous colors based on hue
        self.vars['grad_start'] = hsv_to_hex((h + 0.05) % 1.0, 0.8, 0.6)
        self.vars['grad_end'] = hsv_to_hex((h - 0.05) % 1.0, 0.6, 0.3)
        
        # Accent: Complementary (Opposite Hue) or Bright
        self.vars['accent'] = hsv_to_hex((h + 0.5) % 1.0, 0.9, 1.0)
        
        # Text: High Contrast
        self.vars['text_main'] = "#ffffff"
        self.vars['text_sub'] = "#cbd5e1" # Slate-300

        self.update_preview_ui()

    def update_preview_ui(self):
        # Update Color Buttons
        for k, v in self.vars.items():
            try: getattr(self, f"btn_{k}").configure(fg_color=v)
            except: pass

        # Update Phone Preview
        self.phone.configure(fg_color=self.vars['bg_color'])
        
        # Header
        self.p_header.configure(text_color=self.vars['accent'])
        self.p_sub.configure(text_color=self.vars['text_sub'])
        
        # Cards (Gradient Simulation: We use start color for Python preview)
        for card in [self.p_card1, self.p_card2]:
            card.configure(fg_color=self.vars['grad_start'], border_color="white", border_width=0)
            card.lbl_title.configure(text_color=self.vars['text_main'])
            card.lbl_sub.configure(text_color=self.vars['text_sub'])

    def update_preview_text(self, event):
        txt = self.entries["Shop Name"].get()
        if txt: self.p_header.configure(text="🍾 " + txt)

    def ask_paste(self):
        # Simple input dialog for paste
        dialog = ctk.CTkInputDialog(text="Paste your Config Text here:", title="Auto Fill")
        t = dialog.get_input()
        if t:
            p = {'LIFF ID':r'(\d{10}-\w{8})', 'Worker URL':r'(https?://[\w\-\.]+\.workers\.dev)'}
            for k,r in p.items():
                m = re.search(r, t)
                if m: self.entries[k].delete(0, "end"); self.entries[k].insert(0, m.group(1))
            messagebox.showinfo("OK", "Data Extracted")

    def build(self):
        shop = self.entries["Shop Name"].get().strip()
        if not shop: return messagebox.showerror("Error", "Enter Shop Name")
        
        # Save Config
        d_save = {k: v.get() for k,v in self.entries.items()}
        d_save['colors'] = self.vars
        with open("config.json", "w") as f: json.dump(d_save, f)

        html = HTML_RAW.replace("__SHOP__", shop) \
                       .replace("__BG_COLOR__", self.vars['bg_color']) \
                       .replace("__GRAD_START__", self.vars['grad_start']) \
                       .replace("__GRAD_END__", self.vars['grad_end']) \
                       .replace("__TEXT_MAIN__", self.vars['text_main']) \
                       .replace("__TEXT_SUB__", self.vars['text_sub']) \
                       .replace("__ACCENT__", self.vars['accent']) \
                       .replace("__LIFF__", self.entries["LIFF ID"].get()) \
                       .replace("__WORKER__", self.entries["Worker URL"].get()) \
                       .replace("__PASS__", "8888")

        folder = f"Output_{shop.replace(' ', '_')}"
        if not os.path.exists(folder): os.makedirs(folder)
        
        with open(f"{folder}/index.html", "w", encoding="utf-8") as f: f.write(html)
        with open(f"{folder}/worker.js", "w", encoding="utf-8") as f: f.write(WORKER_RAW)
        
        messagebox.showinfo("Success", f"App generated in {folder}")
        webbrowser.open(folder)

    def load_config(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json") as f:
                    d = json.load(f)
                    for k,v in d.items(): 
                        if k in self.entries: self.entries[k].insert(0,v)
                    if 'colors' in d:
                        self.vars = d['colors']
                        self.update_preview_ui()
            except: pass

if __name__ == "__main__":
    app = AppGenerator()
    app.mainloop()