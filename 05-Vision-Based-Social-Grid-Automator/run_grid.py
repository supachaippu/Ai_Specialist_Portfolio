import os
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps
import mediapipe as mp
import numpy as np
import webbrowser
import shutil
import requests
import zipfile
import json
import base64

# ================= USER CONFIG =================
LINE_TOKEN = "ใส่_LINE_Token_ของคุณตรงนี้"
NETLIFY_TOKEN = "ใส่_Access_Token_จาก_Netlify"
NETLIFY_SITE_ID = "ใส่_API_ID_ของเว็บคุณ"
TRACKING_SCRIPT_URL = "ใส่_Google_Apps_Script_URL_ของคุณ" 

# --- 🔐 รายชื่อลูกค้า (Dropdown) ---
CLIENT_ACCOUNTS = [
    {"name": "VIP User 1", "pass": "90"},
    {"name": "K. Siri",    "pass": "Siri"},
    {"name": "K. Ball",    "pass": "Ball"},
    {"name": "K. Velvet",  "pass": "Velvet"}
]
# ===============================================

QUALITY = 100
PREVIEW_MAX_WIDTH = 800

TEMPLATES = {
    '01_FB_แนวตั้ง_1+2': {'type': 'v', 'category': 'FB Vertical', 'slots': [(960, 1920), (1920, 1920), (1920, 1920)], 'stitch': {'canvas': (2000, 2000), 'resize_to': [(1000, 2000), (1000, 1000), (1000, 1000)], 'pos': [(0,0), (1000,0), (1000,1000)]}},
    '02_FB_ผสม_2+3_VerticalSplit': {'type': 'sq', 'category': 'FB Mix', 'slots': [(1920, 1920), (1920, 1920), (1920, 1280), (1920, 1280), (1920, 1280)], 'stitch': {'canvas': (1200, 1200), 'resize_to': [(600, 600), (600, 600), (600, 400), (600, 400), (600, 400)], 'pos': [(0,0), (0,600), (600,0), (600,400), (600,800)]}},
    '03_FB_แนวตั้ง_1+3': {'type': 'v', 'category': 'FB Vertical', 'slots': [(1280, 1920), (1920, 1920), (1920, 1920), (1920, 1920)], 'stitch': {'canvas': (2400, 2400), 'resize_to': [(1600, 2400), (800, 800), (800, 800), (800, 800)], 'pos': [(0,0), (1600,0), (1600,800), (1600,1600)]}},
    '04_FB_แนวนอน_1+2': {'type': 'h', 'category': 'FB Horizontal', 'slots': [(1920, 960), (1920, 1920), (1920, 1920)], 'stitch': {'canvas': (2000, 2000), 'resize_to': [(2000, 1000), (1000, 1000), (1000, 1000)], 'pos': [(0,0), (0,1000), (1000,1000)]}},
    '05_FB_แนวนอน_1+3': {'type': 'h', 'category': 'FB Horizontal', 'slots': [(1920, 1280), (1920, 1920), (1920, 1920), (1920, 1920)], 'stitch': {'canvas': (2400, 2400), 'resize_to': [(2400, 1600), (800, 800), (800, 800), (800, 800)], 'pos': [(0,0), (0,1600), (800,1600), (1600,1600)]}},
    '06_FB_ผสม_2+3_HorizontalSplit': {'type': 'sq', 'category': 'FB Mix', 'slots': [(1920, 1920), (1920, 1920), (1920, 1920), (1920, 1920), (1920, 1920)], 'stitch': {'canvas': (1200, 1000), 'resize_to': [(600, 600), (600, 600), (400, 400), (400, 400), (400, 400)], 'pos': [(0,0), (600,0), (0,600), (400,600), (800,600)]}},
    '07_FB_จัตุรัส_4': {'type': 'sq', 'category': 'FB Mix', 'slots': [(1920, 1920)]*4, 'stitch': {'canvas': (2000, 2000), 'resize_to': [(1000, 1000)]*4, 'pos': [(0,0), (1000,0), (0,1000), (1000,1000)]}},
    'IG_Portrait_4:5': {'type': 'v', 'category': 'Instagram', 'slots': [(1080, 1350)], 'stitch': {'canvas': (1080,1350), 'resize_to': [(1080,1350)], 'pos': [(0,0)]}},
    'TikTok_9:16':     {'type': 'v', 'category': 'TikTok', 'slots': [(1080, 1920)], 'stitch': {'canvas': (1080,1920), 'resize_to': [(1080,1920)], 'pos': [(0,0)]}},
}

mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# --- Helper Functions ---
def get_smart_center(pil_image):
    try:
        img_np = np.array(pil_image)
        results = face_detector.process(img_np)
        if not results.detections: return (0.5, 0.5)
        sum_x=0; sum_y=0; count=0
        for d in results.detections:
            b = d.location_data.relative_bounding_box
            sum_x += b.xmin + b.width/2; sum_y += b.ymin + b.height/2
            count += 1
        return (max(0, min(1, sum_x/count)), max(0, min(1, sum_y/count)))
    except: return (0.5, 0.5)

def get_image_orientation(pil_image):
    w, h = pil_image.size
    ratio = w / h
    if 0.9 <= ratio <= 1.1: return 'sq'
    elif w > h: return 'h'
    else: return 'v'

def compute_dhash(pil_image):
    try:
        img = pil_image.convert('L').resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(img.getdata())
        diff = []
        for row in range(8):
            for col in range(8):
                diff.append(pixels[row*9+col] > pixels[row*9+col+1])
        return diff
    except: return []

def is_too_similar(hash1, hash2, threshold=15):
    if not hash1 or not hash2: return False
    return sum(h1 != h2 for h1, h2 in zip(hash1, hash2)) < threshold

def apply_logo(bg_image, logo_path):
    if not logo_path or not os.path.exists(logo_path): return bg_image
    try:
        logo = Image.open(logo_path).convert("RGBA")
        bg_w, bg_h = bg_image.size
        scale_ratio = 0.15 
        new_logo_w = int(bg_w * scale_ratio)
        aspect_ratio = logo.height / logo.width
        new_logo_h = int(new_logo_w * aspect_ratio)
        logo = logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)
        margin_bottom = int(bg_h * 0.05)
        x = (bg_w - new_logo_w) // 2
        y = bg_h - new_logo_h - margin_bottom
        bg_image.paste(logo, (x, y), logo)
        return bg_image
    except: return bg_image

def create_preview_stitch(set_dir, tmpl_name, generated_files):
    if tmpl_name not in TEMPLATES or 'stitch' not in TEMPLATES[tmpl_name]: return None
    st = TEMPLATES[tmpl_name]['stitch']
    canvas = Image.new('RGB', st['canvas'], (255, 255, 255))
    try:
        for i, path in enumerate(generated_files):
            if i < len(st['pos']):
                with Image.open(path) as img:
                    target_w, target_h = st['resize_to'][i]
                    img_resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    canvas.paste(img_resized, st['pos'][i])
        canvas.thumbnail((PREVIEW_MAX_WIDTH, PREVIEW_MAX_WIDTH))
        p = os.path.join(set_dir, "PREVIEW_MOCKUP.jpg")
        canvas.save(p, quality=85)
        return p
    except: return None

# --- SECURITY FUNCTIONS ---
def simple_obfuscate(password):
    salted = password[::-1] + "_SG_SECURE"
    return base64.b64encode(salted.encode()).decode()

def get_auth_config():
    config = {}
    for client in CLIENT_ACCOUNTS:
        h = simple_obfuscate(client['pass'])
        config[h] = client['name']
    return json.dumps(config)

# --- HTML Generator ---
def generate_web_files(outp, data_list):
    data_list.sort(key=lambda x: x['set_name'])
    auth_config_json = get_auth_config()
    
    categories = sorted(list(set([d['category'] for d in data_list])))
    buttons_html = "".join([f" <button class='filter-btn' onclick=\"filter('{c}')\">{c}</button>" for c in categories])
    
    tracking_script = ""
    if TRACKING_SCRIPT_URL:
        tracking_script = f"""const TRACKING_URL = "{TRACKING_SCRIPT_URL}"; function trackAction(s,a){{fetch(TRACKING_URL+"?set="+encodeURIComponent(s)+"&action="+encodeURIComponent(a),{{mode:'no-cors'}}).catch(e=>console.log(e));}} function confirmDelete(s){{if(confirm("ยืนยันรับไฟล์แล้ว?")){{trackAction(s,'🚨 CONFIRMED_DELETE');alert("ขอบคุณครับ ระบบจะทำการลบไฟล์เร็วๆนี้");}}}}"""

    # --- HTML STRUCTURE ---
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Gallery</title><style>
        body{{font-family:'Prompt',sans-serif;background:#f1f5f9;padding:0;margin:0;color:#334155;height:100vh;display:flex;flex-direction:column;}}
        #login-section{{display:flex;align-items:center;justify-content:center;height:100%;background:#1e293b;position:fixed;width:100%;z-index:999;transition: opacity 0.5s;}}
        .login-box{{background:#334155;padding:40px;border-radius:16px;text-align:center;width:300px;box-shadow:0 10px 30px rgba(0,0,0,0.5);}}
        .login-box input{{width:80%;padding:12px;margin:20px 0;border-radius:8px;border:none;text-align:center;font-size:16px;}}
        .login-box button{{width:90%;padding:12px;border-radius:8px;border:none;background:#3b82f6;color:white;font-weight:bold;cursor:pointer;font-size:16px;}}
        .login-box button:hover{{background:#2563eb;}}
        #gallery-section{{display:none;padding:20px;}}
        .header{{display:flex;justify-content:space-between;margin-bottom:20px;align-items:center;padding-bottom:15px;border-bottom:1px solid #cbd5e1;}}
        .badge{{background:#dbeafe;color:#1e40af;padding:5px 15px;border-radius:20px;font-weight:bold;}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:25px;}}
        .card{{background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);display:none;}} 
        .preview img{{width:100%;display:block;}}
        .info{{padding:15px;}}
        .btn{{display:block;width:100%;padding:10px;margin-top:5px;text-align:center;border-radius:8px;text-decoration:none;font-weight:bold;cursor:pointer;}}
        .zip{{background:#10b981;color:white;}} .del{{background:#fff1f2;color:#e11d48;border:1px solid #fda4af;}}
        .img-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:5px;margin-top:10px;}}
        .img-btn{{background:#eff6ff;border:1px solid #bfdbfe;color:#1d4ed8;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:14px;}}
        .modal{{display:none;position:fixed;z-index:2000;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.9);align-items:center;justify-content:center;flex-direction:column;}}
        .modal-content{{max-width:90%;max-height:80vh;object-fit:contain;}}
        .modal-controls{{margin-top:20px;display:flex;gap:15px;}}
        .action-btn{{padding:10px 20px;border-radius:50px;border:none;font-weight:bold;cursor:pointer;color:white;}}
        .save{{background:#2563eb;}} .close{{background:#334155;}}
        .hidden{{display:none !important;}}
    </style></head><body>

    <div id="login-section">
        <div class="login-box">
            <h2 style="color:white">🔒 Gallery Login</h2>
            <p style="color:#94a3b8;font-size:14px">ใส่รหัสผ่านของคุณเพื่อเข้าชม</p>
            <input type="password" id="passInput" placeholder="Password" onkeypress="if(event.key==='Enter') doLogin()">
            <button onclick="doLogin()">เข้าสู่ระบบ</button>
        </div>
    </div>

    <div id="gallery-section">
        <div class="header">
            <div>ยินดีต้อนรับ, <span id="uName" class="badge">...</span></div>
            <button onclick="logout()" style="background:none;border:none;color:#ef4444;font-weight:bold;cursor:pointer">ออกจากระบบ</button>
        </div>
        <div style="text-align:center;margin-bottom:30px">
            <h1>📸 Social Grid Gallery</h1>
            <button onclick="filter('all')" class="filter-btn">All</button>{buttons_html}
        </div>
        <div class="grid">"""
    
    for d in data_list:
        fname = os.path.basename(d['folder'])
        img_btns = ""
        count = d.get('file_count', len([f for f in os.listdir(d['folder']) if f.endswith('.jpg') and 'PREVIEW' not in f]))
        for i in range(1, count + 1):
            path = f"./{fname}/{i}.jpg"
            track = f"trackAction('{d['set_name']}', 'View_{i}');" if TRACKING_SCRIPT_URL else ""
            img_btns += f'<div class="img-btn" onclick="{track} openModal(\'{path}\')">{i}</div>'
        del_btn = f'<button class="btn del" onclick="confirmDelete(\'{d["set_name"]}\')">✅ แจ้งลบ</button>' if TRACKING_SCRIPT_URL else ""
        
        # KEY CHANGE: Read owner from metadata (info.json)
        owner_hash = d.get('owner_hash', 'unknown')
        
        html += f"""
        <div class="card" data-owner="{owner_hash}" data-cat="{d['category']}">
            <div class="preview"><img src="./{fname}/PREVIEW_MOCKUP.jpg"></div>
            <div class="info">
                <b>{d['set_name']}</b><br><span style="font-size:12px;color:gray">{d['tmpl']}</span>
                <a href="./{fname}/{d['zip_name']}" class="btn zip" onclick="trackAction('{d['set_name']}','ZIP')">📦 Download ZIP</a>
                <div class="img-grid">{img_btns}</div>
                {del_btn}
            </div>
        </div>"""

    html += f"""</div></div>
    <div id="imageModal" class="modal" onclick="closeModal()">
        <img id="modalImg" class="modal-content" onclick="event.stopPropagation()">
        <div class="modal-controls" onclick="event.stopPropagation()">
            <button class="action-btn save" onclick="shareImage()">📤 บันทึก/แชร์</button>
            <button class="action-btn close" onclick="closeModal()">❌ ปิด</button>
        </div>
    </div>
    <script>
        {tracking_script}
        const users = {auth_config_json};
        let currentUser = null;

        function simpleHash(s) {{
            let reversed = s.split('').reverse().join('');
            let salted = reversed + "_SG_SECURE";
            return btoa(salted);
        }}

        function doLogin() {{
            let p = document.getElementById('passInput').value.trim();
            let h = simpleHash(p);
            if (users[h]) {{
                alert("✅ ยินดีต้อนรับ " + users[h]);
                currentUser = h;
                showGallery(users[h]);
            }} else {{
                alert("❌ รหัสผ่านไม่ถูกต้อง!");
                document.getElementById('passInput').value = '';
            }}
        }}

        function showGallery(name) {{
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('gallery-section').style.display = 'block';
            document.getElementById('uName').innerText = name;
            document.querySelectorAll('.card').forEach(c => {{
                if (c.dataset.owner === currentUser) {{
                    c.style.display = 'block';
                }}
            }});
        }}

        function logout() {{ location.reload(); }}

        function filter(c){{
            document.querySelectorAll('.card').forEach(i=>{{
                if (i.dataset.owner === currentUser) {{
                    i.classList.toggle('hidden', c!=='all' && i.dataset.cat!==c);
                }}
            }});
        }}
        
        const modal=document.getElementById('imageModal'); const modalImg=document.getElementById('modalImg'); let curUrl='';
        function openModal(url){{curUrl=url; modalImg.src=url; modal.style.display="flex";}}
        function closeModal(){{modal.style.display="none"; modalImg.src="";}}
        async function shareImage(){{
            if(!curUrl)return;
            if(navigator.share){{try{{const r=await fetch(curUrl); const b=await r.blob(); await navigator.share({{files:[new File([b],'img.jpg',{{type:'image/jpeg'}})]}});}}catch(e){{alert("กดค้างเพื่อ Save");}}}}else{{alert("กดค้างเพื่อ Save");}}
        }}
    </script></body></html>"""
    
    with open(os.path.join(outp, "index.html"), "w", encoding="utf-8") as f: f.write(html)

# --- Save/Load Info ---
def save_set_info(folder_path, info):
    try:
        with open(os.path.join(folder_path, "info.json"), "w", encoding="utf-8") as f: json.dump(info, f, ensure_ascii=False)
    except: pass

def load_set_info(folder_path):
    try:
        with open(os.path.join(folder_path, "info.json"), "r", encoding="utf-8") as f: return json.load(f)
    except: return {'category': 'Gallery', 'tmpl': 'Unknown', 'file_count': 0, 'owner_hash': 'unknown'}

# --- Deploy & Notify ---
def deploy_to_netlify(folder, site_id, token):
    if not site_id or not token: return None, "Token Missing"
    try:
        zip_path = folder + "_deploy.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for r, _, fs in os.walk(folder):
                for f in fs: z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), folder))
        url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
        r = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/zip"}, data=open(zip_path, 'rb').read())
        os.remove(zip_path)
        return (r.json().get('url'), None) if r.status_code==200 else (None, r.text)
    except Exception as e: return None, str(e)

def send_line(msg):
    if LINE_TOKEN: requests.post('https://notify-api.line.me/api/notify', headers={'Authorization': 'Bearer '+LINE_TOKEN}, data={'message': msg})

# --- Main App ---
class SocialGridApp:
    def __init__(self, root):
        self.root = root; self.root.title("Social Grid V35 (Select Client)")
        self.root.geometry("600x850"); 
        self.input_folder = tk.StringVar(); self.output_folder = tk.StringVar(value=os.path.join(os.getcwd(), 'Output_Website'))
        self.logo_path = tk.StringVar() 
        self.num_sets = tk.IntVar(value=10)
        self.use_ai = tk.BooleanVar(value=True); self.use_smart = tk.BooleanVar(value=True); self.use_anti_dup = tk.BooleanVar(value=True)
        self.template_vars = {}; self.manage_vars = {}
        self.last_url = ""
        self.selected_client = tk.StringVar() # New variable for dropdown
        
        nb = ttk.Notebook(root); nb.pack(fill="both", expand=True)
        self.t1 = ttk.Frame(nb); nb.add(self.t1, text="⚡ Auto Pilot")
        self.t2 = ttk.Frame(nb); nb.add(self.t2, text="🗑️ Manage")
        self.ui_auto(); self.ui_manage()

    def ui_auto(self):
        p = ttk.Frame(self.t1, padding=15); p.pack(fill="both", expand=True)
        
        # --- NEW: CLIENT SELECTOR ---
        f0 = ttk.LabelFrame(p, text="👤 1. เลือกเจ้าของงาน", padding=10); f0.pack(fill="x")
        client_names = [c['name'] for c in CLIENT_ACCOUNTS]
        self.cb_client = ttk.Combobox(f0, textvariable=self.selected_client, values=client_names, state="readonly")
        self.cb_client.pack(fill="x")
        if client_names: self.cb_client.current(0)
        # -----------------------------

        f1 = ttk.LabelFrame(p, text="📂 2. เลือกรูป & โลโก้", padding=10); f1.pack(fill="x", pady=5)
        ttk.Button(f1, text="เลือกโฟลเดอร์รูป", command=self.select_folder).pack(fill="x", pady=2)
        ttk.Button(f1, text="เลือกโลโก้ (PNG)", command=self.select_logo).pack(fill="x", pady=2)
        
        f2 = ttk.LabelFrame(p, text="⚙️ 3. Config", padding=10); f2.pack(fill="x", pady=5)
        ttk.Checkbutton(f2, text="AI Face", variable=self.use_ai).pack(side="left")
        ttk.Checkbutton(f2, text="Smart Match", variable=self.use_smart).pack(side="left", padx=5)
        ttk.Checkbutton(f2, text="Anti-Dup", variable=self.use_anti_dup).pack(side="left")
        
        f3 = ttk.LabelFrame(p, text="🎨 4. Template", padding=5); f3.pack(fill="both", expand=True)
        cv = tk.Canvas(f3, height=100); sc = ttk.Scrollbar(f3, command=cv.yview); 
        tf = ttk.Frame(cv); cv.create_window((0,0), window=tf, anchor="nw"); tf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.configure(yscrollcommand=sc.set); cv.pack(side="left", fill="both", expand=True); sc.pack(side="right", fill="y")
        for k in TEMPLATES:
            self.template_vars[k] = tk.BooleanVar(value=True)
            ttk.Checkbutton(tf, text=k, variable=self.template_vars[k]).pack(anchor="w")
            
        f4 = ttk.Frame(p, padding=10); f4.pack(fill="x")
        ttk.Label(f4, text="จำนวน:").pack(side="left"); ttk.Spinbox(f4, from_=1, to=999, textvariable=self.num_sets, width=5).pack(side="left")
        ttk.Button(f4, text="Clear Old", command=self.clear_old).pack(side="right")
        
        self.btn_run = tk.Button(p, text="🚀 START AUTO PILOT", command=self.start, bg="#2563eb", fg="white", font=("bold", 12), pady=10); self.btn_run.pack(fill="x")
        self.btn_view_web = tk.Button(p, text="🌐 เปิดดูเว็บล่าสุด", command=lambda: webbrowser.open(self.last_url) if self.last_url else None, state="disabled", bg="#059669", fg="white", font=("bold", 10), pady=5)
        self.btn_view_web.pack(fill="x", pady=5)
        self.status = ttk.Label(p, text="Ready", foreground="gray"); self.status.pack()

    def ui_manage(self):
        p = ttk.Frame(self.t2, padding=15); p.pack(fill="both", expand=True)
        ttk.Button(p, text="🔄 Refresh List", command=self.refresh_m).pack(anchor="e")
        f = ttk.LabelFrame(p, text="Online Items"); f.pack(fill="both", expand=True, pady=10)
        cv = tk.Canvas(f); sc = ttk.Scrollbar(f, command=cv.yview)
        self.mf = ttk.Frame(cv); cv.create_window((0,0), window=self.mf, anchor="nw"); self.mf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.configure(yscrollcommand=sc.set); cv.pack(side="left", fill="both", expand=True); sc.pack(side="right", fill="y")
        self.btn_del = tk.Button(p, text="🗑️ Delete Selected & Update", command=self.do_del, bg="#ef4444", fg="white", font=("bold", 12), pady=10); self.btn_del.pack(fill="x")

    def select_folder(self):
        try: path=filedialog.askdirectory(); 
        except: path=""
        if path: self.input_folder.set(path)

    def select_logo(self):
        try: path=filedialog.askopenfilename(filetypes=[("PNG","*.png"),("All","*.*")]); 
        except: path=""
        if path: self.logo_path.set(path)

    def clear_old(self):
        if messagebox.askyesno("Confirm", "ล้างไฟล์เก่าทั้งหมด?"):
            shutil.rmtree(self.output_folder.get(), ignore_errors=True)
            self.refresh_m()

    def start(self): threading.Thread(target=self.run).start()

    def run(self):
        try:
            inp, out, logo = self.input_folder.get(), self.output_folder.get(), self.logo_path.get()
            if not inp: self.btn_run.config(state="normal"); return 
            
            # --- GET SELECTED CLIENT INFO ---
            sel_name = self.selected_client.get()
            sel_pass = next((c['pass'] for c in CLIENT_ACCOUNTS if c['name'] == sel_name), "90")
            sel_hash = simple_obfuscate(sel_pass) # Create owner hash for this run
            # --------------------------------

            self.btn_run.config(state="disabled", text="Running...")
            if not os.path.exists(out): os.makedirs(out)
            exts = ('.jpg','.png','.webp'); pool = [os.path.join(inp, f) for f in os.listdir(inp) if f.lower().endswith(exts)]
            if len(pool)<3: self.status.config(text="❌ Not enough images"); self.btn_run.config(state="normal"); return

            existing = sorted([d for d in os.listdir(out) if d.startswith("Set_")])
            start_idx = int(existing[-1].split('_')[1]) + 1 if existing else 1
            target = self.num_sets.get(); cnt=0
            
            while cnt < target:
                self.status.config(text=f"Processing {cnt+1}/{target}...")
                random.shuffle(pool)
                hero = pool[0]; tmpl_keys=[k for k,v in self.template_vars.items() if v.get()]
                if not tmpl_keys: break
                tmpl = random.choice(tmpl_keys)
                if self.use_smart.get():
                    try:
                        with Image.open(hero) as img: ori = get_image_orientation(img)
                        matches = [t for t in tmpl_keys if TEMPLATES[t]['type'] == ori]
                        if not matches and ori=='h': matches = [t for t in tmpl_keys if TEMPLATES[t]['type'] in ('h','sq')]
                        if matches: tmpl = random.choice(matches); print(f"🧠 Smart: {ori}->{tmpl}")
                    except: pass
                slots = TEMPLATES[tmpl]['slots']; needed = len(slots); 
                selected_imgs = []; selected_hashes = []; attempts = 0
                if len(pool) < needed: pool = list(pool); random.shuffle(pool)
                while len(selected_imgs) < needed:
                    if not pool: break
                    cand = pool.pop(0)
                    if self.use_anti_dup.get():
                        try:
                            with Image.open(cand) as c_img:
                                h = compute_dhash(c_img)
                                if any(is_too_similar(h, existing) for existing in selected_hashes): 
                                    print("🚫 Dup skipped"); continue
                                selected_hashes.append(h)
                        except: pass
                    selected_imgs.append(cand)
                if len(selected_imgs) < needed:
                    remain = needed - len(selected_imgs)
                    pool = [os.path.join(inp, f) for f in os.listdir(inp) if f.lower().endswith(exts)]
                    random.shuffle(pool)
                    selected_imgs.extend(pool[:remain])
                sname = f"Set_{start_idx+cnt:03d}"; d = os.path.join(out, sname); os.makedirs(d)
                gen = []
                for i, (w,h) in enumerate(slots):
                    try:
                        with Image.open(selected_imgs[i]) as img:
                            img = img.convert('RGB')
                            c = get_smart_center(img) if self.use_ai.get() else (0.5,0.5)
                            final = ImageOps.fit(img, (w,h), method=Image.Resampling.LANCZOS, centering=c)
                            if logo: final = apply_logo(final, logo)
                            p = os.path.join(d, f"{i+1}.jpg"); final.save(p, quality=100); gen.append(p)
                    except: pass
                create_preview_stitch(d, tmpl, gen)
                shutil.make_archive(os.path.join(out, sname), 'zip', d)
                shutil.move(os.path.join(out, f"{sname}.zip"), os.path.join(d, f"{sname}.zip"))
                
                # --- SAVE WITH SPECIFIC OWNER ---
                save_set_info(d, {
                    'set_name': sname, 'tmpl': tmpl, 
                    'category': TEMPLATES[tmpl].get('category', 'Gallery'),
                    'file_count': len(gen), 'zip_name': f"{sname}.zip",
                    'owner_hash': sel_hash # Save the specific owner
                })
                cnt+=1
            self.rebuild_and_deploy()
        except Exception as e:
            print(f"ERROR: {e}")
            self.status.config(text=f"Error: {e}")
            self.btn_run.config(state="normal")

    def rebuild_and_deploy(self):
        out = self.output_folder.get()
        sets = sorted([d for d in os.listdir(out) if d.startswith("Set_")])
        data_list = []
        for s in sets:
            info = load_set_info(os.path.join(out, s))
            info['folder'] = os.path.join(out, s)
            if 'set_name' not in info: info['set_name'] = s
            if 'zip_name' not in info: info['zip_name'] = f"{s}.zip"
            data_list.append(info)
        generate_web_files(out, data_list)
        self.status.config(text="☁️ Uploading...")
        u, e = deploy_to_netlify(out, NETLIFY_SITE_ID, NETLIFY_TOKEN)
        if u: 
            webbrowser.open(u); send_line(f"New work: {u}")
            self.last_url = u
            self.btn_view_web.config(state="normal")
            self.status.config(text="✅ Done!")
        else: self.status.config(text=f"❌ Error: {e}")
        self.btn_run.config(state="normal", text="🚀 START AUTO PILOT")
        self.refresh_m()

    def refresh_m(self):
        for w in self.mf.winfo_children(): w.destroy()
        self.manage_vars = {}
        if not os.path.exists(self.output_folder.get()): return
        for d in sorted([x for x in os.listdir(self.output_folder.get()) if x.startswith("Set_")]):
            v = tk.BooleanVar(); self.manage_vars[d] = v
            ttk.Checkbutton(self.mf, text=d, variable=v).pack(anchor="w")

    def do_del(self):
        out = self.output_folder.get()
        for k,v in self.manage_vars.items():
            if v.get(): shutil.rmtree(os.path.join(out, k))
        self.rebuild_and_deploy()

if __name__ == "__main__":
    root = tk.Tk(); app = SocialGridApp(root); root.mainloop()