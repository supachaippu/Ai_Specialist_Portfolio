import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox
import os
import json
import webbrowser
import random
import colorsys

# ==============================================================================
# 1. HTML TEMPLATE (V85.7 - Added Booking Toggle)
# ==============================================================================
HTML_RAW = r"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>__SHOP__</title>
    
    <link rel="preconnect" href="https://static.line-scdn.net">
    <link rel="preconnect" href="https://cdn.tailwindcss.com">
    <link rel="preconnect" href="https://cdnjs.cloudflare.com">
    <link rel="preconnect" href="https://unpkg.com">
    <link rel="preconnect" href="https://cdn.jsdelivr.net">

    <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: __BG_COLOR__;
            --grad-start: __GRAD_START__;
            --grad-end: __GRAD_END__;
            --text-main: __TEXT_MAIN__;
            --text-sub: __TEXT_SUB__;
            --accent: __ACCENT__;
        }

        body { font-family: 'Prompt', sans-serif; background-color: var(--bg-color); color: var(--text-main); height: 100dvh; width: 100vw; overflow: hidden; display: flex; flex-direction: column; margin: 0; padding: 0; }
        .main-container { padding: 20px; width: 100%; max-width: 448px; margin: 0 auto; height: 100%; display: flex; flex-direction: column; position: relative; overflow-y: auto; }
        .header-section { flex: 0 0 auto; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-start; }
        #view-customer { flex: 1; display: flex; flex-direction: column; justify-content: center; padding-bottom: 60px; }
        #view-staff, #view-wallet, #view-booking, #view-manager { flex: 1; display: flex; flex-direction: column; }
        .hidden { display: none !important; }

        .btn-menu { background: linear-gradient(145deg, var(--grad-start), var(--grad-end)); border: 1px solid rgba(255,255,255,0.1); border-radius: __RADIUS__; box-shadow: 0 8px 15px -3px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.2); padding: 25px 15px; margin-bottom: 15px; text-align: center; cursor: pointer; transition: all 0.2s; text-decoration: none; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; position: relative; backdrop-filter: blur(5px); flex-grow: 1; max-height: 140px; }
        .btn-menu:active { transform: scale(0.98); }
        .btn-menu:hover { box-shadow: 0 10px 20px -5px rgba(0,0,0,0.5); transform: translateY(-2px); border-color: var(--accent); }
        .btn-menu.disabled { filter: grayscale(100%); opacity: 0.6; cursor: not-allowed; }

        .icon { font-size: 36px; margin-bottom: 8px; display: block; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); }
        .label { font-size: 18px; font-weight: 600; display: block; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .sub-label { font-size: 12px; color: rgba(255,255,255,0.8); display: block; margin-top: 2px; font-weight: 300; }

        .staff-zone { display: none; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; }
        .glass-input { background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 12px; width: 100%; color: var(--text-main); outline: none; margin-bottom: 10px; font-size: 16px; box-sizing: border-box; }
        .glass-input:focus { border-color: var(--accent); background: rgba(0,0,0,0.4); box-shadow: 0 0 0 1px var(--accent); }
        .glass-input::placeholder { color: var(--text-sub); opacity: 0.6; }

        .btn-action { background: linear-gradient(90deg, var(--grad-start), var(--grad-end)); color: white; font-weight: bold; padding: 14px; border-radius: 16px; width: 100%; border: none; font-size: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; letter-spacing: 1px; }
        .lang-select { background: rgba(255,255,255,0.05); color: var(--text-sub); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 4px 10px; font-size: 11px; outline: none; margin-left: auto; }
        .lang-select option { background: var(--bg-color); color: var(--text-main); }
        
        #wallet-active, #wallet-history, #stock-list { max-height: 50vh; overflow-y: auto; padding-right: 5px; }
        .profile-container { display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }

        .swal2-popup { background: var(--bg-color) !important; border: 1px solid rgba(255,255,255,0.1); border-radius: 24px !important; color: var(--text-main) !important; }
        .swal2-title { color: var(--text-main) !important; font-family: 'Prompt', sans-serif; }
        .swal2-confirm { background: linear-gradient(90deg, var(--grad-start), var(--grad-end)) !important; }
        .swal2-cancel { background-color: #334155 !important; }

        .btn-refresh-pill { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: var(--text-main); padding: 6px 12px; border-radius: 50px; font-size: 12px; display: flex; align-items: center; gap: 6px; cursor: pointer; transition: all 0.3s; }
        .btn-refresh-pill:hover { background: rgba(255,255,255,0.2); border-color: var(--accent); }
        .spin-anim { animation: spin 1s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        
        .file-upload { border: 2px dashed rgba(255,255,255,0.2); border-radius: 20px; padding: 0; text-align: center; margin-bottom: 15px; cursor: pointer; transition: all 0.3s; background: rgba(255,255,255,0.02); width: 100%; height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden; box-sizing: border-box; position: relative; }
        .file-upload:hover { background: rgba(255,255,255,0.05); border-color: var(--accent); }
        .file-upload.has-img { border-style: solid; border-color: var(--accent); padding: 0; }
        .preview-img { width: 100%; height: 100%; object-fit: cover; position: absolute; top:0; left:0; }
        
        .type-btn { flex: 1; padding: 14px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); color: var(--text-sub); transition: all 0.2s; font-weight: normal; }
        .type-btn.active { background: linear-gradient(135deg, var(--grad-start), var(--grad-end)); color: white; font-weight: bold; border: 1px solid var(--accent); box-shadow: 0 0 15px rgba(255,255,255,0.1); }

        .code-display-box { background: rgba(255,255,255,0.05); border: 1px solid var(--accent); border-radius: 16px; padding: 15px; text-align: center; margin-bottom: 15px; animation: fadeIn 0.5s ease; width: 100%; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; }
        .code-label { font-size: 12px; color: var(--text-sub); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
        .code-row { display: flex; align-items: center; gap: 10px; }
        .code-value { font-size: 42px; font-weight: bold; color: var(--accent); font-family: monospace; letter-spacing: 3px; text-shadow: 0 0 10px rgba(0,0,0,0.5); }
        .btn-refresh-code { background: rgba(255,255,255,0.1); border: none; color: white; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .btn-refresh-code:hover { background: rgba(255,255,255,0.2); transform: rotate(180deg); }

        /* Toggle Switch */
        .toggle-checkbox { display: none; }
        .toggle-label { width: 50px; height: 28px; background: #334155; border-radius: 100px; position: relative; cursor: pointer; transition: 0.3s; border: 1px solid rgba(255,255,255,0.1); }
        .toggle-label::after { content: ''; position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; border-radius: 50%; background: #fff; transition: 0.3s; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .toggle-checkbox:checked + .toggle-label { background: var(--accent); }
        .toggle-checkbox:checked + .toggle-label::after { transform: translateX(22px); }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

        __LAYOUT_CSS__
    </style>
</head>
<body>
    <div class="main-container">
        <div id="loading" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 backdrop-blur-sm"><div class="animate-spin rounded-full h-12 w-12 border-4 border-t-transparent" style="border-color: var(--accent);"></div><p class="mt-4 text-sm" style="color: var(--text-sub);">Loading...</p></div>

        <div class="header-section">
            <div onclick="secretTap()" class="flex-1 text-left"><h1 class="text-2xl font-bold mb-0 tracking-tight" style="color: var(--text-main); text-shadow: 0 0 10px rgba(255,255,255,0.1);">__SHOP__</h1><p class="text-[10px] uppercase tracking-widest font-semibold opacity-70" style="color: var(--accent);">Nightlife System</p></div>
            <div class="flex flex-col gap-1 items-end">
                <div class="flex gap-2">
                    <select id="lang-switch" class="lang-select" onchange="changeLang(this.value)"><option value="th">🇹🇭 TH</option><option value="en">🇬🇧 EN</option><option value="cn">🇨🇳 CN</option></select>
                    <button id="btn-staff-switch" onclick="toggleStaffMode()" class="hidden text-[10px] bg-white/10 px-2 py-1 rounded-full border border-white/5 text-gray-300 flex items-center gap-1"><span>🔄</span> <span id="staff-mode-text">Staff</span></button>
                    <button onclick="verifyManager()" class="opacity-30 hover:opacity-100 text-sm transition-opacity">⚙️</button>
                </div>
            </div>
        </div>

        <div id="view-customer" class="hidden animate-fade-in">
             <div class="profile-container"><div class="inline-block p-1 rounded-full border-2 mb-2 shadow-lg" style="border-color: var(--accent);"><img id="user-img" class="w-16 h-16 rounded-full" src=""></div><h2 id="user-name" class="text-xl font-bold" style="color: var(--text-main);">Guest</h2><p class="text-xs font-light" data-i18n="welcome" style="color: var(--text-sub);">ยินดีต้อนรับ กรุณาเลือกบริการ</p></div>
             <div id="menu-container" class="menu-layout w-full pb-4">
                <div id="menu-booking-btn" onclick="checkAndOpenBooking()" class="btn-menu menu-item-1"><span class="icon">📅</span><span class="label" data-i18n="menu_booking">จองโต๊ะ</span><span class="sub-label" data-i18n="menu_booking_sub">สำรองที่นั่งล่วงหน้า</span></div>
                <div onclick="show('view-wallet'); startWalletSync();" class="btn-menu menu-item-2"><span class="icon">🥃</span><span class="label" data-i18n="menu_wallet">ระบบฝากเหล้า</span><span class="sub-label" data-i18n="menu_wallet_sub">เช็ครายการฝาก / เบิกเหล้า / โอนสิทธิ์</span></div>
             </div>
        </div>

        <div id="view-staff" class="hidden">
            <div class="staff-zone flex-1" style="display:flex !important; flex-direction: column;">
                <div style="text-align: center; margin-bottom: 15px;"><span style="color:var(--accent); font-weight:bold; font-size:10px; letter-spacing:2px; text-transform:uppercase; background:rgba(255,255,255,0.05); padding:6px 12px; border-radius: 100px; border:1px solid rgba(255,255,255,0.1);">STAFF ACCESS</span></div>
                <div class="flex flex-col gap-4 flex-1 justify-center">
                    <div onclick="openDepositFlow()" class="btn-menu" style="background: rgba(255,255,255,0.05) !important; border-color: rgba(255,255,255,0.1) !important; flex:1; max-height:none;"><span class="icon" style="font-size: 32px !important;">📥</span><span class="label" style="font-size: 18px !important;">รับฝาก</span></div>
                    <div onclick="openWithdrawScanner()" class="btn-menu" style="background: rgba(220, 38, 38, 0.15) !important; border-color: rgba(239, 68, 68, 0.2) !important; box-shadow: none !important; flex:1; max-height:none;"><span class="icon" style="font-size: 32px !important;">📤</span><span class="label" style="font-size: 18px !important; color: #fca5a5 !important;">เบิกออก</span></div>
                </div>
            </div>
        </div>

        <div id="view-wallet" class="hidden h-full flex flex-col">
            <div class="flex justify-between mb-4 items-center shrink-0">
                <button onclick="stopWalletSync(); show('view-customer')" class="text-xs flex items-center gap-1 opacity-70 hover:opacity-100 transition" style="color: var(--text-main);">← <span data-i18n="back">กลับ</span></button>
                <div class="flex gap-2"><button id="btn-wallet-refresh" onclick="manualWalletRefresh()" class="btn-refresh-pill"><span id="icon-refresh" style="font-size:14px;">↻</span> อัพเดทสถานะ</button></div>
            </div>
            <div class="flex justify-between items-end mb-4 shrink-0">
                <h2 class="text-xl font-bold" data-i18n="wallet_title" style="color: var(--text-main);">🍾 My Collection</h2>
                <button onclick="manualClaimInput()" class="text-[10px] px-3 py-1 rounded-full font-bold shadow-lg mb-1" style="background: linear-gradient(90deg, var(--grad-start), var(--grad-end)); color: white;" data-i18n="btn_manual_code">🔑 กรอกรหัส</button>
            </div>
            <div class="flex-1 overflow-y-auto pr-1">
                <div class="text-[10px] font-bold uppercase tracking-wider border-b border-white/10 pb-2 mb-3" style="color: var(--accent);" data-i18n="wallet_active">📦 รายการคงเหลือ (Active)</div>
                <div id="wallet-active" class="space-y-3 pb-4 min-h-[50px]"></div>
                <div class="text-[10px] font-bold uppercase tracking-wider border-b border-white/10 pb-2 mb-3 mt-6" data-i18n="wallet_history" style="color: var(--text-sub);">🕒 ประวัติการเบิก (History)</div>
                <div id="wallet-history" class="space-y-2 pb-10 opacity-60"></div>
            </div>
        </div>

        <div id="view-booking" class="hidden">
            <div class="flex justify-between mb-6 items-center"><h2 class="text-xl font-bold" data-i18n="bk_title" style="color: var(--text-main);">📝 จองโต๊ะ</h2><button onclick="show('view-customer')" style="color: var(--text-sub);" class="text-2xl hover:text-white transition">×</button></div>
            <div class="bg-white/5 p-5 rounded-3xl border border-white/10 space-y-4 shadow-xl backdrop-blur-sm">
                <input type="text" id="bk-name" placeholder="ชื่อผู้จอง" class="glass-input" data-i18n-ph="ph_name"><input type="tel" id="bk-phone" placeholder="เบอร์โทรติดต่อ" class="glass-input" data-i18n-ph="ph_phone">
                <div class="flex gap-3"><input type="date" id="bk-date" class="glass-input"><input type="time" id="bk-time" value="20:00" class="glass-input"></div>
                <p id="date-display" class="text-xs text-right mt-[-8px] mb-2 font-mono" style="color: var(--accent);"></p>
                <input type="text" id="bk-pax" placeholder="จำนวนคน (เช่น 5 คน)" class="glass-input" data-i18n-ph="ph_pax">
                <button onclick="submitBooking()" class="btn-action mt-2 shadow-xl hover:shadow-2xl transition-shadow" data-i18n="btn_confirm_bk">ยืนยันการจอง</button>
            </div>
        </div>

        <div id="modal-deposit" class="fixed inset-0 z-[70] hidden flex-col bg-black p-4">
            <div class="flex justify-between mb-2"><h2 class="text-xl font-bold text-white">📸 ฝากของ</h2><button onclick="closeModal('modal-deposit')" class="text-gray-400">✕</button></div>
            
            <div class="code-display-box">
                <div class="code-label">เขียนรหัสนี้ที่ข้างขวด</div>
                <div class="code-row">
                    <div id="pre-gen-code" class="code-value">...</div>
                    <button onclick="genNewCode()" class="btn-refresh-code">↻</button>
                </div>
            </div>

            <div class="flex-1 overflow-y-auto">
                <label class="file-upload" id="dep-img-area"><input type="file" accept="image/*" capture="environment" id="dep-file" class="hidden" onchange="previewDepositImage(this)"><div id="dep-placeholder"><div class="text-4xl mb-2">📷</div><p class="text-sm text-gray-400">แตะเพื่อเปิดกล้อง</p></div><img id="dep-preview" class="hidden preview-img"></label>
                <div class="flex justify-end mb-4"><label class="text-xs text-gray-400 underline cursor-pointer">เลือกรูปจากอัลบั้ม<input type="file" accept="image/*" class="hidden" onchange="previewDepositImage(this)"></label></div>
                <div class="space-y-3">
                    <div class="flex gap-2"><button onclick="setDepType('liquor')" id="btn-type-liquor" class="type-btn active">🥃 เหล้า</button><button onclick="setDepType('beer')" id="btn-type-beer" class="type-btn">🍺 เบียร์</button></div>
                    <input list="drink-list" id="dep-brand" placeholder="ค้นหายี่ห้อ..." class="glass-input"><datalist id="drink-list"></datalist>
                    <input id="dep-amount" type="number" placeholder="จำนวน / %" class="glass-input">
                    <input id="dep-remark" placeholder="หมายเหตุ" class="glass-input">
                    <button onclick="submitDeposit()" class="btn-action mt-2">บันทึกรายการ</button>
                </div>
            </div>
        </div>

        <div id="modal-deposit-success" class="fixed inset-0 z-[80] hidden flex items-center justify-center bg-black/95 p-6">
            <div class="bg-gray-900 w-full rounded-3xl p-6 text-center border border-green-500/30">
                <div class="text-5xl mb-3">✅</div><h2 class="text-xl font-bold text-white mb-1">ฝากสำเร็จ!</h2><p class="text-gray-400 text-xs mb-4">ให้ลูกค้าสแกน QR หรือกรอกรหัส</p>
                <div class="bg-white/5 rounded-2xl p-4 mb-4 border border-white/10"><span id="success-code" class="text-5xl font-mono font-bold tracking-[0.2em] text-green-400">00000</span><p class="text-[10px] text-gray-500 mt-2 uppercase tracking-wider">รหัสรับของ (5 หลัก)</p></div>
                <div class="bg-white p-3 rounded-2xl w-fit mx-auto mb-4 shadow-2xl"><div id="success-qr"></div></div>
                <button onclick="manualStaffCheck()" id="btn-staff-refresh" class="w-full bg-white/10 text-white border border-white/20 py-2 rounded-xl mb-3 text-xs hover:bg-white/20 transition flex items-center justify-center gap-2"><span id="staff-refresh-icon">↻</span> อัพเดทสถานะ</button>
                <button id="btn-copy-link" onclick="copyClaimLink()" class="w-full bg-blue-600/20 text-blue-400 border border-blue-500/30 py-2 rounded-xl mb-3 text-xs">📋 คัดลอกลิ้งค์</button>
                <button onclick="show('view-staff'); stopStaffCheck();" class="w-full bg-gray-800 text-gray-300 py-2 rounded-xl text-xs">ปิดหน้าต่าง</button>
            </div>
        </div>

        <div id="modal-withdraw" class="fixed inset-0 z-[70] hidden flex-col bg-black p-4">
            <div class="flex justify-between mb-4"><h2 class="text-xl font-bold text-white">📤 สแกนเพื่อเบิก</h2><button onclick="closeModal('modal-withdraw')" class="text-gray-400">✕</button></div>
            <div id="reader" class="rounded-xl overflow-hidden mb-4 border border-white/20 bg-black min-h-[250px]"></div>
            <label class="block text-center mb-4"><span class="text-xs text-gray-400 bg-white/10 px-3 py-1 rounded-full cursor-pointer">📂 อัปโหลดรูป QR</span><input type="file" accept="image/*" class="hidden" onchange="cleanFromFile(this)"></label>
            <div class="flex gap-2"><input id="manual-code" placeholder="รหัส 5 หลัก (เช่น 10589)" class="glass-input text-center text-xl tracking-widest font-mono"><button onclick="manualWithdraw()" class="btn-action w-auto px-6">เบิก</button></div>
        </div>

        <div id="view-manager" class="hidden h-full flex flex-col">
            <div class="flex justify-between items-center mb-4 shrink-0"><h2 class="text-xl font-bold" style="color: var(--text-main);">👑 Dashboard</h2><button onclick="location.reload()" class="text-xs bg-red-900 text-red-200 px-3 py-1 rounded">Logout</button></div>
            
            <div class="bg-white/5 p-4 rounded-xl border border-white/10 flex justify-between items-center mb-4 shrink-0">
                <div class="flex items-center gap-3">
                    <span class="text-2xl">📅</span>
                    <div>
                        <div class="font-bold text-sm">Booking System</div>
                        <div id="mgr-bk-status-text" class="text-xs text-green-400">● Open</div>
                    </div>
                </div>
                <div class="flex items-center">
                    <input type="checkbox" id="toggle-bk" class="toggle-checkbox" onchange="updateBookingConfig(this.checked)">
                    <label for="toggle-bk" class="toggle-label"></label>
                </div>
            </div>

            <div class="flex gap-2 mb-4 bg-white/5 p-1 rounded-xl shrink-0">
                <button onclick="switchMgrTab('stock')" class="flex-1 py-2 rounded-lg text-sm font-bold bg-white/10">📦 Stock</button>
                <button onclick="switchMgrTab('users')" class="flex-1 py-2 rounded-lg text-sm text-gray-400 hover:text-white">👥 Staff</button>
                <button onclick="switchMgrTab('logs')" class="flex-1 py-2 rounded-lg text-sm text-gray-400 hover:text-white">📜 Logs</button>
            </div>
            
            <div id="mgr-tab-stock" class="space-y-4 flex-1 overflow-y-auto">
                <div class="bg-white/5 p-3 rounded-xl border border-white/10 flex flex-wrap gap-2">
                    <div class="flex w-full gap-2"><input id="filter-brand" placeholder="🔍 ค้นหา..." class="glass-input flex-1 outline-none"><button onclick="filterStock()" class="text-white px-4 py-2 rounded-lg font-bold" style="background: linear-gradient(90deg, var(--grad-start), var(--grad-end));">ค้นหา</button></div>
                    <select id="filter-expiry" onchange="filterStock()" class="glass-input outline-none border border-white/10"><option value="all">📅 วันหมดอายุ</option><option value="7">⚠️ < 7 วัน</option><option value="14">⚠️ < 14 วัน</option></select>
                    <select id="filter-pct" onchange="filterStock()" class="glass-input outline-none border border-white/10"><option value="all">📊 ปริมาณ</option><option value="low">🔴 น้อย</option><option value="mid">🟡 กลาง</option><option value="high">🟢 เยอะ</option></select>
                </div>
                <button onclick="testNotification()" class="w-full bg-orange-600/20 border border-orange-500/50 text-orange-400 py-3 rounded-xl font-bold hover:bg-orange-600/40 transition">🔔 Test Notification</button>
                <div id="stock-list" class="space-y-2 pb-10">Loading Stock...</div>
            </div>
            
            <div id="mgr-tab-users" class="hidden space-y-4 flex-1 overflow-y-auto">
                <div class="bg-white/5 p-4 rounded-xl border-l-4 border-yellow-500"><h3 class="text-yellow-500 font-bold mb-2">Pending</h3><div id="pending-list" class="space-y-2 text-sm"></div></div>
                <div class="bg-white/5 p-4 rounded-xl border-l-4 border-green-500"><h3 class="text-green-500 font-bold mb-2">Active</h3><div id="active-list" class="space-y-2 text-sm"></div></div>
            </div>
            
            <div id="mgr-tab-logs" class="hidden bg-white/5 p-2 rounded-xl flex-1 overflow-y-auto">
                <div id="logs-list" class="space-y-4 text-xs">Loading...</div>
                <button id="btn-load-more-logs" onclick="showMoreLogs()" class="w-full mt-4 bg-white/10 text-gray-300 py-2 rounded hidden">⬇️ โหลดเพิ่มเติม</button>
            </div>
        </div>
        
        <div id="view-staff-register" class="fixed inset-0 z-[65] hidden flex items-center justify-center bg-black/90 p-6"><div class="bg-[#1e293b] w-full max-w-xs p-6 rounded-2xl border border-white/10 text-center"><h2 class="text-xl font-bold mb-2 text-white">New Staff</h2><input type="text" id="reg-name" placeholder="ชื่อเล่น" class="glass-input text-center"><button onclick="registerStaff()" class="btn-action mt-2">ส่งคำขอ</button><button onclick="show('view-customer')" class="text-gray-500 text-sm mt-4">ยกเลิก</button></div></div>
        <div id="view-staff-waiting" class="fixed inset-0 z-[65] hidden flex flex-col items-center justify-center bg-black"><div class="text-6xl mb-4">⏳</div><h2 class="text-xl font-bold text-white">รอการอนุมัติ</h2><p id="my-uid-display" class="mt-6 bg-white/10 p-2 rounded text-xs font-mono select-all text-gray-300"></p><button onclick="show('view-customer')" class="mt-8 text-gray-500 underline">กลับหน้าหลัก</button></div>
    
    </div>

    <script>
        const CFG = { liff: "__LIFF__", worker: "__WORKER__", shop: "__SHOP__", r2: "__R2_URL__", hold: "__HOLD_TIME__", bk_tmpl: __BK_MSG__ };
        let profile={}, html5QrcodeScanner=null, depType='liquor', walletInterval=null, isStaffMode=false, staffUser=null, qrTimer=null, qrPoll=null, staffCheckInterval=null, allStockData=[], secretTapCount=0, currentClaimLink="";
        let currentLang = 'th';
        let allLogs = [];
        let logsLimit = 10;
        let walletPollCount = 0; const walletPollMax = 2; 
        let staffPollCount = 0; const staffPollMax = 20; 
        let currentDepCode = ""; 
        let isBookingOpen = true; // V85.7 Default true

        const I18N = {
            th: { welcome: "ยินดีต้อนรับ,", menu_booking: "จองโต๊ะ", menu_booking_sub: "สำรองที่นั่งล่วงหน้า", menu_wallet: "ระบบฝากเหล้า", menu_wallet_sub: "เช็ครายการฝาก / เบิกเหล้า / โอนสิทธิ์", bk_title: "📝 จองโต๊ะ", ph_name: "ชื่อผู้จอง", ph_phone: "เบอร์โทรติดต่อ", ph_pax: "จำนวนคน (เช่น 5 คน)", btn_confirm_bk: "ยืนยันการจอง", wallet_title: "🍾 My Collection", wallet_active: "📦 รายการคงเหลือ (Active)", wallet_history: "🕒 ประวัติการเบิก (History)", back: "กลับ", btn_manual_code: "🔑 กรอกรหัสรับของ", alert_fill: "กรุณากรอกข้อมูลให้ครบ", alert_conf_title: "ยืนยันการจอง", alert_conf_head: "✨ ข้อมูลการจอง ✨", alert_name: "👤 ชื่อ:", alert_date: "📅 วันที่:", alert_pax: "👥 จำนวน:", alert_phone: "📞 โทร:", alert_time: "⏰ เวลา:", alert_note: "กรุณามารับโต๊ะก่อนเวลา", alert_note2: "เพื่อรักษาสิทธิ์ของท่าน" },
            en: { welcome: "Welcome,", menu_booking: "Book Table", menu_booking_sub: "Reserve in advance", menu_wallet: "My Bottle", menu_wallet_sub: "Check / Withdraw / Transfer", bk_title: "📝 Reservation", ph_name: "Your Name", ph_phone: "Phone Number", ph_pax: "Pax (e.g. 5 ppl)", btn_confirm_bk: "Confirm Booking", wallet_title: "🍾 My Collection", wallet_active: "📦 Active Items", wallet_history: "🕒 History", back: "Back", btn_manual_code: "🔑 Enter Code", alert_fill: "Please fill all fields", alert_conf_title: "Confirm?", alert_conf_head: "✨ Reservation Info ✨", alert_name: "👤 Name:", alert_date: "📅 Date:", alert_pax: "👥 Pax:", alert_phone: "📞 Tel:", alert_time: "⏰ Time:", alert_note: "Please arrive before", alert_note2: "to hold your table." },
            cn: { welcome: "欢迎,", menu_booking: "预订桌位", menu_booking_sub: "提前预订", menu_wallet: "我的酒库", menu_wallet_sub: "查看 / 取酒 / 转让", bk_title: "📝 预订", ph_name: "姓名", ph_phone: "电话号码", ph_pax: "人数 (例如 5人)", btn_confirm_bk: "确认预订", wallet_title: "🍾 我的收藏", wallet_active: "📦 现有物品", wallet_history: "🕒 历史记录", back: "返回", btn_manual_code: "🔑 输入代码", alert_fill: "请填写完整信息", alert_conf_title: "确认?", alert_conf_head: "✨ 预订信息 ✨", alert_name: "👤 姓名:", alert_date: "📅 日期:", alert_pax: "👥 人数:", alert_phone: "📞 电话:", alert_time: "⏰ 时间:", alert_note: "请在", alert_note2: "前到达以保留座位。" }
        };
        const DRINKS = ["Chang", "Singha", "Leo", "Heineken", "Tiger", "Budweiser", "Hoegaarden", "Hoegaarden Rosée", "Stella Artois", "San Miguel", "San Miguel Light", "Federbräu", "Snowy Weizen", "Copper", "Corona", "Asahi", "Carlsberg", "Regency", "SangSom", "Blend 285", "Blend 285 Signature", "Hong Thong", "Meridian", "Johnnie Walker Red", "Johnnie Walker Black", "Johnnie Walker Double Black", "Johnnie Walker Gold", "Johnnie Walker Blue", "Chivas Regal 12", "Chivas Regal 18", "Jack Daniel’s", "Jameson", "Ballantine's", "Monkey Shoulder", "Absolut Vodka", "Grey Goose", "Suntory Kakubin", "Bombay Sapphire", "Jose Cuervo", "Penfolds Bin 2", "Penfolds Bin 389", "Penfolds Bin 407", "Yellow Tail", "Jacob's Creek", "Casillero del Diablo", "Mont Gras", "Robert Mondavi", "Concha y Toro", "Silver Oak", "Sutter Home", "Berri Estates"];
        const MOCK_STOCK = [{ item_name: "Regency", item_type: "liquor", amount: 60, deposit_code: "0001", expiry_date: new Date(new Date().getTime() + 5*24*60*60*1000), owner_name: "ลูกค้า A" }, { item_name: "Leo", item_type: "beer", amount: 3, deposit_code: "0002", expiry_date: new Date(new Date().getTime() + 20*24*60*60*1000), owner_name: "ลูกค้า B" }];
        
        function isPreviewMode() { return location.protocol === 'file:' || location.href.includes("preview_temp.html") || CFG.worker === ""; }
        function compressImage(f,q=0.7,m=800){return new Promise(r=>{const R=new FileReader();R.readAsDataURL(f);R.onload=e=>{const i=new Image();i.src=e.target.result;i.onload=()=>{const c=document.createElement('canvas');let w=i.width,h=i.height;if(w>m){h=Math.round((h*m)/w);w=m}c.width=w;c.height=h;c.getContext('2d').drawImage(i,0,0,w,h);r(c.toDataURL('image/jpeg',q))}}})}
        function formatDateSmart(dateStr) { if (!dateStr) return ""; const d = new Date(dateStr); const day = String(d.getDate()).padStart(2, '0'); const month = String(d.getMonth() + 1).padStart(2, '0'); let year = d.getFullYear(); if (currentLang === 'th') { return `${day}-${month}-${year + 543}`; } else { return `${day}-${month}-${year}`; } }
        function changeLang(lang) { currentLang = lang; document.querySelectorAll('[data-i18n]').forEach(el => { const key = el.getAttribute('data-i18n'); if (I18N[lang][key]) el.innerText = I18N[lang][key]; }); document.querySelectorAll('[data-i18n-ph]').forEach(el => { const key = el.getAttribute('data-i18n-ph'); if (I18N[lang][key]) el.placeholder = I18N[lang][key]; }); const dateVal = document.getElementById('bk-date').value; if(dateVal) document.getElementById('date-display').innerText = formatDateSmart(dateVal); }
        
        // V85.7: Fetch Booking Status
        async function fetchBookingStatus() {
            try {
                if(isPreviewMode()) return;
                const res = await fetch(CFG.worker + "/api/config?key=booking_status");
                const data = await res.json();
                isBookingOpen = (data.value !== 'false');
                updateBookingButton();
            } catch(e) { console.log("Fetch Config Error:", e); }
        }

        function updateBookingButton() {
            const btn = document.getElementById('menu-booking-btn');
            const sub = btn.querySelector('.sub-label');
            if(!isBookingOpen) {
                btn.classList.add('disabled');
                if(sub) sub.innerText = "ปิดปรับปรุงชั่วคราว";
            } else {
                btn.classList.remove('disabled');
                if(sub) sub.innerText = I18N[currentLang]['menu_booking_sub'];
            }
        }

        function checkAndOpenBooking() {
            if(!isBookingOpen) {
                Swal.fire("ขออภัย", "ระบบจองโต๊ะปิดให้บริการชั่วคราว", "warning");
            } else {
                show('view-booking');
            }
        }

        async function updateBookingConfig(isOpen) {
            try {
                const statusStr = isOpen ? 'true' : 'false';
                const label = document.getElementById('mgr-bk-status-text');
                label.innerText = "Updating...";
                
                if(isPreviewMode()) {
                     setTimeout(() => {
                         label.innerText = isOpen ? "● Open" : "● Closed";
                         label.className = isOpen ? "text-xs text-green-400" : "text-xs text-red-400";
                         isBookingOpen = isOpen;
                         updateBookingButton();
                     }, 500);
                     return;
                }

                await fetch(CFG.worker + "/api/config", {
                    method: 'POST',
                    body: JSON.stringify({ key: 'booking_status', value: statusStr })
                });
                
                label.innerText = isOpen ? "● Open" : "● Closed";
                label.className = isOpen ? "text-xs text-green-400" : "text-xs text-red-400";
                isBookingOpen = isOpen;
                updateBookingButton();
            } catch(e) {
                Swal.fire("Error", "Update failed", "error");
                document.getElementById('toggle-bk').checked = !isOpen; // Revert
            }
        }

        async function main() {
            const dl = document.getElementById('drink-list'); DRINKS.forEach(d => { const op = document.createElement('option'); op.value = d; dl.appendChild(op); });
            document.getElementById('bk-date').addEventListener('change', (e) => { document.getElementById('date-display').innerText = formatDateSmart(e.target.value); });
            try { await liff.init({ liffId: CFG.liff }); 
                if (!liff.isLoggedIn()) { 
                    if(isPreviewMode()) { profile={userId:"PREVIEW",displayName:"Preview User",pictureUrl:"https://via.placeholder.com/150"}; show('view-customer'); document.getElementById('loading').classList.add('hidden'); return; }
                    liff.login({ redirectUri: window.location.href }); return; 
                } 
                profile = await liff.getProfile(); document.getElementById('user-img').src = profile.pictureUrl; document.getElementById('user-name').innerText = profile.displayName; 
                const today = new Date(); document.getElementById('bk-date').valueAsDate = today; document.getElementById('date-display').innerText = formatDateSmart(today.toISOString().split('T')[0]);
                
                // Fetch status
                fetchBookingStatus();

                const u=new URLSearchParams(window.location.search); if(u.get('action')==='register'){show('view-staff-register');document.getElementById('loading').classList.add('hidden');return} if(u.get('claim_id'))await claimDeposit(u.get('claim_id')); checkRole(); 
            } catch(e) { 
                if(isPreviewMode()) { profile={userId:"PREVIEW",displayName:"Preview User",pictureUrl:"https://via.placeholder.com/150"}; show('view-customer'); document.getElementById('loading').classList.add('hidden'); } 
                else Swal.fire('Error', e.message, 'error'); 
            }
        }

        async function checkRole() { 
            try { 
                if(isPreviewMode()){document.getElementById('loading').classList.add('hidden');show('view-customer');return} 
                if(!profile.userId) return;
                const res=await fetch(CFG.worker+"/api/me?uid="+profile.userId);
                if (!res.ok) throw new Error("API Connection Error");
                const data=await res.json();
                document.getElementById('loading').classList.add('hidden');
                if(data.status==='pending'){
                    show('view-staff-waiting');
                    document.getElementById('my-uid-display').innerText=profile.userId
                } else if(data.role==='staff'||data.role==='manager'){
                    staffUser=data;
                    document.getElementById('btn-staff-switch').classList.remove('hidden'); 
                    sessionStorage.setItem('staffName',data.name);
                    isStaffMode=true;
                    updateModeUI()
                } else {
                    show('view-customer')
                } 
            } catch(e) { 
                console.error(e);
                document.getElementById('loading').classList.add('hidden');
                show('view-customer');
            } 
        }
        
        function show(id) { document.querySelectorAll('[id^="view-"], [id^="modal-"]').forEach(el => { el.classList.add('hidden'); el.classList.remove('flex'); }); const t = document.getElementById(id); t.classList.remove('hidden'); if(id.startsWith('modal-')) t.classList.add('flex'); window.scrollTo(0,0); }
        function toggleStaffMode() { isStaffMode = !isStaffMode; updateModeUI(); }
        function updateModeUI() { 
            const btnText = document.getElementById('staff-mode-text'); 
            if (btnText) { 
                btnText.innerText = isStaffMode ? "User" : "Staff"; 
                show(isStaffMode ? 'view-staff' : 'view-customer'); 
            } 
        }
        function closeModal(id) { show(isStaffMode ? 'view-staff' : 'view-customer'); if(html5QrcodeScanner) { html5QrcodeScanner.clear(); html5QrcodeScanner = null; } }
        function secretTap() { secretTapCount++; if (secretTapCount >= 5) { show('view-staff-register'); secretTapCount = 0; } }

        function showWithdrawQR(code, itemId) {
            let timeLeft = 120;
            Swal.fire({
                title: 'Scan Code: ' + code, 
                html: `
                <div class="flex justify-center my-4 p-4 bg-white rounded-xl"><div id="wd-qr"></div></div>
                <p class="text-gray-400 text-sm">QR หมดอายุใน <span id="qr-countdown" class="text-red-500 font-bold text-xl">120</span> วิ</p>
                <div class="mt-4">
                    <button onclick="checkWithdrawStatus('${itemId}')" class="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-4 rounded-xl border border-green-400 shadow-lg transition-all transform active:scale-95">
                        ✅ พนักงานสแกนแล้ว (กดเพื่อตรวจสอบ)
                    </button>
                </div>
                `, 
                showConfirmButton: false, 
                showCloseButton: true,
                didOpen: () => {
                    new QRCode(document.getElementById("wd-qr"), { text: code, width: 200, height: 200 });
                    qrTimer = setInterval(() => { 
                        timeLeft--; 
                        const el = document.getElementById('qr-countdown'); 
                        if(el) el.innerText = timeLeft; 
                        if(timeLeft <= 0) { 
                            clearInterval(qrTimer); 
                            Swal.close(); 
                            Swal.fire("หมดเวลา", "QR Code หมดอายุ กรุณากดใหม่", "warning"); 
                        } 
                    }, 1000);
                },
                willClose: () => { clearInterval(qrTimer); }
            });
        }
        
        async function checkWithdrawStatus(itemId) {
            Swal.showLoading();
            try {
                const res = await fetch(CFG.worker + "/api/my-wallet?uid=" + profile.userId);
                const data = await res.json();
                if (!data.find(i => i.id == itemId && i.status === 'active')) {
                    clearInterval(qrTimer);
                    Swal.fire({title: "สำเร็จ", text: "เบิกรายการเรียบร้อยแล้ว", icon: "success", timer: 2000, showConfirmButton: false}).then(() => loadMyWallet());
                } else {
                    Swal.fire({
                        title: "ยังไม่เสร็จสิ้น",
                        text: "กรุณาให้พนักงานสแกน QR Code ก่อนกดปุ่มนี้",
                        icon: "warning",
                        confirmButtonText: "ตกลง"
                    });
                }
            } catch(e) {
                Swal.fire("Error", "Check Failed", "error");
            }
        }
        
        async function submitBooking() { 
            const d = { n: document.getElementById('bk-name').value, p: document.getElementById('bk-phone').value, date: document.getElementById('bk-date').value, time: document.getElementById('bk-time').value, pax: document.getElementById('bk-pax').value }; 
            if(!d.n || !d.p || !d.pax) return Swal.fire("แจ้งเตือน", I18N[currentLang].alert_fill, "warning"); 
            const formattedDate = formatDateSmart(d.date); 
            
            let msg = CFG.bk_tmpl;
            msg = msg.replace('{name}', d.n).replace('{phone}', d.p).replace('{date}', formattedDate).replace('{time}', d.time).replace('{pax}', d.pax).replace('{shop}', CFG.shop).replace('{hold}', CFG.hold);
            
            if(liff.isInClient()) { 
                await liff.sendMessages([{type:'text', text:msg}]); 
                liff.closeWindow(); 
            } else { 
                Swal.fire("Simulated", msg, "info").then(()=> show('view-customer')); 
            } 
        }
        
        function genNewCode() {
            currentDepCode = Math.floor(10000 + Math.random() * 90000).toString();
            document.getElementById('pre-gen-code').innerText = currentDepCode;
        }

        async function openDepositFlow() { 
            document.getElementById('dep-file').value = ""; 
            document.getElementById('dep-preview').src = ""; 
            document.getElementById('dep-preview').classList.add('hidden'); 
            document.getElementById('dep-placeholder').classList.remove('hidden'); 
            document.getElementById('dep-img-area').classList.remove('has-img'); 
            document.getElementById('dep-brand').value = ""; 
            document.getElementById('dep-amount').value = ""; 
            document.getElementById('dep-remark').value = ""; 
            setDepType('liquor'); 
            genNewCode(); 
            show('modal-deposit'); 
        }
        
        function previewDepositImage(input) { if (input.files && input.files[0]) { const reader = new FileReader(); reader.onload = function(e) { document.getElementById('dep-preview').src = e.target.result; document.getElementById('dep-preview').classList.remove('hidden'); document.getElementById('dep-placeholder').classList.add('hidden'); document.getElementById('dep-img-area').classList.add('has-img'); }; reader.readAsDataURL(input.files[0]); } }
        function setDepType(t) { depType = t; document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active')); document.getElementById('btn-type-'+t).classList.add('active'); document.getElementById('dep-amount').placeholder = (t === 'liquor') ? "จำนวนเหลือ (%)" : "จำนวน (ขวด)"; }
        
        async function submitDeposit() { 
            const file = document.getElementById('dep-file').files[0] || document.querySelector('input[type="file"]:not(#dep-file)').files[0]; 
            const brand = document.getElementById('dep-brand').value; 
            const amt = document.getElementById('dep-amount').value; 
            const remark = document.getElementById('dep-remark').value; 
            
            if(!file) return Swal.fire("แจ้งเตือน", "กรุณาถ่ายรูป", "warning"); 
            if(!brand || !amt) return Swal.fire("แจ้งเตือน", "กรอกข้อมูลให้ครบ", "warning"); 
            
            const btn = document.querySelector('#modal-deposit .btn-action'); 
            const oldText = btn.innerText; 
            btn.innerText = "กำลังอัปโหลด..."; 
            btn.disabled = true; 
            
            if(isPreviewMode()){ setTimeout(()=>{show('modal-deposit-success');document.getElementById('success-code').innerText=currentDepCode;btn.innerText=oldText;btn.disabled=false},1000);return} 
            
            const formData = new FormData();
            formData.append('image', file); 
            formData.append('staff_uid', profile.userId); 
            formData.append('item_name', brand);
            formData.append('item_type', depType);
            formData.append('amount', amt);
            formData.append('remarks', remark);
            formData.append('deposit_code', currentDepCode); 
            
            try { 
                const res = await fetch(CFG.worker + "/api/deposit", { method: 'POST', body: formData }); 
                const data = await res.json(); 
                
                if(!data.success) throw new Error(data.message || "Upload failed");
                
                show('modal-deposit-success'); 
                document.getElementById('success-code').innerText = data.code; 
                document.getElementById('success-qr').innerHTML = ""; 
                currentClaimLink = `https://liff.line.me/${CFG.liff}?claim_id=${data.deposit_id}`; 
                new QRCode(document.getElementById("success-qr"), { text: currentClaimLink, width: 128, height: 128 }); 
                startStaffCheck(data.deposit_id); 
            } catch(e) { 
                Swal.fire("Error", e.message, "error"); 
            } finally { 
                btn.innerText = oldText; 
                btn.disabled = false; 
            } 
        }
        function copyClaimLink() { if(navigator.clipboard) { navigator.clipboard.writeText(currentClaimLink); Swal.fire({ toast: true, position: 'top', icon: 'success', title: 'คัดลอกลิ้งค์แล้ว', showConfirmButton: false, timer: 1500 }); } else { prompt("Copy link:", currentClaimLink); } }
        
        function startStaffCheck(depositId) { 
            if(staffCheckInterval) clearTimeout(staffCheckInterval); 
            staffPollCount = 0; 
            const check = async () => { 
                staffPollCount++;
                try { 
                    const res = await fetch(CFG.worker + "/api/check-deposit?id=" + depositId); 
                    const data = await res.json(); 
                    if (data.claimed) { 
                        Swal.fire({ title: '✅ เรียบร้อย!', text: 'ลูกค้าได้รับของแล้ว', icon: 'success' }).then(() => show('view-staff')); 
                        return; 
                    } 
                } catch(e) {} 
                
                if (staffPollCount < staffPollMax) {
                    staffCheckInterval = setTimeout(check, 3000);
                } else {
                    console.log("Auto-poll stopped.");
                }
            }; 
            check(); 
        }
        function manualStaffCheck() {
            const btnIcon = document.getElementById('staff-refresh-icon');
            btnIcon.classList.add('spin-anim');
            setTimeout(() => btnIcon.classList.remove('spin-anim'), 1000);
            
            const id = new URLSearchParams(currentClaimLink.split('?')[1]).get('claim_id');
            if(id) {
                staffPollCount = 0; 
                startStaffCheck(id);
                Swal.fire({ toast: true, position: 'top', icon: 'info', title: 'กำลังเช็คสถานะ...', showConfirmButton: false, timer: 1000 });
            }
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
            
            const res = await fetch(CFG.worker + "/api/withdraw", { method: 'POST', body: JSON.stringify({ code, staff_uid: profile.userId }) }); 
            const d = await res.json(); 
            if(d.success) { Swal.fire("สำเร็จ", "เบิกเรียบร้อยแล้ว", "success").then(()=> closeModal('modal-withdraw')); } 
            else { Swal.fire("ผิดพลาด", d.message, "error").then(()=> closeModal('modal-withdraw')); } 
        }
        
        async function manualClaimInput() { 
            const { value: code } = await Swal.fire({ 
                title: I18N[currentLang].btn_manual_code, 
                text: 'ดูเลข 5 หลักจากหน้าจอพนักงาน', 
                input: 'text', 
                inputPlaceholder: '00000', 
                inputAttributes: { maxlength: 5, autocapitalize: 'off', autocorrect: 'off' }, 
                showCancelButton: true 
            }); 
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

        async function claimDeposit(id) { try { const res = await fetch(CFG.worker + "/api/claim", { method: 'POST', body: JSON.stringify({ id, uid: profile.userId, name: profile.displayName }) }); const d = await res.json(); if(d.success) Swal.fire({ title: 'สำเร็จ!', text: 'รายการถูกเพิ่มในกระเป๋าของคุณแล้ว', icon: 'success', confirmButtonText: 'เปิดกระเป๋า' }).then(() => { window.location.href = window.location.pathname; }); else Swal.fire("เสียใจด้วย", "รายการนี้ถูกรับไปแล้ว หรือไม่ถูกต้อง", "error").then(() => window.location.href = window.location.pathname); } catch(e) { Swal.fire("Error", "Connect error", "error"); } }
        
        function startWalletSync() { walletPollCount = 0; loadMyWallet(); if(walletInterval) clearInterval(walletInterval); walletInterval = setInterval(() => { if (walletPollCount < walletPollMax) { loadMyWallet(); walletPollCount++; } else { console.log("Wallet sync paused."); } }, 5000); }
        function manualWalletRefresh() { walletPollCount = 0; loadMyWallet(); const btn = document.getElementById('icon-refresh'); btn.classList.add('spin-anim'); setTimeout(()=> btn.classList.remove('spin-anim'), 1000); }
        function stopWalletSync() { if(walletInterval) clearInterval(walletInterval); }
        
        function getProgressColor(amount) { if(amount <= 30) return 'bg-red-500'; if(amount <= 70) return 'bg-yellow-500'; return 'bg-green-500'; }
        
        async function shareItem(id, name, img, days) {
            if (!liff.isApiAvailable('shareTargetPicker')) {
                return Swal.fire("Error", "อุปกรณ์นี้ไม่รองรับการแชร์", "error");
            }
            const flex = {
                type: "flex",
                altText: "คุณได้รับของขวัญ! 🎁",
                contents: {
                    type: "bubble",
                    hero: { type: "image", url: img, size: "full", aspectRatio: "1:1", aspectMode: "cover" },
                    body: {
                        type: "box", layout: "vertical",
                        contents: [
                            { type: "text", text: "🎁 คุณได้รับของขวัญ", weight: "bold", color: "#EAB308", size: "lg" },
                            { type: "text", text: name, weight: "bold", size: "xl", margin: "md" },
                            { type: "text", text: "รีบกดรับก่อนหมดอายุ (" + days + ")", size: "xs", color: "#aaaaaa", margin: "sm" }
                        ]
                    },
                    footer: {
                        type: "box", layout: "vertical",
                        contents: [
                            { type: "button", style: "primary", color: "#EAB308", action: { type: "uri", label: "กดรับสิทธิ์", uri: "https://liff.line.me/" + CFG.liff + "?claim_id=" + id } }
                        ]
                    }
                }
            };
            liff.shareTargetPicker([flex])
                .then(res => {
                    if (res) Swal.fire("สำเร็จ", "ส่งของขวัญเรียบร้อย", "success");
                })
                .catch(err => Swal.fire("Error", err.message, "error"));
        }

        async function loadMyWallet() { 
            try { 
                if(isPreviewMode()) return; 
                const res = await fetch(CFG.worker + "/api/my-wallet?uid=" + profile.userId); 
                const data = await res.json(); 
                const activeDiv = document.getElementById('wallet-active'); 
                const historyDiv = document.getElementById('wallet-history'); 
                let activeHtml = "", historyHtml = ""; 
                
                data.forEach(item => { 
                    const createdDate = new Date(item.created_at).toLocaleDateString('th-TH'); 
                    if (item.status === 'active') { 
                        const days = Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24)); 
                        const daysText = days > 0 ? `${days} วัน` : "หมดอายุ"; 
                        const colorClass = days <= 5 ? 'text-red-400' : 'text-green-400'; 
                        
                        let imgUrl = (CFG.r2 && CFG.r2.length > 5) ? CFG.r2 + "/" + item.image_key : CFG.worker + "/api/image/" + item.image_key; 
                        
                        let visual = item.item_type === 'liquor' ? `<div class="flex items-center gap-2 mt-2"><div class="flex-1 bg-gray-700 h-2 rounded-full overflow-hidden"><div class="${getProgressColor(item.amount)} h-full" style="width: ${Math.min(item.amount, 100)}%"></div></div><span class="text-xs font-bold" style="color: var(--accent);">${item.amount}%</span></div>` : `<div class="mt-2 text-right"><span class="text-xl font-bold" style="color: var(--accent);">x ${item.amount}</span> <span class="text-xs">ขวด</span></div>`; 
                        
                        activeHtml += `<div class="bg-white/5 p-4 rounded-xl border border-white/10 relative overflow-hidden"><div class="flex gap-4"><div class="w-20 h-24 bg-black rounded-lg overflow-hidden shrink-0"><img src="${imgUrl}" class="w-full h-full object-cover" onclick="viewImage('${imgUrl}')"></div><div class="flex-1 min-w-0"><div class="flex justify-between items-start"><div><h3 class="font-bold text-lg truncate" style="color: var(--text-main);">${item.item_name}</h3><p class="text-xs text-gray-400">${item.remarks || '-'}</p></div><span class="bg-white/10 text-xs px-2 py-1 rounded font-mono">${item.deposit_code}</span></div>${visual}<div class="mt-2 flex justify-between items-end"><p class="text-xs ${colorClass}">⏳ เหลือ ${daysText}</p></div></div></div><div class="flex gap-2 mt-3 pt-3 border-t border-white/10"><button onclick="showWithdrawQR('${item.deposit_code}', '${item.id}')" class="flex-1 bg-red-500/10 text-red-400 py-2 rounded text-sm border border-red-500/30">เบิกออก</button><button onclick="shareItem('${item.id}','${item.item_name}', '${imgUrl}', '${daysText}')" class="flex-1 bg-blue-500/10 text-blue-400 py-2 rounded text-sm border border-blue-500/30">โอนสิทธิ์</button></div></div>`; 
                    } else if (item.status === 'withdrawn') { 
                        historyHtml += `<div class="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/10 grayscale"><div class="text-xs text-gray-400"><div>${item.item_name}</div><div class="text-[10px] opacity-70">ฝากเมื่อ: ${createdDate}</div></div><div class="text-xs font-bold text-red-500 border border-red-500 px-2 py-1 rounded">เบิกแล้ว</div></div>`; 
                    } 
                }); 
                if (activeDiv.innerHTML !== activeHtml) activeDiv.innerHTML = activeHtml; 
                if (historyDiv.innerHTML !== historyHtml) historyDiv.innerHTML = historyHtml; 
            } catch(e) { console.log(e); } 
        }
        
        async function testNotification() { if(isPreviewMode()) { Swal.fire("Sent!", "Test notification simulated.", "success"); return; } let targetUid = profile.userId; const { value: manualUid } = await Swal.fire({ title: 'Test Notification', text: 'กรุณากรอก User ID ของคุณ (ที่ขึ้นต้นด้วย U...)', input: 'text', inputValue: targetUid && targetUid !== 'PREVIEW' ? targetUid : '', inputPlaceholder: 'Uxxxxxxxxxxxxxxxxxxxx...', showCancelButton: true, confirmButtonText: '🚀 ส่งข้อความทดสอบ' }); if (manualUid) targetUid = manualUid; else return; try { const res = await fetch(CFG.worker + "/api/test-push", { method: 'POST', body: JSON.stringify({ uid: targetUid }) }); const d = await res.json(); if(d.success) Swal.fire("สำเร็จ!", "ส่งข้อความแล้ว เช็คใน LINE ได้เลย", "success"); else Swal.fire("ผิดพลาด", d.message, "error"); } catch(e) { Swal.fire("Error", "Connect failed", "error"); } }
        async function verifyManager() { const { value: pass } = await Swal.fire({ title: 'Manager Login', input: 'password', inputPlaceholder: 'Enter password', showCancelButton: true }); if (pass) { if(isPreviewMode()){show('view-manager');allStockData=MOCK_STOCK;filterStock();return} const res = await fetch(CFG.worker + "/api/login", { method: 'POST', body: JSON.stringify({ pass }) }); const d = await res.json(); if(d.success) { show('view-manager'); loadManagerData(); loadHistoryLogs(); loadManagerStock(); fetchBookingStatus().then(() => { document.getElementById('toggle-bk').checked = isBookingOpen; document.getElementById('mgr-bk-status-text').innerText = isBookingOpen ? "● Open" : "● Closed"; document.getElementById('mgr-bk-status-text').className = isBookingOpen ? "text-xs text-green-400" : "text-xs text-red-400"; }); } else Swal.fire("ผิดพลาด", "รหัสผ่านไม่ถูกต้อง", "error"); } }
        function switchMgrTab(tab) { ['stock','users','logs'].forEach(t => document.getElementById('mgr-tab-'+t).classList.add('hidden')); document.getElementById('mgr-tab-'+tab).classList.remove('hidden'); }
        async function loadManagerStock() { try { const res = await fetch(CFG.worker + "/api/manager-stock"); if(!res.ok) throw new Error("API Error"); allStockData = await res.json(); filterStock(); } catch(e) { document.getElementById('stock-list').innerHTML = `<p class="text-red-500 text-center">โหลดข้อมูลไม่สำเร็จ (Error: ${e.message})<br>โปรดตรวจสอบ Database</p>`; } }
        function filterStock() { const brandTxt = document.getElementById('filter-brand').value.toLowerCase(); const expiryVal = document.getElementById('filter-expiry').value; const pctVal = document.getElementById('filter-pct').value; const now = new Date(); const filtered = allStockData.filter(item => { if (brandTxt && !item.item_name.toLowerCase().includes(brandTxt)) return false; const expDate = new Date(item.expiry_date); const diffDays = Math.ceil((expDate - now) / (1000 * 60 * 60 * 24)); if (expiryVal === '7' && diffDays > 7) return false; if (expiryVal === '14' && diffDays > 14) return false; if (pctVal !== 'all' && item.item_type === 'liquor') { if (pctVal === 'low' && item.amount > 30) return false; if (pctVal === 'mid' && (item.amount <= 30 || item.amount > 70)) return false; if (pctVal === 'high' && item.amount <= 70) return false; } return true; }); const list = document.getElementById('stock-list'); list.innerHTML = ""; filtered.forEach(item => { let visual = ""; if(item.item_type === 'liquor') { const barColor = getProgressColor(item.amount); visual = `<div class="w-24 h-2 bg-gray-700 rounded-full overflow-hidden mt-1"><div class="${barColor} h-full" style="width:${item.amount}%"></div></div>`; } else visual = `<span class="text-xs font-bold text-white">x${item.amount}</span>`; const days = Math.ceil((new Date(item.expiry_date) - now) / (1000 * 60 * 60 * 24)); const daysHtml = days <= 7 ? `<span class='text-red-500 font-bold'>⚠️ ${days} วัน</span>` : `${days} วัน`; let imgUrl = (CFG.r2 && CFG.r2.length > 5) ? CFG.r2 + "/" + item.image_key : CFG.worker + "/api/image/" + item.image_key; if(isPreviewMode()) imgUrl = "https://via.placeholder.com/50"; const owner = item.owner_name ? item.owner_name : (item.owner_uid ? item.owner_uid.substring(0,8)+"..." : "Unknown"); list.innerHTML += `<div class="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/10"><img src="${imgUrl}" class="w-12 h-12 rounded object-cover bg-black" onclick="viewImage('${imgUrl}')"><div class="flex-1"><div class="font-bold">${item.item_name}</div><div class="text-xs text-gray-400">Code: ${item.deposit_code} | 👤 ${owner}</div><div class="text-xs text-yellow-500 mt-1">📝 Note: ${item.remarks || '-'}</div></div><div class="text-right">${visual}<div class="text-xs mt-1 text-gray-400">Exp: ${daysHtml}</div></div></div>`; }); }
        async function loadManagerData() { try { const res = await fetch(CFG.worker + "/api/manager-list"); if(!res.ok) throw new Error("API Error"); const data = await res.json(); const pList = document.getElementById('pending-list'); pList.innerHTML = ""; data.pending.forEach(s => { pList.innerHTML += `<div class="flex justify-between py-2 border-b border-white/10"><span>${s.name}</span><button onclick="staffAction('approve','${s.user_id}','${s.name}')" class="text-green-400 font-bold">✓</button></div>`; }); const aList = document.getElementById('active-list'); aList.innerHTML = ""; data.active.forEach(s => { aList.innerHTML += `<div class="flex justify-between py-2 border-b border-white/10"><span>${s.name}</span><button onclick="staffAction('remove','${s.user_id}','${s.name}')" class="text-red-400 font-bold">✕</button></div>`; }); } catch(e) { document.getElementById('pending-list').innerHTML = "<span class='text-red-500'>Error loading staff.</span>"; } }
        async function loadHistoryLogs() { try { const res = await fetch(CFG.worker + "/api/logs"); if(!res.ok) throw new Error("API Error"); const data = await res.json(); allLogs = data.logs; renderLogs(); } catch(e) { document.getElementById('logs-list').innerHTML = "<span class='text-red-500'>Error loading logs.</span>"; } }
        function renderLogs() { const list = document.getElementById('logs-list'); const showBtn = document.getElementById('btn-load-more-logs'); list.innerHTML = ""; const logsToShow = allLogs.slice(0, logsLimit); logsToShow.forEach(l => { const color = l.action === 'deposit' ? 'text-blue-400' : (l.action === 'withdraw' ? 'text-red-400' : 'text-gray-400'); const date = new Date(l.created_at).toLocaleString('th-TH'); let imgHTML = l.image_key ? `<div class="mt-1"><img src="${(CFG.r2 && CFG.r2.length > 5) ? CFG.r2 + "/" + l.image_key : CFG.worker + "/api/image/" + l.image_key}" class="h-12 rounded border border-white/20" onclick="viewImage(this.src)" onerror="this.parentElement.style.display='none'"></div>` : ""; list.innerHTML += `<div class="py-3 border-b border-white/5"><div class="flex justify-between"><strong class="${color} uppercase">${l.action}</strong><span class="opacity-50">${date}</span></div><div class="text-gray-300 mt-1">${l.details}</div>${imgHTML}<div class="text-xs opacity-50 mt-1">by ${l.staff_name}</div></div>`; }); if (logsLimit < allLogs.length) { showBtn.classList.remove('hidden'); showBtn.innerText = `⬇️ โหลดเพิ่มเติม (${allLogs.length - logsLimit})`; } else { showBtn.classList.add('hidden'); } }
        function showMoreLogs() { logsLimit += 10; renderLogs(); }
        async function staffAction(action, uid, name) { const c = await Swal.fire({ title: 'ยืนยัน?', icon: 'warning', showCancelButton: true }); if(c.isConfirmed) { await fetch(CFG.worker + "/api/staff-action", { method: 'POST', body: JSON.stringify({ action, uid, name }) }); loadManagerData(); } }
        async function registerStaff() { const name = document.getElementById('reg-name').value; if(!name) return Swal.fire("แจ้งเตือน", "ใส่ชื่อ", "warning"); await fetch(CFG.worker + "/api/register", { method: 'POST', body: JSON.stringify({ uid: profile.userId, name: name }) }); Swal.fire("สำเร็จ", "ส่งคำขอแล้ว!", "success").then(() => location.reload()); }
        main();
    </script>
</body>
</html>"""

# ==============================================================================
# 2. WORKER CODE (V85.7 - Added Config API)
# ==============================================================================
WORKER_RAW = r"""
export default {
    async fetch(request, env, ctx) {
      const url = new URL(request.url);
      const path = url.pathname;
      const corsHeaders = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" };
      if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });
  
      async function addLog(action, staff, details, imgKey = null) {
          try { await env.DB.prepare("INSERT INTO logs (action, staff_name, details, image_key) VALUES (?, ?, ?, ?)").bind(action, staff, details, imgKey).run(); } catch(e){}
      }

      async function validateStaff(uid) {
          if(!uid) return null;
          return await env.DB.prepare("SELECT * FROM staff_access WHERE user_id = ? AND status = 'active'").bind(uid).first();
      }
  
      try {
          // V85.7 Config API (Booking Toggle)
          if (path === "/api/config") {
              if (request.method === "GET") {
                  const key = url.searchParams.get('key');
                  const res = await env.DB.prepare("SELECT value FROM config WHERE key = ?").bind(key).first();
                  return new Response(JSON.stringify({ value: res ? res.value : 'true' }), { headers: corsHeaders });
              }
              if (request.method === "POST") {
                  const body = await request.json(); // { key: 'booking_status', value: 'true' }
                  await env.DB.prepare("INSERT INTO config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value").bind(body.key, body.value).run();
                  return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
              }
          }

          if (path.startsWith("/api/image/")) {
              const key = path.split('/').pop(); 
              const object = await env.BUCKET.get(key);
              if (!object) return new Response('Not Found', { status: 404 });
              const headers = new Headers(); object.writeHttpMetadata(headers); headers.set('etag', object.httpEtag);
              headers.set('Cache-Control', 'public, max-age=31536000, immutable'); 
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
              const formData = await request.formData();
              const image = formData.get('image');
              const staffUid = formData.get('staff_uid');
              const itemName = formData.get('item_name');
              const itemType = formData.get('item_type');
              const amount = formData.get('amount');
              const remarks = formData.get('remarks') || "";
              const depositCode = formData.get('deposit_code'); 

              if (!depositCode) return new Response(JSON.stringify({ success: false, message: "Missing Code" }), { headers: corsHeaders });

              const staff = await validateStaff(staffUid);
              if (!staff) return new Response(JSON.stringify({ success: false, message: "Unauthorized Staff" }), { headers: corsHeaders });

              const exists = await env.DB.prepare("SELECT id FROM deposits WHERE deposit_code = ? AND status != 'withdrawn'").bind(depositCode).first();
              if (exists) {
                  return new Response(JSON.stringify({ success: false, message: "รหัสซ้ำ (Duplicate) กรุณากดปุ่มรีเฟรชรหัสใหม่" }), { headers: corsHeaders });
              }

              const filename = `dep_${Date.now()}_${Math.floor(Math.random()*1000)}.jpg`; 
              await env.BUCKET.put(filename, image);
              
              const res = await env.DB.prepare(`INSERT INTO deposits (staff_name, item_name, item_type, amount, remarks, image_key, status, expiry_date, deposit_code) VALUES (?, ?, ?, ?, ?, ?, 'pending_claim', date('now', '+30 days'), ?) RETURNING id`).bind(staff.name, itemName, itemType, amount, remarks, filename, depositCode).first();
              
              await addLog('deposit', staff.name, `Deposit: ${itemName} (${depositCode})`, filename);
              return new Response(JSON.stringify({ success: true, deposit_id: res.id, code: depositCode }), { headers: corsHeaders });
          }

          if (path === "/api/check-deposit") {
              const id = url.searchParams.get('id'); const res = await env.DB.prepare("SELECT owner_uid FROM deposits WHERE id = ?").bind(id).first();
              return new Response(JSON.stringify({ claimed: !!(res && res.owner_uid) }), { headers: corsHeaders });
          }
          if (path === "/api/claim" && request.method === "POST") {
              const body = await request.json(); const ownerName = body.name || null; let res;
              if (body.code) res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE id = (SELECT id FROM deposits WHERE deposit_code = ? AND status = 'pending_claim' ORDER BY id ASC LIMIT 1)").bind(body.uid, ownerName, body.code).run();
              else res = await env.DB.prepare("UPDATE deposits SET owner_uid = ?, owner_name = ?, status = 'active' WHERE id = ? AND status != 'withdrawn'").bind(body.uid, ownerName, body.id).run();
              
              if(res.meta.changes > 0) return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
              return new Response(JSON.stringify({ success: false, message: "Invalid code or item already claimed" }), { headers: corsHeaders });
          }
          if (path === "/api/my-wallet") {
              const uid = url.searchParams.get('uid'); const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_uid = ? ORDER BY created_at DESC").bind(uid).all();
              return new Response(JSON.stringify(res.results), { headers: corsHeaders });
          }
          if (path === "/api/withdraw" && request.method === "POST") {
              const body = await request.json();
              const staff = await validateStaff(body.staff_uid);
              if (!staff) return new Response(JSON.stringify({ success: false, message: "Unauthorized Staff" }), { headers: corsHeaders });

              const item = await env.DB.prepare("SELECT * FROM deposits WHERE deposit_code = ? AND status = 'active' ORDER BY id ASC LIMIT 1").bind(body.code).first();
              if (!item) return new Response(JSON.stringify({ success: false, message: "Code not found" }), { headers: corsHeaders });
              
              await env.DB.prepare("UPDATE deposits SET status = 'withdrawn' WHERE id = ?").bind(item.id).run();
              
              if (item.image_key) {
                  ctx.waitUntil(env.BUCKET.delete(item.image_key).catch(err => console.log("R2 Delete Error:", err)));
              }

              await addLog('withdraw', staff.name, `Withdrew: ${item.item_name} (Code: ${body.code})`, item.image_key);
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
              if (body.action === 'approve') { await env.DB.prepare("UPDATE staff_access SET status = 'active' WHERE user_id = ?").bind(body.uid).run(); await addLog('approve', 'Manager', `Approved Staff: ${body.name}`); }
              else if (body.action === 'remove') { await env.DB.prepare("DELETE FROM staff_access WHERE user_id = ?").bind(body.uid).run(); await addLog('remove', 'Manager', `Removed Staff: ${body.name}`); }
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }
          if (path === "/api/test-push" && request.method === "POST") {
              const body = await request.json();
              if (!env.LINE_TOKEN) return new Response(JSON.stringify({ success: false, message: "No LINE Token" }), { headers: corsHeaders });
              const bubble = { "type": "bubble", "body": { "type": "box", "layout": "vertical", "contents": [ { "type": "text", "text": "🔔 Test Notification", "weight": "bold", "color": "#1DB446" } ] } };
              await fetch("https://api.line.me/v2/bot/message/push", { method: "POST", headers: { "Content-Type": "application/json", "Authorization": "Bearer " + env.LINE_TOKEN }, body: JSON.stringify({ "to": body.uid, "messages": [{ "type": "flex", "altText": "Test", "contents": { "type": "carousel", "contents": [bubble] } }] }) });
              return new Response(JSON.stringify({ success: true }), { headers: corsHeaders });
          }
      } catch(e) { return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders }); }
      return new Response("API Ready v85.7", { headers: corsHeaders });
    },
    async scheduled(event, env, ctx) {
      const query = `SELECT * FROM deposits WHERE status = 'active' AND (expiry_date = date('now', '+14 days') OR expiry_date = date('now', '+7 days') OR expiry_date = date('now', '+3 days') OR expiry_date = date('now', '+1 days'))`;
      const results = await env.DB.prepare(query).all();
      if (results.results.length === 0) return;
      const userItems = {};
      results.results.forEach(item => { if (item.owner_uid) { if (!userItems[item.owner_uid]) userItems[item.owner_uid] = []; userItems[item.owner_uid].push(item); } });
      for (const [uid, list] of Object.entries(userItems)) { await sendLinePush(uid, list, env.LINE_TOKEN); }
    }
};
async function sendLinePush(uid, items, token) {
    if (!token) return;
    const bubbles = items.map(item => {
        const days = Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
        const color = days <= 1 ? "#ef4444" : "#f97316";
        return { "type": "bubble", "body": { "type": "box", "layout": "vertical", "contents": [ { "type": "text", "text": "⚠️ Expiry Warning", "weight": "bold", "color": color }, { "type": "text", "text": item.item_name, "size": "xl", "wrap": true }, { "type": "text", "text": `Expires in ${days} days`, "size": "sm", "color": "#aaaaaa" } ] } };
    });
    await fetch("https://api.line.me/v2/bot/message/push", { method: "POST", headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token }, body: JSON.stringify({ "to": uid, "messages": [{ "type": "flex", "altText": "Expiry Warning", "contents": { "type": "carousel", "contents": bubbles } }] }) });
}
"""

# ==============================================================================
# 3. PYTHON UI CONTROLLER (V85.7 - Added Config Table)
# ==============================================================================
class AppGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nightlife System V85.7 (Booking Toggle)")
        self.geometry("1100x850")
        self.profiles = {}
        self.profile_file = "profiles.json"
        
        self.vars = { 
            'bg_color': '#0f172a', 'grad_start': '#0e4296', 'grad_end': '#1e293b', 
            'text_main': '#ffffff', 'text_sub': '#94a3b8', 'accent': '#EAB308', 
            'radius': '16px', 'shadow': '0 4px 15px rgba(0,0,0,0.3)', 'border': '1px solid rgba(255,255,255,0.1)' 
        }
        
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
        
        self.default_bk_tmpl = """✨ Booking Confirmed ✨\n━━━━━━━━━━━━━━━━━━\nร้าน: {shop}\nชื่อ: {name}\nเบอร์: {phone}\nวันที่: {date}\nเวลา: {time}\nจำนวน: {pax} คน\n\n*กรุณามารับโต๊ะก่อนเวลา {hold}\nเพื่อรักษาสิทธิ์ของท่าน"""

        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=2); self.grid_rowconfigure(0, weight=1)
        self.load_profiles()
        self.setup_ui()
        self.update_preview_ui()

    def load_profiles(self):
        if os.path.exists(self.profile_file):
            try: self.profiles = json.load(open(self.profile_file, encoding='utf-8'))
            except: self.profiles = {}

    def save_profiles(self):
        with open(self.profile_file, "w", encoding='utf-8') as f: json.dump(self.profiles, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        left = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent"); left.grid(row=0, column=0, sticky="nsew")
        
        prof_frame = ctk.CTkFrame(left, fg_color="#1e293b"); prof_frame.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(prof_frame, text="📂 Profile Manager").pack()
        self.combo_profiles = ctk.CTkComboBox(prof_frame, values=list(self.profiles.keys()), command=self.load_selected_profile)
        self.combo_profiles.pack(fill="x", padx=10, pady=5)
        btn_row = ctk.CTkFrame(prof_frame, fg_color="transparent"); btn_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_row, text="New", command=self.new_profile, width=60, fg_color="#6366f1").pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="Save", command=self.save_current_profile, width=60, fg_color="#10B981").pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="Del", command=self.delete_profile, width=60, fg_color="#EF4444").pack(side="left", padx=2)

        self.scroll = ctk.CTkScrollableFrame(left, fg_color="transparent"); self.scroll.pack(fill="both", expand=True)
        self.entries = {}
        
        # FIELDS CONFIG
        for k in ["Shop Name", "LIFF ID", "Worker URL", "Manager Password", "R2 Public URL", "Channel Access Token", "D1 Database ID", "Hold Table Time"]:
            ctk.CTkLabel(self.scroll, text=k).pack(anchor="w", padx=20)
            e = ctk.CTkEntry(self.scroll); e.pack(fill="x", padx=20)
            self.entries[k] = e
            if k == "Shop Name": e.bind("<KeyRelease>", self.update_preview_text)
        
        ctk.CTkLabel(self.scroll, text="Booking Message Template", text_color="#EAB308").pack(anchor="w", padx=20, pady=(15,5))
        self.txt_booking = ctk.CTkTextbox(self.scroll, height=100); self.txt_booking.pack(fill="x", padx=20)
        self.txt_booking.insert("1.0", self.default_bk_tmpl)

        ctk.CTkLabel(self.scroll, text="Layout Style").pack(anchor="w", padx=20, pady=(10,5))
        self.combo_layout = ctk.CTkComboBox(self.scroll, values=list(self.LAYOUTS.keys()), command=self.update_preview_ui)
        self.combo_layout.set("Standard (Default)")
        self.combo_layout.pack(fill="x", padx=20)

        c_grid = ctk.CTkFrame(self.scroll); c_grid.pack(fill="x", padx=20, pady=10)
        self.create_color_btn(c_grid, "BG", 'bg_color', 0)
        self.create_color_btn(c_grid, "G1", 'grad_start', 1)
        self.create_color_btn(c_grid, "G2", 'grad_end', 2)
        self.create_color_btn(c_grid, "Accent", 'accent', 3)
        ctk.CTkButton(self.scroll, text="Random Theme", command=self.randomize_palette_based_on_bg).pack(pady=10)
        
        ctk.CTkButton(left, text="GENERATE", command=self.build, height=50, fg_color="#10B981").pack(fill="x", padx=20, pady=20)

        self.preview = ctk.CTkFrame(self, fg_color="#000"); self.preview.grid(row=0, column=1, sticky="nsew")
        ctk.CTkButton(self.preview, text="👁️ OPEN REAL PREVIEW", command=self.open_live_preview, height=40, fg_color="#EAB308", text_color="black").pack(pady=10, fill="x", padx=20)
        
        self.phone = ctk.CTkFrame(self.preview, width=375, height=667, fg_color="#fff"); self.phone.place(relx=0.5, rely=0.5, anchor="center")
        self.phone.pack_propagate(False)
        
        self.p_head = ctk.CTkLabel(self.phone, text="SHOP", font=("Arial", 20)); self.p_head.pack(pady=(40, 10))
        
        self.p_container = ctk.CTkFrame(self.phone, fg_color="transparent")
        self.p_container.pack(fill="both", expand=True, padx=20)

    def new_profile(self):
        for k in self.entries: self.entries[k].delete(0, "end")
        self.txt_booking.delete("1.0", "end"); self.txt_booking.insert("1.0", self.default_bk_tmpl)
        self.combo_profiles.set("")

    def save_current_profile(self):
        name = self.entries["Shop Name"].get().strip()
        if not name: return
        data = {k: v.get() for k,v in self.entries.items()}
        data['colors'] = self.vars.copy()
        data['layout'] = self.combo_layout.get()
        data['bk_tmpl'] = self.txt_booking.get("1.0", "end-1c")
        self.profiles[name] = data
        self.save_profiles()
        self.combo_profiles.configure(values=list(self.profiles.keys())); self.combo_profiles.set(name)
        messagebox.showinfo("Saved", "Profile saved!")

    def load_selected_profile(self, name):
        if name in self.profiles:
            data = self.profiles[name]
            for k,v in data.items():
                if k in self.entries: self.entries[k].delete(0, "end"); self.entries[k].insert(0, v)
            if 'colors' in data: self.vars.update(data['colors'])
            if 'layout' in data: self.combo_layout.set(data['layout'])
            self.txt_booking.delete("1.0", "end")
            self.txt_booking.insert("1.0", data.get('bk_tmpl', self.default_bk_tmpl))
            self.update_preview_ui()

    def delete_profile(self):
        name = self.combo_profiles.get()
        if name in self.profiles:
            del self.profiles[name]; self.save_profiles()
            self.combo_profiles.configure(values=list(self.profiles.keys())); self.combo_profiles.set("")
            self.new_profile()

    def create_color_btn(self, p, l, k, r):
        ctk.CTkLabel(p, text=l).grid(row=r, column=0)
        b = ctk.CTkButton(p, text="", width=40, command=lambda: self.pick_color(k)); b.grid(row=r, column=1); setattr(self, f"btn_{k}", b)

    def pick_color(self, k):
        c = colorchooser.askcolor(color=self.vars[k])[1]
        if c: 
            self.vars[k] = c
            if k == 'bg_color': self.randomize_palette_based_on_bg()
            self.update_preview_ui()

    def randomize_palette_based_on_bg(self):
        bg_hex = self.vars['bg_color']
        r, g, b = self.hex2rgb(bg_hex)
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        if l < 0.5: 
            self.vars['text_main'] = '#ffffff'; self.vars['text_sub'] = '#94a3b8'
            h_acc = (h + random.uniform(0.3, 0.7)) % 1.0; self.vars['accent'] = self.rgb2hex(*[x*255 for x in colorsys.hls_to_rgb(h_acc, 0.6, 0.9)])
            h_grad = (h + random.uniform(-0.1, 0.1)) % 1.0; self.vars['grad_start'] = self.rgb2hex(*[x*255 for x in colorsys.hls_to_rgb(h_grad, min(1, l+0.2), s)]); self.vars['grad_end'] = self.rgb2hex(*[x*255 for x in colorsys.hls_to_rgb(h_grad, max(0, l-0.1), s)])
        else: 
            self.vars['text_main'] = '#0f172a'; self.vars['text_sub'] = '#475569'
            h_acc = (h + 0.5) % 1.0; self.vars['accent'] = self.rgb2hex(*[x*255 for x in colorsys.hls_to_rgb(h_acc, 0.4, 0.8)])
            self.vars['grad_start'] = '#334155'; self.vars['grad_end'] = '#0f172a'
        self.update_preview_ui()

    def hex2rgb(self, hex_col):
        h = hex_col.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def rgb2hex(self, r, g, b): return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))
    
    def update_preview_ui(self, e=None):
        for k, v in self.vars.items():
            try: getattr(self, f"btn_{k}").configure(fg_color=v)
            except: pass
        self.phone.configure(fg_color=self.vars['bg_color'])
        self.p_head.configure(text_color=self.vars['text_main'])
        
        for widget in self.p_container.winfo_children(): widget.destroy()
        layout = self.combo_layout.get()
        if "Grid" in layout:
            self.p_container.grid_columnconfigure(0, weight=1); self.p_container.grid_columnconfigure(1, weight=1)
            btn1 = ctk.CTkFrame(self.p_container, height=100, fg_color=self.vars['grad_start']); btn1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            btn2 = ctk.CTkFrame(self.p_container, height=100, fg_color=self.vars['grad_start']); btn2.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        elif "List" in layout or "Compact" in layout:
            btn1 = ctk.CTkFrame(self.p_container, height=60, fg_color=self.vars['grad_start']); btn1.pack(fill="x", pady=5)
            btn2 = ctk.CTkFrame(self.p_container, height=60, fg_color=self.vars['grad_start']); btn2.pack(fill="x", pady=5)
        else:
            btn1 = ctk.CTkFrame(self.p_container, height=100, fg_color=self.vars['grad_start']); btn1.pack(fill="x", pady=10)
            btn2 = ctk.CTkFrame(self.p_container, height=100, fg_color=self.vars['grad_start']); btn2.pack(fill="x", pady=10)

    def update_preview_text(self, e): self.p_head.configure(text=self.entries["Shop Name"].get())

    def open_live_preview(self):
        try:
            shop = self.entries["Shop Name"].get() or "PREVIEW SHOP"
            layout_css = self.LAYOUTS.get(self.combo_layout.get(), "")
            bk_msg_safe = json.dumps(self.txt_booking.get("1.0", "end-1c"))
            html = HTML_RAW
            for k, v in [("__SHOP__", shop), ("__BG_COLOR__", self.vars['bg_color']), ("__GRAD_START__", self.vars['grad_start']), ("__GRAD_END__", self.vars['grad_end']), ("__TEXT_MAIN__", self.vars['text_main']), ("__TEXT_SUB__", self.vars['text_sub']), ("__ACCENT__", self.vars['accent']), ("__RADIUS__", self.vars['radius']), ("__SHADOW__", self.vars['shadow']), ("__BORDER__", self.vars['border']), ("__LIFF__", ""), ("__WORKER__", ""), ("__R2_URL__", ""), ("__HOLD_TIME__", ""), ("__LAYOUT_CSS__", layout_css), ("__BK_MSG__", bk_msg_safe)]:
                html = html.replace(k, v)
            path = os.path.abspath("preview_temp.html")
            with open(path, "w", encoding="utf-8") as f: f.write(html)
            webbrowser.open(f"file://{path}")
        except Exception as e: messagebox.showerror("Preview Error", str(e))

    def build(self):
        shop = self.entries["Shop Name"].get()
        db_id = self.entries["D1 Database ID"].get().strip()
        
        if not shop: return messagebox.showerror("Error", "No Shop Name")
        if not db_id: return messagebox.showerror("Error", "Please enter D1 Database ID")
        
        layout_css = self.LAYOUTS.get(self.combo_layout.get(), "")
        bk_msg_safe = json.dumps(self.txt_booking.get("1.0", "end-1c"))

        html = HTML_RAW
        for k, v in [("__SHOP__", shop), ("__BG_COLOR__", self.vars['bg_color']), ("__GRAD_START__", self.vars['grad_start']), ("__GRAD_END__", self.vars['grad_end']), ("__TEXT_MAIN__", self.vars['text_main']), ("__TEXT_SUB__", self.vars['text_sub']), ("__ACCENT__", self.vars['accent']), ("__RADIUS__", self.vars['radius']), ("__SHADOW__", self.vars['shadow']), ("__BORDER__", self.vars['border']), ("__LIFF__", self.entries["LIFF ID"].get()), ("__WORKER__", self.entries["Worker URL"].get()), ("__R2_URL__", self.entries["R2 Public URL"].get()), ("__HOLD_TIME__", self.entries["Hold Table Time"].get()), ("__LAYOUT_CSS__", layout_css), ("__BK_MSG__", bk_msg_safe)]:
            html = html.replace(k, v)
            
        worker = WORKER_RAW.replace("__MGR_PASS__", self.entries["Manager Password"].get()).replace("__LIFF__", self.entries["LIFF ID"].get())
        
        folder = f"Output_{shop.replace(' ', '_')}"
        if not os.path.exists(folder): os.makedirs(folder)
        with open(f"{folder}/index.html", "w", encoding="utf-8") as f: f.write(html)
        with open(f"{folder}/worker.js", "w", encoding="utf-8") as f: f.write(worker)
        
        with open(f"{folder}/wrangler.toml", "w", encoding="utf-8") as f: f.write(f"""name = "nightlife-app"\nmain = "worker.js"\ncompatibility_date = "2023-10-30"\n\n[vars]\nLINE_TOKEN = "{self.entries["Channel Access Token"].get()}"\n\n[[d1_databases]]\nbinding = "DB"\ndatabase_name = "nightlife-db"\ndatabase_id = "{db_id}"\n\n[[r2_buckets]]\nbinding = "BUCKET"\nbucket_name = "nightlife-bucket"\n\n[triggers]\ncrons = ["0 3 * * *"]""")
        
        # V85.7: Add config table
        sql_content = """CREATE TABLE IF NOT EXISTS staff_access (user_id TEXT PRIMARY KEY, name TEXT, status TEXT DEFAULT 'pending', role TEXT DEFAULT 'staff', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\nCREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, deposit_code TEXT, staff_name TEXT, item_name TEXT, item_type TEXT, amount TEXT, remarks TEXT, image_key TEXT, status TEXT, expiry_date TEXT, owner_uid TEXT, owner_name TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\nCREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, staff_name TEXT, details TEXT, image_key TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\nCREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT);\nCREATE INDEX IF NOT EXISTS idx_deposit_code ON deposits(deposit_code);\nCREATE INDEX IF NOT EXISTS idx_owner_uid ON deposits(owner_uid);\nCREATE INDEX IF NOT EXISTS idx_status ON deposits(status);"""
        with open(f"{folder}/d1_schema.sql", "w", encoding="utf-8") as f: f.write(sql_content)

        self.save_current_profile()
        messagebox.showinfo("Success", "Generated V85.7 (Added Booking Toggle)!")
        webbrowser.open(folder)

if __name__ == "__main__": app = AppGenerator(); app.mainloop()