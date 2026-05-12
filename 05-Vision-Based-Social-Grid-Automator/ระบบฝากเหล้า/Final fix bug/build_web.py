import re
import os

# 1. ชื่อไฟล์ต้นฉบับของคุณ (ถ้าเปลี่ยนชื่อไฟล์ แก้ตรงนี้ได้เลย)
SOURCE_FILE = 'Final+fix bug copy.py'
OUTPUT_FILE = 'web_generator.html'

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ ไม่พบไฟล์ {SOURCE_FILE} กรุณาวางไฟล์นี้ไว้โฟลเดอร์เดียวกัน")
        return

    # อ่านไฟล์ต้นฉบับ
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # ดึงค่า HTML_RAW และ WORKER_RAW ออกมา
    print("⏳ กำลังดึงโค้ดต้นฉบับ...")
    html_match = re.search(r'HTML_RAW = r"""(.*?)"""', content, re.DOTALL)
    worker_match = re.search(r'WORKER_RAW = r"""(.*?)"""', content, re.DOTALL)

    if not html_match or not worker_match:
        print("❌ หาตัวแปร HTML_RAW หรือ WORKER_RAW ไม่เจอ")
        return

    # ฟังก์ชันแปลงให้เป็น JS String (Escape backticks และ backslashes)
    def escape_js(text):
        text = text.replace('\\', '\\\\') # Escape backslash ก่อน
        text = text.replace('`', '\\`')   # Escape backtick
        text = text.replace('${', '\\${') # Escape template literal placeholder
        text = text.replace('</script>', '<\\/script>') # ป้องกัน HTML พัง
        return text

    js_html = escape_js(html_match.group(1))
    js_worker = escape_js(worker_match.group(1))

    # โค้ดหน้าเว็บ Generator (HTML + Tailwind + JS Logic)
    web_app_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nightlife App Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <style>
        .preview-frame {{ width: 375px; height: 667px; border: 12px solid #1e293b; border-radius: 40px; overflow: hidden; position: relative; background: #000; transition: all 0.3s; }}
        input, select, textarea {{ background: #0f172a; border: 1px solid #334155; color: white; padding: 8px; border-radius: 8px; width: 100%; outline: none; }}
        input:focus {{ border-color: #eab308; }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-thumb {{ background: #475569; border-radius: 10px; }}
    </style>
</head>
<body class="bg-slate-900 text-slate-200 h-screen flex flex-col md:flex-row overflow-hidden font-sans">
    
    <div class="w-full md:w-1/2 h-full flex flex-col border-r border-slate-700 bg-slate-800">
        <div class="p-5 border-b border-slate-700 bg-slate-800 z-10 flex justify-between items-center">
            <h1 class="text-xl font-bold text-yellow-500">🚀 App Generator <span class="text-xs text-slate-500 bg-slate-900 px-2 py-1 rounded">Web Edition</span></h1>
        </div>
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
            
            <section class="space-y-3">
                <h3 class="font-bold text-white border-l-4 border-blue-500 pl-2">1. ร้าน & ระบบ</h3>
                <div class="grid grid-cols-1 gap-3">
                    <div><label class="text-xs text-slate-400">Shop Name</label><input id="shopName" value="MY BAR" oninput="updatePreview()"></div>
                    <div><label class="text-xs text-slate-400">D1 Database ID (Cloudflare)</label><input id="dbId" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"></div>
                </div>
            </section>

            <section class="space-y-3">
                <div class="flex justify-between"><h3 class="font-bold text-white border-l-4 border-pink-500 pl-2">2. ธีมสี (Theme)</h3><button onclick="randomTheme()" class="text-xs bg-slate-700 px-2 py-1 rounded hover:bg-slate-600">🎲 Random</button></div>
                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-slate-900 p-3 rounded border border-slate-700">
                        <label class="text-xs text-slate-500 block mb-1">Background</label>
                        <div class="flex gap-2"><input type="color" id="bgColor" value="#0f172a" class="h-8 w-10 p-0 border-0" oninput="updatePreview()"><span id="bgHex" class="text-xs self-center">#0f172a</span></div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded border border-slate-700">
                        <label class="text-xs text-slate-500 block mb-1">Accent</label>
                        <div class="flex gap-2"><input type="color" id="accentColor" value="#EAB308" class="h-8 w-10 p-0 border-0" oninput="updatePreview()"><span id="accentHex" class="text-xs self-center">#EAB308</span></div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded border border-slate-700 col-span-2">
                        <label class="text-xs text-slate-500 block mb-1">Gradient Button</label>
                        <div class="flex gap-2">
                            <input type="color" id="gradStart" value="#0e4296" class="h-8 w-full p-0 border-0" oninput="updatePreview()">
                            <input type="color" id="gradEnd" value="#1e293b" class="h-8 w-full p-0 border-0" oninput="updatePreview()">
                        </div>
                    </div>
                </div>
            </section>

            <section class="space-y-3">
                <h3 class="font-bold text-white border-l-4 border-green-500 pl-2">3. การเชื่อมต่อ (API)</h3>
                <div class="grid grid-cols-1 gap-2">
                    <input id="liffId" placeholder="LIFF ID">
                    <input id="workerUrl" placeholder="Worker URL">
                    <input id="r2Url" placeholder="R2 Public URL">
                    <input id="lineToken" placeholder="Line Channel Access Token">
                    <input type="password" id="mgrPass" placeholder="Manager Password">
                    <input id="holdTime" placeholder="Hold Time (20:30)" value="20:30">
                </div>
            </section>

            <button onclick="generate()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl shadow-lg transition active:scale-95 flex justify-center gap-2 items-center">
                <span>📦</span> Download Code (.zip)
            </button>
        </div>
    </div>

    <div class="hidden md:flex w-1/2 bg-black items-center justify-center relative bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]">
        <div id="previewFrame" class="preview-frame shadow-2xl">
            <div id="p-content" class="h-full flex flex-col p-6 transition-colors duration-300">
                <div class="flex justify-between items-start mb-8">
                    <div><h1 id="p-shop" class="text-2xl font-bold">MY BAR</h1><p id="p-sub" class="text-[10px] uppercase font-bold opacity-70">Nightlife System</p></div>
                    <div class="text-lg">🇹🇭</div>
                </div>
                <div class="space-y-4">
                    <div class="p-btn h-24 rounded-2xl flex flex-col items-center justify-center border border-white/10 shadow-lg cursor-pointer"><span class="text-2xl mb-1">📅</span><span class="font-bold">จองโต๊ะ</span></div>
                    <div class="p-btn h-24 rounded-2xl flex flex-col items-center justify-center border border-white/10 shadow-lg cursor-pointer"><span class="text-2xl mb-1">🥃</span><span class="font-bold">ระบบฝากเหล้า</span></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- INJECTED TEMPLATES ---
        const HTML_RAW = `{js_html}`;
        const WORKER_RAW = `{js_worker}`;
        // --------------------------

        const $ = id => document.getElementById(id);
        
        function updatePreview() {{
            const bg = $('bgColor').value;
            const accent = $('accentColor').value;
            const shop = $('shopName').value || "SHOP";
            
            $('p-content').style.backgroundColor = bg;
            $('p-content').style.color = isLight(bg) ? '#1e293b' : '#ffffff';
            $('p-shop').innerText = shop;
            $('p-sub').style.color = accent;
            
            const g1 = $('gradStart').value;
            const g2 = $('gradEnd').value;
            document.querySelectorAll('.p-btn').forEach(b => {{
                b.style.background = `linear-gradient(135deg, ${{g1}}, ${{g2}})`;
            }});
            
            $('bgHex').innerText = bg; $('accentHex').innerText = accent;
        }}

        function isLight(c) {{
            const hex = c.replace('#','');
            const r = parseInt(hex.substr(0,2),16), g = parseInt(hex.substr(2,2),16), b = parseInt(hex.substr(4,2),16);
            return ((r*299)+(g*587)+(b*114))/1000 > 155;
        }}

        function randomTheme() {{
            const rc = () => '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0');
            $('bgColor').value = rc(); $('accentColor').value = rc();
            $('gradStart').value = rc(); $('gradEnd').value = rc();
            updatePreview();
        }}

        async function generate() {{
            const shop = $('shopName').value || "MyShop";
            const dbId = $('dbId').value;
            if(!dbId) {{ alert("⚠️ ใส่ D1 Database ID ก่อนครับ"); return; }}
            
            // Prepare Variables
            const vars = {{
                "__SHOP__": shop, "__BG_COLOR__": $('bgColor').value,
                "__GRAD_START__": $('gradStart').value, "__GRAD_END__": $('gradEnd').value,
                "__TEXT_MAIN__": isLight($('bgColor').value) ? "#0f172a" : "#ffffff",
                "__TEXT_SUB__": isLight($('bgColor').value) ? "#475569" : "#94a3b8",
                "__ACCENT__": $('accentColor').value, "__LIFF__": $('liffId').value,
                "__WORKER__": $('workerUrl').value, "__R2_URL__": $('r2Url').value,
                "__HOLD_TIME__": $('holdTime').value, "__MGR_PASS__": $('mgrPass').value,
                "__RADIUS__": "16px", "__LAYOUT_CSS__": "", 
                "__BK_MSG__": JSON.stringify("Booking Confirmed: " + shop)
            }};
            
            // Replace HTML
            let h = HTML_RAW;
            for(const [k,v] of Object.entries(vars)) h = h.split(k).join(v||"");
            
            // Replace Worker
            let w = WORKER_RAW.replace("__MGR_PASS__", vars["__MGR_PASS__"]).replace("__LIFF__", vars["__LIFF__"]);
            
            // Create ZIP
            const zip = new JSZip();
            const f = zip.folder(`Output_${{shop.replace(/\\s+/g,'_')}}`);
            f.file("index.html", h);
            f.file("worker.js", w);
            f.file("wrangler.toml", `name="nightlife-app"\\nmain="worker.js"\\n[vars]\\nLINE_TOKEN="${{$('lineToken').value}}"\\n[[d1_databases]]\\nbinding="DB"\\ndatabase_name="db"\\ndatabase_id="${{dbId}}"\\n[[r2_buckets]]\\nbinding="BUCKET"\\nbucket_name="bucket"\\n[triggers]\\ncrons=["0 3 * * *"]`);
            f.file("d1_schema.sql", `CREATE TABLE IF NOT EXISTS staff_access (user_id TEXT PRIMARY KEY, name TEXT, status TEXT DEFAULT 'pending', role TEXT DEFAULT 'staff', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\\nCREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, deposit_code TEXT, staff_name TEXT, item_name TEXT, item_type TEXT, amount TEXT, remarks TEXT, image_key TEXT, status TEXT, expiry_date TEXT, owner_uid TEXT, owner_name TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);\\nCREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, staff_name TEXT, details TEXT, image_key TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);`);
            
            const content = await zip.generateAsync({{type:"blob"}});
            saveAs(content, `${{shop}}_System.zip`);
        }}
        
        updatePreview();
    </script>
</body>
</html>"""

    # บันทึกไฟล์ html
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(web_app_code)
    
    print(f"✅ สร้างไฟล์สำเร็จ: {OUTPUT_FILE}")
    print("👉 ดับเบิ้ลคลิกไฟล์ web_generator.html เพื่อใช้งานได้เลย!")

if __name__ == "__main__":
    main()