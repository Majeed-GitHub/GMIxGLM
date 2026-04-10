"""
GLM PainForge - Transform Pain Points into Full MVPs
Powered by GLM-5.1 on GMI Cloud | GMIxGLM Hackathon 2026
"""

import streamlit as st
import requests
import json
import re
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="GLM PainForge",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuration
GMI_BASE_URL = "https://api.gmi-serving.com/v1"
GMI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjBkMWMzYTJiLWZiMmEtNDNhOS04MGVlLWEzNWNlZTRlYjIyNiIsInNjb2BlIjoiaWVfbW9kZWwiLCJjbGllbnRJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCJ9.EEEh20kvdGvMExxJ9cV9-DShA-1rRPTIULLEyUAhORw"
MODEL_NAME = "zai-org/GLM-5.1-FP8"

# System prompt
MVP_BUILDER_PROMPT = """You are an elite startup CTO and full-stack developer. Transform ANY pain point into a complete, deployable MVP.

OUTPUT JSON with these exact keys:
{
    "problem_summary": "2 sentence description",
    "target_users": ["user1", "user2"],
    "core_features": ["feature1", "feature2", "feature3"],
    "tech_stack": {"frontend": "tech", "backend": "tech", "database": "tech", "deployment": "tech"},
    "mvp_code": {"filename": "full code..."},
    "setup_instructions": ["step1", "step2"],
    "deployment_guide": "how to deploy",
    "estimated_cost": "₹X/month",
    "time_to_market": "X days"
}

Include COMPLETE RUNNABLE code. Use React/Next.js, Node.js/Python, PostgreSQL/Supabase. Focus on Indian market: UPI payments, WhatsApp integration, regional language support.

Output valid JSON only, no markdown blocks."""


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
        return {"success": True, "content": result["choices"][0]["message"]["content"], "usage": result.get("usage", {})}
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


# Custom CSS - Professional Dark Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    /* Header */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 24px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .title-main {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        letter-spacing: -2px;
    }
    
    .subtitle {
        font-size: 1.4rem;
        color: #a0a0a0;
        font-weight: 300;
    }
    
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .card-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Stats */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #888;
        margin-top: 0.5rem;
    }
    
    /* Features */
    .feature-tag {
        display: inline-block;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(139, 92, 246, 0.2));
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 0.4rem 1rem;
        border-radius: 25px;
        margin: 0.3rem;
        font-size: 0.9rem;
    }
    
    /* Code block */
    .code-section {
        background: #0d1117;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .code-header {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.9rem;
        color: #888;
    }
    
    /* Button */
    .forge-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1.2rem 3rem;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 16px;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .forge-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Textarea */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 16px !important;
        color: white !important;
        font-size: 1.1rem !important;
        padding: 1.5rem !important;
        min-height: 200px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 30px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Templates */
    .template-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .template-btn:hover {
        background: rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
        margin: 2rem 0;
    }
    
    /* Tech stack */
    .tech-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
    }
    
    .tech-box {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .tech-label {
        font-size: 0.75rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .tech-value {
        font-size: 1rem;
        font-weight: 600;
        color: #667eea;
        margin-top: 0.3rem;
    }
    
    /* Success animation */
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .success-icon {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="hero-section">
    <div class="badge">🏆 GMIxGLM Hackathon Singapore 2026</div>
    <h1 class="title-main">🔥 GLM PainForge</h1>
    <p class="subtitle">Transform Pain Points into Full MVPs with GLM-5.1 AI</p>
</div>
""", unsafe_allow_html=True)

# Main content
col_input, col_templates = st.columns([1.5, 1])

with col_input:
    st.markdown('<div class="card"><div class="card-header">💭 Describe Your Pain Point</div>', unsafe_allow_html=True)
    pain_point = st.text_area(
        "",
        placeholder="Example: Indian freelancers need a simple tool to send invoices, track UPI payments, and send payment reminders via WhatsApp...",
        label_visibility="collapsed",
        height=200
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_templates:
    st.markdown('<div class="card"><div class="card-header">⚡ Quick Templates</div>', unsafe_allow_html=True)
    templates = {
        "🛒": "E-commerce store with WhatsApp orders and UPI payments",
        "💼": "Freelancer invoicing with UPI QR and payment tracking",
        "🏪": "Kirana store WhatsApp ordering with delivery tracking",
        "📚": "Live coding tutoring platform for students",
        "🏥": "Clinic appointment booking with SMS reminders",
        "🚗": "Local delivery service with real-time tracking"
    }
    for emoji, desc in templates.items():
        if st.button(f"{emoji} {desc[:20]}...", key=emoji, use_container_width=True):
            st.session_state['template'] = desc

# Template display
if 'template' in st.session_state:
    pain_point = st.text_area("Selected Template", st.session_state['template'], key="template_area", label_visibility="collapsed", height=150)

st.markdown("<hr>", unsafe_allow_html=True)

# Forge button
col_btn = st.columns([1])
with col_btn[0]:
    forge_clicked = st.button("🚀 Forge the MVP", type="primary", use_container_width=True)

# Results
if forge_clicked and pain_point:
    progress_bar = st.progress(0)
    status = st.empty()
    
    status.markdown("🔍 **Analyzing your pain point with GLM-5.1...**")
    progress_bar.progress(25)
    
    status.markdown("🧠 **GLM-5.1 is thinking... (30-60 seconds)**")
    progress_bar.progress(50)
    
    result = call_glm_api(pain_point)
    
    if result["success"]:
        progress_bar.progress(75)
        status.markdown("✨ **Parsing MVP Blueprint...**")
        
        mvp_data = parse_mvp_json(result["content"])
        
        if mvp_data:
            st.session_state['mvp_data'] = mvp_data
            progress_bar.progress(100)
            st.success("🎉 **MVP Forged Successfully!**")
        else:
            st.error("Could not parse response. Please try again.")
    else:
        st.error(f"API Error: {result.get('error', 'Unknown error')}")

# Display results
if 'mvp_data' in st.session_state and st.session_state['mvp_data']:
    mvp = st.session_state['mvp_data']
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("## 🎯 Your MVP Blueprint")
    
    # Stats
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-number">⏱️</div>
            <div class="stat-label">{mvp.get('time_to_market', '3-5 days')}</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">💰</div>
            <div class="stat-label">{mvp.get('estimated_cost', '₹2,000/mo')}</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{len(mvp.get('core_features', []))}</div>
            <div class="stat-label">Features</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">🔥</div>
            <div class="stat-label">GLM-5.1</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Problem & Users
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">📌 Problem</div>
            <p>{mvp.get('problem_summary', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        users = mvp.get('target_users', [])
        st.markdown(f"""
        <div class="card">
            <div class="card-header">👥 Target Users</div>
            {''.join([f'<li>{u}</li>' for u in users[:3]])}
        </div>
        """, unsafe_allow_html=True)
    
    # Features
    st.markdown('<div class="card"><div class="card-header">⚡ Core Features</div>', unsafe_allow_html=True)
    features = mvp.get('core_features', [])
    for f in features:
        st.markdown(f'<span class="feature-tag">{f}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tech Stack
    stack = mvp.get('tech_stack', {})
    st.markdown('<div class="card"><div class="card-header">🛠️ Tech Stack</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="tech-grid">
        <div class="tech-box">
            <div class="tech-label">Frontend</div>
            <div class="tech-value">{stack.get('frontend', 'React')}</div>
        </div>
        <div class="tech-box">
            <div class="tech-label">Backend</div>
            <div class="tech-value">{stack.get('backend', 'Node.js')}</div>
        </div>
        <div class="tech-box">
            <div class="tech-label">Database</div>
            <div class="tech-value">{stack.get('database', 'PostgreSQL')}</div>
        </div>
        <div class="tech-box">
            <div class="tech-label">Deploy</div>
            <div class="tech-value">{stack.get('deployment', 'Vercel')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code
    mvp_code = mvp.get('mvp_code', {})
    if mvp_code:
        st.markdown('<div class="card"><div class="card-header">💻 Generated Code</div>', unsafe_allow_html=True)
        tabs = st.tabs(list(mvp_code.keys()))
        for i, (filename, code) in enumerate(mvp_code.items()):
            with tabs[i]:
                st.code(code, language=get_lang(filename), line_numbers=True)
                st.download_button(f"📥 Download {filename}", code, filename, mime="text/plain")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Setup
    col1, col2 = st.columns(2)
    with col1:
        instructions = mvp.get('setup_instructions', [])
        if instructions:
            st.markdown(f"""
            <div class="card">
                <div class="card-header">🚀 Setup</div>
                {''.join([f'<p>{i+1}. {s}</p>' for i, s in enumerate(instructions[:3])])}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">☁️ Deploy</div>
            <p>{mvp.get('deployment_guide', 'Follow setup instructions')}</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>🔥 Built with GLM-5.1 on GMI Cloud GPU | GMIxGLM Hackathon Singapore 2026</p>
    <p style="font-size: 0.8rem;">Powered by Z.ai | GMI Cloud | OpenCode</p>
</div>
""", unsafe_allow_html=True)

def get_lang(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.jsx': 'jsx', '.tsx': 'tsx', '.html': 'html', '.css': 'css', '.json': 'json'}.get(ext, 'text')
