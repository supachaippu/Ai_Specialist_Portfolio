import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import os
import re
import json

# --- LOGIC ---
DEFAULT_COLOR = "#2563eb"
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except: pass

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

def generate_all_files():
    liff_id = entry_liff.get().strip()
    worker_url = entry_worker.get().strip().rstrip('/')
    r2_url = entry_r2.get().strip().rstrip('/')
    shop_name = entry_shop.get().strip()
    theme_color = color_preview['bg']
    manager_pwd = entry_pwd.get().strip() or "1234"

    if not liff_id or not worker_url or not r2_url:
        messagebox.showwarning("⚠️ ข้อมูลไม่ครบ", "กรอกให้ครบทุกช่องครับลูกพี่")
        return

    save_config({"liff_id":liff_id, "worker_url":worker_url, "r2_url":r2_url, "shop_name":shop_name, "theme_color":theme_color, "manager_pwd":manager_pwd})

    # 1. Worker Script (เหมือน V.37 เป๊ะ เพราะ Logic ไม่เปลี่ยน)
    worker_code = f"""
export default {{
  async fetch(request, env) {{
    const corsHeaders = {{ "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" }};
    if (request.method === "OPTIONS") return new Response(null, {{ headers: corsHeaders }});
    const url = new URL(request.url);
    const MANAGER_PWD = "{manager_pwd}"; 

    if (request.method === "POST" && !url.searchParams.get('action')) {{
      try {{
        const formData = await request.formData();
        const image = formData.get("image");
        if (!image) throw new Error("No image");
        const objectName = crypto.randomUUID() + ".jpg";
        await env.BUCKET.put(objectName, image);
        const token = crypto.randomUUID().split('-')[0];
        const createdAt = new Date().toISOString();
        const expireDate = new Date(); expireDate.setDate(expireDate.getDate() + 14); 
        await env.DB.prepare("INSERT INTO deposits (id, brand, percent, note, shop_name, image_filename, claim_token, status, created_at, expire_date, bottle_label, staff_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), formData.get("brand"), formData.get("percent"), formData.get("note"), formData.get("shop"), objectName, token, 'pending', createdAt, expireDate.toISOString(), formData.get("bottle_label"), formData.get("staff_name")).run();
        return new Response(JSON.stringify({{ status: 'success', claimToken: token }}), {{ headers: corsHeaders }});
      }} catch (e) {{ return new Response(JSON.stringify({{ status: 'error', message: e.message }}), {{ headers: corsHeaders }}); }}
    }}

    if (request.method === "POST" && url.searchParams.get('action')) {{
        const action = url.searchParams.get('action');
        const body = await request.json();
        if (action === 'claim') {{
            const item = await env.DB.prepare("SELECT * FROM deposits WHERE claim_token = ?").bind(body.claimToken).first();
            if (!item) return new Response(JSON.stringify({{ status: 'error', message: 'ไม่พบ/หมดอายุ' }}), {{ headers: corsHeaders }});
            await env.DB.prepare("UPDATE deposits SET line_uid = ?, status = 'active', claim_token = NULL WHERE claim_token = ?").bind(body.lineUid, body.claimToken).run();
            return new Response(JSON.stringify({{ status: 'success', item: item }}), {{ headers: corsHeaders }});
        }}
        if (action === 'gen_token') {{
            const newToken = crypto.randomUUID().split('-')[0];
            await env.DB.prepare("UPDATE deposits SET claim_token = ? WHERE id = ? AND line_uid = ?").bind(newToken, body.id, body.lineUid).run();
            return new Response(JSON.stringify({{ status: 'success', token: newToken }}), {{ headers: corsHeaders }});
        }}
        if (action === 'pickup') {{
            const currentItem = await env.DB.prepare("SELECT * FROM deposits WHERE id = ?").bind(body.id).first();
            if (!currentItem) return new Response(JSON.stringify({{ status: 'error', message: 'ไม่พบรายการ' }}), {{ headers: corsHeaders }});
            if (currentItem.status === 'picked_up') {{ return new Response(JSON.stringify({{ status: 'error', message: '❌ รายการนี้ถูกเบิกไปแล้วครับ!' }}), {{ headers: corsHeaders }}); }}
            
            // ลบรูป R2
            if (currentItem.image_filename) await env.BUCKET.delete(currentItem.image_filename);

            const res = await env.DB.prepare("UPDATE deposits SET status = 'picked_up', image_filename = NULL WHERE id = ? RETURNING *").bind(body.id).first();
            return new Response(JSON.stringify({{ status: 'success', item: res }}), {{ headers: corsHeaders }});
        }}
        if (action === 'check_status') {{
            const item = await env.DB.prepare("SELECT status FROM deposits WHERE id = ?").bind(body.id).first();
            return new Response(JSON.stringify({{ status: 'success', itemStatus: item.status }}), {{ headers: corsHeaders }});
        }}
    }}

    if (request.method === "GET") {{
        const uid = url.searchParams.get("uid");
        const mode = url.searchParams.get("mode");
        const pwd = url.searchParams.get("pwd");
        if (mode === "manager") {{
            if (pwd !== MANAGER_PWD) return new Response(JSON.stringify({{ status: 'error', message: 'Wrong Password' }}), {{ status: 401, headers: corsHeaders }});
            const res = await env.DB.prepare("SELECT * FROM deposits ORDER BY created_at DESC LIMIT 100").all();
            return new Response(JSON.stringify(res.results), {{ headers: corsHeaders }});
        }}
        if (uid) {{
            const res = await env.DB.prepare("SELECT * FROM deposits WHERE line_uid = ? AND status = 'active' ORDER BY created_at DESC").bind(uid).all();
            return new Response(JSON.stringify(res.results), {{ headers: corsHeaders }});
        }}
    }}
    if (request.method === "DELETE") {{
        const urlParams = new URLSearchParams(url.search);
        const id = urlParams.get('id');
        if (urlParams.get('pwd') !== MANAGER_PWD) return new Response(JSON.stringify({{ status: 'error', message: 'Unauthorized' }}), {{ status: 401, headers: corsHeaders }});
        const item = await env.DB.prepare("SELECT image_filename FROM deposits WHERE id = ?").bind(id).first();
        if (item && item.image_filename) await env.BUCKET.delete(item.image_filename);
        await env.DB.prepare("DELETE FROM deposits WHERE id = ?").bind(id).run();
        return new Response(JSON.stringify({{ status: 'success' }}), {{ headers: corsHeaders }});
    }}
    return new Response("OK", {{ headers: corsHeaders }});
  }}
}};
"""

    common_head = f"""<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script><style>:root {{ --theme-color: {theme_color}; }} .bg-theme {{ background-color: var(--theme-color); }} .text-theme {{ color: var(--theme-color); }} .btn-primary {{ background-color: var(--theme-color); color: white; }} body {{ font-family: -apple-system, sans-serif; background-color: #f3f4f6; }} .tab-active {{ background-color: var(--theme-color); color: white; }} .tab-inactive {{ background-color: #e5e7eb; color: #374151; }} @keyframes pulse-red {{ 0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }} }} .urgent {{ animation: pulse-red 2s infinite; border: 2px solid #ef4444 !important; background-color: #fef2f2 !important; }}</style>"""

    # ==========================================
    # 📱 2. Index HTML (เปลี่ยนตัวเลข เป็น Progress Bar)
    # ==========================================
    index_html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{shop_name}</title><script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>{common_head}</head><body class="p-4"><div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden mb-4"><div class="p-4 bg-theme text-white text-center"><h1 class="text-xl font-bold">🍾 {shop_name}</h1><p class="text-sm opacity-90">รายการฝากของฉัน</p></div></div><div class="max-w-md mx-auto bg-white rounded-xl shadow-md p-6 min-h-[300px]"><div id="status" class="text-center text-gray-500 mt-10">กำลังโหลด...</div><div id="listContainer" class="space-y-4"></div></div>
    <script>
    const LIFF_ID="{liff_id}",WORKER_URL="{worker_url}",R2_URL="{r2_url}";
    let pollInterval = null, countdownInterval = null; 

    async function main(){{ await liff.init({{liffId:LIFF_ID}}); if(!liff.isLoggedIn()){{liff.login();return}} const p=await liff.getProfile(); const t=new URLSearchParams(location.search).get('token'); if(t) handleClaim(p.userId,t); else fetchList(p.userId); }}
    async function handleClaim(u,t){{ document.getElementById('status').innerText='รับของ...'; try{{const r=await fetch(`${{WORKER_URL}}?action=claim`,{{method:'POST',body:JSON.stringify({{lineUid:u,claimToken:t}})}}); const j=await r.json(); if(j.status==='success') Swal.fire('สำเร็จ','รับของแล้ว','success').then(()=>{{history.replaceState(null,'',location.pathname);fetchList(u)}}); else Swal.fire('!',j.message,'error').then(()=>{{history.replaceState(null,'',location.pathname);fetchList(u)}})}}catch(e){{alert('Error')}} }}
    
    async function fetchList(u){{ 
        const r=await fetch(`${{WORKER_URL}}?uid=${{u}}`); const d=await r.json(); const c=document.getElementById('listContainer'); document.getElementById('status').style.display='none'; c.innerHTML=''; if(d.length===0){{c.innerHTML='<p class="text-center text-gray-400">ว่างเปล่า</p>';return}} 
        d.forEach(i=>{{
            const now = new Date(); const exp = new Date(i.expire_date); const diffTime = exp - now; const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            let alertClass = "", alertMsg = "", dateColor = "text-gray-500";
            if(diffDays <= 7 && diffDays > 0) {{ alertClass = "urgent"; alertMsg = `<p class="text-red-600 font-bold text-lg animate-bounce">⚠️ เหลืออีก ${{diffDays}} วัน!</p>`; dateColor = "text-red-600 font-bold"; }} 
            else if (diffDays <= 0) {{ alertClass = "bg-gray-200 opacity-70"; alertMsg = `<p class="text-gray-500 font-bold">❌ หมดอายุแล้ว</p>`; }}
            
            // 🔥 คำนวณ % Bar
            let pVal = parseInt(i.percent) || 0;
            if(pVal > 100) pVal = 100; if(pVal < 0) pVal = 0;
            const barColor = pVal < 30 ? 'bg-red-500' : (pVal < 70 ? 'bg-yellow-500' : 'bg-green-500'); // สีเปลี่ยนตามระดับ

            const itemData = encodeURIComponent(JSON.stringify(i));
            c.innerHTML+=`
            <div class="bg-gray-50 p-3 rounded border flex flex-col gap-3 transition-all duration-300 ${{alertClass}}">
                ${{alertMsg}}
                <div class="flex gap-3">
                    <img src="${{R2_URL}}/${{i.image_filename}}" class="w-20 h-24 object-cover rounded bg-gray-200">
                    <div class="flex-1">
                        <h3 class="font-bold text-lg">${{i.brand}}</h3>
                        
                        <div class="mt-2">
                            <div class="flex justify-between text-xs mb-1">
                                <span class="text-gray-500">คงเหลือ</span>
                                <span class="font-bold">${{pVal}}%</span>
                            </div>
                            <div class="w-full bg-gray-300 rounded-full h-2.5">
                                <div class="${{barColor}} h-2.5 rounded-full" style="width: ${{pVal}}%"></div>
                            </div>
                        </div>

                        <p class="text-xs text-gray-500 mt-2">รหัส: ${{i.bottle_label||'-'}}</p>
                        <p class="text-sm ${{dateColor}}">📅 หมดอายุ: ${{exp.toLocaleDateString('th-TH')}}</p>
                    </div>
                </div>
                <div class="flex gap-2">
                    <button onclick="handleAction('${{i.id}}','withdraw', null)" class="flex-1 bg-green-600 text-white py-2 rounded text-sm font-bold shadow hover:bg-green-700">🍺 เบิกดื่ม</button>
                    <button onclick="handleAction('${{i.id}}','transfer', '${{itemData}}')" class="flex-1 bg-blue-600 text-white py-2 rounded text-sm font-bold shadow hover:bg-blue-700">🎁 ส่งให้เพื่อน</button>
                </div>
            </div>`
        }}) 
    }}

    async function handleAction(id, type, itemDataEncoded){{
        const p = await liff.getProfile();
        if(type==='withdraw'){{
            showQR(JSON.stringify({{action:'pickup',id:id}}),'ให้พนักงานสแกน');
            startPolling(id, p.userId);
        }} 
        else {{
            if (!liff.isApiAvailable('shareTargetPicker')) return Swal.fire('ไม่รองรับ', 'กรุณาอัปเดต LINE', 'warning');
            Swal.fire({{title:'สร้างลิงก์...', didOpen:()=>Swal.showLoading()}});
            const r = await fetch(`${{WORKER_URL}}?action=gen_token`, {{method:'POST', body:JSON.stringify({{id:id, lineUid:p.userId}})}});
            const j = await r.json();
            if(j.status === 'success'){{
                const claimLink = `https://liff.line.me/${{LIFF_ID}}?token=${{j.token}}`;
                const item = JSON.parse(decodeURIComponent(itemDataEncoded));
                const flexMsg = {{ type: "flex", altText: "🍾 มีของฝากถึงคุณ!", contents: {{ type: "bubble", hero: {{ type: "image", url: `${{R2_URL}}/${{item.image_filename}}`, size: "full", aspectRatio: "20:13", aspectMode: "cover" }}, body: {{ type: "box", layout: "vertical", contents: [ {{ type: "text", text: "🎁 คุณได้รับของฝาก", weight: "bold", size: "xl", color: "#1DB446" }}, {{ type: "text", text: `${{item.brand}} (${{item.percent}}%)`, weight: "bold", size: "md", margin: "md" }} ] }}, footer: {{ type: "box", layout: "vertical", contents: [ {{ type: "button", style: "primary", color: "#2563eb", action: {{ type: "uri", label: "รับของทันที", uri: claimLink }} }} ] }} }} }};
                Swal.close();
                liff.shareTargetPicker([flexMsg]).then(res => {{ if(res) Swal.fire('เรียบร้อย', 'ส่งแล้ว!', 'success').then(()=>fetchList(p.userId)); }}).catch(err => Swal.fire('Error', 'ส่งไม่ได้: '+err, 'error'));
            }}
        }}
    }}

    function showQR(d,t){{ 
        Swal.fire({{
            title:t, html:`<div id="qrcode" class="flex justify-center my-4"></div><p class="text-xl text-red-600 font-bold animate-pulse">⏳ สแกนภายใน <span id="timer">60</span> วินาที</p>`, confirmButtonText:'ปิด', allowOutsideClick: false, didClose: () => stopAllTimers()
        }}); 
        new QRCode(document.getElementById("qrcode"),{{text:d,width:200,height:200}}); 
    }}
    
    function startPolling(id, uid){{
        stopAllTimers();
        let timeLeft = 60; 
        countdownInterval = setInterval(() => {{
            timeLeft--;
            const timerElem = document.getElementById('timer');
            if(timerElem) timerElem.innerText = timeLeft;
            if(timeLeft <= 0) {{ stopAllTimers(); Swal.close(); Swal.fire('หมดเวลา', 'กรุณากดเบิกใหม่อีกครั้ง', 'warning').then(() => location.reload()); }}
        }}, 1000);

        pollInterval = setInterval(async () => {{
            try {{
                const r = await fetch(`${{WORKER_URL}}?action=check_status`, {{method:'POST', body:JSON.stringify({{id:id}})}});
                const j = await r.json();
                if(j.status === 'success' && j.itemStatus === 'picked_up'){{
                    stopAllTimers(); Swal.close(); Swal.fire('✅ เบิกสำเร็จ!', 'รับของเรียบร้อย', 'success').then(() => fetchList(uid));
                }}
            }} catch(e){{ console.log(e); }}
        }}, 2500); 
    }}

    function stopAllTimers(){{
        if(pollInterval) clearInterval(pollInterval);
        if(countdownInterval) clearInterval(countdownInterval);
        pollInterval = null; countdownInterval = null;
    }}

    main();
    </script></body></html>"""

    # 3. Staff HTML (คงเดิม V.37)
    staff_html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{shop_name} (Staff)</title>
    {common_head}
    <script src="https://unpkg.com/html5-qrcode"></script>
</head>
<body class="p-4 bg-gray-100">
    <div class="max-w-md mx-auto bg-white rounded-xl shadow-md mb-4">
        <div class="p-4 bg-gray-800 text-white text-center">
            <h1 class="text-xl font-bold">👮 Staff & Manager</h1>
            <div class="flex mt-4 gap-1">
                <button onclick="switchTab('deposit')" id="btn-deposit" class="flex-1 py-2 rounded font-bold tab-active">ฝาก</button>
                <button onclick="switchTab('withdraw')" id="btn-withdraw" class="flex-1 py-2 rounded font-bold tab-inactive">เบิก</button>
                <button onclick="switchTab('manager')" id="btn-manager" class="flex-1 py-2 rounded font-bold tab-inactive bg-gray-600 text-white">ผจก.</button>
            </div>
        </div>
    </div>
    
    <div id="sec-deposit" class="max-w-md mx-auto">
        <div class="bg-white rounded-xl shadow p-6 mb-4 text-center">
            <input type="file" id="cam" accept="image/*" capture="environment" class="hidden" onchange="previewImage(this)">
            <button onclick="document.getElementById('cam').click()" class="w-full btn-primary py-4 rounded-xl font-bold text-lg shadow-lg">📷 ถ่ายรูปฝาก</button>
        </div>
        <div id="pv" class="hidden bg-white rounded-xl shadow p-6 space-y-3">
            <img id="img" class="w-full h-56 object-cover rounded mb-4">
            <input id="s_name" placeholder="ชื่อพนักงาน" class="w-full p-2 border rounded">
            <input list="bl" id="br" placeholder="ยี่ห้อ" class="w-full p-2 border rounded">
            <datalist id="bl">
                <option value="Regency"><option value="Black Label"><option value="Red Label"><option value="Blend 285"><option value="SangSom">
            </datalist>
            <input type="number" id="pc" placeholder="%" class="w-full p-2 border rounded">
            <input id="lb" placeholder="รหัสขวด" class="w-full p-2 border rounded">
            <input id="nt" placeholder="หมายเหตุ" class="w-full p-2 border rounded">
            <button onclick="submitDeposit()" class="w-full bg-green-600 text-white py-3 rounded font-bold">ยืนยัน</button>
        </div>
    </div>

    <div id="sec-withdraw" class="max-w-md mx-auto hidden">
        <div class="bg-white rounded-xl shadow p-6 text-center">
            <h2 class="text-lg font-bold mb-4">สแกน QR ลูกค้าเพื่อเบิก</h2>
            <div id="reader" style="width: 100%; min-height: 250px; background: #000;"></div>
            <p id="scanRes" class="mt-4 text-gray-500">กำลังเปิดกล้อง...</p>
        </div>
    </div>

    <div id="sec-manager" class="max-w-md mx-auto hidden">
        <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-lg font-bold mb-4 text-center">🔐 พื้นที่ผู้จัดการ</h2>
            <div id="mgr-login" class="text-center space-y-3">
                <input type="password" id="mgr-pwd" placeholder="ใส่รหัสลับ" class="w-full p-3 border rounded text-center text-lg">
                <button onclick="mgrLogin()" class="w-full bg-gray-800 text-white py-3 rounded font-bold">เข้าสู่ระบบ</button>
            </div>
            <div id="mgr-content" class="hidden">
                <div class="flex justify-between mb-4">
                    <span class="font-bold text-green-700">เข้าสู่ระบบแล้ว ✅</span>
                    <button onclick="mgrLogout()" class="text-red-500 text-sm">ออก</button>
                </div>
                <button onclick="loadMgr()" class="w-full bg-blue-100 text-blue-800 py-2 rounded mb-4">🔄 รีเฟรชรายการ</button>
                <div class="overflow-x-auto max-h-[500px]">
                    <table class="w-full text-sm text-left">
                        <thead class="bg-gray-100"><tr><th class="p-2">ของ</th><th class="p-2">สถานะ</th><th class="p-2">ลบ</th></tr></thead>
                        <tbody id="mgr-tb"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
    const WORKER_URL="{worker_url}";
    const LIFF_ID="{liff_id}";
    let currentPwd = "";
    let html5QrCode;

    function compressImage(file) {{
        return new Promise((resolve) => {{
            const img = new Image(); img.src = URL.createObjectURL(file);
            img.onload = () => {{
                const canvas = document.createElement('canvas');
                const MAX_WIDTH = 800; const scaleSize = MAX_WIDTH / img.width;
                canvas.width = MAX_WIDTH; canvas.height = img.height * scaleSize;
                const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.7);
            }};
        }});
    }}

    async function switchTab(tab) {{
        if (html5QrCode && html5QrCode.isScanning) {{ try {{ await html5QrCode.stop(); html5QrCode.clear(); }} catch(e){{}} }}
        ['deposit', 'withdraw', 'manager'].forEach(t => {{
            document.getElementById('sec-' + t).classList.add('hidden');
            const btn = document.getElementById('btn-' + t);
            btn.classList.remove('tab-active'); btn.classList.add('tab-inactive');
            if (t === 'manager') btn.classList.add('bg-gray-600', 'text-white');
        }});
        document.getElementById('sec-' + tab).classList.remove('hidden');
        const activeBtn = document.getElementById('btn-' + tab);
        activeBtn.classList.add('tab-active'); activeBtn.classList.remove('tab-inactive');
        if (tab === 'withdraw') startScanInstant();
    }}

    function previewImage(input) {{
        if (input.files && input.files[0]) {{
            const reader = new FileReader();
            reader.onload = function(e) {{ document.getElementById('img').src = e.target.result; document.getElementById('pv').classList.remove('hidden'); }};
            reader.readAsDataURL(input.files[0]);
        }}
    }}
    async function submitDeposit() {{
        const fileInput = document.getElementById('cam');
        if (!fileInput.files[0]) return Swal.fire('!', 'กรุณาถ่ายรูป', 'warning');
        const brand = document.getElementById('br').value;
        const staff = document.getElementById('s_name').value;
        if (!brand || !staff) return Swal.fire('ข้อมูลไม่ครบ', 'ระบุยี่ห้อ + ชื่อพนักงาน', 'warning');
        Swal.fire({{ title: 'กำลังย่อรูปและบันทึก...', didOpen: () => Swal.showLoading() }});
        const compressedFile = await compressImage(fileInput.files[0]);
        const formData = new FormData();
        formData.append('image', compressedFile); formData.append('brand', brand); formData.append('percent', document.getElementById('pc').value);
        formData.append('note', document.getElementById('nt').value); formData.append('bottle_label', document.getElementById('lb').value);
        formData.append('shop', '{shop_name}'); formData.append('staff_name', staff);
        try {{
            const res = await fetch(WORKER_URL, {{ method: 'POST', body: formData }});
            const data = await res.json();
            if (data.status === 'success') {{
                Swal.fire({{ title: '✅ รับฝากสำเร็จ!', html: `<div id="qr2" class="flex justify-center my-2"></div><p class="text-sm text-gray-500">ให้ลูกค้าสแกนเพื่อรับของ</p>`, confirmButtonText: 'ตกลง (เริ่มใหม่)', allowOutsideClick: false }}).then(() => location.reload());
                setTimeout(() => {{ new QRCode(document.getElementById("qr2"), {{ text: `https://liff.line.me/${{LIFF_ID}}?token=${{data.claimToken}}`, width: 200, height: 200 }}); }}, 100);
            }} else Swal.fire('Error', data.message, 'error');
        }} catch (e) {{ Swal.fire('Error', 'Network Error', 'error'); }}
    }}

    function startScanInstant() {{
        if (!html5QrCode) html5QrCode = new Html5Qrcode("reader");
        html5QrCode.start({{ facingMode: "environment" }}, {{ fps: 10, qrbox: 250 }}, onScanSuccess).catch(err => {{ document.getElementById('scanRes').innerText = "เปิดกล้องไม่ได้: " + err; }});
    }}
    function onScanSuccess(decodedText, decodedResult) {{
        try {{
            const data = JSON.parse(decodedText);
            if (data.action === 'pickup') {{
                html5QrCode.pause();
                Swal.fire({{ title: 'ยืนยันเบิกของ?', text: 'รหัส: ' + data.id, showCancelButton: true }}).then(async (res) => {{
                    if (res.isConfirmed) {{
                        const r = await fetch(`${{WORKER_URL}}?action=pickup`, {{ method: 'POST', body: JSON.stringify({{ id: data.id }}) }});
                        const j = await r.json();
                        if (j.status === 'success') Swal.fire('ตัดสต็อกสำเร็จ', '', 'success');
                        else Swal.fire('ผิดพลาด', j.message, 'error');
                    }}
                    html5QrCode.resume();
                }});
            }}
        }} catch (e) {{ }}
    }}

    async function mgrLogin() {{
        const p = document.getElementById('mgr-pwd').value;
        const r = await fetch(`${{WORKER_URL}}?mode=manager&pwd=${{p}}`);
        if (r.status === 401) Swal.fire('!', 'รหัสผิด', 'error');
        else {{ currentPwd = p; document.getElementById('mgr-login').classList.add('hidden'); document.getElementById('mgr-content').classList.remove('hidden'); renderMgr(await r.json()); }}
    }}
    function mgrLogout() {{ currentPwd = ""; document.getElementById('mgr-login').classList.remove('hidden'); document.getElementById('mgr-content').classList.add('hidden'); document.getElementById('mgr-pwd').value = ''; }}
    async function loadMgr() {{ const r = await fetch(`${{WORKER_URL}}?mode=manager&pwd=${{currentPwd}}`); renderMgr(await r.json()); }}
    function renderMgr(d) {{
        const t = document.getElementById('mgr-tb'); t.innerHTML = '';
        d.forEach(i => {{
            let statusBadge = ""; let rowClass = "";
            if (i.status === 'picked_up') {{ statusBadge = `<span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-bold">✅ เบิกแล้ว</span>`; rowClass = "bg-green-50"; }} 
            else if (i.status === 'active') {{ statusBadge = `<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">ฝากอยู่</span>`; }} 
            else {{ statusBadge = `<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">รอรับ</span>`; }}
            t.innerHTML += `<tr class="border-b ${{rowClass}}"><td class="p-2"><b>${{i.brand}}</b> (${{i.percent}}%)<br><span class="text-xs text-gray-500">${{i.bottle_label || '-'}}</span></td><td class="p-2">${{statusBadge}}</td><td class="p-2"><button onclick="del('${{i.id}}')" class="bg-red-50 text-red-500 p-2 rounded hover:bg-red-100">🗑</button></td></tr>`;
        }});
    }}
    async function del(id) {{
        if (confirm('ยืนยันลบรายการนี้ทิ้ง? (กู้คืนไม่ได้)')) {{
            const r = await fetch(`${{WORKER_URL}}?id=${{id}}&pwd=${{currentPwd}}`, {{ method: 'DELETE' }});
            if ((await r.json()).status === 'success') loadMgr();
        }}
    }}
    </script>
</body>
</html>"""

    folder = f"web_{shop_name}_V38_ProgressBar"
    if not os.path.exists(folder): os.makedirs(folder)
    with open(os.path.join(folder, "index.js"), "w", encoding="utf-8") as f: f.write(worker_code)
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f: f.write(index_html)
    with open(os.path.join(folder, "staff.html"), "w", encoding="utf-8") as f: f.write(staff_html)
    
    messagebox.showinfo("✅ V.38 บาร์สวยๆ มาแล้ว!", f"หน้าลูกค้า: เปลี่ยนตัวเลขเป็นกราฟแท่ง (Progress Bar)\nเปลี่ยนสีตามระดับ (แดง/เหลือง/เขียว)\n\nโฟลเดอร์: {folder}")

# --- UI Setup ---
root = tk.Tk()
root.title("Soundabout V.38 (Progress Bar)")
root.geometry("650x900")
saved = load_config()

main = tk.Frame(root, padx=30, pady=20)
main.pack(fill="both", expand=True)

tk.Label(main, text="🛠️ สร้างเว็บ (Progress Bar)", font=("Arial", 20, "bold")).pack(pady=10)
tk.Button(main, text="📝 Paste Config", command=open_paste_window, bg="#f59e0b", fg="white", font=("bold", 12), pady=8).pack(fill="x", pady=10)

def add(lb, var, key, ph=""):
    tk.Label(main, text=lb, font=("Arial", 12, "bold"), anchor="w").pack(fill="x")
    e = tk.Entry(main, font=("Arial", 12), borderwidth=2, relief="groove")
    e.pack(fill="x", pady=5, ipady=5)
    e.insert(0, saved.get(key, ph))
    globals()[var] = e

add("1. LIFF ID:", "entry_liff", "liff_id")
add("2. Worker URL:", "entry_worker", "worker_url")
add("3. R2 URL:", "entry_r2", "r2_url")
add("4. ชื่อร้าน:", "entry_shop", "shop_name")
add("5. รหัสผู้จัดการ:", "entry_pwd", "manager_pwd", "9999")

tk.Label(main, text="6. สีธีม:", font=("bold", 12), anchor="w").pack(fill="x", pady=(15,0))
cF = tk.Frame(main); cF.pack(fill="x", pady=5)
color_preview = tk.Label(cF, bg=saved.get("theme_color", DEFAULT_COLOR), width=6, height=2, relief="solid"); color_preview.pack(side="left")
tk.Button(cF, text="🎨", command=lambda: color_preview.config(bg=colorchooser.askcolor()[1])).pack(side="right")

tk.Button(main, text="✅ สร้างไฟล์ (V.38)", command=generate_all_files, bg="#16a34a", fg="white", font=("bold", 16), pady=15).pack(fill="x", pady=20)

root.mainloop()