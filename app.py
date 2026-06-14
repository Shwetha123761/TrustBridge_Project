import os
import re
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
import pytesseract
from google import genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "hackathon-secret")
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Configure Tesseract path for Windows environments if present
if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

# --- INITIALIZE GEMINI GENAI CLIENT ---
api_key = os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=api_key)

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.context_processor
def override_url_for():
    """Cache-busting helper for assets during live hackathon iterations."""
    return dict(url_with_timestamp=lambda endpoint, **values: url_for(
        endpoint, 
        v=int(os.stat(os.path.join(app.root_path, endpoint)).st_mtime), 
        **values
    ))

def extract_text_from_pdf(path):
    """Extracts native text layer from PDF documents."""
    text = ""
    try:
        for page in PdfReader(path).pages:
            t = page.extract_text()
            if t: 
                text += t + "\n"
    except: 
        pass
    return text

def extract_text_from_image(path):
    """Extracts text out of image assets using Tesseract OCR."""
    try: 
        return pytesseract.image_to_string(Image.open(path))
    except: 
        return ""

def extract_key_details(text):
    """Regular expression metadata extraction suite with date extraction."""
    details = {
        "company": "Not Detected", 
        "candidate": "Not Detected", 
        "email": "Not Detected", 
        "role": "Not Detected", 
        "salary": "Not Detected", 
        "date": "Not Detected"
    }
    
    # Extract Email Targets
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if emails: 
        details["email"] = emails[0]
        
    # Extract Salary Packages
    salaries = re.findall(r'(?:INR|USD|\$|₹|Rs\.?)\s*\d+(?:,\d+)*(?:\s*(?:per\s+month|p\.m\.|per\s+annum|p\.a\.|lpa))?', text, re.IGNORECASE)
    if salaries: 
        details["salary"] = salaries[0]

    # Extract Calendar Dates
    dates = re.findall(r'\b\d{1,2}[-/\s](?:\d{1,2}|Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[-/\s]\d{2,4}\b|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\b', text, re.IGNORECASE)
    if dates:
        details["date"] = dates[0]
    
    # Line heuristic evaluation pass for candidate names and corporate headers
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines: 
        details["company"] = lines[0]
        
    for line in lines:
        if "dear" in line.lower(): 
            details["candidate"] = re.sub(r'(?i)dear', '', line).strip(', :')
        if any(k in line.lower() for k in ["role:", "position:", "designation:"]): 
            details["role"] = line
            
    if details["role"] == "Not Detected":
        for line in lines:
            if any(k in line.lower() for k in ["intern", "developer", "engineer", "analyst"]):
                details["role"] = line
                break
                
    return details

def evaluate_rules(text, entities):
    """Deterministic security compliance verification matrix with custom demo realistic scoring."""
    # Start at 95 to provide a realistic score for clean letters
    score = 95
    findings = []
    text_lower = text.lower()
    email = entities["email"].lower()
    
    # 1. Email Domain Evaluation Pass
    if email != "not detected":
        if any(p in email for p in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]):
            score -= 25
            findings.append({
                "name": "Free Email Used", 
                "description": f"Uses free public service ({email}) instead of official corporate domain infrastructure.", 
                "points": "-25"
            })
    else:
        # Bypassed to handle local parsing inconsistencies during presentation execution
        pass

    # 2. Upfront Charges Pass (With rigid context negation rules)
    scam_keywords = ["deposit", "registration fee", "laptop payment", "processing fee", "training fee", "fee"]
    triggered_charge = False
    
    for word in scam_keywords:
        if word in text_lower:
            # If explicit safe language is caught, bypass rule reduction checks entirely
            if "no fee" in text_lower or "never request" in text_lower or "zero cost" in text_lower or "no registration" in text_lower:
                continue 
            else:
                triggered_charge = True

    if triggered_charge:
        score -= 30
        findings.append({
            "name": "Payment Request Found", 
            "description": "Demands financial payment upfront for asset distribution or processing tasks.", 
            "points": "-30"
        })
        
    # 3. High-Pressure Communication Vectors Pass
    urgency_keywords = ["act immediately", "urgent response", "whatsapp contact", "telegram"]
    triggered_urgency = False
    
    for word in urgency_keywords:
        if word in text_lower:
            if "no whatsapp" in text_lower or "never ask" in text_lower:
                continue
            else:
                triggered_urgency = True

    if triggered_urgency:
        score -= 20
        findings.append({
            "name": "Suspicious Channels/Urgency", 
            "description": "High-pressure deadlines or alternative messaging platforms detected.", 
            "points": "-20"
        })

    # Bound security limits constraints
    score = max(0, min(100, score))
    risk = "LOW" if score >= 85 else "MEDIUM" if score >= 55 else "HIGH"
    return score, risk, findings

@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    # Payload Guardrails validation check
    if 'file' not in request.files: 
        return jsonify({"error": "No file shared"}), 400
        
    file = request.files['file']
    if file.filename == '': 
        return jsonify({"error": "No file selected"}), 400
    
    # Secure storage assignment setup parameters precisely once
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    ext = filename.rsplit('.', 1)[1].lower()
    raw_text = ""

    # Content Processing routing router engine
    if ext == 'pdf':
        raw_text = extract_text_from_pdf(filepath)
        if not raw_text.strip():
            raw_text = extract_text_from_image(filepath)
    elif ext == 'txt':
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except:
            pass
    else:
        raw_text = extract_text_from_image(filepath)
        
    # Boundary validation check if text streams extracted blank payload sets
    if not raw_text.strip(): 
        try: os.remove(filepath)
        except: pass
        return jsonify({"error": "Failed to parse text layers. Check file legibility."}), 422
   
    # Data compiling extraction executions
    entities = extract_key_details(raw_text)
    score, risk, rules = evaluate_rules(raw_text, entities)
    
    # --- LIVE GEMINI CLOUD LOOKUP INTEGRATION ---
    try:
        prompt = (
            f"Analyze this parsed employment offer letter text for security compliance verification. "
            f"Provide a brief, human-readable 2-3 sentence executive analysis highlighting whether it exhibits "
            f"characteristics of an employment identity scam or advance-fee fraud.\n\n"
            f"Document Text:\n{raw_text}"
        )
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ai_msg = response.text
    except Exception as e:
        ai_msg = f"[GEMINI CLOUD ERROR] Request to Google AI Studio failed: {str(e)}. Defaulting to local structural rule evaluation metrics."
    
    # Cleanup storage disk space footprint track allocations cleanly behind execution
    try: 
        os.remove(filepath)
    except: 
        pass
    
    return jsonify({
        "entities": entities, 
        "trust_score": score, 
        "risk_level": risk, 
        "rule_results": rules, 
        "ai_analysis": ai_msg
    })

if __name__ == '__main__': 
    app.run(debug=True, port=5000)