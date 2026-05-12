import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import os
import re
import json
import traceback

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

def hex_to_rgb(hex_code):
    try:
        h = hex_code.lstrip('#')
        return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"
    except:
        return "14,66,150"

saved = load_config()

# ==========================================
# 🧠 1. PASTE CONFIG
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
# 🧠 2. GENERATE ALL (V.80 - Clean Version)
# ==========================================
def generate_all_files():
    try:
        # 1. รับค่า Config
        liff_id_deposit = entry_liff.get().strip()
        worker_url = entry_worker.get().strip().rstrip('/')
        r2_url = entry_r2.get().strip().rstrip('/')
        shop_name = entry_shop.get().strip()
        manager_pwd = entry_pwd.get().strip()
        liff_id_booking = entry_booking_liff.get().strip()
        booking_time = entry_booking_time.get().strip()
        theme_color = color_preview.cget('bg')
        theme_rgb = hex_to_rgb(theme_color)

        # 2. บันทึก
        save_config({
            "liff_id": liff_id_deposit, "worker_url": worker_url, "r2_url": r2_url, 
            "shop_name": shop_name, "manager_pwd": manager_pwd,
            "booking_liff": liff_id_booking, "booking_time": booking_time, "theme_color": theme_color
        })

        # 3. เตรียมโฟลเดอร์
        folder = f"web_{shop_name}_V80_Clean"
        if not os.path.exists(folder): os.makedirs(folder)

        # ---------------------------------------------------------
        # 📝 DEFINING ALL TEMPLATES
        # ---------------------------------------------------------

        # 1. COMMON HEAD
        common_head = """<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script><style>:root { --theme-color: __THEME_COLOR__; } .bg-theme { background-color: var(--theme-color); } .text-theme { color: var(--theme-color); } .btn-primary { background-color: var(--theme-color); color: white; } body { font-family: -apple-system, sans-serif; background-color: #f3f4f6; } .tab-active { background-color: var(--theme-color); color: white; } .tab-inactive { background-color: #e5e7eb; color: #374151; } @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } } .urgent { animation: pulse-red 2s infinite; border: 2px solid #ef4444 !important; background-color: #fef2f2 !important; } .progress-bar-bg { width: 100%; background-color: #e5e7eb; border-radius: 9999px; height: 10px; margin-top: 5px; } .progress-bar-fill { height: 10px; border-radius: 9999px; transition: width 0.5s ease-in-out; } input, select { font-size: 16px !important; } .big-id { font-size: 3rem; font-weight: 800; color: #2563eb; letter-spacing: 2px; line-height: 1; }</style>"""

        # 2. HUB HTML (Smart Hub)
        hub_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>__SHOP_NAME__ Hub</title><script charset="utf-8" src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script><script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script><link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap" rel="stylesheet"><style>body { font-family: 'Prompt', sans-serif; background-color: #0f172a; color: white; display: flex; flex-direction: column; min-height: 100vh; } .btn-menu { background: linear-gradient(135deg, __THEME_COLOR__, #1e293b); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 30px 20px; margin-bottom: 20px; text-align: center; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; text-decoration: none; display: block; box-shadow: 0 4px 15px rgba(0,0,0,0.3); } .btn-menu:active { transform: scale(0.98); } .btn-menu:hover { box-shadow: 0 10px 25px rgba(__R_G_B__, 0.4); border-color: rgba(255,255,255,0.3); } .icon { font-size: 40px; margin-bottom: 10px; display: block; } .label { font-size: 20px; font-weight: bold; display: block; color: white; } .sub-label { font-size: 14px; color: #94a3b8; display: block; margin-top: 5px; } #staff-section { display: none; border-top: 1px solid #334155; padding-top: 20px; margin-top: 20px; animation: fadeIn 1s; } @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } } </style></head><body class="p-6 justify-center max-w-md mx-auto w-full"><div class="text-center mb-8"><h1 class="text-2xl font-bold text-white mb-2">🍾 __SHOP_NAME__</h1><p id="welcome-msg" class="text-gray-400 text-sm">ยินดีต้อนรับ</p></div>
        
        <a href="https://liff.line.me/__LIFF_ID_BOOKING__" class="btn-menu"><span class="icon">📅</span><span class="label">จองโต๊ะ</span><span class="sub-label">สำรองที่นั่งล่วงหน้า</span></a>
        <a href="https://liff.line.me/__LIFF_ID_DEPOSIT__" class="btn-menu"><span class="icon">🥃</span><span class="label">ระบบฝากเหล้า</span><span class="sub-label">เช็ครายการฝากของฉัน</span></a>

        <div id="staff-section">
            <h3 class="text-gray-400 text-sm mb-4 text-center">🔐 สำหรับพนักงาน</h3>
            <a href="staff.html" class="btn-menu" style="background: linear-gradient(135deg, #059669, #064e3b);"><span class="icon">👮</span><span class="label">เข้าระบบพนักงาน</span><span class="sub-label">จัดการฝาก/เบิก (Staff Only)</span></a>
        </div>
        
        <script>
        const LIFF_ID = "__LIFF_ID_DEPOSIT__"; 
        const WORKER_URL = "__WORKER_URL__";

        async function main() {
            await liff.init({ liffId: LIFF_ID });
            if (!liff.isLoggedIn()) { liff.login(); return; }
            
            const profile = await liff.getProfile();
            document.getElementById('welcome-msg').innerText = `สวัสดีคุณ ${profile.displayName}`;

            // Check if user is staff
            checkStaffStatus(profile.userId);
            
            // Check query param for registration mode
            const urlParams = new URLSearchParams(window.location.search);
            if(urlParams.get('mode') === 'register'){
                registerStaff(profile);
            }
        }

        async function checkStaffStatus(uid) {
            try {
                const r = await fetch(`${WORKER_URL}?action=check_staff&uid=${uid}`);
                const j = await r.json();
                if (j.status === 'success' && j.role !== 'none') {
                    document.getElementById('staff-section').style.display = 'block';
                }
            } catch(e) { console.log(e); }
        }

        async function registerStaff(profile) {
            if(!profile) profile = await liff.getProfile();
            Swal.fire({
                title: 'ลงทะเบียนพนักงาน?',
                text: `คุณ ${profile.displayName} ต้องการขอสิทธิ์เข้าใช้งานระบบพนักงานใช่ไหม?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'ยืนยัน',
                cancelButtonText: 'ยกเลิก'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    Swal.fire({title:'กำลังส่งคำขอ...', didOpen:()=>Swal.showLoading()});
                    const r = await fetch(`${WORKER_URL}?action=request_staff`, {
                        method: 'POST',
                        body: JSON.stringify({ uid: profile.userId, name: profile.displayName })
                    });
                    const j = await r.json();
                    if(j.status === 'success') Swal.fire('ส่งคำขอแล้ว', 'กรุณาแจ้งผู้จัดการเพื่อกดอนุมัติ', 'success');
                    else Swal.fire('แจ้งเตือน', j.message, 'info');
                }
            });
        }
        main();
        </script>
        </body></html>"""
        
        # 3. DEPOSIT HTML
        deposit_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>รายการฝาก - __SHOP_NAME__</title><script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>__COMMON_HEAD__</head><body class="p-4"><a href="index.html" class="mb-4 inline-block text-sm text-gray-500 hover:text-gray-800">← กลับหน้าหลัก</a><div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden mb-4"><div class="p-4 bg-theme text-white text-center"><h1 class="text-xl font-bold">🍾 __SHOP_NAME__</h1><p class="text-sm opacity-90">รายการฝากของฉัน</p></div></div><div class="max-w-md mx-auto bg-white rounded-xl shadow-md p-6 min-h-[300px]"><div id="status" class="text-center text-gray-500 mt-10">กำลังโหลด...</div><div id="listContainer" class="space-y-4"></div></div>
        <script>const LIFF_ID="__LIFF_ID__",WORKER_URL="__WORKER_URL__",R2_URL="__R2_URL__"; let pollInterval=null,countdownInterval=null;
        async function main(){ 
            if(!WORKER_URL || WORKER_URL === "") { document.getElementById('status').innerHTML = '<span class="text-red-500 font-bold">❌ Error: ไม่พบ Worker URL<br>กรุณากลับไปเช็ค Config ที่โปรแกรมสร้างไฟล์</span>'; return; }
            await liff.init({liffId:LIFF_ID}); if(!liff.isLoggedIn()){liff.login();return} const p=await liff.getProfile(); const t=new URLSearchParams(location.search).get('token'); if(t) handleClaim(p.userId,t); else fetchList(p.userId); 
        }
        function viewImage(url){ Swal.fire({ imageUrl: url, imageAlt: 'Zoom', width: 600, showCloseButton: true, confirmButtonText: 'ปิด' }); }
        async function handleClaim(u,t){ document.getElementById('status').innerText='รับของ...'; try{const r=await fetch(`${WORKER_URL}?action=claim`,{method:'POST',body:JSON.stringify({lineUid:u,claimToken:t})}); const j=await r.json(); if(j.status==='success') Swal.fire('สำเร็จ','รับของแล้ว','success').then(()=>{history.replaceState(null,'',location.pathname);fetchList(u)}); else Swal.fire('!',j.message,'error').then(()=>{history.replaceState(null,'',location.pathname);fetchList(u)})}catch(e){alert('Error: '+e.message)} }
        async function fetchList(u){ 
            try {
                const r=await fetch(`${WORKER_URL}?uid=${u}`); 
                if(r.status!==200) throw new Error('API Error: '+r.status);
                const d=await r.json(); const c=document.getElementById('listContainer'); document.getElementById('status').style.display='none'; c.innerHTML=''; if(d.length===0){c.innerHTML='<p class="text-center text-gray-400">ว่างเปล่า</p>';return} d.forEach(i=>{ const now=new Date(), exp=new Date(i.expire_date), diffTime=exp-now, diffDays=Math.ceil(diffTime/(1000*60*60*24)); let alertClass="", alertMsg="", dateColor="text-gray-500"; if(diffDays<=7 && diffDays>0) { alertClass="urgent"; alertMsg=`<p class="text-red-600 font-bold text-lg animate-bounce">⚠️ เหลืออีก ${diffDays} วัน!</p>`; dateColor="text-red-600 font-bold"; } else if(diffDays<=0) { alertClass="bg-gray-200 opacity-70"; alertMsg=`<p class="text-gray-500 font-bold">❌ หมดอายุแล้ว</p>`; } let pVal=parseInt(i.percent)||0; if(pVal>100)pVal=100; if(pVal<0)pVal=0; const barColor=pVal<30?'bg-red-500':(pVal<70?'bg-yellow-500':'bg-green-500'); const itemData=encodeURIComponent(JSON.stringify(i)); 
                const displayID = i.bottle_label ? `<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded font-bold border border-blue-200 text-lg">${i.bottle_label}</span>` : '<span class="text-gray-400">-</span>';
                c.innerHTML+=`<div class="bg-gray-50 p-3 rounded border flex flex-col gap-3 transition-all duration-300 ${alertClass}">${alertMsg}<div class="flex gap-3"><img src="${R2_URL}/${i.image_filename}" onclick="viewImage('${R2_URL}/${i.image_filename}')" loading="lazy" class="w-20 h-24 object-cover rounded bg-gray-200 cursor-pointer border border-gray-300 hover:opacity-80"><div class="flex-1"><h3 class="font-bold text-lg">${i.brand}</h3><div class="mt-2"><div class="flex justify-between text-xs mb-1"><span class="text-gray-500">คงเหลือ</span><span class="font-bold">${pVal}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill ${barColor}" style="width: ${pVal}%"></div></div></div><p class="text-xs text-gray-500 mt-2 flex items-center gap-1">รหัส: ${displayID}</p><p class="text-sm ${dateColor}">📅 หมดอายุ: ${exp.toLocaleDateString('th-TH')}</p></div></div><div class="flex gap-2"><button onclick="handleAction('${i.id}','withdraw','${i.bottle_label||""}')" class="flex-1 bg-green-600 text-white py-2 rounded text-sm font-bold shadow hover:bg-green-700">🍺 เบิกดื่ม</button><button onclick="handleAction('${i.id}','transfer','${itemData}')" class="flex-1 bg-blue-600 text-white py-2 rounded text-sm font-bold shadow hover:bg-blue-700">🎁 ส่งให้เพื่อน</button></div></div>` }) 
            } catch(e) { document.getElementById('status').innerText='Error: '+e.message; }
        }
        async function handleAction(id,type,data){ 
            const p=await liff.getProfile(); 
            if(type==='withdraw'){ 
                const qrData = "PICKUP|" + id;
                showQR(qrData, data || id.substring(0,4), 'ให้พนักงานสแกน'); 
                startPolling(id,p.userId); 
            } else { 
                if(!liff.isApiAvailable('shareTargetPicker')) return Swal.fire('!','Update LINE','warning'); Swal.fire({title:'Wait...',didOpen:()=>Swal.showLoading()}); const r=await fetch(`${WORKER_URL}?action=gen_token`,{method:'POST',body:JSON.stringify({id:id,lineUid:p.userId})}); const j=await r.json(); if(j.status==='success'){ const link=`https://liff.line.me/${LIFF_ID}?token=${j.token}`; const item=JSON.parse(decodeURIComponent(data)); const msg={type:"flex",altText:"🍾 มีของฝาก!",contents:{type:"bubble",hero:{type:"image",url:`${R2_URL}/${item.image_filename}`,size:"full",aspectRatio:"20:13",aspectMode:"cover"},body:{type:"box",layout:"vertical",contents:[{type:"text",text:"🎁 คุณได้รับของฝาก",weight:"bold",size:"xl",color:"#1DB446"},{type:"text",text:`${item.brand} (${item.percent}%)`,weight:"bold",size:"md",margin:"md"}]},footer:{type:"box",layout:"vertical",contents:[{type:"button",style:"primary",color:"#2563eb",action:{type:"uri",label:"รับของทันที",uri:link}}]}}}; Swal.close(); liff.shareTargetPicker([msg]).then(res=>{if(res)Swal.fire('สำเร็จ','ส่งแล้ว','success').then(()=>fetchList(p.userId))}); } 
            } 
        }
        function showQR(d, code, t){ 
            Swal.fire({
                title: t,
                html: `<div id="qrcode" class="flex justify-center my-4"></div>
                       <div class="bg-blue-50 rounded-xl p-4 mt-2 border-2 border-dashed border-blue-300">
                            <p class="text-sm text-gray-500 mb-1 font-bold">รหัสแปะขวด</p>
                            <p class="big-id">${code}</p>
                       </div>
                       <p class="text-md text-red-500 font-bold animate-pulse mt-4">⏳ ปิดใน <span id="timer">60</span> วิ</p>`,
                confirmButtonText: 'ปิด',
                allowOutsideClick: false,
                didClose: ()=>stopAllTimers()
            }); 
            new QRCode(document.getElementById("qrcode"),{text:d,width:200,height:200}); 
        }
        function startPolling(id,uid){ stopAllTimers(); let time=60; countdownInterval=setInterval(()=>{ time--; const t=document.getElementById('timer'); if(t)t.innerText=time; if(time<=0){ stopAllTimers(); Swal.close(); Swal.fire('หมดเวลา','กดเบิกใหม่','warning').then(()=>location.reload()); } },1000); pollInterval=setInterval(async()=>{ try{ const r=await fetch(`${WORKER_URL}?action=check_status`,{method:'POST',body:JSON.stringify({id:id})}); const j=await r.json(); if(j.status==='success'&&j.itemStatus==='picked_up'){ stopAllTimers(); Swal.close(); Swal.fire('✅ สำเร็จ','รับของแล้ว','success').then(()=>fetchList(uid)); } }catch(e){} },2500); }
        function stopAllTimers(){ if(pollInterval)clearInterval(pollInterval); if(countdownInterval)clearInterval(countdownInterval); }
        main();
        </script></body></html>"""

        # 4. BOOKING HTML
        booking_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><title>__SHOP_NAME__ Reservation</title><script charset="utf-8" src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script><link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/dark.css"><script src="https://cdn.jsdelivr.net/npm/flatpickr"></script><script src="https://npmcdn.com/flatpickr/dist/l10n/th.js"></script><style>:root { --primary: __THEME_COLOR__; --bg-dark: #0b0e14; --card-bg: #151a24; --text-color: #e0e6ed; --accent: #ffab40; } * { box-sizing: border-box; } body { font-family: 'Prompt', sans-serif; background-color: var(--bg-dark); color: var(--text-color); margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100dvh; } .container { width: 90%; max-width: 400px; background: var(--card-bg); padding: 25px 20px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); border: 1px solid #2a3545; position: relative; margin: 20px auto; } .container::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: linear-gradient(90deg, var(--primary), #ffffff50); border-radius: 16px 16px 0 0; } h2 { text-align: center; color: var(--primary); margin: 0 0 10px 0; font-size: 22px; font-weight: 600; text-transform: uppercase; text-shadow: 0 0 15px rgba(255, 255, 255, 0.1); } .warning-text { text-align: center; color: var(--accent); font-size: 14px; margin-bottom: 20px; } .form-group { margin-bottom: 15px; } .form-label { display: block; margin-bottom: 6px; font-size: 13px; color: #a0aec0; } .form-input { width: 100%; height: 45px; padding: 0 12px; background: #1e2532; border: 1px solid #323d52; border-radius: 8px; color: #fff; font-family: 'Prompt', sans-serif; font-size: 16px; transition: all 0.3s; -webkit-appearance: none; } .form-input:focus { outline: none; border-color: var(--primary); background: #252d3d; box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1); } .submit-btn { width: 100%; height: 50px; background: var(--primary); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 10px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); transition: transform 0.2s, filter 0.2s; } .submit-btn:active { transform: scale(0.98); } .submit-btn:hover { filter: brightness(1.1); } .flatpickr-calendar { background: #151a24 !important; border: 1px solid #2a3545 !important; box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important; font-family: 'Prompt', sans-serif !important; } .flatpickr-day.selected { background: var(--primary) !important; border-color: var(--primary) !important; } #loading { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 9999; align-items: center; justify-content: center; flex-direction: column; color: var(--primary); } .spinner { width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.1); border-top: 4px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 15px; } @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } } .back-link { display: block; margin-bottom: 20px; color: #64748b; text-decoration: none; font-size: 14px; text-align: center;} </style></head><body><div id="loading"><div class="spinner"></div><div>กำลังส่งข้อมูล...</div></div><div class="container"><a href="index.html" class="back-link">← กลับหน้าหลัก</a><h2>__SHOP_NAME__</h2><div class="warning-text">* กรุณารับโต๊ะก่อน __TIME_LIMIT__ น.</div><div class="form-group"><label class="form-label">📅 วันที่จอง</label><input type="text" id="inputDate" class="form-input" placeholder="เลือกวันที่..."></div><div class="form-group"><label class="form-label">👤 ชื่อผู้จอง</label><input type="text" id="inputName" class="form-input" placeholder="ระบุชื่อ"></div><div class="form-group"><label class="form-label">👥 จำนวนคน</label><input type="number" id="inputPax" class="form-input" placeholder="ระบุจำนวนคน" min="1" inputmode="numeric"></div><div class="form-group"><label class="form-label">📞 เบอร์ติดต่อ</label><input type="tel" id="inputPhone" class="form-input" placeholder="08x-xxx-xxxx" inputmode="numeric"></div><div class="form-group"><label class="form-label">📝 คำขอพิเศษ (ถ้ามี)</label><input type="text" id="inputRemark" class="form-input" placeholder="เช่น ขอโซนหน้าเวที"></div><button class="submit-btn" onclick="submitToLine()">ยืนยันการจอง</button></div><script>const MY_LIFF_ID = "__LIFF_ID__"; flatpickr("#inputDate", { locale: "th", dateFormat: "Y-m-d", altInput: true, altFormat: "j F Y", defaultDate: "today", disableMobile: "true", theme: "dark" }); async function initializeLiff() { try { await liff.init({ liffId: MY_LIFF_ID }); if (!liff.isLoggedIn()) { liff.login(); } } catch (error) { console.error("LIFF Init Error", error); } } initializeLiff(); function formatDateToThaiOrder(d) { if(!d) return ""; const [y, m, day] = d.split('-'); return `${day}/${m}/${y}`; } async function submitToLine() { const rawDate = document.getElementById('inputDate').value; const name = document.getElementById('inputName').value.trim(); const pax = document.getElementById('inputPax').value.trim(); const phone = document.getElementById('inputPhone').value.trim(); let remark = document.getElementById('inputRemark').value.trim(); if (remark === "") remark = "-"; if(!name || !phone || !rawDate || !pax) { alert("กรุณากรอกข้อมูลให้ครบถ้วน"); return; } document.getElementById('loading').style.display = 'flex'; const displayDate = formatDateToThaiOrder(rawDate); const message = `📌 จองโต๊ะ (__SHOP_NAME__)\\n-------------------------\\n⚠️ (รับโต๊ะก่อน __TIME_LIMIT__ น.)\\n📅 วันที่: ${displayDate}\\n👤 ชื่อ: ${name}\\n👥 จำนวน: ${pax} ท่าน\\n📞 เบอร์: ${phone}\\n📝 คำขอ: ${remark}`; if (liff.isInClient()) { try { await liff.sendMessages([{ type: 'text', text: message }]); liff.closeWindow(); } catch (error) { alert("Error: " + error.message); document.getElementById('loading').style.display = 'none'; } } else { alert("กรุณาเปิดผ่าน LINE"); console.log(message); document.getElementById('loading').style.display = 'none'; } } </script></body></html>"""

        # 5. STAFF HTML (With Staff Whitelist & Clean Stats)
        staff_template = """<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__SHOP_NAME__ Staff</title>__COMMON_HEAD__<script src="https://unpkg.com/html5-qrcode"></script><script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script><style>.zone-btn{transition:0.2s;}.zone-btn:active{transform:scale(0.95);}</style></head><body class="p-4 bg-gray-100"><div class="max-w-md mx-auto bg-white rounded-xl shadow-md mb-4"><div class="p-4 bg-gray-800 text-white text-center"><h1 class="text-xl font-bold">👮 Staff & Manager V.80</h1><p id="staff-info" class="text-xs text-gray-300 mt-1">Checking access...</p><div class="flex mt-4 gap-1"><button onclick="tab('deposit')" id="btn-deposit" class="flex-1 py-2 rounded font-bold tab-active">ฝาก</button><button onclick="tab('withdraw')" id="btn-withdraw" class="flex-1 py-2 rounded font-bold tab-inactive">เบิก</button><button onclick="tab('manager')" id="btn-manager" class="flex-1 py-2 rounded font-bold tab-inactive bg-gray-600 text-white">ผจก.</button></div></div></div>
        
        <div id="sec-deposit" class="max-w-md mx-auto">
            <div class="bg-white rounded-xl shadow p-6 mb-4">
                <h2 class="font-bold text-center mb-4">ขั้นตอน 1: รับเลขรหัส</h2>
                <button onclick="getRunningNumber()" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-6 rounded-2xl font-bold text-2xl shadow-lg transform active:scale-95 transition-all">🔢 ขอเลขรหัสฝาก</button>
                <div id="step2" class="hidden text-center border-t pt-4 mt-6">
                    <p class="text-gray-500 mb-1">เลขรหัสคือ:</p>
                    <div id="generated-id" class="text-6xl font-black text-blue-600 mb-2 tracking-wider">0000</div>
                    <p class="text-red-500 font-bold animate-pulse mb-6 text-lg">✍️ เขียนเลขนี้แปะขวดเดี๋ยวนี้!</p>
                    <input type="file" id="cam" accept="image/*" capture="environment" class="hidden" onchange="previewImage(this)">
                    <button onclick="document.getElementById('cam').click()" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-4 rounded-xl font-bold text-lg shadow-lg">📷 ถ่ายรูป (ให้เห็นเลข)</button>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow p-4 mb-4">
                <h3 class="font-bold text-gray-600 mb-2 border-b pb-2">🕒 รายการล่าสุด (Sync สด)</h3>
                <div id="recent-list" class="text-sm text-center text-gray-400">กำลังโหลด...</div>
            </div>

            <div id="pv" class="hidden bg-white rounded-xl shadow p-6 space-y-3">
                <img id="img" class="w-full h-56 object-cover rounded mb-4 border border-gray-300">
                <div class="bg-gray-100 p-2 rounded text-center mb-2">
                    <span class="text-gray-500 text-sm">รหัสที่แปะขวด:</span><br>
                    <span id="confirm-id" class="text-3xl font-bold text-blue-800 tracking-widest"></span>
                </div>
                <input id="s_name" placeholder="ชื่อพนักงาน" class="w-full p-2 border rounded" readonly>
                <input list="bl" id="br" placeholder="ยี่ห้อ" class="w-full p-2 border rounded">
                <datalist id="bl"><option value="Regency"><option value="Black Label"><option value="Red Label"><option value="Blend 285"><option value="SangSom"></datalist>
                <input type="number" id="pc" placeholder="%" class="w-full p-2 border rounded">
                <input id="nt" placeholder="ชื่อลูกค้า / เบอร์โทร" class="w-full p-2 border rounded bg-yellow-50 border-yellow-200">
                <button onclick="submitDeposit()" class="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded font-bold">✅ ยืนยันการฝาก</button>
            </div>
        </div>
        
        <div id="sec-withdraw" class="max-w-md mx-auto hidden">
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <h2 class="text-lg font-bold mb-2">สแกนเบิก (Hybrid)</h2>
                <div id="reader" style="width:100%;min-height:250px;background:#000;"></div>
                <p id="scanRes" class="mt-4 text-gray-500 text-sm">กำลังเปิดกล้อง...</p>
                <div class="my-4">
                    <input type="file" id="scan-file" accept="image/*" capture="environment" class="hidden" onchange="scanFromFile(this)">
                    <button onclick="document.getElementById('scan-file').click()" class="bg-orange-600 hover:bg-orange-700 text-white w-full py-4 rounded-xl font-bold shadow-lg flex items-center justify-center gap-2 text-lg">📷 ถ่ายรูปสแกน (แก้จอดำ)</button>
                </div>
                <div class="mt-4 pt-4 border-t">
                    <p class="font-bold text-gray-400 text-xs mb-2">หรือกรอกเลข</p>
                    <div class="flex gap-2">
                        <input type="text" id="manualCode" placeholder="0154" class="flex-1 p-2 border rounded text-center font-bold">
                        <button onclick="submitManual()" class="bg-blue-600 text-white px-4 rounded font-bold">เบิก</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="sec-manager" class="max-w-md mx-auto hidden">
            <div class="bg-white rounded-xl shadow p-6">
                <h2 class="text-lg font-bold mb-4 text-center">🔐 ผู้จัดการ</h2>
                <div id="mgr-login" class="text-center space-y-3">
                    <input type="password" id="mgr-pwd" placeholder="รหัส" class="w-full p-3 border rounded text-center">
                    <button onclick="mgrLogin()" class="w-full bg-gray-800 text-white py-3 rounded font-bold">Login</button>
                    <div class="pt-4 border-t mt-4"><p class="text-xs text-gray-400 mb-2">ถ้าขึ้น Error "no column" ให้กดปุ่มนี้</p><button onclick="fixDb()" class="bg-orange-100 text-orange-700 px-4 py-2 rounded text-sm font-bold border border-orange-200">🔧 อัปเดตฐานข้อมูล (แก้ Error)</button></div>
                </div>
                <div id="mgr-content" class="hidden">
                    <div class="grid grid-cols-2 gap-2 mb-4">
                        <div class="bg-blue-50 p-3 rounded text-center border border-blue-100"><span class="text-2xl font-bold text-blue-700" id="stat-total">-</span><br><span class="text-xs">ฝากอยู่ (ขวด)</span></div>
                        <div class="bg-red-50 p-3 rounded text-center border border-red-100"><span class="text-2xl font-bold text-red-700" id="stat-exp">-</span><br><span class="text-xs">ใกล้หมด (ขวด)</span></div>
                    </div>
                    
                    <div class="mb-4 bg-gray-50 border rounded p-3">
                        <div class="flex justify-between items-center mb-2">
                            <h3 class="font-bold text-gray-700">👥 พนักงาน (Whitelist)</h3>
                            <button onclick="loadStaffList()" class="text-xs bg-gray-200 px-2 py-1 rounded">Refresh</button>
                        </div>
                        <div id="staff-pending" class="mb-2"></div>
                        <div id="staff-list" class="space-y-1 max-h-32 overflow-y-auto"></div>
                    </div>

                    <div class="flex gap-2 mb-4"><input id="mgr-search" onkeyup="filterMgr()" placeholder="🔍 ค้นหา (ลูกค้า, เลข, ยี่ห้อ)" class="flex-1 p-2 border rounded"><button onclick="loadMgr()" class="bg-gray-200 px-3 rounded">🔄</button></div>
                    <div class="flex border-b mb-3"><button onclick="switchMgrTab('active')" id="mtab-active" class="flex-1 py-2 font-bold text-blue-600 border-b-2 border-blue-600">รายการฝาก</button><button onclick="switchMgrTab('history')" id="mtab-history" class="flex-1 py-2 text-gray-400">ประวัติ</button></div>
                    <div class="overflow-x-auto max-h-[500px]"><table class="w-full text-sm text-left"><thead class="bg-gray-100 text-gray-600"><tr><th class="p-2">รายละเอียด</th><th class="p-2">หมดอายุ</th><th class="p-2 text-center">จัดการ</th></tr></thead><tbody id="mgr-tb"></tbody></table></div>
                </div>
            </div>
        </div>
        
        <div id="hidden-qr" style="display:none;"></div>

        <script>
        const WORKER_URL="__WORKER_URL__", LIFF_ID="__LIFF_ID__", R2_URL="__R2_URL__"; 
        let currentPwd="", html5QrCode, currentZoneCode="", staffProfile=null;
        
        async function initApp() {
            await liff.init({ liffId: LIFF_ID });
            if (!liff.isLoggedIn()) { liff.login(); return; }
            staffProfile = await liff.getProfile();
            document.getElementById('staff-info').innerText = `Staff: ${staffProfile.displayName}`;
            document.getElementById('s_name').value = staffProfile.displayName;
            loadRecentList();
        }
        initApp();

        function compressImage(file){return new Promise((resolve)=>{const img=new Image();img.src=URL.createObjectURL(file);img.onload=()=>{const cvs=document.createElement('canvas');const mw=800;const sc=mw/img.width;cvs.width=mw;cvs.height=img.height*sc;const ctx=cvs.getContext('2d');ctx.drawImage(img,0,0,cvs.width,cvs.height);cvs.toBlob((b)=>resolve(b),'image/jpeg',0.6);};});}
        
        async function tab(t){ 
            if(html5QrCode){ try{await html5QrCode.stop();html5QrCode.clear();}catch(e){} }
            ['deposit','withdraw','manager'].forEach(x=>{document.getElementById('sec-'+x).classList.add('hidden');const b=document.getElementById('btn-'+x);b.classList.remove('tab-active');b.classList.add('tab-inactive');if(x==='manager')b.classList.add('bg-gray-600','text-white');}); 
            document.getElementById('sec-'+t).classList.remove('hidden'); const ab=document.getElementById('btn-'+t);ab.classList.add('tab-active'); ab.classList.remove('tab-inactive'); 
            if(t==='withdraw') { setTimeout(initCamera, 300); }
            if(t==='deposit') { loadRecentList(); }
        }

        // 🔥 Image Zoom Function
        function viewImage(url){ Swal.fire({ imageUrl: url, imageAlt: 'Zoom', width: 600, showCloseButton: true, confirmButtonText: 'ปิด' }); }

        async function getRunningNumber(){
            if(!WORKER_URL) return Swal.fire('Error', 'กรุณาตั้งค่า Worker URL ก่อน', 'error');
            Swal.fire({title:'Generating ID...',didOpen:()=>Swal.showLoading()});
            try {
                const r = await fetch(`${WORKER_URL}?action=get_next_id`);
                const j = await r.json();
                if(j.status === 'success'){
                    currentZoneCode = j.nextId; 
                    document.getElementById('generated-id').innerText = currentZoneCode;
                    document.getElementById('confirm-id').innerText = currentZoneCode;
                    document.getElementById('step2').classList.remove('hidden');
                    Swal.close();
                } else { Swal.fire('Error', 'Gen ID Failed: ' + j.message, 'error'); }
            } catch(e) { Swal.fire('Error', 'Connection Failed: ' + e.message, 'error'); }
        }
        function previewImage(i){if(i.files[0]){const r=new FileReader();r.onload=e=>{document.getElementById('img').src=e.target.result;document.getElementById('pv').classList.remove('hidden')};r.readAsDataURL(i.files[0])}} 
        
        async function submitDeposit(){
            const f=document.getElementById('cam').files[0],b=document.getElementById('br').value,s=staffProfile.displayName;
            if(!f||!b)return Swal.fire('!','ข้อมูลไม่ครบ','warning');
            Swal.fire({title:'Uploading...',didOpen:()=>Swal.showLoading()});
            
            try {
                const cf=await compressImage(f);
                const d=new FormData(); d.append('image',cf); d.append('brand',b); d.append('percent',document.getElementById('pc').value); d.append('note',document.getElementById('nt').value); d.append('bottle_label', currentZoneCode); d.append('shop','__SHOP_NAME__'); 
                d.append('staff_name',s); 
                d.append('staff_uid', staffProfile.userId); 
                
                const r=await fetch(WORKER_URL,{method:'POST',body:d}); const j=await r.json();
                
                if(j.status==='success'){ 
                    const link=`https://liff.line.me/${LIFF_ID}?token=${j.claimToken}`; 
                    const qrDiv = document.getElementById("hidden-qr"); qrDiv.innerHTML = "";
                    new QRCode(qrDiv, {text: link, width: 250, height: 250});
                    setTimeout(() => {
                        const qrImg = qrDiv.querySelector('img') ? qrDiv.querySelector('img').src : '';
                        loadRecentList(); 
                        Swal.fire({
                            title: '✅ สำเร็จ!',
                            html: `<div class="text-center"><p class="text-3xl font-bold text-blue-600 mb-2 tracking-widest">${currentZoneCode}</p><div class="flex justify-center mb-2"><img src="${qrImg}" style="width:200px; height:200px; border:1px solid #ccc;"></div><p class="text-sm text-gray-500">ให้ลูกค้าสแกนเพื่อรับเข้าระบบ</p></div>`,
                            confirmButtonText: 'ปิด (เริ่มใหม่)'
                        }).then(() => location.reload());
                    }, 200);
                } else Swal.fire('Error',j.message,'error');
            } catch(e) { Swal.fire('Error', 'Upload Failed: '+e.message, 'error'); }
        }

        async function loadRecentList(){
            try {
                const c = document.getElementById('recent-list');
                const r = await fetch(`${WORKER_URL}?action=get_recent`);
                const data = await r.json();
                if(!data || data.length === 0) { c.innerHTML = '<span class="text-gray-400">ไม่มีรายการล่าสุด</span>'; return; }
                c.innerHTML = '<div class="space-y-2">';
                data.forEach(item => {
                    const link = `https://liff.line.me/${LIFF_ID}?token=${item.claim_token}`;
                    const time = new Date(item.created_at).toLocaleTimeString('th-TH', {hour: '2-digit', minute:'2-digit'});
                    const custName = item.note ? `<span class="text-xs text-gray-500 block">👤 ${item.note}</span>` : '';
                    c.innerHTML += `<div class="flex justify-between items-center bg-gray-50 p-2 rounded border">
                        <div><span class="font-bold text-blue-600">${item.bottle_label}</span> <span class="text-gray-800 text-sm">${item.brand}</span>${custName}</div>
                        <div class="flex gap-2 items-center"><span class="text-xs text-gray-400">${time}</span><button onclick="showRecentQR('${link}','${item.bottle_label}')" class="bg-blue-100 text-blue-600 px-3 py-1 rounded text-xs">QR</button></div>
                    </div>`;
                });
                c.innerHTML += '</div>';
            } catch(e) { console.log(e); }
        }
        
        function showRecentQR(link, code){
            const qrDiv = document.getElementById("hidden-qr"); qrDiv.innerHTML = "";
            new QRCode(qrDiv, {text: link, width: 250, height: 250});
            setTimeout(() => {
                const qrImg = qrDiv.querySelector('img').src;
                Swal.fire({
                    title: 'QR Code ย้อนหลัง',
                    html: `<div class="text-center"><p class="font-bold text-lg mb-2">${code}</p><img src="${qrImg}" class="mx-auto" style="width:200px"></div>`,
                    confirmButtonText: 'ปิด'
                });
            }, 100);
        }

        async function initCamera() {
            if(!html5QrCode) html5QrCode = new Html5Qrcode("reader");
            try {
                const devices = await Html5Qrcode.getCameras();
                let targetId = (devices && devices.length) ? devices[0].id : null;
                if(devices){ for(let i=0; i<devices.length; i++){ if(devices[i].label.toLowerCase().includes('back') || devices[i].label.toLowerCase().includes('rear')) targetId = devices[i].id; } }
                startScan(targetId);
            } catch (err) { document.getElementById('scanRes').innerHTML = `<span class="text-red-500">กล้อง Live ไม่พร้อม (ใช้ปุ่มถ่ายรูปแทน)</span>`; }
        }
        function startScan(cameraId){
            const config = { fps: 10, qrbox: {width: 250, height: 250}, disableFlip: false };
            const camConfig = cameraId ? { deviceId: { exact: cameraId } } : { facingMode: "environment" };
            html5QrCode.start(camConfig, config, (t)=>{ if(t.startsWith('PICKUP|')) { confirmPickup(t.split('|')[1]); } }).catch(err => {});
        }
        async function scanFromFile(input) {
            if (input.files.length === 0) return;
            const file = input.files[0];
            try {
                const result = await html5QrCode.scanFileV2(file, true);
                if(result && result.decodedText && result.decodedText.startsWith('PICKUP|')) { confirmPickup(result.decodedText.split('|')[1]); } 
                else { Swal.fire('❌ ไม่พบ QR', 'รูปไม่ชัด หรือไม่ใช่ QR เบิกของ', 'error'); }
            } catch (err) { Swal.fire('❌ Error', 'อ่าน QR ไม่ได้ ลองถ่ายใหม่ให้ชัดขึ้น', 'error'); }
            input.value = ''; 
        }
        async function submitManual(){
            const code = document.getElementById('manualCode').value.trim();
            if(!code) return;
            Swal.fire({title:'Searching...',didOpen:()=>Swal.showLoading()});
            try {
                const r = await fetch(`${WORKER_URL}?action=pickup_manual&code=${code}`);
                const j = await r.json();
                if(j.status === 'success') confirmPickup(j.item.id, code);
                else Swal.fire('❌', 'ไม่พบรหัสนี้', 'error');
            } catch(e) { Swal.fire('Error', 'Connection Failed', 'error'); }
        }
        function confirmPickup(id, label=''){
            if(html5QrCode.isScanning) html5QrCode.pause();
            Swal.fire({ title: `เบิก ${label}?`, text: "ยืนยันการเบิกสินค้า", showCancelButton: true, confirmButtonColor: '#16a34a', confirmButtonText: '✅ เบิกเลย' }).then(async(r)=>{
                if(r.isConfirmed){
                    // Pass staff UID
                    const res=await fetch(`${WORKER_URL}?action=pickup`,{method:'POST',body:JSON.stringify({id:id, staff_uid: staffProfile.userId, staff_name: staffProfile.displayName})}); const j=await res.json();
                    if(j.status==='success') Swal.fire('สำเร็จ','','success').then(()=>document.getElementById('manualCode').value=''); else Swal.fire('!',j.message,'error');
                }
                if(html5QrCode.isScanning) html5QrCode.resume();
            });
        }

        let mgrData = [];
        async function mgrLogin(){
            const p=document.getElementById('mgr-pwd').value;
            try {
                const r=await fetch(`${WORKER_URL}?mode=manager&pwd=${p}`);
                if(r.status===401) { Swal.fire('!','รหัสผิด (Wrong Password)','error'); } 
                else if(r.status===500) { const txt = await r.text(); Swal.fire('Database Error', 'ฐานข้อมูลยังไม่อัปเดต กรุณากดปุ่ม "อัปเดตฐานข้อมูล" ข้างล่าง', 'warning'); }
                else { currentPwd=p; document.getElementById('mgr-login').classList.add('hidden'); document.getElementById('mgr-content').classList.remove('hidden'); loadMgrData(); loadStaffList(); }
            } catch(e) { Swal.fire('Error', 'Connection Error: '+e.message, 'error'); }
        } 
        async function fixDb() {
            Swal.fire({title:'กำลังซ่อม...', didOpen:()=>Swal.showLoading()});
            try { const r = await fetch(`${WORKER_URL}?action=migrate_db`); const t = await r.text(); Swal.fire('ผลการซ่อม', t, 'info'); } catch(e) { Swal.fire('Error', e.message, 'error'); }
        }
        async function loadMgrData(){
            const r = await fetch(`${WORKER_URL}?mode=manager&pwd=${currentPwd}`); mgrData = await r.json(); renderMgr(mgrData.active, 'active');
            document.getElementById('stat-total').innerText = mgrData.active.length;
            const expCount = mgrData.active.filter(i => { const days = Math.ceil((new Date(i.expire_date) - new Date())/(1000*60*60*24)); return days <= 3; }).length;
            document.getElementById('stat-exp').innerText = expCount;
        }

        // --- STAFF MANAGEMENT UI ---
        async function loadStaffList(){
            const r = await fetch(`${WORKER_URL}?action=get_staff_list&pwd=${currentPwd}`);
            const j = await r.json();
            const pendingDiv = document.getElementById('staff-pending');
            const listDiv = document.getElementById('staff-list');
            pendingDiv.innerHTML = ''; listDiv.innerHTML = '';
            
            // Pending Requests
            j.pending.forEach(s => {
                pendingDiv.innerHTML += `<div class="flex justify-between items-center bg-yellow-50 border border-yellow-200 p-2 rounded mb-1">
                    <span class="text-sm font-bold text-yellow-800">⚠️ ขออนุมัติ: ${s.display_name}</span>
                    <div class="flex gap-1"><button onclick="approveStaff('${s.line_uid}', 'staff')" class="bg-green-500 text-white text-xs px-2 py-1 rounded">Staff</button><button onclick="approveStaff('${s.line_uid}', 'manager')" class="bg-blue-600 text-white text-xs px-2 py-1 rounded">Manager</button></div>
                </div>`;
            });
            // Active List
            j.active.forEach(s => {
                listDiv.innerHTML += `<div class="flex justify-between items-center text-sm border-b py-1">
                    <span>${s.display_name} <span class="text-xs text-gray-400">(${s.role})</span></span>
                    <button onclick="delStaff('${s.line_uid}')" class="text-red-500 text-xs">ลบ</button>
                </div>`;
            });
        }
        async function approveStaff(uid, role){
            await fetch(`${WORKER_URL}?action=approve_staff&pwd=${currentPwd}`, {method:'POST', body:JSON.stringify({uid:uid, role:role})});
            loadStaffList();
        }
        async function delStaff(uid){
            if(confirm('ลบสิทธิ์พนักงานคนนี้?')){
                await fetch(`${WORKER_URL}?action=delete_staff&pwd=${currentPwd}`, {method:'POST', body:JSON.stringify({uid:uid})});
                loadStaffList();
            }
        }

        let currentMgrTab = 'active';
        function switchMgrTab(t) {
            currentMgrTab = t;
            document.getElementById('mtab-active').className = t==='active' ? "flex-1 py-2 font-bold text-blue-600 border-b-2 border-blue-600" : "flex-1 py-2 text-gray-400";
            document.getElementById('mtab-history').className = t==='history' ? "flex-1 py-2 font-bold text-blue-600 border-b-2 border-blue-600" : "flex-1 py-2 text-gray-400";
            renderMgr(t==='active' ? mgrData.active : mgrData.history, t);
        }
        function filterMgr(){
            const k = document.getElementById('mgr-search').value.toLowerCase();
            const src = currentMgrTab==='active' ? mgrData.active : mgrData.history;
            const filtered = src.filter(i => (i.bottle_label && i.bottle_label.toLowerCase().includes(k)) || (i.brand && i.brand.toLowerCase().includes(k)) || (i.note && i.note.toLowerCase().includes(k)));
            renderMgr(filtered, currentMgrTab);
        }
        
        function showMgrQR(token, label){
            if(!token || token === 'null' || token === 'undefined') {
                return Swal.fire('Error', 'ไม่พบ Token (รายการอาจถูกเบิกแล้ว)', 'error');
            }
            const link=`https://liff.line.me/${LIFF_ID}?token=${token}`;
            showRecentQR(link, label);
        }

        // 🔥 FIX: Clean History Log Logic
        function renderMgr(list, type){
            const t=document.getElementById('mgr-tb');t.innerHTML='';
            list.forEach(i=>{
                const exp = new Date(i.expire_date); const days = Math.ceil((exp - new Date())/(1000*60*60*24));
                let st = "";
                let bgRow = "";
                
                if(type === 'active') { 
                    st = `<div class="flex justify-center gap-2"><button onclick="showMgrQR('${i.claim_token}','${i.bottle_label}')" class="bg-purple-100 text-purple-600 p-1 rounded">📱</button><button onclick="editItem('${i.id}')" class="text-blue-500">✏️</button><button onclick="del('${i.id}')" class="text-red-500">🗑</button></div>`; 
                } 
                else { 
                    if (i.status === 'history_log') {
                        // Extended
                        st = `<div class="text-right"><span class="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-bold border border-green-200">📅 ต่ออายุ +30 วัน</span><br><span class="text-[10px] text-gray-400">โดย: ${i.staff_name || 'System'}</span></div>`;
                        bgRow = "bg-green-50";
                    } else if (i.status === 'picked_up') {
                        // Picked up
                        st = `<div class="text-right"><span class="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs border">Pick Out</span><br><span class="text-[10px] text-gray-400">โดย: ${i.staff_name || '-'}</span></div>`;
                    } else {
                        st = `<span class="text-gray-400 text-xs">Deleted</span>`;
                    }
                }
                
                let badge = `<span class="bg-blue-100 text-blue-800 px-1 rounded font-bold mr-1">${i.bottle_label||'-'}</span>`;
                let customerInfo = i.note ? `<div class="text-xs text-green-700 font-bold mt-1">👤 ${i.note}</div>` : '';
                let thumb = `<img src="${R2_URL}/${i.image_filename}" onclick="viewImage('${R2_URL}/${i.image_filename}')" class="w-10 h-10 object-cover rounded border cursor-pointer hover:scale-110 transition-transform">`;

                let dateDisplay = "";
                if (i.status === 'history_log' || i.status === 'picked_up') {
                     dateDisplay = `<span class="text-gray-500">${new Date(i.updated_at).toLocaleDateString('th-TH')}</span>`;
                } else {
                     dateDisplay = `<span class="${days<=3?'text-red-600 font-bold':''}">${exp.toLocaleDateString('th-TH')}<br>(${days} วัน)</span>`;
                }

                t.innerHTML+=`<tr class="border-b ${bgRow}">
                    <td class="p-2 flex gap-2 items-start">
                        ${thumb}
                        <div>
                            ${badge}<span class="font-bold text-sm">${i.brand}</span><br>
                            <span class="text-xs text-gray-500">${i.percent}%</span>
                            ${customerInfo}
                        </div>
                    </td>
                    <td class="p-2 text-xs">${dateDisplay}</td>
                    <td class="p-2 text-center">${st}</td>
                </tr>`
            })
        }
        async function editItem(id){
            const item = mgrData.active.find(x=>x.id===id);
            const { value: formValues } = await Swal.fire({
                title: 'แก้ไขข้อมูล',
                html: `<input id="swal-label" class="swal2-input" placeholder="รหัสขวด" value="${item.bottle_label||''}"><input id="swal-brand" class="swal2-input" placeholder="ยี่ห้อ" value="${item.brand}"><input id="swal-percent" type="number" class="swal2-input" placeholder="%" value="${item.percent}"><br><br><button onclick="extend('${id}')" class="bg-green-500 text-white px-4 py-2 rounded">📅 +30 วัน (ต่ออายุ)</button>`,
                focusConfirm: false, showCancelButton: true, preConfirm: () => { return [document.getElementById('swal-label').value, document.getElementById('swal-brand').value, document.getElementById('swal-percent').value] }
            });
            if(formValues){ await fetch(`${WORKER_URL}?action=mgr_edit&pwd=${currentPwd}`, { method:'POST', body:JSON.stringify({id:id, bottle_label:formValues[0], brand:formValues[1], percent:formValues[2]}) }); loadMgrData(); }
        }
        // Send Staff Name/UID when extending
        async function extend(id){ 
            await fetch(`${WORKER_URL}?action=mgr_extend&pwd=${currentPwd}&id=${id}&staff_uid=${staffProfile.userId}&staff_name=${staffProfile.displayName}`, {method:'POST'}); 
            Swal.close(); Swal.fire('เรียบร้อย', 'ต่ออายุ 30 วันแล้ว', 'success'); loadMgrData(); 
        }
        async function del(id){if(confirm('ลบรายการ? (ย้ายไป History)')){await fetch(`${WORKER_URL}?id=${id}&pwd=${currentPwd}`,{method:'DELETE'});loadMgrData()}}
        </script></body></html>"""

        # 6. WORKER JS
        worker_template = r"""
export default {
  async fetch(request, env) {
    const corsHeaders = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" };
    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });
    const url = new URL(request.url); const MANAGER_PWD = "__MANAGER_PWD__"; 

    // --- DB MIGRATION (Auto-Create Staff Table) ---
    if (url.searchParams.get('action') === 'migrate_db') {
        try {
            await env.DB.prepare("ALTER TABLE deposits ADD COLUMN updated_at TEXT").run();
        } catch (e) {}
        try {
            // New Staff Table
            await env.DB.prepare("CREATE TABLE IF NOT EXISTS staff_list (line_uid TEXT PRIMARY KEY, display_name TEXT, role TEXT, created_at TEXT)").run();
            // New Columns for Accountability
            await env.DB.prepare("ALTER TABLE deposits ADD COLUMN staff_uid TEXT").run();
            await env.DB.prepare("ALTER TABLE deposits ADD COLUMN staff_name TEXT").run();
            return new Response("✅ Migrated: staff_list created & columns added.", { headers: corsHeaders });
        } catch (e) {
            return new Response("⚠️ Migration Info: " + e.message, { headers: corsHeaders });
        }
    }

    // --- STAFF MANAGEMENT ENDPOINTS ---
    if (request.method === "GET" && url.searchParams.get('action') === 'check_staff') {
        const uid = url.searchParams.get('uid');
        const res = await env.DB.prepare("SELECT * FROM staff_list WHERE line_uid = ?").bind(uid).first();
        if (res) return new Response(JSON.stringify({ status: 'success', role: res.role }), { headers: corsHeaders });
        return new Response(JSON.stringify({ status: 'success', role: 'none' }), { headers: corsHeaders });
    }
    
    if (request.method === "POST" && url.searchParams.get('action') === 'request_staff') {
        const body = await request.json();
        try {
            await env.DB.prepare("INSERT INTO staff_list (line_uid, display_name, role, created_at) VALUES (?, ?, 'pending', ?)").bind(body.uid, body.name, new Date().toISOString()).run();
            return new Response(JSON.stringify({ status: 'success' }), { headers: corsHeaders });
        } catch(e) { return new Response(JSON.stringify({ status: 'error', message: 'Already registered or error' }), { headers: corsHeaders }); }
    }
    
    if (request.method === "GET" && url.searchParams.get('action') === 'get_staff_list') {
        if (url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Unauthorized', {status:401, headers:corsHeaders});
        const pending = await env.DB.prepare("SELECT * FROM staff_list WHERE role = 'pending'").all();
        const active = await env.DB.prepare("SELECT * FROM staff_list WHERE role != 'pending'").all();
        return new Response(JSON.stringify({ pending: pending.results, active: active.results }), { headers: corsHeaders });
    }
    
    if (request.method === "POST" && url.searchParams.get('action') === 'approve_staff') {
        if (url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Unauthorized', {status:401, headers:corsHeaders});
        const body = await request.json();
        await env.DB.prepare("UPDATE staff_list SET role = ? WHERE line_uid = ?").bind(body.role, body.uid).run();
        return new Response(JSON.stringify({ status: 'success' }), { headers: corsHeaders });
    }

    if (request.method === "POST" && url.searchParams.get('action') === 'delete_staff') {
        if (url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Unauthorized', {status:401, headers:corsHeaders});
        const body = await request.json();
        await env.DB.prepare("DELETE FROM staff_list WHERE line_uid = ?").bind(body.uid).run();
        return new Response(JSON.stringify({ status: 'success' }), { headers: corsHeaders });
    }

    // --- EXISTING FEATURES ---

    if (request.method === "GET" && url.searchParams.get('action') === 'get_recent') {
        const res = await env.DB.prepare("SELECT * FROM deposits WHERE status = 'active' ORDER BY created_at DESC LIMIT 5").all();
        return new Response(JSON.stringify(res.results), { headers: corsHeaders });
    }

    if (request.method === "GET" && url.searchParams.get('action') === 'get_next_id') {
        const res = await env.DB.prepare("SELECT bottle_label FROM deposits").all();
        let maxNum = 0;
        if(res.results && res.results.length > 0) {
            res.results.forEach(r => {
                const match = r.bottle_label.match(/(\d+)/); 
                if(match) { const num = parseInt(match[0]); if(num > maxNum) maxNum = num; }
            });
        }
        let nextNum = maxNum + 1;
        let nextId = String(nextNum).padStart(4, '0');
        return new Response(JSON.stringify({ status: 'success', nextId: nextId }), { headers: corsHeaders });
    }

    if (request.method === "GET" && url.searchParams.get('mode') === 'manager') {
        if (url.searchParams.get('pwd') !== MANAGER_PWD) return new Response(JSON.stringify({ status: 'error', message: 'Wrong Password' }), { status: 401, headers: corsHeaders });
        try {
            const active = await env.DB.prepare("SELECT * FROM deposits WHERE status = 'active' ORDER BY expire_date ASC LIMIT 100").all();
            const history = await env.DB.prepare("SELECT * FROM deposits WHERE status != 'active' ORDER BY updated_at DESC LIMIT 50").all(); 
            return new Response(JSON.stringify({ active: active.results, history: history.results }), { headers: corsHeaders });
        } catch(e) {
            return new Response("DB_ERROR: " + e.message, { status: 500, headers: corsHeaders });
        }
    }

    if (request.method === "POST" && url.searchParams.get('action') === 'mgr_edit') {
         if (url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Unauthorized', {status:401, headers:corsHeaders});
         const body = await request.json();
         await env.DB.prepare("UPDATE deposits SET bottle_label=?, brand=?, percent=? WHERE id=?").bind(body.bottle_label, body.brand, body.percent, body.id).run();
         return new Response(JSON.stringify({status:'success'}), {headers:corsHeaders});
    }

    // 🔥 FIX: History Log with Accountability
    if (request.method === "POST" && url.searchParams.get('action') === 'mgr_extend') {
         if (url.searchParams.get('pwd') !== MANAGER_PWD) return new Response('Unauthorized', {status:401, headers:corsHeaders});
         const id = url.searchParams.get('id');
         const staffName = url.searchParams.get('staff_name') || 'Manager';
         const staffUid = url.searchParams.get('staff_uid') || '';
         
         const oldItem = await env.DB.prepare("SELECT * FROM deposits WHERE id=?").bind(id).first();
         if(!oldItem) return new Response('Not found', {status:404});

         const logId = crypto.randomUUID();
         const now = new Date().toISOString();
         
         // Insert History Log (Status: history_log)
         await env.DB.prepare("INSERT INTO deposits (id, bottle_label, brand, percent, note, shop_name, image_filename, status, created_at, updated_at, staff_name, staff_uid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
             .bind(logId, oldItem.bottle_label, oldItem.brand, oldItem.percent, "📅 ต่ออายุ +30 วัน", oldItem.shop_name, oldItem.image_filename, 'history_log', now, now, staffName, staffUid).run();

         // Update Actual Item
         let newDate = new Date(oldItem.expire_date); 
         newDate.setDate(newDate.getDate() + 30);
         await env.DB.prepare("UPDATE deposits SET expire_date=? WHERE id=?").bind(newDate.toISOString(), id).run();
         
         return new Response(JSON.stringify({status:'success'}), {headers:corsHeaders});
    }

    if (request.method === "GET" && url.searchParams.get('action') === 'pickup_manual') {
        const code = url.searchParams.get('code');
        const res = await env.DB.prepare("SELECT * FROM deposits WHERE bottle_label = ? AND status = 'active'").bind(code).first();
        if(!res) return new Response(JSON.stringify({ status: 'error' }), { headers: corsHeaders });
        return new Response(JSON.stringify({ status: 'success', item: res }), { headers: corsHeaders });
    }

    if (request.method === "POST" && !url.searchParams.get('action')) {
      try { const formData = await request.formData(); const image = formData.get("image"); if (!image) throw new Error("No image");
        const objectName = crypto.randomUUID() + ".jpg"; await env.BUCKET.put(objectName, image);
        const token = crypto.randomUUID().split('-')[0]; const createdAt = new Date().toISOString();
        const expireDate = new Date(); expireDate.setDate(expireDate.getDate() + 14); 
        // Capture Staff Name & UID from FormData
        await env.DB.prepare("INSERT INTO deposits (id, brand, percent, note, shop_name, image_filename, claim_token, status, created_at, expire_date, bottle_label, staff_name, staff_uid, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), formData.get("brand"), formData.get("percent"), formData.get("note"), formData.get("shop"), objectName, token, 'active', createdAt, expireDate.toISOString(), formData.get("bottle_label"), formData.get("staff_name"), formData.get("staff_uid"), createdAt).run();
        return new Response(JSON.stringify({ status: 'success', claimToken: token }), { headers: corsHeaders });
      } catch (e) { return new Response(JSON.stringify({ status: 'error', message: e.message }), { headers: corsHeaders }); }
    }
    
    if (request.method === "POST" && url.searchParams.get('action')) {
        const action = url.searchParams.get('action'); const body = await request.json();
        if (action === 'claim') {
            await env.DB.prepare("UPDATE deposits SET line_uid = ?, claim_token = NULL WHERE claim_token = ?").bind(body.lineUid, body.claimToken).run();
            return new Response(JSON.stringify({ status: 'success' }), { headers: corsHeaders });
        }
        if (action === 'gen_token') {
            const newToken = crypto.randomUUID().split('-')[0];
            await env.DB.prepare("UPDATE deposits SET claim_token = ? WHERE id = ?").bind(newToken, body.id).run();
            return new Response(JSON.stringify({ status: 'success', token: newToken }), { headers: corsHeaders });
        }
        if (action === 'pickup') {
            const now = new Date().toISOString();
            // Record who picked it up
            const res = await env.DB.prepare("UPDATE deposits SET status = 'picked_up', updated_at = ?, staff_uid = ?, staff_name = ? WHERE id = ? RETURNING *").bind(now, body.staff_uid, body.staff_name, body.id).first();
            return new Response(JSON.stringify({ status: 'success', item: res }), { headers: corsHeaders });
        }
        if (action === 'check_status') {
            const item = await env.DB.prepare("SELECT status FROM deposits WHERE id = ?").bind(body.id).first();
            return new Response(JSON.stringify({ status: 'success', itemStatus: item.status }), { headers: corsHeaders });
        }
    }
    if (request.method === "GET") {
        const uid = url.searchParams.get("uid"); 
        if (uid) {
            const res = await env.DB.prepare("SELECT * FROM deposits WHERE line_uid = ? AND status = 'active' ORDER BY expire_date ASC").bind(uid).all();
            return new Response(JSON.stringify(res.results), { headers: corsHeaders });
        }
    }
    if (request.method === "DELETE") {
        const urlParams = new URLSearchParams(url.search); const id = urlParams.get('id');
        if (urlParams.get('pwd') !== MANAGER_PWD) return new Response(JSON.stringify({ status: 'error', message: 'Unauthorized' }), { status: 401, headers: corsHeaders });
        const now = new Date().toISOString();
        await env.DB.prepare("UPDATE deposits SET status = 'deleted', updated_at = ? WHERE id = ?").bind(now, id).run();
        return new Response(JSON.stringify({ status: 'success' }), { headers: corsHeaders });
    }
    return new Response("OK", { headers: corsHeaders });
  }
};
"""
        
        # ---------------------------------------------------------
        # 🔥 FINAL WRITING FILES (ALL 5 FILES)
        # ---------------------------------------------------------
        
        # 1. Hub HTML (index.html)
        hub_final = hub_template.replace("__SHOP_NAME__", shop_name) \
                                .replace("__THEME_COLOR__", theme_color) \
                                .replace("__R_G_B__", theme_rgb) \
                                .replace("__LIFF_ID_BOOKING__", liff_id_booking) \
                                .replace("__LIFF_ID_DEPOSIT__", liff_id_deposit) \
                                .replace("__WORKER_URL__", worker_url)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f: f.write(hub_final)

        # 2. Deposit HTML (deposit.html)
        head_final = common_head.replace("__THEME_COLOR__", theme_color)
        
        deposit_final = deposit_template.replace("__SHOP_NAME__", shop_name) \
                                        .replace("__LIFF_ID__", liff_id_deposit) \
                                        .replace("__WORKER_URL__", worker_url) \
                                        .replace("__R2_URL__", r2_url) \
                                        .replace("__COMMON_HEAD__", head_final) \
                                        .replace("__THEME_COLOR__", theme_color)
        with open(os.path.join(folder, "deposit.html"), "w", encoding="utf-8") as f: f.write(deposit_final)

        # 3. Booking HTML (booking.html)
        booking_final = booking_template.replace("__SHOP_NAME__", shop_name) \
                                        .replace("__THEME_COLOR__", theme_color) \
                                        .replace("__LIFF_ID__", liff_id_booking) \
                                        .replace("__TIME_LIMIT__", booking_time)
        with open(os.path.join(folder, "booking.html"), "w", encoding="utf-8") as f: f.write(booking_final)

        # 4. Staff HTML (staff.html)
        staff_final = staff_template.replace("__SHOP_NAME__", shop_name) \
                                    .replace("__LIFF_ID__", liff_id_deposit) \
                                    .replace("__WORKER_URL__", worker_url) \
                                    .replace("__R2_URL__", r2_url) \
                                    .replace("__COMMON_HEAD__", head_final) \
                                    .replace("__MANAGER_PWD__", manager_pwd)
        with open(os.path.join(folder, "staff.html"), "w", encoding="utf-8") as f: f.write(staff_final)

        # 5. Worker JS (index.js)
        worker_final = worker_template.replace("__MANAGER_PWD__", manager_pwd)
        with open(os.path.join(folder, "index.js"), "w", encoding="utf-8") as f: f.write(worker_final)

        # Success Message
        messagebox.showinfo("✅ สร้างสำเร็จ (V.80 - Clean Version)", f"โฟลเดอร์: {folder}\n\n1. ระบบ Whitelist พนักงาน\n2. หน้า Hub เช็คสิทธิ์\n3. แก้ไข History (+30 วัน)\n4. ตัดเรื่องการเงินออกหมดแล้ว\n\n📌 อย่าลืมกดปุ่ม 'อัปเดตฐานข้อมูล' ในหน้า Manager ครั้งแรกด้วยนะครับ!")

    except Exception as e:
        err_msg = traceback.format_exc()
        messagebox.showerror("❌ เกิดข้อผิดพลาด", f"โปรแกรมหยุดทำงาน:\n{err_msg}")

# ==========================================
# 🖥️ UI SETUP
# ==========================================
root = tk.Tk()
root.title("Soundabout Super App V.80 (Clean)")
root.geometry("600x800")
root.configure(bg="#1e293b")

style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background="#1e293b", borderwidth=0)
style.configure("TNotebook.Tab", background="#334155", foreground="white", padding=[20, 10], font=("Arial", 11, "bold"))
style.map("TNotebook.Tab", background=[("selected", "#0e4296")], foreground=[("selected", "white")])
style.configure("TFrame", background="#1e293b")

tk.Label(root, text="🍾 Super App Generator", font=("Arial", 20, "bold"), bg="#1e293b", fg="#38bdf8", pady=15).pack()

# PASTE BUTTON
tk.Button(root, text="📝 Paste Config (วางข้อมูลเดิม)", command=open_paste_window, bg="#f59e0b", fg="white", font=("bold", 12), pady=8).pack(fill="x", padx=20, pady=5)

# COLOR PICKER
color_frame = tk.Frame(root, bg="#1e293b", padx=20, pady=10)
color_frame.pack(fill="x")
tk.Label(color_frame, text="🎨 ธีมสีหลัก:", font=("bold", 12), bg="#1e293b", fg="#ffab40").pack(side="left")
color_preview = tk.Label(color_frame, bg=saved.get("theme_color", DEFAULT_THEME_COLOR), width=8, height=2, relief="solid")
color_preview.pack(side="left", padx=10)
def pick_color():
    c = colorchooser.askcolor(color_preview.cget('bg'))[1]
    if c: color_preview.config(bg=c); save_config({"theme_color": c})
tk.Button(color_frame, text="เลือกสี", command=pick_color, bg="#475569", fg="white").pack(side="left")

# NOTEBOOK
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=10)

# TAB 1: DEPOSIT
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

# TAB 2: BOOKING
tab_booking = ttk.Frame(notebook)
notebook.add(tab_booking, text="📅 ส่วนจองโต๊ะ")
f_b = tk.Frame(tab_booking, bg="#1e293b", padx=20, pady=20)
f_b.pack(fill="both", expand=True)

add_input(f_b, "1. LIFF ID (จองโต๊ะ):", "entry_booking_liff", "booking_liff")
add_input(f_b, "2. เวลาปิดรับจอง (เช่น 20:30):", "entry_booking_time", "booking_time", "20:00")

# GENERATE BUTTON (GLOBAL)
tk.Label(root, text="👇 สร้างไฟล์ทั้งหมดในคลิกเดียว (Hub + Deposit + Booking) 👇", bg="#1e293b", fg="#94a3b8", font=("Arial", 10)).pack()
tk.Button(root, text="✨ สร้าง Web App ครบวงจร (V.80)", command=generate_all_files, bg="#16a34a", fg="white", font=("bold", 14), pady=15).pack(fill="x", padx=20, pady=20)

root.mainloop()