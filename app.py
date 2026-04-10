"""
🔥 GLM PainForge - Transform Pain into Production MVPs
Powered by GLM-5.1 on GMI Cloud | GMIxGLM Hackathon 2026
"""

import streamlit as st
import requests
import json
import re
import os
from datetime import datetime
import time

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="GLM PainForge",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONFIGURATION
# ============================================
GMI_BASE_URL = "https://api.gmi-serving.com/v1"
GMI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjBkMWMzYTJiLWZiMmEtNDNhOS04MGVlLWEzNWNlZTRlYjIyNiIsInNjb2BlIjoiaWVfbW9kZWwiLCJjbGllbnRJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCJ9.EEEh20kvdGvMExxJ9cV9-DShA-1rRPTIULLEyUAhORw"
MODEL_NAME = "zai-org/GLM-5.1-FP8"

# ============================================
# SYSTEM PROMPT
# ============================================
MVP_BUILDER_PROMPT = """You are an elite startup CTO and full-stack developer with 15+ years of experience. 
Transform ANY pain point into a complete, deployable MVP in seconds.

CORE PRINCIPLES:
1. Speed: Ship in minutes, not months
2. Practicality: Real code that works, not pseudo-code
3. Indian Market Focus: UPI payments, WhatsApp integration, regional language support
4. Startup-Ready: Includes auth, database, API endpoints, deployment instructions

OUTPUT FORMAT (Strict JSON):
{
    "problem_summary": "Clear 2-sentence description",
    "target_users": ["User persona 1", "User persona 2"],
    "core_features": ["Feature 1", "Feature 2", "Feature 3"],
    "tech_stack": {"frontend": "...", "backend": "...", "database": "...", "deployment": "..."},
    "mvp_code": {"filename1": "full code content...", "filename2": "full code content..."},
    "setup_instructions": ["Step 1...", "Step 2..."],
    "deployment_guide": "How to deploy on GMI Cloud",
    "estimated_cost": "₹X/month",
    "time_to_market": "X days"
}

CRITICAL INSTRUCTIONS:
- Output valid JSON only, no markdown code blocks
- Include COMPLETE, RUNNABLE code for all files
- Use popular frameworks: React/Next.js, Node.js/Python FastAPI, PostgreSQL/Supabase
- Include error handling, loading states, API routes
- Add comments explaining complex logic
- Make it visually impressive for demos

Generate the complete MVP blueprint now."""

# ============================================
# CUSTOM CSS - Premium SaaS Design
# ============================================
st.markdown("""
<style>
    /* ===== FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* ===== BASE ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #030014 0%, #0a0a1f 50%, #1a0a2e 100%);
        color: #ffffff;
        min-height: 100vh;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0a1f; }
    ::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 4px; }
    
    /* ===== HERO SECTION ===== */
    .hero {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, 
            rgba(99, 102, 241, 0.15) 0%, 
            rgba(139, 92, 246, 0.1) 50%,
            rgba(168, 85, 247, 0.05) 100%);
        border-radius: 32px;
        margin-bottom: 3rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 50%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        padding: 0.5rem 1.5rem;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #a5b4fc 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: #94a3b8;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
    }
    
    .hero-tech {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .tech-tag {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #94a3b8;
    }
    
    .tech-tag strong {
        color: #6366f1;
    }
    
    /* ===== CARDS ===== */
    .card {
        background: linear-gradient(145deg, 
            rgba(30, 30, 50, 0.8) 0%, 
            rgba(20, 20, 40, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 24px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #fff;
    }
    
    .card-subtitle {
        font-size: 0.85rem;
        color: #64748b;
    }
    
    /* ===== SIDEBAR ===== */
    .sidebar .stButton > button {
        width: 100%;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .sidebar .stButton > button:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: #6366f1;
        color: #fff;
    }
    
    /* ===== INPUTS ===== */
    .stTextArea > div > div > textarea {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 2px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 16px !important;
        color: #fff !important;
        font-size: 1.1rem !important;
        padding: 1.5rem !important;
        min-height: 180px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1), 0 0 30px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* ===== PRIMARY BUTTON ===== */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        color: white;
        border: none;
        padding: 1.25rem 3rem;
        font-size: 1.2rem;
        font-weight: 700;
        border-radius: 16px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button[kind="primary"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button[kind="primary"]:hover::before {
        left: 100%;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.4);
    }
    
    /* ===== STATS ===== */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, 
            rgba(99, 102, 241, 0.15) 0%, 
            rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .stat-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    /* ===== FEATURE TAGS ===== */
    .feature-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, 
            rgba(99, 102, 241, 0.2) 0%, 
            rgba(139, 92, 246, 0.15) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.6rem 1.2rem;
        border-radius: 100px;
        margin: 0.3rem;
        font-size: 0.9rem;
        color: #a5b4fc;
        transition: all 0.3s ease;
    }
    
    .feature-tag:hover {
        background: linear-gradient(135deg, 
            rgba(99, 102, 241, 0.3) 0%, 
            rgba(139, 92, 246, 0.25) 100%);
        border-color: #6366f1;
        transform: scale(1.05);
    }
    
    /* ===== CODE BLOCK ===== */
    .code-block {
        background: #0d1117;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .code-header {
        background: rgba(99, 102, 241, 0.1);
        padding: 1rem 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .code-filename {
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.9rem;
        color: #a5b4fc;
    }
    
    .code-lang {
        background: rgba(99, 102, 241, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        color: #6366f1;
        font-weight: 600;
    }
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(30, 30, 50, 0.5);
        padding: 0.5rem;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }
    
    /* ===== PROGRESS ===== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7);
        border-radius: 10px;
    }
    
    /* ===== SUCCESS ===== */
    .success-banner {
        background: linear-gradient(135deg, 
            rgba(34, 197, 94, 0.2) 0%, 
            rgba(16, 185, 129, 0.1) 100%);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        color: #4ade80;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .download-btn {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        margin: 3rem 0;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .footer a {
        color: #6366f1;
        text-decoration: none;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================
def call_glm_api(prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {GMI_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": MVP_BUILDER_PROMPT},
        {"role": "user", "content": prompt}
    ]
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 8192,
        "thinking": {"type": "adaptive"}
    }
    try:
        response = requests.post(f"{GMI_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return {"success": True, "content": result["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def parse_mvp_json(content: str) -> dict:
    try:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None

def get_lang(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', 
            '.jsx': 'jsx', '.tsx': 'tsx', '.html': 'html', '.css': 'css', 
            '.json': 'json', '.sql': 'sql', '.sh': 'bash'}.get(ext, 'text')

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🔥 PainForge</h2>
        <p style="color: #64748b; font-size: 0.85rem;">GLM-5.1 MVP Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Examples")
    st.markdown("*Click to load instantly*")
    
    examples = [
        ("💼", "Freelancers chasing UPI payments"),
        ("📊", "Indian startups GST compliance"),
        ("🎯", "Founders writing pitch decks"),
        ("📋", "Remote teams tracking tasks"),
        ("🏪", "Kirana store inventory"),
        ("🏥", "Clinic appointment booking"),
        ("📚", "Coding bootcamp platform"),
        ("🚗", "Local delivery tracking"),
    ]
    
    selected_example = None
    for emoji, text in examples:
        if st.button(f"{emoji} {text}", key=f"ex_{text}"):
            selected_example = f"I am a {text.lower()} in India. I need a simple tool that..." if "in India" not in text.lower() else text
            st.session_state['pain_input'] = selected_example
    
    st.markdown("---")
    st.markdown("### 🛠️ Tech Stack")
    st.markdown("""
    - **Frontend:** React/Next.js
    - **Backend:** Python FastAPI
    - **Database:** PostgreSQL/Supabase
    - **Deploy:** GMI Cloud GPU
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Powered By")
    st.markdown("""
    <div style="display: flex; gap: 1rem; justify-content: center;">
        <span class="tech-tag"><strong>GMI</strong> Cloud</span>
        <span class="tech-tag"><strong>Z.ai</strong> GLM-5.1</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN CONTENT
# ============================================

# Hero Section
st.markdown("""
<div class="hero">
    <div class="hero-badge">🏆 GMIxGLM Hackathon Singapore 2026</div>
    <h1 class="hero-title">🔥 GLM PainForge</h1>
    <p class="hero-subtitle">
        Pain → Production MVP in seconds<br>
        Powered by GLM-5.1 on GMI Cloud GPU
    </p>
    <div class="hero-tech">
        <span class="tech-tag"><strong>GLM-5.1</strong> AI Model</span>
        <span class="tech-tag"><strong>GMI</strong> Cloud GPU</span>
        <span class="tech-tag"><strong>Z.ai</strong> Technology</span>
        <span class="tech-tag"><strong>OpenCode</strong> Powered</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Input Area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <div class="card-icon">💭</div>
            <div>
                <div class="card-title">Describe Your Pain Point</div>
                <div class="card-subtitle">Be specific about the problem you want to solve</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    default_text = st.session_state.get('pain_input', "")
    pain_point = st.text_area(
        "",
        value=default_text,
        placeholder="Example: Indian freelancers struggle with tracking client payments. They send invoices manually via WhatsApp, chase payments, and have no centralized system. Build a simple tool with UPI QR codes, payment tracking, and automated reminders...",
        label_visibility="collapsed",
        height=180
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card" style="height: 100%;">
        <div class="card-header">
            <div class="card-icon">⚡</div>
            <div>
                <div class="card-title">How It Works</div>
            </div>
        </div>
        <ol style="color: #94a3b8; line-height: 2;">
            <li>Describe your pain point</li>
            <li>Click <strong style="color: #6366f1;">🚀 Forge MVP</strong></li>
            <li>GLM-5.1 analyzes & builds</li>
            <li>Download & deploy!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Forge Button
col_btn = st.columns([1])
with col_btn[0]:
    forge_clicked = st.button("🚀 Forge the MVP", type="primary", use_container_width=True)

# ============================================
# GENERATION PROCESS
# ============================================
if forge_clicked and pain_point:
    # Progress phase
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    phases = [
        ("🔍 Analyzing your pain point...", 15),
        ("🧠 GLM-5.1 is thinking deeply...", 40),
        ("⚙️ Building MVP architecture...", 65),
        ("💻 Generating production code...", 85),
        ("✨ Finalizing your MVP...", 95),
    ]
    
    for phase_text, progress in phases:
        status_text.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #fff; font-size: 1.5rem;">{phase_text}</h2>
            <p style="color: #64748b;">Powered by GLM-5.1 on GMI Cloud</p>
        </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(progress)
        time.sleep(0.5)
    
    # Call API
    result = call_glm_api(pain_point)
    
    if result["success"]:
        progress_bar.progress(100)
        mvp_data = parse_mvp_json(result["content"])
        
        if mvp_data:
            st.session_state['mvp_data'] = mvp_data
            st.markdown('<div class="success-banner">🎉 MVP Forged Successfully with GLM-5.1!</div>', unsafe_allow_html=True)
        else:
            st.error("Could not parse response. Please try again.")
    else:
        st.error(f"API Error: {result.get('error', 'Unknown error')}")

# ============================================
# RESULTS DISPLAY
# ============================================
if 'mvp_data' in st.session_state and st.session_state['mvp_data']:
    mvp = st.session_state['mvp_data']
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("## 🎯 Your MVP Blueprint")
    
    # Stats Row
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">⏱️</div>
            <div class="stat-value">{mvp.get('time_to_market', '3-5 days')}</div>
            <div class="stat-label">Time to Market</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-value">{mvp.get('estimated_cost', '₹2,000/mo')}</div>
            <div class="stat-label">Est. Monthly Cost</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-value">{len(mvp.get('core_features', []))}</div>
            <div class="stat-label">Core Features</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🔥</div>
            <div class="stat-value">GLM-5.1</div>
            <div class="stat-label">AI Powered</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Details in Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📌 Problem & Users", "⚡ Features & Stack", "💻 Generated Code", "🚀 Deploy"])
    
    with tab1:
        col_prob, col_users = st.columns(2)
        
        with col_prob:
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📌</div>
                    <div>
                        <div class="card-title">Problem Summary</div>
                    </div>
                </div>
                <p style="color: #cbd5e1; line-height: 1.8;">{mvp.get('problem_summary', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_users:
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">👥</div>
                    <div>
                        <div class="card-title">Target Users</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            users = mvp.get('target_users', [])
            for user in users:
                st.markdown(f"- **{user}**")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        # Features
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">⚡</div>
                <div>
                    <div class="card-title">Core Features</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        features = mvp.get('core_features', [])
        for f in features:
            st.markdown(f'<span class="feature-tag">✨ {f}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tech Stack
        stack = mvp.get('tech_stack', {})
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🎨</div>
                <div class="stat-value" style="font-size: 1rem;">{stack.get('frontend', 'React')}</div>
                <div class="stat-label">Frontend</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⚙️</div>
                <div class="stat-value" style="font-size: 1rem;">{stack.get('backend', 'Node.js')}</div>
                <div class="stat-label">Backend</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🗄️</div>
                <div class="stat-value" style="font-size: 1rem;">{stack.get('database', 'PostgreSQL')}</div>
                <div class="stat-label">Database</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">☁️</div>
                <div class="stat-value" style="font-size: 1rem;">{stack.get('deployment', 'GMI Cloud')}</div>
                <div class="stat-label">Deploy</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        mvp_code = mvp.get('mvp_code', {})
        if mvp_code:
            filenames = list(mvp_code.keys())
            tabs_code = st.tabs(filenames)
            
            for i, (filename, code) in enumerate(mvp_code.items()):
                with tabs_code[i]:
                    st.markdown(f"""
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-filename">📄 {filename}</span>
                            <span class="code-lang">{get_lang(filename).upper()}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(code, language=get_lang(filename), line_numbers=True)
                    col_dl = st.columns([1, 3, 1])
                    with col_dl[1]:
                        st.download_button(
                            f"📥 Download {filename}",
                            code,
                            filename,
                            mime="text/plain",
                            use_container_width=True
                        )
        else:
            st.info("No code generated in this response.")
    
    with tab4:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">☁️</div>
                <div>
                    <div class="card-title">Deploy to GMI Cloud</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<p style='color: #cbd5e1; line-height: 1.8;'>{mvp.get('deployment_guide', 'Follow setup instructions below.')}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">🚀</div>
                <div>
                    <div class="card-title">Setup Instructions</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        instructions = mvp.get('setup_instructions', [])
        for i, step in enumerate(instructions, 1):
            st.markdown(f"**{i}.** {step}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Download all
        if mvp_code:
            st.markdown("<br>", unsafe_allow_html=True)
            all_code = json.dumps(mvp_code, indent=2)
            st.download_button(
                "📦 Download All Code",
                all_code,
                f"mvp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                type="primary",
                use_container_width=True
            )

# ============================================
# FOOTER
# ============================================
st.markdown("""
<hr>
<div class="footer">
    <p>🔥 Built with <strong>GLM-5.1</strong> on <strong>GMI Cloud GPU</strong></p>
    <p>🏆 GMIxGLM Hackathon Singapore 2026 | Powered by Z.ai | Built with OpenCode</p>
</div>
""", unsafe_allow_html=True)
