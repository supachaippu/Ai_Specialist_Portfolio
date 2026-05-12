import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import json
import os
import math
import sys

# ตั้งค่า Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MapEditorFinal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Map Editor V89 (Anti-Freeze)")
        self.geometry("1400x900")
        
        # --- Data Model ---
        self.tables = [] 
        self.img_path = None
        self.tk_image = None
        self.img_width = 0
        self.img_height = 0
        self.table_radius = 20
        
        # --- State ---
        self.mode = "EDIT"
        self.edit_tool = "VIEW" 
        self.selected_table = None 
        self.align_ref = None 
        
        # --- Booking Sim State ---
        self.sim_pax = 1
        self.sim_required_tables = 1
        self.sim_selected = [] 

        self.setup_ui()

    def setup_ui(self):
        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="📐 MAP EDITOR", font=("Arial", 24, "bold"), text_color="#EAB308").pack(pady=(20, 10))
        
        # Mode Switcher
        self.mode_segment = ctk.CTkSegmentedButton(self.sidebar, values=["🛠️ EDIT MODE", "🧪 TEST SIM"], command=self.switch_mode)
        self.mode_segment.set("🛠️ EDIT MODE")
        self.mode_segment.pack(padx=10, pady=10, fill="x")

        # --- PANEL: EDIT TOOLS ---
        self.frame_edit = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_edit.pack(fill="x", padx=10)
        
        # FILE OPERATIONS
        ctk.CTkLabel(self.frame_edit, text="1. Files (Step-by-Step):", text_color="gray", anchor="w").pack(fill="x")
        
        # Load Image Button
        self.btn_load = ctk.CTkButton(self.frame_edit, text="① Load Image (รูปผังร้าน)", command=self.load_image, fg_color="#3b82f6")
        self.btn_load.pack(pady=5, fill="x")
        
        # Load JSON Button
        self.btn_load_json = ctk.CTkButton(self.frame_edit, text="② Load JSON (งานเก่า)", command=self.load_json, fg_color="#6366f1", state="disabled")
        self.btn_load_json.pack(pady=5, fill="x")
        
        # Status Label (แทน Popup เพื่อกันค้าง)
        self.lbl_file_status = ctk.CTkLabel(self.frame_edit, text="Waiting for Image...", text_color="gray", font=("Arial", 12))
        self.lbl_file_status.pack(pady=5)
        
        # TABLE SIZE
        ctk.CTkLabel(self.frame_edit, text="2. Table Size (Zoom):", text_color="#EAB308", anchor="w").pack(fill="x", pady=(15,0))
        self.slider_size = ctk.CTkSlider(self.frame_edit, from_=10, to=60, number_of_steps=50, command=self.update_table_size)
        self.slider_size.set(20) 
        self.slider_size.pack(pady=5, fill="x")
        
        # TOOLS
        ctk.CTkLabel(self.frame_edit, text="3. Creation Tools:", text_color="gray", anchor="w").pack(fill="x", pady=(10,0))
        self.btn_add = ctk.CTkButton(self.frame_edit, text="➕ วางโต๊ะ (Place)", command=lambda: self.set_tool("ADD"), fg_color="transparent", border_width=1, anchor="w")
        self.btn_add.pack(pady=2, fill="x")
        self.btn_link = ctk.CTkButton(self.frame_edit, text="🔗 เชื่อมโต๊ะ (Link)", command=lambda: self.set_tool("LINK"), fg_color="transparent", border_width=1, anchor="w")
        self.btn_link.pack(pady=2, fill="x")
        self.btn_del = ctk.CTkButton(self.frame_edit, text="❌ ลบโต๊ะ (Delete)", command=lambda: self.set_tool("DELETE"), fg_color="transparent", border_width=1, text_color="#ef4444", border_color="#ef4444", anchor="w")
        self.btn_del.pack(pady=2, fill="x")

        # ALIGNMENT
        ctk.CTkLabel(self.frame_edit, text="4. Alignment:", text_color="gray", anchor="w").pack(fill="x", pady=(10,0))
        self.btn_align_h = ctk.CTkButton(self.frame_edit, text="↔️ จัดตรงแนวนอน", command=lambda: self.set_tool("ALIGN_H"), fg_color="transparent", border_width=1, anchor="w")
        self.btn_align_h.pack(pady=2, fill="x")
        self.btn_align_v = ctk.CTkButton(self.frame_edit, text="↕️ จัดตรงแนวตั้ง", command=lambda: self.set_tool("ALIGN_V"), fg_color="transparent", border_width=1, anchor="w")
        self.btn_align_v.pack(pady=2, fill="x")
        
        self.lbl_status = ctk.CTkLabel(self.frame_edit, text="Ready", text_color="#10b981")
        self.lbl_status.pack(pady=10)

        # --- PANEL: SIMULATION ---
        self.frame_test = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        
        ctk.CTkLabel(self.frame_test, text="Test Scenario:", text_color="gray", anchor="w").pack(fill="x")
        self.pax_frame = ctk.CTkFrame(self.frame_test, fg_color="transparent")
        self.pax_frame.pack(fill="x", pady=5)
        self.ent_pax = ctk.CTkEntry(self.pax_frame, placeholder_text="1")
        self.ent_pax.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.btn_calc = ctk.CTkButton(self.pax_frame, text="Set Pax", width=60, command=self.update_sim_req)
        self.btn_calc.pack(side="right")
        
        self.info_box = ctk.CTkFrame(self.frame_test, fg_color="#334155")
        self.info_box.pack(pady=10, fill="x", ipady=10)
        ctk.CTkLabel(self.info_box, text="REQUIRED TABLES", font=("Arial", 10)).pack()
        self.lbl_req = ctk.CTkLabel(self.info_box, text="1", font=("Arial", 30, "bold"), text_color="#EAB308")
        self.lbl_req.pack()
        
        self.btn_reset = ctk.CTkButton(self.frame_test, text="🔄 Reset Selection", command=self.reset_sim, fg_color="#64748b")
        self.btn_reset.pack(pady=10, fill="x")
        
        self.lbl_sim_msg = ctk.CTkLabel(self.frame_test, text="Ready", text_color="white", wraplength=220)
        self.lbl_sim_msg.pack(pady=5)

        # Footer
        self.btn_save = ctk.CTkButton(self.sidebar, text="💾 Export JSON", command=self.export_json, fg_color="#10b981", height=40)
        self.btn_save.pack(side="bottom", pady=20, padx=10, fill="x")

        # 2. Main Canvas
        self.canvas_frame = ctk.CTkFrame(self, fg_color="#0f172a")
        self.canvas_frame.pack(side="right", fill="both", expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    # --- Mode Switching ---
    def switch_mode(self, value):
        if "EDIT" in value:
            self.mode = "EDIT"
            self.frame_test.pack_forget()
            self.frame_edit.pack(fill="x", padx=10)
            self.set_tool("VIEW")
        else:
            self.mode = "TEST"
            self.frame_edit.pack_forget()
            self.frame_test.pack(fill="x", padx=10)
            self.reset_sim()
        self.redraw()

    def set_tool(self, tool):
        self.edit_tool = tool
        self.selected_table = None
        self.align_ref = None 
        
        btns = [self.btn_add, self.btn_link, self.btn_del, self.btn_align_h, self.btn_align_v]
        for b in btns: b.configure(fg_color="transparent")
        
        active_color = "#334155"
        if tool == "ADD": self.btn_add.configure(fg_color=active_color)
        elif tool == "LINK": self.btn_link.configure(fg_color=active_color)
        elif tool == "DELETE": self.btn_del.configure(fg_color=active_color)
        elif tool == "ALIGN_H": self.btn_align_h.configure(fg_color=active_color)
        elif tool == "ALIGN_V": self.btn_align_v.configure(fg_color=active_color)
        
        msgs = {
            "ADD": "จิ้มที่แผนผังเพื่อวางโต๊ะ",
            "LINK": "จิ้มโต๊ะ A แล้วไปจิ้มโต๊ะ B เพื่อเชื่อม",
            "DELETE": "จิ้มโต๊ะที่ต้องการลบ",
            "ALIGN_H": "เลือกโต๊ะหลัก -> เลือกโต๊ะที่จะให้ตรง",
            "ALIGN_V": "เลือกโต๊ะหลัก -> เลือกโต๊ะที่จะให้ตรง",
            "VIEW": "ลากย้ายตำแหน่งได้"
        }
        self.lbl_status.configure(text=msgs.get(tool, "Ready"), text_color="#10b981")
        self.redraw()

    def update_table_size(self, value):
        self.table_radius = int(value)
        self.redraw()

    # --- Simulation Logic ---
    def update_sim_req(self):
        try:
            pax = int(self.ent_pax.get())
            if pax < 1: pax = 1
            req = math.ceil(pax / 4)
            self.sim_pax = pax
            self.sim_required_tables = req
            self.lbl_req.configure(text=str(req))
            self.reset_sim()
        except:
            pass

    def reset_sim(self):
        self.sim_selected = []
        if self.sim_required_tables > 1:
            self.lbl_sim_msg.configure(text=f"ต้องเลือก {self.sim_required_tables} โต๊ะที่ติดกัน", text_color="#EAB308")
        else:
            self.lbl_sim_msg.configure(text="เลือกโต๊ะที่ต้องการ", text_color="white")
        self.redraw()

    # --- Drawing Logic ---
    def redraw(self):
        self.canvas.delete("all")
        
        if self.tk_image:
            self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
            self.canvas.config(scrollregion=(0,0, self.img_width, self.img_height))
        else:
            self.canvas.create_text(400, 300, text="กรุณากด Load Image เพื่อเริ่มทำงาน", fill="gray", font=("Arial", 24))
            return

        drawn_links = set()
        
        for t in self.tables:
            for n_id in t['neighbors']:
                target = next((x for x in self.tables if x['id'] == n_id), None)
                if target:
                    link_id = tuple(sorted((t['id'], target['id'])))
                    if link_id not in drawn_links:
                        is_merged = (self.mode == "TEST" and t['id'] in self.sim_selected and target['id'] in self.sim_selected)
                        
                        if self.mode == "EDIT":
                            self.canvas.create_line(t['x'], t['y'], target['x'], target['y'], fill="#fbbf24", width=2, dash=(4,2))
                        elif self.mode == "TEST" and is_merged:
                            capsule_width = self.table_radius * 2.2 
                            self.canvas.create_line(t['x'], t['y'], target['x'], target['y'], fill="#EAB308", width=capsule_width, capstyle=tk.ROUND)
                        
                        drawn_links.add(link_id)

        r = self.table_radius 
        for t in self.tables:
            t_id = t['id']
            fill = "#3b82f6"
            outline = "white"
            width = 2
            
            if self.mode == "EDIT":
                if self.selected_table and self.selected_table['id'] == t_id:
                    fill = "#ef4444"
                elif self.align_ref and self.align_ref['id'] == t_id:
                    fill = "#06b6d4" 
                    outline = "#22d3ee"
                    width = 4
                    
            elif self.mode == "TEST":
                if t_id in self.sim_selected:
                    fill = "#EAB308" 
                    outline = "white" 
                    width = 2
                else:
                    is_neighbor = False
                    if len(self.sim_selected) > 0 and len(self.sim_selected) < self.sim_required_tables:
                        last = next((x for x in self.tables if x['id'] == self.sim_selected[-1]), None)
                        if last and t_id in last['neighbors']:
                            is_neighbor = True
                    
                    if is_neighbor:
                        fill = "#22c55e" # Green
                        width = 3
                    elif len(self.sim_selected) == 0:
                        fill = "#3b82f6" # Normal
                    else:
                        fill = "#1e293b" # Dimmed
                        outline = "#475569"

            self.canvas.create_oval(t['x']-r, t['y']-r, t['x']+r, t['y']+r, fill=fill, outline=outline, width=width)
            
            if r > 10:
                text_col = "black" if (self.mode=="TEST" and t_id in self.sim_selected) else "white"
                font_size = max(8, int(r * 0.6))
                self.canvas.create_text(t['x'], t['y'], text=t_id, fill=text_col, font=("Arial", font_size, "bold"))

    # --- Interaction ---
    def on_click(self, event):
        if not self.tk_image: return
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        clicked = None
        r = self.table_radius + 5
        for t in self.tables:
            if (t['x']-r < x < t['x']+r) and (t['y']-r < y < t['y']+r):
                clicked = t
                break
        
        if self.mode == "EDIT":
            self.handle_edit(x, y, clicked)
        else:
            self.handle_test(clicked)

    def handle_edit(self, x, y, clicked):
        if self.edit_tool == "ADD":
            if clicked: return
            tid = simpledialog.askstring("ID", "ตั้งชื่อโต๊ะ (เช่น A1):")
            if tid:
                if any(t['id'] == tid for t in self.tables):
                    messagebox.showerror("Error", "ชื่อซ้ำกัน")
                    return
                self.tables.append({"id": tid, "x": x, "y": y, "neighbors": []})
                self.redraw()
        
        elif self.edit_tool == "DELETE":
            if clicked:
                for t in self.tables:
                    if clicked['id'] in t['neighbors']: t['neighbors'].remove(clicked['id'])
                self.tables.remove(clicked)
                self.redraw()
                
        elif self.edit_tool == "LINK":
            if clicked:
                if not self.selected_table:
                    self.selected_table = clicked
                else:
                    if self.selected_table != clicked:
                        t1, t2 = self.selected_table, clicked
                        if t2['id'] not in t1['neighbors']: t1['neighbors'].append(t2['id'])
                        if t1['id'] not in t2['neighbors']: t2['neighbors'].append(t1['id'])
                    self.selected_table = None
                self.redraw()
                
        elif self.edit_tool in ["ALIGN_H", "ALIGN_V"]:
            if clicked:
                if not self.align_ref:
                    self.align_ref = clicked
                    self.lbl_status.configure(text=f"Ref: {clicked['id']} -> Click targets")
                else:
                    if self.edit_tool == "ALIGN_H": clicked['y'] = self.align_ref['y']
                    else: clicked['x'] = self.align_ref['x']
                self.redraw()
            else:
                self.align_ref = None
                self.lbl_status.configure(text="Ref cleared. Select new.")
                self.redraw()

    def handle_test(self, clicked):
        if not clicked: return
        if clicked['id'] in self.sim_selected:
            self.reset_sim()
            return
            
        if len(self.sim_selected) == 0:
            self.sim_selected.append(clicked['id'])
        elif len(self.sim_selected) < self.sim_required_tables:
            last = next(t for t in self.tables if t['id'] == self.sim_selected[-1])
            if clicked['id'] in last['neighbors']:
                self.sim_selected.append(clicked['id'])
            else:
                self.lbl_sim_msg.configure(text="❌ ต้องเลือกโต๊ะที่ติดกันเท่านั้น!", text_color="#ef4444")
                return
        
        if len(self.sim_selected) == self.sim_required_tables:
            self.lbl_sim_msg.configure(text=f"✅ ครบแล้ว: {self.sim_selected}", text_color="#10b981")
        else:
            self.lbl_sim_msg.configure(text="เลือกต่ออีก...", text_color="#3b82f6")
        self.redraw()

    def on_drag(self, event):
        if self.mode == "EDIT" and self.edit_tool == "VIEW":
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            x = max(0, min(x, self.img_width))
            y = max(0, min(y, self.img_height))
            
            r = self.table_radius + 5
            for t in self.tables:
                if (t['x']-r < x < t['x']+r) and (t['y']-r < y < t['y']+r):
                    t['x'] = x
                    t['y'] = y
                    self.redraw()
                    break

    def load_image(self):
        try:
            path = filedialog.askopenfilename(title="Select Floor Plan")
            if not path: return
            # Basic validation
            valid = ['.png', '.jpg', '.jpeg', '.bmp']
            if not any(path.lower().endswith(ext) for ext in valid):
                self.lbl_file_status.configure(text="Invalid Image File", text_color="red")
                return
            
            pil_img = Image.open(path)
            base_height = 700
            w_percent = (base_height / float(pil_img.size[1]))
            w_size = int((float(pil_img.size[0]) * float(w_percent)))
            
            if hasattr(Image, 'Resampling'): resample = Image.Resampling.LANCZOS
            else: resample = Image.ANTIALIAS
            
            pil_img = pil_img.resize((w_size, base_height), resample)
            
            self.img_path = path
            self.img_width = w_size
            self.img_height = base_height
            self.tk_image = ImageTk.PhotoImage(pil_img)
            self.tables = []
            
            # Unlock JSON Load button
            self.btn_load_json.configure(state="normal")
            self.lbl_file_status.configure(text=f"Loaded Image: {os.path.basename(path)}", text_color="#10b981")
            self.redraw()
        except Exception as e:
            self.lbl_file_status.configure(text=f"Error: {str(e)}", text_color="red")

    def load_json(self):
        if not self.tk_image:
            self.lbl_file_status.configure(text="⚠️ PLEASE LOAD IMAGE FIRST", text_color="orange")
            return

        try:
            path = filedialog.askopenfilename(title="Select JSON Layout", defaultextension=".json")
            if not path: return
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.tables = []
            for t_data in data.get('tables', []):
                px_x = (t_data['x'] / 100) * self.img_width
                px_y = (t_data['y'] / 100) * self.img_height
                
                self.tables.append({
                    "id": t_data['id'],
                    "x": px_x,
                    "y": px_y,
                    "neighbors": t_data.get('neighbors', [])
                })
            
            self.redraw()
            # NO POPUP (To prevent freeze)
            self.lbl_file_status.configure(text=f"Loaded JSON: {len(self.tables)} tables", text_color="#10b981")
            
        except Exception as e:
            self.lbl_file_status.configure(text=f"JSON Error: {str(e)}", text_color="red")

    def export_json(self):
        if not self.tables: 
            self.lbl_file_status.configure(text="Nothing to save", text_color="orange")
            return
            
        data = []
        for t in self.tables:
            data.append({
                "id": t['id'],
                "label": t['id'],
                "x": round((t['x']/self.img_width)*100, 2),
                "y": round((t['y']/self.img_height)*100, 2),
                "neighbors": t['neighbors']
            })
        
        f = filedialog.asksaveasfilename(defaultextension=".json", title="Save Layout JSON")
        if f:
            with open(f, "w") as out:
                json.dump({"tables": data}, out, indent=2)
            # NO POPUP (To prevent freeze)
            self.lbl_file_status.configure(text=f"Saved to: {os.path.basename(f)}", text_color="#10b981")

if __name__ == "__main__":
    try:
        app = MapEditorFinal()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")