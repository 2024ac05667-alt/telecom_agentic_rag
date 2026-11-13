"""
Streamlit Control Panel & RTL Mobile Diagnostic Interface.
"""

import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="Qatar Telecom Diagnostic System",
    page_icon="📱",
    layout="wide"
)

# Custom RTL & Mobile Styling CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* Global Arabic Font */
    .arabic-text {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Mobile Device Frame Container */
    .mobile-frame {
        max-width: 410px;
        margin: 0 auto;
        border: 12px solid #1f2937;
        border-radius: 40px;
        padding: 20px;
        background-color: #090d16;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .mobile-header {
        text-align: center;
        padding-bottom: 15px;
        border-bottom: 1px solid #374151;
        margin-bottom: 15px;
    }
    
    .arabic-card {
        background-color: #111827;
        border-right: 4px solid #8b0000;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    
    .badge-pii {
        background-color: #ef4444;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

API_ENDPOINT = "http://127.0.0.1:8000/api/diagnose"

# Header & Toolbar
st.title("🇶🇦 Qatar Telecom Multi-Agent Diagnostic Platform")

view_mode = st.radio(
    "Select Display Mode:",
    ["💻 Enterprise Desktop Dashboard", "📱 RTL Mobile Customer View (Smartphone Frame)"],
    horizontal=True
)

st.divider()

# Left Column: Controls & Input
with st.sidebar:
    st.header("🎮 Scenario Presets")
    preset = st.selectbox(
        "Load Quick Test Case:",
        ["Custom Input", "Shattered OLED Screen", "Qatar Repair SLA Enquiry", "PII Scrubbing Test", "Out of Scope Recipe"]
    )
    
    default_text = ""
    if preset == "Shattered OLED Screen":
        default_text = "My phone screen is cracked and showing green display lines. What is the repair timeline under Qatar law?"
    elif preset == "Qatar Repair SLA Enquiry":
        default_text = "کم تستغرق عملية إصلاح جهاز محمول في قطر وفقاً للائحة حماية المستهلك؟"
    elif preset == "PII Scrubbing Test":
        default_text = "Check status for QID 29812345678 and mobile 55123456 regarding device repair."
    elif preset == "Out of Scope Recipe":
        default_text = "Can you give me an authentic recipe for Qatari Machboos?"

    user_query = st.text_area("User Diagnostic Request:", value=default_text, height=120)
    uploaded_file = st.file_uploader("Upload Device Damage Image (Optional):", type=["jpg", "jpeg", "png"])
    
    submit_btn = st.button("🚀 Run Multi-Agent Diagnostic Pipeline", use_container_width=True)

# Processing Logic
if submit_btn and user_query:
    with st.spinner("Executing LangGraph Agents & Vision Engine..."):
        try:
            files = {}
            if uploaded_file:
                files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            data = {"query": user_query}
            
            response = requests.post(API_ENDPOINT, data=data, files=files)
            
            if response.status_code == 200:
                res = response.json()
                st.session_state["last_result"] = res
            else:
                st.error(f"Backend API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Failed to connect to FastAPI Backend ({API_ENDPOINT}). Error: {str(e)}")

# Display Result Viewports
if "last_result" in st.session_state:
    res = st.session_state["last_result"]
    
    if view_mode == "💻 Enterprise Desktop Dashboard":
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("📋 Bilingual Diagnostic Report")
            
            if res.get("pii_scrubbed"):
                st.markdown('<span class="badge-pii">⚠️ PII Sanitized by Security Sentinel</span>', unsafe_allow_html=True)
                st.write("")

            st.markdown("### 🇬🇧 English Summary")
            st.info(res.get("response_en", ""))
            
            st.markdown("### 🇶🇦 Arabic Summary (RTL)")
            st.markdown(f'<div class="arabic-card arabic-text">{res.get("response_ar", "")}</div>', unsafe_allow_html=True)
            
            st.divider()
            st.markdown(f"**RAG Context:** `{res.get('policy_context')}`")
            st.markdown(f"**Hardware Assessment:** `{res.get('hardware_assessment')}`")
            
        with col2:
            st.subheader("🔍 LangGraph Trace Logs")
            st.metric("Execution Latency", f"{res.get('latency_seconds')} seconds")
            
            for log in res.get("agent_history", []):
                st.code(log, language="text")

    else:
        # RTL Mobile Phone Shell View
        st.markdown("""
        <div class="mobile-frame">
            <div class="mobile-header">
                <h4 style="color:white; margin:0;">🇶🇦 Qatar Mobile Support</h4>
                <small style="color:#9ca3af;">تطبيق التشخيص والدعم الفني</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        m_col1, m_col2, m_col3 = st.columns([1, 2, 1])
        with m_col2:
            st.markdown(f'''
            <div class="arabic-card arabic-text">
                <h4 style="color: #f87171; margin-top:0;">نتيجة التشخيص:</h4>
                <p style="color: #e5e7eb; font-size: 1.05rem; line-height: 1.6;">
                    {res.get("response_ar", "")}
                </p>
                <hr style="border-color:#374151;">
                <small style="color:#9ca3af;">English Reference:</small>
                <p style="color:#d1d5db; font-size:0.9rem;">{res.get("response_en", "")}</p>
            </div>
            ''', unsafe_allow_html=True)