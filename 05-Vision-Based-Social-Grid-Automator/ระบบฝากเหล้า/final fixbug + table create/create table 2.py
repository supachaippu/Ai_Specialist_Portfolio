import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog, filedialog
import os
import json
import webbrowser
import random
import colorsys
import math
import sys

# --- DEPENDENCY CHECK ---
try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Critical Error", "ต้องติดตั้ง Pillow ก่อนใช้งาน Map Editor\nกรุณาพิมพ์คำสั่ง: pip install Pillow")
    sys.exit(1)

# ==============================================================================
# 1. HTML TEMPLATE (V94.0 - FULL UNCOMPRESSED SOURCE)
# ==============================================================================
HTML_RAW = r"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>__SHOP__</title>
    
    <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* CSS VARIABLES FROM PYTHON */
        :root {
            --bg-color: __BG_COLOR__;
            --grad-start: __GRAD_START__;
            --grad-end: __GRAD_END__;
            --text-main: __TEXT_MAIN__;
            --text-sub: __TEXT_SUB__;
            --accent: __ACCENT__;
        }

        /* BASE STYLES */
        body {
            font-family: 'Prompt', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            height: 100dvh;
            width: 100vw;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            margin: 0;
            padding: 0;
        }

        .main-container {
            padding: 20px;
            width: 100%;
            max-width: 448px;
            margin: 0 auto;
            height: 100%;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow-y: auto;
        }

        .header-section {
            flex: 0 0 auto;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .hidden {
            display: none !important;
        }

        /* VIEW CONTAINERS */
        #view-customer {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding-bottom: 60px;
        }
        #view-staff, #view-wallet, #view-booking, #view-manager {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        /* BUTTON STYLES (DEFAULT) */
        .btn-menu {
            background: linear-gradient(145deg, var(--grad-start), var(--grad-end));
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: __RADIUS__;
            box-shadow: 0 8px 15px -3px rgba(0,0,0,0.4);
            padding: 25px 15px;
            margin-bottom: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            position: relative;
        }
        .btn-menu:active {
            transform: scale(0.98);
        }
        .icon {
            font-size: 36px;
            margin-bottom: 8px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        }
        .label {
            font-size: 18px;
            font-weight: 600;
            color: white;
        }
        .sub-label {
            font-size: 12px;
            color: rgba(255,255,255,0.8);
            margin-top: 2px;
        }

        /* FORM INPUTS */
        .glass-input {
            background: rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 12px;
            width: 100%;
            color: var(--text-main);
            outline: none;
            margin-bottom: 10px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .glass-input:focus {
            border-color: var(--accent);
            background: rgba(0,0,0,0.4);
            box-shadow: 0 0 0 1px var(--accent);
        }

        .btn-action {
            background: linear-gradient(90deg, var(--grad-start), var(--grad-end));
            color: white;
            font-weight: bold;
            padding: 14px;
            border-radius: 16px;
            width: 100%;
            border: none;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            cursor: pointer;
        }

        /* MAP STYLES */
        #map-container {
            width: 100%;
            height: 350px;
            background: #000;
            border-radius: 16px;
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
            display: none;
        }
        canvas {
            width: 100%;
            height: 100%;
            touch-action: none;
        }
        .map-hint {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 10px;
            pointer-events: none;
        }

        /* UTILS */
        .swal2-popup {
            background: var(--bg-color) !important;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px !important;
            color: var(--text-main) !important;
        }
        .file-upload {
            border: 2px dashed rgba(255,255,255,0.2);
            border-radius: 20px;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }
        .type-btn {
            flex: 1;
            padding: 14px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05);
            color: var(--text-sub);
        }
        .type-btn.active {
            background: linear-gradient(135deg, var(--grad-start), var(--grad-end));
            color: white;
            font-weight: bold;
            border: 1px solid var(--accent);
        }

        /* DYNAMIC LAYOUT CSS INJECTED HERE */
        __LAYOUT_CSS__
    </style>
</head>
<body>
    <div class="main-container">
        <div id="loading" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 backdrop-blur-sm">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-t-transparent" style="border-color: var(--accent);"></div>
        </div>

        <div class="header-section">
            <div onclick="secretTap()" class="flex-1 text-left">
                <h1 class="text-2xl font-bold mb-0 tracking-tight" style="color: var(--text-main);">__SHOP__</h1>
                <p class="text-[10px] uppercase tracking-widest font-semibold opacity-70" style="color: var(--accent);">Nightlife System</p>
            </div>
            <div class="flex flex-col gap-1 items-end">
                <div class="flex gap-2">
                    <select id="lang-switch" class="bg-white/10 text-white rounded px-2 text-xs" onchange="changeLang(this.value)">
                        <option value="th">🇹🇭 TH</option>
                        <option value="en">🇬🇧 EN</option>
                        <option value="cn">🇨🇳 CN</option>
                    </select>
                    <button id="btn-staff-switch" onclick="toggleStaffMode()" class="hidden text-[10px] bg-white/10 px-2 py-1 rounded-full border border-white/5 text-gray-300 flex items-center gap-1">
                        <span>🔄</span> <span id="staff-mode-text">Staff</span>
                    </button>
                    <button onclick="verifyManager()" class="opacity-30 hover:opacity-100 text-sm transition-opacity">⚙️</button>
                </div>
            </div>
        </div>

        <div id="view-customer" class="hidden animate-fade-in">
             <div class="flex flex-col items-center mb-6">
                <div class="inline-block p-1 rounded-full border-2 mb-2 shadow-lg" style="border-color: var(--accent);">
                    <img id="user-img" class="w-16 h-16 rounded-full" src="">
                </div>
                <h2 id="user-name" class="text-xl font-bold">Guest</h2>
                <p class="text-xs font-light" data-i18n="welcome">ยินดีต้อนรับ</p>
             </div>
             <div class="menu-layout w-full pb-4">
                <div onclick="show('view-booking'); tryRenderMap();" class="btn-menu menu-item-1">
                    <span class="icon">📅</span>
                    <span class="label" data-i18n="menu_booking">จองโต๊ะ</span>
                    <span class="sub-label" data-i18n="menu_booking_sub">สำรองที่นั่ง / ผังร้าน</span>
                </div>
                <div onclick="show('view-wallet'); startWalletSync();" class="btn-menu menu-item-2">
                    <span class="icon">🥃</span>
                    <span class="label" data-i18n="menu_wallet">ระบบฝากเหล้า</span>
                    <span class="sub-label" data-i18n="menu_wallet_sub">เช็ครายการฝาก / เบิกเหล้า / โอนสิทธิ์</span>
                </div>
             </div>
        </div>

        <div id="view-staff" class="hidden">
            <div class="text-center mb-4">
                <span class="bg-white/10 px-3 py-1 rounded-full text-[10px] uppercase tracking-widest border border-white/10">STAFF ACCESS</span>
            </div>
            <div class="flex flex-col gap-4 flex-1 justify-center">
                <div onclick="openDepositFlow()" class="btn-menu">
                    <span class="icon">📥</span><span class="label">รับฝาก</span>
                </div>
                <div onclick="openWithdrawScanner()" class="btn-menu" style="border-color: rgba(239, 68, 68, 0.2);">
                    <span class="icon">📤</span><span class="label text-red-300">เบิกออก</span>
                </div>
            </div>
        </div>

        <div id="view-booking" class="hidden h-full flex flex-col">
            <div class="flex justify-between mb-4 items-center">
                <h2 class="text-xl font-bold" data-i18n="bk_title">📝 จองโต๊ะ</h2>
                <button onclick="show('view-customer')" class="text-2xl hover:text-white transition opacity-50">×</button>
            </div>
            <div class="flex-1 overflow-y-auto pr-1">
                <div id="map-container">
                    <canvas id="map-canvas"></canvas>
                    <div class="map-hint">👆 แตะเพื่อเลือกโต๊ะ (สีเหลือง)</div>
                </div>
                <div id="selected-table-info" class="hidden bg-white/5 p-2 rounded mb-3 border border-yellow-500/30 flex justify-between items-center">
                    <span class="text-gray-400 text-xs">โต๊ะที่เลือก:</span>
                    <span id="sel-table-id" class="text-yellow-400 font-bold text-lg"></span>
                </div>
                <div class="bg-white/5 p-5 rounded-3xl border border-white/10 space-y-4 shadow-xl backdrop-blur-sm">
                    <input type="text" id="bk-name" placeholder="ชื่อผู้จอง" class="glass-input" data-i18n-ph="ph_name">
                    <input type="tel" id="bk-phone" placeholder="เบอร์โทรติดต่อ" class="glass-input" data-i18n-ph="ph_phone">
                    <div class="flex gap-3">
                        <input type="date" id="bk-date" class="glass-input" onchange="onDateChange()">
                        <input type="time" id="bk-time" value="20:00" class="glass-input">
                    </div>
                    <div class="relative">
                        <input type="number" id="bk-pax" placeholder="จำนวนคน" class="glass-input" oninput="calculateTables()" data-i18n-ph="ph_pax">
                        <div id="pax-hint" class="text-xs text-right text-yellow-500 mt-1 hidden"></div>
                    </div>
                    <button onclick="submitBooking()" class="btn-action mt-2 shadow-xl" data-i18n="btn_confirm_bk">ยืนยันการจอง</button>
                </div>
            </div>
        </div>

        <div id="view-wallet" class="hidden h-full flex flex-col">
            <div class="flex justify-between mb-4 items-center shrink-0">
                <button onclick="stopWalletSync(); show('view-customer')" class="text-xs flex items-center gap-1 opacity-70 hover:opacity-100 transition">← <span data-i18n="back">กลับ</span></button>
                <div class="flex gap-2">
                    <button id="btn-wallet-refresh" onclick="manualWalletRefresh()" class="btn-refresh-pill">↻ อัพเดท</button>
                </div>
            </div>
            <div class="flex justify-between items-end mb-4 shrink-0">
                <h2 class="text-xl font-bold" data-i18n="wallet_title">🍾 My Collection</h2>
                <button onclick="manualClaimInput()" class="text-[10px] px-3 py-1 rounded-full font-bold shadow-lg mb-1 bg-accent text-black" data-i18n="btn_manual_code">🔑 กรอกรหัส</button>
            </div>
            <div class="flex-1 overflow-y-auto" id="wallet-active"></div>
            <div class="mt-4 border-t border-white/10 pt-2">
                <h3 class="text-xs font-bold text-gray-500" data-i18n="wallet_history">History</h3>
                <div id="wallet-history" class="opacity-60"></div>
            </div>
        </div>

        <div id="view-manager" class="hidden h-full flex flex-col">
            <div class="flex justify-between mb-4">
                <h2 class="text-xl font-bold">👑 Dashboard</h2>
                <button onclick="location.reload()" class="text-xs text-red-400">Logout</button>
            </div>
            <div class="flex gap-2 mb-4">
                <button onclick="switchMgrTab('stock')" class="flex-1 py-2 bg-white/10 rounded">Stock</button>
                <button onclick="switchMgrTab('users')" class="flex-1 py-2 rounded text-gray-400">Staff</button>
                <button onclick="switchMgrTab('logs')" class="flex-1 py-2 rounded text-gray-400">Logs</button>
            </div>
            <div id="mgr-tab-stock" class="flex-1 overflow-y-auto">
                <input id="filter-brand" placeholder="Search..." class="glass-input mb-2" onkeyup="filterStock()">
                <div id="stock-list"></div>
            </div>
            <div id="mgr-tab-users" class="hidden flex-1">
                <div id="pending-list"></div>
                <div id="active-list" class="mt-4"></div>
            </div>
            <div id="mgr-tab-logs" class="hidden flex-1">
                <div id="logs-list" class="text-xs"></div>
            </div>
        </div>
        
        <div id="modal-deposit" class="fixed inset-0 z-[70] hidden flex-col bg-black p-4">
            <div class="flex justify-between mb-2"><h2>📸 ฝากของ</h2><button onclick="show('view-staff')" class="text-gray-400">✕</button></div>
            <div class="bg-white/5 p-4 rounded-xl text-center mb-4">
                <div class="text-xs text-gray-400">CODE</div>
                <div id="pre-gen-code" class="text-4xl font-mono font-bold text-accent tracking-widest">...</div>
                <button onclick="genNewCode()" class="text-xs underline mt-2 opacity-50">สุ่มใหม่</button>
            </div>
            <label class="file-upload">
                <input type="file" accept="image/*" capture="environment" id="dep-file" class="hidden" onchange="previewDepositImage(this)">
                <img id="dep-preview" class="hidden w-full h-full object-cover">
                <div id="dep-placeholder">📷 ถ่ายรูป</div>
            </label>
            <div class="flex gap-2 mt-2">
                <button onclick="setDepType('liquor')" id="btn-type-liquor" class="type-btn active">🥃 เหล้า</button>
                <button onclick="setDepType('beer')" id="btn-type-beer" class="type-btn">🍺 เบียร์</button>
            </div>
            <input id="dep-brand" placeholder="ยี่ห้อ" class="glass-input mt-2">
            <input id="dep-amount" placeholder="จำนวน/เปอร์เซ็นต์" class="glass-input">
            <input id="dep-remark" placeholder="หมายเหตุ" class="glass-input">
            <button onclick="submitDeposit()" class="btn-action mt-2">บันทึก</button>
        </div>
        
        <div id="view-staff-register" class="fixed inset-0 z-[65] hidden flex items-center justify-center bg-black/90 p-6">
            <div class="bg-[#1e293b] w-full max-w-xs p-6 rounded-2xl text-center">
                <h2 class="text-xl font-bold mb-2">New Staff</h2>
                <input type="text" id="reg-name" placeholder="ชื่อเล่น" class="glass-input text-center">
                <button onclick="registerStaff()" class="btn-action mt-2">ส่งคำขอ</button>
            </div>
        </div>
        <div id="view-staff-waiting" class="fixed inset-0 z-[65] hidden flex flex-col items-center justify-center bg-black">
            <div class="text-6xl mb-4">⏳</div>
            <h2 class="text-xl font-bold text-white">รอการอนุมัติ</h2>
            <p id="my-uid-display" class="mt-6 bg-white/10 p-2 rounded text-xs font-mono select-all text-gray-300"></p>
            <button onclick="show('view-customer')" class="mt-8 text-gray-500 underline">กลับหน้าหลัก</button>
        </div>

        <div id="modal-withdraw" class="fixed inset-0 z-[70] hidden flex-col bg-black p-4">
            <div class="flex justify-between mb-4"><h2 class="text-xl font-bold">📤 สแกนเบิก</h2><button onclick="show('view-staff')">✕</button></div>
            <div id="reader" class="rounded-xl overflow-hidden mb-4 border border-white/20 bg-black min-h-[250px]"></div>
            <input id="manual-code" placeholder="รหัส 5 หลัก" class="glass-input text-center text-xl font-mono">
            <button onclick="manualWithdraw()" class="btn-action mt-2">เบิก</button>
        </div>
    </div>

    <script>
        // CONFIGURATION VARIABLES FROM PYTHON
        const CFG = { 
            liff: "__LIFF__", 
            worker: "__WORKER__", 
            shop: "__SHOP__", 
            hold: "__HOLD_TIME__", 
            bk_tmpl: __BK_MSG__ 
        };
        const BK_MODE = "__BK_MODE__";
        const MAP_DATA = __MAP_JSON__; 
        const MAP_IMG_URL = "__MAP_IMG__";
        
        // GLOBAL VARIABLES
        let profile = {};
        let html5QrcodeScanner = null;
        let depType = 'liquor';
        let walletInterval = null;
        let isStaffMode = false;
        let staffUser = null;
        let allStockData = [];
        let secretTapCount = 0;
        let currentLang = 'th';
        let logsLimit = 10;
        let currentDepCode = "";
        let bookedTables = [];
        let selectedTable = null;
        let currentPax = 4;
        let requiredTableCount = 1;
        let selectedTables = [];

        // LANGUAGE DATA
        const I18N = {
            th: {
                welcome: "ยินดีต้อนรับ,",
                menu_booking: "จองโต๊ะ", menu_booking_sub: "สำรองที่นั่งล่วงหน้า",
                menu_wallet: "ระบบฝากเหล้า", menu_wallet_sub: "เช็ครายการฝาก",
                bk_title: "📝 จองโต๊ะ",
                ph_name: "ชื่อผู้จอง", ph_phone: "เบอร์โทรติดต่อ", ph_pax: "จำนวนคน (เช่น 5 คน)",
                btn_confirm_bk: "ยืนยันการจอง",
                wallet_title: "🍾 My Collection", wallet_active: "📦 รายการคงเหลือ", wallet_history: "🕒 ประวัติการเบิก",
                back: "กลับ", btn_manual_code: "🔑 กรอกรหัสรับของ", alert_fill: "กรุณากรอกข้อมูลให้ครบ"
            },
            en: {
                welcome: "Welcome,",
                menu_booking: "Book Table", menu_booking_sub: "Reserve in advance",
                menu_wallet: "My Bottle", menu_wallet_sub: "Check / Withdraw",
                bk_title: "📝 Reservation",
                ph_name: "Your Name", ph_phone: "Phone Number", ph_pax: "Pax (e.g. 5 ppl)",
                btn_confirm_bk: "Confirm Booking",
                wallet_title: "🍾 My Collection", wallet_active: "📦 Active Items", wallet_history: "🕒 History",
                back: "Back", btn_manual_code: "🔑 Enter Code", alert_fill: "Please fill all fields"
            },
            cn: {
                welcome: "欢迎,",
                menu_booking: "预订桌位", menu_booking_sub: "提前预订",
                menu_wallet: "我的酒库", menu_wallet_sub: "查看 / 取酒",
                bk_title: "📝 预订",
                ph_name: "姓名", ph_phone: "电话号码", ph_pax: "人数 (例如 5人)",
                btn_confirm_bk: "确认预订",
                wallet_title: "🍾 我的收藏", wallet_active: "📦 现有物品", wallet_history: "🕒 历史记录",
                back: "返回", btn_manual_code: "🔑 输入代码", alert_fill: "请填写完整信息"
            }
        };

        // --- HELPER FUNCTIONS ---
        function changeLang(l) {
            currentLang = l;
            document.querySelectorAll('[data-i18n]').forEach(e => e.innerText = I18N[l][e.getAttribute('data-i18n')]);
            document.querySelectorAll('[data-i18n-ph]').forEach(e => e.placeholder = I18N[l][e.getAttribute('data-i18n-ph')]);
        }

        function formatDateSmart(dateStr) {
            if (!dateStr) return "";
            const d = new Date(dateStr);
            const day = String(d.getDate()).padStart(2, '0');
            const month = String(d.getMonth() + 1).padStart(2, '0');
            let year = d.getFullYear();
            if (currentLang === 'th') { return `${day}-${month}-${year + 543}`; }
            else { return `${day}-${month}-${year}`; }
        }

        // --- MAIN INITIALIZATION ---
        async function main() {
            try {
                await liff.init({ liffId: CFG.liff });
                if (!liff.isLoggedIn()) {
                    liff.login({ redirectUri: window.location.href });
                    return;
                }
                profile = await liff.getProfile();
                document.getElementById('user-img').src = profile.pictureUrl;
                document.getElementById('user-name').innerText = profile.displayName;
                document.getElementById('bk-date').valueAsDate = new Date();
                
                // CHECK FOR MAGIC LINK
                const urlParams = new URLSearchParams(window.location.search);
                const magicCode = urlParams.get('magic_code');
                const uClaimId = urlParams.get('claim_id');
                
                if(magicCode) {
                    await autoClaim(magicCode);
                } else if(uClaimId) {
                    await claimDeposit(uClaimId);
                }

                checkRole();
                setupBookingView();
                
            } catch(e) {
                document.getElementById('loading').classList.add('hidden');
                show('view-customer');
            }
        }

        async function autoClaim(code) {
            try {
                const res = await fetch(CFG.worker+"/api/claim", { method: 'POST', body: JSON.stringify({ code: code, uid: profile.userId, name: profile.displayName }) });
                const d = await res.json();
                if(d.success) Swal.fire("สำเร็จ!", "ข้อมูลถูกย้ายมาที่บัญชีใหม่แล้ว", "success").then(() => { window.history.replaceState({}, document.title, window.location.pathname); show('view-wallet'); startWalletSync(); });
                else Swal.fire("ไม่พบข้อมูล", "รหัสไม่ถูกต้อง หรือถูกใช้ไปแล้ว", "error");
            } catch(e) { Swal.fire("Error", "Connection Error", "error"); }
        }

        async function checkRole() {
            try {
                const res = await fetch(CFG.worker+"/api/me?uid="+profile.userId);
                const data = await res.json();
                document.getElementById('loading').classList.add('hidden');
                if(data.status === 'pending') {
                    show('view-staff-waiting');
                    document.getElementById('my-uid-display').innerText = profile.userId;
                } else if(data.role === 'staff' || data.role === 'manager') {
                    staffUser = data;
                    document.getElementById('btn-staff-switch').classList.remove('hidden');
                    isStaffMode = true;
                    updateModeUI();
                } else {
                    show('view-customer');
                }
            } catch(e) {
                document.getElementById('loading').classList.add('hidden');
                show('view-customer');
            }
        }

        function show(id) {
            document.querySelectorAll('[id^="view-"], [id^="modal-"]').forEach(el => {
                if(!el.id.startsWith('booking-')) {
                    el.classList.add('hidden');
                    el.classList.remove('flex');
                }
            });
            const t = document.getElementById(id);
            t.classList.remove('hidden');
            if(id.startsWith('modal-')) t.classList.add('flex');
            window.scrollTo(0,0);
            if(id === 'view-booking') setupBookingView();
        }

        function toggleStaffMode() { isStaffMode = !isStaffMode; updateModeUI(); }
        function updateModeUI() { const btnText = document.getElementById('staff-mode-text'); if (btnText) { btnText.innerText = isStaffMode ? "User" : "Staff"; show(isStaffMode ? 'view-staff' : 'view-customer'); } }
        function closeModal(id) { show(isStaffMode ? 'view-staff' : 'view-customer'); if(html5QrcodeScanner) { html5QrcodeScanner.clear(); html5QrcodeScanner = null; } }
        function secretTap() { secretTapCount++; if (secretTapCount >= 5) { show('view-staff-register'); secretTapCount = 0; } }

        // --- MAP LOGIC (V96) ---
        let mapImg = new Image();
        let scale = 1;

        function setupBookingView() { if(BK_MODE==='map') tryRenderMap(); }

        function calculateTables() {
            const pax = parseInt(document.getElementById('bk-pax').value) || 0;
            if(pax > 0) {
                requiredTableCount = Math.ceil(pax/4);
                document.getElementById('pax-hint').innerText = `มา ${pax} คน = ต้องจอง ${requiredTableCount} โต๊ะ`;
                document.getElementById('pax-hint').classList.remove('hidden');
            } else {
                requiredTableCount = 1;
                document.getElementById('pax-hint').classList.add('hidden');
            }
            if(BK_MODE === 'map') {
                selectedTables = [];
                updateSelectionUI();
                draw();
            }
        }

        async function onDateChange() {
            const dateStr = document.getElementById('bk-date').value;
            try {
                const res = await fetch(`${CFG.worker}/api/bookings?date=${dateStr}`);
                const d = await res.json();
                bookedTables = d.booked || [];
                tryRenderMap();
            } catch(e) { bookedTables = []; }
        }

        function tryRenderMap() {
            if(BK_MODE !== 'map') return;
            const container = document.getElementById('map-container');
            container.style.display = 'block';
            const canvas = document.getElementById('map-canvas');
            const ctx = canvas.getContext('2d');
            
            // High DPI support
            const dpr = window.devicePixelRatio || 1;
            const rect = container.getBoundingClientRect();
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            ctx.scale(dpr, dpr);

            mapImg.src = MAP_IMG_URL || "https://via.placeholder.com/800x400?text=No+Map";
            mapImg.onload = () => {
                const scaleW = rect.width / mapImg.width;
                const scaleH = rect.height / mapImg.height;
                scale = Math.min(scaleW, scaleH);
                draw();
            };

            canvas.onclick = (e) => {
                const rect = canvas.getBoundingClientRect();
                const clickX = (e.clientX - rect.left) / scale;
                const clickY = (e.clientY - rect.top) / scale;
                let clicked = null;
                const r = 30; // Touch radius
                
                if(MAP_DATA && MAP_DATA.tables) {
                    MAP_DATA.tables.forEach(t => {
                        if(clickX >= t.x-r && clickX <= t.x+r && clickY >= t.y-r && clickY <= t.y+r) clicked = t;
                    });
                }
                if(clicked) handleTableClick(clicked);
            };
        }

        function handleTableClick(t) {
            if(bookedTables.includes(t.id)) return Swal.fire("เต็ม", "โต๊ะนี้จองแล้ว", "warning");
            
            const idx = selectedTables.indexOf(t.id);
            if(idx > -1) {
                selectedTables.splice(idx, 1);
            } else {
                if(selectedTables.length < requiredTableCount) {
                    // Check adjacency if not the first table
                    if(selectedTables.length > 0) {
                        const lastId = selectedTables[selectedTables.length-1];
                        const lastT = MAP_DATA.tables.find(x => x.id === lastId);
                        if(lastT.neighbors && !lastT.neighbors.includes(t.id)) {
                            return Swal.fire("ไม่ติดกัน", "กรุณาเลือกโต๊ะที่เชื่อมกัน", "warning");
                        }
                    }
                    selectedTables.push(t.id);
                } else {
                    if(requiredTableCount === 1) {
                        selectedTables = [t.id]; // Replace if only 1 required
                    } else {
                        Swal.fire("ครบแล้ว", `เลือกครบ ${requiredTableCount} โต๊ะแล้ว`, "info");
                    }
                }
            }
            updateSelectionUI();
            draw();
        }

        function updateSelectionUI() {
            const el = document.getElementById('selected-table-info');
            if(selectedTables.length > 0) {
                el.classList.remove('hidden');
                document.getElementById('sel-table-id').innerText = selectedTables.join(", ");
            } else {
                el.classList.add('hidden');
            }
        }

        function draw() {
            const canvas = document.getElementById('map-canvas');
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            ctx.clearRect(0, 0, rect.width, rect.height);
            
            ctx.save();
            ctx.scale(scale, scale);
            ctx.drawImage(mapImg, 0, 0);
            
            if(MAP_DATA && MAP_DATA.tables) {
                MAP_DATA.tables.forEach(t => {
                    const isSel = selectedTables.includes(t.id);
                    const isBooked = bookedTables.includes(t.id);
                    
                    ctx.beginPath();
                    ctx.arc(t.x, t.y, 20, 0, 2*Math.PI);
                    
                    if (isBooked) {
                        ctx.fillStyle = "#EF4444"; // Red
                    } else if (isSel) {
                        ctx.fillStyle = "#EAB308"; // Gold
                    } else {
                        ctx.fillStyle = "rgba(59, 130, 246, 0.6)"; // Blue
                    }
                    
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = isSel ? 3 : 1;
                    ctx.fill();
                    ctx.stroke();
                    
                    ctx.fillStyle = "white";
                    ctx.font = "bold 12px Arial";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(t.id, t.x, t.y);
                });
            }
            ctx.restore();
        }

        async function submitBooking() {
            const d = { 
                n: document.getElementById('bk-name').value, 
                p: document.getElementById('bk-phone').value, 
                date: document.getElementById('bk-date').value, 
                time: document.getElementById('bk-time').value, 
                pax: document.getElementById('bk-pax').value 
            };
            
            if(!d.n || !d.p || !d.pax) return Swal.fire("แจ้งเตือน", I18N[currentLang].alert_fill, "warning");
            
            if(BK_MODE === 'map' && selectedTables.length < requiredTableCount) {
                return Swal.fire("เลือกโต๊ะไม่ครบ", `มา ${d.pax} คน ต้องเลือก ${requiredTableCount} โต๊ะ`, "warning");
            }
            
            // Loop booking for multiple tables
            if(BK_MODE === 'map') {
                for(const tid of selectedTables) {
                    await fetch(`${CFG.worker}/api/book`, {
                        method: 'POST',
                        body: JSON.stringify({
                            uid: profile.userId,
                            name: d.n,
                            phone: d.p,
                            date: d.date,
                            time: d.time,
                            pax: d.pax,
                            table_id: tid
                        })
                    });
                }
            }

            let msg = CFG.bk_tmpl
                .replace('{name}', d.n)
                .replace('{phone}', d.p)
                .replace('{date}', d.date)
                .replace('{time}', d.time)
                .replace('{pax}', d.pax)
                .replace('{shop}', CFG.shop)
                .replace('{hold}', CFG.hold);
            
            if(BK_MODE === 'map' && selectedTables.length > 0) {
                msg += `\n📍 โต๊ะ: ${selectedTables.join(", ")}`;
            }
            
            if(liff.isInClient()) {
                await liff.sendMessages([{type:'text', text:msg}]);
                liff.closeWindow();
            } else {
                Swal.fire("Sent", msg, "success");
            }
        }

        // --- WALLET & STAFF LOGIC ---
        function genNewCode() {
            currentDepCode = Math.floor(10000 + Math.random() * 90000).toString();
            document.getElementById('pre-gen-code').innerText = currentDepCode;
        }
        function openDepositFlow() {
            genNewCode();
            show('modal-deposit');
        }
        function previewDepositImage(i) {
            if(i.files && i.files[0]) {
                const r = new FileReader();
                r.onload = e => {
                    document.getElementById('dep-preview').src = e.target.result;
                    document.getElementById('dep-preview').classList.remove('hidden');
                    document.getElementById('dep-placeholder').classList.add('hidden');
                };
                r.readAsDataURL(i.files[0]);
            }
        }
        function setDepType(t) {
            depType = t;
            document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-type-'+t).classList.add('active');
        }
        async function submitDeposit() {
            const f = document.getElementById('dep-file').files[0];
            const b = document.getElementById('dep-brand').value;
            if(!f) return Swal.fire("!", "ถ่ายรูป", "warning");
            
            const fd = new FormData();
            fd.append('image', f);
            fd.append('staff_uid', profile.userId);
            fd.append('item_name', b);
            fd.append('item_type', depType);
            fd.append('amount', document.getElementById('dep-amount').value);
            fd.append('remarks', document.getElementById('dep-remark').value);
            fd.append('deposit_code', currentDepCode);
            
            try {
                const res = await fetch(CFG.worker+"/api/deposit", { method: 'POST', body: fd });
                const d = await res.json();
                if(d.success) Swal.fire("Success", `Code: ${d.code}`, "success").then(() => show('view-staff'));
                else Swal.fire("Error", d.message, "error");
            } catch(e) {
                Swal.fire("Error", "Connection", "error");
            }
        }
        function manualWalletRefresh() { loadMyWallet(); }
        async function loadMyWallet() {
            try {
                const res = await fetch(CFG.worker+"/api/my-wallet?uid="+profile.userId);
                const data = await res.json();
                let html = "";
                data.forEach(i => {
                    if(i.status === 'active') {
                        const days = Math.ceil((new Date(i.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
                        const color = days <= 5 ? 'text-red-500' : 'text-green-500';
                        html += `
                        <div class="bg-white/5 p-3 rounded mb-2 flex gap-3 border border-white/10">
                            <img src="${CFG.worker}/api/image/${i.image_key}" class="w-16 h-16 rounded object-cover bg-black" onclick="viewImage('${CFG.worker}/api/image/${i.image_key}')">
                            <div class="flex-1">
                                <div>${i.item_name}</div>
                                <div class="text-xs text-gray-400">Code: ${i.deposit_code} | <span class="${color}">${days} วัน</span></div>
                                <button onclick="shareItem('${i.id}','${i.item_name}','${i.image_key}')" class="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded mt-1">🎁 ส่งต่อ</button>
                            </div>
                        </div>`;
                    }
                });
                document.getElementById('wallet-active').innerHTML = html || "<p class='text-center opacity-50'>Empty</p>";
            } catch(e) {}
        }
        
        function viewImage(url) {
            Swal.fire({
                imageUrl: url,
                imageAlt: 'Zoom',
                showCloseButton: true,
                showConfirmButton: false,
                background: 'transparent',
                backdrop: 'rgba(0,0,0,0.9)'
            });
        }

        async function manualClaimInput() {
            const { value: c } = await Swal.fire({ title: 'Enter Code', input: 'text' });
            if(c) {
                await fetch(CFG.worker+"/api/claim", { method: 'POST', body: JSON.stringify({ code: c, uid: profile.userId, name: profile.displayName }) });
                Swal.fire("Success", "Added", "success").then(loadMyWallet);
            }
        }
        async function shareItem(id, name, imgKey) {
            if (!liff.isApiAvailable('shareTargetPicker')) return Swal.fire("Error", "Device not support", "error");
            const img = `${CFG.worker}/api/image/${imgKey}`;
            liff.shareTargetPicker([{
                type: "flex",
                altText: "Gift",
                contents: {
                    type: "bubble",
                    hero: { type: "image", url: img, size: "full", aspectRatio: "1:1", aspectMode: "cover" },
                    body: {
                        type: "box", layout: "vertical",
                        contents: [
                            { type: "text", text: "🎁 Gift for you", weight: "bold", color: "#EAB308" },
                            { type: "text", text: name, size: "xl" }
                        ]
                    },
                    footer: {
                        type: "box", layout: "vertical",
                        contents: [{ type: "button", style: "primary", action: { type: "uri", label: "GET", uri: `https://liff.line.me/${CFG.liff}?claim_id=${id}` } }]
                    }
                }
            }]).then(res => { if(res) Swal.fire("Sent") });
        }
        
        async function claimDeposit(id) {
            try {
                const res = await fetch(CFG.worker + "/api/claim", { method: 'POST', body: JSON.stringify({ id, uid: profile.userId, name: profile.displayName }) });
                const d = await res.json();
                if(d.success) Swal.fire("Success", "รับของแล้ว", "success").then(() => location.href = location.pathname);
            } catch(e) {}
        }

        function startWalletSync() { loadMyWallet(); walletInterval = setInterval(loadMyWallet, 5000); }
        function stopWalletSync() { clearInterval(walletInterval); }
        
        function openWithdrawScanner() { show('modal-withdraw'); startScanner(); }
        function startScanner() { html5QrcodeScanner = new Html5Qrcode("reader"); html5QrcodeScanner.start({ facingMode: "environment" }, { fps: 10 }, t => processWithdraw(t)); }
        
        async function processWithdraw(c) {
            if(html5QrcodeScanner) html5QrcodeScanner.stop();
            if(confirm('เบิก ' + c + '?')) {
                await fetch(CFG.worker+"/api/withdraw", { method: 'POST', body: JSON.stringify({ code: c, staff_uid: profile.userId }) });
                alert('OK');
                show('view-staff');
            }
        }
        async function registerStaff() {
            await fetch(CFG.worker+"/api/register", { method: 'POST', body: JSON.stringify({ uid: profile.userId, name: document.getElementById('reg-name').value }) });
            alert('Sent');
            location.reload();
        }
        async function verifyManager() {
            const { value: p } = await Swal.fire({ title: 'Password', input: 'password' });
            if(p) {
                const r = await fetch(CFG.worker+"/api/login", { method: 'POST', body: JSON.stringify({ pass: p }) });
                const d = await r.json();
                if(d.success) { show('view-manager'); loadManagerData(); }
            }
        }
        
        function switchMgrTab(t) {
            ['stock', 'users', 'logs'].forEach(x => document.getElementById('mgr-tab-'+x).classList.add('hidden'));
            document.getElementById('mgr-tab-'+t).classList.remove('hidden');
            if(t === 'stock') loadManagerStock();
        }
        async function loadManagerStock() {
            const r = await fetch(CFG.worker+"/api/manager-stock");
            allStockData = await r.json();
            filterStock();
        }
        
        // --- MANAGER STOCK FILTER & MAGIC LINK ---
        function filterStock() {
            const t = document.getElementById('filter-brand').value;
            document.getElementById('stock-list').innerHTML = allStockData.filter(x => !t || x.item_name.includes(t)).map(x => `
                <div class="bg-white/5 p-2 rounded mb-2 flex justify-between items-center">
                    <span>${x.item_name} (${x.deposit_code})</span>
                    <button onclick="copyMagicLink('${x.deposit_code}')" class="bg-blue-500/20 text-blue-300 px-2 py-1 rounded text-xs">🔗 Link</button>
                </div>
            `).join('');
        }
        function copyMagicLink(code) {
            const link = `https://liff.line.me/${CFG.liff}?magic_code=${code}`;
            if(navigator.clipboard) {
                navigator.clipboard.writeText(link);
                Swal.fire({toast:true, position:'top', icon:'success', title:'Copied!', showConfirmButton:false, timer:1500});
            } else {
                Swal.fire("Link", link);
            }
        }

        async function loadManagerData() {
            const r = await fetch(CFG.worker+"/api/manager-list");
            const d = await r.json();
            document.getElementById('pending-list').innerHTML = d.pending.map(u => `<div>${u.name} <button onclick="staffAction('approve','${u.user_id}')">OK</button></div>`).join('');
        }
        async function staffAction(a, u) {
            await fetch(CFG.worker+"/api/staff-action", { method: 'POST', body: JSON.stringify({ action: a, uid: u }) });
            loadManagerData();
        }
        async function testNotification() {
            await fetch(CFG.worker+"/api/test-push", { method: 'POST', body: JSON.stringify({ uid: profile.userId }) });
            Swal.fire("Sent");
        }

        main();
    </script>
</body>
</html>"""

# ==============================================================================
# 2. WORKER CODE (V94.0 - FULL UNCOMPRESSED)
# ==============================================================================
WORKER_RAW = r"""
export default {
    async fetch(request, env, ctx) {
      const url = new URL(request.url);
      
      // CORS Headers
      const corsHeaders = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
      };
      
      if (request.method === "OPTIONS") {
        return new Response(null, { headers: corsHeaders });
      }
  
      // Helper Functions
      async function addLog(action, staff, details, imgKey = null) {
        try {
            await env.DB.prepare("INSERT INTO logs (action, staff_name, details, image_key) VALUES (?, ?, ?, ?)").bind(action, staff, details, imgKey).run();
        } catch(e) {}
      }
      
      async function validateStaff(uid) {
        if(!uid) return null;
        return await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ? AND status = 'active'").bind(uid).first();
      }
  
      try {
          // --- IMAGE HANDLER ---
          if (url.pathname.startsWith("/api/image/")) {
              const key = url.pathname.split('/').pop();
              const object = await env.BUCKET.get(key);
              if (!object) return new Response('Not Found', { status: 404 });
              const headers = new Headers();
              object.writeHttpMetadata(headers);
              headers.set('etag', object.httpEtag);
              return new Response(object.body, { headers });
          }

          // --- BOOKING API ---
          if (url.pathname === "/api/bookings") {
              const date = url.searchParams.get('date');
              const res = await env.DB.prepare("SELECT table_id FROM bookings WHERE date = ? AND status = 'confirmed'").bind(date).all();
              return new Response(JSON.stringify({ booked: res.results.map(r => r.table_id) }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/book" && request.method === "POST") {
              const b = await request.json();
              // Check double booking
              const ex = await env.DB.prepare("SELECT id FROM bookings WHERE date = ? AND table_id = ? AND status = 'confirmed'").bind(b.date, b.table_id).first();
              if(ex) return new Response(JSON.stringify({ success: false }), { headers: corsHeaders });
              
              await env.DB.prepare("INSERT INTO bookings (user_id, name, phone, date, time, pax, table_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed')")
                .bind(b.uid, b.name, b.phone, b.date, b.time, b.pax, b.table_id).run();
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }

          // --- WALLET API ---
          if (url.pathname === "/api/deposit" && request.method === "POST") {
              const fd = await request.formData();
              const staff = await validateStaff(fd.get('staff_uid'));
              if (!staff) return new Response(JSON.stringify({ success: false, message: "Unauthorized" }), { headers: corsHeaders });
              
              // Check duplicate code
              const ex = await env.DB.prepare("SELECT id FROM deposits WHERE deposit_code = ? AND status != 'withdrawn'").bind(fd.get('deposit_code')).first();
              if (ex) return new Response(JSON.stringify({ success: false, message: "Duplicate Code" }), { headers: corsHeaders });
              
              const fn = `dep_${Date.now()}.jpg`;
              await env.BUCKET.put(fn, fd.get('image'));
              
              const res = await env.DB.prepare(`INSERT INTO deposits (staff_name, item_name, item_type, amount, remarks, image_key, status, expiry_date, deposit_code) VALUES (?, ?, ?, ?, ?, ?, 'pending_claim', date('now', '+30 days'), ?) RETURNING id`)
                .bind(staff.name, fd.get('item_name'), fd.get('item_type'), fd.get('amount'), fd.get('remarks'), fn, fd.get('deposit_code')).first();
              
              await addLog('deposit', staff.name, `Dep: ${fd.get('item_name')}`, fn);
              return new Response(JSON.stringify({ success: true, deposit_id: res.id, code: fd.get('deposit_code') }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/claim" && request.method === "POST") {
              const b = await request.json();
              let res;
              // Magic Claim Logic: Allow status != withdrawn
              if(b.code) {
                  res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE deposit_code = ? AND status != 'withdrawn'").bind(b.uid, b.name, b.code).run();
              } else {
                  res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE id = ?").bind(b.uid, b.name, b.id).run();
              }
              return new Response(JSON.stringify({ success: res.meta.changes > 0 }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/my-wallet") {
              const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_uid = ? ORDER BY created_at DESC").bind(url.searchParams.get('uid')).all();
              return new Response(JSON.stringify(res.results), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/withdraw" && request.method === "POST") {
              const b = await request.json();
              const staff = await validateStaff(b.staff_uid);
              if (!staff) return new Response(JSON.stringify({ success: false }), { headers: corsHeaders });
              
              await env.DB.prepare("UPDATE deposits SET status = 'withdrawn' WHERE deposit_code = ?").bind(b.code).run();
              await addLog('withdraw', staff.name, `W/D Code: ${b.code}`);
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }

          // --- AUTH & MANAGER API ---
          if (url.pathname === "/api/me") {
              const u = await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ?").bind(url.searchParams.get('uid')).first();
              return new Response(JSON.stringify(u ? { role: u.role, status: u.status, name: u.name } : { role: 'customer' }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/login" && request.method === "POST") {
              const b = await request.json();
              return new Response(JSON.stringify({ success: b.pass === "__MGR_PASS__" }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/manager-list") {
              const p = await env.DB.prepare("SELECT * FROM staff_access WHERE status='pending'").all();
              const a = await env.DB.prepare("SELECT * FROM staff_access WHERE status='active'").all();
              return new Response(JSON.stringify({ pending: p.results, active: a.results }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/manager-stock") {
              const r = await env.DB.prepare("SELECT * FROM deposits WHERE status='active'").all();
              return new Response(JSON.stringify(r.results), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/logs") {
              const r = await env.DB.prepare("SELECT * FROM logs ORDER BY created_at DESC LIMIT 50").all();
              return new Response(JSON.stringify({ logs: r.results }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/staff-action" && request.method === "POST") {
              const b = await request.json();
              if (b.action === 'approve') await env.DB.prepare("UPDATE staff_access SET status='active' WHERE user_id=?").bind(b.uid).run();
              if (b.action === 'remove') await env.DB.prepare("DELETE FROM staff_access WHERE user_id=?").bind(b.uid).run();
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/register" && request.method === "POST") {
              const b = await request.json();
              await env.DB.prepare("INSERT OR IGNORE INTO staff_access (user_id, name, status) VALUES (?, ?, 'pending')").bind(b.uid, b.name).run();
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }
          
          if (url.pathname === "/api/test-push" && request.method === "POST") {
              const b = await request.json();
              await fetch("https://api.line.me/v2/bot/message/push", {
                  method: "POST",
                  headers: { "Content-Type": "application/json", "Authorization": "Bearer " + env.LINE_TOKEN },
                  body: JSON.stringify({ "to": b.uid, "messages": [{ "type": "text", "text": "🔔 Test Notification" }] })
              });
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }

      } catch(e) {
          return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders });
      }
      return new Response("API Ready", { headers: corsHeaders });
    },
    
    // CRON JOB (Auto Notify 14 Days)
    async scheduled(event, env, ctx) {
      const results = await env.DB.prepare("SELECT * FROM deposits WHERE status = 'active' AND (expiry_date = date('now', '+14 days') OR expiry_date = date('now', '+7 days'))").all();
      for (const item of results.results) {
          if (item.owner_uid) {
              await fetch("https://api.line.me/v2/bot/message/push", {
                  method: "POST",
                  headers: { "Content-Type": "application/json", "Authorization": "Bearer " + env.LINE_TOKEN },
                  body: JSON.stringify({ "to": item.owner_uid, "messages": [{ "type": "text", "text": `⚠️ รายการ ${item.item_name} จะหมดอายุในเร็วๆ นี้ กรุณามาใช้บริการ` }] })
              });
          }
      }
    }
};
"""

# ==============================================================================
# 3. PYTHON POPUP MAP EDITOR (V94.0 - Full Features)
# ==============================================================================
class MapEditorPopup(ctk.CTkToplevel):
    def __init__(self, parent, callback, initial_data=None):
        super().__init__(parent)
        self.title("Map Editor V94.0 (Full Features)")
        self.geometry("1400x900")
        self.callback = callback
        
        self.tables = []
        self.img_path = None
        self.tk_image = None
        self.img_width = 800
        self.img_height = 600
        self.table_radius = 20
        self.mode = "EDIT"
        self.edit_tool = "VIEW"
        self.selected_table = None
        self.align_ref = None
        self.sim_selected = []
        self.sim_required_tables = 1

        self.setup_ui()
        
        if initial_data and initial_data.get('url'):
            self.lbl_status.configure(text=f"Loaded Map URL: {initial_data['url']}")
            if initial_data.get('tables'):
                self.tables = initial_data['tables']
                self.redraw()

    def setup_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="📐 MAP EDITOR", font=("Arial", 24, "bold")).pack(pady=(20,10))
        
        # Mode Switch
        self.mode_seg = ctk.CTkSegmentedButton(self.sidebar, values=["🛠️ EDIT MODE", "🧪 TEST SIM"], command=self.switch_mode)
        self.mode_seg.set("🛠️ EDIT MODE")
        self.mode_seg.pack(padx=10, pady=10, fill="x")

        # --- EDIT TOOLS ---
        self.frame_edit = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_edit.pack(fill="x", padx=10)
        
        ctk.CTkButton(self.frame_edit, text="📂 Load BG Image", command=self.load_image).pack(fill="x", pady=5)
        self.ent_url = ctk.CTkEntry(self.frame_edit, placeholder_text="Web Image URL"); self.ent_url.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.frame_edit, text="Table Size:", anchor="w").pack(fill="x", pady=(10,0))
        self.slider_size = ctk.CTkSlider(self.frame_edit, from_=10, to=60, number_of_steps=50, command=self.update_table_size)
        self.slider_size.set(20)
        self.slider_size.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.frame_edit, text="Tools:", anchor="w").pack(fill="x", pady=(10,0))
        self.btn_add = ctk.CTkButton(self.frame_edit, text="➕ Place Table", command=lambda: self.set_tool("ADD"))
        self.btn_add.pack(fill="x", pady=2)
        self.btn_link = ctk.CTkButton(self.frame_edit, text="🔗 Link Tables", command=lambda: self.set_tool("LINK"))
        self.btn_link.pack(fill="x", pady=2)
        self.btn_del = ctk.CTkButton(self.frame_edit, text="❌ Delete", command=lambda: self.set_tool("DELETE"), fg_color="#ef4444")
        self.btn_del.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.frame_edit, text="Alignment:", anchor="w").pack(fill="x", pady=(10,0))
        self.btn_align_h = ctk.CTkButton(self.frame_edit, text="↔️ Align H", command=lambda: self.set_tool("ALIGN_H"))
        self.btn_align_h.pack(fill="x", pady=2)
        self.btn_align_v = ctk.CTkButton(self.frame_edit, text="↕️ Align V", command=lambda: self.set_tool("ALIGN_V"))
        self.btn_align_v.pack(fill="x", pady=2)

        # --- SIM TOOLS ---
        self.frame_test = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        ctk.CTkLabel(self.frame_test, text="Simulation Pax:").pack()
        self.ent_pax = ctk.CTkEntry(self.frame_test, placeholder_text="1")
        self.ent_pax.pack(fill="x", pady=5)
        ctk.CTkButton(self.frame_test, text="Set Pax", command=self.update_sim_req).pack(fill="x")
        self.lbl_req = ctk.CTkLabel(self.frame_test, text="Required: 1 Table", font=("Arial", 16, "bold"), text_color="#EAB308")
        self.lbl_req.pack(pady=10)
        self.lbl_sim_msg = ctk.CTkLabel(self.frame_test, text="Ready", wraplength=200)
        self.lbl_sim_msg.pack()

        # Footer
        ctk.CTkButton(self.sidebar, text="💾 SAVE & CLOSE", command=self.save_and_close, fg_color="#10b981", height=40).pack(side="bottom", fill="x", padx=10, pady=20)
        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Ready", text_color="gray"); self.lbl_status.pack(side="bottom")

        # Canvas
        self.canvas = tk.Canvas(self, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def switch_mode(self, val):
        if "EDIT" in val:
            self.mode="EDIT"; self.frame_test.pack_forget(); self.frame_edit.pack(fill="x", padx=10); self.set_tool("VIEW")
        else:
            self.mode="TEST"; self.frame_edit.pack_forget(); self.frame_test.pack(fill="x", padx=10); self.sim_selected=[]
        self.redraw()

    def set_tool(self, t):
        self.edit_tool = t
        self.selected_table = None
        self.align_ref = None
        self.lbl_status.configure(text=f"Tool: {t}")
        # Reset Button Colors
        for b in [self.btn_add, self.btn_link, self.btn_del, self.btn_align_h, self.btn_align_v]: b.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        if t=="DELETE": self.btn_del.configure(fg_color="#991b1b")

    def update_table_size(self, val): self.table_radius = int(val); self.redraw()

    def update_sim_req(self):
        try:
            pax = int(self.ent_pax.get())
            self.sim_required_tables = math.ceil(pax/4)
            self.lbl_req.configure(text=f"Required: {self.sim_required_tables} Tables")
            self.sim_selected = []
            self.redraw()
        except: pass

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            pil_img = Image.open(path); base_h = 800; w_pct = (base_h / float(pil_img.size[1])); w_size = int((float(pil_img.size[0]) * float(w_pct)))
            pil_img = pil_img.resize((w_size, base_h), Image.Resampling.LANCZOS)
            self.img_width, self.img_height = w_size, base_h; self.tk_image = ImageTk.PhotoImage(pil_img); self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        if self.tk_image: self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw"); self.canvas.config(scrollregion=(0,0,self.img_width,self.img_height))
        else: self.canvas.create_text(400,300, text="Load Image First", fill="gray", font=("Arial", 20))
        
        # Links
        for t in self.tables:
            for n_id in t.get('neighbors', []):
                target = next((x for x in self.tables if x['id'] == n_id), None)
                if target:
                    color = "#EAB308" if (self.mode=="TEST" and t['id'] in self.sim_selected and target['id'] in self.sim_selected) else "#fbbf24"
                    width = 5 if (self.mode=="TEST" and t['id'] in self.sim_selected and target['id'] in self.sim_selected) else 1
                    self.canvas.create_line(t['x'], t['y'], target['x'], target['y'], fill=color, width=width, dash=(4,2) if width==1 else None)

        r = self.table_radius
        for t in self.tables:
            fill = "#3b82f6"
            outline = "white"
            if self.mode == "EDIT":
                if self.selected_table == t: fill="#ef4444"
                if self.align_ref == t: outline="#22d3ee"; fill="#06b6d4"
            elif self.mode == "TEST":
                if t['id'] in self.sim_selected: fill="#EAB308"
            
            self.canvas.create_oval(t['x']-r, t['y']-r, t['x']+r, t['y']+r, fill=fill, outline=outline, width=2)
            self.canvas.create_text(t['x'], t['y'], text=t['id'], fill="white", font=("Arial", max(10, int(r*0.6)), "bold"))

    def on_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        clicked = next((t for t in self.tables if (t['x']-25 < x < t['x']+25) and (t['y']-25 < y < t['y']+25)), None)
        
        if self.mode == "EDIT":
            if self.edit_tool == "ADD" and not clicked:
                tid = simpledialog.askstring("ID", "Table Name:")
                if tid: self.tables.append({"id": tid, "x": x, "y": y, "neighbors": []})
            elif self.edit_tool == "DELETE" and clicked:
                self.tables.remove(clicked)
                for t in self.tables: 
                    if clicked['id'] in t.get('neighbors',[]): t['neighbors'].remove(clicked['id'])
            elif self.edit_tool == "LINK" and clicked:
                if not self.selected_table: self.selected_table = clicked
                else:
                    if self.selected_table != clicked:
                        if clicked['id'] not in self.selected_table.get('neighbors',[]): 
                            if 'neighbors' not in self.selected_table: self.selected_table['neighbors'] = []
                            self.selected_table['neighbors'].append(clicked['id'])
                        if self.selected_table['id'] not in clicked.get('neighbors',[]):
                            if 'neighbors' not in clicked: clicked['neighbors'] = []
                            clicked['neighbors'].append(self.selected_table['id'])
                    self.selected_table = None
            elif self.edit_tool in ["ALIGN_H", "ALIGN_V"] and clicked:
                if not self.align_ref: self.align_ref = clicked
                else:
                    if self.edit_tool == "ALIGN_H": clicked['y'] = self.align_ref['y']
                    else: clicked['x'] = self.align_ref['x']
                    self.align_ref = None
        else:
            if clicked:
                # Sim Logic
                if clicked['id'] in self.sim_selected: self.sim_selected = []
                else:
                    if len(self.sim_selected) > 0:
                        last = next((t for t in self.tables if t['id'] == self.sim_selected[-1]), None)
                        if last and clicked['id'] in last.get('neighbors',[]): self.sim_selected.append(clicked['id'])
                        else: self.lbl_sim_msg.configure(text="❌ ต้องเลือกโต๊ะที่เชื่อมกัน", text_color="red")
                    else: self.sim_selected.append(clicked['id'])
                
                if len(self.sim_selected) == self.sim_required_tables: self.lbl_sim_msg.configure(text="✅ ครบแล้ว", text_color="green")
        
        self.redraw()

    def on_drag(self, event):
        if self.mode == "EDIT" and self.edit_tool == "VIEW":
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            clicked = next((t for t in self.tables if (t['x']-25 < x < t['x']+25) and (t['y']-25 < y < t['y']+25)), None)
            if clicked: clicked['x'] = x; clicked['y'] = y; self.redraw()

    def save_and_close(self):
        url = self.ent_url.get()
        if not url: messagebox.showwarning("Warning", "อย่าลืมใส่ Map Image URL สำหรับเว็บ")
        self.callback({"url": url, "tables": self.tables})
        self.destroy()

# ==============================================================================
# 4. APP GENERATOR (MAIN UI - V85.6 Logic + V93 Layouts)
# ==============================================================================
class AppGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nightlife System V94.0 (Ultimate Full)")
        self.geometry("1200x850")
        self.profiles = {}
        self.profile_file = "profiles.json"
        self.map_data = {}
        
        self.vars = { 
            'bg_color': '#0f172a', 'grad_start': '#0e4296', 'grad_end': '#1e293b', 
            'text_main': '#ffffff', 'text_sub': '#94a3b8', 'accent': '#EAB308', 
            'radius': '16px' 
        }
        
        # --- ALL 9 LAYOUTS RESTORED ---
        self.LAYOUTS = {
            "Standard (Default)": "", 
            "Grid (2 Columns)": ".menu-layout { display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 15px !important; } .btn-menu { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; padding: 20px !important; text-align: center !important; margin-bottom: 0 !important; height: auto !important; aspect-ratio: 1/1 !important; }",
            "List View (Horizontal)": ".menu-layout { display: flex !important; flex-direction: column !important; gap: 10px !important; } .btn-menu { flex-direction: row !important; align-items: center !important; justify-content: flex-start !important; padding: 15px 25px !important; text-align: left !important; height: auto !important; min-height: 80px !important; } .icon { margin-bottom: 0 !important; margin-right: 20px !important; font-size: 30px !important; } .label { font-size: 18px !important; } .sub-label { display: none !important; }",
            "Modern Card (Floating)": ".btn-menu { background: rgba(255, 255, 255, 0.05) !important; border: none !important; box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important; border-radius: 24px !important; transform: translateY(0); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); } .btn-menu:active { transform: scale(0.95); }",
            "Glassmorphism (Blur)": ".btn-menu { background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1) !important; }",
            "Neumorphism (Soft UI)": ".btn-menu { background: var(--bg-color) !important; border-radius: 30px !important; box-shadow: 20px 20px 60px #0a0a0a, -20px -20px 60px #1f1f1f !important; border: none !important; } .label { color: var(--text-main) !important; text-shadow: none !important; }",
            "Cyberpunk (Neon)": ".btn-menu { background: #000 !important; border: 2px solid var(--accent) !important; box-shadow: 0 0 15px var(--accent), inset 0 0 15px var(--accent) !important; border-radius: 0 !important; clip-path: polygon(10% 0, 100% 0, 100% 90%, 90% 100%, 0 100%, 0 10%); } .label { font-family: 'Courier New', monospace !important; letter-spacing: 2px !important; }",
            "Minimalist (Clean)": ".btn-menu { background: transparent !important; border: 1px solid rgba(255,255,255,0.2) !important; box-shadow: none !important; } .btn-menu:hover { background: rgba(255,255,255,0.05) !important; border-color: var(--text-main) !important; }",
            "Compact (Small Rows)": ".menu-layout { gap: 8px !important; } .btn-menu { padding: 15px !important; margin-bottom: 0 !important; flex-direction: row !important; justify-content: space-between !important; min-height: 60px !important; } .icon { font-size: 24px !important; margin-bottom: 0 !important; } .label { font-size: 16px !important; } .sub-label { display: none !important; }"
        }
        self.default_bk = """✨ Booking Confirmed ✨\nร้าน: {shop}\nชื่อ: {name}\nวันที่: {date} {time}\nจำนวน: {pax} คน\n*มาก่อน {hold}"""
        
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=2); self.grid_rowconfigure(0, weight=1)
        self.load_profiles(); self.setup_ui(); self.update_preview()

    def load_profiles(self):
        if os.path.exists(self.profile_file):
            try: self.profiles = json.load(open(self.profile_file, encoding='utf-8'))
            except: self.profiles = {}
    def save_profiles(self): json.dump(self.profiles, open(self.profile_file, "w", encoding='utf-8'), indent=4)

    def setup_ui(self):
        left = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent"); left.grid(row=0, column=0, sticky="nsew")
        
        # Profile
        pf = ctk.CTkFrame(left, fg_color="#1e293b"); pf.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(pf, text="📂 Profile").pack()
        self.combo_pro = ctk.CTkComboBox(pf, values=list(self.profiles.keys()), command=self.load_pro); self.combo_pro.pack(fill="x", padx=10, pady=5)
        btn_r = ctk.CTkFrame(pf, fg_color="transparent"); btn_r.pack()
        ctk.CTkButton(btn_r, text="Save", width=60, command=self.save_pro, fg_color="#10B981").pack(side="left", padx=2)
        ctk.CTkButton(btn_r, text="Del", width=60, command=self.del_pro, fg_color="#EF4444").pack(side="left", padx=2)

        self.scroll = ctk.CTkScrollableFrame(left, fg_color="transparent"); self.scroll.pack(fill="both", expand=True)
        self.entries = {}
        for k in ["Shop Name", "LIFF ID", "Worker URL", "Manager Password", "R2 Public URL", "Channel Access Token", "D1 Database ID", "Hold Table Time"]:
            ctk.CTkLabel(self.scroll, text=k).pack(anchor="w", padx=20); e = ctk.CTkEntry(self.scroll); e.pack(fill="x", padx=20); self.entries[k] = e
            if k == "Shop Name": e.bind("<KeyRelease>", self.update_preview_text)

        ctk.CTkLabel(self.scroll, text="Booking Mode", text_color="#EAB308").pack(pady=(15,0))
        self.bk_mode = ctk.CTkComboBox(self.scroll, values=["Standard", "Map"]); self.bk_mode.set("Map"); self.bk_mode.pack(fill="x", padx=20)
        ctk.CTkButton(self.scroll, text="🗺️ EDIT MAP", command=self.open_map, fg_color="#3b82f6").pack(fill="x", padx=20, pady=5)
        self.lbl_map = ctk.CTkLabel(self.scroll, text="No Data", text_color="gray"); self.lbl_map.pack()

        ctk.CTkLabel(self.scroll, text="Theme").pack(pady=(10,0))
        c_grid = ctk.CTkFrame(self.scroll); c_grid.pack(fill="x", padx=20)
        self.create_cbtn(c_grid, "BG", 'bg_color', 0); self.create_cbtn(c_grid, "G1", 'grad_start', 1); self.create_cbtn(c_grid, "G2", 'grad_end', 2); self.create_cbtn(c_grid, "Acc", 'accent', 3)
        
        ctk.CTkLabel(self.scroll, text="Layout Style").pack(pady=(10,0))
        self.combo_layout = ctk.CTkComboBox(self.scroll, values=list(self.LAYOUTS.keys()), command=self.update_preview); self.combo_layout.pack(fill="x", padx=20)
        
        ctk.CTkButton(left, text="GENERATE", command=self.build, height=50, fg_color="#10B981").pack(fill="x", padx=20, pady=20)
        
        # PREVIEW AREA
        self.preview = ctk.CTkFrame(self, fg_color="#000"); self.preview.grid(row=0, column=1, sticky="nsew")
        self.phone = ctk.CTkFrame(self.preview, width=375, height=667, corner_radius=30, fg_color="#ffffff"); self.phone.place(relx=0.5, rely=0.5, anchor="center")
        self.phone.pack_propagate(False)
        self.p_head = ctk.CTkLabel(self.phone, text="SHOP NAME", font=("Arial", 20, "bold")); self.p_head.pack(pady=(40,20))
        self.p_con = ctk.CTkFrame(self.phone, fg_color="transparent"); self.p_con.pack(fill="both", expand=True, padx=20)

    def create_cbtn(self, p, l, k, c): 
        b = ctk.CTkButton(p, text="", width=40, height=20, fg_color=self.vars[k], command=lambda: self.pick_c(k))
        b.grid(row=0, column=c, padx=2, pady=2); setattr(self, f"btn_{k}", b)
    def pick_c(self, k): 
        c = colorchooser.askcolor(self.vars[k])[1]
        if c: self.vars[k] = c; getattr(self, f"btn_{k}").configure(fg_color=c); self.update_preview()

    def update_preview(self, e=None):
        self.phone.configure(fg_color=self.vars['bg_color']); self.p_head.configure(text_color=self.vars['text_main'])
        for w in self.p_con.winfo_children(): w.destroy()
        
        # Re-create mock buttons based on layout
        layout = self.combo_layout.get()
        is_grid = "Grid" in layout
        is_list = "List" in layout or "Compact" in layout
        
        if is_grid:
            self.p_con.grid_columnconfigure(0, weight=1); self.p_con.grid_columnconfigure(1, weight=1)
            self.mock_btn(0, 0, "Booking", "grid"); self.mock_btn(0, 1, "Wallet", "grid")
        elif is_list:
            self.mock_btn(0, 0, "Booking", "list"); self.mock_btn(1, 0, "Wallet", "list")
        else: # Standard
            self.mock_btn(0, 0, "Booking", "std"); self.mock_btn(1, 0, "Wallet", "std")

    def mock_btn(self, r, c, txt, mode):
        # Simulate Gradient using single color for preview simplicity
        color = self.vars['grad_start']
        btn = ctk.CTkFrame(self.p_con, fg_color=color, corner_radius=16)
        
        if mode == "grid":
            btn.configure(height=100)
            btn.grid(row=r, column=c, sticky="ew", padx=5, pady=5)
            ctk.CTkLabel(btn, text="📅", font=("Arial", 30)).pack(pady=(10,0))
            ctk.CTkLabel(btn, text=txt, text_color="white", font=("Arial", 14, "bold")).pack()
        elif mode == "list":
            btn.configure(height=60)
            btn.pack(fill="x", pady=5)
            # Row layout simulation
            icon = ctk.CTkLabel(btn, text="📅", font=("Arial", 20)); icon.place(relx=0.1, rely=0.5, anchor="center")
            lbl = ctk.CTkLabel(btn, text=txt, text_color="white", font=("Arial", 16, "bold")); lbl.place(relx=0.3, rely=0.5, anchor="w")
        else: # Std
            btn.configure(height=100)
            btn.pack(fill="x", pady=5)
            ctk.CTkLabel(btn, text="📅", font=("Arial", 30)).pack(pady=(10,0))
            ctk.CTkLabel(btn, text=txt, text_color="white", font=("Arial", 18, "bold")).pack()

    def update_preview_text(self, e): self.p_head.configure(text=self.entries["Shop Name"].get())
    
    def open_map(self): MapEditorPopup(self, self.on_map_save, self.map_data)
    def on_map_save(self, d): self.map_data = d; self.lbl_map.configure(text=f"OK ({len(d.get('tables',[]))})", text_color="green")
    
    def save_pro(self):
        n = self.entries["Shop Name"].get()
        if n: 
            d = {k:v.get() for k,v in self.entries.items()}
            d.update({'colors':self.vars, 'layout':self.combo_layout.get(), 'bk_mode':self.bk_mode.get(), 'map':self.map_data})
            self.profiles[n] = d; self.save_profiles(); self.combo_profiles.configure(values=list(self.profiles.keys())); self.combo_profiles.set(n); messagebox.showinfo("Saved", "OK")
    
    def load_pro(self, n):
        if n in self.profiles:
            d = self.profiles[n]
            for k,v in d.items(): 
                if k in self.entries: self.entries[k].delete(0, "end"); self.entries[k].insert(0, v)
            if 'colors' in d: self.vars.update(d['colors']); self.update_preview()
            if 'map' in d: self.on_map_save(d['map'])
            if 'layout' in d: self.combo_layout.set(d['layout']); self.update_preview()
            if 'bk_mode' in d: self.bk_mode.set(d['bk_mode'])
            
    def del_pro(self):
        if self.combo_profiles.get() in self.profiles: del self.profiles[self.combo_profiles.get()]; self.save_profiles(); self.combo_profiles.set(""); self.load_profiles()

    def build(self):
        shop = self.entries["Shop Name"].get()
        if not shop: return messagebox.showerror("Error", "Shop Name Required")
        map_json = json.dumps(self.map_data); map_img = self.map_data.get('url', ''); bk_m = "map" if self.bk_mode.get() == "Map" else "std"
        
        html = HTML_RAW
        for k, v in [("__SHOP__", shop), ("__BG_COLOR__", self.vars['bg_color']), ("__GRAD_START__", self.vars['grad_start']), ("__GRAD_END__", self.vars['grad_end']), ("__TEXT_MAIN__", self.vars['text_main']), ("__TEXT_SUB__", self.vars['text_sub']), ("__ACCENT__", self.vars['accent']), ("__RADIUS__", self.vars['radius']), ("__LIFF__", self.entries["LIFF ID"].get()), ("__WORKER__", self.entries["Worker URL"].get()), ("__R2_URL__", self.entries["R2 Public URL"].get()), ("__HOLD_TIME__", self.entries["Hold Table Time"].get()), ("__LAYOUT_CSS__", self.LAYOUTS.get(self.combo_layout.get(), "")), ("__BK_MSG__", json.dumps(self.default_bk)), ("__MAP_JSON__", map_json), ("__MAP_IMG__", map_img), ("__BK_MODE__", bk_m)]: 
            html = html.replace(k, v)
        
        worker = WORKER_RAW.replace("__MGR_PASS__", self.entries["Manager Password"].get()).replace("__LIFF__", self.entries["LIFF ID"].get())
        folder = f"Output_{shop.replace(' ', '_')}"
        if not os.path.exists(folder): os.makedirs(folder)
        
        with open(f"{folder}/index.html", "w", encoding="utf-8") as f: f.write(html)
        with open(f"{folder}/worker.js", "w", encoding="utf-8") as f: f.write(worker)
        with open(f"{folder}/wrangler.toml", "w", encoding="utf-8") as f: f.write(f"""name = "nightlife-app"\nmain = "worker.js"\ncompatibility_date = "2023-10-30"\n\n[vars]\nLINE_TOKEN = "{self.entries["Channel Access Token"].get()}"\n\n[[d1_databases]]\nbinding = "DB"\ndatabase_name = "nightlife-db"\ndatabase_id = "{self.entries["D1 Database ID"].get()}"\n\n[[r2_buckets]]\nbinding = "BUCKET"\nbucket_name = "nightlife-bucket"\n\n[triggers]\ncrons = ["0 3 * * *"]""")
        with open(f"{folder}/d1_schema.sql", "w", encoding="utf-8") as f: f.write("""CREATE TABLE IF NOT EXISTS staff_access (user_id TEXT PRIMARY KEY, name TEXT, status TEXT DEFAULT 'pending', role TEXT DEFAULT 'staff', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\nCREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, deposit_code TEXT, staff_name TEXT, item_name TEXT, item_type TEXT, amount TEXT, remarks TEXT, image_key TEXT, status TEXT, expiry_date TEXT, owner_uid TEXT, owner_name TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\nCREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, staff_name TEXT, details TEXT, image_key TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\nCREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, name TEXT, phone TEXT, date TEXT, time TEXT, pax INTEGER, table_id TEXT, status TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\nCREATE INDEX IF NOT EXISTS idx_deposit_code ON deposits(deposit_code);\nCREATE INDEX IF NOT EXISTS idx_owner_uid ON deposits(owner_uid);\nCREATE INDEX IF NOT EXISTS idx_status ON deposits(status);""")
        
        messagebox.showinfo("Success", f"V94 Generated!\nFolder: {folder}")
        webbrowser.open(folder)

if __name__ == "__main__": app = AppGenerator(); app.mainloop()