import sqlite3
import os
import json
from config import Config

def get_db_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            sender_email TEXT,
            sender_phone TEXT,
            sender_domain TEXT,
            job_title TEXT,
            scam_type TEXT NOT NULL,
            description TEXT NOT NULL,
            loss_amount REAL DEFAULT 0,
            evidence_file TEXT,
            reported_by TEXT DEFAULT 'Anonymous Jobseeker',
            city TEXT DEFAULT 'Global',
            date_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Verified Scam',
            risk_level TEXT DEFAULT 'High'
        )
    ''')
    
    # Verified companies and official career portals
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS official_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            aliases TEXT,
            official_domain TEXT NOT NULL,
            official_careers_url TEXT NOT NULL,
            verified_policy TEXT,
            active_listings TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
