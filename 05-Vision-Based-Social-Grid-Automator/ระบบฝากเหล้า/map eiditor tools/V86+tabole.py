import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog, simpledialog
import os
import json
import webbrowser
import random
import colorsys
import math
import sys
import traceback

# --- CHECK DEPENDENCIES ---
try:
    from PIL import Image, ImageTk
except ImportError:
    tk.messagebox.showerror("Critical Error", "ไม่พบไลบรารี Pillow\nกรุณาติดตั้งด้วยคำสั่ง: pip install Pillow")
    sys.exit(1)

# ==============================================================================
# 1. HTML TEMPLATE (V96 - SHARP MAP & MULTI-SELECT LOGIC)
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

        .icon { font-size: 36px; margin-bottom: 8px; display: block; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); }
        .label { font-size: 18px; font-weight: 600; display: block; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .sub-label { font-size: 12px; color: rgba(255,255,255,0.8); display: block; margin-top: 2px; font-weight: 300; }

        .glass-input { background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 12px; width: 100%; color: var(--text-main); outline: none; margin-bottom: 10px; font-size: 16px; box-sizing: border-box; }
        .glass-input:focus { border-color: var(--accent); background: rgba(0,0,0,0.4); box-shadow: 0 0 0 1px var(--accent); }
        
        .btn-action { background: linear-gradient(90deg, var(--grad-start), var(--grad-end)); color: white; font-weight: bold; padding: 14px; border-radius: 16px; width: 100%; border: none; font-size: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; letter-spacing: 1px; }
        
        /* --- MAP STYLES --- */
        #map-container { width: 100%; height: 350px; background: #000; border-radius: 16px; margin-bottom: 15px; position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); display: none; }
        canvas { width: 100%; height: 100%; touch-action: none; }
        .map-hint { position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 8px; font-size: 10px; pointer-events: none; }
        
        /* Animation */
        .animate-pulse-border { animation: pulse-border 2s infinite; }
        @keyframes pulse-border { 0% { box-shadow: 0 0 0 0 rgba(234, 179, 8, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(234, 179, 8, 0); } 100% { box-shadow: 0 0 0 0 rgba(234, 179, 8, 0); } }

        __LAYOUT_CSS__
    </style>
</head>
<body>
    <div class="main-container">
        <div id="loading" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 backdrop-blur-sm"><div class="animate-spin rounded-full h-12 w-12 border-4 border-t-transparent" style="border-color: var(--accent);"></div></div>

        <div class="header-section">
            <div class="flex-1 text-left"><h1 class="text-2xl font-bold mb-0 tracking-tight" style="color: var(--text-main); text-shadow: 0 0 10px rgba(255,255,255,0.1);">__SHOP__</h1><p class="text-[10px] uppercase tracking-widest font-semibold opacity-70" style="color: var(--accent);">Nightlife System</p></div>
        </div>

        <div id="view-customer" class="hidden animate-fade-in">
             <div class="flex flex-col items-center mb-6"><div class="inline-block p-1 rounded-full border-2 mb-2 shadow-lg" style="border-color: var(--accent);"><img id="user-img" class="w-16 h-16 rounded-full" src=""></div><h2 id="user-name" class="text-xl font-bold" style="color: var(--text-main);">Guest</h2></div>
             <div id="menu-container" class="menu-layout w-full pb-4">
                <div onclick="show('view-booking'); tryRenderMap();" class="btn-menu menu-item-1"><span class="icon">📅</span><span class="label">จองโต๊ะ</span><span class="sub-label">เลือกโต๊ะจากผังร้าน</span></div>
                <div onclick="show('view-wallet');" class="btn-menu menu-item-2"><span class="icon">🥃</span><span class="label">ฝากเหล้า</span><span class="sub-label">เช็คของในสต็อก</span></div>
             </div>
        </div>

        <div id="view-booking" class="hidden h-full flex flex-col">
            <div class="flex justify-between mb-2 items-center"><h2 class="text-xl font-bold" style="color: var(--text-main);">📝 จองโต๊ะ</h2><button onclick="show('view-customer')" style="color: var(--text-sub);" class="text-2xl hover:text-white transition">×</button></div>
            
            <div class="flex-1 overflow-y-auto pr-1">
                <div id="map-container">
                    <canvas id="map-canvas"></canvas>
                    <div class="map-hint">👆 แตะเพื่อเลือกโต๊ะ (สีเหลือง)</div>
                </div>
                
                <div id="selected-table-info" class="hidden bg-white/5 p-2 rounded mb-3 border border-yellow-500/30 flex justify-between items-center">
                    <span class="text-gray-400 text-xs">โต๊ะที่เลือก:</span>
                    <span id="sel-table-id" class="text-yellow-400 font-bold text-lg">ยังไม่เลือก</span>
                </div>

                <div class="bg-white/5 p-5 rounded-3xl border border-white/10 space-y-4 shadow-xl backdrop-blur-sm">
                    <input type="text" id="bk-name" placeholder="ชื่อผู้จอง" class="glass-input">
                    <input type="tel" id="bk-phone" placeholder="เบอร์โทรติดต่อ" class="glass-input">
                    <div class="flex gap-3"><input type="date" id="bk-date" class="glass-input"><input type="time" id="bk-time" value="20:00" class="glass-input"></div>
                    
                    <div class="relative">
                        <input type="number" id="bk-pax" placeholder="จำนวนคน (เช่น 5)" class="glass-input" oninput="calculateTables()">
                        <div id="pax-hint" class="text-xs text-right text-yellow-500 mt-1 hidden">ต้องจอง 2 โต๊ะ</div>
                    </div>

                    <button onclick="submitBooking()" class="btn-action mt-2 shadow-xl hover:shadow-2xl transition-shadow">ยืนยันการจอง</button>
                </div>
            </div>
        </div>
        
        <div id="view-wallet" class="hidden h-full flex flex-col"><div class="flex justify-between mb-4 items-center"><button onclick="show('view-customer')" class="text-xs">← กลับ</button><h2 class="text-xl font-bold">My Bottle</h2></div><div class="text-center text-gray-500 mt-10">ระบบฝากเหล้า (API Connect)</div></div>

    </div>

    <script>
        const CFG = { liff: "__LIFF__", shop: "__SHOP__", hold: "__HOLD_TIME__", bk_tmpl: __BK_MSG__ };
        const BK_MODE = "__BK_MODE__";
        const MAP_DATA = __MAP_JSON__; 
        const MAP_IMG_URL = "__MAP_IMG__";
        
        let profile = {}, selectedTables = [];
        let requiredTableCount = 1;
        
        // --- MAP RENDERER (SHARP FIX) ---
        let mapImg = new Image();
        let scale = 1;

        async function main() {
            try { await liff.init({ liffId: CFG.liff }); 
                if (!liff.isLoggedIn()) { liff.login(); return; } 
                profile = await liff.getProfile(); 
                document.getElementById('user-img').src = profile.pictureUrl; 
                document.getElementById('user-name').innerText = profile.displayName; 
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('view-customer').classList.remove('hidden');
                document.getElementById('bk-date').valueAsDate = new Date();
            } catch(e) { 
                // Preview Mode
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('view-customer').classList.remove('hidden');
            }
        }
        
        function show(id) { document.querySelectorAll('[id^="view-"]').forEach(el => el.classList.add('hidden')); document.getElementById(id).classList.remove('hidden'); }

        function calculateTables() {
            const pax = parseInt(document.getElementById('bk-pax').value) || 0;
            if (pax > 0) {
                requiredTableCount = Math.ceil(pax / 4);
                const hint = document.getElementById('pax-hint');
                hint.innerText = `มา ${pax} คน = ต้องจอง ${requiredTableCount} โต๊ะ`;
                hint.classList.remove('hidden');
            } else {
                requiredTableCount = 1;
                document.getElementById('pax-hint').classList.add('hidden');
            }
            // Reset selection if requirement changes to avoid confusion
            if (BK_MODE === 'map') {
                selectedTables = [];
                updateSelectionUI();
                draw();
            }
        }

        function tryRenderMap() {
            if (BK_MODE !== 'map') return;
            const container = document.getElementById('map-container');
            container.style.display = 'block';
            
            const canvas = document.getElementById('map-canvas');
            const ctx = canvas.getContext('2d');
            
            // --- FIX: High DPI Canvas Scaling ---
            const dpr = window.devicePixelRatio || 1;
            const rect = container.getBoundingClientRect();
            
            // Set actual size in memory (scaled up for retina)
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            
            // Normalize coordinate system to use CSS pixels
            ctx.scale(dpr, dpr);
            
            mapImg.src = MAP_IMG_URL || "https://via.placeholder.com/800x600?text=No+Map+URL";
            mapImg.onload = () => {
                // Calculate scale to fit image into CSS width/height
                const scaleW = rect.width / mapImg.width;
                const scaleH = rect.height / mapImg.height;
                scale = Math.min(scaleW, scaleH);
                draw();
            };

            // Touch Handler
            canvas.onclick = (e) => {
                const rect = canvas.getBoundingClientRect();
                const clickX = (e.clientX - rect.left) / scale;
                const clickY = (e.clientY - rect.top) / scale;
                
                let clicked = null;
                const r = 30; // Radius hit box
                
                if (MAP_DATA && MAP_DATA.tables) {
                    MAP_DATA.tables.forEach(t => {
                        if (clickX >= t.x - r && clickX <= t.x + r && clickY >= t.y - r && clickY <= t.y + r) {
                            clicked = t;
                        }
                    });
                }
                
                if (clicked) handleTableClick(clicked);
            };
        }

        function handleTableClick(t) {
            // Check if already selected
            const index = selectedTables.indexOf(t.id);
            if (index > -1) {
                // Deselect
                selectedTables.splice(index, 1);
            } else {
                // Select new
                if (selectedTables.length < requiredTableCount) {
                    // Check Connectivity (Only if choosing more than 1)
                    if (selectedTables.length > 0) {
                        const lastId = selectedTables[selectedTables.length - 1];
                        const lastTable = MAP_DATA.tables.find(x => x.id === lastId);
                        
                        // Check if neighbors
                        const isNeighbor = lastTable.neighbors && lastTable.neighbors.includes(t.id);
                        if (!isNeighbor) {
                            return Swal.fire("ไม่ติดกัน", "กรุณาเลือกโต๊ะที่เชื่อมกัน", "warning");
                        }
                    }
                    selectedTables.push(t.id);
                } else {
                    // Replace last one or warn? Let's warn.
                    if (requiredTableCount === 1) {
                        selectedTables = [t.id]; // Single mode: just switch
                    } else {
                        Swal.fire("ครบแล้ว", `คุณเลือกครบ ${requiredTableCount} โต๊ะแล้ว`, "info");
                    }
                }
            }
            updateSelectionUI();
            draw();
        }

        function updateSelectionUI() {
            const el = document.getElementById('selected-table-info');
            const txt = document.getElementById('sel-table-id');
            if (selectedTables.length > 0) {
                el.classList.remove('hidden');
                txt.innerText = selectedTables.join(", ");
                // Highlight color check
                txt.style.color = (selectedTables.length === requiredTableCount) ? "#4ade80" : "#fbbf24";
            } else {
                el.classList.add('hidden');
            }
        }

        function draw() {
            const canvas = document.getElementById('map-canvas');
            const ctx = canvas.getContext('2d');
            
            // Clear using logical size
            const rect = canvas.getBoundingClientRect();
            ctx.clearRect(0, 0, rect.width, rect.height);
            
            ctx.save();
            ctx.scale(scale, scale);
            ctx.drawImage(mapImg, 0, 0);
            
            if (MAP_DATA && MAP_DATA.tables) {
                MAP_DATA.tables.forEach(t => {
                    const isSelected = selectedTables.includes(t.id);
                    
                    ctx.beginPath();
                    ctx.arc(t.x, t.y, 20, 0, 2 * Math.PI);
                    
                    if (isSelected) {
                        ctx.fillStyle = "#EAB308"; // Selected Yellow
                        ctx.strokeStyle = "#ffffff";
                        ctx.lineWidth = 3;
                    } else {
                        // Check if it's a valid neighbor option for the NEXT selection
                        let isPotential = false;
                        if (selectedTables.length > 0 && selectedTables.length < requiredTableCount) {
                            const lastId = selectedTables[selectedTables.length - 1];
                            const lastTable = MAP_DATA.tables.find(x => x.id === lastId);
                            if (lastTable && lastTable.neighbors && lastTable.neighbors.includes(t.id)) {
                                isPotential = true;
                            }
                        }

                        if (isPotential) {
                            ctx.fillStyle = "rgba(74, 222, 128, 0.8)"; // Green hint
                            ctx.strokeStyle = "#ffffff";
                            ctx.lineWidth = 2;
                        } else {
                            ctx.fillStyle = "rgba(59, 130, 246, 0.6)"; // Normal Blue
                            ctx.strokeStyle = "rgba(255,255,255,0.5)";
                            ctx.lineWidth = 1;
                        }
                    }
                    
                    ctx.fill();
                    ctx.stroke();
                    
                    // Text
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
            const name = document.getElementById('bk-name').value;
            const phone = document.getElementById('bk-phone').value;
            const pax = document.getElementById('bk-pax').value;
            const date = document.getElementById('bk-date').value;
            const time = document.getElementById('bk-time').value;

            if (!name || !phone || !pax) {
                return Swal.fire("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลให้ครบถ้วน", "warning");
            }

            if (BK_MODE === 'map') {
                if (selectedTables.length < requiredTableCount) {
                    return Swal.fire("เลือกโต๊ะไม่ครบ", `มา ${pax} คน กรุณาเลือก ${requiredTableCount} โต๊ะ`, "warning");
                }
            }

            let msg = CFG.bk_tmpl;
            msg = msg.replace('{name}', name).replace('{phone}', phone)
                     .replace('{date}', date).replace('{time}', time)
                     .replace('{pax}', pax).replace('{shop}', CFG.shop)
                     .replace('{hold}', CFG.hold);
            
            if (BK_MODE === 'map' && selectedTables.length > 0) {
                msg += `\n📍 โต๊ะที่จอง: ${selectedTables.join(", ")}`;
            }

            if(liff.isInClient()) {
                await liff.sendMessages([{type:'text', text:msg}]);
                liff.closeWindow();
            } else {
                Swal.fire("จำลองการส่ง", msg, "success");
            }
        }
        
        main();
    </script>
</body>
</html>"""

# ==============================================================================
# 2. APP GENERATOR CLASS (V96)
# ==============================================================================
class AppGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nightlife System V96 (High-Res Map & Logic)")
        self.geometry("1200x950")
        
        self.map_json_data = {"tables": []} 
        self.map_img_url = ""
        self.profiles = {}
        self.profile_file = "profiles.json"
        
        self.vars = { 
            'bg_color': '#0f172a', 'grad_start': '#0e4296', 'grad_end': '#1e293b', 
            'text_main': '#ffffff', 'text_sub': '#94a3b8', 'accent': '#EAB308', 
            'radius': '16px' 
        }
        
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
        
        # Profile Manager
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
        
        for k in ["Shop Name", "LIFF ID", "Worker URL", "Manager Password", "R2 Public URL", "Channel Access Token", "D1 Database ID", "Hold Table Time"]:
            ctk.CTkLabel(self.scroll, text=k).pack(anchor="w", padx=20)
            e = ctk.CTkEntry(self.scroll); e.pack(fill="x", padx=20)
            self.entries[k] = e
            if k == "Shop Name": e.bind("<KeyRelease>", self.update_preview_text)
        
        # --- FEATURE: BOOKING MODE ---
        ctk.CTkLabel(self.scroll, text="Booking System Mode", text_color="#EAB308").pack(anchor="w", padx=20, pady=(15,5))
        self.combo_bk_mode = ctk.CTkComboBox(self.scroll, values=["Standard (Form Only)", "Interactive Map (Select Table)"])
        self.combo_bk_mode.set("Interactive Map (Select Table)")
        self.combo_bk_mode.pack(fill="x", padx=20)
        # -----------------------------

        ctk.CTkLabel(self.scroll, text="Booking Message Template").pack(anchor="w", padx=20, pady=(10,5))
        self.txt_booking = ctk.CTkTextbox(self.scroll, height=80); self.txt_booking.pack(fill="x", padx=20)
        self.default_bk_tmpl = """✨ Booking Confirmed ✨\n━━━━━━━━━━━━━━━━━━\nร้าน: {shop}\nชื่อ: {name}\nเบอร์: {phone}\nวันที่: {date}\nเวลา: {time}\nจำนวน: {pax} คน\n\n*กรุณามารับโต๊ะก่อนเวลา {hold}\nเพื่อรักษาสิทธิ์ของท่าน"""
        self.txt_booking.insert("1.0", self.default_bk_tmpl)

        # Map Tools
        ctk.CTkLabel(self.scroll, text="Map Integration", text_color="#3b82f6").pack(anchor="w", padx=20, pady=(20,5))
        self.btn_map = ctk.CTkButton(self.scroll, text="🗺️ Open Map Editor", command=self.open_map_editor, fg_color="#3b82f6")
        self.btn_map.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.scroll, text="📂 Import JSON Map", command=self.import_map_json, fg_color="#64748b").pack(fill="x", padx=20, pady=5)
        self.lbl_map_status = ctk.CTkLabel(self.scroll, text="No Map Loaded", text_color="gray", font=("Arial", 10))
        self.lbl_map_status.pack(padx=20)

        ctk.CTkButton(left, text="GENERATE APP", command=self.build, height=50, fg_color="#10B981").pack(fill="x", padx=20, pady=20)

        # Preview Section
        self.preview = ctk.CTkFrame(self, fg_color="#000"); self.preview.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(self.preview, text="LIVE PREVIEW", font=("Arial", 20, "bold"), text_color="white").pack(pady=20)
        self.phone = ctk.CTkFrame(self.preview, width=375, height=667, fg_color="#fff"); self.phone.pack()
        self.phone.pack_propagate(False)
        self.p_head = ctk.CTkLabel(self.phone, text="SHOP", font=("Arial", 20))
        self.p_head.pack(pady=(40, 10))
        self.p_container = ctk.CTkFrame(self.phone, fg_color="transparent")
        self.p_container.pack(fill="both", expand=True, padx=20)

    # --- HELPER LOGIC ---
    def update_preview_ui(self, e=None):
        self.phone.configure(fg_color=self.vars['bg_color'])
        self.p_head.configure(text_color=self.vars['text_main'])
        for widget in self.p_container.winfo_children(): widget.destroy()
        
        # Simple Mockup Buttons
        btn1 = ctk.CTkFrame(self.p_container, height=80, fg_color=self.vars['grad_start']); btn1.pack(fill="x", pady=10)
        ctk.CTkLabel(btn1, text="Booking", text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        btn2 = ctk.CTkFrame(self.p_container, height=80, fg_color=self.vars['grad_start']); btn2.pack(fill="x", pady=10)
        ctk.CTkLabel(btn2, text="Wallet", text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    def update_preview_text(self, e): 
        self.p_head.configure(text=self.entries["Shop Name"].get())

    def new_profile(self):
        for k in self.entries: self.entries[k].delete(0, "end")
        self.txt_booking.delete("1.0", "end"); self.txt_booking.insert("1.0", self.default_bk_tmpl)
        self.combo_profiles.set("")

    def save_current_profile(self):
        name = self.entries["Shop Name"].get().strip()
        if not name: return
        data = {k: v.get() for k,v in self.entries.items()}
        data['colors'] = self.vars.copy()
        data['bk_mode'] = self.combo_bk_mode.get()
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
            if 'bk_tmpl' in data:
                self.txt_booking.delete("1.0", "end")
                self.txt_booking.insert("1.0", data['bk_tmpl'])
            if 'colors' in data: self.vars.update(data['colors'])
            if 'bk_mode' in data: self.combo_bk_mode.set(data['bk_mode'])
            self.update_preview_ui()

    def delete_profile(self):
        name = self.combo_profiles.get()
        if name in self.profiles:
            del self.profiles[name]; self.save_profiles()
            self.combo_profiles.configure(values=list(self.profiles.keys())); self.combo_profiles.set("")
            self.new_profile()

    def open_map_editor(self):
        MapEditorWindow(self)

    def import_map_json(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.map_json_data = data
                    self.map_img_url = data.get('url', '')
                    self.lbl_map_status.configure(text=f"Loaded: {len(data.get('tables', []))} Tables", text_color="#10b981")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid JSON: {e}")

    def build(self):
        shop = self.entries["Shop Name"].get()
        db_id = self.entries["D1 Database ID"].get().strip()
        if not shop: return messagebox.showerror("Error", "No Shop Name")
        if not db_id: return messagebox.showerror("Error", "Please enter D1 Database ID")
        
        map_json_str = json.dumps(self.map_json_data)
        bk_msg_safe = json.dumps(self.txt_booking.get("1.0", "end-1c"))
        bk_mode_val = "map" if "Interactive" in self.combo_bk_mode.get() else "standard"

        html = HTML_RAW
        for k, v in [("__SHOP__", shop), ("__BG_COLOR__", self.vars['bg_color']), ("__GRAD_START__", self.vars['grad_start']), ("__GRAD_END__", self.vars['grad_end']), ("__TEXT_MAIN__", self.vars['text_main']), ("__TEXT_SUB__", self.vars['text_sub']), ("__ACCENT__", self.vars['accent']), ("__LIFF__", self.entries["LIFF ID"].get()), ("__HOLD_TIME__", self.entries["Hold Table Time"].get()), ("__LAYOUT_CSS__", ""), ("__BK_MSG__", bk_msg_safe), ("__MAP_JSON__", map_json_str), ("__MAP_IMG__", self.map_img_url), ("__BK_MODE__", bk_mode_val)]:
            html = html.replace(k, v)
            
        worker = """export default { async fetch(request, env, ctx) { return new Response("Worker V96 Ready", {headers: {"Access-Control-Allow-Origin": "*"}}); } };""" # Simplified Worker for this snippet (Full worker logic from V85.2 should be used in real prod)
        
        folder = f"Output_{shop.replace(' ', '_')}"
        if not os.path.exists(folder): os.makedirs(folder)
        with open(f"{folder}/index.html", "w", encoding="utf-8") as f: f.write(html)
        with open(f"{folder}/worker.js", "w", encoding="utf-8") as f: f.write(worker)
        with open(f"{folder}/wrangler.toml", "w", encoding="utf-8") as f: f.write(f"""name = "nightlife-app"\nmain = "worker.js"\ncompatibility_date = "2023-10-30"\n\n[vars]\nLINE_TOKEN = "{self.entries["Channel Access Token"].get()}"\n\n[[d1_databases]]\nbinding = "DB"\ndatabase_name = "nightlife-db"\ndatabase_id = "{db_id}"\n\n[[r2_buckets]]\nbinding = "BUCKET"\nbucket_name = "nightlife-bucket"\n\n[triggers]\ncrons = ["0 7 * * *"]""")
        
        self.save_current_profile()
        messagebox.showinfo("Success", f"Generated V96 with Smart Map Logic!\nLocation: {folder}")
        webbrowser.open(folder)

# --- MAP EDITOR CLASS (Re-included for completeness) ---
class MapEditorWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent); self.title("Map Editor"); self.geometry("1200x800")
        self.tables = []; self.img_path = None; self.tk_image = None; self.img_width = 1000; self.img_height = 1000; self.table_radius = 20; self.edit_tool = "VIEW"; self.setup_ui()
    
    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=250); self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkButton(self.sidebar, text="📂 Load Image", command=self.load_image).pack(fill="x", pady=5)
        self.ent_url = ctk.CTkEntry(self.sidebar, placeholder_text="Web Image URL"); self.ent_url.pack(fill="x", pady=5)
        ctk.CTkButton(self.sidebar, text="➕ Add Table", command=lambda: self.set_tool("ADD")).pack(fill="x", pady=2)
        ctk.CTkButton(self.sidebar, text="🔗 Link Tables", command=lambda: self.set_tool("LINK")).pack(fill="x", pady=2)
        ctk.CTkButton(self.sidebar, text="💾 SAVE JSON", command=self.save_json, fg_color="#10b981").pack(side="bottom", fill="x", pady=20)
        self.canvas = tk.Canvas(self, bg="#0f172a"); self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

    def set_tool(self, t): self.edit_tool = t
    def load_image(self):
        try:
            path = filedialog.askopenfilename(parent=self, filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                img = Image.open(path); img.thumbnail((2000, 2000))
                self.img_width, self.img_height = img.size; self.tk_image = ImageTk.PhotoImage(img)
                self.tables = []; self.redraw()
        except Exception as e: messagebox.showerror("Error", str(e))

    def redraw(self):
        self.canvas.delete("all")
        if self.tk_image: self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
        for t in self.tables:
            self.canvas.create_oval(t['x']-20, t['y']-20, t['x']+20, t['y']+20, fill="#3b82f6", outline="white")
            self.canvas.create_text(t['x'], t['y'], text=t['id'], fill="white")
            for n in t.get('neighbors', []):
                target = next((x for x in self.tables if x['id'] == n), None)
                if target: self.canvas.create_line(t['x'], t['y'], target['x'], target['y'], fill="yellow", dash=(4,2))

    def on_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        clicked = next((t for t in self.tables if (t['x']-25 < x < t['x']+25) and (t['y']-25 < y < t['y']+25)), None)
        
        if self.edit_tool == "ADD" and not clicked:
            tid = simpledialog.askstring("ID", "Table ID:", parent=self)
            if tid: self.tables.append({"id": tid, "x": x, "y": y, "neighbors": []}); self.redraw()
        elif self.edit_tool == "LINK" and clicked:
            if not hasattr(self, 'link_start') or not self.link_start: self.link_start = clicked
            else:
                if self.link_start != clicked:
                    if clicked['id'] not in self.link_start['neighbors']: self.link_start['neighbors'].append(clicked['id'])
                    if self.link_start['id'] not in clicked['neighbors']: clicked['neighbors'].append(self.link_start['id'])
                self.link_start = None; self.redraw()

    def save_json(self):
        data = {"url": self.ent_url.get(), "tables": self.tables}
        f = filedialog.asksaveasfilename(defaultextension=".json", parent=self)
        if f: 
            with open(f, "w") as out: json.dump(data, out)
            messagebox.showinfo("Saved", "Saved JSON!", parent=self); self.destroy()

if __name__ == "__main__": app = AppGenerator(); app.mainloop()