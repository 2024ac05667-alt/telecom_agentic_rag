import streamlit as st
import requests
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="Qatar Mobile Enterprise AI Agent",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling for Enterprise Look & Feel ---
st.markdown("""
<style>
    .chat-card-user {
        background-color: #F0F2F6;
        padding: 12px 18px;
        border-radius: 15px 15px 2px 15px;
        margin-bottom: 10px;
        color: #1E1E1E;
    }
    .chat-card-agent {
        background-color: #0E1117;
        color: #FFFFFF;
        padding: 16px 20px;
        border-radius: 15px 15px 15px 2px;
        margin-bottom: 15px;
        border: 1px solid #262730;
    }
    .status-badge {
        font-size: 0.8rem;
        padding: 4px 10px;
        border-radius: 12px;
        background-color: #1E3A8A;
        color: #93C5FD;
        display: inline-block;
        margin-right: 5px;
    }
    .agent-trace {
        font-family: monospace;
        background: #111827;
        padding: 10px;
        border-radius: 6px;
        color: #10B981;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/smartphone-ram.png", width=64)
    st.title("Enterprise Control Center")
    st.caption("Qatar Telecom Diagnostics RAG v2.0")
    
    st.divider()
    
    mode = st.radio(
        "Select User Viewpoint:",
        ["📱 Customer View (Bilingual)", "🛠️ Technician & Supervisor Dashboard"]
    )
    
    st.divider()
    if st.button("🗑️ Clear Session History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Layout ---
st.title("📱 Qatar Telecom Diagnostic & SLA Assistant")
st.caption("Powered by Gemini 2.5 Flash Multi-Agent Architecture & ChromaDB Policy RAG")

# --- Render Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image_bytes" in msg and msg["image_bytes"]:
            st.image(msg["image_bytes"], caption="Attached Device Photo", width=250)
        
        st.markdown(msg["content"])
        
        # If there's trace metadata available, show it in tech mode
        if "trace" in msg and "Technician" in mode:
            with st.expander("🔍 LangGraph Supervisor Trace Execution", expanded=False):
                for step in msg["trace"]:
                    st.markdown(f"`{step}`")

# --- Chat Input Controls ---
with st.container():
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        uploaded_file = st.file_uploader("Attach Photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
prompt = st.chat_input("Ask about device diagnostics, repair turnaround times, or Qatar SLA laws...")

# --- Process Input ---
if prompt:
    # Read image if attached
    img_bytes = uploaded_file.getvalue() if uploaded_file else None

    # Append User Message to UI
    user_msg = {"role": "user", "content": prompt}
    if img_bytes:
        user_msg["image_bytes"] = img_bytes
    st.session_state.messages.append(user_msg)

    # Render User Message immediately
    with st.chat_message("user"):
        if img_bytes:
            st.image(img_bytes, caption="Attached Device Photo", width=250)
        st.markdown(prompt)

    # Call FastAPI Service
    with st.chat_message("assistant"):
        with st.spinner("🧠 LangGraph agents inspecting hardware and retrieving Qatar SLA policies..."):
            try:
                files = {"image": ("device.jpg", img_bytes, "image/jpeg")} if img_bytes else None
                payload = {
                    "query": prompt,
                    "language": "ar" if "Arabic" in prompt or any('\u0600' <= c <= '\u06FF' for c in prompt) else "en"
                }

                response = requests.post("http://127.0.0.1:8000/diagnose", data=payload, files=files)

                if response.status_code == 200:
                    data = response.json()
                    
                    response_en = data.get("response_en", "Diagnostic completed.")
                    response_ar = data.get("response_ar", "تم التشخيص بنجاح.")
                    trace = data.get("trace", [])
                    pii_scrubbed = data.get("pii_scrubbed", False)

                    # Build Response View
                    if pii_scrubbed:
                        st.warning("🔒 SecuritySentinel: Personal Identifiable Information (QID/Phone) detected and scrubbed.")
                    
                    full_response = f"""
### Diagnostic Assessment & SLA Timeline

{response_en}

---
**التقرير باللغة العربية:**  
{response_ar}
"""
                    st.markdown(full_response)

                    if "Technician" in mode:
                        with st.expander("🔍 LangGraph Supervisor Trace Execution", expanded=True):
                            for step in trace:
                                st.markdown(f"`{step}`")

                    # Append Assistant Message to History
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "trace": trace
                    })

                else:
                    st.error(f"Backend Service Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Failed to connect to FastAPI Backend (127.0.0.1:8000): {str(e)}")