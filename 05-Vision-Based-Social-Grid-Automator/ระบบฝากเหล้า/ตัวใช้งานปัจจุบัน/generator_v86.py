import customtkinter as ctk
from tkinter import colorchooser, messagebox
import os
import json

# ==============================================================================
# 1. HTML TEMPLATE V86 (CRM & REWARDS EDITION)
# ==============================================================================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>__SHOP_NAME__</title>
    <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --accent: __COLOR_ACCENT__; --bg: __COLOR_BG__; }
        body { font-family: 'Prompt', sans-serif; background-color: var(--bg); color: white; margin: 0; min-height: 100dvh; overflow-x: hidden; }
        .glass { background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); }
        .btn-grad { background: linear-gradient(135deg, __COLOR_GRAD_START__, __COLOR_GRAD_END__); }
        .hidden { display: none !important; }
        .card-grad { background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02)); }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col">
    <div id="loading" class="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/90">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-t-transparent border-[var(--accent)]"></div>
        <p class="mt-4 text-xs tracking-widest text-[#94a3b8]">LOADING CRM SYSTEM...</p>
    </div>

    <!-- UI: Phone Link -->
    <div id="view-phone-link" class="hidden fixed inset-0 z-[90] flex items-center justify-center bg-black/95 p-6 backdrop-blur-md">
        <div class="glass w-full max-w-sm p-10 rounded-[2.5rem] text-center shadow-2xl">
            <div class="text-5xl mb-6">📱</div>
            <h2 class="text-2xl font-bold mb-3">ยินดีต้อนรับ</h2>
            <p class="text-xs text-gray-400 mb-8 leading-relaxed">กรุณาระบุเบอร์โทรศัพท์เพื่อเริ่มสะสมแต้ม<br>และฝากเหล้ากับทางร้านของเรา</p>
            <input type="tel" id="link-phone" placeholder="08x-xxx-xxxx" class="w-full bg-white/5 border border-white/20 rounded-2xl p-5 text-center text-2xl mb-6 focus:border-[var(--accent)] outline-none transition-all text-white">
            <button onclick="linkPhoneToUID()" class="btn-grad w-full p-5 rounded-2xl font-bold text-white shadow-lg active:scale-95 transition-transform">เริ่มใช้งานระบบสมาชิก</button>
        </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 max-w-md mx-auto w-full p-4 pb-24">
        <div class="flex justify-between items-start mb-8 pt-4">
            <div onclick="requestStaffAccess()">
                <h1 class="text-2xl font-bold tracking-tight text-white">__SHOP_NAME__</h1>
                <p id="display-phone" class="text-[10px] text-gray-400 font-mono tracking-widest mt-1 uppercase"></p>
            </div>
            <button id="btn-staff-mode" onclick="toggleStaff()" class="hidden glass px-4 py-2 rounded-full text-[10px] font-bold text-[var(--accent)] uppercase tracking-tighter">Staff Area</button>
        </div>

        <!-- Customer View -->
        <div id="view-customer" class="space-y-6">
            <!-- Points Display Card -->
            <div class="glass p-8 rounded-[2.5rem] relative overflow-hidden card-grad">
                <div class="absolute top-0 right-0 p-8 opacity-10 text-6xl">💎</div>
                <div class="flex items-center gap-4 mb-6">
                    <img id="user-img" class="w-14 h-14 rounded-full border-2 border-[var(--accent)] p-0.5 bg-black">
                    <div>
                        <h2 id="user-name" class="font-bold text-lg text-white">Guest</h2>
                        <span class="text-[9px] bg-[var(--accent)]/20 text-[var(--accent)] px-2 py-0.5 rounded-full font-bold">SILVER MEMBER</span>
                    </div>
                </div>
                <div class="flex justify-between items-end mt-10">
                    <div>
                        <p class="text-[10px] text-gray-400 uppercase tracking-widest">Available Points</p>
                        <p id="user-points" class="text-5xl font-bold text-[var(--accent)] mt-1">0</p>
                    </div>
                    <button onclick="show('view-rewards')" class="glass px-4 py-2 rounded-2xl text-[10px] font-bold text-white mb-1">REDEEM</button>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <button onclick="show('view-wallet'); loadWallet();" class="glass p-6 rounded-[2rem] flex flex-col items-center">
                    <div class="text-4xl mb-3">🍾</div>
                    <span class="text-xs font-bold tracking-widest uppercase">My Bottles</span>
                </button>
                <button onclick="show('view-history')" class="glass p-6 rounded-[2rem] flex flex-col items-center">
                    <div class="text-4xl mb-3">📜</div>
                    <span class="text-xs font-bold tracking-widest uppercase">History</span>
                </button>
            </div>
        </div>

        <!-- Rewards Store -->
        <div id="view-rewards" class="hidden space-y-6">
            <div class="flex items-center gap-4">
                <button onclick="show('view-customer')" class="glass w-10 h-10 rounded-full flex items-center justify-center text-sm text-white">←</button>
                <h2 class="text-xl font-bold text-white">REWARD STORE</h2>
            </div>
            <div class="grid grid-cols-1 gap-4" id="rewards-list">
                <!-- Rewards will be populated here -->
                <div class="glass p-4 rounded-3xl flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-blue-500/20 rounded-2xl flex items-center justify-center text-2xl">🧊</div>
                        <div>
                            <h3 class="font-bold text-sm">น้ำแข็ง 1 ถัง</h3>
                            <p class="text-[10px] text-gray-400">ใช้ 100 แต้ม</p>
                        </div>
                    </div>
                    <button onclick="redeemReward('Ice Bucket', 100)" class="btn-grad px-4 py-2 rounded-xl text-[10px] font-bold text-white">แลกเลย</button>
                </div>
                <div class="glass p-4 rounded-3xl flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-green-500/20 rounded-2xl flex items-center justify-center text-2xl">🥤</div>
                        <div>
                            <h3 class="font-bold text-sm">มิกเซอร์ 3 ขวด</h3>
                            <p class="text-[10px] text-gray-400">ใช้ 250 แต้ม</p>
                        </div>
                    </div>
                    <button onclick="redeemReward('Mixers x3', 250)" class="btn-grad px-4 py-2 rounded-xl text-[10px] font-bold text-white">แลกเลย</button>
                </div>
            </div>
        </div>

        <!-- Staff View -->
        <div id="view-staff" class="hidden space-y-4">
            <div class="flex gap-2 p-1 bg-white/5 rounded-2xl mb-4">
                <button onclick="setStaffTab('deposit')" id="tab-dep" class="flex-1 p-3 rounded-xl font-bold text-xs btn-grad shadow-lg transition-all text-white">📥 รับฝาก</button>
                <button onclick="setStaffTab('search')" id="tab-src" class="flex-1 p-3 rounded-xl font-bold text-xs glass border-none transition-all">🔍 ค้นหาลูกค้า</button>
            </div>
            
            <div id="staff-deposit" class="space-y-4">
                <div class="glass p-6 rounded-[2rem]">
                    <h3 class="text-xs font-bold mb-4 text-[var(--accent)] uppercase">ฝากเหล้า + ให้แต้ม</h3>
                    <input type="tel" id="dep-phone" placeholder="เบอร์โทรลูกค้า *" class="w-full bg-black/40 p-4 rounded-xl border border-white/10 mb-3 outline-none focus:border-[var(--accent)] text-white">
                    <input type="text" id="dep-brand" placeholder="ยี่ห้อเหล้า" class="w-full bg-black/40 p-4 rounded-xl border border-white/10 mb-3 outline-none text-white">
                    <input type="number" id="dep-amount" placeholder="ปริมาณคงเหลือ (%)" class="w-full bg-black/40 p-4 rounded-xl border border-white/10 mb-4 outline-none text-white">
                    
                    <div class="photo-upload-container __TIER2_ONLY__">
                        <label class="block glass h-32 rounded-2xl border-dashed border-2 border-white/20 flex flex-col items-center justify-center cursor-pointer overflow-hidden relative mb-4">
                            <input type="file" accept="image/*" capture="environment" id="dep-file" class="hidden" onchange="previewImg(this)">
                            <div id="dep-placeholder" class="text-center opacity-60">
                                <span class="text-3xl block mb-1">📸</span>
                                <p class="text-[9px] uppercase font-bold text-white">ถ่ายรูปหลักฐาน</p>
                            </div>
                            <img id="dep-preview" class="absolute inset-0 w-full h-full object-cover hidden">
                        </label>
                    </div>

                    <div class="bg-[var(--accent)]/10 p-4 rounded-2xl border border-[var(--accent)]/10">
                        <p class="text-[10px] text-[var(--accent)] font-bold mb-2">CRM SETTINGS</p>
                        <div class="flex items-center justify-between">
                            <span class="text-xs text-white">แต้มที่จะได้รับ:</span>
                            <div class="flex items-center gap-2">
                                <input type="number" id="dep-points" value="100" class="w-20 bg-black/40 p-2 rounded-lg text-center font-bold text-[var(--accent)] outline-none">
                                <span class="text-[10px]">pts</span>
                            </div>
                        </div>
                    </div>

                    <button onclick="submitDepositStaff()" class="btn-grad w-full p-5 rounded-2xl font-bold mt-6 shadow-xl active:scale-95 transition-transform text-white">บันทึกรายการ</button>
                </div>
            </div>

            <div id="staff-search" class="hidden space-y-4">
                <div class="flex gap-2">
                    <input type="tel" id="search-phone" placeholder="ระบุเบอร์โทร..." class="flex-1 bg-white/10 p-5 rounded-2xl outline-none border border-white/10 focus:border-[var(--accent)] text-white">
                    <button onclick="searchByPhone()" class="btn-grad px-8 rounded-2xl font-bold shadow-lg text-white">ค้นหา</button>
                </div>
                <div id="user-info-section" class="hidden glass p-6 rounded-3xl animate-in fade-in transition-all">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="font-bold text-sm text-[var(--accent)]">ข้อมูลสมาชิก</h3>
                        <span id="info-points" class="text-xl font-bold text-white">0 Pts</span>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="adjustPoints('add')" class="flex-1 bg-green-500/20 text-green-500 py-3 rounded-xl font-bold text-[10px] border border-green-500/20">+ ADD PTS</button>
                        <button onclick="adjustPoints('deduct')" class="flex-1 bg-red-500/20 text-red-500 py-3 rounded-xl font-bold text-[10px] border border-red-500/20">- REDEEM</button>
                    </div>
                </div>
                <div id="search-results" class="space-y-3 pt-2"></div>
            </div>
        </div>

        <div id="view-wallet" class="hidden space-y-6">
            <div class="flex items-center gap-4">
                <button onclick="show('view-customer')" class="glass w-10 h-10 rounded-full flex items-center justify-center text-sm text-white">←</button>
                <h2 class="text-xl font-bold text-white">MY DRINKS</h2>
            </div>
            <div id="wallet-list" class="space-y-4"></div>
        </div>
    </div>

    <!-- Navigation Bar -->
    <nav id="nav-bar" class="fixed bottom-0 left-0 w-full glass border-t border-white/10 p-4 flex justify-around items-center z-40 backdrop-blur-2xl">
        <button onclick="show('view-customer')" class="flex flex-col items-center"><span class="text-2xl">💎</span><span class="text-[10px] mt-1 text-gray-400">Home</span></button>
        <button onclick="show('view-wallet'); loadWallet();" class="flex flex-col items-center"><span class="text-2xl">🍾</span><span class="text-[10px] mt-1 text-gray-400">Cabinet</span></button>
        <button onclick="show('view-rewards')" class="flex flex-col items-center"><span class="text-2xl">🎁</span><span class="text-[10px] mt-1 text-gray-400">Rewards</span></button>
    </nav>

    <script>
        const CFG = { liff: "__LIFF_ID__", worker: "__WORKER_URL__" };
        let profile = {}, myPhone = "", isStaff = false, currentPoints = 0;

        async function init() {
            try {
                await liff.init({ liffId: CFG.liff });
                if (!liff.isLoggedIn()) { liff.login(); return; }
                profile = await liff.getProfile();
                document.getElementById('user-img').src = profile.pictureUrl;
                document.getElementById('user-name').innerText = profile.displayName;
                checkUser();
            } catch (err) { console.error(err); }
        }

        async function checkUser() {
            const res = await fetch(`${CFG.worker}/api/me?uid=${profile.userId}`);
            const data = await res.json();
            document.getElementById('loading').classList.add('hidden');
            
            if (data.role === 'staff' || data.role === 'manager') {
                isStaff = true;
                document.getElementById('btn-staff-mode').classList.remove('hidden');
            }
            
            if (!data.phone) { 
                show('view-phone-link'); 
            } else {
                myPhone = data.phone;
                currentPoints = data.points || 0;
                document.getElementById('display-phone').innerText = `Certified: ${myPhone}`;
                document.getElementById('user-points').innerText = currentPoints.toLocaleString();
                show('view-customer');
            }
        }

        async function requestStaffAccess() {
            const { value: password } = await Swal.fire({
                title: 'Staff Login',
                input: 'password',
                inputLabel: 'กรุณากรอกรหัสผ่านเพื่อเชื่อมต่อ UID พนักงาน',
                inputPlaceholder: 'รหัสผ่าน...',
                showCancelButton: true
            });
            if (password) {
                Swal.showLoading();
                const res = await fetch(`${CFG.worker}/api/staff-login`, {
                    method: 'POST',
                    body: JSON.stringify({ uid: profile.userId, password, name: profile.displayName })
                });
                const d = await res.json();
                if (d.success) {
                    Swal.fire('สำเร็จ', 'เชื่อมต่อระบบพนักงานและ CRM เรียบร้อย', 'success').then(() => location.reload());
                } else {
                    Swal.fire('ผิดพลาด', 'รหัสผ่านไม่ถูกต้อง', 'error');
                }
            }
        }

        async function linkPhoneToUID() {
            const phone = document.getElementById('link-phone').value;
            if (phone.length < 9) return Swal.fire("Error", "ระบุเบอร์โทรไม่ถูกต้อง", "warning");
            Swal.showLoading();
            const res = await fetch(`${CFG.worker}/api/link-phone`, {
                method: 'POST', body: JSON.stringify({ uid: profile.userId, phone, name: profile.displayName })
            });
            if (await res.json().then(d => d.success)) {
                myPhone = phone;
                Swal.fire("สำเร็จ", "คุณได้รับโบนัสสมัครสมาชิก 50 แต้ม!", "success").then(() => checkUser());
            }
        }

        async function submitDepositStaff() {
            const phone = document.getElementById('dep-phone').value;
            const brand = document.getElementById('dep-brand').value;
            const amt = document.getElementById('dep-amount').value;
            const pts = document.getElementById('dep-points').value;
            const file = document.getElementById('dep-file').files[0];
            
            if (!phone || !brand || !amt) return Swal.fire("Warning", "กรอกข้อมูลไม่ครบครับ", "warning");

            Swal.showLoading();
            const formData = new FormData();
            if(file) formData.append('image', file);
            formData.append('phone', phone);
            formData.append('brand', brand);
            formData.append('amount', amt);
            formData.append('points', pts);
            formData.append('staff_uid', profile.userId);

            const res = await fetch(`${CFG.worker}/api/deposit`, { method: 'POST', body: formData });
            if (await res.json().then(d => d.success)) {
                Swal.fire("สำเร็จ", `บันทึกและเพิ่ม ${pts} แต้มให้ลูกค้าแล้ว`, "success").then(() => location.reload());
            }
        }

        async function adjustPoints(action) {
            const phone = document.getElementById('search-phone').value;
            const { value: amount } = await Swal.fire({
                title: action === 'add' ? 'Add Points' : 'Redeem Points',
                input: 'number',
                inputLabel: 'จำนวนแต้ม',
                showCancelButton: true
            });
            
            if (amount) {
                Swal.showLoading();
                const res = await fetch(`${CFG.worker}/api/points-adjust`, {
                    method: 'POST',
                    body: JSON.stringify({ phone, action, amount, staff_uid: profile.userId })
                });
                if (await res.json().then(d => d.success)) {
                    Swal.fire("สำเร็จ", "ปรับปรุงแต้มเรียบร้อย", "success").then(() => searchByPhone());
                }
            }
        }

        async function redeemReward(name, cost) {
            if (currentPoints < cost) return Swal.fire("แต้มไม่พอ", `รางวัลนี้ใช้ ${cost} แต้ม คุณมีเพียง ${currentPoints} แต้ม`, "error");
            
            const conf = await Swal.fire({
                title: 'ยืนยันการแลกรางวัล?',
                text: `คุณจะแลกแต้ม ${cost} Pts สำหรับ '${name}'`,
                icon: 'question',
                showCancelButton: true
            });

            if (conf.isConfirmed) {
                Swal.showLoading();
                const res = await fetch(`${CFG.worker}/api/redeem`, {
                    method: 'POST',
                    body: JSON.stringify({ uid: profile.userId, reward: name, points: cost })
                });
                if (await res.json().then(d => d.success)) {
                    Swal.fire("สำเร็จ!", "กรุณาโชว์หน้านี้ให้พนักงานดูเพื่อรับของรางวัล", "success").then(() => checkUser());
                }
            }
        }

        async function searchByPhone() {
            const phone = document.getElementById('search-phone').value;
            if (!phone) return;
            Swal.showLoading();
            const res = await fetch(`${CFG.worker}/api/staff-search?phone=${phone}`);
            const data = await res.json();
            Swal.close();
            
            const info = document.getElementById('user-info-section');
            const resCont = document.getElementById('search-results');
            
            if (data.user) {
                info.classList.remove('hidden');
                document.getElementById('info-points').innerText = `${data.user.points || 0} Pts`;
            } else {
                info.classList.add('hidden');
            }

            resCont.innerHTML = "";
            data.deposits.forEach(item => {
                resCont.innerHTML += `
                    <div class="glass p-4 rounded-3xl flex gap-4">
                        <img src="${item.image_url}" class="w-16 h-20 rounded-2xl object-cover bg-black">
                        <div class="flex-1 flex flex-col justify-between">
                            <div>
                                <h3 class="font-bold text-xs text-white uppercase">${item.item_name}</h3>
                                <div class="w-full bg-white/5 h-1 rounded-full mt-2 overflow-hidden">
                                    <div class="bg-[var(--accent)] h-full" style="width:${item.amount}%"></div>
                                </div>
                            </div>
                            <button onclick="withdrawByStaff('${item.id}')" class="w-full bg-red-500/10 text-red-500 py-1.5 rounded-xl text-[9px] font-bold border border-red-500/20">Withdraw</button>
                        </div>
                    </div>
                `;
            });
        }

        async function withdrawByStaff(id) {
            const conf = await Swal.fire({ title: 'Confirm?', text: 'เบิกเหล้าให้ลูกค้าหรือไม่', icon: 'warning', showCancelButton: true });
            if (!conf.isConfirmed) return;
            const res = await fetch(`${CFG.worker}/api/staff-withdraw`, {
                method: 'POST', body: JSON.stringify({ deposit_id: id, staff_uid: profile.userId })
            });
            if (await res.json().then(d => d.success)) {
                Swal.fire("Success", "เบิกเรียบร้อย", "success").then(() => searchByPhone());
            }
        }

        function show(id) {
            document.querySelectorAll('[id^="view-"]').forEach(el => el.classList.add('hidden'));
            document.getElementById(id).classList.remove('hidden');
            if (id === 'view-phone-link') document.getElementById(id).classList.add('flex');
            document.getElementById('nav-bar').classList.toggle('hidden', id === 'view-staff' || id === 'view-phone-link');
        }

        function toggleStaff() {
            if(document.getElementById('view-staff').classList.contains('hidden')) show('view-staff');
            else show('view-customer');
        }

        function setStaffTab(tab) {
            document.getElementById('staff-deposit').classList.toggle('hidden', tab !== 'deposit');
            document.getElementById('staff-search').classList.toggle('hidden', tab !== 'search');
            document.getElementById('tab-dep').className = (tab === 'deposit') ? "flex-1 p-3 rounded-xl font-bold text-xs btn-grad text-white" : "flex-1 p-3 rounded-xl font-bold text-xs glass text-gray-400";
            document.getElementById('tab-src').className = (tab === 'search') ? "flex-1 p-3 rounded-xl font-bold text-xs btn-grad text-white" : "flex-1 p-3 rounded-xl font-bold text-xs glass text-gray-400";
        }

        function previewImg(input) {
            if (input.files && input.files[0]) {
                const r = new FileReader();
                r.onload = e => {
                    document.getElementById('dep-preview').src = e.target.result;
                    document.getElementById('dep-preview').classList.remove('hidden');
                    document.getElementById('dep-placeholder').classList.add('hidden');
                };
                r.readAsDataURL(input.files[0]);
            }
        }

        async function loadWallet() {
            const list = document.getElementById('wallet-list');
            list.innerHTML = "<div class='text-center py-20 opacity-30'>Loading...</div>";
            const res = await fetch(`${CFG.worker}/api/my-wallet?uid=${profile.userId}`);
            const data = await res.json();
            list.innerHTML = data.length ? "" : "<div class='text-center py-20 opacity-30'><p>No items found</p></div>";
            data.forEach(item => {
                list.innerHTML += `
                    <div class="glass p-5 rounded-[2.5rem] flex gap-5">
                        <img src="${item.image_url}" class="w-24 h-32 rounded-3xl object-cover bg-black">
                        <div class="flex-1 flex flex-col justify-center">
                            <h3 class="font-bold text-lg text-white mb-1 uppercase tracking-tight">${item.item_name}</h3>
                            <div class="w-full bg-white/5 h-2 rounded-full mt-3 overflow-hidden">
                                <div class="bg-gradient-to-r from-[var(--accent)] to-white/50 h-full" style="width:${item.amount}%"></div>
                            </div>
                            <p class="text-[9px] text-gray-500 mt-4 uppercase">Bottle ID: ${item.id}</p>
                        </div>
                    </div>
                `;
            });
        }

        init();
    </script>
</body>
</html>"""

# ==============================================================================
# 2. WORKER TEMPLATE V86 (CRM Logic)
# ==============================================================================
WORKER_TEMPLATE = r"""
const CONFIG = { MANAGER_PASSWORD: "__MANAGER_PASSWORD__" };

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*" };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    try {
      if (path === "/api/me") {
        const uid = url.searchParams.get('uid');
        const user = await env.DB.prepare("SELECT * FROM user_profiles WHERE uid = ?").bind(uid).first();
        const staff = await env.DB.prepare("SELECT role FROM staff_access WHERE uid = ? AND status = 'active'").bind(uid).first();
        return new Response(JSON.stringify({ phone: user ? user.phone : null, points: user ? user.points : 0, role: staff ? staff.role : 'customer' }), { headers: cors });
      }

      if (path === "/api/staff-login" && request.method === "POST") {
        const { uid, password, name } = await request.json();
        if (password === CONFIG.MANAGER_PASSWORD) {
          await env.DB.prepare("INSERT OR REPLACE INTO staff_access (uid, name, role) VALUES (?, ?, 'staff')").bind(uid, name).run();
          return new Response(JSON.stringify({ success: true }), { headers: cors });
        }
        return new Response(JSON.stringify({ success: false }), { headers: cors });
      }

      if (path === "/api/link-phone" && request.method === "POST") {
        const { uid, phone, name } = await request.json();
        // Give 50 points as welcome bonus
        await env.DB.prepare("INSERT OR REPLACE INTO user_profiles (uid, phone, name, points) VALUES (?, ?, ?, 50)").bind(uid, phone, name).run();
        await env.DB.prepare("UPDATE deposits SET owner_uid = ? WHERE owner_phone = ? AND (owner_uid IS NULL OR owner_uid = '')").bind(uid, phone).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/deposit" && request.method === "POST") {
        const form = await request.formData();
        const image = form.get('image');
        const phone = form.get('phone');
        const brand = form.get('brand');
        const amount = form.get('amount');
        const points = parseInt(form.get('points') || '0');
        const staff_uid = form.get('staff_uid');

        const profile = await env.DB.prepare("SELECT uid FROM user_profiles WHERE phone = ?").bind(phone).first();
        const owner_uid = profile ? profile.uid : null;
        
        let filename = null;
        if (image && image.size > 0) {
            filename = `v86_${Date.now()}.jpg`;
            await env.BUCKET.put(filename, image);
        }
        
        await env.DB.prepare("INSERT INTO deposits (item_name, amount, owner_phone, owner_uid, image_key, status, staff_uid) VALUES (?, ?, ?, ?, ?, 'active', ?)").bind(brand, amount, phone, owner_uid, filename, staff_uid).run();
        
        // Add Points to User
        if (phone) {
            await env.DB.prepare("UPDATE user_profiles SET points = points + ? WHERE phone = ?").bind(points, phone).run();
            await env.DB.prepare("INSERT INTO point_logs (phone, amount, action, staff_uid) VALUES (?, ?, 'deposit_bonus', ?)").bind(phone, points, staff_uid).run();
        }

        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/staff-search") {
        const phone = url.searchParams.get('phone');
        const user = await env.DB.prepare("SELECT * FROM user_profiles WHERE phone = ?").bind(phone).first();
        const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_phone = ? AND status = 'active'").bind(phone).all();
        const mapped = res.results.map(r => ({ ...r, image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : "https://via.placeholder.com/150?text=No+Photo" }));
        return new Response(JSON.stringify({ user, deposits: mapped }), { headers: cors });
      }

      if (path === "/api/points-adjust" && request.method === "POST") {
        const { phone, action, amount, staff_uid } = await request.json();
        const finalAmt = action === 'add' ? parseInt(amount) : -parseInt(amount);
        await env.DB.prepare("UPDATE user_profiles SET points = points + ? WHERE phone = ?").bind(finalAmt, phone).run();
        await env.DB.prepare("INSERT INTO point_logs (phone, amount, action, staff_uid) VALUES (?, ?, ?, ?)").bind(phone, finalAmt, action, staff_uid).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/redeem" && request.method === "POST") {
        const { uid, reward, points } = await request.json();
        const user = await env.DB.prepare("SELECT points, phone FROM user_profiles WHERE uid = ?").bind(uid).first();
        if (user.points < points) return new Response(JSON.stringify({ success: false }), { headers: cors });
        
        await env.DB.prepare("UPDATE user_profiles SET points = points - ? WHERE uid = ?").bind(points, uid).run();
        await env.DB.prepare("INSERT INTO point_logs (phone, amount, action, staff_uid) VALUES (?, ?, ?, 'system')").bind(user.phone, -points, `redeem_${reward}`).run();
        return new Response(JSON.stringify({ success: true }), { headers: cors });
      }

      if (path === "/api/my-wallet") {
        const uid = url.searchParams.get('uid');
        const res = await env.DB.prepare("SELECT * FROM deposits WHERE owner_uid = ? AND status = 'active'").bind(uid).all();
        const mapped = res.results.map(r => ({ ...r, image_url: r.image_key ? `${url.origin}/api/image/${r.image_key}` : "https://via.placeholder.com/150?text=No+Photo" }));
        return new Response(JSON.stringify(mapped), { headers: cors });
      }

      if (path.startsWith("/api/image/")) {
        const key = path.split('/').pop();
        const obj = await env.BUCKET.get(key);
        if(!obj) return new Response("Not Found", { status: 404 });
        return new Response(obj.body, { headers: { "Content-Type": "image/jpeg", ...cors } });
      }

    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: cors });
    }
  }
}
"""

# ==============================================================================
# 3. SQL SCHEMA (CRM Tables Included)
# ==============================================================================
SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_profiles (
    uid TEXT PRIMARY KEY,
    phone TEXT,
    name TEXT,
    points INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS point_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    amount INTEGER,
    action TEXT,
    staff_uid TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff_access (
    uid TEXT PRIMARY KEY,
    name TEXT,
    role TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    amount INTEGER,
    owner_phone TEXT,
    owner_uid TEXT,
    image_key TEXT,
    status TEXT,
    staff_uid TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at DATETIME,
    withdrawn_by TEXT
);
"""

# ==============================================================================
# 4. PYTHON GENERATOR GUI
# ==============================================================================
PROFILES_FILE = "profiles.json"

class V86MasterGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bottle Keep V86 - CRM & REWARDS EDITION")
        self.geometry("1100x850")
        ctk.set_appearance_mode("dark")
        self.colors = {'bg': '#0f172a', 'accent': '#EAB308', 'grad_start': '#1e3a8a', 'grad_end': '#1e293b'}
        self.profiles = {}
        self.setup_ui()
        self.load_profiles()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.left = ctk.CTkScrollableFrame(self, width=450, corner_radius=0)
        self.left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        ctk.CTkLabel(self.left, text="V86 CRM MASTER", font=("Arial", 28, "bold"), text_color="#EAB308").pack(pady=(30, 5))
        
        self.create_head("📁 SELECT SHOP PROFILE")
        self.profile_var = ctk.StringVar(value="-- เลือกโปรไฟล์ร้าน --")
        self.profile_menu = ctk.CTkOptionMenu(self.left, values=["-- เลือกโปรไฟล์ร้าน --"], variable=self.profile_var, command=self.on_profile_select, height=40)
        self.profile_menu.pack(fill="x", padx=20, pady=10)

        self.create_head("1. CONFIGURATION")
        self.ent_shop = self.create_in("ชื่อร้านค้า", "Siri Clubhouse")
        self.ent_liff = self.create_in("LIFF ID", "")
        self.ent_worker = self.create_in("Worker URL", "")
        self.ent_pw = self.create_in("Manager Password", "7777")
        
        self.create_head("2. TIER SELECTION")
        self.tier_var = ctk.StringVar(value="Professional (Tier 2)")
        self.tier_menu = ctk.CTkOptionMenu(self.left, values=["Starter (Tier 1)", "Professional (Tier 2)", "Enterprise (Tier 3)"], variable=self.tier_var, height=35)
        self.tier_menu.pack(fill="x", padx=20, pady=10)

        self.create_head("3. AESTHETICS")
        f_colors = ctk.CTkFrame(self.left, fg_color="transparent")
        f_colors.pack(fill="x", padx=20, pady=10)
        self.btn_bg = self.col_btn(f_colors, "พื้นหลัง", 'bg')
        self.btn_accent = self.col_btn(f_colors, "สีเน้นหลัก", 'accent')
        self.btn_grad = self.col_btn(f_colors, "Gradient", 'grad_start')

        self.create_head("4. GLOBAL ADMIN")
        self.ent_my_uid = self.create_in("Admin LINE UID (Your UID)", "")

        self.btn_gen = ctk.CTkButton(self.left, text="🚀 BUILD CRM SYSTEM", font=("Arial", 18, "bold"), height=60, fg_color="#EAB308", text_color="black", command=self.generate)
        self.btn_gen.pack(fill="x", padx=20, pady=(40, 10))

        self.btn_deploy = ctk.CTkButton(self.left, text="☁️ DEPLOY TO CLOUDFLARE", font=("Arial", 16, "bold"), height=50, fg_color="#2563eb", text_color="white", command=self.auto_deploy)
        self.btn_deploy.pack(fill="x", padx=20, pady=10)

    def log_status(self, msg):
        self.guide.insert("end", f"\n> {msg}")
        self.guide.see("end")
        self.update_idletasks()

    def auto_deploy(self):
        import threading
        # รันใน Thread แยกเพื่อไม่ให้ GUI ค้าง
        threading.Thread(target=self._exec_deploy_flow, daemon=True).start()

    def _exec_deploy_flow(self):
        import subprocess
        import re
        shop = self.ent_shop.get()
        out_dir = f"V86_CRM_{shop.replace(' ', '_')}"
        
        if not os.path.exists(out_dir):
            messagebox.showwarning("V86", "โปรดกด BUILD CRM SYSTEM ก่อน")
            return

        self.btn_deploy.configure(state="disabled", text="⌛ CHECKING ACCOUNT...")
        self.log_status(f"กำลังเริ่มระบบ Deploy สำหรับ {shop}...")

        try:
            # 1. วิ่งไปถาม Cloudflare ว่าใครล็อกอินอยู่
            self.log_status("กำลังเรียกข้อมูลบัญชีจาก Cloudflare (wrangler whoami)...")
            whoami = subprocess.check_output("npx wrangler whoami", shell=True, stderr=subprocess.STDOUT).decode()
            
            # ดึง Email แบบละเอียดยิ่งขึ้น
            email_match = re.search(r'email\s+([^\s]+)', whoami) or re.search(r'\[([^\]]+)\]', whoami)
            current_email = email_match.group(1) if email_match else "Unknown (บัญชีปัจจุบันของคุณ)"

            # 2. กระโดดออกมาถามหน้าเว็บ (หน้าจอหลัก)
            self.log_status(f"พบบัญชี: {current_email}")
            
            conf_msg = f"�️ ตรวจพบการล็อกอิน:\n--------------------------\nEmail: {current_email}\n--------------------------\n\nนี่คือบัญชีของร้าน '{shop}' ใช่หรือไม่?\n(ถ้ากด Yes ระบบจะเริ่ม Deploy ทันที)"
            
            if not messagebox.askyesno("ยืนยันตัวตน Cloudflare", conf_msg):
                self.log_status("❌ ผู้ใช้ยกเลิกการ Deploy เนื่องจากบัญชีไม่ถูกต้อง")
                self.btn_deploy.configure(state="normal", text="☁️ DEPLOY TO CLOUDFLARE")
                return

            # 3. เริ่มการ Deploy
            self.log_status("🚀 เริ่มการ Deploy ขึ้น Cloudflare Workers... (ขั้นตอนนี้อาจใช้เวลา 10-30 วินาที)")
            
            # สร้าง wrangler.toml อัตโนมัติถ้าไม่มี
            w_toml = f"{out_dir}/wrangler.toml"
            if not os.path.exists(w_toml):
                with open(w_toml, "w") as f:
                    f.write(f'name = "v86-crm-{shop.lower().replace(" ", "-")}"\nmain = "worker.js"\ncompatibility_date = "2023-12-01"\n\n[[d1_databases]]\nbinding = "DB"\ndatabase_name = "v86_db"\n\n[[r2_buckets]]\nbinding = "BUCKET"\nbucket_name = "v86-photos"')

            # รันคำสั่ง deploy จริง
            deploy_res = subprocess.check_output(f"cd \"{out_dir}\" && npx wrangler deploy", shell=True, stderr=subprocess.STDOUT).decode()
            
            self.log_status("✅ DEPLOY สำเร็จ!")
            messagebox.showinfo("Success", f"ออนไลน์เรียบร้อยครับ!\nบัญชี: {current_email}")
            
        except Exception as e:
            err_msg = str(e.output.decode() if hasattr(e, 'output') else e)
            self.log_status(f"❌ เกิดข้อผิดพลาด: {err_msg[:100]}...")
            messagebox.showerror("Deploy Error", f"ความผิดพลาด:\n{err_msg}")
        
        self.btn_deploy.configure(state="normal", text="☁️ DEPLOY TO CLOUDFLARE")

        # RIGHT PANEL
        self.right = ctk.CTkFrame(self, fg_color="#000")
        self.right.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.guide = ctk.CTkTextbox(self.right, font=("Arial", 14), fg_color="#000", border_width=0)
        self.guide.pack(fill="both", expand=True, padx=30, pady=30)
        self.update_guide()

    def create_head(self, t): ctk.CTkLabel(self.left, text=t, font=("Arial", 13, "bold"), text_color="#EAB308").pack(anchor="w", padx=20, pady=(20, 5))
    def create_in(self, l, d):
        f = ctk.CTkFrame(self.left, fg_color="transparent"); f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text=l, font=("Arial", 11)).pack(anchor="w")
        e = ctk.CTkEntry(f, height=35, corner_radius=8); e.insert(0, d); e.pack(fill="x"); return e
    def col_btn(self, f, l, k):
        btn_f = ctk.CTkFrame(f, fg_color="transparent"); btn_f.pack(side="left", fill="x", expand=True, padx=2)
        b = ctk.CTkButton(btn_f, text="", fg_color=self.colors[k], height=45, command=lambda: self.pick(k))
        b.pack(fill="x"); ctk.CTkLabel(btn_f, text=l, font=("Arial", 10)).pack(); return b

    def pick(self, k):
        c = colorchooser.askcolor(initialcolor=self.colors[k])[1]
        if c: self.colors[k] = c; self.update_colors()

    def update_colors(self):
        self.btn_bg.configure(fg_color=self.colors['bg']); self.btn_accent.configure(fg_color=self.colors['accent']); self.btn_grad.configure(fg_color=self.colors['grad_start'])

    def load_profiles(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    self.profiles = json.load(f)
                    self.profile_menu.configure(values=list(self.profiles.keys()))
            except: pass

    def on_profile_select(self, name):
        p = self.profiles.get(name)
        if not p: return
        self.ent_shop.delete(0, 'end'); self.ent_shop.insert(0, p.get('Shop Name', name))
        self.ent_liff.delete(0, 'end'); self.ent_liff.insert(0, p.get('LIFF ID', ''))
        self.ent_worker.delete(0, 'end'); self.ent_worker.insert(0, p.get('Worker URL', ''))
        c = p.get('colors', {})
        self.colors['bg'] = c.get('bg_color', self.colors['bg'])
        self.colors['accent'] = c.get('accent', self.colors['accent'])
        self.colors['grad_start'] = c.get('grad_start', self.colors['grad_start'])
        self.update_colors()

    def update_guide(self):
        self.guide.delete("0.0", "end")
        g = "--- V86 CRM & REWARDS ---\n\n"
        g += "💎 CRM Logic:\n"
        g += "- สมัครสมาชิกเบอร์โทรครั้งแรก: ได้ 50 แต้มฟรี\n"
        g += "- พนักงานรับฝากเหล้า: เลือกจำนวนแต้มที่จะให้ลูกค้าได้\n"
        g += "- หน้าร้านค้า (Rewards): ลูกค้ากดแลกแต้มได้เองจากใน LINE\n\n"
        g += "🛠 CRM Controls:\n"
        g += "- หน้า Staff จะมีฟีเจอร์ค้นหาเบอร์เพื่อ 'เพิ่ม/ลดแต้ม' โดยตรง\n"
        g += "- ทุกการกระทำจะมีการบันทึก Logs ใน Table point_logs"
        self.guide.insert("0.0", g)

    def generate(self):
        shop = self.ent_shop.get(); tier = self.tier_var.get(); pw = self.ent_pw.get()
        out = f"V86_CRM_{shop.replace(' ', '_')}"
        os.makedirs(out, exist_ok=True)
        
        html = HTML_TEMPLATE.replace("__SHOP_NAME__", shop)\
                             .replace("__LIFF_ID__", self.ent_liff.get())\
                             .replace("__WORKER_URL__", self.ent_worker.get())\
                             .replace("__COLOR_BG__", self.colors['bg'])\
                             .replace("__COLOR_ACCENT__", self.colors['accent'])\
                             .replace("__COLOR_GRAD_START__", self.colors['grad_start'])\
                             .replace("__COLOR_GRAD_END__", self.colors['grad_end'])
        
        if "Starter" in tier: html = html.replace("__TIER2_ONLY__", "hidden")
        else: html = html.replace("__TIER2_ONLY__", "")

        worker_code = WORKER_TEMPLATE.replace("__MANAGER_PASSWORD__", pw)

        with open(f"{out}/index.html", "w", encoding="utf-8") as f: f.write(html)
        with open(f"{out}/worker.js", "w", encoding="utf-8") as f: f.write(worker_code)
        
        sql = SQL_SCHEMA
        if self.ent_my_uid.get():
            sql += f"\nINSERT OR REPLACE INTO staff_access (uid, name, role) VALUES ('{self.ent_my_uid.get()}', 'Global Admin', 'manager');"
        with open(f"{out}/schema.sql", "w", encoding="utf-8") as f: f.write(sql)
        
        messagebox.showinfo("V86 CRM", f"สร้างระบบ CRM สำหรับ {shop} เรียบร้อย!")
        os.system(f"open {out}")

if __name__ == "__main__":
    app = V86MasterGenerator()
    app.mainloop()
