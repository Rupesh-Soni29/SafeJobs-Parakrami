import os
import json
import base64
import re
import requests
from config import Config
from services.domain_checker import scrutinize_domain, extract_email_address, extract_domain

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

SYSTEM_INSTRUCTION = """
You are SafeJobs AI, an elite cybersecurity fraud investigator and corporate recruitment verification auditor.
Your job is to scrutinize recruitment emails, offer letters, job vacancy postings, SMS, WhatsApp, and Telegram messages for scams, fraud, phishing, advance-fee rackets, and corporate impersonation.

Evaluate the content rigorously against standard employment fraud indicators:
1. Sender Domain vs Claimed Enterprise: Legitimate corporations (Google, Amazon, TCS, Microsoft, etc.) never recruit from free emails (@gmail.com, @yahoo.com) or suspicious domains.
2. Advance Fees & Equipment: Legitimate companies NEVER demand upfront payment for equipment, laptops, registration, interview badges, or background checks.
3. Chat App Interviews: Hiring solely over Telegram, WhatsApp, or Signal text chat without video interviews or official corporate applicant tracking systems is almost always a scam.
4. Too Good to Be True Compensation: Absurdly high pay ($50/hr for simple data entry, ₹5000/day for liking videos) is a classic hook.
5. Urgency & Suspicious Formatting: High-pressure deadlines, generic salutations ("Dear Beneficiary/Applicant"), grammatical errors, fake stamps, or stolen corporate logos.

CRITICAL REQUIREMENT:
You MUST output strictly raw, valid JSON with no markdown wrapping, no backticks, and no preamble:
{
  "scam_score": <integer from 0 to 100, where 0 is 100% legitimate and 100 is definite scam>,
  "verdict": "<DEFINITE_SCAM | SUSPICIOUS | LIKELY_LEGITIMATE>",
  "verdict_title": "<short 3-5 word verdict headline>",
  "company_identified": "<name of claimed company or 'Unknown'>",
  "job_role_identified": "<job title mentioned or 'Not specified'>",
  "sender_address_identified": "<email or phone or handle detected or 'None'>",
  "salary_offered": "<claimed compensation or 'Not specified'>",
  "interview_platform": "<e.g. Telegram, WhatsApp, Workday, Google Meet, Onsite, Email>",
  "fee_demanded": <true if upfront money/deposit is asked, false otherwise>,
  "fee_details": "<amount and reason or 'None'>",
  "red_flags": [
    "<red flag 1>",
    "<red flag 2>"
  ],
  "green_flags": [
    "<positive legitimate indicators if any>"
  ],
  "detailed_analysis": "<thorough 2-3 paragraph breakdown explaining the technical and contextual findings>",
  "safety_recommendations": [
    "<practical action step 1>",
    "<practical action step 2>",
    "<practical action step 3>"
  ]
}
"""

def get_effective_api_key(custom_key=None):
    """Retrieves API key from parameter or environment."""
    if custom_key and len(custom_key.strip()) > 10:
        return custom_key.strip()
    return Config.GEMINI_API_KEY.strip() if Config.GEMINI_API_KEY else ""

def analyze_recruitment_text(text_content, sender_email="", claimed_company="", custom_key=None):
    """
    Scrutinizes recruitment email/message text using Gemini AI with fallback to local heuristics.
    """
    api_key = get_effective_api_key(custom_key)
    
    # Run domain check first
    domain_data = {}
    detected_email = sender_email or extract_email_address(text_content)
    if detected_email:
        domain_data = scrutinize_domain(detected_email, claimed_company)
    
    # If Gemini API key is available, call Gemini 1.5 Flash
    if api_key:
        try:
            ai_result = call_gemini_api(
                prompt=f"Scrutinize this recruitment message and sender details:\n\nSender Email/Contact: {sender_email}\nClaimed Company: {claimed_company}\n\nMessage Body:\n{text_content}",
                api_key=api_key
            )
            if ai_result:
                # Merge domain insights into AI result
                ai_result["domain_analysis"] = domain_data
                ai_result["analysis_engine"] = "Gemini 1.5 Flash Multimodal AI"
                return ai_result
        except Exception as e:
            print(f"Gemini API call failed, falling back to local heuristic engine: {e}")

    # Fallback to local heuristic engine
    result = run_heuristic_analysis(text_content, detected_email, claimed_company)
    result["domain_analysis"] = domain_data
    result["analysis_engine"] = "SafeJobs Advanced Heuristic Engine (Connect Gemini API Key for Multimodal AI)"
    return result

def analyze_recruitment_image(image_path, additional_notes="", custom_key=None):
    """
    Scrutinizes uploaded screenshot / image using Gemini Multimodal Vision API.
    """
    api_key = get_effective_api_key(custom_key)
    
    if api_key and os.path.exists(image_path):
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            b64_data = base64.b64encode(img_bytes).decode("utf-8")
            
            ext = os.path.splitext(image_path)[1].lower().replace(".", "")
            mime = "image/jpeg"
            if ext == "png":
                mime = "image/png"
            elif ext == "webp":
                mime = "image/webp"

            prompt = f"Scrutinize this recruitment screenshot (chat message, offer letter, email, or job poster). Inspect logos, sender contacts, formatting, grammatical errors, and financial demands. Additional user context: {additional_notes}"
            
            payload = {
                "system_instruction": {
                    "parts": [{"text": SYSTEM_INSTRUCTION}]
                },
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime,
                                    "data": b64_data
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.9,
                    "maxOutputTokens": 1500
                }
            }

            url = f"{GEMINI_API_URL}?key={api_key}"
            headers = {"Content-Type": "application/json"}
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
                cleaned_text = clean_json_response(candidate_text)
                parsed = json.loads(cleaned_text)
                parsed["analysis_engine"] = "Gemini 1.5 Flash Vision Multimodal AI"
                return parsed
            else:
                print(f"Gemini Vision API error HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"Vision API exception: {e}")

    # Fallback image heuristic: Inspect file name and context
    fallback = run_heuristic_analysis(
        f"Screenshot uploaded for analysis. Context: {additional_notes}",
        sender_email="",
        claimed_company=""
    )
    fallback["analysis_engine"] = "SafeJobs Visual Heuristic Engine (Provide Gemini API Key for deep OCR & visual inspection)"
    fallback["red_flags"].append("Image uploaded. For complete OCR extraction of visual letterheads, stamps, and chat screenshots, enter your Gemini API Key in the top navigation bar.")
    return fallback

def call_gemini_api(prompt, api_key):
    """Calls Gemini REST endpoint with strict JSON schema."""
    url = f"{GEMINI_API_URL}?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.9,
            "maxOutputTokens": 1500
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    if resp.status_code == 200:
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        cleaned_text = clean_json_response(raw_text)
        return json.loads(cleaned_text)
    else:
        raise Exception(f"Gemini API returned HTTP {resp.status_code}: {resp.text}")

def clean_json_response(raw_text):
    """Strips markdown code fences like ```json ... ```."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def run_heuristic_analysis(text, sender_email="", claimed_company=""):
    """
    Deterministic rule-based NLP engine analyzing recruitment fraud signals.
    Guarantees SafeJobs works instantly out-of-the-box even before an API key is entered.
    """
    text_lower = text.lower()
    score = 15  # baseline
    red_flags = []
    green_flags = []
    
    # 1. Financial fee requests
    fee_indicators = [
        ("registration fee", "Demands registration/processing fee before interview."),
        ("security deposit", "Requests security deposit for interview or laptop equipment."),
        ("deposit", "Requests upfront money or equipment deposit before hiring."),
        ("laptop fee", "Requests payment or deposit for company laptop/MacBook."),
        ("processing fee", "Charges candidate a processing fee to proceed."),
        ("verification fee", "Requests payment for background/medical verification."),
        ("training kit", "Asks candidate to purchase training material or kit."),
        ("cheque", "Mentions sending a check/cheque to buy home office supplies (Classic fake check fraud)."),
        ("cashier check", "Mentions cashier check payment (Advance check cashing scam)."),
        ("crypto", "Instructs payment or withdrawal via cryptocurrency / Bitcoin / USDT."),
        ("wire transfer", "Demands payment via direct bank wire / Zelle / CashApp."),
        ("cashapp", "Instructs payment via personal CashApp / Zelle / Venmo."),
        ("gift card", "Demands payment via Apple / Steam / Amazon gift cards.")
    ]
    fee_demanded = False
    fee_details = "None"
    for phrase, explanation in fee_indicators:
        if phrase in text_lower:
            fee_demanded = True
            fee_details = phrase.title()
            score += 35
            red_flags.append(f"FINANCIAL RED FLAG: {explanation}")
            break

    # 2. Chat app interview channels
    chat_channels = [
        ("telegram", "Directs candidate to an anonymous Telegram handle (@...) for interview."),
        ("whatsapp", "Directs interview strictly to WhatsApp without formal ATS application."),
        ("signal", "Directs interview to Signal messenger."),
        ("skype", "Requires text-only Skype chat interview.")
    ]
    interview_platform = "Official / Unspecified"
    for ch, explanation in chat_channels:
        if ch in text_lower:
            interview_platform = ch.title()
            score += 25
            red_flags.append(f"COMMUNICATION RED FLAG: {explanation}")
            break

    # 3. Task / Like-Subscribe Scam Patterns
    task_phrases = [
        ("like youtube", "Offers daily payment for liking YouTube videos (Task Scam)."),
        ("subscribe", "Asks to subscribe to channels or rate hotel bookings for daily payout."),
        ("daily profit", "Promises daily guaranteed profit/income for simple clicks."),
        ("vip task", "Mentions VIP or Prepaid tasks."),
        ("prepaid recharge", "Demands account recharge to unlock task commission.")
    ]
    for phrase, explanation in task_phrases:
        if phrase in text_lower:
            score += 35
            red_flags.append(f"TASK FRAUD PATTERN: {explanation}")
            break

    # 4. Email / Domain Discrepancy
    email = sender_email or extract_email_address(text)
    if email:
        domain = extract_domain(email)
        from services.domain_checker import FREE_EMAIL_DOMAINS
        if domain in FREE_EMAIL_DOMAINS:
            score += 30
            red_flags.append(f"DOMAIN RED FLAG: Recruiter uses public free email provider (@{domain}) instead of official company domain.")

    # 5. Urgency & Instant Hiring
    urgency_phrases = [
        ("immediate joining", "High pressure for immediate acceptance."),
        ("selected without interview", "Job offered without standard technical or HR interview."),
        ("offer letter attached", "Offer letter sent immediately without application process."),
        ("congratulations you have been selected", "Unsolicited selection message.")
    ]
    for phrase, explanation in urgency_phrases:
        if phrase in text_lower:
            score += 15
            red_flags.append(f"URGENCY/SELECTION RED FLAG: {explanation}")

    # 6. Check for legitimate signals
    if "https://" in text_lower and ("workday.com" in text_lower or "greenhouse.io" in text_lower or "lever.co" in text_lower):
        green_flags.append("Contains reference to reputable Applicant Tracking System (Workday/Greenhouse/Lever).")
        score -= 20

    # Cap score between 5 and 99
    score = min(max(score, 5), 98)
    
    if score >= 75:
        verdict = "DEFINITE_SCAM"
        verdict_title = "Critical Employment Scam Alert"
    elif score >= 45:
        verdict = "SUSPICIOUS"
        verdict_title = "Suspicious Recruitment Activity"
    else:
        verdict = "LIKELY_LEGITIMATE"
        verdict_title = "Low Risk / Likely Legitimate"

    return {
        "scam_score": score,
        "verdict": verdict,
        "verdict_title": verdict_title,
        "company_identified": claimed_company or "Unspecified Company",
        "job_role_identified": "Extracted from message",
        "sender_address_identified": email or "Unspecified",
        "salary_offered": "Extracted from message",
        "interview_platform": interview_platform,
        "fee_demanded": fee_demanded,
        "fee_details": fee_details,
        "red_flags": red_flags or ["No immediate severe red flags detected by heuristic scanner."],
        "green_flags": green_flags,
        "detailed_analysis": f"Our analysis evaluated this recruitment offer across domain authentication, financial requisitions, communication platforms, and urgency triggers. The calculated threat rating is {score}% ({verdict_title}). Always confirm vacancy listings on the company's verified corporate domain before disclosing sensitive information.",
        "safety_recommendations": [
            "NEVER transfer money, purchase gift cards, or deposit unknown checks for a job.",
            "Verify the role directly on the employer's official Careers page using the SafeJobs Vacancy Verifier tab.",
            "Inspect the sender's full email address header, not just the display name.",
            "Report fraudulent recruiter profiles to SafeJobs Community Scam Database."
        ]
    }
