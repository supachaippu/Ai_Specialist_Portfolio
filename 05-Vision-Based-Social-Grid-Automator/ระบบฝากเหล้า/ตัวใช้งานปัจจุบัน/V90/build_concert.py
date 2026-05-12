import json

# ==========================================
# 1. ตั้งค่าราคาและเงื่อนไขคอนเสิร์ต (Pricing & Details)
# ==========================================
CONCERT_DETAILS = {
    "extra_chair_price": 200,
    "lock_table_price": 500,
    
    # ราคาตามขนาดโต๊ะ VVIP
    "ticket_price_vvip_2": 0, 
    "ticket_price_vvip_4": 4000, 
    "ticket_price_vvip_6": 6000,
    
    # ราคาตามขนาดโต๊ะ VIP
    "ticket_price_vip_2": 0, 
    "ticket_price_vip_4": 3000, 
    "ticket_price_vip_6": 4500,
    
    # ราคาตามขนาดโต๊ะ Normal
    "ticket_price_normal_2": 0, 
    "ticket_price_normal_4": 2000, 
    "ticket_price_normal_6": 3000,
    
    # ราคาตามขนาดโต๊ะ Small (โต๊ะยืน)
    "ticket_price_small_2": 1000, 
    "ticket_price_small_4": 0, 
    "ticket_price_small_6": 0,
    
    # สิทธิพิเศษที่จะโชว์ให้ลูกค้าเห็น
    "privilege_vvip": "โซฟาติดขอบเวทีสุดเอ็กซ์คลูซีฟ",
    "privilege_vip": "มองเห็นเวทีชัดเจน นั่งสบาย",
    "privilege_normal": "โต๊ะนั่งชิลๆ วิวดี",
    "privilege_small": "โต๊ะยืนสายปาร์ตี้มันส์ๆ"
}

# ==========================================
# 2. ตั้งค่าผังโต๊ะ (Table Layout)
# พิกัด x_position, y_position คือ % บนหน้าจอ (1 ถึง 100)
# ==========================================
TABLES = {
    "1": [ # ชั้น 1
        {"id": "1", "table_number": "VVIP1", "table_type": "VVIP", "capacity": 6, "x_position": 40, "y_position": 18, "is_available": True, "allow_extra_chairs": True, "max_extra_chairs": 2},
        {"id": "2", "table_number": "VVIP2", "table_type": "VVIP", "capacity": 6, "x_position": 50, "y_position": 18, "is_available": True, "allow_extra_chairs": True, "max_extra_chairs": 2},
        {"id": "3", "table_number": "VVIP3", "table_type": "VVIP", "capacity": 6, "x_position": 60, "y_position": 18, "is_available": True, "allow_extra_chairs": True, "max_extra_chairs": 2},
        
        {"id": "4", "table_number": "VIP1", "table_type": "VIP", "capacity": 4, "x_position": 30, "y_position": 30, "is_available": True, "allow_extra_chairs": True, "max_extra_chairs": 1},
        {"id": "5", "table_number": "VIP2", "table_type": "VIP", "capacity": 4, "x_position": 45, "y_position": 30, "is_available": True, "allow_extra_chairs": True, "max_extra_chairs": 1},
        {"id": "6", "table_number": "VIP3", "table_type": "VIP", "capacity": 4, "x_position": 60, "y_position": 30, "is_available": True, "allow_extra_chairs": True, "max_extra_chairs": 1},
        
        {"id": "7", "table_number": "N1", "table_type": "Normal", "capacity": 4, "x_position": 20, "y_position": 45, "is_available": True, "allow_extra_chairs": False, "max_extra_chairs": 0},
        {"id": "8", "table_number": "N2", "table_type": "Normal", "capacity": 4, "x_position": 35, "y_position": 45, "is_available": True, "allow_extra_chairs": False, "max_extra_chairs": 0},
        {"id": "9", "table_number": "N3", "table_type": "Normal", "capacity": 4, "x_position": 50, "y_position": 45, "is_available": True, "allow_extra_chairs": False, "max_extra_chairs": 0},
        {"id": "10", "table_number": "N4", "table_type": "Normal", "capacity": 4, "x_position": 65, "y_position": 45, "is_available": True, "allow_extra_chairs": False, "max_extra_chairs": 0}
    ],
    "2": [ # ชั้น 2
        {"id": "11", "table_number": "S1", "table_type": "Small", "capacity": 2, "x_position": 30, "y_position": 20, "is_available": True, "allow_extra_chairs": False, "max_extra_chairs": 0},
        {"id": "12", "table_number": "S2", "table_type": "Small", "capacity": 2, "x_position": 50, "y_position": 20, "is_available": True, "allow_extra_chairs": False, "max_extra_chairs": 0},
        {"id": "13", "table_number": "S3", "table_type": "Small", "capacity": 2, "x_position": 70, "y_position": 20, "is_available": True, "allow_extra_chairs": False, "max_extra_chairs": 0}
    ]
}

def generate_js_code():
    js_output = f"""
// ====================================================
// โค้ดนี้ถูกสร้างอัตโนมัติจากไฟล์ build_concert.py
// ====================================================

const concertDetails = {json.dumps(CONCERT_DETAILS, indent=4, ensure_ascii=False)};

const allTables = {json.dumps(TABLES, indent=4, ensure_ascii=False)};
"""
    return js_output

if __name__ == "__main__":
    output = generate_js_code()
    
    # บันทึกโค้ดลงไฟล์
    with open("generated_concert_data.js", "w", encoding="utf-8") as f:
        f.write(output)
        
    print("✅ สร้างไฟล์ generated_concert_data.js สำเร็จแล้ว!")
    print("คุณสามารถคัดลอกข้อมูลในไฟล์นี้ไปใส่ทับใน master_app.html ได้เลย\n")
