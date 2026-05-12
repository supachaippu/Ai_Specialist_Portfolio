# 💳 Edge-Native Smart Payment Portal
> **Focus:** Serverless Payments, OCR Multi-Bank Verification, & High-Speed Ticketing

## 🚀 Business Purpose
In high-traffic event environments, processing payments and verifying bank transfer slips manually is impossible. The **Smart Payment Portal** provides a decentralized, edge-native solution that handles ticket sales, authenticates bank transfers from major Thai banks (KBank, SCB, Krungsri), and issues digital receipts in real-time.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
ระบบพอร์ทัลชำระเงินอัจฉริยะแบบ Edge-Native พัฒนาขึ้นเพื่อรองรับการขายบัตรและการจองในอีเวนต์ที่มีทราฟฟิกสูง ระบบสามารถตรวจสอบสลิปโอนเงินอัตโนมัติจากธนาคารหลัก (KBank, SCB, Krungsri) และออกหลักฐานการชำระเงินได้ทันทีโดยไม่ต้องรอพนักงานตรวจสอบ ช่วยลดความผิดพลาดและเพิ่มความรวดเร็วในการบริการลูกค้า

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
- **Multi-Bank OCR Integration:** Intelligent parsing logic to validate transaction data across different bank slip formats.
- **Serverless Backend (Cloudflare Workers):** Processes payment logic at the network edge for sub-second response times.
- **Edge Data Persistence (D1 SQL):** Distributed SQL database for secure transaction logging and inventory management.
- **Secure Image Vault (R2):** Automated archiving of verified slips for auditing and fraud prevention.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **Instant Slip Verification:** Real-time auditing for KBank, SCB, and Krungsri slips.
- ✅ **Dynamic Pricing & Inventory:** Real-time ticket availability updates at the edge.
- ✅ **Fraud Prevention:** Signature-based verification and duplicate slip detection.
- ✅ **Mobile-First UI:** Optimized for seamless checkout experience on LINE LIFF.

---

## 📂 Project Structure
- `worker.js`: Core payment processing and OCR logic.
- `index.html`: High-conversion payment portal interface.
- `schema.sql`: Database schema for transaction and inventory tracking.
- `wrangler.toml`: Edge deployment configuration.

---
*Developed by Supachai Pumpoung (AI Specialist & System Architect).*
