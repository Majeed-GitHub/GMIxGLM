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

CRITICAL: Use chain-of-thought reasoning to break down the problem step by step.
Think through: 1) Who has this problem, 2) What exactly do they need, 3) What's the simplest solution, 4) What tech stack, 5) Generate working code.

OUTPUT FORMAT (Strict JSON):
{
    "problem_summary": "Clear 2-sentence description",
    "target_users": ["User persona 1", "User persona 2"],
    "core_features": ["Feature 1", "Feature 2", "Feature 3"],
    "tech_stack": {"frontend": "...", "backend": "...", "database": "...", "deployment": "..."},
    "mvp_code": {"app.py": "full python code...", "requirements.txt": "dependencies..."},
    "setup_instructions": ["Step 1...", "Step 2..."],
    "deployment_guide": "How to deploy on GMI Cloud",
    "estimated_cost": "₹X/month",
    "time_to_market": "X days"
}

CRITICAL INSTRUCTIONS:
- Output valid JSON only, no markdown code blocks
- Include COMPLETE, RUNNABLE code for all files
- Use Python Streamlit or React/Next.js for fast prototyping
- Include error handling, loading states, API routes
- Make it visually impressive for demos

Generate the complete MVP blueprint now."""

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #030014 0%, #0a0a1f 50%, #1a0a2e 100%);
        color: #ffffff;
        min-height: 100vh;
    }
    
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0a1f; }
    ::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 4px; }
    
    .hero {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 32px;
        margin-bottom: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        padding: 0.5rem 1.5rem;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #a5b4fc 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #94a3b8;
        font-weight: 300;
    }
    
    .card {
        background: linear-gradient(145deg, rgba(30, 30, 50, 0.8) 0%, rgba(20, 20, 40, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(20px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 2px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 16px !important;
        color: #fff !important;
        font-size: 1rem !important;
        padding: 1.25rem !important;
        min-height: 160px !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 1.1rem 3rem;
        font-size: 1.1rem;
        font-weight: 700;
        border-radius: 14px;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.4);
    }
    
    .thinking-step {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
        border-left: 4px solid #6366f1;
        padding: 1rem 1.5rem;
        margin: 0.75rem 0;
        border-radius: 0 12px 12px 0;
        color: #cbd5e1;
    }
    
    .thinking-step-number {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.75rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .feature-tag {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 100px;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    
    .code-block {
        background: #0d1117;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .code-header {
        background: rgba(99, 102, 241, 0.1);
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-family: monospace;
        font-size: 0.85rem;
        color: #a5b4fc;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(30, 30, 50, 0.5);
        padding: 0.5rem;
        border-radius: 14px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 0.6rem 1.25rem;
        font-weight: 600;
        color: #64748b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }
    
    hr { border: none; height: 1px; background: rgba(99, 102, 241, 0.2); margin: 2rem 0; }
    
    .footer { text-align: center; padding: 2rem; color: #64748b; }
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

def extract_thinking_steps(content: str) -> list:
    """Extract reasoning steps from GLM response"""
    steps = []
    lines = content.split('\n')
    for line in lines[:30]:
        line = line.strip()
        if line and len(line) > 30:
            steps.append(line[:150])
    if not steps:
        steps = ["Analyzing problem context...", "Identifying core requirements...", "Designing MVP architecture...", "Generating production code..."]
    return steps[:6]

def get_lang(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', 
            '.jsx': 'jsx', '.html': 'html', '.css': 'css', 
            '.json': 'json', '.sql': 'sql', '.sh': 'bash', '.md': 'markdown'}.get(ext, 'text')

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem;">
        <h2 style="font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🔥 GLM PainForge
        </h2>
        <p style="color: #64748b; font-size: 0.8rem;">GLM-5.1 MVP Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Examples")
    
    examples = [
        ("💼", "Freelancer invoice + UPI tracking"),
        ("📊", "GST compliance tool"),
        ("🎯", "Multi-language pitch deck generator"),
        ("📋", "Task management for remote teams"),
        ("🏪", "Kirana inventory + WhatsApp orders"),
        ("🏥", "Clinic appointment booking"),
    ]
    
    for emoji, text in examples:
        if st.button(f"{emoji} {text}", key=f"ex_{text}", use_container_width=True):
            st.session_state['pain_input'] = f"I am a {text.lower()}. I need a simple tool that helps me..."

# ============================================
# MAIN CONTENT
# ============================================

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-badge">🏆 GMIxGLM Hackathon Singapore 2026</div>
    <h1 class="hero-title">🔥 GLM PainForge</h1>
    <p class="hero-subtitle">
        Pain → Production MVP in seconds • Powered by GLM-5.1 on GMI Cloud
    </p>
</div>
""", unsafe_allow_html=True)

# Input Section
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <div class="card-icon">💭</div>
            <div>
                <div style="font-weight: 700; font-size: 1.1rem;">Describe Your Pain Point</div>
                <div style="color: #64748b; font-size: 0.85rem;">Be specific about the problem you want to solve</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    default_text = st.session_state.get('pain_input', "")
    pain_point = st.text_area(
        "",
        value=default_text,
        placeholder="Example: Indian freelancers struggle with tracking client payments. They send invoices manually via WhatsApp, chase payments, and have no centralized system. Build a simple tool with UPI QR codes, payment tracking, and automated reminders...",
        label_visibility="collapsed",
        height=160
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card" style="height: 100%;">
        <div class="card-header">
            <div class="card-icon">⚡</div>
            <div style="font-weight: 700;">How It Works</div>
        </div>
        <ol style="color: #94a3b8; line-height: 2; font-size: 0.9rem; padding-left: 1.2rem;">
            <li>Describe your pain</li>
            <li>Click <strong style="color: #6366f1;">🚀 Forge MVP</strong></li>
            <li>GLM-5.1 thinks & builds</li>
            <li>Download & deploy!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Forge Button
forge_clicked = st.button("🚀 Forge the MVP", type="primary", use_container_width=True)

# ============================================
# GENERATION
# ============================================
if forge_clicked and pain_point:
    # Initialize session state
    st.session_state['thinking_steps'] = []
    st.session_state['mvp_data'] = None
    
    # Show thinking progress
    progress_bar = st.progress(0)
    status = st.empty()
    
    # Phase 1: Analyze
    status.markdown("### 🔍 GLM-5.1 is analyzing your pain point...")
    progress_bar.progress(15)
    time.sleep(0.3)
    
    # Phase 2: Think
    status.markdown("### 🧠 GLM-5.1 is thinking step-by-step...")
    progress_bar.progress(30)
    time.sleep(0.3)
    
    # Call API
    result = call_glm_api(pain_point)
    
    if result["success"]:
        progress_bar.progress(60)
        status.markdown("### ⚙️ GLM-5.1 is building the MVP...")
        
        # Extract thinking steps
        thinking_steps = extract_thinking_steps(result["content"])
        st.session_state['thinking_steps'] = thinking_steps
        
        # Parse MVP
        mvp_data = parse_mvp_json(result["content"])
        
        if mvp_data:
            st.session_state['mvp_data'] = mvp_data
            progress_bar.progress(100)
            st.success("✅ **MVP Forged Successfully!**")
        else:
            st.error("Could not parse response. Please try again.")
    else:
        st.error(f"API Error: {result.get('error', 'Unknown error')}")

# ============================================
# THINKING STEPS (Expandable)
# ============================================
if st.session_state.get('thinking_steps'):
    with st.expander("🧠 **View GLM-5.1 Thinking Process**", expanded=True):
        st.markdown("""
        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">
            Watch how GLM-5.1 breaks down your problem and designs the solution...
        </p>
        """, unsafe_allow_html=True)
        
        for i, step in enumerate(st.session_state['thinking_steps'], 1):
            st.markdown(f"""
            <div class="thinking-step">
                <span class="thinking-step-number">{i}</span>
                {step}
            </div>
            """, unsafe_allow_html=True)

# ============================================
# RESULTS
# ============================================
if st.session_state.get('mvp_data'):
    mvp = st.session_state['mvp_data']
    
    st.markdown("---")
    st.markdown("## 🎯 Your MVP Blueprint")
    
    # Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 1.5rem;">⏱️</div>
            <div class="stat-value">{mvp.get('time_to_market', '3-5 days')}</div>
            <div style="color: #64748b; font-size: 0.8rem;">Time to Market</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 1.5rem;">💰</div>
            <div class="stat-value">{mvp.get('estimated_cost', '₹2K/mo')}</div>
            <div style="color: #64748b; font-size: 0.8rem;">Est. Cost</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        features = mvp.get('core_features', [])
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 1.5rem;">⚡</div>
            <div class="stat-value">{len(features)}</div>
            <div style="color: #64748b; font-size: 0.8rem;">Features</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 1.5rem;">🔥</div>
            <div class="stat-value">GLM-5.1</div>
            <div style="color: #64748b; font-size: 0.8rem;">AI Powered</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for details
    tab1, tab2, tab3, tab4 = st.tabs([
        "📌 Problem & Users",
        "⚡ Features & Stack", 
        "💻 Generated Code",
        "🚀 Deploy Guide"
    ])
    
    with tab1:
        col_prob, col_users = st.columns(2)
        
        with col_prob:
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📌</div>
                    <div style="font-weight: 700;">Problem Summary</div>
                </div>
                <p style="color: #cbd5e1; line-height: 1.7;">
                    {mvp.get('problem_summary', 'N/A')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_users:
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">👥</div>
                    <div style="font-weight: 700;">Target Users</div>
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
                <div style="font-weight: 700;">Core Features</div>
            </div>
        """, unsafe_allow_html=True)
        features = mvp.get('core_features', [])
        for f in features:
            st.markdown(f'<span class="feature-tag">✨ {f}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tech Stack
        stack = mvp.get('tech_stack', {})
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            st.markdown(f"<div class='stat-card'><div style='color:#64748b;font-size:0.75rem;'>FRONTEND</div><div style='font-weight:600;color:#6366f1'>{stack.get('frontend', 'React')}</div></div>", unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"<div class='stat-card'><div style='color:#64748b;font-size:0.75rem;'>BACKEND</div><div style='font-weight:600;color:#6366f1'>{stack.get('backend', 'Node.js')}</div></div>", unsafe_allow_html=True)
        with col_s3:
            st.markdown(f"<div class='stat-card'><div style='color:#64748b;font-size:0.75rem;'>DATABASE</div><div style='font-weight:600;color:#6366f1'>{stack.get('database', 'PostgreSQL')}</div></div>", unsafe_allow_html=True)
        with col_s4:
            st.markdown(f"<div class='stat-card'><div style='color:#64748b;font-size:0.75rem;'>DEPLOY</div><div style='font-weight:600;color:#6366f1'>{stack.get('deployment', 'GMI Cloud')}</div></div>", unsafe_allow_html=True)
    
    with tab3:
        mvp_code = mvp.get('mvp_code', {})
        if mvp_code:
            filenames = list(mvp_code.keys())
            tabs_code = st.tabs(filenames)
            
            for i, (filename, code) in enumerate(mvp_code.items()):
                with tabs_code[i]:
                    st.markdown(f"""
                    <div class="code-block">
                        <div class="code-header">📄 {filename}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(code, language='python', line_numbers=True)
                    
                    col_dl = st.columns([1, 2, 1])
                    with col_dl[1]:
                        st.download_button(
                            f"📥 Download {filename}",
                            code,
                            filename,
                            mime="text/plain",
                            use_container_width=True
                        )
        else:
            st.info("No code in this response.")
    
    with tab4:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">☁️</div>
                <div style="font-weight: 700;">Deploy to GMI Cloud</div>
            </div>
            <p style="color: #cbd5e1; line-height: 1.7;">
                {mvp.get('deployment_guide', 'Follow setup instructions below.')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">🚀</div>
                <div style="font-weight: 700;">Setup Instructions</div>
            </div>
        """, unsafe_allow_html=True)
        instructions = mvp.get('setup_instructions', [])
        for i, step in enumerate(instructions, 1):
            st.markdown(f"**{i}.** {step}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Big Download Button
    st.markdown("<br>", unsafe_allow_html=True)
    if mvp.get('mvp_code'):
        all_code = json.dumps(mvp.get('mvp_code', {}), indent=2)
        st.download_button(
            "📦 Download All Code",
            all_code,
            f"mvp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            type="primary",
            use_container_width=True
        )

# Footer
st.markdown("""
<hr>
<div class="footer">
    <p>🔥 Built with <strong>GLM-5.1</strong> on <strong>GMI Cloud GPU</strong> | GMIxGLM Hackathon Singapore 2026</p>
</div>
""", unsafe_allow_html=True)
