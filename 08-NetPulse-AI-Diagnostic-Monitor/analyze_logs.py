import csv
import os
from collections import Counter

LOG_FILE = "internet_logs.csv"

def analyze():
    if not os.path.exists(LOG_FILE):
        print(f"[{LOG_FILE}] ไม่พบไฟล์ Log กรุณารัน internet_monitor.py ก่อนครับ")
        return

    with open(LOG_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    total_checks = len(rows)
    if total_checks == 0:
        print("ยังไม่มีข้อมูลใน Log ครับ")
        return

    online_count = sum(1 for row in rows if row['Public_IP_Ping'] == 'OK')
    offline_count = total_checks - online_count
    
    uptime = (online_count / total_checks) * 100
    
    # Analyze failure reasons
    reasons = [row['Status'] for row in rows if row['Status'] != 'Online']
    reason_counts = Counter(reasons)
    
    # Signal Strength (RSSI) Analysis
    rssi_values = []
    for row in rows:
        try:
            rssi = int(row['RSSI'])
            if rssi != 0: # 0 means No Info
                rssi_values.append(rssi)
        except (ValueError, KeyError):
            pass
            
    print("-" * 50)
    print("📊 รายงานวิเคราะห์คุณภาพอินเทอร์เน็ต (Internet Quality Report)")
    print("-" * 50)
    print(f"✅ บันทึกข้อมูลทั้งหมด: {total_checks} ครั้ง")
    print(f"📈 Uptime (เวลาที่เน็ตใช้ได้): {uptime:.2f}%")
    print(f"❌ จำนวนครั้งที่มีปัญหา: {offline_count}")
    
    if offline_count > 0:
        print("\n🔍 สาเหตุที่หลุดส่วนใหญ่:")
        for reason, count in reason_counts.most_common():
            print(f"- {reason}: {count} ครั้ง ({(count/offline_count)*100:.1f}%)")
            
    if rssi_values:
        avg_rssi = sum(rssi_values) / len(rssi_values)
        print(f"\n📡 ความแรงสัญญาณ Wi-Fi เฉลี่ย (RSSI): {avg_rssi:.1f} dBm")
        if avg_rssi < -75:
            print("⚠️ คำแนะนำ: สัญญาณ Wi-Fi ค่อนข้างอ่อน (<-75 dBm) อาจเป็นสาเหตุให้หลุดบ่อย ลองย้ายเข้าใกล้ Router ดูครับ")
        elif avg_rssi > -60:
            print("✨ สัญญาณ Wi-Fi ยอดเยี่ยมมาก (>-60 dBm)")
        else:
            print("🆗 สัญญาณ Wi-Fi อยู่ในระดับปกติ")

    # High latency (> 150ms)
    high_latency_count = sum(1 for row in rows if row['Latency'] != '0' and float(row['Latency']) > 150)
    if high_latency_count > 0:
        print(f"\n⚡️ ความหน่วงสูง (>150ms): เจอทั้งหมด {high_latency_count} ครั้ง")

    print("-" * 50)

if __name__ == "__main__":
    analyze()
