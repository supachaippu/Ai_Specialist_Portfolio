import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
from PIL import Image, ImageOps
import numpy as np
import os
import shutil
import threading
import json
import random
import http.server
import socketserver
import webbrowser
import time
from datetime import date, timedelta, datetime

# --- CONFIGURATIONS ---
PROJECT_DEFAULT = "Content"
CONFIG_FILE = "cms_config.json"
USERS_FILE = "cms_users_v2.json"

# --- TEMPLATES SPECS (SYNCHRONIZED WITH CSS GRID) ---
# ทุก Template ถูกคำนวณให้เข้ากับ CSS Grid แบบ Pixel-Perfect
TEMPLATES = {
    # T2: Album 5 (2 บน + 3 ล่าง) -> ทั้งหมดเป็นจัตุรัส เพื่อความสวยงามและเต็มกรอบง่าย
    "T2": { 
        "name": "1. Album 5 (Standard 5 Squares)", 
        "specs": [
            (1200, 1200), (1200, 1200),             # บน 2 (1:1)
            (1200, 1200), (1200, 1200), (1200, 1200) # ล่าง 3 (1:1)
        ] 
    },
    # T3: Album 4 (2x2) -> จัตุรัสล้วน
    "T3": { 
        "name": "2. Album 4 (4 Squares)", 
        "specs": [
            (1200, 1200), (1200, 1200), 
            (1200, 1200), (1200, 1200)
        ] 
    },
    # T4: Mix 5 (บน 2 จัตุรัส + ล่าง 3 แนวตั้ง 2:3)
    "T4": { 
        "name": "3. Mix 5 (2 Sq + 3 Portrait)", 
        "specs": [
            (1200, 1200), (1200, 1200),            # บน 2 (1:1)
            (800, 1200), (800, 1200), (800, 1200)  # ล่าง 3 (2:3) 
        ] 
    }
}

class AutoGridV80:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGrid V80 (Synced Layouts + Source Crop)")
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
            json.dump(data, f, indent=4, ensure_ascii=False)

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
        f1 = tk.LabelFrame(p, text=" 1. Client Info ", bg="#1e1e1e", fg="#00BFFF", font=("bold", 12))
        f1.pack(fill="x", pady=5, padx=10)
        
        tk.Label(f1, text="User:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5)
        self.cb_user = ttk.Combobox(f1, values=list(self.users.keys()), width=20, state="readonly")
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
        self.lbl_in = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray", width=40, anchor="w")
        self.lbl_in.grid(row=0, column=1, sticky="w")
        
        tk.Button(f2, text="2. Food Images (Opt)", command=self.sel_food, bg="#FF8C00", fg="white", width=20).grid(row=1, column=0, padx=5, pady=5)
        self.lbl_food = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray", width=40, anchor="w")
        self.lbl_food.grid(row=1, column=1, sticky="w")
        
        tk.Button(f2, text="3. Output Folder", command=self.sel_out, bg="#444", fg="white", width=20).grid(row=2, column=0, padx=5, pady=5)
        self.lbl_out = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray", width=40, anchor="w")
        self.lbl_out.grid(row=2, column=1, sticky="w")
        
        tk.Button(f2, text="4. Select Logo", command=self.sel_logo, bg="#444", fg="white", width=20).grid(row=3, column=0, padx=5, pady=5)
        self.lbl_logo = tk.Label(f2, text="-", bg="#1e1e1e", fg="gray", width=40, anchor="w")
        self.lbl_logo.grid(row=3, column=1, sticky="w")
        
        tk.Label(f2, text="Pos:", bg="#1e1e1e", fg="white").grid(row=3, column=2, padx=5)
        self.cb_logo_pos = ttk.Combobox(f2, values=["Bottom-Right", "Bottom-Center"], state="readonly", width=12)
        self.cb_logo_pos.current(0)
        self.cb_logo_pos.grid(row=3, column=3, padx=5)

        # 3. PROCESS
        f3 = tk.LabelFrame(p, text=" 3. Process ", bg="#1e1e1e", fg="#00BFFF", font=("bold", 12))
        f3.pack(fill="x", pady=5, padx=10)
        
        self.chk_reuse = tk.BooleanVar(value=True)
        tk.Checkbutton(f3, text="♻️ Reuse Images x2 (ใช้ซ้ำได้ 1 รอบ)", variable=self.chk_reuse, bg="#1e1e1e", fg="#00FF7F", selectcolor="#333", font=("bold", 10)).pack(anchor="w", padx=10)
        
        self.chk_shuffle = tk.BooleanVar(value=True)
        tk.Checkbutton(f3, text="🔀 Random Shuffle (กระจายรูป)", variable=self.chk_shuffle, bg="#1e1e1e", fg="#FFD700", selectcolor="#333").pack(anchor="w", padx=10)
        
        f_temp = tk.Frame(f3, bg="#1e1e1e")
        f_temp.pack(anchor="w", padx=5)
        self.chk_vars = {}
        
        row_c = 0
        col_c = 0
        for k in sorted(TEMPLATES.keys()):
            v = tk.BooleanVar(value=True)
            self.chk_vars[k] = v
            tk.Checkbutton(f_temp, text=TEMPLATES[k]["name"], variable=v, bg="#1e1e1e", fg="white", selectcolor="#333", command=self.update_calc).grid(row=row_c, column=col_c, sticky="w", padx=5)
            col_c += 1
            if col_c > 1:
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
        
        self.btn_run = tk.Button(f4, text="🚀 START", command=self.start, bg="#00C853", fg="white", font=("bold", 14), height=2)
        self.btn_run.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_stop = tk.Button(f4, text="🛑 STOP", command=self.stop, bg="#D50000", fg="white", font=("bold", 14), height=2, state="disabled")
        self.btn_stop.pack(side="left", fill="x", padx=5)
        
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
        self.log(">> System Ready... (V80: Synced Ratios + Clean T1)")

    def log(self, msg):
        self.log_box.insert(tk.END, f">> {msg}\n")
        self.log_box.see(tk.END)

    def on_user_select(self, e):
        u = self.cb_user.get()
        if u in self.users:
            data = self.users[u]
            if isinstance(data, dict):
                self.input_dir = data.get("input_dir", "")
                self.food_dir = data.get("food_dir", "")
                self.output_dir = data.get("output_dir", "")
                self.logo_path = data.get("logo_path", "")
                self.update_labels()
            else:
                self.users[u] = {}
                self.save_json(USERS_FILE, self.users)
                self.update_labels()

    def update_user_data(self):
        u = self.cb_user.get()
        if u:
            self.users[u] = {
                "input_dir": self.input_dir,
                "food_dir": self.food_dir,
                "output_dir": self.output_dir,
                "logo_path": self.logo_path
            }
            self.save_json(USERS_FILE, self.users)

    def update_labels(self):
        self.lbl_in.config(text=self.input_dir if self.input_dir else "No Folder", fg="#00FF7F" if self.input_dir else "gray")
        self.lbl_food.config(text=self.food_dir if self.food_dir else "No Folder", fg="#FF8C00" if self.food_dir else "gray")
        self.lbl_out.config(text=self.output_dir if self.output_dir else "No Folder", fg="green" if self.output_dir else "gray")
        self.lbl_logo.config(text=os.path.basename(self.logo_path) if self.logo_path else "No File", fg="green" if self.logo_path else "gray")
        
        if self.input_dir and os.path.exists(self.input_dir):
            self.files_main = [os.path.join(self.input_dir, f) for f in os.listdir(self.input_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if self.food_dir and os.path.exists(self.food_dir):
            self.files_food = [os.path.join(self.food_dir, f) for f in os.listdir(self.food_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        self.update_calc()

    def add_u(self):
        u = simpledialog.askstring("Add", "User (Store Name):")
        if u:
            self.users[u] = {}
            self.save_json(USERS_FILE, self.users)
            self.cb_user['values'] = list(self.users.keys())
            self.cb_user.set(u)
            self.on_user_select(None)

    def del_u(self):
        u = self.cb_user.get()
        if u in self.users:
            del self.users[u]
            self.save_json(USERS_FILE, self.users)
            self.cb_user['values'] = list(self.users.keys())
            self.cb_user.set('')
            self.update_labels()

    def sel_in(self):
        d = filedialog.askdirectory()
        if d:
            self.input_dir = d
            self.update_user_data()
            self.update_labels()

    def sel_food(self):
        d = filedialog.askdirectory()
        if d:
            self.food_dir = d
            self.update_user_data()
            self.update_labels()

    def sel_out(self):
        d = filedialog.askdirectory()
        if d:
            self.output_dir = d
            self.update_user_data()
            self.update_labels()

    def sel_logo(self):
        f = filedialog.askopenfilename()
        if f:
            self.logo_path = f
            self.update_user_data()
            self.update_labels()

    def update_calc(self):
        tot = len(self.files_main) + len(self.files_food)
        if self.chk_reuse.get(): tot *= 2
            
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

    def process_logo(self, tw, th):
        if not self.logo_path: return None
        l = Image.open(self.logo_path).convert("RGBA")
        bbox = l.getbbox()
        if bbox: l = l.crop(bbox)

        target_lw = int(tw * 0.18)
        if target_lw <= 0: target_lw = 1
        ratio = target_lw / l.width
        target_lh = int(l.height * ratio)
        l = l.resize((target_lw, target_lh), Image.Resampling.LANCZOS)
        
        margin_x = int(tw * 0.05) 
        margin_y = int(th * 0.05)
        
        pos = self.cb_logo_pos.get()
        if pos == "Bottom-Center":
            x = (tw - target_lw) // 2
            y = th - target_lh - margin_y
        else: 
            x = tw - target_lw - margin_x
            y = th - target_lh - margin_y
        return l, x, y

    # --- SOURCE-BASED CROP (LOGIC CORRECTED) ---
    def crop_from_source(self, pil_img, target_w, target_h):
        pil_img = ImageOps.exif_transpose(pil_img)
        
        src_w, src_h = pil_img.size
        target_ratio = target_w / target_h
        src_ratio = src_w / src_h
        
        if src_ratio > target_ratio:
            # Source Wider -> Cut Width
            crop_h = src_h
            crop_w = int(src_h * target_ratio)
            left = (src_w - crop_w) // 2
            top = 0
        else:
            # Source Taller -> Cut Height
            crop_w = src_w
            crop_h = int(src_w / target_ratio)
            left = 0
            # Center-Top Bias (20% from top)
            center_y = (src_h - crop_h) // 2
            shift = int((src_h - crop_h) * 0.2)
            top = center_y - shift
            if top < 0: top = 0
            
        right = left + crop_w
        bottom = top + crop_h
        
        cropped_img = pil_img.crop((left, top, right, bottom))
        return cropped_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    def smart_sort_images(self, images_paths, specs):
        if len(images_paths) != len(specs): return images_paths
        slot_ratios = [(s[0]/s[1], i) for i, s in enumerate(specs)]
        img_objs = []
        for p in images_paths:
            try:
                with Image.open(p) as i: img_objs.append((i.width/i.height, p))
            except: img_objs.append((1.0, p))
        slot_ratios.sort(key=lambda x: x[0])
        img_objs.sort(key=lambda x: x[0])
        final_order = [None] * len(specs)
        for i in range(len(specs)):
            target_idx = slot_ratios[i][1]
            final_order[target_idx] = img_objs[i][1]
        return final_order

    def start(self):
        threading.Thread(target=self.run).start()

    def stop(self):
        self.running = False
        self.btn_stop.config(state="disabled")
        self.log(">> 🛑 STOPPING...")

    def run(self):
        self.running = True
        u = self.cb_user.get()
        start_date = self.ent_date.get()
        
        if not u or not self.input_dir or not self.output_dir:
            messagebox.showerror("Err", "Please ensure User, Input Folder, and Output Folder are selected.")
            self.running = False
            return
        
        self.btn_run.config(state="disabled")
        self.btn_prev.config(state="disabled")
        self.btn_stop.config(state="normal") 
        
        month_name = datetime.now().strftime("%B")
        proj_base = self.ent_proj.get()
        proj = f"{month_name}_{proj_base}"
        
        days = int(self.spin_days.get())
        
        self.deploy_path = os.path.join(self.output_dir, "Cloudflare_Deploy")
        aroot = os.path.join(self.deploy_path, "assets", u, proj)
        if os.path.exists(self.deploy_path): shutil.rmtree(self.deploy_path)
        os.makedirs(aroot, exist_ok=True)
        
        pool_main = list(self.files_main)
        pool_food = list(self.files_food)
        
        if self.chk_reuse.get():
            pool_main = pool_main * 2
            pool_food = pool_food * 2
            self.log(f">> Reuse x2 Active: Main={len(pool_main)}, Food={len(pool_food)}")
        
        if self.chk_shuffle.get():
            random.shuffle(pool_main)
            if pool_food: random.shuffle(pool_food)
        
        d_types = []
        streak = 0
        f_idx = 0
        for _ in range(days):
            is_food = False
            if pool_food and f_idx < len(pool_food) and streak < 3:
                if random.random() < 0.3: is_food = True
            if is_food:
                d_types.append('F')
                streak += 1; f_idx += 1
            else:
                d_types.append('M')
                streak = 0
            
        acts = [k for k in sorted(TEMPLATES.keys()) if self.chk_vars[k].get()]
        if not acts: return
        
        active_platforms = []
        if self.chk_fb.get(): active_platforms.append('fb')
        if self.chk_ig.get(): active_platforms.append('ig')
        if self.chk_tt.get(): active_platforms.append('tt')
        if not active_platforms:
             messagebox.showerror("Err", "Select Platform")
             self.running = False; return

        m_idx = 0
        f_ptr = 0
        content = {p: [] for p in ['fb', 'ig', 'tt']}
        
        try:
            for i, dt in enumerate(d_types):
                if not self.running: break
                day = i + 1
                t = acts[i % len(acts)]
                specs = TEMPLATES[t]["specs"]
                n = len(specs)
                src = []
                
                if dt == 'F' and f_ptr + n <= len(pool_food):
                    for _ in range(n): src.append(pool_food[f_ptr]); f_ptr += 1
                    self.log(f"Day {day}: Food ({t})")
                else:
                    for _ in range(n): 
                        if m_idx >= len(pool_main): m_idx = 0
                        src.append(pool_main[m_idx]); m_idx += 1
                    self.log(f"Day {day}: Main ({t})")
                
                sorted_src = self.smart_sort_images(src, specs)
                
                for p in active_platforms:
                    dpath = os.path.join(aroot, p, f"Day_{day:02d}")
                    os.makedirs(dpath, exist_ok=True)
                    wpaths = []
                    for idx, path in enumerate(sorted_src):
                        with Image.open(path) as img:
                            w, h = (1080, 1920) if p == 'tt' else (1080, 1350) if p == 'ig' else specs[idx]
                            
                            # --- USE NEW LOGIC: CROP FROM SOURCE ---
                            fin = self.crop_from_source(img, w, h)
                            
                            if self.logo_path:
                                lr, lx, ly = self.process_logo(w, h)
                                if lr: fin.paste(lr, (lx, ly), lr)
                            fn = f"{idx+1}.png"
                            fin.save(os.path.join(dpath, fn))
                            wpaths.append(f"assets/{u}/{proj}/{p}/Day_{day:02d}/{fn}")
                    content[p].append({"day": day, "template": t, "images": wpaths})
            
            self.generate_web(self.deploy_path, u, "", content, start_date)
            shutil.make_archive(os.path.join(self.output_dir, f"{proj}_Upload"), 'zip', self.deploy_path)
            
            self.btn_prev.config(state="normal")
            if self.running:
                self.log("DONE!")
                self.root.bell()
                messagebox.showinfo("OK", f"Finished!\nFolder: {proj}")
            
        except Exception as e:
            messagebox.showerror("Err", str(e))
            self.log(f"Err: {e}")
            print(e)
            
        self.btn_run.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.running = False

    def generate_web(self, output_root, user, password, content_map, start_date_str):
        json_content = json.dumps(content_map)
        html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{user}</title><script src="https://cdn.tailwindcss.com"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script><link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet"><style>body{{background:#0f172a;color:white;font-family:sans-serif}}
        .page{{min-height:100vh; display:none;}} .page.active{{display:block; animation:fadeIn 0.3s}} @keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
        
        .feed-container {{ display: flex; flex-direction: column; gap: 20px; padding: 20px; max-width: 1400px; margin: 0 auto; }}
        @media (min-width: 1024px) {{ .feed-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; align-items: start; }} }}
        .feed-item {{ background: #1e293b; border-radius: 12px; padding: 10px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        
        /* Grid gap 2px for white separator */
        .grid-wrap {{ display: flex; flex-direction: column; gap: 2px; background: white; padding: 0; border: 2px solid white; border-radius: 8px; overflow: hidden; margin: 0 auto; }}
        .grid-wrap img {{ width: 100%; height: 100%; display: block; object-fit: cover; }}
        
        /* Force CSS Grid */
        .grid-wrap {{ display: grid; gap: 2px; background: white; }}
        
        /* SYNCED CSS RATIOS with Python */
        
        /* T2: 6/5 Ratio (2 Squares Top, 3 Squares Bottom) */
        .layout-T2 {{ aspect-ratio: 6/5; grid-template-columns: repeat(6, 1fr); grid-template-rows: 1fr 1fr; }}
        .layout-T2 img:nth-child(1) {{ grid-column: 1 / 4; grid-row: 1; }} 
        .layout-T2 img:nth-child(2) {{ grid-column: 4 / 7; grid-row: 1; }} 
        .layout-T2 img:nth-child(3) {{ grid-column: 1 / 3; grid-row: 2; }} 
        .layout-T2 img:nth-child(4) {{ grid-column: 3 / 5; grid-row: 2; }} 
        .layout-T2 img:nth-child(5) {{ grid-column: 5 / 7; grid-row: 2; }}

        /* T3: 1/1 Ratio (4 Squares) */
        .layout-T3 {{ aspect-ratio: 1/1; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; }}
        
        /* T4: 1/1 Ratio (2 Squares Top, 3 Portait Bottom) */
        .layout-T4 {{ aspect-ratio: 1/1; grid-template-columns: repeat(6, 1fr); grid-template-rows: 1fr 1fr; }}
        .layout-T4 img:nth-child(1) {{ grid-column: 1 / 4; grid-row: 1; }}
        .layout-T4 img:nth-child(2) {{ grid-column: 4 / 7; grid-row: 1; }}
        .layout-T4 img:nth-child(3) {{ grid-column: 1 / 3; grid-row: 2; }}
        .layout-T4 img:nth-child(4) {{ grid-column: 3 / 5; grid-row: 2; }}
        .layout-T4 img:nth-child(5) {{ grid-column: 5 / 7; grid-row: 2; }}

        .dl-all-btn {{ width: 100%; background: #059669; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; cursor: pointer; transition: 0.2s; display: none; }}
        @media (min-width: 768px) {{ .dl-all-btn {{ display: block; }} }}
        .toggle-btn {{ background: #334155; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; border: 1px solid #475569; }}
        .toggle-btn.active {{ background: #2563eb; border-color: #3b82f6; color: white; }}
        
        body.view-mobile .feed-container {{ display: flex; flex-direction: column; }}
        body.view-pc .feed-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
        </style></head><body>
        
        <div id="p-dash" class="page active pb-20">
            <div class="sticky top-0 bg-slate-900 p-4 flex justify-between border-b border-slate-800 items-center z-10">
                <div><span class="font-bold text-blue-400 block">{user}</span></div>
                <div class="flex gap-2">
                    <button onclick="setView('mobile')" id="btn-mobile" class="toggle-btn"><i class="fas fa-mobile-alt"></i> Mobile</button>
                    <button onclick="setView('pc')" id="btn-pc" class="toggle-btn"><i class="fas fa-desktop"></i> PC</button>
                    <button onclick="location.reload()" class="text-slate-400 px-2"><i class="fas fa-sign-out-alt"></i></button>
                </div>
            </div>
            <div class="p-2 flex gap-2"><button onclick="appTab('fb')" id="b-fb" class="flex-1 p-2 rounded bg-blue-600">FB</button><button onclick="appTab('ig')" id="b-ig" class="flex-1 p-2 rounded bg-slate-800">IG</button><button onclick="appTab('tt')" id="b-tt" class="flex-1 p-2 rounded bg-slate-800">TT</button><button onclick="appTab('cal')" id="b-cal" class="flex-1 p-2 rounded bg-yellow-600"><i class="fas fa-calendar-alt"></i></button></div>
            <div id="feed" class="feed-container"></div>
            <div id="pagination" class="pagination flex justify-center gap-4 p-4"><button class="px-4 py-2 bg-blue-600 rounded disabled:opacity-50" onclick="changePage(-1)" id="btn-prev">Prev</button><span id="page-num" class="py-2">Page 1</span><button class="px-4 py-2 bg-blue-600 rounded disabled:opacity-50" onclick="changePage(1)" id="btn-next">Next</button></div>
            <div id="cal-view" class="hidden p-4"></div>
        </div>
        <div id="p-det" class="page pb-20"><div class="sticky top-0 bg-slate-900 p-4 border-b border-slate-800 flex gap-4"><button onclick="appNav('p-dash')"><i class="fas fa-arrow-left"></i></button><b>Day <span id="d-day"></span></b></div><div class="p-4"><button onclick="downloadAll()" class="dl-all-btn"><i class="fas fa-file-archive"></i> Download ZIP (PC)</button><div id="d-img" class="space-y-4"></div></div></div>
        <script>
        const D={json_content}; const START_DATE="{start_date_str}"; let C='fb'; let PAGE=1; const PER_PAGE=12; let currentCalMonth = new Date(START_DATE); let currentDetailImages = [];
        function setView(mode) {{ document.body.classList.remove('view-pc', 'view-mobile'); document.getElementById('btn-pc').classList.remove('active'); document.getElementById('btn-mobile').classList.remove('active'); if(mode === 'pc') {{ document.body.classList.add('view-pc'); document.getElementById('btn-pc').classList.add('active'); }} else {{ document.body.classList.add('view-mobile'); document.getElementById('btn-mobile').classList.add('active'); }} }}
        if(window.innerWidth >= 1024) setView('pc'); else setView('mobile');
        appNav('p-dash');
        function appNav(id){{document.querySelectorAll('.page').forEach(e=>e.classList.remove('active'));document.getElementById(id).classList.add('active');window.scrollTo(0,0)}}
        function appTab(t){{ C=t; PAGE=1; ['fb','ig','tt','cal'].forEach(x=>document.getElementById('b-'+x).className=x==t?'flex-1 p-2 rounded bg-blue-600':'flex-1 p-2 rounded bg-slate-800'); if(t=='cal') document.getElementById('b-cal').className='flex-1 p-2 rounded bg-yellow-600'; if(t=='cal') {{ document.getElementById('feed').classList.add('hidden'); document.getElementById('pagination').classList.add('hidden'); document.getElementById('cal-view').classList.remove('hidden'); renderCalendar(); }} else {{ document.getElementById('feed').classList.remove('hidden'); document.getElementById('pagination').classList.remove('hidden'); document.getElementById('cal-view').classList.add('hidden'); appRender(); }} }}
        function changePage(d){{ const list = D[C] || []; const totalPages = Math.ceil(list.length / PER_PAGE); let newPage = PAGE + d; if(newPage >= 1 && newPage <= totalPages){{ PAGE = newPage; appRender(); window.scrollTo(0,0); }} }}
        function appRender(){{ const c=document.getElementById('feed'); c.innerHTML=''; const list = D[C] || []; if(!list || list.length === 0) {{ c.innerHTML = '<div class="text-gray-500 text-center mt-10 w-full col-span-3">No content for this platform</div>'; document.getElementById('page-num').innerText = `0/0`; return; }} const start = (PAGE - 1) * PER_PAGE; const end = start + PER_PAGE; const items = list.slice(start, end); const totalPages = Math.ceil(list.length / PER_PAGE) || 1; items.forEach(d=>{{c.innerHTML+=renderItem(d, C)}}); document.getElementById('page-num').innerText = `Page ${{PAGE}} / ${{totalPages}}`; document.getElementById('btn-prev').disabled = (PAGE === 1); document.getElementById('btn-next').disabled = (PAGE === totalPages); }} 
        function renderItem(d, platform){{ let h=''; let k=d.template; let dateObj = new Date(START_DATE); dateObj.setDate(dateObj.getDate() + (d.day-1)); let dateStr = dateObj.toLocaleDateString('th-TH'); if(platform=='fb'){{ let tKey = 'Single'; if(k.includes('T2')) tKey='T2'; else if(k.includes('T3')) tKey='T3'; else if(k.includes('T4')) tKey='T4'; h=`<div class="grid-wrap layout-${{tKey}}">${{d.images.map(s=>`<img src="${{s}}">`).join('')}}</div>`; }} else {{ h=`<div class="flex overflow-x-auto gap-2">${{d.images.map(s=>`<img src="${{s}}" class="w-32 aspect-[4/5] rounded">`).join('')}}</div>` }} return `<div onclick="appView(${{d.day}})" class="feed-item cursor-pointer hover:bg-slate-700 transition"><div class="flex justify-between mb-2 font-bold text-sm text-gray-300">Day ${{d.day}} (${{dateStr}})</div>${{h}}</div>`; }}
        function changeCalMonth(d){{ currentCalMonth.setMonth(currentCalMonth.getMonth() + d); renderCalendar(); }}
        function renderCalendar() {{ const c = document.getElementById('cal-view'); c.innerHTML = ''; let year = currentCalMonth.getFullYear(); let month = currentCalMonth.getMonth(); let firstDay = new Date(year, month, 1); let lastDay = new Date(year, month + 1, 0); let monthLabel = firstDay.toLocaleDateString('th-TH', {{ month: 'long', year: 'numeric' }}); let html = `<div class="flex justify-between items-center mb-4"><button class="px-3 py-1 bg-blue-600 rounded" onclick="changeCalMonth(-1)"><</button><h3 class="text-xl font-bold">${{monthLabel}}</h3><button class="px-3 py-1 bg-blue-600 rounded" onclick="changeCalMonth(1)">></button></div><div class="cal-grid">`; for(let i=0; i<firstDay.getDay(); i++) html += '<div></div>'; for(let d=1; d<=lastDay.getDate(); d++){{ let currDate = new Date(year, month, d); let startDateObj = new Date(START_DATE); let diffTime = currDate - startDateObj; let diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; let content = (D['fb']||[]).find(x => x.day == diffDays); let cls = content ? 'cal-day has-content' : 'cal-day disabled'; let dot = content ? '<div class="cal-dot"></div>' : ''; let clickAction = content ? `appView(${{diffDays}})` : ''; html += `<div class="${{cls}}" onclick="${{clickAction}}"><div class="font-bold">${{d}}</div>${{dot}}</div>`; }} html += '</div>'; c.innerHTML = html; }}
        function appView(d){{ const x=D[C=='cal'?'fb':C].find(i=>i.day==d); if(!x) return; document.getElementById('d-day').innerText=d; currentDetailImages = x.images; const c=document.getElementById('d-img'); c.innerHTML=''; x.images.forEach(s=>{{ let fname = s.split('/').pop(); c.innerHTML+=`<div><img src="${{s}}" class="rounded-lg shadow"><a href="${{s}}" download="${{fname}}" class="dl-btn"><i class="fas fa-arrow-down"></i> Download Original</a></div>`; }}); appNav('p-det'); }}
        
        async function downloadAll() {{
            if(!currentDetailImages || currentDetailImages.length === 0) return;
            const btn = document.querySelector('.dl-all-btn'); const oldTxt = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Zipping...'; btn.disabled = true;
            try {{
                const zip = new JSZip();
                const dayLabel = 'Day_' + document.getElementById('d-day').innerText;
                const folder = zip.folder(dayLabel);
                const promises = currentDetailImages.map(async (url, i) => {{ const res = await fetch(url); const blob = await res.blob(); folder.file(url.split('/').pop(), blob); }});
                await Promise.all(promises);
                const content = await zip.generateAsync({{type:"blob"}});
                saveAs(content, dayLabel + '.zip');
            }} catch(e) {{ alert('Error: ' + e.message); }} finally {{ btn.innerHTML = oldTxt; btn.disabled = false; }}
        }}
        </script></body></html>"""
        with open(os.path.join(output_root, "index.html"), "w", encoding='utf-8') as f: f.write(html)

    def start_server_thread(self, root_dir):
        if self.httpd: self.httpd.shutdown(); self.httpd.server_close()
        os.chdir(root_dir)
        handler = http.server.SimpleHTTPRequestHandler; socketserver.TCPServer.allow_reuse_address = True
        try: self.httpd = socketserver.TCPServer(("", self.server_port), handler); self.httpd.serve_forever()
        except: self.server_port += 1; self.start_server_thread(root_dir)

    def preview(self):
        target_path = self.deploy_path if self.deploy_path else os.path.join(self.output_dir, "Cloudflare_Deploy")
        if target_path and os.path.exists(target_path):
            t = threading.Thread(target=self.start_server_thread, args=(target_path,), daemon=True); t.start()
            time.sleep(1); webbrowser.open(f"http://127.0.0.1:{self.server_port}")
        else: messagebox.showerror("Error", "No folder to preview.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoGridV80(root)
    root.mainloop()