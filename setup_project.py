import os

# Define the folder tree layout
folders = [
    "templates",
    "static/css",
    "static/js",
    "uploads"
]

# Create folders if they don't exist
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"✔ Folder verified/created: {folder}")

# --- FILE CONTENT DEFINITIONS ---

files_content = {
    # 1. REQUIREMENTS FILE
    "requirements.txt": """flask==3.0.3
python-dotenv==1.0.1
pypdf==4.2.0
pytesseract==0.3.10
pillow==10.3.0
google-genai==0.1.1
""",

    # 2. HTML INTERFACE FILE
    "templates/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustBridge | AI Offer Letter Verifier</title>
    <link rel="stylesheet" href="{{ url_with_timestamp('static/css/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="container navbar">
            <div class="logo"><i class="fa-solid fa-shield-halved-sign"></i> Trust<span>Bridge</span></div>
            <button id="theme-toggle" class="btn btn-secondary"><i class="fa-solid fa-moon"></i> Dark Mode</button>
        </div>
    </header>
    <main class="container">
        <section class="hero">
            <h1>Verify the Authenticity of Your Job Offer</h1>
            <p>Protect yourself from employment scams. Upload your offer letter for an instant compliance check.</p>
        </section>
        <section class="upload-container">
            <form id="upload-form">
                <div class="drop-zone" id="drop-zone">
                    <i class="fa-solid fa-cloud-arrow-up upload-icon"></i>
                    <p>Drag & drop your offer letter here or <span class="browse-text">browse files</span></p>
                    <span class="file-info">Supports PDF, PNG, JPG (Max 5MB)</span>
                    <input type="file" id="file-input" name="file" accept=".pdf,.png,.jpg,.jpeg" style="display: none;">
                </div>
                <div id="file-selected-name" class="file-selected-name"></div>
                <button type="submit" class="btn btn-primary btn-block" id="submit-btn" disabled>Verify Offer Letter</button>
            </form>
        </section>
        <div class="loader-container" id="loader">
            <div class="spinner"></div>
            <p>Analyzing document security layout syntax...</p>
        </div>
        <section id="results-dashboard" class="results-dashboard" style="display: none;">
            <div class="dashboard-header">
                <h2>Analysis Dashboard</h2>
                <button onclick="window.print()" class="btn btn-secondary btn-sm">Download Report</button>
            </div>
            <div class="grid-layout">
                <div class="card score-card">
                    <h3>Trust Score</h3>
                    <div class="score-display"><span id="score-num">0</span><span class="score-max">/100</span></div>
                    <div class="risk-badge" id="risk-badge">Checking...</div>
                </div>
                <div class="card ai-card">
                    <h3><i class="fa-solid fa-brain"></i> Analysis Summary</h3>
                    <div id="ai-summary" class="ai-text">Analyzing...</div>
                </div>
            </div>
            <div class="card entities-card">
                <h3><i class="fa-solid fa-address-card"></i> Extracted Metadata</h3>
                <div class="entities-grid" id="entities-grid"></div>
            </div>
            <div class="card rules-card">
                <h3><i class="fa-solid fa-list-check"></i> Cybersecurity Rule Assessment</h3>
                <ul class="rule-list" id="rule-list"></ul>
            </div>
        </section>
        <section class="history-section card" style="margin-top: 2rem;">
            <h3><i class="fa-solid fa-history"></i> Recent Verifications</h3>
            <table class="history-table" style="width:100%; border-collapse:collapse; margin-top:1rem;">
                <thead>
                    <tr style="background:#f1f5f9; text-align:left;">
                        <th style="padding:10px;">Company</th><th style="padding:10px;">Role</th><th style="padding:10px;">Score</th>
                    </tr>
                </thead>
                <tbody id="history-rows"></tbody>
            </table>
        </section>
    </main>
    <script src="{{ url_with_timestamp('static/js/app.js') }}"></script>
</body>
</html>
""",

    # 3. CSS STYLING FILE
    "static/css/style.css": """:root {
    --bg-primary: #f8fafc; --bg-card: #ffffff; --text-main: #0f172a; --text-muted: #64748b;
    --border-color: #e2e8f0; --primary: #2563eb; --primary-hover: #1d4ed8; --success: #10b981; --danger: #ef4444; --radius: 12px;
}
[data-theme="dark"] {
    --bg-primary: #0f172a; --bg-card: #1e293b; --text-main: #f8fafc; --text-muted: #94a3b8; --border-color: #334155;
}
* { margin: 0; padding: 0; box-sizing: border-box; font-family: sans-serif; }
body { background-color: var(--bg-primary); color: var(--text-main); min-height: 100vh; padding: 1rem; }
.container { max-width: 1000px; margin: 0 auto; width: 100%; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--border-color); }
.logo { font-size: 1.5rem; font-weight: 700; color: var(--primary); }
.logo span { color: var(--text-main); }
.hero { text-align: center; margin: 2rem 0; }
.upload-container { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.drop-zone { border: 2px dashed var(--primary); border-radius: var(--radius); padding: 2.5rem; text-align: center; cursor: pointer; }
.upload-icon { font-size: 2.5rem; color: var(--primary); margin-bottom: 1rem; }
.file-selected-name { text-align: center; margin-top: 1rem; color: var(--success); font-weight: 600; }
.btn { padding: 0.75rem 1.5rem; font-weight: 600; border-radius: 8px; cursor: pointer; border: none; }
.btn-primary { background: var(--primary); color: white; }
.btn-block { display: block; width: 100%; margin-top: 1rem; }
.loader-container { display: none; text-align: center; margin: 2rem 0; }
.spinner { width: 40px; height: 40px; border: 4px solid var(--border-color); border-top: 4px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.grid-layout { display: grid; grid-template-columns: 1fr 2fr; gap: 1rem; margin-top: 2rem; }
.card { background: var(--bg-card); border: 1px solid var(--border-color); padding: 1.5rem; border-radius: var(--radius); margin-bottom: 1rem; }
.score-display { font-size: 3.5rem; font-weight: 800; }
.risk-badge { padding: 0.25rem 1rem; border-radius: 50px; display: inline-block; font-weight: 700; font-size: 0.85rem; }
.bg-safe { background: rgba(16,185,129,0.15); color: #059669; }
.bg-warning { background: rgba(245,158,17,0.15); color: #d97706; }
.bg-danger { background: rgba(239,64,64,0.15); color: #dc2626; }
.entities-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; }
.entity-item { background: var(--bg-primary); padding: 0.5rem; border-radius: 6px; border: 1px solid var(--border-color); }
.entity-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; }
.entity-val { font-weight: 600; }
.rule-list { list-style: none; margin-top: 1rem; }
.rule-list li { padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); }
""",

    # 4. JAVASCRIPT FRONTEND CONTROLLER
    "static/js/app.js": """document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileSelectedName = document.getElementById('file-selected-name');
    const uploadForm = document.getElementById('upload-form');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const resultsDashboard = document.getElementById('results-dashboard');
    let selectedFile = null;

    themeToggle.addEventListener('click', () => {
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
    });

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => { if(e.target.files.length) handleFile(e.target.files[0]); });
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); });
    dropZone.addEventListener('drop', (e) => { e.preventDefault(); if(e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });

    function handleFile(file) {
        selectedFile = file;
        fileSelectedName.textContent = `Selected: ${file.name}`;
        submitBtn.disabled = false;
    }

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', selectedFile);
        loader.style.display = 'block';
        resultsDashboard.style.display = 'none';

        try {
            const res = await fetch('/verify', { method: 'POST', body: formData });
            const data = await res.json();
            if(!res.ok) throw new Error(data.error);
            renderDashboard(data);
        } catch(err) { alert(err.message); }
        finally { loader.style.display = 'none'; }
    });

    function renderDashboard(data) {
        document.getElementById('score-num').textContent = data.trust_score;
        const badge = document.getElementById('risk-badge');
        badge.textContent = data.risk_level;
        badge.className = 'risk-badge ' + (data.risk_level === 'LOW' ? 'bg-safe' : data.risk_level === 'MEDIUM' ? 'bg-warning' : 'bg-danger');
        document.getElementById('ai-summary').textContent = data.ai_analysis;

        const grid = document.getElementById('entities-grid');
        grid.innerHTML = '';
        for(const [k, v] of Object.entries(data.entities)) {
            grid.innerHTML += `<div class="entity-item"><div class="entity-label">${k}</div><div class="entity-val">${v}</div></div>`;
        }

        const rList = document.getElementById('rule-list');
        rList.innerHTML = '';
        data.rule_results.forEach(r => {
            rList.innerHTML += `<li><strong>${r.name}</strong>: ${r.description} (${r.points})</li>`;
        });

        const hRows = document.getElementById('history-rows');
        hRows.innerHTML = `<tr><td style="padding:10px;">${data.entities.company || 'Unknown'}</td><td style="padding:10px;">${data.entities.role || 'Unknown'}</td><td style="padding:10px;">${data.trust_score}/100</td></tr>` + hRows.innerHTML;
        resultsDashboard.style.display = 'block';
    }
});
""",

    # 5. CORE FLASK PYTHON APP
    "app.py": """import os, re
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
import pytesseract

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "hackathon-secret")
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

@app.context_processor
def override_url_for():
    return dict(url_with_timestamp=lambda endpoint, **values: url_for(endpoint, v=int(os.stat(os.path.join(app.root_path, endpoint)).st_mtime), **values))

def extract_text_from_pdf(path):
    text = ""
    try:
        for page in PdfReader(path).pages:
            t = page.extract_text()
            if t: text += t + "\\n"
    except: pass
    return text

def extract_text_from_image(path):
    try: return pytesseract.image_to_string(Image.open(path))
    except: return ""

def extract_key_details(text):
    details = {"company": "Not Detected", "candidate": "Not Detected", "email": "Not Detected", "role": "Not Detected", "salary": "Not Detected", "date": "Not Detected"}
    emails = re.findall(r'[\\w\\.-]+@[\\w\\.-]+\\.\\w+', text)
    if emails: details["email"] = emails[0]
    salaries = re.findall(r'(?:INR|USD|\\$|₹|Rs\\.?)\\s*\\d+(?:,\\d+)*', text, re.IGNORECASE)
    if salaries: details["salary"] = salaries[0]
    
    lines = [l.strip() for l in text.split('\\n') if l.strip()]
    if lines: details["company"] = lines[0]
    for line in lines:
        if "dear" in line.lower(): details["candidate"] = line.replace("Dear", "").strip(", ")
        if "role" in line.lower() or "position" in line.lower(): details["role"] = line
    return details

def evaluate_rules(text, entities):
    score = 100
    findings = []
    email = entities["email"].lower()
    
    if email != "not detected":
        if any(p in email for p in ["gmail.com", "yahoo.com", "hotmail.com"]):
            score -= 25
            findings.append({"name": "Free Email Used", "description": f"Uses free service ({email}) instead of corporate domain.", "points": "-25"})
    else:
        score -= 15
        findings.append({"name": "No Contact Email", "description": "No outreach address discovered.", "points": "-15"})

    if any(k in text.lower() for k in ["deposit", "registration fee", "laptop payment", "processing fee"]):
        score -= 30
        findings.append({"name": "Payment Request Found", "description": "Demands payment upfront for onboarding or assets.", "points": "-30"})
        
    if any(k in text.lower() for k in ["act immediately", "urgent response", "whatsapp contact", "telegram"]):
        score -= 20
        findings.append({"name": "Suspicious Channels/Urgency", "description": "High-pressure words or off-platform messaging channels detected.", "points": "-20"})

    score = max(0, min(100, score))
    risk = "LOW" if score >= 85 else "MEDIUM" if score >= 55 else "HIGH"
    return score, risk, findings

@app.route('/')
def home(): return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    if 'file' not in request.files: return jsonify({"error": "No file shared"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    ext = filename.rsplit('.', 1)[1].lower()
    raw_text = extract_text_from_pdf(filepath) if ext == 'pdf' else extract_text_from_image(filepath)
    if not raw_text.strip() and ext == 'pdf': raw_text = extract_text_from_image(filepath)
    
    if not raw_text.strip(): return jsonify({"error": "Failed to parse text layers."}), 422
    
    entities = extract_key_details(raw_text)
    score, risk, rules = evaluate_rules(raw_text, entities)
    
    ai_msg = "[FALLBACK MODE ACTIVE] TrustBridge successfully executed local security checking rules logic on device. Skipping cloud lookup."
    
    try: os.remove(filepath)
    except: pass
    
    return jsonify({"entities": entities, "trust_score": score, "risk_level": risk, "rule_results": rules, "ai_analysis": ai_msg})

if __name__ == '__main__': app.run(debug=True, port=5000)
"""
}

# Write files natively out
for file_path, content in files_content.items():
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✔ File generated successfully: {file_path}")

print("\n🚀 SUCCESS! Your entire project structure is generated. You are fully organized!")