"""
🎲 สคริปต์สร้างไฟล์ทดสอบ - ปรับแต่งง่าย!
เปลี่ยนเลขบรรทัดเดียวด้านล่าง ↓↓↓
"""

# ════════════════════════════════════════════════════════════════════
# 🎯 เปลี่ยนตรงนี้เท่านั้น! (บรรทัดเดียว)
# ════════════════════════════════════════════════════════════════════
SAMPLE_SIZE = 100  # 👈 เปลี่ยนตัวเลขนี้ (เช่น 1000, 5000, 10000)
# ════════════════════════════════════════════════════════════════════

"""
📝 คำอธิบาย SAMPLE_SIZE:
- SAMPLE_SIZE = จำนวน URLs ที่ต้องการสุ่มจาก dataset
- ตัวอย่าง:
  • 100   → ทดสอบเร็ว (1-2 นาที)
  • 1000  → ทดสอบปานกลาง (5-10 นาที)
  • 3000  → ทดสอบมาตรฐาน (15-20 นาที) ✅ แนะนำ
  • 5000  → ทดสอบละเอียด (25-30 นาที)
  • 10000 → ทดสอบเต็มรูป (45-60 นาที)

📝 คำอธิบาย RANDOM_SEED:
- random_seed=69 → ถ้ารันหลายครั้ง จะได้ URLs ชุดเดิมทุกครั้ง ✅
- random_seed=42 → เปลี่ยนเป็น 42 จะได้ URLs ชุดใหม่ (สุ่มแบบอื่น)
- random_seed=100 → เปลี่ยนเป็น 100 จะได้อีกชุดหนึ่ง

💡 ใช้งาน:
1. ครั้งแรก: ใช้ seed=69, SAMPLE_SIZE=3000
2. ทดสอบซ้ำ: ใช้ seed=69 เดิม (ได้ชุดเดิม)
3. ทดสอบชุดใหม่: เปลี่ยนเป็น seed=100 (ได้ชุดใหม่)

🎯 ไฟล์ที่จะได้:
- answer_key_3000.csv      ← ไฟล์เฉลย (เก็บไว้เปรียบเทียบ)
- upload_urls_3000.txt     ← อัปโหลดไฟล์นี้ไปเว็บ
- upload_urls_3000.csv     ← หรือใช้ไฟล์นี้ก็ได้

📌 หมายเหตุ:
ชื่อไฟล์จะเปลี่ยนตาม SAMPLE_SIZE อัตโนมัติ
เช่น SAMPLE_SIZE=5000 → answer_key_5000.csv
"""

# ═══════════════════════════════════════════════════════════════════
# 🔧 ตั้งค่าขั้นสูง (ไม่ต้องแก้ก็ได้)
# ═══════════════════════════════════════════════════════════════════
DATASET_FILE = 'test_dataset1.csv'  # ชื่อไฟล์ dataset ของคุณ
RANDOM_SEED = 69                     # ค่า seed สำหรับสุ่ม (ใช้ค่าเดิมได้ URLs ชุดเดิม)

# ═══════════════════════════════════════════════════════════════════
# 📦 โค้ดหลัก (ไม่ต้องแก้)
# ═══════════════════════════════════════════════════════════════════

import pandas as pd
import os
import sys

def generate_test_files(dataset_file, sample_size, random_seed):
    """สร้างไฟล์ทดสอบจาก dataset"""
    
    print("=" * 70)
    print("🎲 URL THREAT ANALYZER - สร้างไฟล์ทดสอบ")
    print("=" * 70)
    print(f"\n⚙️  การตั้งค่า:")
    print(f"   • ไฟล์ Dataset: {dataset_file}")
    print(f"   • จำนวน URLs: {sample_size:,}")
    print(f"   • Random Seed: {random_seed} {'(ได้ชุดเดิมทุกครั้ง)' if random_seed == 69 else '(ชุดใหม่)'}")
    print()
    
    # ตรวจสอบไฟล์
    if not os.path.exists(dataset_file):
        print(f"❌ Error: ไม่พบไฟล์ '{dataset_file}'")
        print("   📁 วางไฟล์ dataset ในโฟลเดอร์เดียวกันกับสคริปต์นี้")
        return False
    
    print(f"⏳ กำลังโหลด {dataset_file}...")
    
    try:
        # โหลด dataset
        df = pd.read_csv(dataset_file, low_memory=False)
        total = len(df)
        print(f"✅ โหลดสำเร็จ: {total:,} URLs")
        
        # ตรวจสอบคอลัมน์
        if 'url' not in df.columns:
            print(f"❌ Error: ไม่พบคอลัมน์ 'url' ในไฟล์")
            print(f"   คอลัมน์ที่มี: {list(df.columns)}")
            return False
        
        # หา label column
        label_col = None
        for col in ['label', 'Label', 'status', 'Status']:
            if col in df.columns:
                label_col = col
                break
        
        if not label_col:
            print(f"❌ Error: ไม่พบคอลัมน์ label")
            return False
        
        # แสดงสถิติ
        print(f"\n📊 ข้อมูลใน Dataset:")
        print("=" * 70)
        label_counts = df[label_col].value_counts()
        for label, count in label_counts.items():
            pct = (count / total) * 100
            emoji = "✅" if str(label).lower() in ['good', '0'] else "⚠️"
            print(f"   {emoji} {label}: {count:,} ({pct:.1f}%)")
        
        # ทำความสะอาด
        df = df.dropna(subset=['url', label_col])
        df = df.drop_duplicates(subset=['url'])
        cleaned = len(df)
        
        if cleaned < total:
            print(f"\n🧹 ลบข้อมูลซ้ำ/ว่าง: {total - cleaned:,} บรรทัด")
            print(f"   เหลือ: {cleaned:,} URLs")
        
        # ตรวจสอบขนาด
        if sample_size > cleaned:
            print(f"\n⚠️  จำนวนที่ต้องการ ({sample_size:,}) มากกว่าข้อมูล ({cleaned:,})")
            sample_size = cleaned
            print(f"   ปรับเป็น {sample_size:,} URLs")
        
        # สุ่มข้อมูล
        print(f"\n🎲 กำลังสุ่ม {sample_size:,} URLs (seed={random_seed})...")
        sampled = df.sample(n=sample_size, random_state=random_seed)
        
        # แสดงสัดส่วน
        print(f"\n📊 ตัวอย่างที่สุ่มได้:")
        sampled_counts = sampled[label_col].value_counts()
        for label, count in sampled_counts.items():
            pct = (count / sample_size) * 100
            emoji = "✅" if str(label).lower() in ['good', '0'] else "⚠️"
            print(f"   {emoji} {label}: {count:,} ({pct:.1f}%)")
        
        # สร้างไฟล์
        print(f"\n💾 กำลังสร้างไฟล์...")
        
        # 1. ไฟล์เฉลย
        answer_file = f'answer_key_{sample_size}.csv'
        sampled.to_csv(answer_file, index=False, encoding='utf-8-sig')
        size_mb = os.path.getsize(answer_file) / (1024 * 1024)
        print(f"   ✅ {answer_file} ({size_mb:.2f} MB)")
        
        # 2. ไฟล์ TXT
        txt_file = f'upload_urls_{sample_size}.txt'
        sampled['url'].to_csv(txt_file, index=False, header=False, encoding='utf-8')
        print(f"   ✅ {txt_file}")
        
        # 3. ไฟล์ CSV
        csv_file = f'upload_urls_{sample_size}.csv'
        sampled[['url']].to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"   ✅ {csv_file}")
        
        # ประมาณเวลา
        time_min = (sample_size * 0.027) / 60
        time_concurrent = time_min / 10
        print(f"\n⏱️  ประมาณเวลาสแกนบนเว็บ: ~{time_concurrent:.1f} นาที")
        
        print("\n✅ สร้างไฟล์สำเร็จ!")
        return True
        
    except MemoryError:
        print(f"\n❌ Error: หน่วยความจำไม่พอ")
        print(f"   ลด SAMPLE_SIZE ลงเหลือ 1000-2000")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ═══════════════════════════════════════════════════════════════════
# 🚀 เริ่มทำงาน
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "🎲" * 35)
    print(f"📝 ตั้งค่าปัจจุบัน: SAMPLE_SIZE = {SAMPLE_SIZE:,}")
    print(f"📝 Random Seed: {RANDOM_SEED}")
    print("🎲" * 35 + "\n")
    
    success = generate_test_files(
        dataset_file=DATASET_FILE,
        sample_size=SAMPLE_SIZE,
        random_seed=RANDOM_SEED
    )
    
    if not success:
        print("\n❌ สร้างไฟล์ไม่สำเร็จ")
    else:
        print("\n✅ สร้างไฟล์ทดสอบสำเร็จ! ตรวจสอบไฟล์ในโฟลเดอร์นี้ได้เลย")