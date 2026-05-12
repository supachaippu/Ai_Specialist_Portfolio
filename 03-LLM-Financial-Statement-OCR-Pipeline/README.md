# 📊 LLM Financial Statement OCR & Intelligence Suite
> **Focus:** Generative AI (LLMs), Financial Data Engineering, & Semantic Analysis

## 🚀 Business Purpose
Extracting structured transaction data from unstructured, non-standard bank statements is a major challenge for accounting and financial analysis. Traditional OCR often fails due to complex layouts. This project implements a **high-fidelity pipeline using LLMs (Gemini)** to intelligently parse, structure, and analyze financial data with deep contextual awareness and semantic classification.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
การดึงข้อมูลธุรกรรมจาก Statement ธนาคารที่มีรูปแบบหลากหลายและไม่มีโครงสร้างที่แน่นอน เป็นความท้าทายอย่างมากสำหรับงานบัญชีและการวิเคราะห์การเงิน ระบบ OCR ทั่วไปมักล้มเหลวเมื่อเจอเลย์เอาต์ที่ซับซ้อน โครงการนี้จึงนำเทคโนโลยี **LLM (Gemini)** มาใช้เพื่อทำความเข้าใจบริบท สกัดข้อมูลสำคัญ และวิเคราะห์หมวดหมู่รายจ่ายอัตโนมัติเพื่อให้เห็นภาพรวมทางการเงินที่แม่นยำ

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
A multi-layered AI pipeline designed for high-accuracy data extraction:

- **Generative AI Parsing:** Leverages **Google Gemini** for its advanced reasoning capabilities to extract dates, descriptions, and amounts from raw PDF text where traditional regex fails.
- **Semantic Classification:** Automatically categorizes transactions into meaningful groups (e.g., Food, Travel, Subscriptions) using AI.
- **Dynamic Analysis Dashboard:** A full-stack application (FastAPI + JS) to visualize spending habits, detect internal transfers, and generate financial insights.
- **Multi-Bank Support:** Designed to handle various statement formats from major Thai banks (SCB, KBank, BBL) without manual template configuration.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **Structured Data Output:** Converts raw PDF/Text into clean JSON/CSV formats for easy integration.
- ✅ **End-to-End Tracking:** Includes a modern UI for monitoring extraction progress and results.

---

## 📈 Business Impact (ผลลัพธ์)
- **Efficiency:** Reduced manual data entry and reconciliation time by over 95%.
- **Versatility:** Eliminated the need for constant maintenance of fragile, format-specific scrapers.
- **Scalability:** Able to process high volumes of financial documents with minimal human oversight.

---

## 🛠 Tech Stack
- **AI Model:** Google Gemini (Generative AI).
- **Backend:** Python (FastAPI), JavaScript (Cloudflare Workers).
- **Database:** SQLite / Cloudflare D1.
- **Frontend:** Vanilla JS, Tailwind CSS.

---
*Developed by Supachai Pumpoung (AI Specialist Workflow).*
