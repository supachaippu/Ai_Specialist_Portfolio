import streamlit as st
import os
import shutil
import re
import stat
import json

# 🏭 V91 STORE FACTORY - ANTIGRAVITY EDITION
st.set_page_config(page_title="V91 Store Factory", page_icon="🏭", layout="wide")

# Paths relative to this file
FACTORY_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FACTORY_DIR)
TEMPLATE_DIR = os.path.join(FACTORY_DIR, "template")
CONFIGS_DIR = os.path.join(FACTORY_DIR, "configs")
V91_SRC_DIR = os.path.join(BASE_DIR, "V91")

if not os.path.exists(CONFIGS_DIR):
    os.makedirs(CONFIGS_DIR)

# --- PREMIUM THEMES ---
THEMES = {
    "✨ Luxury Gold": {"accent": "#EAB308", "bg": "#060a14", "grad_start": "#1e3a8a", "grad_end": "#1e293b"},
    "🌿 Emerald Green": {"accent": "#10b981", "bg": "#022c22", "grad_start": "#065f46", "grad_end": "#064e3b"},
    "🍷 Ruby Red": {"accent": "#ef4444", "bg": "#2d0a0a", "grad_start": "#7f1d1d", "grad_end": "#450a0a"},
    "💎 Sapphire Blue": {"accent": "#3b82f6", "bg": "#081b33", "grad_start": "#1e40af", "grad_end": "#172554"},
    "🔮 Midnight Violet": {"accent": "#a855f7", "bg": "#1e0b3c", "grad_start": "#4c1d95", "grad_end": "#2e1065"},
    "🔥 Deep Orange": {"accent": "#f97316", "bg": "#2a0f05", "grad_start": "#9a3412", "grad_end": "#7c2d12"}
}

# --- MOCK SCRIPT FOR _INDEX.HTML ---
MOCK_FETCH_SCRIPT = """
    <!-- --- MOCK SYSTEM BY ANTIGRAVITY --- -->
    <script>
        console.log("🛠️ RUNNING IN STATIC DEMO MODE");
        
        // 1. Mock LIFF System
        window.liff = {
            init: async () => { console.log("Mock LIFF Init Success"); return true; },
            isLoggedIn: () => true,
            getProfile: async () => ({
                userId: 'U_DEMO_ADMIN_999',
                displayName: 'Admin Demo User (Local)',
                pictureUrl: 'https://v86-th.com/v88/demo-avatar.png'
            })
        };

        // 2. Mock Fetch APIs for Offline Testing
        const originalFetch = window.fetch;
        window.fetch = async (url, options) => {
            console.log("⚓ API INTERCEPTED:", url);
            
            // Mock Response Helper
            const mockRes = (data) => ({
                ok: true,
                status: 200,
                json: async () => data
            });

            if (url.includes('/api/config')) {
                return mockRes({ 
                    name: "{{SHOP_NAME}}", 
                    tier: {{TIER}}
                });
            }
            if (url.includes('/api/me')) {
                return mockRes({ 
                    role: 'manager', 
                    status: 'active', 
                    staffName: 'Admin Tester', 
                    phone: '0812345678', 
                    points: 999 
                });
            }
            if (url.includes('/api/stats')) {
                return mockRes({ success: true, revenue: 50000, bookings: 12, bottles: 8 });
            }
            if (url.includes('/api/admin')) {
                return mockRes({ success: true, items: [], message: "Mock Admin Success" });
            }
            
            // Default success for other calls
            return mockRes({ success: true, message: "Mock Success" });
        };

        // 3. Bypass LIFF Authentication Redirects
        window.addEventListener('load', () => {
            console.log("🚀 Static Demo Ready");
            // Inject mock profile into UI if needed immediately
            const userImg = document.getElementById('user-img');
            const userName = document.getElementById('user-name');
            if(userImg) userImg.src = 'https://www.w3schools.com/howto/img_avatar.png';
            if(userName) userName.innerText = 'Admin Demo';
        });
    </script>
"""

def init_factory():
    if not os.path.exists(V91_SRC_DIR):
        st.error(f"❌ ไม่พบ V91 ต้นฉบับที่ {V91_SRC_DIR}")
        return
    
    if os.path.exists(TEMPLATE_DIR):
        shutil.rmtree(TEMPLATE_DIR)
    os.makedirs(TEMPLATE_DIR)
    
    # Files to copy from master V91
    files_to_copy = [
        "index.html", "map_builder.html", "map_server.py", 
        "map_config.js", "worker.js", "wrangler.toml"
    ]
    
    for f in files_to_copy:
        src = os.path.join(V91_SRC_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(TEMPLATE_DIR, f))
        else:
            st.warning(f"⚠️ ไม่พบไฟล์ {f} ใน V91")
            
    # Create Default Start Builder script
    builder_script = """#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Starting Map Builder Server..."
python3 map_server.py
"""
    with open(os.path.join(TEMPLATE_DIR, "Start_Builder.command"), "w") as f:
        f.write(builder_script)
    os.chmod(os.path.join(TEMPLATE_DIR, "Start_Builder.command"), 0o755)
    
    st.success("✅ โหลดแม่พิมพ์ V91 และรีเซ็ตโรงงานสำเร็จ!")

# --- UI INTERFACE ---
st.title("🚀 V91 Store Factory")
st.markdown("ระบบผลิตร้านค้าจากแม่พิมพ์ **V91 (Clean Version)**")

if not os.path.exists(TEMPLATE_DIR) or not os.listdir(TEMPLATE_DIR):
    st.info("ยังไม่มีแม่พิมพ์ในโรงงานใหม่นี้ กรุณากดปุ่มเพื่อเริ่มเซ็ตอัพ")
    if st.button("🏗️ เริ่มเซ็ตอัพโรงงานจาก V91 (Init Factory)"):
        init_factory()
        st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ ตั้งค่าโรงงาน V91")
        if st.button("♻️ อัปเดตแม่พิมพ์จาก V91 ต้นฉบับ"):
            init_factory()
            st.rerun()
        st.divider()
        
        st.subheader("📁 โหลดข้อมูลร้านเดิม")
        existing_configs = [f.replace(".json", "") for f in os.listdir(CONFIGS_DIR) if f.endswith(".json")]
        if existing_configs:
            load_store = st.selectbox("เลือกร้านที่เคยทำไว้", ["--- เลือกร้าน ---"] + existing_configs)
            if load_store != "--- เลือกร้าน ---":
                if st.button(f"📥 โหลดข้อมูล {load_store}"):
                    with open(os.path.join(CONFIGS_DIR, f"{load_store}.json"), "r", encoding="utf-8") as f:
                        saved_data = json.load(f)
                        for k, v in saved_data.items():
                            st.session_state[k] = v
                    st.success(f"โหลดข้อมูลร้าน {load_store} สำเร็จ!")
                    st.rerun()
        else:
            st.info("ยังไม่มีข้อมูลร้านที่บันทึกไว้")
            
        st.divider()
        st.caption("Enhanced by Antigravity AI")

    def save_config(name, data):
        if not name: return
        filename = f"{name.replace(' ', '_')}.json"
        with open(os.path.join(CONFIGS_DIR, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    with st.container():
        st.subheader("📦 ข้อมูลสำหรับการผลิตแอป")
        col1, col2 = st.columns(2)
        store_name = col1.text_input("📍 ชื่อร้าน (Display Name)", placeholder="เช่น Velvet Bangsaen", key="store_name")
        
        tier_options = ["Starter (Tier 1)", "Professional (Tier 2/3)"]
        default_tier_idx = 0
        if "tier_sel" in st.session_state:
            try: default_tier_idx = tier_options.index(st.session_state["tier_sel"])
            except: pass
        tier_sel = col2.selectbox("🥇 เลือกระดับความเทพ (Tier)", tier_options, index=default_tier_idx, key="tier_sel")
        tier = 1 if "Starter" in tier_sel else 2

        st.markdown("---")
        st.subheader("🔑 การตั้งค่าระบบ (Cloudflare & Line)")
        c1, c2 = st.columns(2)
        worker_url = c1.text_input("🔗 Worker URL", value="https://v91-crm-production-worker.likesolution99.workers.dev", key="worker_url")
        pages_url = c2.text_input("🌐 Pages URL (Origin)", value="https://v91-crm-test-web.pages.dev", key="pages_url")
        
        c3, c4 = st.columns(2)
        liff_id = c3.text_input("🆔 LIFF ID", value="2009020696-z6Zlyc90", key="liff_id")
        line_token = c4.text_input("💬 Line OA Token (Long-lived)", type="password", key="line_token")
        
        c5, c6 = st.columns(2)
        manager_pass = c5.text_input("🔐 Manager Password (Login)", value="7777", key="manager_pass")
        thunder_key = c6.text_input("⚡ Thunder API Key (Slip Check)", type="password", key="thunder_key")

        st.markdown("---")
        st.subheader("💰 Pricing Defaults")
        c_price1, c_price2 = st.columns(2)
        extra_chair_price = c_price1.number_input("🪑 ราคาเก้าอี้เสริม (บาท/ตัว)", value=int(st.session_state.get('extra_chair_price', 0)), key="extra_chair_price")
        lock_table_price = c_price2.number_input("🔒 ราคาล็อคโต๊ะ (บาท)", value=int(st.session_state.get('lock_table_price', 500)), key="lock_table_price")

        st.markdown("---")
        st.subheader("🎨 รูปลักษณ์และธีม (Appearance)")
        
        theme_options = list(THEMES.keys()) + ["🎨 Custom"]
        default_theme_idx = 0
        if "theme_sel" in st.session_state:
            try: default_theme_idx = theme_options.index(st.session_state["theme_sel"])
            except: pass
            
        theme_sel = st.selectbox("เลือกธีมสีระดับพรีเมียม", theme_options, index=default_theme_idx, key="theme_sel")
        
        if theme_sel == "🎨 Custom":
            c1, c2, c3, c4 = st.columns(4)
            accent = c1.color_picker("Accent Color", st.session_state.get("accent", "#EAB308"), key="accent")
            bg = c2.color_picker("Background", st.session_state.get("bg", "#060a14"), key="bg")
            g1 = c3.color_picker("Grad Start", st.session_state.get("g1", "#1e3a8a"), key="g1")
            g2 = c4.color_picker("Grad End", st.session_state.get("g2", "#1e293b"), key="g2")
        else:
            selected_theme = THEMES[theme_sel]
            accent = selected_theme["accent"]
            bg = selected_theme["bg"]
            g1 = selected_theme["grad_start"]
            g2 = selected_theme["grad_end"]
            
            st.info(f"Theme Selected: {theme_sel}")
            st.markdown(f'<div style="display:flex; gap:10px;">'
                        f'<div style="width:30px;height:30px;background:{accent};border-radius:5px;border:1px solid white;"></div>'
                        f'<div style="width:30px;height:30px;background:{bg};border-radius:5px;border:1px solid white;"></div>'
                        f'<div style="width:30px;height:30px;background:linear-gradient(to right, {g1}, {g2});border-radius:5px;border:1px solid white;"></div>'
                        f'</div>', unsafe_allow_html=True)

    # Prepare data for saving
    current_config = {
        "store_name": store_name,
        "tier_sel": tier_sel,
        "worker_url": worker_url,
        "pages_url": pages_url,
        "liff_id": liff_id,
        "line_token": line_token,
        "manager_pass": manager_pass,
        "thunder_key": thunder_key,
        "extra_chair_price": extra_chair_price,
        "lock_table_price": lock_table_price,
        "theme_sel": theme_sel,
        "accent": accent,
        "bg": bg,
        "g1": g1,
        "g2": g2
    }

    col_btn1, col_btn2 = st.columns([1, 4])
    if col_btn1.button("💾 เซฟข้อมูลร้าน"):
        if store_name:
            save_config(store_name, current_config)
            st.success(f"💾 บันทึกข้อมูลร้าน {store_name} แล้ว!")
        else:
            st.error("กรุณาใส่ชื่อร้านก่อนเซฟ")

    if col_btn2.button("🔥 เริ่มกระบวนการผลิต (Execute Build V91)"):
        if not store_name:
            st.error("🚨 กรุณาระบุชื่อร้านก่อนเริ่มผลิต")
        else:
            save_config(store_name, current_config)
            with st.status("🏗️ กำลังสร้างแอปจากแม่พิมพ์ V91...", expanded=True) as status:
                # 1. Versioning Logic
                folders = [f for f in os.listdir(BASE_DIR) if f.startswith('V') and '_' in f]
                v_nums = []
                for f in folders:
                    match = re.search(r'V(\d+)', f)
                    if match: v_nums.append(int(match.group(1)))
                
                next_v = max(v_nums) + 1 if v_nums else 92
                folder_name = f"V{next_v}_{store_name.replace(' ', '_')}"
                target_path = os.path.join(BASE_DIR, folder_name)
                
                status.write(f"📁 สร้างโฟลเดอร์: {folder_name}")
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(TEMPLATE_DIR, target_path)

                # 2. Processing Files & Placeholders
                status.write("✏️ Injection: กำลังเขียน Config และชุดคำสั่ง...")
                for root, dirs, files in os.walk(target_path):
                    for f in files:
                        if f.startswith('.'): continue
                        p = os.path.join(root, f)
                        try:
                            with open(p, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            content = content.replace("{{SHOP_NAME}}", store_name)
                            content = content.replace("{{PORT}}", str(8000 + next_v))
                            content = content.replace("{{TIER}}", str(tier))
                            content = content.replace("{{WORKER_URL}}", worker_url.rstrip('/'))
                            content = content.replace("{{PAGES_URL}}", pages_url.rstrip('/'))
                            content = content.replace("{{LIFF_ID}}", liff_id)
                            content = content.replace("{{LINE_TOKEN}}", line_token)
                            content = content.replace("{{MANAGER_PASSWORD}}", manager_pass)
                            content = content.replace("{{THUNDER_API_KEY}}", thunder_key)
                            content = content.replace("{{EXTRA_CHAIR_PRICE}}", str(extra_chair_price))
                            content = content.replace("{{LOCK_TABLE_PRICE}}", str(lock_table_price))
                            content = content.replace("{{ACCENT_COLOR}}", accent)
                            content = content.replace("{{BG_COLOR}}", bg)
                            content = content.replace("{{GRAD_START}}", g1)
                            content = content.replace("{{GRAD_END}}", g2)
                            content = content.replace("{{FOLDER_NAME}}", folder_name)
                            
                            if f == "wrangler.toml":
                                content = re.sub(r'name\s*=\s*"[^"]*"', f'name = "store-v91-{store_name.lower().replace(" ","-")}"', content)
                            
                            with open(p, 'w', encoding='utf-8') as file:
                                file.write(content)
                            
                            if f.endswith(".command"):
                                os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
                        except Exception as e:
                            status.write(f"⚠️ ข้ามไฟล์ {f}: {str(e)}")

                status.write("🛠️ กำลังสร้างตัวอย่างออฟไลน์ (_index.html)...")
                index_p = os.path.join(target_path, "index.html")
                offline_p = os.path.join(target_path, "_index.html")
                
                if os.path.exists(index_p):
                    with open(index_p, 'r', encoding='utf-8') as f:
                        no_liff_content = f.read()
                    
                    current_mock = MOCK_FETCH_SCRIPT.replace("{{SHOP_NAME}}", store_name).replace("{{TIER}}", str(tier))
                    no_liff_content = re.sub(r'<body([^>]*)>', r'<body\1>' + current_mock, no_liff_content, flags=re.IGNORECASE)
                    
                    mock_init_logic = """
                    // --- MOCKED BY FACTORY V91 ---
                    console.log("⏩ Demo Mode: Bypassing LIFF");
                    profile = { 
                        userId: "U_DEMO_V91_" + Math.random().toString(36).substring(7), 
                        displayName: "V91 Admin Demo", 
                        pictureUrl: "https://www.w3schools.com/howto/img_avatar.png" 
                    };
                    document.getElementById('user-img').src = profile.pictureUrl;
                    document.getElementById('user-name').innerText = profile.displayName;
                    localStorage.setItem('last_uid', profile.userId);
                    updateLoading(100);
                    await checkUser();
                    if(typeof handleClaim === 'function' && myPhone) await handleClaim();
                    return; 
                    """
                    init_pattern = r"await\s+liff\.init\(.*?\);.*?await\s+checkUser\(.*?\);"
                    no_liff_content = re.sub(init_pattern, mock_init_logic, no_liff_content, flags=re.DOTALL)
                    
                    with open(offline_p, 'w', encoding='utf-8') as f:
                        f.write(no_liff_content)

                status.update(label="✅ ปั๊มแอปใหม่เสร็จสิ้น!", state="complete")
            
            st.success(f"🎉 สร้างร้านใหม่ชุด V91: **{store_name}** สำเร็จ!")
            st.markdown(f"👉 **Path:** `{folder_name}`")
            st.balloons()

    st.markdown("---")
    st.subheader("🛠️ อัปเดตงานเดิมด้วยชุดคำสั่ง V91")
    
    v_folders = [f for f in os.listdir(BASE_DIR) if f.startswith('V') and os.path.isdir(os.path.join(BASE_DIR, f))]
    target_v = st.selectbox("เลือกแอปเดิมที่ต้องการอัปเดตเป็น V91", ["--- เลือกโฟลเดอร์ ---"] + sorted(v_folders, reverse=True))

    if st.button("🛠️ อัปเดตไฟล์ HTML/Logic เข้าโฟลเดอร์ที่เลือก (Update to V91)"):
        if target_v == "--- เลือกโฟลเดอร์ ---":
            st.error("เลือกโฟลเดอร์ก่อนพี่")
        elif not store_name:
            st.error("ระบุชื่อร้านด้านบนด้วยครับ (เพื่อแมพชื่อลงไป)")
        else:
            with st.status(f"🛠️ กำลังแปลงร่าง {target_v} เป็น V91...", expanded=True) as status:
                repair_path = os.path.join(BASE_DIR, target_v)
                sync_files = ["index.html", "map_builder.html", "worker.js", "wrangler.toml", "map_server.py"]
                
                for f in sync_files:
                    src = os.path.join(TEMPLATE_DIR, f)
                    dst = os.path.join(repair_path, f)
                    if os.path.exists(src):
                        shutil.copy2(src, dst)
                        status.write(f"✅ อัปเดต {f}")
                        try:
                            with open(dst, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            content = content.replace("{{SHOP_NAME}}", store_name)
                            v_match = re.search(r'V(\d+)', target_v)
                            v_num = int(v_match.group(1)) if v_match else 0
                            content = content.replace("{{PORT}}", str(8000 + v_num))
                            content = content.replace("{{TIER}}", str(tier))
                            content = content.replace("{{WORKER_URL}}", worker_url.rstrip('/'))
                            content = content.replace("{{PAGES_URL}}", pages_url.rstrip('/'))
                            content = content.replace("{{LIFF_ID}}", liff_id)
                            content = content.replace("{{LINE_TOKEN}}", line_token)
                            content = content.replace("{{MANAGER_PASSWORD}}", manager_pass)
                            content = content.replace("{{THUNDER_API_KEY}}", thunder_key)
                            content = content.replace("{{EXTRA_CHAIR_PRICE}}", str(extra_chair_price))
                            content = content.replace("{{LOCK_TABLE_PRICE}}", str(lock_table_price))
                            content = content.replace("{{ACCENT_COLOR}}", accent)
                            content = content.replace("{{BG_COLOR}}", bg)
                            content = content.replace("{{GRAD_START}}", g1)
                            content = content.replace("{{GRAD_END}}", g2)
                            content = content.replace("{{FOLDER_NAME}}", target_v)
                            
                            with open(dst, 'w', encoding='utf-8') as file:
                                file.write(content)
                        except Exception as e:
                            status.write(f"⚠️ พลาดที่ไฟล์ {f}: {str(e)}")

                status.write("🛠️ รีเฟรช _index.html...")
                template_index_p = os.path.join(repair_path, "index.html")
                target_offline_p = os.path.join(repair_path, "_index.html")
                
                if os.path.exists(template_index_p):
                    with open(template_index_p, 'r', encoding='utf-8') as f:
                        no_liff_content = f.read()
                    current_mock = MOCK_FETCH_SCRIPT.replace("{{SHOP_NAME}}", store_name).replace("{{TIER}}", str(tier))
                    no_liff_content = re.sub(r'<body([^>]*)>', r'<body\1>' + current_mock, no_liff_content, flags=re.IGNORECASE)
                    
                    mock_init_logic = """
                    // --- MOCKED BY FACTORY ---
                    console.log("⏩ Demo Mode: Bypassing LIFF");
                    profile = { userId: "U_DEMO_V91", displayName: "V91 Demo", pictureUrl: "https://www.w3schools.com/howto/img_avatar.png" };
                    document.getElementById('user-img').src = profile.pictureUrl;
                    document.getElementById('user-name').innerText = profile.displayName;
                    localStorage.setItem('last_uid', profile.userId);
                    updateLoading(100);
                    await checkUser();
                    if(typeof handleClaim === 'function' && myPhone) await handleClaim();
                    return; 
                    """
                    init_pattern = r"await\s+liff\.init\(.*?\);.*?await\s+checkUser\(.*?\);"
                    no_liff_content = re.sub(init_pattern, mock_init_logic, no_liff_content, flags=re.DOTALL)
                    
                    with open(target_offline_p, 'w', encoding='utf-8') as f:
                        f.write(no_liff_content)

                status.update(label="✅ อัปเดตแอปเดิมเป็น V91 สำเร็จ!", state="complete")
                st.success(f"🛠️ อัปเดต Logic V91 เข้าไปที่ `{target_v}` เรียบร้อย! (ความลับผังโต๊ะยังอยู่ดี)")
                st.balloons()
