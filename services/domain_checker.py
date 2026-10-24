import re
from urllib.parse import urlparse

# Well-known free/public email providers
FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "live.com",
    "icloud.com", "mail.com", "protonmail.com", "proton.me", "zoho.com",
    "yandex.com", "rediffmail.com", "gmx.com", "fastmail.com", "aol.com"
}

# High-risk TLDs frequently used in rapid disposable phishing
SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".icu", ".buzz", ".online", ".site", ".tk", ".ml",
    ".cf", ".ga", ".gq", ".work", ".click", ".link", ".monster", ".fit"
}

# Major corporate domains to check for typosquatting / spoofing
KNOWN_LEGIT_DOMAINS = {
    "amazon": "amazon.com",
    "google": "google.com",
    "microsoft": "microsoft.com",
    "apple": "apple.com",
    "meta": "meta.com",
    "facebook": "meta.com",
    "netflix": "netflix.com",
    "tcs": "tcs.com",
    "tata": "tcs.com",
    "infosys": "infosys.com",
    "wipro": "wipro.com",
    "hcl": "hcltech.com",
    "cognizant": "cognizant.com",
    "accenture": "accenture.com",
    "ibm": "ibm.com",
    "deloitte": "deloitte.com",
    "ey": "ey.com",
    "pwc": "pwc.com",
    "kpmg": "kpmg.com",
    "goldman": "goldmansachs.com",
    "jpmorgan": "jpmorgan.com",
    "morganstanley": "morganstanley.com",
    "fedex": "fedex.com",
    "dhl": "dhl.com",
    "flipkart": "flipkart.com",
    "zara": "zara.com"
}

SUSPICIOUS_KEYWORDS = [
    "-careers", "-recruitment", "-hr", "-jobs", "-hiring", "-verify", 
    "-portal", "-global", "-online", "-career-portal", "-apply", "-interview"
]

def extract_email_address(raw_text):
    """Extracts email addresses from text."""
    if not raw_text:
        return None
    matches = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    return matches[0] if matches else None

def extract_domain(email_or_url):
    """Extracts clean domain from email or URL or raw domain string."""
    if not email_or_url:
        return ""
    email_or_url = email_or_url.strip().lower()
    if "@" in email_or_url:
        return email_or_url.split("@")[-1].strip()
    if email_or_url.startswith(("http://", "https://")):
        parsed = urlparse(email_or_url)
        return parsed.netloc or parsed.path
    # Clean possible paths or trailing slashes
    domain = email_or_url.split("/")[0].split(":")[0]
    return domain

def levenshtein_distance(s1, s2):
    """Calculate edit distance to detect typosquatting."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def scrutinize_domain(sender_email_or_domain, claimed_company=""):
    """
    Examines the sender domain against claimed company, free webmails,
    typosquatting, and deceptive subdomain structures.
    """
    domain = extract_domain(sender_email_or_domain)
    claimed_comp_lower = claimed_company.lower().strip() if claimed_company else ""
    
    analysis = {
        "domain": domain,
        "is_free_provider": False,
        "is_typosquatting": False,
        "is_suspicious_subdomain": False,
        "is_suspicious_tld": False,
        "official_domain_match": None,
        "domain_risk_score": 0,  # 0 to 100
        "risk_rating": "LOW",
        "red_flags": [],
        "explanation": ""
    }
    
    if not domain:
        analysis["explanation"] = "No sender domain provided for verification."
        return analysis

    # 1. Free Provider Check
    if domain in FREE_EMAIL_DOMAINS:
        analysis["is_free_provider"] = True
        analysis["domain_risk_score"] = 85
        flag = f"Sender uses public free email provider (@{domain}) instead of a verified corporate domain."
        if claimed_comp_lower:
            flag = f"CRITICAL: Claims to represent '{claimed_company}', but uses a free webmail service (@{domain}). Real corporate recruiters from reputable enterprises NEVER hire via free public email accounts."
            analysis["domain_risk_score"] = 95
        analysis["red_flags"].append(flag)

    # 2. Suspicious TLD Check
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            analysis["is_suspicious_tld"] = True
            analysis["domain_risk_score"] = max(analysis["domain_risk_score"], 70)
            analysis["red_flags"].append(f"Domain uses high-risk disposable TLD '{tld}', frequently used in cyber fraud & phishing.")
            break

    # 3. Suspicious Keywords in Domain (e.g. amazon-careers-verify.com)
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in domain:
            analysis["is_suspicious_subdomain"] = True
            analysis["domain_risk_score"] = max(analysis["domain_risk_score"], 75)
            analysis["red_flags"].append(f"Domain contains deceptive recruiter keyword '{kw}' (common tactic in impersonation spoofing).")
            break

    # 4. Typosquatting / Lookalike Check against known corporations
    base_name = domain.split(".")[0].replace("-", "")
    for brand_key, official_dom in KNOWN_LEGIT_DOMAINS.items():
        # If user claims this company or domain resembles it
        brand_match = (brand_key in claimed_comp_lower) if claimed_comp_lower else False
        brand_in_domain = (brand_key in domain)

        if brand_match or brand_in_domain:
            if domain == official_dom or domain.endswith("." + official_dom):
                analysis["official_domain_match"] = official_dom
                # Legitimate corporate domain
                if not analysis["is_free_provider"]:
                    analysis["domain_risk_score"] = min(analysis["domain_risk_score"], 15)
            else:
                # Discrepancy! Brand mentioned or in domain, but domain is NOT official
                analysis["is_typosquatting"] = True
                analysis["domain_risk_score"] = 90
                analysis["red_flags"].append(
                    f"DOMAIN SPOOFING: Official domain for {brand_key.title()} is '{official_dom}', but sender domain is '{domain}'."
                )

    # Calculate final rating
    score = analysis["domain_risk_score"]
    if score >= 75:
        analysis["risk_rating"] = "CRITICAL / SCAM"
    elif score >= 45:
        analysis["risk_rating"] = "SUSPICIOUS"
    else:
        analysis["risk_rating"] = "LIKELY LEGITIMATE"

    # Human-readable summary
    if not analysis["red_flags"]:
        analysis["explanation"] = f"The domain '{domain}' appears to be a standard custom domain without immediate public free webmail or obvious typosquatting red flags."
    else:
        analysis["explanation"] = " | ".join(analysis["red_flags"])

    return analysis
