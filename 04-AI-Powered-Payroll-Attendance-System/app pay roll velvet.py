import streamlit as st
import pandas as pd
import json
import sys
import subprocess
from streamlit.web import cli as stcli

# ==========================================
# 1. ส่วนของ HTML TEMPLATE (V35 Clean Version)
# ==========================================
html_template = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{shop_name}} Payroll System</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xlsx-js-style@1.2.0/dist/xlsx.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;800&display=swap');
        body {{ font-family: 'Sarabun', sans-serif; background-color: #f1f5f9; padding: 20px; color: #334155; }}
        .container {{ max-width: 1250px; margin: 0 auto; background: white; padding: 35px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
        h1 {{ margin-bottom: 20px; text-align: center; color: #0f172a; font-weight: 800; }}
        .upload-row {{ display: flex; gap: 20px; justify-content: center; margin-bottom: 30px; flex-wrap: wrap; }}
        .upload-card {{ border: 2px dashed #cbd5e1; padding: 25px; border-radius: 10px; width: 42%; text-align: center; cursor: pointer; transition: 0.2s; background: #f8fafc; position: relative; }}
        .upload-card:hover {{ border-color: #2563eb; background: #eff6ff; }}
        .upload-card.active {{ border-color: #16a34a; background: #f0fdf4; border-style: solid; }}
        .btn {{ padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; transition: 0.2s; }}
        .btn-primary {{ background-color: #2563eb; color: white; }}
        .btn-outline {{ background: white; border: 1px solid #2563eb; color: #2563eb; padding: 6px 12px; font-size: 14px; margin-top: 8px; }}
        .table-responsive {{ overflow-x: auto; margin-top: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; background: white; }}
        th, td {{ border-bottom: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
        th {{ background-color: #f8fafc; font-weight: 600; color: #475569; }}
    </style>
</head>
<body>
<div class="container">
    <h1>💰 {{shop_name_thai}} Payroll</h1>
    <div class="upload-row">
        <label class="upload-card" id="box-db">
            <span style="font-size:30px">📂</span><br>
            <b>1. อัปเดตรายชื่อ (Excel)</b>
            <input type="file" id="fileDB" accept=".xlsx, .xls" style="display:none;">
            <span id="name-db" style="display:block; margin-top:8px; color:#16a34a; font-weight:bold;"></span>
            <button class="btn-outline" onclick="event.preventDefault(); downloadTemplate()">📥 โหลดฟอร์ม</button>
        </label>
        <label class="upload-card" id="box-pdf">
            <span style="font-size:30px">📄</span><br>
            <b>2. ไฟล์สแกนนิ้ว (PDF)</b>
            <input type="file" id="filePDF" accept=".pdf" style="display:none;">
            <span id="name-pdf" style="display:block; margin-top:8px; color:#16a34a; font-weight:bold;"></span>
        </label>
    </div>
    <div style="text-align:center;">
        <button id="calcBtn" class="btn btn-primary" onclick="startCalculation()" disabled>🚀 เริ่มคำนวณเงินเดือน</button>
        <button id="exportBtn" class="btn" style="background-color:#16a34a; color:white; display:none; margin-left:10px;" onclick="exportFullExcel()">📥 ดาวน์โหลด Excel</button>
    </div>
    <div id="statusMsg" style="text-align:center; margin-top:15px; font-weight:bold; color:#16a34a;"></div>
    <div id="resultArea" style="display:none; margin-top:20px;">
        <div class="table-responsive">
            <table id="dailyTable">
                <thead><tr><th>วันที่</th><th>ชื่อ</th><th>เข้า</th><th>ออก</th><th>สาย</th><th>หมายเหตุ</th></tr></thead>
                <tbody id="dailyBody"></tbody>
            </table>
        </div>
    </div>
</div>
<script>
    const DEFAULT_DB = {default_db_json};
    let LOCAL_DB = JSON.parse(JSON.stringify(DEFAULT_DB));
    let pdfFile = null;
    let DAILY_DATA = [];

    document.getElementById('fileDB').addEventListener('change', function(e) {{
        const reader = new FileReader();
        reader.onload = (ev) => {{
            const wb = XLSX.read(new Uint8Array(ev.target.result), {{type:'array'}});
            const arr = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
            LOCAL_DB = {{}};
            arr.forEach(r => LOCAL_DB[r.ID] = {{name:r.NickName, role:r.Role||'Service'}});
            document.getElementById('box-db').classList.add('active');
            document.getElementById('name-db').innerText = e.target.files[0].name;
        }};
        reader.readAsArrayBuffer(e.target.files[0]);
    }});

    document.getElementById('filePDF').addEventListener('change', function(e) {{
        pdfFile = e.target.files[0];
        if(pdfFile) {{
            document.getElementById('box-pdf').classList.add('active');
            document.getElementById('name-pdf').innerText = pdfFile.name;
            document.getElementById('calcBtn').disabled = false;
        }}
    }});

    async function startCalculation() {{
        document.getElementById('statusMsg').innerText = '⏳ กำลังประมวลผล...';
        try {{
            const data = await pdfFile.arrayBuffer();
            const pdf = await pdfjsLib.getDocument({{data}}).promise;
            const raw = [];
            const nameToId = {{}};
            for(let id in LOCAL_DB) nameToId[LOCAL_DB[id].name.toLowerCase().trim()] = id;

            for(let i=1; i<=pdf.numPages; i++) {{
                const page = await pdf.getPage(i);
                const content = await page.getTextContent();
                const textLine = content.items.map(item => item.str).join(' ');
                const m = textLine.match(/(\d{{1,2}})[-/](\d{{1,2}})[-/](\d{{2,4}})\s+(\d{{1,2}}):(\d{{2}})/g);
                if(m) {{
                    m.forEach(matchStr => {{
                        const tsMatch = matchStr.match(/(\d{{1,2}})[-/](\d{{1,2}})[-/](\d{{2,4}})\s+(\d{{1,2}}):(\d{{2}})/);
                        const namePart = textLine.split(matchStr)[0].split(' ').pop().toLowerCase();
                        if(nameToId[namePart]) {{
                            let yr = parseInt(tsMatch[3]); if(yr<100) yr+=2000;
                            raw.push({{ id: nameToId[namePart], ts: new Date(yr, tsMatch[2]-1, tsMatch[1], tsMatch[4], tsMatch[5]) }});
                        }}
                    }});
                }}
            }}
            renderFinal(raw);
            document.getElementById('statusMsg').innerText = '✅ เสร็จสิ้น';
            document.getElementById('resultArea').style.display = 'block';
            document.getElementById('exportBtn').style.display = 'inline-block';
        }} catch(e) {{ alert(e.message); }}
    }}

    function renderFinal(raw) {{
        const tb = document.getElementById('dailyBody'); tb.innerHTML = '';
        raw.forEach(r => {{
            tb.innerHTML += `<tr><td>${{r.ts.toLocaleDateString()}}</td><td>${{LOCAL_DB[r.id].name}}</td><td>${{r.ts.toLocaleTimeString()}}</td><td>-</td><td>-</td><td>-</td></tr>`;
        }});
    }}

    function downloadTemplate() {{
        const arr = [{{ID:1, NickName:'Bart', Role:'Service', Salary:15000}}];
        const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(arr), "Sheet1");
        XLSX.writeFile(wb, "Template.xlsx");
    }}
</script>
</body>
</html>
"""

# ==========================================
# 2. STREAMLIT GUI (หน้าจอตัวสร้าง)
# ==========================================
def run_app():
    st.set_page_config(page_title="Payroll Generator", page_icon="⚙️")
    st.title("⚙️ Payroll WebApp Generator")
    
    with st.sidebar:
        st.header("ตั้งค่าร้านค้า")
        shop_id = st.text_input("ID ร้าน (ภาษาอังกฤษ)", value="velvet")
        shop_thai = st.text_input("ชื่อร้าน (แสดงผล)", value="Velvet Bangsaen")

    st.header("1. อัปโหลด Excel พนักงาน")
    uploaded_file = st.file_uploader("เลือกไฟล์พนักงาน (.xlsx)", type=['xlsx'])

    db_json = "{}"
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        db_dict = {str(r['ID']): {"name": r['Name'], "role": r['Role']} for _, r in df.iterrows()}
        db_json = json.dumps(db_dict, ensure_ascii=False)
        st.success(f"โหลดข้อมูลพนักงาน {len(db_dict)} คนเรียบร้อย")

    if st.button("🛠️ สร้างไฟล์ index.html"):
        final_html = html_template.replace("{{shop_name}}", shop_id)\
                                  .replace("{{shop_name_thai}}", shop_thai)\
                                  .replace("{default_db_json}", db_json)
        st.download_button("📥 ดาวน์โหลดไฟล์", final_html, f"index_{shop_id}.html", "text/html")

# ==========================================
# 3. ส่วนที่ทำให้รันด้วย F5 ได้ (IDLE Run Mode)
# ==========================================
if __name__ == "__main__":
    if "streamlit" in sys.argv[0] or (len(sys.argv) > 1 and sys.argv[1] == "run"):
        run_app()
    else:
        # สั่งรันตัวเองผ่าน streamlit cli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())