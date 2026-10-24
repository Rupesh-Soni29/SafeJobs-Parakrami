import json
import sqlite3
import re
from database.db import get_db_connection

def find_company_in_db(company_name):
    """Finds verified company record by name or alias."""
    if not company_name:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    
    clean_name = company_name.strip().lower()
    
    # Try exact match or alias match
    cursor.execute("SELECT * FROM official_companies")
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        name_lower = row["name"].lower()
        aliases = [a.strip().lower() for a in (row["aliases"] or "").split(",") if a.strip()]
        
        if clean_name in name_lower or name_lower in clean_name:
            return dict(row)
        for alias in aliases:
            if alias in clean_name or clean_name in alias:
                return dict(row)
                
    return None

def verify_job_vacancy(company_name, job_title=""):
    """
    Scrutinizes whether the company genuinely has an active posting on their official
    careers portal for the specified job role.
    """
    comp_record = find_company_in_db(company_name)
    clean_job = (job_title or "").strip().lower()

    if not comp_record:
        # Company not in our official registry
        return {
            "verified": False,
            "status": "UNREGISTERED_OR_UNKNOWN_COMPANY",
            "company_name": company_name,
            "badge": "Caution: Unverified Employer",
            "badge_color": "warning",
            "message": f"'{company_name}' is not in the certified global corporate registry. Exercise caution. Search the company's official corporate domain and check if they have a dedicated career section.",
            "official_portal": None,
            "official_domain": None,
            "matched_job": None,
            "active_listings": [],
            "red_flag_notes": [
                "Verify if the company has a physical headquarters, legitimate business registration, and professional website.",
                "Ensure recruitment emails come from an established company domain, not free webmail (@gmail.com, @yahoo.com)."
            ]
        }

    # Company found in official registry
    active_listings = json.loads(comp_record["active_listings"]) if comp_record["active_listings"] else []
    official_domain = comp_record["official_domain"]
    official_portal = comp_record["official_careers_url"]
    policy = comp_record["verified_policy"]

    matched_job = None
    if clean_job:
        job_keywords = set(re.findall(r'\w+', clean_job))
        best_score = 0
        for job in active_listings:
            title_lower = job["title"].lower()
            title_words = set(re.findall(r'\w+', title_lower))
            overlap = len(job_keywords.intersection(title_words))
            if overlap > best_score and overlap >= 1:
                best_score = overlap
                matched_job = job

    # If job is matched with official active opening
    if matched_job:
        return {
            "verified": True,
            "status": "OFFICIALLY_VERIFIED_ON_CAREERS_PAGE",
            "company_name": comp_record["name"],
            "badge": "Verified Active Job Opening",
            "badge_color": "success",
            "message": f"Matching opening confirmed on the official {comp_record['name']} Careers portal!",
            "official_portal": official_portal,
            "official_domain": official_domain,
            "policy": policy,
            "matched_job": matched_job,
            "all_openings_count": len(active_listings),
            "verification_details": {
                "official_job_id": matched_job.get("job_id"),
                "official_role_title": matched_job.get("title"),
                "department": matched_job.get("department"),
                "location": matched_job.get("location"),
                "experience_required": matched_job.get("experience"),
                "official_requirements": matched_job.get("requirements"),
                "direct_application_url": matched_job.get("official_url")
            },
            "comparison": {
                "legitimate_application_process": f"Apply ONLY directly on {official_portal}. Never wire money or send verification fees.",
                "official_screening": "Conducted through certified enterprise video conferencing (Zoom/Webex/Teams/Google Meet) or on-campus interviews, NEVER via text chat on Telegram/WhatsApp."
            }
        }
    else:
        # Role NOT found on official careers portal!
        return {
            "verified": False,
            "status": "NO_OFFICIAL_POSTING_FOUND",
            "company_name": comp_record["name"],
            "badge": "No Official Careers Posting Found",
            "badge_color": "danger",
            "message": f"{comp_record['name']} does NOT have an active public vacancy for '{job_title or 'this role'}' on their official careers portal.",
            "official_portal": official_portal,
            "official_domain": official_domain,
            "policy": policy,
            "matched_job": None,
            "available_openings": active_listings,
            "red_flag_notes": [
                f"HIGH RISK: Scammers often create fake postings for '{job_title or 'entry-level'}' roles (e.g. data entry, proofreading, telegram assistant) pretending to be {comp_record['name']}.",
                f"{comp_record['name']} policy: {policy}",
                f"Always apply directly through the verified corporate careers site at {official_portal}."
            ]
        }

def get_all_registered_companies():
    """Returns list of registered verified companies."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, official_domain, official_careers_url, verified_policy FROM official_companies ORDER BY name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
