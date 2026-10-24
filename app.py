import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from config import Config
from database.db import init_db
from services.gemini_analyzer import (
    analyze_recruitment_text,
    analyze_recruitment_image,
    call_gemini_api
)
from services.career_verifier import verify_job_vacancy, get_all_registered_companies
from services.scam_database import (
    check_company_report_history,
    submit_new_report,
    get_recent_reports
)
from services.domain_checker import scrutinize_domain

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database is initialized
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Renders the main SafeJobs dashboard."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for cloud hosting."""
    return jsonify({"status": "healthy", "service": "SafeJobs Verifier"}), 200

# ----------------- AI SCRUTINIZER APIS -----------------

@app.route('/api/analyze/text', methods=['POST'])
def api_analyze_text():
    """
    Scrutinizes recruitment email/message text and sender domain.
    """
    data = request.get_json() or {}
    text_content = data.get('text_content', '').strip()
    sender_email = data.get('sender_email', '').strip()
    claimed_company = data.get('claimed_company', '').strip()
    api_key = data.get('api_key', '').strip()

    if not text_content and not sender_email:
        return jsonify({"error": "Please provide either the message text or sender email address."}), 400

    # Perform analysis
    result = analyze_recruitment_text(
        text_content=text_content,
        sender_email=sender_email,
        claimed_company=claimed_company,
        custom_key=api_key
    )

    # Check if this company or domain was previously reported in our community DB
    comp_query = claimed_company or (result.get("company_identified") if result.get("company_identified") != "Unknown" else sender_email)
    report_history = check_company_report_history(comp_query) if comp_query else None
    result["report_history"] = report_history

    # Also automatically cross-check official career portal if company is identified
    if comp_query and comp_query.lower() not in ["unknown", "unspecified company", "none"]:
        career_check = verify_job_vacancy(comp_query, result.get("job_role_identified", ""))
        result["official_career_check"] = career_check

    return jsonify({"success": True, "data": result})

@app.route('/api/analyze/image', methods=['POST'])
def api_analyze_image():
    """
    Scrutinizes uploaded recruitment screenshot (WhatsApp, Telegram, Offer Letter, Email).
    """
    if 'image_file' not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files['image_file']
    if file.filename == '':
        return jsonify({"error": "No image selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed formats: PNG, JPG, JPEG, WEBP."}), 400

    # Save file safely
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"scan_{uuid.uuid4().hex[:12]}.{ext}"
    saved_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file.save(saved_path)

    notes = request.form.get('notes', '')
    api_key = request.form.get('api_key', '')

    result = analyze_recruitment_image(
        image_path=saved_path,
        additional_notes=notes,
        custom_key=api_key
    )

    # Cross-reference with scam database & careers portal
    comp = result.get("company_identified", "")
    if comp and comp.lower() not in ["unknown", "unspecified company", "none"]:
        result["report_history"] = check_company_report_history(comp)
        result["official_career_check"] = verify_job_vacancy(comp, result.get("job_role_identified", ""))

    result["uploaded_image_url"] = f"/static/uploads/{unique_name}"
    return jsonify({"success": True, "data": result})

# ----------------- CAREERS PAGE VERIFIER APIS -----------------

@app.route('/api/careers/verify', methods=['GET'])
def api_verify_careers():
    """
    Verifies if a specific job opening is genuinely published on the company's official Careers page.
    """
    company = request.args.get('company', '').strip()
    role = request.args.get('role', '').strip()

    if not company:
        return jsonify({"error": "Company name is required."}), 400

    result = verify_job_vacancy(company, role)
    # Also fetch past scam reports for this company
    history = check_company_report_history(company)
    result["scam_report_history"] = history

    return jsonify({"success": True, "data": result})

@app.route('/api/careers/companies', methods=['GET'])
def api_list_companies():
    """Returns list of registered corporations with verified career portals."""
    companies = get_all_registered_companies()
    return jsonify({"success": True, "companies": companies})

# ----------------- SCAM DATABASE & REPORT HISTORY APIS -----------------

@app.route('/api/reports/check', methods=['GET'])
def api_check_reports():
    """
    Checks if a company, email, phone number, or domain has been reported in the past.
    """
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "Search query is required."}), 400

    result = check_company_report_history(query)
    return jsonify({"success": True, "data": result})

@app.route('/api/reports/submit', methods=['POST'])
def api_submit_report():
    """
    Allows jobseekers to report a recruitment scam with evidence.
    """
    company_name = request.form.get('company_name', '').strip()
    scam_type = request.form.get('scam_type', '').strip()
    description = request.form.get('description', '').strip()

    if not company_name or not description:
        return jsonify({"error": "Company name and incident description are required."}), 400

    evidence_filename = ""
    if 'evidence_file' in request.files:
        file = request.files['evidence_file']
        if file and file.filename != '' and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            evidence_filename = f"evidence_{uuid.uuid4().hex[:10]}.{ext}"
            file.save(os.path.join(Config.UPLOAD_FOLDER, evidence_filename))

    data = {
        "company_name": company_name,
        "sender_email": request.form.get('sender_email', '').strip(),
        "sender_phone": request.form.get('sender_phone', '').strip(),
        "sender_domain": request.form.get('sender_domain', '').strip(),
        "job_title": request.form.get('job_title', '').strip(),
        "scam_type": scam_type or "Employment Scam",
        "description": description,
        "loss_amount": request.form.get('loss_amount', 0),
        "evidence_file": evidence_filename,
        "reported_by": request.form.get('reported_by', 'Anonymous Jobseeker').strip() or 'Anonymous Jobseeker',
        "city": request.form.get('city', 'Global').strip() or 'Global'
    }

    report_id = submit_new_report(data)
    return jsonify({"success": True, "message": "Scam report successfully submitted to the SafeJobs database.", "report_id": report_id})

@app.route('/api/reports/recent', methods=['GET'])
def api_recent_reports():
    """Returns recent scam alerts from the community."""
    limit = int(request.args.get('limit', 10))
    reports = get_recent_reports(limit)
    return jsonify({"success": True, "reports": reports})

# ----------------- GEMINI KEY VALIDATOR & STATUS -----------------

@app.route('/api/gemini/status', methods=['GET'])
def api_gemini_status():
    """Returns the current Gemini API key status from environment or cache."""
    from services.gemini_analyzer import get_effective_api_key, discover_working_model
    key = get_effective_api_key()
    has_key = bool(key and len(key) > 10)
    model = discover_working_model(key) if has_key else "gemini-3.8-flash"
    return jsonify({"has_key": has_key, "model": model})

@app.route('/api/gemini/test-key', methods=['POST'])
def api_test_key():
    """Tests if a user provided Gemini API key or .env key is functional."""
    from services.gemini_analyzer import get_effective_api_key, discover_working_model, ping_gemini
    data = request.get_json() or {}
    key = data.get('api_key', '').strip()
    if not key:
        key = get_effective_api_key()
    if not key:
        return jsonify({"valid": False, "message": "No API key found in request or .env file."}), 400
    try:
        model = discover_working_model(key)
        ping_gemini(key, model_name=model)
        return jsonify({"valid": True, "message": f"Connected to Google Gemini ({model}) successfully!", "model": model})
    except Exception as e:
        return jsonify({"valid": False, "message": f"Verification failed: {str(e)}"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
