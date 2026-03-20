import pandas as pd
import numpy as np
import time
import math
import re
import tldextract
import difflib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler 
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import joblib
from scipy.sparse import hstack, csr_matrix
from tqdm import tqdm
import gc

CSV_FILE_PATH = r"D:\CODE\python\RMSE\test_dataset1.csv"
xgb_keywords = ['login', 'signin', 'verify', 'update', 'account', 'security', 'confirm', 'free', 'bonus', 'gift', 'promotion', 'lucky', 'win', 'prize', 'slot', 'bet', 'casino', 'game', 'spin', 'agent', 'wallet', 'crypto', 'support']
TARGET_BRANDS = ['facebook', 'google', 'apple', 'microsoft', 'paypal', 'amazon', 'netflix', 'kbank', 'scb', 'shopee', 'lazada', 'instagram', 'twitter', 'tiktok', 'yahoo', 'steam']

def clean_label(label):
    label = str(label).strip().lower()
    return 1 if label in ['1', 'bad', 'phishing', 'malicious', 'danger', 'yes'] else 0

def calc_entropy(text):
    if not text: return 0
    entropy = 0
    for x in range(256):
        p_x = float(text.count(chr(x))) / len(text)
        if p_x > 0: entropy += - p_x * math.log(p_x, 2)
    return entropy

def get_max_brand_similarity(domain):
    max_sim = 0
    for brand in TARGET_BRANDS:
        sim = difflib.SequenceMatcher(None, domain.lower(), brand).ratio()
        if sim > max_sim: max_sim = sim
    return max_sim

def extract_advanced_features(url):
    url_lower = str(url).lower()
    ext = tldextract.extract(url_lower)
    subdomain, domain, suffix = ext.subdomain, ext.domain, ext.suffix
    full_domain = f"{domain}.{suffix}"
    
    f1 = len(url_lower)
    f2 = url_lower.count('.')
    f3 = 1 if not url_lower.startswith('https') else 0
    f4 = len(domain)
    f5 = sum(c.isdigit() for c in url_lower)
    f6 = sum(1 for kw in xgb_keywords if kw in url_lower)
    f7 = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_lower) else 0
    f8 = 1 if '@' in url_lower else 0
    f9 = 1 if url_lower.rfind('//') > 7 else 0 
    f10 = 1 if '-' in domain else 0
    f11 = 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain) else 0
    shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'bit.do']
    f12 = 1 if full_domain in shorteners or domain in shorteners else 0
    f13 = domain.count('-')
    f14 = calc_entropy(domain) 
    path = url_lower.split(full_domain)[-1] if full_domain in url_lower else ""
    f15 = path.count('/')
    f16 = f5 / f1 if f1 > 0 else 0
    f17 = 1 if any(kw in xgb_keywords for kw in subdomain) else 0
    f18 = len(subdomain)
    f19 = get_max_brand_similarity(domain) 
    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17, f18, f19]

def main():
    print("================================================================")
    print(" 🧠 FINAL ACADEMIC TUNING (GPU ACCELERATED - VRAM OPTIMIZED)")
    print("================================================================")
    
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df.columns = df.columns.str.strip().str.lower()
        if 'url' not in df.columns and 'domain' in df.columns: df.rename(columns={'domain': 'url'}, inplace=True)
        if 'label' not in df.columns:
            for col in ['status', 'class', 'result']:
                if col in df.columns: df.rename(columns={col: 'label'}, inplace=True); break
        df = df.dropna(subset=['url', 'label'])
        df['target'] = df['label'].apply(clean_label)
        
        num_safe = len(df[df['target'] == 0])
        num_phishing = len(df[df['target'] == 1])
        scale_weight = num_safe / num_phishing if num_phishing > 0 else 1
    except Exception as e:
        print(f"❌ โหลดไฟล์ไม่สำเร็จ: {e}")
        return

    print("\n⏳ 2. กำลังคำนวณ 19 Features + Brand Similarity...")
    tqdm.pandas(desc="Extracting Features")
    numeric_features = df['url'].progress_apply(extract_advanced_features)
    X_num = np.array(numeric_features.tolist(), dtype=np.float32) 

    X = df['url']
    y = df['target']
    
    X_train_text, X_test_text, X_train_num, X_test_num, y_train, y_test = train_test_split(
        X, X_num, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n📏 กำลังปรับสเกลตัวเลข (MinMax Scaler)...")
    scaler = MinMaxScaler()
    X_train_num_scaled = scaler.fit_transform(X_train_num).astype(np.float32) 
    X_test_num_scaled = scaler.transform(X_test_num).astype(np.float32)

    # ใช้ 10,000 คำเหมือนเดิม! เพื่อความแม่นยำ 99%
    print("\n🧠 3. กำลังแปลง URL เป็นตัวเลข (TF-IDF 10,000 คำ)...")
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), max_features=10000, dtype=np.float32)
    X_train_tfidf = vectorizer.fit_transform(X_train_text)
    X_test_tfidf = vectorizer.transform(X_test_text)

    print("\n🧬 4. กำลังรวมร่าง (Feature Fusion - Sparse Compression)...")
    X_train_fusion = hstack([X_train_tfidf, csr_matrix(X_train_num_scaled)], format='csr')
    X_test_fusion = hstack([X_test_tfidf, csr_matrix(X_test_num_scaled)], format='csr')
    
    # 🧹 เคลียร์แรมเครื่องคอม
    del X_train_tfidf, X_test_tfidf, X_train_num_scaled, X_test_num_scaled, df, X_num
    gc.collect()

    print("\n🔋 5. โหลดข้อมูลลงหน่วยความจำการ์ดจอ (DMatrix ปกติ)...")
    # 🌟 กลับมาใช้ DMatrix ปกติ เพื่อไม่ให้คณิตศาสตร์พัง
    dtrain = xgb.DMatrix(X_train_fusion, label=y_train)
    dtest = xgb.DMatrix(X_test_fusion, label=y_test)
    
    del X_train_fusion, X_test_fusion
    gc.collect()

    print("\n🔥 6. เริ่มฝึกฝน XGBoost ด้วย GPU (RTX 4050 Safe Mode)...")
    TOTAL_TREES = 2500  # เทรนนานขึ้น เก็บรายละเอียดให้ลึก
    
    params = {
        'learning_rate': 0.05,        
        'max_depth': 7,               # 🌟 พระเอกของเรา! ลดลงมาเหลือ 7 VRAM ไม่พุ่ง 18GB แน่นอน
        'subsample': 0.8,
        'colsample_bytree': 0.8,      
        'scale_pos_weight': scale_weight,
        'tree_method': 'hist',        
        'device': 'cuda',             # 🌟 ใช้ GPU เต็มสูบ
        'random_state': 42,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss'
    }
    
    evals_result = {}
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=TOTAL_TREES,
        evals=[(dtrain, 'train'), (dtest, 'test')],
        early_stopping_rounds=50,
        verbose_eval=50, 
        evals_result=evals_result
    )

    print("\n🎯 7. กำลังทดสอบโมเดลกับ Test Set...")
    y_pred_prob = model.predict(dtest)
    y_pred = (y_pred_prob > 0.5).astype(int)
    acc = accuracy_score(y_test, y_pred) * 100
    
    print("==================================================")
    print(f"🏆 ความแม่นยำขั้นสุดยอด (GPU Accelerated SOTA): {acc:.4f}%")
    print(f"🌲 จำนวนต้นไม้ที่ดีที่สุดก่อนหยุด: {model.best_iteration}")
    print("==================================================")

    print("\n💾 8. กำลังบันทึกโมเดลทั้งหมด...")
    joblib.dump(scaler, 'fusion_scaler.pkl')          
    joblib.dump(vectorizer, 'fusion_vectorizer.pkl')  
    model.save_model('fusion_xgb_model.json')      
    print("✅ บันทึกเสร็จสมบูรณ์! พร้อมนำไปใช้งาน")

if __name__ == "__main__":
    main()