import streamlit as st
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

from core.ingest import parse_jd, parse_resume
from core.scoring import extract_jd_requirements, score_candidate, WEIGHTS
from core.reporting import generate_html_report_str

load_dotenv()

st.set_page_config(page_title="AI HR Agent", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (PREMIUM OVERHAUL) ---
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">

<style>
    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #f8fafc;
    }
    
    h1, h2, h3, .main-banner h1 {
        font-family: 'Outfit', sans-serif;
    }

    /* Animated Background */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at 20% 30%, #1e1b4b 0%, transparent 40%),
                    radial-gradient(circle at 80% 70%, #4c1d95 0%, transparent 40%);
        opacity: 0.4;
        z-index: -1;
        animation: drift 20s infinite alternate ease-in-out;
    }
    @keyframes drift {
        from { transform: scale(1) translate(0, 0); }
        to { transform: scale(1.1) translate(2%, 2%); }
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 15, 0.8);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.5);
        border-color: rgba(139, 92, 246, 0.3);
    }

    /* Main Banner */
    .main-banner {
        background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%);
        padding: 40px;
        border-radius: 24px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px -12px rgba(124, 58, 237, 0.3);
        text-align: center;
    }
    .main-banner h1 {
        margin: 0;
        font-size: 2.8rem;
        letter-spacing: -1px;
    }
    .main-banner p {
        margin: 10px 0 0 0;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1rem;
    }

    /* Custom Metrics */
    .metric-card {
        text-align: center;
        padding: 20px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #a78bfa;
        font-family: 'Outfit', sans-serif;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    /* Badges */
    .badge {
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
    }
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-purple { background: rgba(139, 92, 246, 0.15); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }

    /* Console Box */
    .console-box {
        background: #000000;
        color: #34d399;
        font-family: 'Courier New', monospace;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        font-size: 0.9rem;
        line-height: 1.5;
        height: 300px;
        overflow-y: auto;
    }

    /* Tabs Override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        color: #94a3b8;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(139, 92, 246, 0.15) !important;
        color: #a78bfa !important;
        border-bottom: 2px solid #a78bfa !important;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "results" not in st.session_state:
    st.session_state.results = None
if "jd_reqs" not in st.session_state:
    st.session_state.jd_reqs = None
if "console_logs" not in st.session_state:
    st.session_state.console_logs = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

def log_to_console(msg):
    st.session_state.console_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    if os.getenv("GROQ_API_KEY"):
        st.markdown('<div class="badge badge-green">✅ Groq API Key Configured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge badge-red">❌ Missing API Key</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    jd_file = st.file_uploader("📂 Job Description (TXT/PDF)", type=["txt", "pdf"])
    resume_files = st.file_uploader("📄 Candidates (TXT/PDF)", type=["txt", "pdf"], accept_multiple_files=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Scoring Rubric")
    rubric = [
        ("Skills Match", "30%", "badge-green"),
        ("Experience", "25%", "badge-purple"),
        ("Projects", "20%", "badge-purple"),
        ("Education", "15%", "badge-purple"),
        ("Comm.", "10%", "badge-purple")
    ]
    for label, weight, cls in rubric:
        st.markdown(f'<div class="badge {cls}" style="display:block; margin-bottom:5px;">{label}: {weight}</div>', unsafe_allow_html=True)

# --- MAIN BANNER ---
st.markdown("""
<div class="main-banner">
    <h1>💼 AI HR Shortlisting Agent</h1>
    <p>Acme Corp Enterprise • Intelligent Candidate Evaluation • Human-in-the-Loop</p>
</div>
""", unsafe_allow_html=True)

# --- TABS ---
tab_dashboard, tab_candidates, tab_run, tab_audit, tab_reports = st.tabs([
    "📊 Dashboard", "📄 Candidates", "🚀 Run Agent", "📝 Audit Log", "📥 Reports"
])

# --- TAB: RUN AGENT ---
with tab_run:
    st.markdown("""
    <div class="glass-card">
        <h3 style='margin-top:0;'>🚀 Evaluation Engine</h3>
        <p style='color:#94a3b8;'>Upload JD and Resumes in the sidebar to begin processing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Start AI Evaluation", type="primary", use_container_width=True):
        if not jd_file or not resume_files:
            st.error("Please upload a Job Description and at least one Resume.")
        else:
            st.session_state.is_running = True
            st.session_state.console_logs = []
            log_to_console("Initializing Engine...")
            
            os.makedirs("temp_files", exist_ok=True)
            jd_path = os.path.join("temp_files", jd_file.name)
            with open(jd_path, "wb") as f: f.write(jd_file.getbuffer())
            
            jd_text = parse_jd(jd_path) if jd_path.endswith(".txt") else parse_resume(jd_path)["text"]
            st.session_state.jd_reqs = extract_jd_requirements(jd_text)
            log_to_console("Job requirements extracted.")
            
            results = []
            for idx, r_file in enumerate(resume_files):
                log_to_console(f"Evaluating: {r_file.name}")
                r_path = os.path.join("temp_files", r_file.name)
                with open(r_path, "wb") as f: f.write(r_file.getbuffer())
                
                resume_data = parse_resume(r_path)
                scores = score_candidate(resume_data["text"], st.session_state.jd_reqs)
                scores["name"] = resume_data["name"]
                scores["recommendation"] = "Hire" if scores["total_score"] >= 7 else "No Hire"
                results.append(scores)
                
            results.sort(key=lambda x: x["total_score"], reverse=True)
            st.session_state.results = results
            st.session_state.is_running = False
            log_to_console("Evaluation complete!")
            st.rerun()

    st.markdown("### 🖥️ Engine Output")
    console_text = "\n".join(st.session_state.console_logs) if st.session_state.console_logs else "Waiting for trigger..."
    st.markdown(f'<div class="console-box">{console_text}</div>', unsafe_allow_html=True)

# --- TAB: DASHBOARD ---
with tab_dashboard:
    if not st.session_state.results:
        st.info("No data processed yet.")
    else:
        st.markdown("### 📊 Workforce Insights")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1: st.markdown(f'<div class="glass-card metric-card"><div class="metric-value">{len(st.session_state.results)}</div><div class="metric-label">Processed</div></div>', unsafe_allow_html=True)
        hires = sum(1 for r in st.session_state.results if r["recommendation"] == "Hire")
        with c2: st.markdown(f'<div class="glass-card metric-card"><div class="metric-value">{hires}</div><div class="metric-label">Hires</div></div>', unsafe_allow_html=True)
        avg = round(sum(r["total_score"] for r in st.session_state.results) / len(st.session_state.results), 1)
        with c3: st.markdown(f'<div class="glass-card metric-card"><div class="metric-value">{avg}</div><div class="metric-label">Avg Score</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="glass-card metric-card"><div class="metric-value">100%</div><div class="metric-label">Reliability</div></div>', unsafe_allow_html=True)
        
        st.markdown("### 🏆 Leaderboard")
        for i, c in enumerate(st.session_state.results[:5]):
            st.markdown(f"""
            <div class="glass-card" style="padding:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:20px;">
                    <span style="font-size:1.5rem; font-weight:800; color:#4c1d95;">#{i+1}</span>
                    <span style="font-weight:600; font-size:1.1rem;">{c['name']}</span>
                </div>
                <div style="display:flex; align-items:center; gap:15px;">
                    <span class="badge {'badge-green' if c['recommendation'] == 'Hire' else 'badge-red'}">{c['recommendation']}</span>
                    <span style="font-family:'Outfit'; font-weight:800; font-size:1.4rem; color:#a78bfa;">{c['total_score']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- TAB: CANDIDATES ---
with tab_candidates:
    if not st.session_state.results:
        st.info("No data processed yet.")
    else:
        for idx, c in enumerate(st.session_state.results):
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <h2 style="margin:0;">{idx+1}. {c['name']}</h2>
                        <div style="text-align:right;">
                            <div style="font-size:2rem; font-family:'Outfit'; font-weight:800; color:#a78bfa;">{c['total_score']} / 10</div>
                            <span class="badge {'badge-green' if c['recommendation'] == 'Hire' else 'badge-red'}">{c['recommendation']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(5)
                dims = [
                    ("Skills", "skills_match"), ("Experience", "experience_relevance"),
                    ("Education", "education_certs"), ("Projects", "project_portfolio"), ("Comm.", "communication_quality")
                ]
                for i, (label, key) in enumerate(dims):
                    cols[i].markdown(f"**{label}**")
                    cols[i].markdown(f"### {c[key]['score']}")
                    cols[i].caption(c[key]['justification'])
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                with st.expander("🛠️ Human-in-the-Loop Override"):
                    with st.form(key=f"override_{idx}"):
                        dim = st.selectbox("Dimension", [d[1] for d in dims])
                        new_score = st.number_input("New Score (0-10)", 0, 10, int(c[dim]["score"]))
                        reason = st.text_input("Reason")
                        if st.form_submit_button("Apply Correction"):
                            if reason:
                                os.makedirs("audit", exist_ok=True)
                                with open("audit/overrides.jsonl", "a") as f:
                                    f.write(json.dumps({"candidate": c["name"], "dimension": dim, "old": c[dim]["score"], "new": new_score, "reason": reason, "time": str(datetime.now())}) + "\n")
                                c[dim]["score"] = new_score
                                c[dim]["justification"] = f"HUMAN OVERRIDE: {reason}"
                                c["total_score"] = round(sum(c[k]["score"] * w for k, w in WEIGHTS.items()), 2)
                                c["recommendation"] = "Hire" if c["total_score"] >= 7 else "No Hire"
                                st.session_state.results.sort(key=lambda x: x["total_score"], reverse=True)
                                st.rerun()

# --- TAB: AUDIT LOG ---
with tab_audit:
    st.markdown("### 📋 System Audit Trail")
    if os.path.exists("audit/overrides.jsonl"):
        with open("audit/overrides.jsonl", "r") as f: logs = f.readlines()
        if logs:
            audit_text = ""
            for log in reversed(logs):
                l = json.loads(log)
                audit_text += f"[{l['time']}] OVERRIDE: {l['candidate']} | {l['dimension']} | {l['old']}->{l['new']}\nReason: {l['reason']}\n{'-'*60}\n"
            st.markdown(f'<div class="console-box">{audit_text}</div>', unsafe_allow_html=True)
        else: st.info("No overrides yet.")
    else: st.info("No overrides yet.")

# --- TAB: REPORTS ---
with tab_reports:
    if not st.session_state.results: st.info("No data processed yet.")
    else:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📤 Export Artifacts")
        st.download_button("📥 Download JSON Full Data", json.dumps(st.session_state.results, indent=2), "results.json", "application/json", use_container_width=True)
        st.download_button("📥 Download Executive HTML Report", generate_html_report_str(st.session_state.results), "report.html", "text/html", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
