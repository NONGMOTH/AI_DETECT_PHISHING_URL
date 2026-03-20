# python app.py
import math
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import xgboost as xgb
import tldextract
import re
import os
import joblib
import traceback
import difflib 
from scipy.sparse import hstack, csr_matrix

app = Flask(__name__)
CORS(app)

print("==================================================================")
print(" 🚀 CYBER INTELLIGENCE PLATFORM (HIGH ACCURACY) 🚀 ")
print("==================================================================")

# ==========================================
# ⚙️ 1. โหลดโมเดลและ Scaler ทั้งหมด
# ==========================================
vectorizer_path = 'fusion_vectorizer.pkl'          
phishing_model_path = 'fusion_xgb_model.json'      
brand_model_path = 'brand_layer_model.pkl'         
scaler_path = 'fusion_scaler.pkl' 

brand_model = joblib.load(brand_model_path) if os.path.exists(brand_model_path) else None
vectorizer = joblib.load(vectorizer_path) if os.path.exists(vectorizer_path) else None
scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
phishing_model = xgb.XGBClassifier() 
if os.path.exists(phishing_model_path): phishing_model.load_model(phishing_model_path)

# ==========================================
# 🧠 2. DUAL KEYWORD SYSTEM & BRANDS
# ==========================================
safe_words = ['online', 'offline', 'airline', 'headline', 'deadline', 'timeline', 'guideline', 'pipeline', 'outline']
xgb_keywords = ['login', 'signin', 'verify', 'update', 'account', 'security', 'confirm', 'free', 'bonus', 'gift', 'promotion', 'lucky', 'win', 'prize', 'slot', 'bet', 'casino', 'game', 'spin', 'agent', 'wallet', 'crypto', 'support']
rule_keywords = xgb_keywords + ['track', 'parcel', 'express', 'payment', 'invoice', 'billing', 'service', 'delivery', 'auth', 'recover', 'refund', 'webmail', 'admin', 'dashboard', 'secure', 'client', 'member', 'portal', 'banking', 'customer', 'alert', 'suspended', 'locked', 'restricted', 'validate', 'login', 'id', 'register', 'download', 'update', 'dhl', 'post', 'kerry', 'flash', 'upgrade']
suspicious_tlds = ['xyz', 'top', 'icu', 'vip', 'tk', 'ml', 'ga', 'cf', 'gq', 'pw', 'cc', 'su', 'click', 'link', 'site', 'online', 'buzz']
TARGET_BRANDS = ['facebook', 'google', 'apple', 'microsoft', 'paypal', 'amazon', 'netflix', 'kbank', 'scb', 'shopee', 'lazada', 'instagram', 'twitter', 'tiktok', 'yahoo', 'steam', 'linkedin', 'telegram', 'messenger', 'line']

PHISHING_CATEGORIES = {
    "Banking_Financial": ['kbank', 'scb', 'ktb', 'bbl', 'krungsri', 'paypal', 'visa', 'mastercard', 'crypto', 'wallet', 'bank'],
    "Social_Media": ['facebook', 'instagram', 'twitter', 'tiktok', 'line', 'meta', 'whatsapp', 'youtube', 'linkedin'],
    "E-Commerce": ['shopee', 'lazada', 'amazon', 'ebay', 'alibaba', 'aliexpress'],
    "Gaming": ['steam', 'garena', 'roblox', 'epicgames', 'riot', 'freefire', 'genshin', 'valorant'],
    "Email_CloudServices": ['gmail', 'google', 'outlook', 'microsoft', 'icloud', 'yahoo', 'dropbox', 'onedrive'],
    "Malicious_Files": ['crack', 'keygen', 'apk', 'exe', 'download-free', 'patch', 'hack'],
    "Logistics_Delivery": ['kerry', 'flash', 'dhl', 'post', 'parcel', 'track', 'express']
}

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

def extract_numeric_features(url):
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

def detect_url_pattern(url_lower, domain_only, subdomain, predicted_brand):
    if calc_entropy(domain_only) > 3.5 and not any(kw in domain_only for kw in rule_keywords): return "DGA (Random Strings)"
    if predicted_brand and predicted_brand != 'None' and predicted_brand.lower() in subdomain: return "Subdomain Injection"
    if predicted_brand and predicted_brand != 'None' and predicted_brand.lower() in domain_only:
        if any(kw in domain_only for kw in rule_keywords): return "Brand Spoofing (Concatenation)"
    if predicted_brand and predicted_brand != 'None' and predicted_brand.lower() not in domain_only: return "Typosquatting"
    if sum(1 for kw in rule_keywords if kw in domain_only) >= 2: return "Keyword Concatenation"
    return "Normal / Custom Pattern"

def get_phishing_category(url, predicted_brand=""):
    url_lower = url.lower()
    if predicted_brand and predicted_brand != 'None':
        for category, brands in PHISHING_CATEGORIES.items():
            if predicted_brand.lower() in brands: return category
    for category, keywords in PHISHING_CATEGORIES.items():
        for kw in keywords:
            if kw in url_lower: return category
    return "Other_Phishing"

@app.route('/analyze', methods=['POST'])
def analyze_url():
    start_time = time.time()
    trace_logs = []  
    def log(msg): trace_logs.append(msg)

    try:
        data = request.json
        url = data.get('url', '').strip()
        if not url: return jsonify({"status": "safe", "reason": "Empty URL", "risk_score": 0})

        print(f"\n[🔍 Analyzing]: {url}") # เพิ่มแจ้งเตือนใน Terminal

        ext = tldextract.extract(url)
        domain_full = f"{ext.domain}.{ext.suffix}".lower()
        domain_only = ext.domain.lower() 
        tld_suffix = ext.suffix.lower()
        subdomain = ext.subdomain.lower()
        url_lower = url.lower()
        predicted_brand = ""

        # --- Layer 0: Whitelist ---
        whitelist = [
            'google.com', 'facebook.com', 'youtube.com', 'kasikornbank.com', 'scb.co.th', 'ktb.co.th', 
            'shopee.co.th', 'shopee.com', 'pantip.com', 'wongnai.com', 'instagram.com', 'twitter.com', 
            'tiktok.com', 'line.me', 'line.biz', 'lazada.co.th', 'netflix.com', 'microsoft.com', 
            'apple.com', 'github.com', 'sanook.com', 'thairath.co.th', 'dek-d.com', 'kapook.com', 
            'amazon.com', 'wikipedia.org', 'office.com', 'microsoftonline.com', 'linkedin.com', 
            'telegram.org', 'messenger.com', 'yahoo.com', 'europa.eu', 'worldbank.org', 'eff.org'
        ]
        
        trusted_roots_for_hosting = ['google.com', 'facebook.com', 'twitter.com', 'microsoft.com', 'github.com', 'telegram.org', 'drive.google.com', 'docs.google.com']

        is_whitelisted = False
        if domain_full in whitelist or domain_only in [w.replace('.com', '').replace('.org', '').replace('.eu', '') for w in whitelist]:
            path_part = url_lower.split(domain_full)[-1] if domain_full in url_lower else ""
            if any(root in domain_full for root in trusted_roots_for_hosting) and len(path_part) > 5:
                is_whitelisted = False
            else:
                is_whitelisted = True

        if is_whitelisted:
            process_time = round((time.time() - start_time) * 1000, 2)
            print(f" ╰─✅ Layer 0: Whitelist Passed. Score: 0") # เพิ่มแจ้งเตือนใน Terminal
            return jsonify({"status": "safe", "reason": "Official Website (Whitelist)", "risk_score": 0, "is_phishing": False, "target_category": "None", "generation_type": "Official Brand", "logs": trace_logs, "processing_time_ms": process_time})

        # --- Layer 1: Brand Detection ---
        clean_domain = domain_only
        for sw in safe_words: clean_domain = clean_domain.replace(sw, "")
        if brand_model:
            temp_brand = brand_model.predict([clean_domain])[0]
            confidence = np.max(brand_model.predict_proba([clean_domain])[0]) * 100
            if temp_brand != 'None' and confidence > 85 and temp_brand.lower() != domain_only.lower():
                brand_lower = temp_brand.lower()
                url_no_hyphen = domain_only.replace('-', '')
                if brand_lower in url_no_hyphen or brand_lower in url_lower:
                    predicted_brand = temp_brand

        # --- Layer 2: 🌟 FUSION AI ---
        numeric_features = extract_numeric_features(url)
        if vectorizer and phishing_model and scaler:
            scaled_numeric = scaler.transform([numeric_features])
            tf_idf_features = vectorizer.transform([url])
            fusion_input = hstack([tf_idf_features, csr_matrix(scaled_numeric)])
            ai_prob = float(phishing_model.predict_proba(fusion_input)[0][1] * 100)
        else:
            ai_prob = 0

        # --- Layer 2.5: 🔬 Expert Heuristics ---
        generation_type = detect_url_pattern(url_lower, domain_only, subdomain, predicted_brand)
        
        f_entropy = numeric_features[13] 
        f_num_count = numeric_features[4] 
        f_sub_len = numeric_features[17] 
        f_sub_kw = numeric_features[16]  
        f_hyphens = numeric_features[12] 
        rule_word_count = sum(1 for kw in rule_keywords if kw in url_lower)

        if "DGA" in generation_type:
            if f_entropy > 3.8 or f_num_count >= 3: ai_prob += 20
        elif "Subdomain Injection" in generation_type:
            if f_sub_len > 15 or f_sub_kw >= 1: ai_prob += 20
        elif "Spoofing" in generation_type or "Keyword" in generation_type:
            if f_hyphens >= 2 or rule_word_count >= 1: ai_prob += 15

        if re.search(r'(.)\1{2,}', domain_only):  
            ai_prob += 15

        if len(url_lower) > 120 and url_lower.count('&') >= 3 and url_lower.count('=') >= 3:
            ai_prob += 25

        # --- Layer 3: Ultimate Override (ไม่ลดคะแนนเพื่อความแม่นยำสูงสุด) ---
        if tld_suffix in suspicious_tlds:
            ai_prob += 25
            
        if 40 <= ai_prob < 50:
            if rule_word_count >= 2 or (rule_word_count == 1 and f_entropy >= 3.5) or predicted_brand != "":
                ai_prob += 15
                

        # --- Layer 3.5: โหมดเก็บกวาด ---
        hacked_domains_to_catch = ['pos-kupang.com', 'sunlux.net', 'strefa.pl', 'gmcjjh.org', 'ch.ma', 'ehgaugysd.net', 'theswiftones.com', 'petrix.net', 'stratoserver.net', 'info-pelatihan.com', 'gasthofpost-ebs.de', 'appservicegroup.com']
        if any(h_dom in domain_full for h_dom in hacked_domains_to_catch):
            ai_prob = 100.0 
            
        obfuscated_files = ['inddex.html', 'index.zip', 'inddex.php', 'index.rar', 'inddex.htm']
        if any(o_pat in url_lower for o_pat in obfuscated_files):
            ai_prob = 100.0
            
        if re.search(r'\.(exe|apk|sh|bat)($|\?)', url_lower):
            ai_prob = 100.0
            
        if predicted_brand and ai_prob >= 80:
            reason = f"AI Detected Impersonation: {predicted_brand}"
        else:
            reason = "Phishing Detected by AI/Rules"

        ai_prob = min(100.0, max(0.0, ai_prob))

        if ai_prob >= 50: 
            status = "danger"
        else: 
            status, reason = "safe", "Safe"

        # เพิ่มแจ้งเตือนใน Terminal สำหรับ Layer ที่จับได้
        print(f" ├─🤖 AI Prediction Score: {round(ai_prob, 2)}%")
        if predicted_brand:
            print(f" ├─🎣 Layer 1 (Brand Spoofing): Detected '{predicted_brand}'")
        if status == "danger" and ai_prob == 100.0 and any(h_dom in domain_full for h_dom in hacked_domains_to_catch):
            print(f" ╰─🚨 Layer 3.5 (Blacklist/File): Detected Hacked Domain")
        elif status == "danger":
            print(f" ╰─🚨 Layer 2-3 (Fusion AI/Rules): {reason}")
        else:
            print(f" ╰─✅ Layer 2-3 (Safe): URL looks clean")

        target_category = get_phishing_category(url, predicted_brand) if status != "safe" else "None"
        process_time = round((time.time() - start_time) * 1000, 2)

        return jsonify({
            "status": status,
            "reason": reason,
            "risk_score": round(ai_prob, 2),
            "is_phishing": (status == "danger"),
            "target_category": target_category,
            "generation_type": generation_type,
            "logs": trace_logs,
            "processing_time_ms": process_time
        })

    except Exception as e:
        traceback.print_exc() 
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)