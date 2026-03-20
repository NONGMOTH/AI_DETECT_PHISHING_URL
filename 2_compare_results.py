"""
🔍 สคริปต์เปรียบเทียบความแม่นยำ - ใช้งานง่าย!
ไม่ต้องตั้งค่าอะไร รันเลย!
"""

# ════════════════════════════════════════════════════════════════════
# 💡 ไม่ต้องเปลี่ยนอะไร! สคริปต์จะค้นหาไฟล์อัตโนมัติ
# ════════════════════════════════════════════════════════════════════

"""
📝 วิธีใช้:
1. วางไฟล์ทั้ง 2 ไฟล์ในโฟลเดอร์เดียวกัน:
   ✅ answer_key_XXXX.csv  ← ไฟล์เฉลย (จาก generate_test_files_EASY.py)
   ✅ web_results.csv      ← ไฟล์จากเว็บ (ดาวน์โหลดจากปุ่ม "url + label")

2. รันสคริปต์นี้
   python compare_web_accuracy_EASY.py

3. ดูผลลัพธ์:
   📊 Accuracy, Precision, Recall, F1-Score
   📋 Confusion Matrix
   📁 ไฟล์วิเคราะห์: web_error_analysis_XXXX.csv

💡 หมายเหตุ:
- สคริปต์จะค้นหาไฟล์เฉลยอัตโนมัติ (answer_key_*.csv)
- ไฟล์จากเว็บต้องชื่อ "web_results.csv" เท่านั้น
- ถ้ามีหลายไฟล์เฉลย จะใช้ไฟล์แรกที่เจอ
"""

# ═══════════════════════════════════════════════════════════════════
# 📦 โค้ดหลัก (ไม่ต้องแก้)
# ═══════════════════════════════════════════════════════════════════

import pandas as pd
import os
import glob

def normalize_label(label):
    """แปลง label ให้เป็นรูปแบบมาตรฐาน"""
    if pd.isna(label):
        return None
    
    label_str = str(label).lower().strip()
    
    # ปลอดภัย
    if label_str in ['good', 'legitimate', 'safe', '0', '0.0', 'benign']:
        return False
    # อันตราย
    elif label_str in ['bad', 'phishing', 'danger', '1', '1.0', 'malicious']:
        return True
    else:
        return None

def find_answer_key():
    """ค้นหาไฟล์เฉลยอัตโนมัติ"""
    patterns = ['answer_key_*.csv', 'answer_*.csv']
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            return files[0]
    return None

def check_accuracy():
    """เปรียบเทียบความแม่นยำ"""
    
    print("=" * 70)
    print("🔍 URL THREAT ANALYZER - ตรวจสอบความแม่นยำ")
    print("=" * 70)
    print("\n⏳ กำลังโหลดไฟล์...\n")
    
    try:
        # 1. ค้นหาไฟล์เฉลย
        answer_file = find_answer_key()
        if not answer_file:
            print("❌ Error: ไม่พบไฟล์เฉลย")
            print("   📁 ต้องมีไฟล์ชื่อ 'answer_key_*.csv'")
            print("   💡 รัน generate_test_files_EASY.py ก่อน")
            return
        
        # 2. ตรวจสอบไฟล์ผลลัพธ์
        if not os.path.exists('web_results.csv'):
            print("❌ Error: ไม่พบไฟล์ 'web_results.csv'")
            print("   📁 ดาวน์โหลดผลลัพธ์จากเว็บ (ปุ่ม 'url + label')")
            print("   💡 บันทึกเป็นชื่อ 'web_results.csv'")
            return
        
        # 3. โหลดไฟล์
        print(f"📂 ไฟล์เฉลย: {answer_file}")
        truth_df = pd.read_csv(answer_file, low_memory=False)
        print(f"   ✅ {len(truth_df):,} URLs")
        
        print(f"\n📂 ไฟล์ผลลัพธ์: web_results.csv")
        web_df = pd.read_csv('web_results.csv', low_memory=False)
        print(f"   ✅ {len(web_df):,} URLs\n")
        
        # 4. ตรวจสอบคอลัมน์
        if 'url' not in truth_df.columns or 'url' not in web_df.columns:
            print("❌ Error: ไม่พบคอลัมน์ 'url'")
            return
        
        # 5. หา label column
        label_col = None
        for col in ['label', 'Label', 'status', 'Status']:
            if col in truth_df.columns:
                label_col = col
                break
        
        if not label_col:
            print("❌ Error: ไม่พบคอลัมน์ label ในไฟล์เฉลย")
            return
        
        if 'label' not in web_df.columns:
            print("❌ Error: ไฟล์เว็บไม่มีคอลัมน์ 'label'")
            print("   💡 ดาวน์โหลดจากปุ่ม 'url + label' (ไม่ใช่ 'ผลลัพธ์เต็ม')")
            return
        
        # 6. แสดง labels
        print("📊 Labels ในไฟล์:")
        print("=" * 70)
        print(f"ไฟล์เฉลย:")
        for label, count in truth_df[label_col].value_counts().items():
            print(f"   • {label}: {count:,}")
        
        print(f"\nไฟล์เว็บ:")
        for label, count in web_df['label'].value_counts().items():
            print(f"   • {label}: {count:,}")
        print()
        
        # 7. แปลง labels
        print("🔄 กำลังแปลง labels...")
        truth_df['norm'] = truth_df[label_col].apply(normalize_label)
        web_df['norm'] = web_df['label'].apply(normalize_label)
        
        # กรองข้อมูลที่ไม่สมบูรณ์
        truth_clean = truth_df[truth_df['norm'].notna()].copy()
        web_clean = web_df[web_df['norm'].notna()].copy()
        
        print(f"   ✅ ไฟล์เฉลย: {len(truth_clean):,} URLs (valid)")
        print(f"   ✅ ไฟล์เว็บ: {len(web_clean):,} URLs (valid)\n")
        
        # 8. รวมข้อมูล
        merged = pd.merge(
            truth_clean[['url', 'norm']],
            web_clean[['url', 'norm']],
            on='url',
            how='inner',
            suffixes=('_truth', '_web')
        )
        
        total = len(merged)
        
        if total == 0:
            print("❌ ไม่พบ URL ที่ตรงกัน!")
            print("   ตรวจสอบว่าไฟล์เว็บใช้ URLs เดียวกับไฟล์เฉลย")
            return
        
        print(f"✅ พบ URL ที่ตรงกัน: {total:,} URLs\n")
        
        # 9. คำนวณความถูกต้อง
        merged['correct'] = merged['norm_truth'] == merged['norm_web']
        correct = merged['correct'].sum()
        incorrect = total - correct
        accuracy = (correct / total) * 100
        
        # 10. Confusion Matrix
        tp = ((merged['norm_web'] == True) & (merged['norm_truth'] == True)).sum()
        tn = ((merged['norm_web'] == False) & (merged['norm_truth'] == False)).sum()
        fp = ((merged['norm_web'] == True) & (merged['norm_truth'] == False)).sum()
        fn = ((merged['norm_web'] == False) & (merged['norm_truth'] == True)).sum()
        
        # 11. คำนวณเมตริก
        precision = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0
        
        # 12. แสดงผลลัพธ์
        print("=" * 70)
        print(" 📊 สรุปผลการทดสอบ")
        print("=" * 70)
        print(f"🎯 URLs ทดสอบ: {total:,}")
        print(f"✅ ทายถูก: {correct:,}")
        print(f"❌ ทายผิด: {incorrect:,}")
        print(f"\n🏆 Accuracy: {accuracy:.2f}%")
        print(f"🎯 Precision: {precision:.2f}%")
        print(f"🔍 Recall: {recall:.2f}%")
        print(f"🛡️  Specificity: {specificity:.2f}%")
        print(f"📈 F1-Score: {f1:.2f}%")
        print("=" * 70)
        
        # 13. Confusion Matrix
        print("\n📋 Confusion Matrix:")
        print("=" * 70)
        print(f"                      │ Predicted: GOOD  │ Predicted: BAD")
        print(f"──────────────────────┼──────────────────┼──────────────────")
        print(f" Actual: GOOD         │  TN = {tn:>6}    │  FP = {fp:>6}")
        print(f" Actual: BAD          │  FN = {fn:>6}    │  TP = {tp:>6}")
        print("=" * 70)
        
        print("\n💡 คำอธิบาย:")
        print(f"   • TN: ทายถูก - URLs ปลอดภัย ({tn:,})")
        print(f"   • TP: ทายถูก - URLs อันตราย ({tp:,})")
        print(f"   • FP: ทายผิด - แจ้งเตือนเกิน ({fp:,})")
        print(f"   • FN: ทายผิด - ปล่อย URLs อันตรายผ่าน ({fn:,})")
        
        # 14. วิเคราะห์ข้อผิดพลาด
        errors = merged[~merged['correct']].copy()
        
        if len(errors) > 0:
            # ดึงข้อมูลเพิ่มเติม
            web_detail = web_df[['url', 'label']].rename(columns={'label': 'web_label'})
            truth_detail = truth_df[['url', label_col]].rename(columns={label_col: 'truth_label'})
            
            errors = errors.merge(web_detail, on='url', how='left')
            errors = errors.merge(truth_detail, on='url', how='left')
            
            print(f"\n⚠️  ข้อผิดพลาด {len(errors):,} URLs:")
            print("=" * 70)
            
            # False Positives
            fp_errors = errors[(errors['norm_web'] == True) & (errors['norm_truth'] == False)]
            if len(fp_errors) > 0:
                print(f"\n🔴 False Positives ({len(fp_errors):,} URLs):")
                print("   (URLs ปลอดภัยแต่เว็บบอกว่าอันตราย)\n")
                for _, row in fp_errors.head(5).iterrows():
                    print(f"   • {row['url'][:65]}")
                    print(f"     เฉลย: {row['truth_label']} | เว็บทาย: {row['web_label']}")
                if len(fp_errors) > 5:
                    print(f"   ... และอีก {len(fp_errors) - 5:,} URLs")
            
            # False Negatives
            fn_errors = errors[(errors['norm_web'] == False) & (errors['norm_truth'] == True)]
            if len(fn_errors) > 0:
                print(f"\n🔴 False Negatives ({len(fn_errors):,} URLs):")
                print("   (URLs อันตรายแต่เว็บบอกว่าปลอดภัย - อันตราย!)\n")
                for _, row in fn_errors.head(5).iterrows():
                    print(f"   • {row['url'][:65]}")
                    print(f"     เฉลย: {row['truth_label']} | เว็บทาย: {row['web_label']}")
                if len(fn_errors) > 5:
                    print(f"   ... และอีก {len(fn_errors) - 5:,} URLs")
            
            # บันทึกไฟล์
            error_file = f'web_error_analysis_{total}.csv'
            errors.to_csv(error_file, index=False, encoding='utf-8-sig')
            print("\n" + "=" * 70)
            print(f"📁 บันทึกข้อผิดพลาดที่: {error_file}")
        else:
            print("\n🎉 ไม่มีข้อผิดพลาด! ทายถูก 100%!")
        
        # 15. บันทึกผลเต็ม
        full_file = f'web_validation_full_{total}.csv'
        merged.to_csv(full_file, index=False, encoding='utf-8-sig')
        print(f"✅ บันทึกผลเต็มที่: {full_file}")
        
        # 16. สรุปท้าย
        print("\n" + "=" * 70)
        if accuracy >= 98.0:
            print("🏆 ยอดเยี่ยม! ความแม่นยำระดับ State-of-the-Art (≥98%)")
        elif accuracy >= 95.0:
            print("✨ ดีมาก! ความแม่นยำอยู่ในเกณฑ์ดี (95-98%)")
        elif accuracy >= 90.0:
            print("👍 ดี แต่ควรปรับปรุง (90-95%)")
        else:
            print("⚠️  ต้องปรับปรุง (<90%)")
        
        print(f"\n📊 สรุป: Accuracy={accuracy:.2f}%, Precision={precision:.2f}%, Recall={recall:.2f}%")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"❌ หาไฟล์ไม่พบ: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# ═══════════════════════════════════════════════════════════════════
# 🚀 เริ่มทำงาน
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    check_accuracy()
    print("\n✅ กด Enter เพื่อปิด...")
    input()