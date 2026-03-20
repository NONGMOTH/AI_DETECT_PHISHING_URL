# python auto_test_csv.py
import pandas as pd
import requests
import time
from tqdm import tqdm

# ==========================================
# ⚙️ ตั้งค่าก่อนรัน
# ==========================================
CSV_FILE_PATH = r"D:\CODE\python\RMSE\test_dataset1.csv" 
API_URL = "http://127.0.0.1:5000/analyze"
SAMPLE_SIZE = 10000

def get_true_label(label):
    label = str(label).strip().lower()
    if label in ['1', 'bad', 'phishing', 'malicious', 'danger', 'yes', 'true']:
        return True
    return False

def main():
    print("===========================================")
    print(" 🤖 BATCH TESTING SYSTEM (AI PHISHING)")
    print("===========================================")
    
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"✅ โหลดไฟล์ {CSV_FILE_PATH} สำเร็จ (ทั้งหมด {len(df)} แถว)")
    except Exception as e:
        print(f"❌ หาไฟล์ CSV ไม่พบ: {e}")
        return

    label_col = None
    for col in ['status', 'label', 'class', 'result', 'type']:
        if col in df.columns:
            label_col = col
            break
            
    if not label_col:
        print("❌ ไม่พบคอลัมน์ที่ระบุสถานะเว็บในไฟล์ CSV")
        return

    if 'url' not in df.columns and 'domain' in df.columns:
        df.rename(columns={'domain': 'url'}, inplace=True)

    df = df.dropna(subset=['url', label_col])

    if SAMPLE_SIZE and SAMPLE_SIZE < len(df):
        print(f"✅ สุ่มดึงข้อมูลมาทดสอบจำนวน {SAMPLE_SIZE} รายการ")
        df_test = df.sample(n=SAMPLE_SIZE, random_state=42)
    else:
        print(f"✅ ทำการทดสอบข้อมูลทั้งหมด {len(df)} รายการ")
        df_test = df

    print("\n🚀 กำลังส่งข้อมูลให้ AI วิเคราะห์...")
    
    correct_predictions = 0
    total_tested = 0
    failed_requests = 0
    error_cases = []

    for index, row in tqdm(df_test.iterrows(), total=len(df_test), desc="Testing URLs"):
        url = str(row['url']).strip()
        true_is_phishing = get_true_label(row[label_col])

        try:
            response = requests.post(API_URL, json={"url": url}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # 🌟 เช็คแค่ว่าเป็น Danger ไหม (เพราะเราตัด Caution ออกแล้ว)
                status = data.get('status', 'safe')
                ai_is_phishing = status == "danger"

                if ai_is_phishing == true_is_phishing:
                    correct_predictions += 1
                else:
                    error_cases.append({
                        "url": url,
                        "true_phishing": true_is_phishing,
                        "ai_predicted": ai_is_phishing,
                        "risk_score": data.get('risk_score', 0),
                        "reason": data.get('reason', '')
                    })

                total_tested += 1
            else:
                failed_requests += 1
        except requests.exceptions.RequestException:
            failed_requests += 1

        time.sleep(0.01)

    print("\n===========================================")
    print(" 📊 สรุปผลการทดสอบ (TEST RESULTS)")
    print("===========================================")
    print(f"🎯 จำนวนเว็บที่ทดสอบสำเร็จ: {total_tested} URLs")
    
    if total_tested > 0:
        accuracy = (correct_predictions / total_tested) * 100
        print(f"✅ ทายถูกทั้งหมด: {correct_predictions} URLs")
        print(f"❌ ทายผิดพลาด: {total_tested - correct_predictions} URLs")
        print(f"🏆 ความแม่นยำ (Accuracy): {accuracy:.2f}%")
        if len(error_cases) > 0:
            pd.DataFrame(error_cases).to_csv('error_analysis.csv', index=False, encoding='utf-8')
            print(f"📁 บันทึกรายชื่อเว็บที่ทายผิดไว้ที่ไฟล์: error_analysis.csv")
    print("===========================================\n")

if __name__ == "__main__":
    main()