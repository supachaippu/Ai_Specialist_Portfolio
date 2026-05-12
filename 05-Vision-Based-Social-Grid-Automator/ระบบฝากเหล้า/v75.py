import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import os
import re
import json
import traceback
import shutil
import random
import time

# --- CONFIG ---
CONFIG_FILE = "config_superapp.json"
DEFAULT_THEME_COLOR = "#0e4296"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_config(data):
    try:
        current_data = load_config()
        current_data.update(data)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(current_data, f, ensure_ascii=False, indent=4)
    except: pass

saved = load_config()

# ==========================================
# 🧠 1. PASTE CONFIG UI
# ==========================================
def open_paste_window():
    popup = tk.Toplevel(root)
    popup.title("วางข้อมูล Config")
    popup.geometry("600x450")
    tk.Label(popup, text="วางข้อมูลที่นี่ 👇", font=("Arial", 14, "bold")).pack(pady=10)
    txt = tk.Text(popup, height=10, font=("Arial", 12)); txt.pack(fill="both", expand=True, padx=20, pady=10); txt.focus_set()

    def process():
        raw = txt.get("1.0", tk.END).strip()
        liff = re.search(r'(\d{10}-[a-zA-Z0-9-_]{4,20})', raw)
        worker = re.search(r'(https://[\w\.-]+\.workers\.dev)', raw)
        r2 = re.search(r'(https://[\w\.-]+\.r2\.dev)', raw)
        if not r2: r2 = re.search(r'(https://pub-[\w\.-]+\.r2\.dev)', raw)
        
        if liff: entry_liff.delete(0, tk.END); entry_liff.insert(0, liff.group(1))
        if worker: entry_worker.delete(0, tk.END); entry_worker.insert(0, worker.group(1))
        if r2: entry_r2.delete(0, tk.END); entry_r2.insert(0, r2.group(1))
        
        messagebox.showinfo("เสร็จ", "ดึงข้อมูลเรียบร้อย")
        popup.destroy()

    tk.Button(popup, text="⚡ แยกข้อมูล", command=process, bg="#2563eb", fg="white", font=("bold", 12), pady=10).pack(fill="x", padx=20, pady=20)

# ==========================================
# 🧠 2. GENERATE ALL (V.82 - Final Fix)
# ==========================================
def generate_all_files():
    try:
        # 1. รับค่า
        liff_id_deposit = entry_liff.get().strip()
        worker_url = entry_worker.get().strip().rstrip('/')
        r2_url = entry_r2.get().strip().rstrip('/')
        shop_name = entry_shop.get().strip()
        manager_pwd = entry_pwd.get().strip()
        liff_id_booking = entry_booking_liff.get().strip()
        booking_time = entry_booking_time.get().strip()
        theme_color = color_preview.cget('bg')

        # 2. บันทึก
        save_config({
            "liff_id": liff_id_deposit, "worker_url": worker_url, "r2_url": r2_url, 
            "shop_name": shop_name, "manager_pwd": manager_pwd,
            "booking_liff": liff_id_booking, "booking_time": booking_time, "theme_color": theme_color
        })

        # 3. สร้างโฟลเดอร์ (บังคับ Drive C)
        base_path = "C:\\Soundabout_App"
        if not os.path.exists(base_path): os.makedirs(base_path)
        folder_name = f"web_{shop_name}_V82_Final"
        folder = os.path.join(base_path, folder_name)
        if os.path.exists(folder):
            try: shutil.rmtree(folder)
            except: folder = os.path.join(base_path, f"web_{shop_name}_V82_{int(time.time())}")
        if not os.path.exists(folder): os.makedirs(folder)

        # ----------------------------------------------------
        # 1. HUB PAGE (index.html) - มีปุ่ม Staff ที่ซ่อนอยู่
        # ----------------------------------------------------
        hub_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__SHOP_NAME__ Hub</title><script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap" rel="stylesheet"><style>body{font-family:'Prompt',sans-serif;background-color:#0f172a;color:white;display:flex;flex-direction:column;min-height:100vh}.btn-menu{background:linear-gradient(135deg,__THEME_COLOR__,#1e293b);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:30px 20px;margin-bottom:20px;text-align:center;cursor:pointer;transition:transform 0.2s,box-shadow 0.2s;text-decoration:none;display:block;box-shadow:0 4px 15px rgba(0,0,0,0.3)}.btn-menu:active{transform:scale(0.98)}.btn-menu:hover{box-shadow:0 10px 25px rgba(__R_G_B__,0.4);border-color:rgba(255,255,255,0.3)}.icon{font-size:40px;margin-bottom:10px;display:block}.label{font-size:20px;font-weight:bold;display:block;color:white}.sub-label{font-size:14px;color:#94a3b8;display:block;margin-top:5px}.staff-zone{display:none;margin-top:40px;border-top:1px solid #334155;padding-top:20px}.staff-title{color:#ef4444;font-weight:bold;font-size:14px;letter-spacing:2px;margin-bottom:15px;text-transform:uppercase;text-align:center;background:#1e293b;display:inline-block;padding:0 10px;position:relative;top:-30px}</style></head><body class="p-6 justify-center max-w-md mx-auto w-full">
        <div class="text-center mb-8"><h1 class="text-2xl font-bold text-white mb-2">🍾 __SHOP_NAME__</h1><p class="text-gray-400 text-sm">ยินดีต้อนรับ กรุณาเลือกบริการ</p></div>
        <a href="https://liff.line.me/__LIFF_ID_BOOKING__" class="btn-menu"><span class="icon">📅</span><span class="label">จองโต๊ะ</span><span class="sub-label">สำรองที่นั่งล่วงหน้า</span></a>
        <a href="https://liff.line.me/__LIFF_ID_DEPOSIT__" class="btn-menu"><span class="icon">🥃</span><span class="label">ระบบฝากเหล้า</span><span class="sub-label">เช็ครายการฝาก / เบิกเหล้า / โอนสิทธิ์</span></a>
        <div id="staff-area" class="staff-zone text-center border-t border-gray-700">
             <span class="staff-title">⛔ Staff Only</span>
             <a href="staff.html" class="btn-menu" style="background: linear-gradient(135deg, #7f1d1d, #450a0a); border-color: #ef4444;">
                <span class="icon">👮</span><span class="label text-red-100">ระบบพนักงาน</span><span class="sub-label text-red-300">เข้าสู่หน้าจัดการร้าน</span>
            </a>
        </div>
        <script>const LIFF_ID="__LIFF_ID_DEPOSIT__", WORKER_URL="__WORKER_URL__";
        async function checkStaff() { try { await liff.init({ liffId: LIFF_ID }); if (liff.isLoggedIn()) { const p = await liff.getProfile(); const r = await fetch(`${WORKER_URL}?action=check_staff&uid=${p.userId}`); const j = await r.json(); if (j.isStaff) { document.getElementById('staff-area').style.display = 'block'; } } } catch (e) {} }
        checkStaff();</script></body></html>"""
        
        hex_c = theme_color.lstrip('#'); rgb_c = f"{int(hex_c[0:2],16)},{int(hex_c[2:4],16)},{int(hex_c[4:6],16)}"
        hub_final = hub_template.replace("__SHOP_NAME__", shop_name).replace("__THEME_COLOR__", theme_color).replace("__R_G_B__", rgb_c).replace("__LIFF_ID_DEPOSIT__", liff_id_deposit).replace("__LIFF_ID_BOOKING__", liff_id_booking).replace("__WORKER_URL__", worker_url)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f: f.write(hub_final)

        # ----------------------------------------------------
        # 2. DEPOSIT PAGE (deposit.html) - ฝั่งลูกค้า
        # ----------------------------------------------------
        deposit_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>รายการฝาก</title><script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script><script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script><style>:root{--theme-color:__THEME_COLOR__}.bg-theme{background-color:var(--theme-color)}.text-theme{color:var(--theme-color)}.tab-active{border-bottom:3px solid var(--theme-color);color:var(--theme-color);font-weight:bold}.tab-inactive{color:#9ca3af}.progress-bar-fill{transition:width 0.5s ease-in-out}.urgent{animation:pulse-red 2s infinite;border:2px solid #ef4444!important;background-color:#fef2f2!important}@keyframes pulse-red{0%{box-shadow:0 0 0 0 rgba(239,68,68,0.7)}70%{box-shadow:0 0 0 10px rgba(239,68,68,0)}100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}}</style></head><body class="p-4 bg-gray-50 pb-20">
        <a href="index.html" class="mb-4 inline-block text-sm text-gray-500 hover:text-gray-800">← กลับหน้าหลัก</a>
        <div class="max-w-md mx-auto bg-white rounded-xl shadow-sm overflow-hidden mb-4">
            <div class="p-4 bg-theme text-white text-center"><h1 class="text-xl font-bold">🍾 __SHOP_NAME__</h1><p class="text-sm opacity-90">ระบบจัดการฝากดื่ม</p><div id="points-badge" class="mt-2 inline-block bg-white/20 px-3 py-1 rounded-full text-xs hidden">⭐ แต้มสะสม: <span id="user-points">0</span></div></div>
        </div>
        <div id="alert-area" class="max-w-md mx-auto mb-4 hidden"></div>
        <div class="max-w-md mx-auto bg-white rounded-t-xl shadow-sm border-b flex mb-0 sticky top-0 z-10"><button onclick="switchTab('active')" id="tab-active" class="flex-1 py-3 text-center transition-all tab-active">🍾 ฝากอยู่</button><button onclick="switchTab('history')" id="tab-history" class="flex-1 py-3 text-center transition-all tab-inactive">📜 ประวัติ</button></div>
        <div class="max-w-md mx-auto bg-white rounded-b-xl shadow-md p-6 min-h-[400px]"><div id="status" class="text-center text-gray-500 mt-10">กำลังโหลด...</div><div id="listContainer" class="space-y-4"></div></div>
        <script>const LIFF_ID="__LIFF_ID__",WORKER_URL="__WORKER_URL__",R2_URL="__R2_URL__"; let currentUid=null, pollInterval=null;
        async function main(){ if(!WORKER_URL) return; await liff.init({liffId:LIFF_ID}); if(!liff.isLoggedIn()){liff.login();return} const p = await liff.getProfile(); currentUid = p.userId; const t = new URLSearchParams(location.search).get('token'); if(t) handleReceive(p.userId, t); else fetchList(p.userId, 'active'); fetchPoints(p.userId); if('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js'); }
        async function fetchPoints(uid) { try{const r=await fetch(`${WORKER_URL}?action=get_points&uid=${uid}`);const j=await r.json();if(j.points!==undefined){document.getElementById('user-points').innerText=j.points;document.getElementById('points-badge').classList.remove('hidden');}}catch(e){} }
        async function fetchList(uid, type) { const c=document.getElementById('listContainer'); c.innerHTML=''; document.getElementById('status').style.display='block'; try { const r=await fetch(`${WORKER_URL}?uid=${uid}&type=${type}`); const d=await r.json(); document.getElementById('status').style.display='none'; if(d.length===0){c.innerHTML='<div class="text-center py-10 text-gray-400">ไม่มีรายการ</div>';return} let urgentCount=0; d.forEach(i=>{ const exp=new Date(i.expire_date), daysLeft=Math.ceil((exp-new Date())/(1000*60*60*24)); let alertHtml='', cardClass=''; if(type==='active'){ if(daysLeft<=3&&daysLeft>0){urgentCount++;cardClass='urgent';alertHtml=`<p class="text-red-600 font-bold text-xs animate-bounce mb-1">⚠️ หมดอายุใน ${daysLeft} วัน</p>`;} } const itemData=encodeURIComponent(JSON.stringify(i)); if(type==='active'){ c.innerHTML+=`<div class="bg-gray-50 p-3 rounded-xl border flex flex-col gap-3 ${cardClass}">${alertHtml}<div class="flex gap-3"><img src="${R2_URL}/${i.image_filename}" onclick="viewImage('${R2_URL}/${i.image_filename}')" class="w-24 h-32 object-cover rounded-lg bg-gray-200 border cursor-pointer"><div class="flex-1 flex flex-col justify-between"><div><h3 class="font-bold text-lg text-gray-800">${i.brand}</h3><span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-bold">${i.bottle_label}</span></div><div><div class="flex justify-between text-xs mb-1"><span>เหลือ</span><span class="font-bold">${i.percent}%</span></div><div class="w-full bg-gray-200 rounded-full h-2.5"><div class="bg-theme h-2.5 rounded-full" style="width:${i.percent}%"></div></div><p class="text-xs text-gray-500 mt-2 text-right">หมด: ${exp.toLocaleDateString('th-TH')}</p></div></div></div><div class="flex gap-2"><button onclick="actionWithdraw('${i.id}','${i.bottle_label}')" class="flex-1 bg-green-600 text-white py-2 rounded font-bold shadow active:scale-95">🍺 เบิกดื่ม</button><button onclick="actionTransfer('${i.id}','${itemData}')" class="flex-1 bg-blue-600 text-white py-2 rounded font-bold shadow active:scale-95">🎁 ส่งต่อ</button></div></div>`; } else { c.innerHTML+=`<div class="bg-gray-50 p-3 rounded-xl border flex gap-3 opacity-75"><img src="${R2_URL}/${i.image_filename}" class="w-16 h-16 object-cover rounded bg-gray-200"><div class="flex-1"><h3 class="font-bold text-gray-700">${i.brand}</h3><div class="text-xs text-green-600 font-bold">✅ เบิกแล้ว: ${new Date(i.updated_at).toLocaleDateString('th-TH')}</div></div></div>`; } }); const alertArea=document.getElementById('alert-area'); if(urgentCount>0&&type==='active'){alertArea.classList.remove('hidden');alertArea.innerHTML=`<div class="bg-red-50 border-l-4 border-red-500 p-3 rounded shadow text-red-700 text-sm font-bold">⚠️ มี ${urgentCount} รายการใกล้หมดอายุ! รีบมาดื่มนะ</div>`;}else alertArea.classList.add('hidden'); } catch(e){document.getElementById('status').innerText='Error: '+e.message;} }
        function switchTab(t){document.getElementById('tab-active').className=t==='active'?'flex-1 py-3 text-center transition-all tab-active':'flex-1 py-3 text-center transition-all tab-inactive';document.getElementById('tab-history').className=t==='history'?'flex-1 py-3 text-center transition-all tab-active':'flex-1 py-3 text-center transition-all tab-inactive';fetchList(currentUid,t);}
        function actionWithdraw(id,label){const qrData="PICKUP|"+id;Swal.fire({title:'ยื่นให้พนักงานสแกน',html:`<div id="qrcode" class="flex justify-center my-4"></div><p class="text-3xl font-bold text-blue-600">${label}</p><p class="text-red-500 animate-pulse mt-2">⏳ ปิดใน <span id="timer">60</span> วิ</p>`,showConfirmButton:false,showCloseButton:true,didOpen:()=>{new QRCode(document.getElementById("qrcode"),{text:qrData,width:200,height:200});startPolling(id);},willClose:()=>clearInterval(pollInterval)});}
        function startPolling(id){let timeLeft=60;pollInterval=setInterval(async()=>{timeLeft--;const t=document.getElementById('timer');if(t)t.innerText=timeLeft;if(timeLeft<=0){clearInterval(pollInterval);Swal.close();return;}try{const r=await fetch(`${WORKER_URL}?action=check_status`,{method:'POST',body:JSON.stringify({id:id})});const j=await r.json();if(j.status==='success'&&j.itemStatus==='picked_up'){clearInterval(pollInterval);Swal.fire('✅ สำเร็จ','เบิกดื่มเรียบร้อย ขอให้สนุก!','success').then(()=>fetchList(currentUid,'active'));}}catch(e){}},2500);}
        async function actionTransfer(id,itemDataStr){Swal.fire({title:'กำลังสร้าง Link...',didOpen:()=>Swal.showLoading()});try{const r=await fetch(`${WORKER_URL}?action=gen_token`,{method:'POST',body:JSON.stringify({id:id,lineUid:currentUid})});const j=await r.json();if(j.status==='success'){Swal.close();if(liff.isApiAvailable('shareTargetPicker')){const link=`https://liff.line.me/${LIFF_ID}?token=${j.token}`;const item=JSON.parse(decodeURIComponent(itemDataStr));const msg={type:"flex",altText:"🍾 มีคนส่งเหล้าให้คุณ!",contents:{type:"bubble",hero:{type:"image",url:`${R2_URL}/${item.image_filename}`,size:"full",aspectRatio:"20:13",aspectMode:"cover"},body:{type:"box",layout:"vertical",contents:[{type:"text",text:"🎁 คุณได้รับของฝาก",weight:"bold",size:"xl",color:"#16a34a"},{type:"text",text:`${item.brand} (${item.percent}%)`,size:"md",margin:"md"}]},footer:{type:"box",layout:"vertical",contents:[{type:"button",style:"primary",color:"#0e4296",action:{type:"uri",label:"กดรับของขวัญ",uri:link}}]}}};liff.shareTargetPicker([msg]).then(res=>{if(res)Swal.fire('ส่งแล้ว','เพื่อนของคุณได้รับ Link แล้ว','success');});}else{Swal.fire('แชร์ไม่ได้','กรุณาเปิดใน LINE Mobile','warning');}}else{Swal.fire('Error','สร้าง Link ไม่สำเร็จ','error');}}catch(e){Swal.fire('Error',e.message,'error');}}
        async function handleReceive(uid,token){Swal.fire({title:'กำลังรับของ...',didOpen:()=>Swal.showLoading()});try{const r=await fetch(`${WORKER_URL}?action=claim`,{method:'POST',body:JSON.stringify({lineUid:uid,claimToken:token})});const j=await r.json();if(j.status==='success')Swal.fire('ยินดีด้วย!','คุณได้รับของฝากแล้ว','success').then(()=>{history.replaceState(null,'',location.pathname);fetchList(uid,'active');});else Swal.fire('เสียใจด้วย',j.message,'error').then(()=>{history.replaceState(null,'',location.pathname);fetchList(uid,'active');});}catch(e){Swal.fire('Error',e.message,'error');}}
        function viewImage(url){Swal.fire({imageUrl:url,width:600,showCloseButton:true,confirmButtonText:'ปิด'});}
        main();</script></body></html>"""
        
        deposit_final = deposit_template.replace("__LIFF_ID__", liff_id_deposit).replace("__WORKER_URL__", worker_url).replace("__R2_URL__", r2_url).replace("__SHOP_NAME__", shop_name).replace("__THEME_COLOR__", theme_color)
        with open(os.path.join(folder, "deposit.html"), "w", encoding="utf-8") as f: f.write(deposit_final)

        # ----------------------------------------------------
        # 3. STAFF PAGE (staff.html) - แก้ระบบ Delete Staff
        # ----------------------------------------------------
        staff_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Staff</title><script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script><script src="https://unpkg.com/html5-qrcode"></script><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script><script src="https://cdn.tailwindcss.com"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script><style>.tab-active{background-color:#0f172a;color:white}.tab-inactive{background-color:#e2e8f0;color:#64748b}</style></head><body class="bg-gray-100 p-4">
        <div id="auth-screen" class="max-w-md mx-auto bg-white rounded-xl shadow-md p-6 text-center mt-10 hidden">
            <h2 class="text-xl font-bold mb-4">👮 Staff Access</h2><p id="auth-msg" class="text-gray-500 mb-4">กำลังตรวจสอบ...</p>
            <button id="req-btn" onclick="requestAccess()" class="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hidden">ขอสิทธิ์พนักงาน</button>
            <div id="admin-login-box" class="mt-8 pt-8 border-t hidden"><p class="text-xs text-gray-400 mb-2">เข้าด้วยรหัสผู้จัดการ</p><input type="password" id="mgr-pwd-input" placeholder="รหัสผู้จัดการ" class="border p-2 rounded w-full mb-2 text-center"><button onclick="loginAsManager()" class="bg-gray-800 text-white px-4 py-2 rounded w-full">Login Admin</button></div>
        </div>
        <div id="app-screen" class="hidden max-w-md mx-auto pb-20">
            <div class="bg-white rounded-xl shadow-md mb-4 p-4 text-center"><h1 class="text-lg font-bold text-gray-800">👮 __SHOP_NAME__ Staff</h1><p id="staff-name-display" class="text-xs text-gray-500"></p><div class="flex mt-4 gap-1"><button onclick="tab('deposit')" id="btn-deposit" class="flex-1 py-2 rounded font-bold tab-active">ฝาก</button><button onclick="tab('withdraw')" id="btn-withdraw" class="flex-1 py-2 rounded font-bold tab-inactive">เบิก</button><button onclick="tab('admin')" id="btn-admin" class="flex-1 py-2 rounded font-bold tab-inactive bg-red-50 text-red-600 hidden">Admin</button></div></div>
            <div id="sec-deposit"><div class="bg-white rounded-xl shadow p-6 mb-4"><button onclick="getRunningNumber()" class="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold text-xl shadow mb-4">🔢 ขอรหัสฝากใหม่</button><div id="new-deposit-form" class="hidden"><div class="text-center mb-4"><span class="text-sm text-gray-500">รหัสขวด</span><div id="gen-code" class="text-4xl font-black text-blue-600">0000</div></div><input type="file" id="cam" accept="image/*" capture="environment" class="hidden" onchange="previewImage(this)"><button onclick="document.getElementById('cam').click()" class="w-full bg-gray-200 py-3 rounded-lg mb-2 font-bold text-gray-700">📷 ถ่ายรูปขวด</button><img id="img-preview" class="w-full h-48 object-cover rounded-lg mb-2 hidden"><input id="inp-brand" placeholder="ยี่ห้อ" class="w-full border p-2 rounded mb-2"><input id="inp-percent" type="number" placeholder="%" class="w-full border p-2 rounded mb-2"><input id="inp-note" placeholder="ชื่อลูกค้า" class="w-full border-2 border-yellow-200 bg-yellow-50 p-2 rounded mb-2"><button onclick="submitDeposit()" class="w-full bg-green-600 text-white py-3 rounded-lg font-bold text-lg shadow">✅ ยืนยัน</button></div></div><div class="bg-white rounded-xl shadow p-4"><h3 class="font-bold text-gray-600 mb-2 border-b pb-2">รายการล่าสุด</h3><div id="recent-list" class="space-y-2"></div></div></div>
            <div id="sec-withdraw" class="hidden"><div class="bg-white rounded-xl shadow p-4 text-center"><div id="reader" class="w-full bg-black min-h-[250px] rounded-lg mb-4"></div><p class="text-sm text-gray-500 mb-2">สแกน QR ลูกค้า</p><div class="flex gap-2 border-t pt-4"><input id="manual-code" placeholder="กรอกรหัสขวด" class="flex-1 border p-2 rounded text-center font-bold"><button onclick="manualWithdraw()" class="bg-blue-600 text-white px-4 rounded font-bold">เบิก</button></div></div></div>
            <div id="sec-admin" class="hidden">
                <div class="bg-white rounded-xl shadow p-4 mb-4"><h3 class="font-bold border-b pb-2 mb-2">👥 จัดการพนักงาน</h3><div id="staff-list" class="space-y-2 max-h-60 overflow-y-auto"></div></div>
                <div class="bg-white rounded-xl shadow p-4"><h3 class="font-bold border-b pb-2 mb-2">📦 สต็อกสินค้า</h3><div class="flex gap-2 mb-2"><input id="search-box" placeholder="ค้นหา..." class="flex-1 border p-2 rounded" onkeyup="searchItems()"></div><div class="flex gap-2 mb-2 text-sm"><label><input type="checkbox" id="chk-all" onchange="toggleAll(this)"> เลือกทั้งหมด</label><button onclick="bulkExtend()" class="text-blue-600 font-bold ml-auto">ต่ออายุ</button><button onclick="bulkDelete()" class="text-red-600 font-bold ml-2">ลบ</button></div><div class="overflow-x-auto"><table class="w-full text-sm text-left"><thead class="bg-gray-100"><tr><th class="p-2"></th><th class="p-2">รายละเอียด</th><th class="p-2">สถานะ</th></tr></thead><tbody id="stock-table"></tbody></table></div></div>
                <div class="mt-4 text-center"><button onclick="viewAuditLog()" class="text-gray-500 text-xs underline">Audit Log</button></div>
            </div>
        </div>
        <div id="qr-modal" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center z-50" onclick="this.classList.add('hidden')"><div class="bg-white p-6 rounded-xl text-center" onclick="event.stopPropagation()"><div id="qrcode"></div><p class="mt-2 font-bold text-lg" id="qr-label"></p><button onclick="document.getElementById('qr-modal').classList.add('hidden')" class="mt-4 bg-gray-200 px-4 py-2 rounded">ปิด</button></div></div>
        <script>
        const LIFF_ID="__LIFF_ID__",WORKER_URL="__WORKER_URL__",R2_URL="__R2_URL__",MANAGER_PWD="__MANAGER_PWD__"; let currentUser=null,html5QrCode=null,currentGenId=null,allStock=[];
        async function init(){ document.getElementById('auth-screen').classList.remove('hidden'); await liff.init({liffId:LIFF_ID}); if(!liff.isLoggedIn()){liff.login();return} const p=await liff.getProfile(); currentUser=p; const r=await fetch(`${WORKER_URL}?action=check_staff&uid=${p.userId}`); const j=await r.json(); if(j.isStaff){document.getElementById('auth-screen').classList.add('hidden');document.getElementById('app-screen').classList.remove('hidden');document.getElementById('staff-name-display').innerText=`สวัสดี, ${j.name}`;if(j.role==='manager'){document.getElementById('btn-admin').classList.remove('hidden');loadStaffList();loadStock();}}else{document.getElementById('auth-msg').innerText="ยังไม่มีสิทธิ์";document.getElementById('req-btn').classList.remove('hidden');document.getElementById('admin-login-box').classList.remove('hidden');} }
        async function requestAccess(){ await fetch(`${WORKER_URL}?action=req_staff`,{method:'POST',body:JSON.stringify({uid:currentUser.userId,name:currentUser.displayName})}); Swal.fire('ส่งคำขอแล้ว','แจ้งผู้จัดการให้กดรับ','success'); }
        async function loginAsManager(){ if(document.getElementById('mgr-pwd-input').value===MANAGER_PWD){ await fetch(`${WORKER_URL}?action=promote_manager`,{method:'POST',body:JSON.stringify({uid:currentUser.userId,name:currentUser.displayName,pwd:MANAGER_PWD})}); location.reload(); }else Swal.fire('รหัสผิด'); }
        function tab(t){ ['deposit','withdraw','admin'].forEach(x=>{document.getElementById('sec-'+x).classList.add('hidden');document.getElementById('btn-'+x).className='flex-1 py-2 rounded font-bold tab-inactive';}); document.getElementById('sec-'+t).classList.remove('hidden'); document.getElementById('btn-'+t).className='flex-1 py-2 rounded font-bold tab-active'; if(t==='withdraw')startScanner();else stopScanner(); }
        async function getRunningNumber(){ const r=await fetch(`${WORKER_URL}?action=get_next_id`); const j=await r.json(); currentGenId=j.nextId; document.getElementById('gen-code').innerText=j.nextId; document.getElementById('new-deposit-form').classList.remove('hidden'); }
        async function submitDeposit(){ const f=document.getElementById('cam').files[0]; if(!f)return Swal.fire('ถ่ายรูปก่อน'); Swal.fire({title:'Upload...',didOpen:()=>Swal.showLoading()}); const img=await compressImage(f); const fd=new FormData(); fd.append('image',img); fd.append('brand',document.getElementById('inp-brand').value); fd.append('percent',document.getElementById('inp-percent').value); fd.append('note',document.getElementById('inp-note').value); fd.append('bottle_label',currentGenId); fd.append('staff_name',currentUser.displayName); try{ const r=await fetch(WORKER_URL,{method:'POST',body:fd}); const j=await r.json(); if(j.status==='success'){ const link=`https://liff.line.me/${LIFF_ID}?token=${j.claimToken}`; document.getElementById('qr-modal').classList.remove('hidden'); document.getElementById('qrcode').innerHTML=''; new QRCode(document.getElementById('qrcode'),{text:link,width:200,height:200}); document.getElementById('qr-label').innerText=currentGenId; Swal.close(); document.getElementById('new-deposit-form').classList.add('hidden'); } }catch(e){Swal.fire('Error',e.message);} }
        function compressImage(file){return new Promise((resolve)=>{const img=new Image();img.src=URL.createObjectURL(file);img.onload=()=>{const cvs=document.createElement('canvas');const mw=800;const sc=mw/img.width;cvs.width=mw;cvs.height=img.height*sc;const ctx=cvs.getContext('2d');ctx.drawImage(img,0,0,cvs.width,cvs.height);cvs.toBlob((b)=>resolve(b),'image/jpeg',0.6);};});}
        function previewImage(i){if(i.files[0]){const r=new FileReader();r.onload=e=>{document.getElementById('img-preview').src=e.target.result;document.getElementById('img-preview').classList.remove('hidden');};r.readAsDataURL(i.files[0])}}
        function startScanner(){ html5QrCode=new Html5Qrcode("reader"); html5QrCode.start({facingMode:"environment"},{fps:10,qrbox:250},(t)=>{if(t.startsWith('PICKUP|'))confirmPickup(t.split('|')[1]);}).catch(()=>{}); }
        function stopScanner(){ if(html5QrCode)html5QrCode.stop().catch(()=>{}); }
        async function manualWithdraw(){ const j=await(await fetch(`${WORKER_URL}?action=find_by_code&code=${document.getElementById('manual-code').value}`)).json(); if(j.found)confirmPickup(j.id); else Swal.fire('ไม่พบ'); }
        function confirmPickup(id){ Swal.fire({title:'เบิก?',showCancelButton:true}).then(async(r)=>{if(r.isConfirmed){ await fetch(`${WORKER_URL}?action=pickup`,{method:'POST',body:JSON.stringify({id:id,staff:currentUser.displayName})}); Swal.fire('สำเร็จ'); }}); }
        async function loadStaffList(){ const list=await(await fetch(`${WORKER_URL}?action=list_staff&pwd=${MANAGER_PWD}`)).json(); document.getElementById('staff-list').innerHTML=list.map(s=>`<div class="flex justify-between items-center bg-gray-50 p-2 rounded border"><div><span class="font-bold">${s.name}</span> <span class="text-xs text-gray-500">(${s.status})</span></div><div>${s.status==='active'?`<button onclick="deleteStaff('${s.uid}','${s.name}')" class="text-red-500 border border-red-500 px-2 py-1 rounded text-xs">ลบสิทธิ์</button>`:`<button onclick="approveStaff('${s.uid}')" class="bg-green-600 text-white px-2 py-1 rounded text-xs mr-1">รับ</button><button onclick="deleteStaff('${s.uid}','${s.name}')" class="text-red-500 border border-red-500 px-2 py-1 rounded text-xs">ลบ</button>`}</div></div>`).join(''); }
        async function approveStaff(uid){ await fetch(`${WORKER_URL}?action=approve_staff&pwd=${MANAGER_PWD}`,{method:'POST',body:JSON.stringify({uid:uid})}); loadStaffList(); }
        async function deleteStaff(uid,n){ if(confirm(`ลบ ${n}?`)){ await fetch(`${WORKER_URL}?action=delete_staff&pwd=${MANAGER_PWD}`,{method:'POST',body:JSON.stringify({uid:uid})}); loadStaffList(); } }
        async function loadStock(){ allStock=await(await fetch(`${WORKER_URL}?action=list_stock&pwd=${MANAGER_PWD}`)).json(); renderStock(allStock); }
        function renderStock(l){ document.getElementById('stock-table').innerHTML=l.map(i=>`<tr class="border-b"><td class="p-2"><input type="checkbox" class="stock-chk" value="${i.id}"></td><td class="p-2"><b>${i.bottle_label}</b> ${i.brand}<br><span class="text-xs">${i.note||''}</span></td><td class="p-2 text-xs">${i.expire_date.split('T')[0]}</td></tr>`).join(''); }
        function searchItems(){ const q=document.getElementById('search-box').value.toLowerCase(); renderStock(allStock.filter(i=>(i.brand+i.bottle_label+i.note).toLowerCase().includes(q))); }
        async function bulkExtend(){ const ids=[...document.querySelectorAll('.stock-chk:checked')].map(c=>c.value); if(ids.length>0&&confirm('ต่ออายุ?')) { await fetch(`${WORKER_URL}?action=bulk_extend&pwd=${MANAGER_PWD}`,{method:'POST',body:JSON.stringify({ids:ids})}); loadStock(); } }
        async function viewAuditLog(){ const l=await(await fetch(`${WORKER_URL}?action=audit_log&pwd=${MANAGER_PWD}`)).json(); Swal.fire({title:'Log',html:`<div class='max-h-60 overflow-y-auto text-left text-xs'>${l.map(x=>`<div class='border-b py-1'>${x.timestamp.split('T')[0]} <b>${x.actor_name}</b>: ${x.action} ${x.details}</div>`).join('')}</div>`}); }
        init();
        </script></body></html>"""
        with open(os.path.join(folder, "staff.html"), "w", encoding="utf-8") as f: f.write(staff_template.replace("__LIFF_ID__", liff_id_deposit).replace("__WORKER_URL__", worker_url).replace("__SHOP_NAME__", shop_name).replace("__MANAGER_PWD__", manager_pwd).replace("__R2_URL__", r2_url))

        # ----------------------------------------------------
        # 4. WORKER (index.js)
        # ----------------------------------------------------
        worker_template = """
        const MANAGER_PWD = "__MANAGER_PWD__";
        export default {
          async fetch(request, env) {
            const url = new URL(request.url);
            const headers = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': '*', 'Access-Control-Allow-Headers': '*' };
            if (request.method === 'OPTIONS') return new Response(null, { headers });
            try {
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS bottles (id TEXT PRIMARY KEY, line_uid TEXT, brand TEXT, percent INTEGER, image_filename TEXT, status TEXT, created_at TEXT, updated_at TEXT, expire_date TEXT, claim_token TEXT, bottle_label TEXT, note TEXT, staff_name TEXT, points_awarded INTEGER DEFAULT 0)`).run();
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS staff_users (uid TEXT PRIMARY KEY, name TEXT, role TEXT, status TEXT, created_at TEXT)`).run();
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS user_points (uid TEXT PRIMARY KEY, points INTEGER)`).run();
                await env.DB.prepare(`CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, actor_uid TEXT, actor_name TEXT, details TEXT, timestamp TEXT)`).run();
                const action = url.searchParams.get('action');
                const log = async (act, uid, name, det) => { await env.DB.prepare("INSERT INTO audit_logs (action, actor_uid, actor_name, details, timestamp) VALUES (?, ?, ?, ?, ?)").bind(act, uid, name, det, new Date().toISOString()).run(); };

                if (request.method === 'POST') {
                    if (!action) {
                        const fd = await request.formData();
                        const id = crypto.randomUUID(), token = crypto.randomUUID(), now = new Date().toISOString(), exp = new Date(Date.now() + 30*24*60*60*1000).toISOString();
                        await env.BUCKET.put(fd.get('image').name, fd.get('image'));
                        await env.DB.prepare(`INSERT INTO bottles (id, line_uid, brand, percent, image_filename, status, created_at, updated_at, expire_date, claim_token, bottle_label, note, staff_name, points_awarded) VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, 0)`).bind(id, '', fd.get('brand'), fd.get('percent'), fd.get('image').name, now, now, exp, token, fd.get('bottle_label'), fd.get('note'), fd.get('staff_name')).run();
                        await log('DEPOSIT', 'staff', fd.get('staff_name'), `Deposited ${fd.get('bottle_label')}`);
                        return new Response(JSON.stringify({ status: 'success', claimToken: token }), { headers });
                    }
                    if (action === 'claim') {
                        const b = await request.json();
                        const res = await env.DB.prepare("UPDATE bottles SET line_uid = ?, claim_token = NULL, updated_at = ? WHERE claim_token = ? AND status = 'active'").bind(b.lineUid, new Date().toISOString(), b.claimToken).run();
                        if (res.meta.changes > 0) { await env.DB.prepare(`INSERT INTO user_points (uid, points) VALUES (?, 10) ON CONFLICT(uid) DO UPDATE SET points = points + 10`).bind(b.lineUid).run(); return new Response(JSON.stringify({ status: 'success' }), { headers }); }
                        return new Response(JSON.stringify({ status: 'error', message: 'Item not found' }), { headers });
                    }
                    if (action === 'pickup') {
                        const b = await request.json();
                        const item = await env.DB.prepare("SELECT line_uid FROM bottles WHERE id = ?").bind(b.id).first();
                        await env.DB.prepare("UPDATE bottles SET status = 'picked_up', updated_at = ? WHERE id = ?").bind(new Date().toISOString(), b.id).run();
                        if(item && item.line_uid) await env.DB.prepare(`INSERT INTO user_points (uid, points) VALUES (?, 5) ON CONFLICT(uid) DO UPDATE SET points = points + 5`).bind(item.line_uid).run();
                        await log('PICKUP', 'staff', b.staff, `Picked up ${b.id}`);
                        return new Response(JSON.stringify({ status: 'success' }), { headers });
                    }
                    if (action === 'gen_token') {
                        const b = await request.json();
                        const t = crypto.randomUUID();
                        await env.DB.prepare("UPDATE bottles SET claim_token = ? WHERE id = ? AND line_uid = ?").bind(t, b.id, b.lineUid).run();
                        return new Response(JSON.stringify({ status: 'success', token: t }), { headers });
                    }
                    if (action === 'req_staff') {
                        const b = await request.json();
                        await env.DB.prepare("INSERT OR IGNORE INTO staff_users (uid, name, role, status, created_at) VALUES (?, ?, 'staff', 'pending', ?)").bind(b.uid, b.name, new Date().toISOString()).run();
                        return new Response('OK', {headers});
                    }
                    if (action === 'approve_staff') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Auth Fail', {headers});
                        const b = await request.json();
                        await env.DB.prepare("UPDATE staff_users SET status = 'active' WHERE uid = ?").bind(b.uid).run();
                        return new Response('OK', {headers});
                    }
                    if (action === 'delete_staff') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Auth Fail', {headers});
                        const b = await request.json();
                        await env.DB.prepare("DELETE FROM staff_users WHERE uid = ?").bind(b.uid).run();
                        return new Response('OK', {headers});
                    }
                    if (action === 'bulk_extend') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Auth Fail', {headers});
                        const b = await request.json();
                        for(const id of b.ids) { const item = await env.DB.prepare("SELECT expire_date FROM bottles WHERE id=?").bind(id).first(); if(item) { const newExp = new Date(new Date(item.expire_date).getTime() + 30*24*60*60*1000).toISOString(); await env.DB.prepare("UPDATE bottles SET expire_date=? WHERE id=?").bind(newExp, id).run(); } }
                        return new Response('OK', {headers});
                    }
                    if (action === 'promote_manager') {
                        const b = await request.json();
                        if(b.pwd === MANAGER_PWD) await env.DB.prepare("INSERT OR REPLACE INTO staff_users (uid, name, role, status, created_at) VALUES (?, ?, 'manager', 'active', ?)").bind(b.uid, b.name, new Date().toISOString()).run();
                        return new Response('OK', {headers});
                    }
                    if (request.method === 'POST' && action === 'check_status') {
                         const b = await request.json();
                         const item = await env.DB.prepare("SELECT status FROM bottles WHERE id = ?").bind(b.id).first();
                         return new Response(JSON.stringify({ status: 'success', itemStatus: item ? item.status : 'unknown' }), { headers });
                    }
                }

                if (request.method === 'GET') {
                    const uid = url.searchParams.get('uid');
                    if (uid && url.searchParams.get('type')) {
                         const type = url.searchParams.get('type');
                         let sql = "SELECT * FROM bottles WHERE line_uid = ? AND status = 'active' ORDER BY expire_date ASC";
                         if(type === 'history') sql = "SELECT * FROM bottles WHERE line_uid = ? AND status = 'picked_up' ORDER BY updated_at DESC LIMIT 20";
                         const res = await env.DB.prepare(sql).bind(uid).all();
                         return new Response(JSON.stringify(res.results), { headers });
                    }
                    if (action === 'get_points') {
                        const res = await env.DB.prepare("SELECT points FROM user_points WHERE uid = ?").bind(uid).first();
                        return new Response(JSON.stringify({ points: res ? res.points : 0 }), { headers });
                    }
                    if (action === 'check_staff') {
                        const user = await env.DB.prepare("SELECT role, status, name FROM staff_users WHERE uid = ?").bind(uid).first();
                        if(user && user.status === 'active') return new Response(JSON.stringify({ isStaff: true, role: user.role, name: user.name }), { headers });
                        return new Response(JSON.stringify({ isStaff: false }), { headers });
                    }
                    if (action === 'get_next_id') {
                        const nextId = Math.floor(1000 + Math.random() * 9000).toString();
                        return new Response(JSON.stringify({ nextId: nextId }), { headers });
                    }
                    if (action === 'list_staff') {
                        if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Fail', {headers});
                        const res = await env.DB.prepare("SELECT * FROM staff_users").all();
                        return new Response(JSON.stringify(res.results), {headers});
                    }
                    if (action === 'list_stock') {
                         if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Fail', {headers});
                         const res = await env.DB.prepare("SELECT * FROM bottles WHERE status='active' ORDER BY expire_date ASC").all();
                         return new Response(JSON.stringify(res.results), {headers});
                    }
                    if (action === 'find_by_code') {
                        const code = url.searchParams.get('code');
                        const item = await env.DB.prepare("SELECT * FROM bottles WHERE bottle_label = ? AND status = 'active'").bind(code).first();
                        return new Response(JSON.stringify({ found: !!item, id: item?.id }), {headers});
                    }
                    if (action === 'audit_log') {
                         if(url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Fail', {headers});
                         const res = await env.DB.prepare("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50").all();
                         return new Response(JSON.stringify(res.results), {headers});
                    }
                }
                return new Response('404', { status: 404, headers });
            } catch (e) {
                return new Response(JSON.stringify({ error: e.message }), { status: 500, headers });
            }
          }
        };
        """
        with open(os.path.join(folder, "index.js"), "w", encoding="utf-8") as f: f.write(worker_template.replace("__MANAGER_PWD__", manager_pwd))
        
        sw_content = """self.addEventListener('install',e=>{e.waitUntil(caches.open('v1').then(c=>c.addAll(['deposit.html','staff.html','https://cdn.tailwindcss.com']))) });self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))) });"""
        with open(os.path.join(folder, "sw.js"), "w", encoding="utf-8") as f: f.write(sw_content)
        
        booking_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Booking</title><script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-900 text-white flex items-center justify-center h-screen"><div class="p-6 text-center"><h1 class="text-2xl mb-4">จองโต๊ะ</h1><input id="name" placeholder="ชื่อ" class="block w-full mb-2 p-2 rounded text-black"><input id="tel" placeholder="เบอร์โทร" class="block w-full mb-4 p-2 rounded text-black"><button onclick="book()" class="bg-blue-600 px-6 py-2 rounded">ยืนยัน</button></div><script>async function book(){ await liff.init({liffId:"__LIFF_ID__"}); if(!liff.isLoggedIn()){liff.login();return;} const name=document.getElementById('name').value; const tel=document.getElementById('tel').value; if(name&&tel){ liff.sendMessages([{type:'text',text:`จองโต๊ะ\nชื่อ: ${name}\nเบอร์: ${tel}`}]); liff.closeWindow(); } }</script></body></html>"""
        with open(os.path.join(folder, "booking.html"), "w", encoding="utf-8") as f: f.write(booking_template.replace("__LIFF_ID__", liff_id_booking))

        messagebox.showinfo("✅ V.82 สำเร็จ!", f"ไฟล์อยู่ที่: {folder}\n\n1. ก๊อปโค้ดใน index.js ไปใส่ Worker ใหม่\n2. อัปโหลด HTML ขึ้น Host\n3. ฟีเจอร์ครบ! (ลบสิทธิ์พนักงานได้แล้ว)")

    except Exception as e:
        err_msg = traceback.format_exc()
        messagebox.showerror("❌ Error", f"{err_msg}")

# ==========================================
# 🖥️ UI SETUP
# ==========================================
root = tk.Tk()
root.title("Super App V.82")
root.geometry("600x800")
root.configure(bg="#1e293b")

style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background="#1e293b", borderwidth=0)
style.configure("TNotebook.Tab", background="#334155", foreground="white", padding=[20, 10], font=("Arial", 11, "bold"))
style.map("TNotebook.Tab", background=[("selected", "#0e4296")], foreground=[("selected", "white")])
style.configure("TFrame", background="#1e293b")

tk.Label(root, text="🍾 Super App V.82 (Final)", font=("Arial", 20, "bold"), bg="#1e293b", fg="#38bdf8", pady=15).pack()
tk.Button(root, text="📝 Paste Config", command=open_paste_window, bg="#f59e0b", fg="white", font=("bold", 12), pady=8).pack(fill="x", padx=20, pady=5)

color_frame = tk.Frame(root, bg="#1e293b", padx=20, pady=10)
color_frame.pack(fill="x")
tk.Label(color_frame, text="🎨 ธีมสีหลัก:", font=("bold", 12), bg="#1e293b", fg="#ffab40").pack(side="left")
color_preview = tk.Label(color_frame, bg=saved.get("theme_color", DEFAULT_THEME_COLOR), width=8, height=2, relief="solid")
color_preview.pack(side="left", padx=10)
def pick_color():
    c = colorchooser.askcolor(color_preview.cget('bg'))[1]
    if c: color_preview.config(bg=c); save_config({"theme_color": c})
tk.Button(color_frame, text="เลือกสี", command=pick_color, bg="#475569", fg="white").pack(side="left")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=10)

tab_deposit = ttk.Frame(notebook)
notebook.add(tab_deposit, text="🍺 ส่วนฝากเหล้า")
f_d = tk.Frame(tab_deposit, bg="#1e293b", padx=20, pady=20)
f_d.pack(fill="both", expand=True)

def add_input(parent, lb, var, key, d=""):
    tk.Label(parent, text=lb, font=("bold", 10), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x", pady=(5,2))
    e = tk.Entry(parent, font=("Arial", 11), bg="#334155", fg="white", relief="flat", insertbackground="white")
    e.pack(fill="x", ipady=5); e.insert(0, saved.get(key, d))
    globals()[var] = e

add_input(f_d, "1. LIFF ID (ฝาก):", "entry_liff", "liff_id")
add_input(f_d, "2. Worker URL:", "entry_worker", "worker_url")
add_input(f_d, "3. R2 URL:", "entry_r2", "r2_url")
add_input(f_d, "4. ชื่อร้าน:", "entry_shop", "shop_name")
add_input(f_d, "5. รหัสผู้จัดการ:", "entry_pwd", "manager_pwd", "9999")

tab_booking = ttk.Frame(notebook)
notebook.add(tab_booking, text="📅 ส่วนจองโต๊ะ")
f_b = tk.Frame(tab_booking, bg="#1e293b", padx=20, pady=20)
f_b.pack(fill="both", expand=True)

add_input(f_b, "1. LIFF ID (จองโต๊ะ):", "entry_booking_liff", "booking_liff")
add_input(f_b, "2. เวลาปิดรับจอง (เช่น 20:30):", "entry_booking_time", "booking_time", "20:00")

tk.Label(root, text="👇 กดปุ่มนี้เพื่อสร้างไฟล์ทั้งหมด 👇", bg="#1e293b", fg="#94a3b8", font=("Arial", 10)).pack()
tk.Button(root, text="🚀 สร้าง Web App V.82 (Final)", command=generate_all_files, bg="#16a34a", fg="white", font=("bold", 14), pady=15).pack(fill="x", padx=20, pady=20)

root.mainloop()