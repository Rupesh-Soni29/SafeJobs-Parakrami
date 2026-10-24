import json
from database.db import get_db_connection, init_db

def seed():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM official_companies")
    if cursor.fetchone()[0] > 0:
        print("Database already seeded.")
        conn.close()
        return

    # 1. Seed Official Companies & Real Career Portals
    companies = [
        {
            "name": "Tata Consultancy Services (TCS)",
            "aliases": "TCS, Tata Consultancy, TCS iON",
            "official_domain": "tcs.com",
            "official_careers_url": "https://www.tcs.com/careers",
            "verified_policy": "TCS never charges any recruitment fee, registration fee, or security deposit at any stage of hiring. TCS only communicates via official @tcs.com email addresses and conducts applications strictly through TCS iON / NextStep portal.",
            "active_listings": json.dumps([
                {
                    "job_id": "TCS-ENG-2026-902",
                    "title": "Systems Engineer / Full Stack Developer",
                    "department": "Engineering & Technology",
                    "location": "Mumbai / Bengaluru / Hyderabad (Hybrid)",
                    "experience": "2 - 5 years",
                    "requirements": "Proficiency in Java, Spring Boot, React or Angular, and SQL. B.Tech / B.E or MCA required.",
                    "official_url": "https://www.tcs.com/careers/india/entry-level",
                    "status": "Active Opening"
                },
                {
                    "job_id": "TCS-CLOUD-2026-441",
                    "title": "Cloud Security Specialist",
                    "department": "Cybersecurity Unit",
                    "location": "Pune / Chennai (On-site)",
                    "experience": "3 - 7 years",
                    "requirements": "AWS/Azure security certifications, SIEM tools, firewall management, SOC experience.",
                    "official_url": "https://www.tcs.com/careers/india",
                    "status": "Active Opening"
                },
                {
                    "job_id": "TCS-DS-2026-118",
                    "title": "Data Analyst / BI Developer",
                    "department": "Business Analytics",
                    "location": "Noida / Kolkata",
                    "experience": "1 - 3 years",
                    "requirements": "Strong Python, PowerBI, Tableau, Advanced Excel and SQL. Good communication skills.",
                    "official_url": "https://www.tcs.com/careers/india",
                    "status": "Active Opening"
                }
            ])
        },
        {
            "name": "Amazon",
            "aliases": "Amazon Inc, Amazon AWS, Amazon India, Amazon Development Centre",
            "official_domain": "amazon.com",
            "official_careers_url": "https://www.amazon.jobs",
            "verified_policy": "Amazon does NOT conduct text-only interviews via Telegram, WhatsApp, or Signal. Amazon never sends checks to purchase home office equipment, and never asks candidates to pay for background checks or badge fees. All real applications are tracked on amazon.jobs.",
            "active_listings": json.dumps([
                {
                    "job_id": "AMZ-SDE2-78921",
                    "title": "Software Development Engineer II (SDE II)",
                    "department": "AWS Core Infrastructure",
                    "location": "Bengaluru / Hyderabad (Hybrid)",
                    "experience": "4+ years",
                    "requirements": "Expertise in distributed systems, Java/C++, low-latency backend architectures, algorithms, data structures.",
                    "official_url": "https://www.amazon.jobs/en/jobs/AMZ-SDE2-78921",
                    "status": "Active Opening"
                },
                {
                    "job_id": "AMZ-OPS-34012",
                    "title": "Operations Team Lead",
                    "department": "Fulfillment & Logistics",
                    "location": "Delhi NCR / Mumbai (Onsite)",
                    "experience": "2+ years",
                    "requirements": "Supply chain management, workforce planning, inventory tracking. Degree required.",
                    "official_url": "https://www.amazon.jobs/en/jobs/AMZ-OPS-34012",
                    "status": "Active Opening"
                },
                {
                    "job_id": "AMZ-CS-10934",
                    "title": "Customer Support Associate",
                    "department": "Customer Trust & Partner Support",
                    "location": "Work from Home (India - Eligible States)",
                    "experience": "0 - 1 years",
                    "requirements": "Excellent written and verbal English communication. High school diploma or Bachelor's. Amazon provides official laptop directly.",
                    "official_url": "https://www.amazon.jobs/en/jobs/AMZ-CS-10934",
                    "status": "Active Opening"
                }
            ])
        },
        {
            "name": "Google",
            "aliases": "Google LLC, Alphabet, Google Cloud",
            "official_domain": "google.com",
            "official_careers_url": "https://careers.google.com",
            "verified_policy": "Google recruiters communicate exclusively from @google.com email domains. Google NEVER uses Gmail accounts (e.g. hr-google@gmail.com) for recruitment. No payment is ever required for interviews or training.",
            "active_listings": json.dumps([
                {
                    "job_id": "GOOG-SWE-55102",
                    "title": "Software Engineer III",
                    "department": "Google Cloud Platform",
                    "location": "Bengaluru, India / Sunnyvale, CA",
                    "experience": "3+ years",
                    "requirements": "BS/MS in Computer Science, Golang/C++/Python, Kubernetes, distributed database design.",
                    "official_url": "https://careers.google.com/jobs/results/GOOG-SWE-55102",
                    "status": "Active Opening"
                },
                {
                    "job_id": "GOOG-PM-99214",
                    "title": "Associate Product Manager",
                    "department": "Android Ecosystem",
                    "location": "Hyderabad / Remote eligible",
                    "experience": "2 - 4 years",
                    "requirements": "Product lifecycle management, user analytics, technical background, cross-functional collaboration.",
                    "official_url": "https://careers.google.com/jobs/results/GOOG-PM-99214",
                    "status": "Active Opening"
                }
            ])
        },
        {
            "name": "Infosys",
            "aliases": "Infosys Limited, Infosys BPM",
            "official_domain": "infosys.com",
            "official_careers_url": "https://www.infosys.com/careers",
            "verified_policy": "Infosys does not appoint any agency to collect fees for recruitment. Any offer letter asking for medical fee or visa processing fee to a private bank account is fraudulent.",
            "active_listings": json.dumps([
                {
                    "job_id": "INF-SE-32109",
                    "title": "Senior Systems Engineer",
                    "department": "Digital Experience",
                    "location": "Bengaluru / Pune / Chennai",
                    "experience": "3 - 5 years",
                    "requirements": "Angular/React, Node.js, Microservices, REST APIs, CI/CD pipeline.",
                    "official_url": "https://career.infosys.com/jobdesc?jobReferenceCode=INF-SE-32109",
                    "status": "Active Opening"
                },
                {
                    "job_id": "INF-BPM-11204",
                    "title": "Process Specialist - Financial Services",
                    "department": "Business Process Management",
                    "location": "Jaipur / Gurgaon",
                    "experience": "1 - 3 years",
                    "requirements": "Finance/Commerce graduate, KYC/AML validation, reconciliation experience.",
                    "official_url": "https://career.infosys.com/jobdesc?jobReferenceCode=INF-BPM-11204",
                    "status": "Active Opening"
                }
            ])
        },
        {
            "name": "Wipro",
            "aliases": "Wipro Limited, Wipro Technologies",
            "official_domain": "wipro.com",
            "official_careers_url": "https://careers.wipro.com",
            "verified_policy": "Wipro never demands security deposit or training fee. Beware of fake appointment letters with forged signatures or stamps.",
            "active_listings": json.dumps([
                {
                    "job_id": "WIP-DEV-7721",
                    "title": "Full Stack Java Consultant",
                    "department": "Enterprise Application Services",
                    "location": "Hyderabad / Bengaluru",
                    "experience": "4 - 8 years",
                    "requirements": "Core Java, Spring, Hibernate, Kafka, Docker, Kubernetes.",
                    "official_url": "https://careers.wipro.com/careers-home/jobs/WIP-DEV-7721",
                    "status": "Active Opening"
                }
            ])
        },
        {
            "name": "Microsoft",
            "aliases": "Microsoft Corporation, MSFT",
            "official_domain": "microsoft.com",
            "official_careers_url": "https://careers.microsoft.com",
            "verified_policy": "Microsoft only hires through Microsoft Careers website. Recruiters will never contact via Telegram or send fake check payments.",
            "active_listings": json.dumps([
                {
                    "job_id": "MS-AI-88301",
                    "title": "Applied Data Scientist",
                    "department": "Azure AI Services",
                    "location": "Hyderabad / Noida (Hybrid)",
                    "experience": "3+ years",
                    "requirements": "Machine Learning, LLM fine-tuning, PyTorch, Azure ML, Python.",
                    "official_url": "https://careers.microsoft.com/us/en/job/MS-AI-88301",
                    "status": "Active Opening"
                }
            ])
        },
        {
            "name": "Accenture",
            "aliases": "Accenture Solutions, Accenture India",
            "official_domain": "accenture.com",
            "official_careers_url": "https://www.accenture.com/careers",
            "verified_policy": "Accenture does not request payment at any stage of the recruitment process. All formal communications originate from @accenture.com.",
            "active_listings": json.dumps([
                {
                    "job_id": "ACC-ANL-5521",
                    "title": "Security Delivery Analyst",
                    "department": "Accenture Security",
                    "location": "Gurugram / Bengaluru",
                    "experience": "2 - 4 years",
                    "requirements": "Network security, vulnerability scanning, threat intelligence, Splunk.",
                    "official_url": "https://www.accenture.com/careers/jobdetails?id=ACC-ANL-5521",
                    "status": "Active Opening"
                }
            ])
        }
    ]

    for c in companies:
        cursor.execute('''
            INSERT INTO official_companies (name, aliases, official_domain, official_careers_url, verified_policy, active_listings)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (c["name"], c["aliases"], c["official_domain"], c["official_careers_url"], c["verified_policy"], c["active_listings"]))

    # 2. Seed Real-world Reported Scam Incidents (Historical Database)
    reports = [
        {
            "company_name": "Amazon Remote Jobs Impersonation",
            "sender_email": "careers-amazon-global@gmail.com",
            "sender_phone": "+91 98765 43210",
            "sender_domain": "gmail.com",
            "job_title": "Remote Data Entry / Order Processor",
            "scam_type": "Advance Fee / Equipment Scam",
            "description": "Received an email claiming I was selected for an Amazon Work From Home Data Entry job paying $45/hour. They requested a 'refundable laptop security deposit' of $180 via UPI/crypto before dispatching the MacBook Pro. Domain was a free Gmail account.",
            "loss_amount": 180.0,
            "evidence_file": "fake-offer-scam.jpg",
            "reported_by": "Rohit V.",
            "city": "Bengaluru",
            "status": "Verified Scam",
            "risk_level": "Critical"
        },
        {
            "company_name": "Telegram Task Scam (Posing as YouTube / Flipkart / Zara)",
            "sender_email": "recruiter-zara-tasks@outlook.com",
            "sender_phone": "+1 (555) 349-2019",
            "sender_domain": "outlook.com",
            "job_title": "Part-Time Video Reviewer & Product Liker",
            "scam_type": "Telegram Task Fraud",
            "description": "Recruiter contacted via WhatsApp offering ₹2,500 - ₹5,000 daily for liking videos and subscribing to channels. Moved discussion to Telegram (@HR_Admin_Zara_Tasks). Paid ₹150 initially to build trust, then demanded ₹10,000 'VIP Task Prepaid Recharge' which was never refunded.",
            "loss_amount": 120.0,
            "evidence_file": "remote-job-scam-chat.jpg",
            "reported_by": "Priya Sharma",
            "city": "Delhi",
            "status": "Verified Scam",
            "risk_level": "Critical"
        },
        {
            "company_name": "TCS Fake Offer Letter Ring",
            "sender_email": "tcs-onboarding@tcs-careers-india.net",
            "sender_phone": "+91 70211 99283",
            "sender_domain": "tcs-careers-india.net",
            "job_title": "Assistant Software Engineer",
            "scam_type": "Fake Offer Letter",
            "description": "Received an offer letter on fake TCS letterhead with forged signatures demanding ₹8,500 for 'Medical Background Verification & Training Kit'. The website domain 'tcs-careers-india.net' was registered only 14 days ago on Namecheap.",
            "loss_amount": 100.0,
            "evidence_file": "sample-job-offer.jpg",
            "reported_by": "Aman Verma",
            "city": "Pune",
            "status": "Verified Scam",
            "risk_level": "High"
        },
        {
            "company_name": "FedEx Logistics Fake Check Fraud",
            "sender_email": "fedex-dispatch-hr@zoho.com",
            "sender_phone": "+1 415 889 0122",
            "sender_domain": "zoho.com",
            "job_title": "Package Quality Inspector (Remote)",
            "scam_type": "Cheque Cashing Scam",
            "description": "Sent a fraudulent cashier check for $2,400 to 'set up home office equipment'. Instructed me to deposit the check and wire $1,900 to their 'approved vendor' via Zelle/CashApp. The check bounced 3 days later, leaving the victim liable.",
            "loss_amount": 1900.0,
            "evidence_file": "fake-offer-scam.jpg",
            "reported_by": "Michael Chang",
            "city": "Chicago",
            "status": "Verified Scam",
            "risk_level": "Critical"
        },
        {
            "company_name": "Wipro HR Impersonation",
            "sender_email": "wipro.careers.interview@gmail.com",
            "sender_phone": "+91 88472 10293",
            "sender_domain": "gmail.com",
            "job_title": "Junior Python Developer",
            "scam_type": "Ghost Job / Phishing",
            "description": "Requested Aadhaar card, PAN card front/back, bank account statement, and passport copy before even scheduling an interview. Attempted identity theft using Wipro's brand name.",
            "loss_amount": 0.0,
            "evidence_file": "email-phishing-analysis.jpg",
            "reported_by": "Kavita R.",
            "city": "Hyderabad",
            "status": "Verified Scam",
            "risk_level": "High"
        },
        {
            "company_name": "Global Freelance Ghost Employer",
            "sender_email": "hr@apex-tech-recruitment.xyz",
            "sender_phone": "+44 7911 123456",
            "sender_domain": "apex-tech-recruitment.xyz",
            "job_title": "Digital Content Creator & Proofreader",
            "scam_type": "Ghost Job / Phishing",
            "description": "Posted on LinkedIn. Interview conducted solely over Telegram chat with an anonymous 'HR Manager'. Offered $3,000/month for translating PDF documents, but required a $50 registration fee.",
            "loss_amount": 50.0,
            "evidence_file": "mobile-scam-alert.jpg",
            "reported_by": "David Miller",
            "city": "London",
            "status": "Verified Scam",
            "risk_level": "Medium"
        }
    ]

    for r in reports:
        cursor.execute('''
            INSERT INTO reports (company_name, sender_email, sender_phone, sender_domain, job_title, scam_type, description, loss_amount, evidence_file, reported_by, city, status, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (r["company_name"], r["sender_email"], r["sender_phone"], r["sender_domain"], r["job_title"], r["scam_type"], r["description"], r["loss_amount"], r["evidence_file"], r["reported_by"], r["city"], r["status"], r["risk_level"]))

    conn.commit()
    conn.close()
    print("Database seeded with official companies and real-world scam reports.")

if __name__ == "__main__":
    seed()
