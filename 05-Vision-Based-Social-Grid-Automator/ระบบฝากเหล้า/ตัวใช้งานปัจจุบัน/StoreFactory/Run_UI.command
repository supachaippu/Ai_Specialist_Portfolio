#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 กำลังเปิดหน้า Dashboard โรงงานปั๊มร้าน (V88 Streamlit Engine)..."
pip install streamlit --quiet
streamlit run App.py
read -p "กด Enter เพื่อปิด..."
