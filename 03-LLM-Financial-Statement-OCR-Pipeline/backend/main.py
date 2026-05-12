from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
import PyPDF2

import sqlite3
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Statement Parser API")

# Allow Frontend (Local UI) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("statement_tracker.db")
    c = conn.cursor()
    # ตารางเก็บความจำ AI (Memory Cache)
    c.execute('''CREATE TABLE IF NOT EXISTS memory_cache 
                 (group_name TEXT PRIMARY KEY, tag TEXT)''')
    # ตารางเก็บประวัติรายการทั้งหมด
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, amount REAL, description TEXT, 
                  group_name TEXT, type TEXT, tag TEXT)''')
    conn.commit()
    conn.close()

init_db()

class TransactionItem(BaseModel):
    date: str
    amount: float
    description: str
    group_name: str
    type: str
    tag: str

class SaveRequest(BaseModel):
    transactions: List[TransactionItem]

@app.post("/api/save-transactions")
async def save_transactions(data: SaveRequest):
    conn = sqlite3.connect("statement_tracker.db")
    c = conn.cursor()
    
    saved_count = 0
    for tx in data.transactions:
        # 1. บันทึกประวัติ
        c.execute('''INSERT INTO transactions (date, amount, description, group_name, type, tag) 
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                  (tx.date, tx.amount, tx.description, tx.group_name, tx.type, tx.tag))
        
        # 2. สอน AI (Update Memory Cache) ทับของเดิม
        c.execute('''INSERT OR REPLACE INTO memory_cache (group_name, tag) 
                     VALUES (?, ?)''', (tx.group_name, tx.tag))
        saved_count += 1
                     
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"บันทึกสำเร็จ {saved_count} รายการ พร้อมอัปเดตสมองจำ AI!"}

@app.get("/")
def read_root():
    return {"message": "API is running. Ready to parse statements."}

@app.post("/api/parse-statement")
async def parse_statement(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    import pdfplumber
    import json
    from google import genai
    from google.genai import types
    
    # Read the uploaded file into memory
    pdf_bytes = await file.read()
    pdf_file = io.BytesIO(pdf_bytes)
    
    full_text = ""
    
    try:
        with pdfplumber.open(pdf_file, password=password or "") as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    full_text += extracted + "\n"
    except Exception as e:
        if 'Password' in str(e) or 'password' in str(e).lower():
            raise HTTPException(status_code=401, detail="รหัสผ่านไม่ถูกต้อง (Incorrect Password)")
        else:
            raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการเปิดไฟล์ PDF: {str(e)}")

    if not full_text.strip():
        raise HTTPException(status_code=400, detail="ไม่พบข้อความในไฟล์ PDF หรือไฟล์อาจจะเป็นรูปภาพ")

    transactions = []
    
    # Universal AI Parsing using Gemini
    try:
        # Initialize Gemini Client
        # API Key provided by User
        client = genai.Client(api_key="YOUR_GEMINI_API_KEY_HERE")
        
        prompt = f"""
คุณคือนักบัญชีอัจฉริยะ หน้าที่ของคุณคือดึงข้อมูลรายการเดินบัญชี (Transactions) จากข้อความ Raw Text ของ Statement ธนาคาร (รองรับทุกธนาคารในไทย เช่น SCB, KBANK, BBL, KTB ฯลฯ)

1. ดึงข้อมูลทุกรายการที่มีการเคลื่อนไหว (เงินเข้า และ เงินออก)
2. จัดหมวดหมู่ให้แต่ละรายการ โดยเลือกจากหมวดหมู่นี้เท่านั้น: ['อาหาร/ของใช้', 'เดินทาง/เติมเงิน', 'ช้อปปิ้ง', 'ค่าใช้จ่าย/บิล', 'ยอดขาย (แม่มณี)', 'รับเงินโอน', 'โอนเงินออก', 'อื่นๆ']
   - ถ้าเป็นเงินเข้า (Income) ให้ตั้ง type เป็น "income" และมักจะคู่กับหมวด 'รับเงินโอน', 'ยอดขาย' หรือ 'อื่นๆ'
   - ถ้าเป็นเงินออก (Expense) ให้ตั้ง type เป็น "expense" และ amount ต้องติดลบ (-) และคู่กับหมวด 'โอนเงินออก', 'อาหาร/ของใช้', 'ช้อปปิ้ง', ฯลฯ
3. สกัดชื่อกลุ่ม (group_name) สั้นๆ เพื่อใช้จัดกลุ่มรายการที่คล้ายกัน เช่น 'PromptPay', '7-ELEVEN', 'MaeManee', 'ร้านถุงเงิน' (ตัดพวกตัวเลขหรือรหัสสาขาทิ้งไป)

ข้อความจาก Statement:
{full_text}

ให้ตอบกลับเป็นโครงสร้าง JSON Array เท่านั้น ห้ามมีคำอธิบายอื่นผสม:
[
  {{
    "date": "01/05/2026",
    "amount": -150.00,
    "description": "7-ELEVEN สาขา 1234",
    "group_name": "7-ELEVEN",
    "type": "expense",
    "tag": "อาหาร/ของใช้"
  }}
]
"""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        # Parse the JSON response from Gemini
        response_text = response.text.strip()
        print("--- GEMINI RAW OUTPUT ---")
        print(response_text)
        print("-------------------------")
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        transactions = json.loads(response_text)
        if isinstance(transactions, dict):
            # Try to unpack if it wrapped in a dictionary
            for key in transactions.keys():
                if isinstance(transactions[key], list):
                    transactions = transactions[key]
                    break
        
    except json.JSONDecodeError:
         raise HTTPException(status_code=500, detail="AI วิเคราะห์ข้อมูลสำเร็จ แต่รูปแบบข้อมูลที่ส่งกลับมาไม่ถูกต้อง")
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการให้ AI วิเคราะห์: {str(e)}")
    
    if not transactions:
        raise HTTPException(status_code=400, detail="ไม่พบข้อมูลรายการโอนเงินในไฟล์นี้ หรือรูปแบบไฟล์อ่านยากเกินไป")
    
    return {
        "status": "success",
        "message": "อ่านไฟล์ PDF สำเร็จ!",
        "filename": file.filename,
        "transactions": transactions
    }
