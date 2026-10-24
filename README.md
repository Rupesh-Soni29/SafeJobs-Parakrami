# 🛡️ SafeJobs - Local Job Scam & Vacancy Verifier

SafeJobs is an AI-powered cybersecurity defense platform designed to protect jobseekers from fraudulent recruitment scams, fake appointment letters, task fraud rings, and unauthorized corporate impersonation.

Built with **Python (Flask), HTML5, CSS3, and modern JavaScript**, SafeJobs integrates **Google Gemini Multimodal AI** to scrutinize recruitment emails, inspect message screenshots, check community scam history, and verify vacancies against official corporate Careers pages in real time.

---

## 🚀 Key Features

### 1. 🔍 AI Recruitment Email & Message Scrutinizer
- **Sender Domain Verification**: Automatically detects free public email addresses (e.g. `hr.amazon@gmail.com`) claiming to represent major corporations.
- **Typosquatting & Lookalike Spoofing**: Detects deceptively similar domains (e.g. `tcs-careers-india.net`, `micros0ft-careers.com`, `careers-amazon-verify.com`).
- **Fraud Vector Analysis**: Flags upfront fees (laptop deposits, training kits, medical fees, background check charges), Telegram/WhatsApp-only interview channels, fake check schemes, and unrealistic salaries.
- **Multimodal AI Analysis**: Powered by Google's **Gemini 1.5 Flash AI** with automatic fallback to local heuristic NLP if an API key is not yet configured.

### 2. 📸 Screenshot & Offer Letter Vision OCR
- Upload screenshots of WhatsApp conversations, Telegram task groups, SMS recruitment offers, or scanned PDF/JPEG appointment letters.
- Multimodal Vision AI extracts text, inspects forged company letterheads/stamps, and identifies fraud signals directly from images.

### 3. 🏢 Official Careers Page & Vacancy Verifier
- **Cross-Platform Verification**: Checks whether a vacancy seen on WhatsApp, Telegram, LinkedIn, or external boards actually exists on the company's verified corporate Careers portal.
- **Detailed Opening Breakdown**: When confirmed, displays the official Job ID, verified department, genuine location/work-mode, skill prerequisites, and direct application links.
- **Cross-Platform Reality Matrix**: Side-by-side comparison between scammer promises (instant hire, paid kit) and the official company's certified zero-fee hiring policy.

### 4. 🛡️ Prior Scam Incident History & Community Tracker
- Search past fraud complaints by company name, recruiter email, phone number, or website domain.
- Displays community risk score, total financial losses reported, and historical incident testimonials.
- **Report a Scam**: Community reporting portal where jobseekers can submit new incidents with evidence to protect others.

### 5. 📚 Real-World Scam Gallery & Guide
- Includes locally downloaded real-world reference images demonstrating fake appointment letters, Telegram task schemes, phishing anatomy, and safe job search golden rules.

---

## 🛠️ Tech Stack (Strictly HTML, CSS, JS & Python)

- **Backend**: Python 3.10+, Flask, SQLite3, Requests, BeautifulSoup4, Pillow, Gunicorn
- **Frontend**: Vanilla HTML5, Modern CSS3 (Dark-mode Cybersecurity theme), Vanilla JavaScript (ES6+)
- **AI Integration**: Google Gemini 1.5 Flash (Multimodal Text & Vision)

---

## 📁 Project Architecture

```
SafeJobs 2/
├── app.py                      # Flask Application with REST APIs & Gemini Integration
├── config.py                   # Configuration & Gemini API key loading
├── requirements.txt            # Python dependencies
├── Procfile                    # Render / Railway / Heroku deployment config
├── render.yaml                 # Render Blueprint configuration
├── vercel.json                 # Vercel Serverless configuration
├── runtime.txt                 # Python runtime version
├── .env.example                # Environment variables template
├── test_app.py                 # Automated unit test suite (9 tests)
├── database/
│   ├── db.py                   # SQLite schema & database connection
│   ├── seed_data.py            # Pre-seeded official portals & historical scam reports
│   └── safejobs.db             # SQLite database file
├── services/
│   ├── gemini_analyzer.py      # Gemini Multimodal AI + Heuristic Fallback
│   ├── domain_checker.py       # Domain & Sender reputation scrutinizer
│   ├── career_verifier.py      # Official careers page vacancy verification
│   └── scam_database.py        # Community scam report queries & submission
├── static/
│   ├── css/
│   │   └── style.css           # Responsive cybersecurity theme
│   ├── js/
│   │   └── app.js              # Tab management, dropzone, AI results renderer
│   ├── images/                 # Downloaded real-world images from the Internet
│   │   ├── hero-security.jpg
│   │   ├── fake-offer-scam.jpg
│   │   ├── email-phishing-analysis.jpg
│   │   ├── remote-job-scam-chat.jpg
│   │   ├── mobile-scam-alert.jpg
│   │   ├── verified-careers.jpg
│   │   ├── community-warning.jpg
│   │   ├── sample-job-offer.jpg
│   │   └── sample-telegram-scam.jpg
│   └── uploads/                # User uploaded screenshots
└── templates/
    └── index.html              # Main dashboard
```

---

## 💻 Local Setup & Running

### 1. Clone or Open the Workspace
```bash
cd "SafeJobs 2"
```

### 2. Activate the Virtual Environment
**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Gemini API Key
You can set your Gemini API key in a `.env` file or directly inside the web UI using the top navigation bar's **"Gemini AI Key"** button:
```bash
# Copy example file
cp .env.example .env
```
Inside `.env`:
```ini
GEMINI_API_KEY=AIzaSyYourKeyHere...
```
*(Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

> **Note:** SafeJobs features an intelligent built-in heuristic scanner. Even if no Gemini API key is configured, all core scrutiny, domain verification, and career checks work out-of-the-box.

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

### 6. Run Automated Tests
```bash
python test_app.py
```

---

## 🌐 Free Cloud Deployment Instructions

### Option 1: Deploy on Render (Recommended - 100% Free)
1. Push this repository to GitHub or GitLab:
   ```bash
   git add .
   git commit -m "Initial commit for SafeJobs"
   git remote add origin https://github.com/your-username/safejobs.git
   git push -u origin master
   ```
2. Go to [Render.com](https://render.com) and sign in for free.
3. Click **"New +"** &rarr; **"Web Service"**.
4. Connect your GitHub repository.
5. Render will automatically detect `render.yaml` or fill in:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt && python -m database.seed_data`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: `Free`
6. (Optional) In **Environment Variables**, add `GEMINI_API_KEY`.
7. Click **"Create Web Service"**. Your app will be live with a free HTTPS URL (e.g. `https://safejobs.onrender.com`).

---

### Option 2: Deploy on Railway (Free Starter Tier)
1. Sign in to [Railway.app](https://railway.app).
2. Click **"New Project"** &rarr; **"Deploy from GitHub repo"**.
3. Select your repository. Railway automatically reads the included `Procfile` (`gunicorn app:app`).
4. Set `GEMINI_API_KEY` under the **Variables** tab.
5. Click **"Generate Domain"** under Networking to get your public URL.

---

### Option 3: Deploy on PythonAnywhere (Free Forever)
1. Register for a free account at [PythonAnywhere.com](https://www.pythonanywhere.com).
2. Open a Bash console and clone your repo or upload files.
3. Create a virtualenv: `mkvirtualenv --python=/usr/bin/python3.10 safejobs-venv`
4. Install packages: `pip install -r requirements.txt`
5. Under the **Web** tab, create a new web app pointing to `safejobs-venv` and your `app.py` WSGI handler.
6. Seed the DB: `python -m database.seed_data`
7. Click **Reload**.

---

## 🔒 Security Best Practices
- SafeJobs sanitizes all file uploads and uses secure UUIDs to prevent directory traversal.
- Passwords and personal data are never permanently cached.
- All community scam reports are stored locally in an embedded SQLite database.
