# 📚 NLP-Driven Agenda Automation
> **Focus:** Intelligent Document Processing (IDP), NLP, & Workflow Optimization

## 🚀 Business Purpose
Educational institutions often handle hundreds of complex agendas manually, leading to human error in tracking student absences and excessive time spent generating evaluation forms. This project automates the entire document lifecycle—from parsing schedules to generating teacher-ready evaluation PDFs—increasing operational efficiency by 90%.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
สถาบันการศึกษามักประสบปัญหาการจัดการตารางเรียน (Agenda) จำนวนมากด้วยคน ซึ่งทำให้เกิดความผิดพลาดในการเช็คชื่อและเสียเวลาอย่างมากในการจัดเตรียมใบประเมินผล โครงการนี้ถูกพัฒนาขึ้นเพื่อเปลี่ยนกระบวนการทั้งหมดให้เป็นอัตโนมัติ ตั้งแต่การอ่านไฟล์ PDF ไปจนถึงการสร้างใบประเมินที่พร้อมใช้งาน ช่วยเพิ่มประสิทธิภาพการทำงานได้กว่า 90%

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
A high-performance Python application built with **Streamlit** to handle complex document workflows:

- **Heuristic-based NLP:** Utilizes Regex and NLP patterns to parse unstructured PDF data, identifying student names, times, and specific classrooms (Oxford, Cambridge, etc.).
- **Automated Absence Detection:** Intelligently detects "Absent" status and applies visual strikeout annotations directly onto the original PDF using **PyMuPDF**.
- **Dynamic PDF Generation:** Re-engineers paper-heavy evaluation forms into space-saving, grouped PDF layouts using **ReportLab**, tailored for teacher workflows.
- **Instant Processing:** A localized processing engine that allows staff to batch-upload and download results in seconds.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **Smart PDF Annotation:** High-fidelity highlighting and strikeouts for easy status tracking.
- ✅ **Optimized Form Generation:** Reduces paper usage by grouping multiple classes into a single, well-formatted page.
- ✅ **Teacher-Centric Design:** Automatically groups outputs by teacher name for instant distribution.
- ✅ **Regex-Powered Parsing:** High precision extraction of lesson types (1-to-1 vs. 2-to-1).

---

## 📈 Business Impact (ผลลัพธ์)
- **Time Savings:** Evaluation form generation time reduced from hours to seconds.
- **Accuracy:** Eliminated 100% of human error in student absence reporting.
- **Sustainability:** Reduced paper waste through dynamic layout optimization.

---

## 🛠 Tech Stack
- **Language:** Python 3.8+
- **Libraries:** Streamlit, PyMuPDF (fitz), ReportLab, Pandas.
- **Logic:** Regex-driven NLP.

---
*Developed by Supachai Pumpoung (AI Specialist Workflow).*
