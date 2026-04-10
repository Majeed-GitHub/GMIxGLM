"""
GLM PainForge - Transform Pain Points into Full MVPs in Seconds
Powered by GLM-5.1 on GMI Cloud
GMIxGLM Hackathon 2026
"""

import streamlit as st
import requests
import json
import re
import os
from datetime import datetime

# Configuration
GMI_BASE_URL = "https://api.gmi-serving.com/v1"
GMI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImRiZDcwYWM2LWYyZTItNGNmYy1iNmQ3LTRiMGE1ZTM5N2E2ZSIsInNjb3BlIjoiaWVfbW9kZWwiLCJjbGllbnRJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCJ9.fP705Pn7n-uX4SXM44RUJQpJv-kU8GVaMf6c8p8hyxs"
MODEL_NAME = "zai-org/GLM-5.1-FP8"  # Correct model name for GMI Cloud

# System prompt for MVP Builder Agent
MVP_BUILDER_PROMPT = """You are an elite startup CTO and full-stack developer with 15+ years of experience. 
Your mission is to transform ANY pain point into a complete, deployable MVP in seconds.

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
    "mvp_code": {
        "filename1": "full code content...",
        "filename2": "full code content..."
    },
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

INDIAN STARTUP CONTEXT:
- Integrate UPI/GPay/PhonePe payment flows
- WhatsApp Business API for notifications
- Support Hindi/Hinglish in UI
- Compliance with Indian data laws (PDPA)
- Consider Bharat-focused use cases:
  * Kirana store management
  * Freelancer invoicing
  * Tutoring/ coaching platforms
  * Healthcare appointment booking
  * Local service marketplace

STARTUP FOCUS:
- B2B SaaS for SMBs
- Marketplace models
- SaaS with freemium tiers
- Micro-SaaS (single problem solvers)

Generate the complete MVP blueprint now."""


def call_glm_api(prompt: str, thinking_enabled: bool = True) -> dict:
    """Call GMI Cloud GLM-5.1 API with thinking support"""
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
        "max_tokens": 8192
    }
    
    try:
        response = requests.post(
            f"{GMI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "content": result["choices"][0]["message"]["content"],
            "usage": result.get("usage", {})
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def parse_mvp_json(content: str) -> dict:
    """Parse the JSON response from GLM"""
    # Try to extract JSON from the response
    json_match = re.search(r'\{[\s\S]*\}', content)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON in code blocks
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None


def extract_thinking_steps(content: str) -> list:
    """Extract thinking/reasoning steps from the response"""
    steps = []
    
    # Split by common thinking indicators
    patterns = [
        r'\*\*Thinking[:\]?\s*\*\*\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)',
        r'###\s*Step\s*(\d+)[:\s]*([^\n]+(?:\n(?!\###)[^\n]+)*)',
        r'(\d+\.\s*\*\*[^*]+\*\*[:\s]*[^\n]+(?:\n(?!\d+\.)[^\n]+)*)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            step_text = match.group(0).strip()
            if len(step_text) > 20:
                steps.append(step_text[:200])
    
    # If no structured steps found, create logical chunks
    if not steps:
        sentences = content.split('. ')
        current_step = []
        for sent in sentences[:20]:  # First 20 sentences as thinking
            current_step.append(sent)
            if len(current_step) >= 3:
                steps.append('. '.join(current_step) + '.')
                current_step = []
    
    return steps[:10]  # Limit to 10 steps


def main():
    # Page config
    st.set_page_config(
        page_title="GLM PainForge",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    
    .title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #a0a0a0;
        margin-bottom: 2rem;
    }
    
    .hackathon-badge {
        background: linear-gradient(90deg, #667eea, #764ba2);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        color: white;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 2rem;
    }
    
    .pain-input {
        background: rgba(255,255,255,0.05);
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    .forge-button {
        background: linear-gradient(90deg, #4d96ff, #6b5ce7);
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
        padding: 1rem 3rem;
        border-radius: 50px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 40px rgba(77, 150, 255, 0.3);
    }
    
    .forge-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 50px rgba(77, 150, 255, 0.5);
    }
    
    .result-card {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .thinking-step {
        background: rgba(77, 150, 255, 0.1);
        border-left: 4px solid #4d96ff;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0 12px 12px 0;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .code-block {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 1.5rem;
        font-family: 'Fira Code', monospace;
        overflow-x: auto;
    }
    
    .feature-tag {
        background: linear-gradient(90deg, #667eea, #764ba2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        color: white;
        font-size: 0.85rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #4d96ff;
    }
    
    .download-btn {
        background: linear-gradient(90deg, #6bcb77, #4d96ff);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 30px;
        border: none;
        font-weight: 600;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="hackathon-badge">🏆 GMIxGLM Hackathon Singapore 2026</div>
        <h1 class="title">🔥 GLM PainForge</h1>
        <p class="subtitle">Pain → Full MVP in seconds | Powered by GLM-5.1 on GMI Cloud</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💭 Describe Your Pain Point")
        
        pain_point = st.text_area(
            "",
            placeholder="""Example: "I'm a freelancer in India who loses track of client payments. I need a simple tool to send invoices, track UPI payments, and remind clients without using complicated accounting software."

Or: "My kirana store loses customers because I can't deliver in 30 minutes like Dunzo. I want a WhatsApp-based ordering system that my staff can use easily."

Or: "College students in tier-2 cities need affordable coding tutoring, but Zoom is too complex and Google Meet has time limits. Build a simple 1-on-1 live coding platform.""",
            height=300,
            label_visibility="collapsed"
        )
        
        st.markdown("""
        <style>
        .stTextArea textarea {
            background: rgba(255,255,255,0.08);
            border: 2px solid rgba(77, 150, 255, 0.3);
            border-radius: 16px;
            color: white;
            font-size: 1rem;
            padding: 1rem;
        }
        .stTextArea textarea:focus {
            border-color: #4d96ff;
            box-shadow: 0 0 20px rgba(77, 150, 255, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ⚡ Quick Templates")
        templates = {
            "🛒 E-commerce": "Small boutique owner needs online store with WhatsApp orders and UPI payments",
            "📱 SaaS App": "B2B SaaS for gyms to manage members, track attendance, and send renewal reminders",
            "💼 Freelancer": "Indian freelancer needs to send professional invoices and track payments via UPI QR",
            "🏪 Local Delivery": "Kirana store wants WhatsApp ordering with 30-min delivery tracking",
            "📚 EdTech": "Tutor platform connecting teachers with students for live coding sessions",
            "🏥 Healthcare": "Clinic appointment booking with WhatsApp reminders and SMS alerts"
        }
        
        for name, template in templates.items():
            if st.button(name, key=f"btn_{name}"):
                st.session_state['template'] = template
    
    # Template display
    if 'template' in st.session_state:
        pain_point = st.text_area(
            "Selected Template",
            value=st.session_state['template'],
            height=200,
            key="template_input",
            label_visibility="collapsed"
        )
    
    # Forge button
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        forge_clicked = st.button(
            "🚀 Forge the MVP",
            type="primary",
            use_container_width=True
        )
    
    # Results area
    if forge_clicked and pain_point:
        # Initialize session state
        if 'mvp_data' not in st.session_state:
            st.session_state['mvp_data'] = None
        if 'thinking_steps' not in st.session_state:
            st.session_state['thinking_steps'] = []
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Analyzing
        status_text.markdown("### 🔍 **GLM-5.1 is analyzing your pain point...**")
        progress_bar.progress(20)
        
        # Show thinking steps area
        thinking_placeholder = st.empty()
        
        # Call API
        status_text.markdown("### 🧠 **GLM-5.1 is thinking... (This takes ~30 seconds)**")
        progress_bar.progress(40)
        
        result = call_glm_api(pain_point)
        
        if result["success"]:
            progress_bar.progress(70)
            status_text.markdown("### ✨ **Parsing MVP Blueprint...**")
            
            # Extract thinking steps
            thinking_steps = extract_thinking_steps(result["content"])
            st.session_state['thinking_steps'] = thinking_steps
            
            # Parse MVP data
            mvp_data = parse_mvp_json(result["content"])
            
            if mvp_data:
                st.session_state['mvp_data'] = mvp_data
                progress_bar.progress(100)
                status_text.markdown("### 🎉 **MVP Forged Successfully!**")
            else:
                st.error("Failed to parse MVP response. Please try again.")
        else:
            error_msg = result.get('error', 'Unknown error')
            if 'insufficient balance' in error_msg.lower() or '402' in str(error_msg):
                st.error("⚠️ **Insufficient API Credits** - Please add credits to your GMI Cloud account to use GLM-5.1")
                st.info("💡 **Hackathon Solution:** Visit the GMI Cloud booth to get free credits for the hackathon!")
            else:
                st.error(f"API Error: {error_msg}")
    
    # Display results
    if st.session_state.get('mvp_data'):
        mvp = st.session_state['mvp_data']
        
        st.markdown("---")
        st.markdown("## 🎯 Your MVP Blueprint")
        
        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">⏱️ {mvp.get('time_to_market', '3-5 days')}</div>
                <div>Time to Market</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">💰 {mvp.get('estimated_cost', '₹2,000/month')}</div>
                <div>Monthly Cost</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            features = mvp.get('core_features', [])
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(features)}</div>
                <div>Core Features</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            stack = mvp.get('tech_stack', {})
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stack.get('frontend', 'React')}</div>
                <div>Tech Stack</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Problem & Users
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="result-card">
                <h3>📌 Problem Summary</h3>
            """, unsafe_allow_html=True)
            st.markdown(mvp.get('problem_summary', 'Problem not specified'))
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="result-card">
                <h3>👥 Target Users</h3>
            """, unsafe_allow_html=True)
            users = mvp.get('target_users', [])
            for user in users:
                st.markdown(f"- {user}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Features
        st.markdown("""
        <div class="result-card">
            <h3>⚡ Core Features</h3>
        """, unsafe_allow_html=True)
        
        features = mvp.get('core_features', [])
        for feature in features:
            st.markdown(f'<span class="feature-tag">{feature}</span>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Tech Stack
        st.markdown("""
        <div class="result-card">
            <h3>🛠️ Tech Stack</h3>
        """, unsafe_allow_html=True)
        
        stack = mvp.get('tech_stack', {})
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown(f"**Frontend:** {stack.get('frontend', 'React')}")
        with cols[1]:
            st.markdown(f"**Backend:** {stack.get('backend', 'Node.js')}")
        with cols[2]:
            st.markdown(f"**Database:** {stack.get('database', 'PostgreSQL')}")
        with cols[3]:
            st.markdown(f"**Deploy:** {stack.get('deployment', 'Vercel')}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Code files
        st.markdown("""
        <div class="result-card">
            <h3>💻 Generated Code</h3>
        """, unsafe_allow_html=True)
        
        mvp_code = mvp.get('mvp_code', {})
        
        if mvp_code:
            tabs = st.tabs(list(mvp_code.keys()))
            
            for i, (filename, code) in enumerate(mvp_code.items()):
                with tabs[i]:
                    st.code(code, language=get_language(filename), line_numbers=True)
                    
                    # Download button for each file
                    st.download_button(
                        f"📥 Download {filename}",
                        code,
                        file_name=filename,
                        mime="text/plain"
                    )
        else:
            st.info("Code generation not available in this response.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Setup & Deployment
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="result-card">
                <h3>🚀 Setup Instructions</h3>
            """, unsafe_allow_html=True)
            instructions = mvp.get('setup_instructions', [])
            for i, step in enumerate(instructions, 1):
                st.markdown(f"**{i}.** {step}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="result-card">
                <h3>☁️ Deploy to GMI Cloud</h3>
            """, unsafe_allow_html=True)
            st.markdown(mvp.get('deployment_guide', 'Deployment guide not available'))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Download all as ZIP
        st.markdown("<br>", unsafe_allow_html=True)
        
        if mvp_code:
            full_code = json.dumps(mvp_code, indent=2)
            st.download_button(
                "📦 Download All Code as JSON",
                full_code,
                file_name=f"mvp_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                type="primary"
            )
    
    # Thinking steps accordion
    if st.session_state.get('thinking_steps'):
        with st.expander("🧠 View GLM-5.1 Thinking Process", expanded=False):
            for i, step in enumerate(st.session_state['thinking_steps'], 1):
                st.markdown(f"""
                <div class="thinking-step">
                    <strong>Step {i}:</strong> {step}
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🔥 Built with GLM-5.1 on GMI Cloud GPU | GMIxGLM Hackathon Singapore 2026</p>
        <p style="font-size: 0.8rem;">Powered by Z.ai | GMI Cloud | OpenCode</p>
    </div>
    """, unsafe_allow_html=True)

def get_language(filename: str) -> str:
    """Get language for code highlighting"""
    ext = os.path.splitext(filename)[1].lower()
    lang_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.sql': 'sql',
        '.sh': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml',
    }
    return lang_map.get(ext, 'text')


if __name__ == "__main__":
    main()
