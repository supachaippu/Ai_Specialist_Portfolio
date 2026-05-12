# 🎬 Cloud-Native Video Content Pipeline (Opus & BLC)
> **Focus:** Serverless Orchestration, Content Engineering, & Automated Archiving

## 🚀 Business Purpose
In the fast-paced world of short-form video production, managing content at scale often leads to bottlenecks in quality control and archiving. This project provides a **full-cycle content pipeline** for the British Learning Centre (BLC), allowing teams to autonomously harvest AI-generated clips, review them via a professional approval portal, and automatically archive approved assets to Google Drive for permanent storage.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
ระบบจัดการวงจรคอนเทนต์วิดีโอแบบครบวงจรสำหรับ BLC โดยมีตั้งแต่ระบบสแกนคลิปจาก AI, หน้าจออนุมัติงานสำหรับลูกค้า (Approval Portal) และระบบสำรองข้อมูลอัตโนมัติไปยัง **Google Drive** เมื่อคลิปได้รับการอนุมัติ เพื่อแก้ปัญหาคอขวดในการจัดการสื่อจำนวนมากและการเก็บรักษาไฟล์ในระยะยาว

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
- **Omni Scan Tools:** JavaScript-based tools to harvest video metadata and source URLs directly from production platforms.
- **Approval Portal:** A premium web interface for clients to review videos, edit captions, and approve/reject content.
- **Edge Storage (Cloudflare R2):** High-performance object storage for video assets.
- **Serverless Backend (Cloudflare Workers):** Handles all API logic and integration triggers at the network edge.
- **Google Drive Integration:** Automated backup triggered via webhooks upon final approval.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **One-Click Harvesting:** Rapid ingestion of AI-generated clips.
- ✅ **Professional Approval Portal:** Streamlined client feedback loop.
- ✅ **Automated Archiving:** Seamless sync to Google Drive for all approved assets.
- ✅ **Interactive Metadata Editor:** Polishing content directly within the pipeline.

---
*Architected & Developed by Supachai Pumpoung (AI Specialist Workflow).*
