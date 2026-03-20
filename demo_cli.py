import requests
import json
import os
import sys

# ตั้งค่าสี
class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    GREY = '\033[90m'

API_URL = "http://127.0.0.1:5000/analyze"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print(f"{Color.CYAN}=========================================={Color.RESET}")
    print(f"{Color.CYAN}   PHISHING DETECTION SYSTEM (CLI DEMO)   {Color.RESET}")
    print(f"{Color.CYAN}=========================================={Color.RESET}")
    print("ตรวจสอบเว็บด้วย Layered Model (AI + Rules)")
    print("พิมพ์ 'exit' เพื่อออกจากโปรแกรม\n")

    while True:
        try:
            url = input(f"{Color.BOLD}🔎 กรุณาใส่ URL ที่ต้องการตรวจสอบ:{Color.RESET} ").strip()
            
            if url.lower() in ['exit', 'quit']:
                print(f"{Color.RESET}จบการทำงาน")
                break
                
            if not url:
                continue

            print(f"   {Color.CYAN}กำลังส่งให้ AI วิเคราะห์... {Color.RESET}", end='', flush=True)

            # ส่งไปหา Server
            response = requests.post(API_URL, json={"url": url}, timeout=5)
            
            print("เสร็จสิ้น!") 
            print("-" * 60)

            if response.status_code == 200:
                data = response.json()
                
                # ===================================================
                # 📜 ส่วนแสดง LOGS จาก Server 
                # ===================================================
                server_logs = data.get('logs', [])
                if server_logs:
                    for log in server_logs:
                        # ใส่สีให้ Log ดูเหมือนหน้า Server
                        if "ENTERING LAYER" in log:
                            print(f"{Color.CYAN}{log}{Color.RESET}")
                        elif "MATCH FOUND" in log or "SAFE" in log:
                            print(f"{Color.GREEN}{log}{Color.RESET}")
                        elif "DETECTED" in log or "BLOCK" in log or "DANGER" in log:
                            print(f"{Color.RED}{log}{Color.RESET}")
                        else:
                            print(log)
                    print("-" * 60) # ขีดคั่นจบ Log
                # ===================================================

                status = data.get('status', 'safe')
                reason = data.get('reason', '-')
                risk_score = data.get('risk_score', 0) 
                
                # ✨ ดึงค่าหมวดหมู่และรูปแบบ URL จากตัวแปร 'data'
                target_category = data.get('target_category', 'None')
                gen_type = data.get('generation_type', 'Unknown')
                
                # --- ส่วนแสดงผลลัพธ์สุดท้าย (ฉบับ Binary ตัด Caution ทิ้ง) ---
                if status == 'danger':
                    print(f"   {Color.RED}⛔ [DANGER / อันตราย (PHISHING)]{Color.RESET}")
                    print(f"   📝 เหตุผล: {reason}")
                    print(f"   📊 ระดับความเสี่ยง: {risk_score}%")
                    if target_category != 'None':
                        print(f"   🎯 เป้าหมายที่ถูกเลียนแบบ: {Color.RED}{target_category}{Color.RESET}")
                    # print(f"   🧬 รูปแบบการปลอมแปลง: {Color.CYAN}{gen_type}{Color.RESET}")
                    
                else:
                    print(f"   {Color.GREEN}✅ [SAFE / ปลอดภัย]{Color.RESET}")
                    print(f"   📝 สถานะ: {reason}")
                    
                    # แปลง Risk Score เป็น Safety Score เพื่อความเข้าใจง่าย
                    safety_score = 100 - risk_score
                    print(f"   🛡️ ระดับความมั่นใจ: {safety_score:.2f}%") 
                    print(f"   🧬 รูปแบบ URL: {Color.CYAN}{gen_type}{Color.RESET}")
                
                print("-" * 60 + "\n")
            else:
                print(f"\n❌ Server Error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"\n\n{Color.RED}❌ เชื่อมต่อ Server ไม่ได้!{Color.RESET}")
            print("กรุณาเปิดไฟล์ app.py ทิ้งไว้ก่อนนะครับ\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()