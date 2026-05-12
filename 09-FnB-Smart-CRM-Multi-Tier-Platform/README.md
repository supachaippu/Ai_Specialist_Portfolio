# 🏢 FnB Smart CRM Multi-Tier Platform
> **Focus:** SaaS Architecture, CRM Systems, & Rapid Deployment Engines

## 🚀 Business Purpose
For food and beverage (FnB) groups managing multiple venues, maintaining separate CRM and deposit systems for each location is operationally complex and expensive. This project provides a **Multi-Tier CRM Orchestrator** that allows a single manager to generate and deploy customized CRM instances for different venues, each with a tailored feature set (Basic to Premium), from a centralized configuration engine.

---

## 🇹🇭 จุดประสงค์ของโครงการ (Business Purpose)
สำหรับกลุ่มธุรกิจอาหารและเครื่องดื่ม (FnB) ที่บริหารจัดการหลายสาขา การรันระบบ CRM และระบบฝากของแยกกันในแต่ละร้านเป็นเรื่องที่ยุ่งยากและมีต้นทุนสูง โครงการนี้จึงถูกพัฒนาขึ้นเป็น **แพลตฟอร์มบริหารจัดการ CRM แบบ Multi-Tier** ที่ช่วยให้ผู้จัดการสามารถสร้าง (Generate) และติดตั้งระบบ CRM ที่ปรับแต่งตามความต้องการของแต่ละร้านได้จากศูนย์กลาง โดยมีฟีเจอร์ให้เลือกตั้งแต่ระดับพื้นฐานไปจนถึงระดับพรีเมียม

---

## 🛠 The Solution (สถาปัตยกรรมทางเทคนิค)
A scalable, generator-based architecture for rapid client onboarding:

- **Tiered Feature Orchestration:** Implements a logic-based tiering system where features (e.g., photo attachments, loyalty points, reward coupons) are dynamically toggled based on the venue's subscription level.
- **Config-Driven Deployment:** Uses a central `generator.html` tool to inject venue metadata and business rules into a `master_app.html` template, allowing for near-instant deployment of new client instances.
- **Client-Side Persistence:** Utilizes JSON-based profiles to manage venue metadata without the need for a complex central database for the orchestrator itself.
- **Responsive Web Architecture:** Built with high-fidelity Vanilla JavaScript and CSS3 to ensure a premium, app-like experience across all mobile and desktop devices.

---

## ✨ Key Features (คุณสมบัติเด่น)
- ✅ **Dynamic Instance Generator:** Create new venue-specific CRMs in seconds.
- ✅ **3-Tier Service Model:** 
    - **Tier 1 (Basic):** Essential deposit tracking.
    - **Tier 2 (Standard):** Adds visual verification (Photo capture).
    - **Tier 3 (Premium):** Full CRM with Points & Rewards.
- ✅ **Unified Management Interface:** A single dashboard to monitor all deployed venue profiles.
- ✅ **Modular Master Template:** A single codebase that supports all 3 tiers via conditional rendering.

---

## 📈 Business Impact (ผลลัพธ์)
- **Deployment Speed:** Reduced the time to onboard a new venue from days to minutes.
- **Scalability:** Easily manage 10+ venues from a single master template with zero code duplication.
- **Revenue Flexibility:** Enables tiered pricing models for software-as-a-service (SaaS) offerings.

---

## 🛠 Tech Stack
- **Frontend:** HTML5, CSS3 (Modern UI), Vanilla JavaScript.
- **Data Architecture:** JSON-based Configuration & Profiles.
- **Design Pattern:** Generator-Pattern for rapid scaling.

---
**Developed for scalable business operations by Supachai Pumpoung.**
