# 🕒 Velvet AI Attendance & Payroll System
> **Focus:** Computer Vision (OCR), Financial Automation, & Workforce Management

## 🚀 Business Purpose
Managing staff attendance and payroll in the hospitality industry is often plagued by manual errors and time theft. **Velvet AI Attendance** solves this by using **Computer Vision (OCR)** to verify work hours directly from photos of attendance logs, automatically calculating wages, and generating professional payroll reports for the Velvet Bangsaen venue.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
ระบบบริหารจัดการเวลาเข้างานและคำนวณเงินเดือนสำหรับร้าน Velvet Bangsaen โดยใช้เทคโนโลยี **Computer Vision (OCR)** ในการอ่านค่าเวลาจากบันทึกการทำงานจริง เพื่อป้องกันความผิดพลาดจากการคีย์ข้อมูลด้วยมือ และประมวลผลเป็นรายงาน Payroll อัตโนมัติ ช่วยลดเวลาการทำงานฝ่ายบุคคลลงอย่างมหาศาล

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
- **AI-Driven Time Tracking:** Uses Gemini/Tesseract to extract check-in/out times from physical logs or digital photos.
- **Automated Payroll Engine:** Python-based logic to calculate daily wages, overtime, and deductions based on extracted time data.
- **D1 Database Persistence:** Securely stores staff logs and access roles on Cloudflare's serverless SQL database.
- **Bilingual Reporting:** Generates professional PDF/HTML payroll statements in both Thai and English.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **OCR Verification:** 100% automated extraction of work hours from image data.
- ✅ **One-Click Payroll:** Converts a month of attendance data into a ready-to-pay report in seconds.
- ✅ **Edge-Native Deployment:** Runs on Cloudflare Workers for ultra-fast performance and scalability.
- ✅ **Role-Based Access:** Managed staff access and manager approval workflows.

---

## 📂 Project Structure
- `บันทึกเวลางาน velvet.py`: Core logic for attendance tracking and OCR integration.
- `payroll_generator.py`: Automated wage calculation and report generation.
- `attendance_d1_system/`: Backend architecture using Cloudflare Workers & D1 SQL.
- `pay roll velvet.html`: Interactive dashboard for payroll management.

---
*Engineering Excellence in Workforce Automation by Supachai Pumpoung.*
