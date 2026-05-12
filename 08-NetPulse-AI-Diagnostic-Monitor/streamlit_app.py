import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import subprocess
import threading
from datetime import datetime
import io

# Set page config
st.set_page_config(page_title="Internet Diagnosis Pro", layout="wide", page_icon="📡")

# Constants
LOG_FILE = "internet_logs.csv"
CHECK_INTERVAL = 5
TARGET_PUBLIC = "8.8.8.8"

# --- Monitoring Section (Background Thread) ---
def get_gateway():
    try:
        output = subprocess.check_output(["netstat", "-rn"], text=True)
        for line in output.splitlines():
            if "default" in line:
                parts = line.split()
                if len(parts) > 1: return parts[1]
    except: pass
    return "192.168.1.1"

def get_wifi_info():
    """Get macOS WiFi signal info (Supports airport and wdutil)."""
    try:
        # Try airport legacy first
        cmd = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I"
        output = subprocess.check_output(cmd, shell=True, text=True)
        res = {l.split(":")[0].strip(): l.split(":")[1].strip() for l in output.splitlines() if ":" in l}
        if res: return {"ssid": res.get("SSID", "N/A"), "rssi": res.get("agrCtlRSSI", "0")}
    except: pass
    
    try:
        # Try wdutil (Sonoma+)
        cmd = "wdutil info"
        output = subprocess.check_output(cmd, shell=True, text=True)
        res = {l.split(":")[0].strip(): l.split(":")[1].strip() for l in output.splitlines() if ":" in l}
        return {"ssid": res.get("SSID", "N/A"), "rssi": res.get("RSSI", "0")}
    except:
        return {"ssid": "N/A", "rssi": "0"}

def ping_check(host):
    try:
        start = time.time()
        subprocess.check_output(["ping", "-c", "1", "-W", "1000", host], stderr=subprocess.STDOUT)
        return True, round((time.time() - start) * 1000, 2)
    except:
        return False, 0

def monitoring_loop():
    gateway = get_gateway()
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', encoding='utf-8-sig') as f:
            f.write("Timestamp,Public_Net,Gateway,Latency,SSID,RSSI,Status\n")

    while True:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pub_ok, lat = ping_check(TARGET_PUBLIC)
        gate_ok, _ = ping_check(gateway)
        wifi = get_wifi_info()
        
        status = "Online"
        if not pub_ok:
            status = "Lost Router Connection" if not gate_ok else "ISP Link Down (ค่ายเน็ตเสีย)"
        
        # Save with utf-8-sig so Excel on Mac/PC can read Thai characters
        with open(LOG_FILE, mode='a', encoding='utf-8-sig') as f:
            f.write(f"{ts},{'OK' if pub_ok else 'FAIL'},{'OK' if gate_ok else 'FAIL'},{lat},{wifi['ssid']},{wifi['rssi']},{status}\n")
        
        time.sleep(CHECK_INTERVAL)

if 'monitor_active' not in st.session_state:
    threading.Thread(target=monitoring_loop, daemon=True).start()
    st.session_state['monitor_active'] = True

# --- App UI ---
st.title("📡 ตัววิเคราะห์อาการเน็ตหลุด (Internet Diagnosis Pro)")

tab1, tab2 = st.tabs(["🔴 มอนิเตอร์ปัจจุบัน", "📁 อัปโหลด Log มาวิเคราะห์"])

with tab1:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        if not df.empty:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            last = df.iloc[-1]
            
            # Key Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Uptime", f"{( (df['Status'] == 'Online').sum() / len(df) * 100 ):.1f}%")
            m2.metric("สถานะปัจจุบัน", last['Status'], delta=None, delta_color="inverse" if last['Status'] != "Online" else "normal")
            m3.metric("ความหน่วง (ms)", last['Latency'])
            m4.metric("ความแรง Wi-Fi", f"{last['RSSI']} dBm")
            
            # Latency Chart
            fig = px.line(df.tail(100), x='Timestamp', y='Latency', title='ประวัติการแล็กล่าสุด (ms)', color_discrete_sequence=['#ff4b4b'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Failure Summary
            if (df['Status'] != 'Online').any():
                st.subheader("⚠️ ประวัติการหลุด")
                st.table(df[df['Status'] != 'Online'].tail(5)[['Timestamp', 'SSID', 'Status']])
        else:
            st.info("กำลังรอข้อมูลรอบแรก...")
    else:
        st.warning("⚠️ กำลังสร้างไฟล์ Log กรุณารอสักครู่...")

with tab2:
    st.subheader("📁 อัปโหลดไฟล์เพื่อวิเคราะห์เชิงลึก")
    st.write("คุณสามารถอัปโหลดไฟล์ `internet_logs.csv` หรือไฟล์ Log จาก Router (`.txt`) มาที่นี่")
    
    uploaded_file = st.file_uploader("เลือกไฟล์ Log", type=['csv', 'txt', 'log'])
    
    if uploaded_file:
        content = uploaded_file.getvalue()
        # Handle "Alien Language" encoding issues
        try:
            text = content.decode('utf-8-sig')
        except:
            text = content.decode('tis-620', errors='replace')
            
        is_router_log = False
        if uploaded_file.name.endswith('.csv'):
            # Analyze CSV with error handling
            try:
                df_up = pd.read_csv(io.StringIO(text), on_bad_lines='skip')
                st.success(f"โหลดไฟล์ {uploaded_file.name} สำเร็จ!")
                st.dataframe(df_up.head())
            except:
                is_router_log = True
        else:
            is_router_log = True
            
        if is_router_log:
            st.info("ตรวจพบไฟล์ Log (โหมดข้อความ) กำลังวิเคราะห์อาการ...")
            lines = text.splitlines()
            issues = []
            for line in lines:
                l_lower = line.lower()
                if 'down' in l_lower or 'fail' in l_lower or 'loss' in l_lower or 'disconnect' in l_lower:
                    # Translate common errors
                    msg = line
                    if 'loss of signal' in l_lower: msg += " ➔ [สายไฟเบอร์ขาด/แสงไม่พอ]"
                    if 'pppoe' in l_lower: msg += " ➔ [ค่ายเน็ตมีปัญหาทางเทคนิค]"
                    if 'reboot' in l_lower: msg += " ➔ [ไฟตกหรือเร้าเตอร์แฮงค์]"
                    issues.append(msg)
            
            if issues:
                st.error(f"🚩 ตรวจพบจุดที่น่าสงสัย {len(issues)} จุด:")
                for i in issues[-20:]: # Show last 20
                    st.write(f"• {i}")
            else:
                st.success("ไม่พบประวัติการหลุดในไฟล์ Log นี้ครับ")

# Auto refresh for tab1
if st.button("🔄 อัปเดตข้อมูลตอนนี้"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("💻 **สำหรับผู้ใช้ Mac:**")
st.sidebar.write("ถ้าเปิด CSV ใน Excel แล้วเป็นต่างดาว ให้ลองเปิดใน **Numbers** หรือรันแอปนี้แทนครับ ผมแก้เรื่อง Encoding ให้เรียบร้อยแล้ว")
