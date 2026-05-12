# 📡 NetPulse AI Diagnostic Monitor
> **Focus:** Real-time Monitoring, Network Diagnostics, & Data Visualization

## 🚀 Business Purpose
Unstable internet connections can disrupt remote work, video production, and cloud-native workflows. Identifying whether a connectivity issue lies with the local hardware (Router), the Name Server (DNS), or the Internet Service Provider (ISP) is often confusing for non-technical users. This project provides a **real-time diagnostic dashboard** that pinpoints the exact point of failure, reducing troubleshooting time and technical frustration.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
การเชื่อมต่ออินเทอร์เน็ตที่ไม่เสถียรสามารถรบกวนการทำงานทางไกล, โปรดักชั่นวิดีโอ และการทำงานบนคลาวด์ การระบุว่าปัญหาเกิดจากอุปกรณ์ในบ้าน (Router), ระบบแปลชื่อ (DNS) หรือผู้ให้บริการ (ISP) มักเป็นเรื่องที่น่าปวดหัวสำหรับผู้ใช้ทั่วไป โครงการนี้จึงถูกพัฒนาขึ้นเพื่อเป็น **แดชบอร์ดวินิจฉัยปัญหาแบบเรียลไทม์** ที่ช่วยระบุจุดที่เกิดปัญหาได้อย่างแม่นยำ ช่วยลดเวลาในการหาสาเหตุและลดความหงุดหงิดในการใช้งาน

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
A lightweight monitoring engine built with **Python** and **Streamlit** for instant diagnostics:

- **Multi-Checkpoint Diagnostics:** Simultaneously pings three critical infrastructure points: the Local Gateway (Router), Public DNS, and Global IP (8.8.8.8) to isolate the connection bottleneck.
- **Real-time Visualization:** Uses **Plotly** to generate live latency charts, allowing users to visualize connection stability and jitter over time.
- **macOS System Integration:** Leverages system commands to read **RSSI (Signal Strength)** and noise levels directly from the Wi-Fi card for hardware-level monitoring.
- **Autonomous Logging:** Automatically logs all "Downtime Events" into a structured CSV format with precise timestamps and failure codes for long-term ISP quality analysis.
- **Log Analysis Engine:** Features a secondary tool to analyze uploaded router logs and identify recurring failure patterns.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **Live Connectivity Dashboard:** Visualizes network health every 5 seconds.
- ✅ **Smart Failure Attribution:** Tells you exactly if the problem is your Router, DNS, or ISP.
- ✅ **Wi-Fi Signal Analysis:** Monitors signal quality (RSSI) to detect local interference.
- ✅ **Event History Tracking:** Persistent logging of all outages for ISP accountability.

---

## 📈 Business Impact (ผลลัพธ์)
- **Troubleshooting Speed:** Users can identify and fix local network issues without calling external technical support.
- **Evidence-based reporting:** Provides hard data (logs/latency charts) for reporting recurring outages to ISPs.
- **Uptime Awareness:** Increases productivity by providing early warnings of degrading signal quality before total failure occurs.

---

## 🛠 Tech Stack
- **Language:** Python 3.9+
- **Frontend:** Streamlit.
- **Libraries:** Pandas, Plotly, Subprocess.
- **Monitoring:** ICMP Ping, Socket Handshakes.

---
*Developed for Network Reliability by Supachai Pumpoung (AI Specialist Workflow).*
