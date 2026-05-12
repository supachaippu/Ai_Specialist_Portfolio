#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Starting V91 Store Factory UI..."
/usr/bin/python3 -m streamlit run App.py --server.port 8502
