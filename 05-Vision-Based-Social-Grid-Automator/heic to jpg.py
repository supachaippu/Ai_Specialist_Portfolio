import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from pillow_heif import register_heif_opener

# ลงทะเบียนตัวอ่าน HEIC
register_heif_opener()

def select_and_convert():
    # 1. ซ่อนหน้าต่างหลักของ Tkinter (ไม่ให้มีหน้าต่างเปล่าๆ โผล่มา)
    root = tk.Tk()
    root.withdraw()

    # 2. เปิดหน้าต่างให้เลือกโฟลเดอร์
    print("⏳ กำลังเปิดหน้าต่างเลือกโฟลเดอร์...")
    source_folder = filedialog.askdirectory(title="เลือกโฟลเดอร์ที่มีรูป HEIC")

    # ถ้ากด Cancel หรือไม่ได้เลือกอะไร ให้จบการทำงาน
    if not source_folder:
        print("❌ ยกเลิกการเลือกโฟลเดอร์")
        return

    # 3. สร้างโฟลเดอร์ปลายทาง (ชื่อเดิม + _Converted)
    folder_name = os.path.basename(source_folder)
    # สร้าง folder ปลายทางไว้ข้างๆ folder ต้นทาง
    output_folder = os.path.join(os.path.dirname(source_folder), f"{folder_name}_Converted")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"📂 เลือกโฟลเดอร์: {source_folder}")
    print(f"💾 โฟลเดอร์ปลายทาง: {output_folder}")
    print("-" * 40)

    # 4. เริ่มแปลงไฟล์
    count = 0
    errors = 0
    
    files = os.listdir(source_folder)
    total_files = len([f for f in files if f.lower().endswith('.heic')])
    
    if total_files == 0:
        messagebox.showwarning("ไม่พบไฟล์", "ไม่พบไฟล์ .HEIC ในโฟลเดอร์ที่เลือกเลยครับ")
        return

    for filename in files:
        if filename.lower().endswith(".heic"):
            heic_path = os.path.join(source_folder, filename)
            jpg_filename = os.path.splitext(filename)[0] + ".jpg"
            jpg_path = os.path.join(output_folder, jpg_filename)

            try:
                img = Image.open(heic_path)
                img = img.convert("RGB")
                img.save(jpg_path, "JPEG", quality=95)
                
                count += 1
                print(f"[{count}/{total_files}] ✅ แปลงเสร็จ: {filename}")
                
            except Exception as e:
                errors += 1
                print(f"❌ แปลงไม่ได้: {filename} ({e})")

    # 5. แจ้งเตือนเมื่อเสร็จ
    print("-" * 40)
    result_msg = f"🎉 ทำงานเสร็จสิ้น!\n\n✅ แปลงได้: {count} รูป\n❌ ผิดพลาด: {errors} รูป\n\nไฟล์อยู่ที่: {output_folder}"
    print(result_msg)
    messagebox.showinfo("เรียบร้อย", result_msg)

if __name__ == "__main__":
    # เช็คว่าลง library ครบหรือยัง
    try:
        select_and_convert()
    except ImportError:
        print("❌ คุณยังไม่ได้ลง Library ครับ")
        print("👉 กรุณารันคำสั่งนี้ใน Terminal/CMD ก่อน: pip install pillow pillow-heif")
        input("กด Enter เพื่อปิด...")