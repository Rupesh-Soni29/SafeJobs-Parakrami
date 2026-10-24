import sqlite3
from database.db import get_db_connection

def check_company_report_history(query):
    """
    Checks if a company, sender email, domain, or phone number has been reported
    by anyone in the past.
    """
    if not query:
        return {"reported": False, "count": 0, "reports": [], "threat_level": "UNKNOWN"}

    conn = get_db_connection()
    cursor = conn.cursor()
    
    clean_q = f"%{query.strip().lower()}%"
    
    cursor.execute('''
        SELECT * FROM reports 
        WHERE LOWER(company_name) LIKE ? 
           OR LOWER(sender_email) LIKE ? 
           OR LOWER(sender_domain) LIKE ? 
           OR sender_phone LIKE ?
        ORDER BY date_reported DESC
    ''', (clean_q, clean_q, clean_q, clean_q))
    
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    count = len(rows)
    total_loss = sum(r.get("loss_amount") or 0 for r in rows)
    
    if count >= 3:
        threat_level = "CRITICAL"
        threat_badge = "High Community Scam Alert"
        threat_color = "danger"
    elif count >= 1:
        threat_level = "HIGH"
        threat_badge = "Reported Scam Activity"
        threat_color = "danger"
    else:
        threat_level = "CLEAN"
        threat_badge = "No Prior Scam Reports in SafeJobs Database"
        threat_color = "success"

    return {
        "query": query,
        "reported": count > 0,
        "count": count,
        "total_reported_loss": total_loss,
        "threat_level": threat_level,
        "threat_badge": threat_badge,
        "threat_color": threat_color,
        "reports": rows
    }

def submit_new_report(data):
    """Submits a new community scam report to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reports (
            company_name, sender_email, sender_phone, sender_domain,
            job_title, scam_type, description, loss_amount, evidence_file,
            reported_by, city, status, risk_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("company_name", "Unknown Company"),
        data.get("sender_email", ""),
        data.get("sender_phone", ""),
        data.get("sender_domain", ""),
        data.get("job_title", "Unspecified"),
        data.get("scam_type", "Other Scam"),
        data.get("description", "No description provided"),
        float(data.get("loss_amount", 0) or 0),
        data.get("evidence_file", ""),
        data.get("reported_by", "Anonymous Jobseeker"),
        data.get("city", "Global"),
        "Verified Scam",
        "High"
    ))
    
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_recent_reports(limit=10):
    """Returns the most recent scam reports filed by the community."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM reports 
        ORDER BY date_reported DESC 
        LIMIT ?
    ''', (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
