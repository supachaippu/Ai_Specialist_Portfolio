import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
from PIL import Image, ImageOps
import numpy as np
import os
import shutil
import threading
import json
import random
import cv2
import http.server
import socketserver
import webbrowser
import time
from datetime import date, timedelta, datetime

# --- CONFIGURATIONS ---
PROJECT_DEFAULT = "Jan_Content"
CONFIG_FILE = "cms_config.json"
USERS_FILE = "cms_users.json"

# --- TEMPLATES SPECS (UPDATED V60) ---
TEMPLATES = {
    "T1": { 
        "name": "1. จัตุรัส 4 (4 รูป)", 
        "specs": [
            (1080, 1080), (1080, 1080), 
            (1080, 1080), (1080, 1080)
        ] 
    },
    "T2": { 
        "name": "2. แนวนอน 1+2 (3 รูป)", 
        "specs": [
            (1200, 800),   # บน (3:2)
            (1080, 1080),  # ล่างซ้าย (1:1)
            (1080, 1080)   # ล่างขวา (1:1)
        ] 
    },
    "T3": { 
        "name": "3. แนวตั้ง 1+2 (3 รูป)", 
        "specs": [
            (1280, 1920),  # ซ้าย (แนวตั้ง)
            (1080, 1080),  # ขวาบน (1:1)
            (1080, 1080)   # ขวาล่าง (1:1)
        ] 
    },
    "T4": { 
        "name": "4. จัตุรัส 2+3 (5 รูป)", 
        "specs": [
            (1200, 1200), (1200, 1200),             # แถวบน 2 รูป
            (1200, 1200), (1200, 1200), (1200, 1200) # แถวล่าง 3 รูป
        ] 
    }
}

class AutoGridV59:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGrid V60 (Fixed Layout & Ratios)")
        self.root.geometry("1000x950")
        self.root.configure(bg="#1e1e1e")
        
        self.users = self.load_json(USERS_FILE, {})
        self.config = self.load_json(CONFIG_FILE, {"project": PROJECT_DEFAULT})
        
        self.input_dir = ""
        self.food_dir = ""
        self.output_dir = ""
        self.logo_path = ""
        
        self.files_main = []
        self.files_food = []
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.server_port = 8098
        self.httpd = None
        self.deploy_path = ""
        self.running = False
        
        self.setup_ui()

    def load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default

    def save_json(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        tabs = ttk.Notebook(self.root)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_main = tk.Frame(tabs, bg="#1e1e1e")
        self.tab_logs = tk.Frame(tabs, bg="#000000")
        
        tabs.add(self.tab_main, text=" SETTINGS ")
        tabs.add(self.tab_logs, text=" LOGS ")
        
        self.setup_main_tab()
        self.setup_logs_tab()

    def setup_main_tab(self):
        p = self.tab_main
        
        # 1. INFO
        f1 = tk.LabelFrame(p, text=" 1. Client Info & Date ", bg="#1e1e1e", fg="#00BFFF", font=("bold", 12))
        f1.pack(fill="x", pady=5, padx=10)
        
        tk.Label(f1, text="User:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5)
        self.cb_user = ttk.Combobox(f1, values=list(self.users.keys()), width=15, state="readonly")
        self.cb_user.grid(row=0, column=1, padx=5)
        self.cb_user.bind("<<ComboboxSelected>>", self.on_user_select)
        
        tk.Label(f1, text="Project:", bg="#1e1e1e", fg="white").grid(row=0, column=2, padx=5)
        self.ent_proj = tk.Entry(f1, bg="#333", fg="white", width=15)
        self.ent_proj.grid(row=0, column=3, padx=5)
        self.ent_proj.insert(0, self.config.get("project", PROJECT_DEFAULT))
        
        tk.Label(f1, text="Start Date:", bg="#1e1e1e", fg="#FFD700").grid(row=0, column=4, padx=5)
        self.ent_date = tk.Entry(f1, bg="#333", fg="#FFD700", width=12)
        self.ent_date.grid(row=0, column=5, padx=5)
        self.ent_date.insert(0, str(date.today()))
        
        tk.Label(f1, text="Days:", bg="#1e1e1e", fg="white").grid(row=0, column=6, padx=5)
        self.spin_days = tk.Spinbox(f1, from_=1, to=999, width=5)
        self.spin_days.grid(row=0, column=7, padx=5)
        
        self.lbl_calc = tk.Label(f1, text="(Auto)", bg="#1e1e1e", fg="gray")
        self.lbl_calc.grid(row=0, column=8, padx=5)

        # 2. FILES
        f2 = tk.LabelFrame(p, text=" 2. Files ", bg="#1e1e1e", fg="#00BFFF", font=("bold", 12))
        f2.pack(fill="x", pady=5, padx=10)
        
        tk.Button(f2, text="1. Main Images", command=self.sel_in, bg="#007acc", fg="white", width=20).grid(row=0, column=0, padx=5, pady=5)
        self.lbl_in = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray")
        self.lbl_in.grid(row=0, column=1, sticky="w")
        
        tk.Button(f2, text="2. Food Images (Opt)", command=self.sel_food, bg="#FF8C00", fg="white", width=20).grid(row=1, column=0, padx=5, pady=5)
        self.lbl_food = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray")
        self.lbl_food.grid(row=1, column=1, sticky="w")
        
        tk.Button(f2, text="3. Output Folder", command=self.sel_out, bg="#444", fg="white", width=20).grid(row=2, column=0, padx=5, pady=5)
        self.lbl_out = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray")
        self.lbl_out.grid(row=2, column=1, sticky="w")
        
        tk.Button(f2, text="4. Select Logo", command=self.sel_logo, bg="#444", fg="white", width=20).grid(row=3, column=0, padx=5, pady=5)
        self.lbl_logo = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray")
        self.lbl_logo.grid(row=3, column=1, sticky="w")
        
        tk.Label(f2, text="Pos:", bg="#1e1e1e", fg="white").grid(row=3, column=2, padx=5)
        self.cb_logo_pos = ttk.Combobox(f2, values=["Bottom-Right", "Bottom-Center"], state="readonly", width=12)
        self.cb_logo_pos.current(0)
        self.cb_logo_pos.grid(row=3, column=3, padx=5)

        # 3. PROCESS
        f3 = tk.LabelFrame(p, text=" 3. Process ", bg="#1e1e1e", fg="#00BFFF", font=("bold", 12))
        f3.pack(fill="x", pady=5, padx=10)
        
        self.chk_shuffle = tk.BooleanVar(value=True)
        tk.Checkbutton(f3, text="Shuffle Images", variable=self.chk_shuffle, bg="#1e1e1e", fg="#FFD700", selectcolor="#333").pack(anchor="w", padx=10)
        
        f_temp = tk.Frame(f3, bg="#1e1e1e")
        f_temp.pack(anchor="w", padx=5)
        self.chk_vars = {}
        
        row_c = 0
        col_c = 0
        # สร้าง Checkbox ตาม Template ใหม่ (T1-T4)
        for k in sorted(TEMPLATES.keys()):
            v = tk.BooleanVar(value=True)
            self.chk_vars[k] = v
            tk.Checkbutton(f_temp, text=TEMPLATES[k]['name'], variable=v, bg="#1e1e1e", fg="white", selectcolor="#333", command=self.update_calc).grid(row=row_c, column=col_c, sticky="w", padx=5)
            col_c += 1
            if col_c > 1: # จัดเรียง 2 คอลัมน์
                col_c = 0
                row_c += 1
            
        f_plat = tk.Frame(f3, bg="#1e1e1e")
        f_plat.pack(anchor="w", padx=5, pady=5)
        self.chk_fb = tk.BooleanVar(value=True)
        self.chk_ig = tk.BooleanVar(value=True)
        self.chk_tt = tk.BooleanVar(value=True)
        tk.Checkbutton(f_plat, text="| FB", variable=self.chk_fb, bg="#1e1e1e", fg="#00FF7F", selectcolor="#333").pack(side="left")
        tk.Checkbutton(f_plat, text="IG", variable=self.chk_ig, bg="#1e1e1e", fg="#00FF7F", selectcolor="#333").pack(side="left")
        tk.Checkbutton(f_plat, text="TT", variable=self.chk_tt, bg="#1e1e1e", fg="#00FF7F", selectcolor="#333").pack(side="left")

        # 4. ACTION
        f4 = tk.Frame(p, bg="#1e1e1e")
        f4.pack(fill="x", pady=10, padx=10)
        
        # START BUTTON
        self.btn_run = tk.Button(f4, text="🚀 START", command=self.start, bg="#00C853", fg="white", font=("bold", 14), height=2)
        self.btn_run.pack(side="left", fill="x", expand=True, padx=5)
        
        # STOP BUTTON
        self.btn_stop = tk.Button(f4, text="🛑 STOP", command=self.stop, bg="#D50000", fg="white", font=("bold", 14), height=2, state="disabled")
        self.btn_stop.pack(side="left", fill="x", padx=5)
        
        # PREVIEW BUTTON
        self.btn_prev = tk.Button(f4, text="🌐 PREVIEW", command=self.preview, bg="#007acc", fg="white", font=("bold", 12), height=2)
        self.btn_prev.pack(side="right", fill="x", expand=True, padx=5)

        # 5. USER TOOLS
        f5 = tk.Frame(p, bg="#1e1e1e")
        f5.pack(fill="x", padx=10)
        tk.Button(f5, text="Add User", command=self.add_u).pack(side="left")
        tk.Button(f5, text="Del User", command=self.del_u).pack(side="left", padx=5)
        
        if self.users:
            self.cb_user.current(0)
            self.on_user_select(None)

    def setup_logs_tab(self):
        self.log_box = scrolledtext.ScrolledText(self.tab_logs, bg="black", fg="#00ff00", font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log(">> System Ready... (V60 - 4 Templates)")

    def log(self, msg):
        self.log_box.insert(tk.END, f">> {msg}\n")
        self.log_box.see(tk.END)

    def update_calc(self):
        tot = len(self.files_main) + len(self.files_food)
        if tot == 0:
            self.lbl_calc.config(text="(No images)", fg="gray")
            return
        
        acts = [k for k in sorted(TEMPLATES.keys()) if self.chk_vars[k].get()]
        if not acts:
            self.lbl_calc.config(text="(Select Templ)", fg="red")
            return
        
        c = 0
        d = 0
        while True:
            t = acts[d % len(acts)]
            n = len(TEMPLATES[t]["specs"])
            if c + n <= tot:
                c += n
                d += 1
            else:
                break
        
        self.spin_days.delete(0, "end")
        self.spin_days.insert(0, d)
        self.lbl_calc.config(text=f"({tot} pics = {d} days)", fg="#00FF7F")

    def on_user_select(self, e):
        pass

    def add_u(self):
        u = simpledialog.askstring("Add", "User:")
        if u:
            self.users[u] = ""
            self.save_json(USERS_FILE, self.users)
            self.cb_user['values'] = list(self.users.keys())
            self.cb_user.set(u)

    def del_u(self):
        u = self.cb_user.get()
        if u in self.users:
            del self.users[u]
            self.save_json(USERS_FILE, self.users)
            self.cb_user['values'] = list(self.users.keys())
            self.cb_user.set('')

    def sel_in(self):
        d = filedialog.askdirectory()
        if d:
            self.input_dir = d
            self.files_main = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            self.lbl_in.config(text=f"{len(self.files_main)}", fg="#00FF7F")
            self.update_calc()

    def sel_food(self):
        d = filedialog.askdirectory()
        if d:
            self.food_dir = d
            self.files_food = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            self.lbl_food.config(text=f"{len(self.files_food)}", fg="#FF8C00")
            self.update_calc()

    def sel_out(self):
        d = filedialog.askdirectory()
        if d:
            self.output_dir = d
            self.lbl_out.config(text="OK", fg="green")

    def sel_logo(self):
        f = filedialog.askopenfilename()
        if f:
            self.logo_path = f
            self.lbl_logo.config(text="OK", fg="green")

    def process_logo(self, tw, th):
        if not self.logo_path:
            return None
        l = Image.open(self.logo_path)
        
        target_lw = int(tw * 0.18)
        ratio = target_lw / l.width
        target_lh = int(l.height * ratio)
        l = l.resize((target_lw, target_lh), Image.Resampling.LANCZOS)
        
        # --- FIXED MARGINS (LOW & TIGHT) ---
        margin_x = int(tw * 0.02)   # 2% from right
        margin_y = int(th * 0.005)  # 0.5% from bottom
        # -----------------------------------
        
        pos = self.cb_logo_pos.get()
        
        if pos == "Bottom-Center":
            x = (tw - target_lw) // 2
            y = th - target_lh - margin_y
        else: 
            x = tw - target_lw - margin_x
            y = th - target_lh - margin_y
            
        return l, x, y

    def smart_crop(self, pil_img, target_w, target_h):
        try:
            img_np = np.array(pil_img)
            if len(img_np.shape)==2:
                img_np=cv2.cvtColor(img_np,cv2.COLOR_GRAY2RGB)
            elif img_np.shape[2]==4:
                img_np=cv2.cvtColor(img_np,cv2.COLOR_RGBA2BGR)
            else:
                img_np=cv2.cvtColor(img_np,cv2.COLOR_RGB2BGR)
            
            gray = cv2.cvtColor(cv2.resize(img_np, (600, int(img_np.shape[0]*(600/img_np.shape[1])))), cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            cx, cy = 0.5, 0.5
            if len(faces) > 0:
                fx,fy,fw,fh = faces[0]
                cx = (fx + fw/2) / 600
                cy = (fy + fh/2) / gray.shape[0]
            
            return ImageOps.fit(pil_img, (target_w, target_h), Image.Resampling.LANCZOS, centering=(cx, cy))
        except:
            return ImageOps.fit(pil_img, (target_w, target_h), Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    def smart_sort_images(self, images_paths, specs):
        if len(images_paths) != len(specs):
            return images_paths
        
        slot_ratios = [(s[0]/s[1], i) for i, s in enumerate(specs)]
        img_objs = []
        
        for p in images_paths:
            try:
                with Image.open(p) as i:
                    img_objs.append((i.width/i.height, p))
            except:
                img_objs.append((1.0, p))
            
        slot_ratios.sort(key=lambda x: x[0])
        img_objs.sort(key=lambda x: x[0])
        
        final_order = [None] * len(specs)
        for i in range(len(specs)):
            target_idx = slot_ratios[i][1]
            final_order[target_idx] = img_objs[i][1]
            
        return final_order

    def generate_web(self, output_root, user, password, content_map, start_date_str):
        json_content = json.dumps(content_map)
        
        # HTML - FIX: Adjusted CSS Grids to match exact specs, removed white borders
        html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{user}</title><script src="https://cdn.tailwindcss.com"></script><link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet"><style>body{{background:#0f172a;color:white;font-family:sans-serif}}
        .page{{min-height:100vh; display:none;}} 
        .page.active{{display:block; animation:fadeIn 0.3s}}
        @keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
        
        /* --- FIXED: Removed white padding and background to kill borders --- */
        .grid-wrap {{ display: grid; gap: 2px; background: transparent; padding: 0; border-radius: 8px; overflow: hidden; margin: 0 auto; width: 100%; max-width: 500px; }}
        img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}

        /* --- UPDATED LAYOUTS WITH CORRECT RATIOS --- */
        
        /* T1: Square 4 (2x2) -> Ratio 1:1 */
        .layout-T1 {{ aspect-ratio: 1/1; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; }} 
        
        /* T2: Landscape 1 (3:2) + 2 Squares (1:1) */
        /* Logic: Top row (3:2) vs Bottom row (two 1:1 side by side). 
           Visual Weight -> Top height:Bottom height is approx 4:3 */
        .layout-T2 {{ aspect-ratio: 6/7; grid-template-columns: 1fr 1fr; grid-template-rows: 4fr 3fr; }} 
        .layout-T2 img:nth-child(1) {{ grid-column: 1 / 3; grid-row: 1; }} 
        .layout-T2 img:nth-child(2) {{ grid-column: 1; grid-row: 2; }} 
        .layout-T2 img:nth-child(3) {{ grid-column: 2; grid-row: 2; }}

        /* T3: Vertical 1 (2:3) + 2 Squares (1:1) */
        /* Logic: Right Col (two squares) is 2 units tall. Left Col is 2:3.
           To match heights, Width ratio is approx 4:3 (Left:Right) */
        .layout-T3 {{ aspect-ratio: 7/6; grid-template-columns: 4fr 3fr; grid-template-rows: 1fr 1fr; }} 
        .layout-T3 img:nth-child(1) {{ grid-column: 1; grid-row: 1 / 3; }} 
        .layout-T3 img:nth-child(2) {{ grid-column: 2; grid-row: 1; }} 
        .layout-T3 img:nth-child(3) {{ grid-column: 2; grid-row: 2; }}

        /* T4: 2 Squares Top + 3 Squares Bottom */
        /* Top Row: 2 items (50% w). Bottom Row: 3 items (33.3% w).
           Height ratio is approx 3:2 (Top Row Height : Bottom Row Height) */
        .layout-T4 {{ aspect-ratio: 6/5; grid-template-columns: repeat(6, 1fr); grid-template-rows: 3fr 2fr; }} 
        .layout-T4 img:nth-child(1) {{ grid-column: 1 / 4; grid-row: 1; }} 
        .layout-T4 img:nth-child(2) {{ grid-column: 4 / 7; grid-row: 1; }} 
        .layout-T4 img:nth-child(3) {{ grid-column: 1 / 3; grid-row: 2; }} 
        .layout-T4 img:nth-child(4) {{ grid-column: 3 / 5; grid-row: 2; }} 
        .layout-T4 img:nth-child(5) {{ grid-column: 5 / 7; grid-row: 2; }} 
        
        .layout-Single {{ display: block; }} .layout-Single img {{ width: 100%; height: auto; max-height: 500px; object-fit: contain; margin: 0 auto; }}
        
        /* Calendar Styles */
        .cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }}
        .cal-day {{ background: #1e293b; padding: 10px; border-radius: 4px; min-height: 80px; position: relative; cursor: pointer; border: 1px solid #334155; }}
        .cal-day.disabled {{ opacity: 0.3; cursor: default; }}
        .cal-day:hover:not(.disabled) {{ background: #334155; }}
        .cal-day.has-content {{ border: 1px solid #3b82f6; background: #1e3a8a; }}
        .cal-dot {{ width: 8px; height: 8px; background: #3b82f6; border-radius: 50%; margin-top: 5px; }}
        .pagination {{ display: flex; justify-content: center; gap: 10px; margin-top: 20px; }}
        .btn {{ padding: 10px 20px; background: #2563eb; color: white; border-radius: 5px; cursor: pointer; }}
        .btn:disabled {{ background: #475569; cursor: not-allowed; }}
        </style></head><body>
        
        <div id="p-dash" class="page active pb-20"><div class="sticky top-0 bg-slate-900 p-4 flex justify-between border-b border-slate-800"><span class="font-bold text-blue-400">{user}</span><button onclick="location.reload()"><i class="fas fa-sign-out-alt"></i></button></div>
        <div class="p-2 flex gap-2">
            <button onclick="appTab('fb')" id="b-fb" class="flex-1 p-2 rounded bg-blue-600">FB</button>
            <button onclick="appTab('ig')" id="b-ig" class="flex-1 p-2 rounded bg-slate-800">IG</button>
            <button onclick="appTab('tt')" id="b-tt" class="flex-1 p-2 rounded bg-slate-800">TT</button>
            <button onclick="appTab('cal')" id="b-cal" class="flex-1 p-2 rounded bg-yellow-600"><i class="fas fa-calendar-alt"></i></button>
        </div>
        <div id="feed" class="p-4 space-y-6"></div>
        <div id="pagination" class="pagination p-4">
            <button class="btn" onclick="changePage(-1)" id="btn-prev">Previous</button>
            <span id="page-num" class="py-2">Page 1</span>
            <button class="btn" onclick="changePage(1)" id="btn-next">Next</button>
        </div>
        <div id="cal-view" class="hidden p-4"></div>
        </div>
        
        <div id="p-det" class="page pb-20"><div class="sticky top-0 bg-slate-900 p-4 border-b border-slate-800 flex gap-4"><button onclick="appNav('p-dash')"><i class="fas fa-arrow-left"></i></button><b>Day <span id="d-day"></span></b></div><div id="d-img" class="p-4 space-y-4"></div></div>
        
        <script>
        const D={json_content}; const START_DATE="{start_date_str}"; 
        let C='fb'; let PAGE=1; const PER_PAGE=10; 
        let currentCalMonth = new Date(START_DATE);

        appRender();

        function appNav(id){{document.querySelectorAll('.page').forEach(e=>e.classList.remove('active'));document.getElementById(id).classList.add('active');window.scrollTo(0,0)}}
        
        function appTab(t){{
            C=t; PAGE=1; 
            ['fb','ig','tt','cal'].forEach(x=>document.getElementById('b-'+x).className=x==t?'flex-1 p-2 rounded bg-blue-600':'flex-1 p-2 rounded bg-slate-800');
            if(t=='cal') document.getElementById('b-cal').className='flex-1 p-2 rounded bg-yellow-600';
            
            if(t=='cal') {{
                document.getElementById('feed').classList.add('hidden');
                document.getElementById('pagination').classList.add('hidden');
                document.getElementById('cal-view').classList.remove('hidden');
                renderCalendar();
            }} else {{
                document.getElementById('feed').classList.remove('hidden');
                document.getElementById('pagination').classList.remove('hidden');
                document.getElementById('cal-view').classList.add('hidden');
                appRender();
            }}
        }}

        function changePage(d){{
            const list = D[C] || [];
            const totalPages = Math.ceil(list.length / PER_PAGE);
            let newPage = PAGE + d;
            if(newPage >= 1 && newPage <= totalPages){{
                PAGE = newPage;
                appRender();
                window.scrollTo(0,0);
            }}
        }}

        function appRender(){{
            const c=document.getElementById('feed'); c.innerHTML='';
            const list = D[C] || [];
            
            const start = (PAGE - 1) * PER_PAGE;
            const end = start + PER_PAGE;
            const items = list.slice(start, end);
            const totalPages = Math.ceil(list.length / PER_PAGE) || 1;

            items.forEach(d=>{{c.innerHTML+=renderItem(d, C)}});
            
            document.getElementById('page-num').innerText = `Page ${{PAGE}} / ${{totalPages}}`;
            document.getElementById('btn-prev').disabled = (PAGE === 1);
            document.getElementById('btn-next').disabled = (PAGE === totalPages);
        }} 
        
        function renderItem(d, platform){{
            let h=''; let k=d.template; let dateObj = new Date(START_DATE); dateObj.setDate(dateObj.getDate() + (d.day-1));
            let dateStr = dateObj.toLocaleDateString('th-TH');
            
            if(platform=='fb'){{
                // Simple mapping for T1-T4
                let tKey = 'Single';
                if(k.includes('T1')) tKey='T1';
                else if(k.includes('T2')) tKey='T2';
                else if(k.includes('T3')) tKey='T3';
                else if(k.includes('T4')) tKey='T4';
                
                h=`<div class="grid-wrap layout-${{tKey}}">${{d.images.map(s=>`<img src="${{s}}">`).join('')}}</div>`;
            }} else {{ 
                h=`<div class="flex overflow-x-auto gap-2">${{d.images.map(s=>`<img src="${{s}}" class="w-32 aspect-[4/5] rounded">`).join('')}}</div>` 
            }}
            
            return `<div onclick="appView(${{d.day}})" class="bg-slate-800 rounded-lg p-3 mb-4 cursor-pointer">
                <div class="flex justify-between mb-2 font-bold">Day ${{d.day}} (${{dateStr}}) <span class="text-blue-400 text-xs">View ></span></div>${{h}}</div>`;
        }}

        function changeCalMonth(d){{
            currentCalMonth.setMonth(currentCalMonth.getMonth() + d);
            renderCalendar();
        }}

        function renderCalendar() {{
            const c = document.getElementById('cal-view'); c.innerHTML = '';
            
            let year = currentCalMonth.getFullYear();
            let month = currentCalMonth.getMonth();
            
            let firstDay = new Date(year, month, 1);
            let lastDay = new Date(year, month + 1, 0);
            
            let monthLabel = firstDay.toLocaleDateString('th-TH', {{ month: 'long', year: 'numeric' }});
            
            let html = `
            <div class="flex justify-between items-center mb-4">
                <button class="btn py-1" onclick="changeCalMonth(-1)"><</button>
                <h3 class="text-xl font-bold">${{monthLabel}}</h3>
                <button class="btn py-1" onclick="changeCalMonth(1)">></button>
            </div>
            <div class="cal-grid">`;
            
            for(let i=0; i<firstDay.getDay(); i++) html += '<div></div>';
            
            for(let d=1; d<=lastDay.getDate(); d++){{
                let currDate = new Date(year, month, d);
                let startDateObj = new Date(START_DATE);
                let diffTime = currDate - startDateObj;
                let diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
                
                let content = (D['fb']||[]).find(x => x.day == diffDays);
                
                let cls = content ? 'cal-day has-content' : 'cal-day disabled';
                let dot = content ? '<div class="cal-dot"></div>' : '';
                let tmpl = content ? `<div class="text-xs text-gray-300 mt-1">${{content.template}}</div>` : '';
                let clickAction = content ? `appView(${{diffDays}})` : '';
                
                html += `<div class="${{cls}}" onclick="${{clickAction}}">
                    <div class="font-bold text-sm">${{d}}</div>
                    ${{dot}} ${{tmpl}}
                </div>`;
            }}
            html += '</div>';
            c.innerHTML = html;
        }}

        function appView(d){{
            const x=D[C=='cal'?'fb':C].find(i=>i.day==d);
            if(!x) return;
            document.getElementById('d-day').innerText=d;
            const c=document.getElementById('d-img'); c.innerHTML='';
            x.images.forEach(s=>c.innerHTML+=`<img src="${{s}}" class="rounded-lg shadow"><a href="${{s}}" download class="block text-center bg-slate-800 p-2 rounded text-sm mt-1 mb-4">Download</a>`);
            appNav('p-det');
        }}
        </script></body></html>"""
        
        with open(os.path.join(output_root, "index.html"), "w", encoding='utf-8') as f:
            f.write(html)

    def start_server_thread(self, root_dir):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        os.chdir(root_dir)
        handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = True
        try:
            self.httpd = socketserver.TCPServer(("", self.server_port), handler)
            self.httpd.serve_forever()
        except:
            self.server_port += 1
            self.start_server_thread(root_dir)

    def preview(self):
        target_path = self.deploy_path
        if not target_path and self.output_dir:
            target_path = os.path.join(self.output_dir, "Cloudflare_Deploy")
        
        if not target_path or not os.path.exists(target_path):
            messagebox.showinfo("Locate", "Deploy folder not found.\nPlease select 'Cloudflare_Deploy' folder manually.")
            target_path = filedialog.askdirectory(title="Select Cloudflare_Deploy Folder")

        if target_path and os.path.exists(target_path):
            t = threading.Thread(target=self.start_server_thread, args=(target_path,), daemon=True)
            t.start()
            time.sleep(1)
            url = f"http://127.0.0.1:{self.server_port}"
            webbrowser.open(url)
            messagebox.showinfo("Server Running", f"Opened: {url}\n\nIf browser didn't open, copy this URL.")
        else:
            messagebox.showerror("Error", "No folder selected.")

    def start(self):
        threading.Thread(target=self.run).start()

    def stop(self):
        self.running = False
        self.btn_stop.config(state="disabled")
        self.log(">> 🛑 STOPPING... Please wait for current process.")

    def run(self):
        self.running = True
        u = self.cb_user.get()
        start_date = self.ent_date.get()
        
        if not u or not self.output_dir or not self.files_main:
            messagebox.showerror("Err", "Missing Info")
            self.running = False
            return
        
        self.btn_run.config(state="disabled")
        self.btn_prev.config(state="disabled")
        self.btn_stop.config(state="normal") # Enable STOP
        
        proj = self.ent_proj.get()
        days = int(self.spin_days.get())
        
        self.deploy_path = os.path.join(self.output_dir, "Cloudflare_Deploy")
        aroot = os.path.join(self.deploy_path, "assets", u, proj)
        if os.path.exists(self.deploy_path):
            shutil.rmtree(self.deploy_path)
        os.makedirs(aroot, exist_ok=True)
        
        if self.chk_shuffle.get():
            random.shuffle(self.files_main)
            if self.files_food:
                random.shuffle(self.files_food)
        
        # Plan Days
        d_types = []
        streak = 0
        f_idx = 0
        for _ in range(days):
            is_food = False
            if self.files_food and f_idx < len(self.files_food) and streak < 3:
                if random.random() < 0.3:
                    is_food = True
            
            if is_food:
                d_types.append('F')
                streak += 1
                f_idx += 1
            else:
                d_types.append('M')
                streak = 0
            
        acts = [k for k in sorted(TEMPLATES.keys()) if self.chk_vars[k].get()]
        if not acts:
            self.btn_run.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.running = False
            return
        
        m_idx = 0
        f_ptr = 0
        content = {p: [] for p in ['fb', 'ig', 'tt']}
        
        try:
            for i, dt in enumerate(d_types):
                # STOP CHECK
                if not self.running:
                    self.log(">> STOPPED by User.")
                    break

                day = i + 1
                t = acts[i % len(acts)]
                specs = TEMPLATES[t]["specs"]
                n = len(specs)
                src = []
                
                if dt == 'F' and f_ptr + n <= len(self.files_food):
                    for _ in range(n):
                        src.append(self.files_food[f_ptr])
                        f_ptr += 1
                    self.log(f"Day {day}: Food ({t})")
                else:
                    for _ in range(n): 
                        if m_idx >= len(self.files_main):
                            m_idx = 0
                        src.append(self.files_main[m_idx])
                        m_idx += 1
                    self.log(f"Day {day}: Main ({t})")
                
                sorted_src = self.smart_sort_images(src, specs)
                
                for p in ['fb', 'ig', 'tt']:
                    dpath = os.path.join(aroot, p, f"Day_{day:02d}")
                    os.makedirs(dpath, exist_ok=True)
                    wpaths = []
                    
                    for idx, path in enumerate(sorted_src):
                        with Image.open(path) as img:
                            w, h = (1080, 1920) if p == 'tt' else (1080, 1350) if p == 'ig' else specs[idx]
                            
                            fin = self.smart_crop(img, w, h)
                            if self.logo_path:
                                lr, lx, ly = self.process_logo(w, h)
                                fin.paste(lr, (lx, ly), lr)
                            
                            # PNG format
                            fn = f"{idx+1}.png"
                            fin.save(os.path.join(dpath, fn)) 
                            wpaths.append(f"assets/{u}/{proj}/{p}/Day_{day:02d}/{fn}")
                            
                    content[p].append({"day": day, "template": t, "images": wpaths})
            
            # PASS START DATE TO HTML GENERATOR
            self.generate_web(self.deploy_path, u, "", content, start_date)
            
            shutil.make_archive(os.path.join(self.output_dir, "Upload_Cloudflare"), 'zip', self.deploy_path)
            
            self.btn_prev.config(state="normal")
            if self.running:
                self.log("DONE!")
                self.root.bell()
                messagebox.showinfo("OK", "Finished! Check ZIP.")
            
        except Exception as e:
            messagebox.showerror("Err", str(e))
            self.log(f"Err: {e}")
            
        self.btn_run.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoGridV59(root)
    root.mainloop()