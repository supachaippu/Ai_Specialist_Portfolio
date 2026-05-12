# 🚀 Edge-Native Smart Venue CRM
> **Focus:** Edge Computing, Serverless Architecture, & Smart CRM Systems

## 🚀 Business Purpose
Venues in the nightlife and entertainment industry often struggle with inefficient booking systems, manual tracking of customer deposits (e.g., liquor bottles), and lack of real-time engagement. This project delivers an **Edge-Native CRM and Reservation Platform** that operates entirely on the cloud's edge, ensuring zero server maintenance, ultra-low latency, and a seamless customer experience via LINE LIFF.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
สถานประกอบการในอุตสาหกรรมบันเทิงและไนต์ไลฟ์ มักประสบปัญหากับระบบจองที่ไม่มีประสิทธิภาพ การติดตามของฝากลูกค้า (เช่น ขวดเหล้า) ที่ต้องใช้มือจด และการขาดระบบเชื่อมต่อกับลูกค้าแบบเรียลไทม์ โครงการนี้จึงนำเสนอ **แพลตฟอร์ม CRM และระบบจองแบบ Edge-Native** ที่ทำงานบน Edge ของคลาวด์ทั้งหมด ทำให้ระบบไม่ล่ม โหลดเร็ว และใช้งานง่ายผ่าน LINE LIFF

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
A high-performance, decoupled architecture engineered for extreme scalability:

- **Edge Runtime (Cloudflare Workers):** Executes business logic globally at the edge, providing sub-100ms response times for all API calls.
- **Serverless SQL (D1):** Manages complex relational data, including customer profiles, bottle deposits, and seating maps, with zero infrastructure overhead.
- **LINE LIFF Integration:** Provides a mobile-first, "no-app" customer portal for managing bookings, checking deposits, and redeeming loyalty points.
- **Dynamic Seating Maps:** Implements real-time seating availability and VIP tier management via a custom JavaScript engine.
- **Automated Notifications:** Uses event-driven logic to send instant **LINE Flex Messages** for bottle deposit updates or booking confirmations.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **Smart Bottle Depository:** Digital tracking of customer assets with real-time LINE updates.
- ✅ **Real-time Seating Maps:** Interactive maps with zone-based pricing and VIP management.
- ✅ **Integrated Customer Wallet:** A self-service portal for customers within the LINE ecosystem.
- ✅ **Granular Access Control:** Separated interfaces and permissions for Staff vs. Managers.

---

## 📈 Business Impact (ผลลัพธ์)
- **Operations Efficiency:** Automated bottle tracking reduced manual logging time and errors.
- **Customer Engagement:** Direct marketing and notification channel via LINE significantly increased repeat visits.
- **Technical Excellence:** Zero server maintenance costs and 99.99% availability under high load.

---

## 🛠 Tech Stack
- **Backend:** JavaScript (Cloudflare Workers).
- **Database:** Cloudflare D1 (SQL).
- **Frontend:** Vanilla JS, Tailwind CSS, LINE LIFF SDK.
- **Media:** Cloudflare R2 (Object Storage).

---
*Architected for High Performance & Extreme Scalability by Supachai Pumpoung.*
