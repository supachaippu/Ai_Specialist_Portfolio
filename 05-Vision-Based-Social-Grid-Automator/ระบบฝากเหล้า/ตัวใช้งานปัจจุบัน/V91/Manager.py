import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# 🏭 V91 MASTER MANAGER - Antigravity Edition
# ระบบจัดการหลังบ้านเวอร์ชันใหม่สำหรับ V91 (Streamlit Hub)
st.set_page_config(
    page_title="V91 Master Controller",
    page_icon="🥃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: white;
    }
    .stApp {
        background: #0f172a;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- CFG INITIALIZATION ---
if 'worker_url' not in st.session_state:
    st.session_state.worker_url = "https://v91-crm-production-worker.likesolution99.workers.dev" coach = ""
if 'staff_uid' not in st.session_state:
    st.session_state.staff_uid = ""

# --- SIDEBAR: AUTH & SETTINGS ---
with st.sidebar:
    st.title("🥃 V91 Hub")
    st.image("https://r2.v86-th.com/v88/app_icon.png", width=80)
    st.markdown("---")
    
    worker_url = st.text_input("Worker API URL", value=st.session_state.worker_url)
    st.session_state.worker_url = worker_url.rstrip('/')
    
    staff_uid = st.text_input("Your Staff UID", value=st.session_state.staff_uid, help="UID ของคุณที่ลงทะเบียนเป็น Staff/Manager")
    st.session_state.staff_uid = staff_uid
    
    manager_pin = st.text_input("Admin PIN", type="password", value="7777")
    
    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.rerun()

# --- API WRAPPER ---
def api_request(method, path, data=None, params=None, is_form=False):
    url = f"{st.session_state.worker_url}{path}"
    if params is None: params = {}
    params['staff_uid'] = st.session_state.staff_uid
    
    try:
        if method == "GET":
            res = requests.get(url, params=params)
        elif method == "POST":
            if is_form:
                res = requests.post(url, data=data, params=params)
            else:
                if data is None: data = {}
                data['staff_uid'] = st.session_state.staff_uid
                res = requests.post(url, json=data)
        
        return res.json()
    except Exception as e:
        return {"success": False, "error": f"Connection Error: {str(e)}"}

# --- MAIN UI ---
if not st.session_state.staff_uid:
    st.warning("🚨 กรุณาระบุ **Staff UID** ในแถบด้านข้างเพื่อเริ่มจัดการระบบ")
    st.info("หากยังไม่มี UID ให้เข้าสู่ระบบที่หน้าเว็บด้วยเบราว์เซอร์ก่อน แล้วคัดลอก UID มาวางที่นี่")
    st.stop()

st.title("🚀 V91 Master Controller")
st.caption(f"Connected to: {st.session_state.worker_url}")

tabs = st.tabs(["📊 สถิติรวม", "📅 จัดการโต๊ะ & Event", "🥃 คลังเหล้า (Stock)", "📢 CRM & ทีมงาน"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    with st.spinner("กำลังโหลดข้อมูล Dashboard..."):
        dash = api_request("GET", "/api/admin/dashboard")
    
    if dash.get("success"):
        owner = dash["owner"]
        col1, col2, col3 = st.columns(3)
        col1.metric("🍾 ขวดเหล้าในสต็อก", f"{owner['total_bottles']} ขวด")
        col2.metric("🏆 แต้มสะสมรวมทั้งระบบ", f"{owner['total_points']:,} PTS")
        col3.metric("📅 วันสุดท้ายที่มีความเคลื่อนไหว", datetime.now().strftime("%d/%m/%Y"))
        
        st.markdown("---")
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📊 ผลงานพนักงาน (วันนี้)")
            perf_df = pd.DataFrame(owner["staff_performance"])
            if not perf_df.empty:
                st.bar_chart(perf_df.set_index("staff_name"))
            else:
                st.info("ยังไม่มีความเคลื่อนไหวจากพนักงานในวันนี้")
        
        with c2:
            st.subheader("🎂 สัปดาห์เกิดลูกค้า")
            bday_df = pd.DataFrame(dash["crm"]["birthday"])
            if not bday_df.empty:
                st.dataframe(bday_df[["name", "phone", "birthday"]], use_container_width=True)
            else:
                st.info("ไม่มีลูกค้าเกิดในสัปดาห์นี้")
    else:
        st.error(f"Error: {dash.get('error', 'Unknown Error')}")

# --- TAB 2: TABLE & EVENT MANAGEMENT ---
with tabs[1]:
    st.subheader("🎟️ จัดการอีเวนท์ & คอนเสิร์ต")
    st.info("ระบบนี้จะแทนที่หน้าจัดการเปิด-ปิดใน HTML เดิม ทำให้มึงคุมจากที่นี่ที่เดียวได้เลย")
    
    with st.expander("✨ แก้ไขข้อมูล Event ปัจจุบัน", expanded=True):
        col_ev1, col_ev2 = st.columns(2)
        ev_title = col_ev1.text_input("หัวข้อมินิคอนเสิร์ต / Event", placeholder="เช่น COCKTAIL Live in Velvet")
        ev_date = col_ev2.date_input("วันที่จัดงาน")
        ev_poster = st.text_input("URL รูปโปสเตอร์ (ทางเลือก)", placeholder="https://...")
        
        if st.button("🔥 อัปเดตข้อมูล Event"):
            # Mock form data send
            res = api_request("POST", "/api/admin/concert-event", data={
                "title": ev_title,
                "date": ev_date.strftime("%Y-%m-%d"),
                "staff_uid": st.session_state.staff_uid
            })
            if res.get("success"):
                st.success("✅ อัปเดตข้อมูล Event เรียบร้อยแล้ว! หน้าเว็บลูกค้าจะเปลี่ยนตามทันที")
            else:
                st.error(res.get("error"))

    st.markdown("---")
    st.subheader("📍 รายการจองโต๊ะลูกค้า")
    with st.spinner("กำลังดึงรายการจอง..."):
        bookings = api_request("GET", "/api/bookings-list")
    
    if isinstance(bookings, list):
        bk_df = pd.DataFrame(bookings)
        if not bk_df.empty:
            st.dataframe(bk_df.sort_values("date", ascending=False), use_container_width=True)
        else:
            st.info("ยังไม่มีรายการจอง")
    else:
        st.error("ไม่สามารถโหลดรายการจองได้")

# --- TAB 3: STOCK MANAGEMENT ---
with tabs[2]:
    st.subheader("📦 คลังเหล้าฝากทั้งหมด")
    with st.spinner("กำลังดึงข้อมูลคลัง..."):
        stock = api_request("GET", "/api/all-deposits")
    
    if isinstance(stock, list):
        df_stock = pd.DataFrame(stock)
        if not df_stock.empty:
            # Filter bar
            search = st.text_input("🔍 ค้นหา (ชื่อลูกค้า / ยี่ห้อ / รหัส)", "")
            if search:
                df_stock = df_stock[
                    df_stock['customer_name'].str.contains(search, case=False, na=False) |
                    df_stock['item_name'].str.contains(search, case=False, na=False) |
                    df_stock['deposit_code'].str.contains(search, na=False)
                ]
            
            st.write(f"พบรายการทั้งหมด {len(df_stock)} รายการ")
            st.dataframe(df_stock[["deposit_code", "customer_name", "item_name", "amount", "expiry_date", "staff_name"]], use_container_width=True)
        else:
            st.info("คลังเหล้าว่างเปล่า")

# --- TAB 4: CRM & BROADCAST ---
with tabs[3]:
    st.subheader("📢 ระบบ Broadcast (LINE)")
    st.markdown("ส่งข่าวสารหรือโปรโมชั่นหาลูกค้าตามกลุ่มเป้าหมาย")
    
    c_crm1, c_crm2 = st.columns([1, 2])
    with c_crm1:
        target = st.selectbox("🎯 กลุ่มเป้าหมาย", [
            "ทุกคน (Everyone)", 
            "คนที่มีเหล้าฝาก (Active Depositors)", 
            "คนที่มีคะแนนสูง (Whales)", 
            "คนเกิดเดือนนี้ (Birthday Month)"
        ])
        msg_format = st.radio("✨ รูปแบบข้อความ", ["Text Only", "Flex Message (Premium)"])
        
    with c_crm2:
        msg_text = st.text_area("✏️ ข้อความที่จะส่ง", height=150, placeholder="ระบุข้อความที่นี่...")
        if st.button("🚀 เริ่มส่ง Broadcast เดี๋ยวนี้"):
            if not msg_text:
                st.warning("กรุณาใส่ข้อความก่อนส่ง")
            else:
                with st.status("📡 กำลังส่งข้อความ...", expanded=True) as status:
                    # In real worker, we need target mapping
                    target_map = {
                        "ทุกคน (Everyone)": "everyone",
                        "คนที่มีเหล้าฝาก (Active Depositors)": "active_depositors",
                        "คนที่มีคะแนนสูง (Whales)": "whales",
                        "คนเกิดเดือนนี้ (Birthday Month)": "birthday"
                    }
                    res = api_request("POST", "/api/broadcast", data={
                        "target": target_map[target],
                        "message": msg_text,
                        "format": "text" if msg_format == "Text Only" else "flex",
                        "staff_uid": st.session_state.staff_uid
                    })
                    if res.get("success"):
                        status.update(label="✅ ส่งข้อความสำเร็จ!", state="complete")
                        st.balloons()
                    else:
                        st.error(res.get("error"))

    st.markdown("---")
    st.subheader("👥 จัดการทีมงาน (Staff Management)")
    with st.spinner("กำลังโหลดรายชื่อทีม..."):
        staff_data = api_request("GET", "/api/staff-list")
    
    if isinstance(staff_data, list):
        for s in staff_data:
            col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
            col_s1.write(f"👤 **{s['name']}** ({s['role']})")
            col_s2.write(f"สถานะ: {'🟢 Active' if s['status'] == 'active' else '🔴 Inactive'}")
            if s['status'] == 'pending' or s['status'] == 'inactive':
                if col_s3.button("อนุมัติ", key=f"app_{s['uid']}"):
                    api_request("POST", "/api/approve-staff", data={"uid": s['uid']})
                    st.rerun()
            elif col_s3.button("ระงับสิทธิ์", key=f"rev_{s['uid']}"):
                api_request("POST", "/api/revoke-staff", data={"uid": s['uid']})
                st.rerun()
