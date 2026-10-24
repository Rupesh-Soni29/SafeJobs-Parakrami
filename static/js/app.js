/**
 * SafeJobs - Frontend Core Application Logic
 */

// State
let currentTab = 'tab-scrutinizer';
let currentScrutinizerMode = 'text';
let selectedFile = null;

// Demo Samples Data
const DEMO_SAMPLES = {
    amazon_data_entry: {
        sender: "amazon-recruitment-team@gmail.com",
        company: "Amazon",
        text: `From: Amazon HR Global <amazon-recruitment-team@gmail.com>
Subject: Job Offer: Remote Data Entry Associate ($45.00/Hour)

Dear Applicant,

Congratulations! Your resume has been shortlisted on Indeed/LinkedIn for our Remote Data Entry / Order Processor role at Amazon. 

Position Details:
- Role: Remote Data Entry Associate
- Compensation: $45.00/Hour (Paid weekly via direct deposit)
- Hours: Flexible 15-20 hours per week (Work from home)
- Experience: None required, comprehensive remote training provided.

Equipment & Joining Process:
Amazon will provide a brand new Apple MacBook Pro and home office kit. However, to dispatch the hardware, our insurance vendor requires a refundable security deposit of $180 via Zelle / CashApp or Apple Gift Card. This deposit will be credited back in your first paycheck.

Please connect immediately with our Hiring Manager on Telegram (@Amazon_HR_Recruitment_Desk) to finalize your onboarding and receive your employment contract.`
    },
    telegram_task: {
        sender: "+1 (555) 349-2019",
        company: "Zara Media Tasks",
        text: `Hello! I am Sarah from Zara Global Digital Marketing. We noticed your profile and have an urgent requirement for Part-Time Video Reviewers.

Work Description:
You only need a smartphone. Simply subscribe to YouTube channels, like videos, and rate hotels on Google Maps. 

Daily Income: ₹2,500 to ₹6,000 daily (Instant payout to your UPI/Bank).
Trial Task: Complete 3 likes now and get ₹150 trial bonus immediately!

To start your trial and receive task credentials, join our Official Receptionist on Telegram: https://t.me/Zara_VIP_Task_Manager`
    },
    tcs_fake_offer: {
        sender: "onboarding@tcs-careers-india.net",
        company: "Tata Consultancy Services (TCS)",
        text: `From: TCS Talent Acquisition <onboarding@tcs-careers-india.net>
Subject: Direct Selection Appointment Letter - Ref: TCS/HR/2026/8941

Dear Candidate,

Based on your profile screening, you have been selected for the position of Assistant Software Engineer at Tata Consultancy Services (TCS) with an annual CTC of ₹7.5 LPA.

As per TCS Company Policy for freshers, you are required to deposit a mandatory Medical Examination and Training Kit Fee of ₹8,500 into our accredited training vendor account within 48 hours to confirm your seat. 

Failure to submit the deposit before the deadline will lead to immediate cancellation of your appointment letter. Download the attached PDF offer letter containing banking details.`
    },
    legit_google: {
        sender: "recruiting@google.com",
        company: "Google",
        text: `From: Google Recruiting <recruiting@google.com>
Subject: Career Opportunity: Software Engineer III - Google Cloud Platform

Hi,

I came across your GitHub and LinkedIn profile and was impressed by your distributed systems work. We are currently looking for a Software Engineer III to join our Google Cloud Platform team in Bengaluru.

Role Details:
- Team: Google Cloud Core Infrastructure
- Location: Bengaluru, India (Hybrid)
- Required: 3+ years experience with Go/C++/Python, microservices architecture, and distributed storage systems.

If you are open to exploring this, you can view the official job opening details and apply directly through our careers portal:
https://careers.google.com/jobs/results/GOOG-SWE-55102

Please note Google never charges any recruitment or training fees, and interviews are conducted exclusively via Google Meet or in our offices.

Best regards,
Ananya Rao | Technical Recruiter | Google`
    }
};

// Initialization on DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
    initGeminiKey();
    loadVerifiedCompanies();
    loadRecentReports();
    setupDropzone();
});

// ================= NAVIGATION =================
function switchTab(tabId) {
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));

    const targetPanel = document.getElementById(tabId);
    if (targetPanel) {
        targetPanel.classList.add('active');
        currentTab = tabId;
    }

    const activeBtn = Array.from(document.querySelectorAll('.nav-btn')).find(b => b.getAttribute('onclick').includes(tabId));
    if (activeBtn) activeBtn.classList.add('active');

    window.scrollTo({ top: 380, behavior: 'smooth' });
}

function setScrutinizerMode(mode) {
    currentScrutinizerMode = mode;
    const textForm = document.getElementById('form-scrutinize-text');
    const imgForm = document.getElementById('form-scrutinize-image');
    const btnText = document.getElementById('btn-mode-text');
    const btnImg = document.getElementById('btn-mode-image');

    if (mode === 'text') {
        textForm.style.display = 'block';
        imgForm.style.display = 'none';
        btnText.classList.add('active');
        btnImg.classList.remove('active');
    } else {
        textForm.style.display = 'none';
        imgForm.style.display = 'block';
        btnText.classList.remove('active');
        btnImg.classList.add('active');
    }
}

// ================= DEMO SAMPLES =================
function loadSample(key) {
    const sample = DEMO_SAMPLES[key];
    if (!sample) return;

    setScrutinizerMode('text');
    document.getElementById('text-sender-email').value = sample.sender;
    document.getElementById('text-claimed-company').value = sample.company;
    document.getElementById('text-content').value = sample.text;

    showToast(`Loaded "${sample.company}" demo sample. Click "Scrutinize with AI" to test!`);
}

// ================= AI SCRUTINIZER: TEXT =================
async function handleTextAnalysis(e) {
    e.preventDefault();
    const textContent = document.getElementById('text-content').value.trim();
    const senderEmail = document.getElementById('text-sender-email').value.trim();
    const claimedCompany = document.getElementById('text-claimed-company').value.trim();

    if (!textContent && !senderEmail) {
        showToast("Please enter the email text or sender address.");
        return;
    }

    const btn = document.getElementById('btn-submit-text');
    setLoading(btn, true);

    const apiKey = getSavedGeminiKey();

    try {
        const response = await fetch('/api/analyze/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text_content: textContent,
                sender_email: senderEmail,
                claimed_company: claimedCompany,
                api_key: apiKey
            })
        });

        const data = await response.json();
        if (data.success && data.data) {
            renderScrutinyResults(data.data);
            showToast("Scrutiny analysis complete!");
        } else {
            showToast(data.error || "Analysis failed.", "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error connecting to SafeJobs server.", "error");
    } finally {
        setLoading(btn, false);
    }
}

// ================= AI SCRUTINIZER: IMAGE =================
function setupDropzone() {
    const dropzone = document.getElementById('image-dropzone');
    if (!dropzone) return;

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--primary-green)';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.style.borderColor = '';
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
}

function handleFileSelected(e) {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast("Please upload an image file (PNG, JPG, WEBP).", "error");
        return;
    }
    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('preview-img').src = e.target.result;
        document.getElementById('dropzone-prompt').style.display = 'none';
        document.getElementById('dropzone-preview').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function removeSelectedFile(e) {
    if (e) e.stopPropagation();
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('dropzone-prompt').style.display = 'block';
    document.getElementById('dropzone-preview').style.display = 'none';
    document.getElementById('preview-img').src = '';
}

async function handleImageAnalysis(e) {
    e.preventDefault();
    if (!selectedFile) {
        showToast("Please upload or drop an image screenshot first.", "error");
        return;
    }

    const btn = document.getElementById('btn-submit-image');
    setLoading(btn, true);

    const notes = document.getElementById('image-notes').value.trim();
    const apiKey = getSavedGeminiKey();

    const formData = new FormData();
    formData.append('image_file', selectedFile);
    formData.append('notes', notes);
    formData.append('api_key', apiKey);

    try {
        const response = await fetch('/api/analyze/image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.success && data.data) {
            renderScrutinyResults(data.data);
            showToast("Visual scrutiny complete!");
        } else {
            showToast(data.error || "Visual analysis failed.", "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error processing image on server.", "error");
    } finally {
        setLoading(btn, false);
    }
}

// ================= RENDER ANALYSIS RESULTS =================
function renderScrutinyResults(data) {
    document.getElementById('result-empty-state').style.display = 'none';
    const resultContent = document.getElementById('result-content');
    resultContent.style.display = 'block';

    const score = data.scam_score || 50;
    const scoreDial = document.getElementById('score-dial');
    const scoreVal = document.getElementById('res-score');
    scoreVal.innerText = score;

    // Set score colors
    if (score >= 70) {
        scoreDial.style.borderColor = 'var(--danger-red)';
        scoreDial.style.boxShadow = '0 0 16px rgba(217, 56, 58, 0.15)';
        document.getElementById('res-verdict-badge').className = 'verdict-badge badge-danger';
        document.getElementById('res-verdict-badge').innerText = 'CRITICAL SCAM ALERT';
    } else if (score >= 40) {
        scoreDial.style.borderColor = 'var(--warning-amber)';
        scoreDial.style.boxShadow = '0 0 16px rgba(217, 119, 6, 0.15)';
        document.getElementById('res-verdict-badge').className = 'verdict-badge badge-warning';
        document.getElementById('res-verdict-badge').innerText = 'SUSPICIOUS RECRUITMENT';
    } else {
        scoreDial.style.borderColor = 'var(--success-green)';
        scoreDial.style.boxShadow = '0 0 16px rgba(57, 120, 79, 0.15)';
        document.getElementById('res-verdict-badge').className = 'verdict-badge badge-success';
        document.getElementById('res-verdict-badge').innerText = 'LIKELY LEGITIMATE';
    }

    document.getElementById('res-verdict-title').innerText = data.verdict_title || 'Scrutiny Completed';
    document.getElementById('res-engine').innerText = `Engine: ${data.analysis_engine || 'Gemini Multimodal AI'}`;

    // Meta details
    document.getElementById('res-company').innerText = data.company_identified || 'Unknown';
    document.getElementById('res-role').innerText = data.job_role_identified || 'Not specified';
    document.getElementById('res-channel').innerText = data.interview_platform || 'Unspecified';
    document.getElementById('res-salary').innerText = data.salary_offered || 'Not mentioned';
    document.getElementById('res-fee').innerText = data.fee_demanded ? `⚠️ YES (${data.fee_details})` : 'No upfront fee mentioned';

    // 1. Domain Scrutiny Card
    const domainBody = document.getElementById('res-domain-body');
    const domainData = data.domain_analysis;
    if (domainData && domainData.domain) {
        let domainHtml = `<p style="font-family:'JetBrains Mono'; font-size:0.84rem; margin-bottom:0.4rem;">
            <strong>Domain:</strong> <code>@${domainData.domain}</code>
        </p>`;
        if (domainData.is_free_provider) {
            domainHtml += `<p style="color:var(--danger-red); font-size:0.82rem;">❌ Public Free Webmail Provider. Legitimate enterprise recruiters never hire from Gmail/Yahoo.</p>`;
        } else if (domainData.is_typosquatting) {
            domainHtml += `<p style="color:var(--danger-red); font-size:0.82rem;">❌ Deceptive / Typosquatted Domain spoofing a known corporation.</p>`;
        } else {
            domainHtml += `<p style="color:var(--success-green); font-size:0.82rem;">✔️ Domain matches expected corporate structure.</p>`;
        }
        domainBody.innerHTML = domainHtml;
    } else {
        domainBody.innerHTML = `<p class="form-hint">No sender email address detected in text to scrutinize domain.</p>`;
    }

    // 2. Official Careers Vacancy Check Card
    const careerBody = document.getElementById('res-career-body');
    const careerCheck = data.official_career_check;
    if (careerCheck) {
        if (careerCheck.verified) {
            careerBody.innerHTML = `
                <p style="color:var(--success-green); font-weight:700; font-size:0.84rem;">✔️ Confirmed Active on Official Careers Page</p>
                <p style="font-size:0.78rem; margin:0.3rem 0; color:var(--text-secondary);">${careerCheck.matched_job.title} (${careerCheck.matched_job.job_id})</p>
                <a href="${careerCheck.official_portal}" target="_blank" class="portal-link">View Official Careers Portal &rarr;</a>
            `;
        } else {
            careerBody.innerHTML = `
                <p style="color:var(--danger-red); font-weight:700; font-size:0.84rem;">❌ No Official Vacancy Found</p>
                <p style="font-size:0.78rem; margin:0.3rem 0; color:var(--text-secondary);">${careerCheck.message}</p>
                ${careerCheck.official_portal ? `<a href="${careerCheck.official_portal}" target="_blank" class="portal-link">Check Official Portal &rarr;</a>` : ''}
            `;
        }
    } else {
        careerBody.innerHTML = `<p class="form-hint">Company name not recognized or not checked.</p>`;
    }

    // 3. Database Check Card
    const dbBody = document.getElementById('res-db-body');
    const reportHistory = data.report_history;
    if (reportHistory && reportHistory.reported) {
        dbBody.innerHTML = `
            <p style="color:var(--danger-red); font-weight:700; font-size:0.84rem;">⚠️ Reported ${reportHistory.count} Time(s) by Jobseekers</p>
            <p style="font-size:0.78rem; margin-top:0.3rem; color:var(--text-secondary);">Prior fraud incidents filed for this company/domain in SafeJobs Community DB.</p>
        `;
    } else {
        dbBody.innerHTML = `
            <p style="color:var(--success-green); font-size:0.84rem;">✔️ No Prior Incident Reports on Record</p>
            <p style="font-size:0.78rem; margin-top:0.3rem; color:var(--text-muted);">First time checked in SafeJobs Community DB.</p>
        `;
    }

    // Red Flags
    const redFlagsUl = document.getElementById('res-red-flags');
    redFlagsUl.innerHTML = '';
    (data.red_flags || []).forEach(flag => {
        const li = document.createElement('li');
        li.innerText = flag;
        redFlagsUl.appendChild(li);
    });

    // Forensic Text
    document.getElementById('res-analysis-text').innerText = data.detailed_analysis || 'No detailed forensic text generated.';

    // Safe Steps
    const stepsUl = document.getElementById('res-recommendations');
    stepsUl.innerHTML = '';
    (data.safety_recommendations || []).forEach(step => {
        const li = document.createElement('li');
        li.innerText = step;
        stepsUl.appendChild(li);
    });

    // Scroll smoothly to results
    document.getElementById('scrutinizer-result-card').scrollIntoView({ behavior: 'smooth' });
}

// ================= TAB 2: CAREERS VERIFIER =================
async function handleCareerVerification(e) {
    if (e) e.preventDefault();
    const company = document.getElementById('career-company-input').value.trim();
    const role = document.getElementById('career-role-input').value.trim();

    if (!company) {
        showToast("Please enter a company name.");
        return;
    }

    const btn = document.getElementById('btn-search-career');
    setLoading(btn, true);

    try {
        const res = await fetch(`/api/careers/verify?company=${encodeURIComponent(company)}&role=${encodeURIComponent(role)}`);
        const data = await res.json();
        if (data.success && data.data) {
            renderCareerResult(data.data, role);
        } else {
            showToast(data.error || "Verification failed.", "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error checking official careers portal.", "error");
    } finally {
        setLoading(btn, false);
    }
}

function searchSpecificVacancy(company, role) {
    document.getElementById('career-company-input').value = company;
    document.getElementById('career-role-input').value = role;
    handleCareerVerification();
}

function renderCareerResult(data, searchedRole) {
    const container = document.getElementById('career-result-container');
    container.style.display = 'block';

    const isVerified = data.verified;
    const boxClass = isVerified ? 'verified' : 'unverified';
    const badgeClass = isVerified ? 'badge-success' : 'badge-danger';

    let html = `
        <div class="career-result-box ${boxClass}">
            <div class="career-header-row">
                <div>
                    <span class="career-status-badge ${badgeClass}">${data.badge}</span>
                    <h2 style="margin-top:0.6rem;">${data.company_name}</h2>
                    <p style="color:var(--text-secondary); margin-top:0.25rem;">${data.message}</p>
                </div>
                ${data.official_portal ? `
                    <a href="${data.official_portal}" target="_blank" class="btn btn-primary" style="padding:0.6rem 1.1rem; font-size:0.85rem;">
                        Visit Official Careers Site &rarr;
                    </a>
                ` : ''}
            </div>
    `;

    if (isVerified && data.matched_job) {
        const j = data.matched_job;
        html += `
            <div class="job-spec-grid">
                <div class="spec-item">
                    <div class="spec-title">Official Job ID</div>
                    <div class="spec-value mono-font">${j.job_id}</div>
                </div>
                <div class="spec-item">
                    <div class="spec-title">Confirmed Title</div>
                    <div class="spec-value">${j.title}</div>
                </div>
                <div class="spec-item">
                    <div class="spec-title">Official Location</div>
                    <div class="spec-value">${j.location}</div>
                </div>
                <div class="spec-item">
                    <div class="spec-title">Required Experience</div>
                    <div class="spec-value">${j.experience}</div>
                </div>
            </div>

            <div style="background:var(--bg-subtle); padding:1rem; border-radius:var(--radius-md); border:1px solid var(--border-color); margin-top:1rem;">
                <h4 style="font-size:0.88rem; color:var(--text-muted); margin-bottom:0.4rem;">Official Requirements & Description:</h4>
                <p style="font-size:0.88rem; line-height:1.5; color:var(--text-main);">${j.requirements}</p>
                <div style="margin-top:0.85rem;">
                    <a href="${j.official_url || data.official_portal}" target="_blank" class="portal-link">
                        Direct Official Listing Link on ${data.official_domain} &rarr;
                    </a>
                </div>
            </div>

            <h4 style="margin-top:1.5rem; font-size:0.95rem; color:var(--text-main);">Cross-Platform Reality Check:</h4>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Recruitment Vector</th>
                        <th>External Unverified Post / Message</th>
                        <th>Official ${data.company_name} Policy</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Recruitment Fee</strong></td>
                        <td style="color:var(--danger-red);">Often demands laptop/medical fee</td>
                        <td style="color:var(--success-green);">${data.policy}</td>
                    </tr>
                    <tr>
                        <td><strong>Interview Format</strong></td>
                        <td style="color:var(--danger-red);">Anonymous Telegram/WhatsApp chat</td>
                        <td style="color:var(--success-green);">Formal ATS / Video Conference</td>
                    </tr>
                </tbody>
            </table>
        `;
    } else {
        // Not verified on careers page
        html += `
            <div style="background:var(--danger-bg); border-left:4px solid var(--danger-red); padding:1rem; border-radius:0 var(--radius-sm) var(--radius-sm) 0; margin-top:1rem;">
                <h4 style="color:var(--danger-text); font-size:0.92rem; margin-bottom:0.4rem;">⚠️ Warning: Ghost or Fabricated Job Opening</h4>
                <p style="font-size:0.85rem; color:var(--text-muted); line-height:1.5;">
                    No job vacancy for <strong>"${searchedRole || 'this title'}"</strong> exists on the verified careers portal of ${data.company_name}. Scammers frequently create fake entry-level jobs on Facebook, Telegram, or WhatsApp using real corporate names to defraud jobseekers.
                </p>
            </div>
        `;

        if (data.available_openings && data.available_openings.length > 0) {
            html += `
                <h4 style="margin-top:1.5rem; font-size:0.92rem; color:var(--text-secondary);">Genuine Active Roles Currently Open at ${data.company_name}:</h4>
                <div class="job-spec-grid" style="margin-top:0.75rem;">
            `;
            data.available_openings.forEach(op => {
                html += `
                    <div class="spec-item">
                        <div class="spec-title">${op.department}</div>
                        <div class="spec-value" style="font-size:0.86rem;">${op.title}</div>
                        <div style="font-size:0.74rem; color:var(--text-muted); margin-top:0.3rem;">Location: ${op.location}</div>
                    </div>
                `;
            });
            html += `</div>`;
        }
    }

    html += `</div>`;
    container.innerHTML = html;
    container.scrollIntoView({ behavior: 'smooth' });
}

async function loadVerifiedCompanies() {
    const grid = document.getElementById('companies-directory-grid');
    if (!grid) return;

    try {
        const res = await fetch('/api/careers/companies');
        const data = await res.json();
        if (data.success && data.companies) {
            grid.innerHTML = '';
            data.companies.forEach(c => {
                const card = document.createElement('div');
                card.className = 'comp-card';
                card.innerHTML = `
                    <div>
                        <div class="comp-name">${c.name}</div>
                        <div class="comp-domain">Domain: @${c.official_domain}</div>
                        <div class="comp-policy">${c.verified_policy || 'Strict zero-fee recruitment policy.'}</div>
                    </div>
                    <div>
                        <a href="${c.official_careers_url}" target="_blank" class="portal-link">
                            Official Careers Portal &rarr;
                        </a>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    } catch (err) {
        console.error("Error loading companies:", err);
    }
}

// ================= TAB 3: SCAM DATABASE & HISTORY =================
async function handleHistorySearch(e) {
    if (e) e.preventDefault();
    const query = document.getElementById('history-query-input').value.trim();
    if (!query) {
        showToast("Please enter a company name, email, or domain.");
        return;
    }

    const btn = document.getElementById('btn-search-history');
    setLoading(btn, true);

    try {
        const res = await fetch(`/api/reports/check?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (data.success && data.data) {
            renderHistoryResults(data.data);
        }
    } catch (err) {
        console.error(err);
        showToast("Error searching database.", "error");
    } finally {
        setLoading(btn, false);
    }
}

function renderHistoryResults(data) {
    const container = document.getElementById('history-results-area');
    container.style.display = 'block';

    if (!data.reported) {
        container.innerHTML = `
            <div class="card" style="border-color:var(--success-green); text-align:center; padding:2rem;">
                <h3 style="color:var(--success-green); margin-bottom:0.5rem;">✔️ No Prior Incident Reports Found</h3>
                <p style="color:var(--text-secondary); max-width:500px; margin:0 auto;">
                    No complaints have been lodged against "${data.query}" in the SafeJobs community database yet. Always remain vigilant and cross-reference their official website domain.
                </p>
            </div>
        `;
    } else {
        let html = `
            <div class="card" style="border-color:var(--danger-red);">
                <div class="card-header flex-between">
                    <div>
                        <span class="career-status-badge badge-danger">⚠️ ${data.threat_badge}</span>
                        <h3 style="margin-top:0.6rem;">Found ${data.count} Past Scam Incident(s) Matching "${data.query}"</h3>
                        <p style="color:var(--text-secondary);">Total community reported loss: <strong>$${data.total_reported_loss.toFixed(2)}</strong></p>
                    </div>
                </div>
                <div class="reports-feed" style="margin-top:1.25rem;">
        `;

        data.reports.forEach(r => {
            html += `
                <div class="report-feed-item">
                    <div class="report-item-header">
                        <div class="report-comp-title">${r.company_name} - <span style="color:var(--primary-green); font-size:0.85rem;">${r.job_title || 'General Offer'}</span></div>
                        <div class="report-date">${r.date_reported}</div>
                    </div>
                    <div class="report-details-row">
                        <span><strong>Scam Type:</strong> ${r.scam_type}</span>
                        <span><strong>Sender:</strong> <code>${r.sender_email || r.sender_phone || 'Anonymous'}</code></span>
                        <span><strong>Reported Loss:</strong> $${r.loss_amount || 0}</span>
                        <span><strong>Location:</strong> ${r.city}</span>
                    </div>
                    <div class="report-desc">${r.description}</div>
                </div>
            `;
        });

        html += `</div></div>`;
        container.innerHTML = html;
    }
    container.scrollIntoView({ behavior: 'smooth' });
}

async function loadRecentReports() {
    const container = document.getElementById('recent-reports-container');
    if (!container) return;

    try {
        const res = await fetch('/api/reports/recent?limit=8');
        const data = await res.json();
        if (data.success && data.reports) {
            container.innerHTML = '';
            data.reports.forEach(r => {
                const item = document.createElement('div');
                item.className = 'report-feed-item';
                item.innerHTML = `
                    <div class="report-item-header">
                        <div class="report-comp-title">${r.company_name} &bull; <span style="color:var(--primary-green); font-size:0.85rem;">${r.job_title}</span></div>
                        <div class="report-date">${r.date_reported}</div>
                    </div>
                    <div class="report-details-row">
                        <span><strong>Tactic:</strong> ${r.scam_type}</span>
                        <span><strong>Sender:</strong> <code>${r.sender_email || r.sender_phone || 'Unlisted'}</code></span>
                        <span><strong>Reported Loss:</strong> $${r.loss_amount || 0}</span>
                        <span><strong>Reporter:</strong> ${r.reported_by} (${r.city})</span>
                    </div>
                    <div class="report-desc">${r.description}</div>
                `;
                container.appendChild(item);
            });
        }
    } catch (err) {
        console.error("Error loading recent reports:", err);
    }
}

// ================= TAB 4: REPORT A SCAM =================
async function handleReportSubmission(e) {
    e.preventDefault();
    const btn = document.getElementById('btn-submit-report');
    setLoading(btn, true);

    const formData = new FormData();
    formData.append('company_name', document.getElementById('rep-company').value.trim());
    formData.append('scam_type', document.getElementById('rep-scam-type').value);
    formData.append('sender_email', document.getElementById('rep-email').value.trim());
    formData.append('sender_phone', document.getElementById('rep-phone').value.trim());
    formData.append('sender_domain', document.getElementById('rep-domain').value.trim());
    formData.append('job_title', document.getElementById('rep-job-title').value.trim());
    formData.append('loss_amount', document.getElementById('rep-loss').value || 0);
    formData.append('description', document.getElementById('rep-description').value.trim());
    formData.append('reported_by', document.getElementById('rep-name').value.trim());

    const evidenceInput = document.getElementById('rep-evidence');
    if (evidenceInput.files.length > 0) {
        formData.append('evidence_file', evidenceInput.files[0]);
    }

    try {
        const res = await fetch('/api/reports/submit', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            showToast("Report submitted successfully! Thank you for protecting jobseekers.");
            document.getElementById('form-submit-scam').reset();
            loadRecentReports();
            switchTab('tab-database');
        } else {
            showToast(data.error || "Submission failed.", "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error submitting scam report.", "error");
    } finally {
        setLoading(btn, false);
    }
}

// ================= GEMINI API KEY CONFIG =================
async function initGeminiKey() {
    const localKey = localStorage.getItem('safejobs_gemini_key');
    const dot = document.getElementById('gemini-status-dot');
    const txt = document.getElementById('gemini-status-text');

    if (localKey && localKey.length > 10) {
        dot.classList.add('connected');
        txt.innerText = 'Gemini AI Ready';
        return;
    }

    // Check if backend has .env key
    try {
        const res = await fetch('/api/gemini/status');
        const data = await res.json();
        if (data.has_key) {
            dot.classList.add('connected');
            txt.innerText = `${data.model || 'Gemini'} Ready (.env)`;
        } else {
            dot.classList.remove('connected');
            txt.innerText = 'Gemini AI Key';
        }
    } catch (e) {
        dot.classList.remove('connected');
        txt.innerText = 'Gemini AI Key';
    }
}

function getSavedGeminiKey() {
    return localStorage.getItem('safejobs_gemini_key') || '';
}

async function openKeyModal() {
    const modal = document.getElementById('key-modal');
    const input = document.getElementById('gemini-key-input');
    const localKey = getSavedGeminiKey();
    input.value = localKey;
    
    const fb = document.getElementById('key-test-feedback');
    fb.style.display = 'none';

    // If localKey is empty, check if .env has one
    if (!localKey) {
        try {
            const res = await fetch('/api/gemini/status');
            const data = await res.json();
            if (data.has_key) {
                fb.style.display = 'block';
                fb.innerHTML = `<span style="color:var(--success-green); font-size:0.85rem;">✔️ A Gemini API Key is loaded from <code>.env</code> file (Model: <strong>${data.model}</strong>). You can leave this input blank or override it below.</span>`;
            }
        } catch (e) {}
    }

    modal.classList.add('active');
}

function closeKeyModal(e) {
    if (e && e.target !== e.currentTarget && !e.target.classList.contains('modal-close')) return;
    document.getElementById('key-modal').classList.remove('active');
}

function saveGeminiKey() {
    const input = document.getElementById('gemini-key-input');
    const val = input.value.trim();
    if (val) {
        localStorage.setItem('safejobs_gemini_key', val);
        showToast("Gemini API Key saved locally.");
    } else {
        localStorage.removeItem('safejobs_gemini_key');
        showToast("Using server .env Gemini key or local heuristics.");
    }
    initGeminiKey();
    closeKeyModal();
}

async function testGeminiKey() {
    const key = document.getElementById('gemini-key-input').value.trim();
    const fb = document.getElementById('key-test-feedback');
    fb.style.display = 'block';
    fb.innerHTML = '<span class="spinner"></span> Testing connection to Google Gemini API...';

    try {
        const res = await fetch('/api/gemini/test-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: key })
        });
        const data = await res.json();
        if (data.valid) {
            fb.innerHTML = `<span style="color:var(--success-green); font-weight:700;">✔️ Success: ${data.message}</span>`;
            initGeminiKey();
        } else {
            fb.innerHTML = `<span style="color:var(--danger-red);">❌ Error: ${data.message}</span>`;
        }
    } catch (err) {
        fb.innerHTML = `<span style="color:var(--danger-red);">❌ Request failed: ${err.message}</span>`;
    }
}

// ================= UTILITIES =================
function resetForm(formId) {
    document.getElementById(formId).reset();
}

function setLoading(button, isLoading) {
    if (!button) return;
    const btnText = button.querySelector('.btn-text');
    const spinner = button.querySelector('.spinner');

    if (isLoading) {
        button.disabled = true;
        if (btnText) btnText.style.display = 'none';
        if (spinner) spinner.style.display = 'inline-block';
    } else {
        button.disabled = false;
        if (btnText) btnText.style.display = 'inline-flex';
        if (spinner) spinner.style.display = 'none';
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.innerText = message;
    if (type === 'error') {
        toast.style.borderColor = 'var(--danger-red)';
    } else {
        toast.style.borderColor = 'var(--primary-green)';
    }
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}
