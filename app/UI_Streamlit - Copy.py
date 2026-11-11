"""
Streamlit Dual-Mode User Interface with Live Agent Trace Terminal.
"""

import requests
import streamlit as st

st.set_page_config(
    page_title="Qatar Mobile - Diagnostic Agent Portal",
    page_icon="📱",
    layout="wide",
)

RTL_CSS = """
<style>
    .rtl-box {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
        background-color: #f8f9fa;
        border-right: 5px solid #007bff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #1f2937;
    }
    .ltr-box {
        direction: ltr;
        text-align: left;
        background-color: #e9ecef;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #1f2937;
    }
</style>
"""
st.markdown(RTL_CSS, unsafe_allow_html=True)

st.title("📱 Qatar Mobile Hardware Diagnostic Portal")
st.caption("Multi-Agent Supervisor Architecture + Model Context Protocol (MCP)")

view_mode = st.sidebar.radio(
    "Select Interface Mode", ["العربية (Mobile View)", "English (Desktop Service Desk)"]
)

api_url = "http://127.0.0.1:8000/diagnose"

if "العربية" in view_mode:
    st.subheader("مركز الصيانة الفنية والتشخيص الذكي")

    with st.form("arabic_form"):
        ar_query = st.text_area(
            "وصف المشكلة (يدعم اللغة العربية والعيوب الفنية):",
            placeholder="مثال: الشاشة مكسورة ورقم بطاقتي الشخصية 28412345678...",
        )
        ar_image = st.file_uploader("إرفاق صورة الجهاز:", type=["jpg", "png", "jpeg"])
        submit_ar = st.form_submit_button("إرسال طلب الصيانة")

    if submit_ar and ar_query:
        with st.spinner("جاري معالجة الطلب عبر الوكلاء الأذكياء..."):
            files = {"image": ar_image.getvalue()} if ar_image else None
            data = {"query": ar_query, "language": "ar"}

            try:
                response = requests.post(api_url, data=data, files=files if ar_image else None)
                if response.status_code == 200:
                    res = response.json()
                    st.success("تم إكمال التشخيص بنجاح!")

                    st.markdown(
                        f"""
                        <div class="rtl-box">
                            <h4>نتيجة التشخيص:</h4>
                            <p>{res.get('response_ar') or res.get('response_en')}</p>
                            <hr>
                            <small>حالة البيانات: تم حجب البيانات الشخصية ({res.get('pii_scrubbed')})</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    with st.expander("🕵️ سجل تفاوض الوكلاء الأذكياء (Live Execution Trace)", expanded=True):
                        for log in res.get("execution_trace", []):
                            st.write(log)
            except Exception as e:
                st.error(f"خطأ في الاتصال بالخادم: {e}")

else:
    st.subheader("Desktop Service Desk Portal")

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.form("english_form"):
            en_query = st.text_area(
                "Customer Issue Description:",
                placeholder="e.g. Screen is cracked and battery dies fast. QID 28412345678.",
            )
            en_image = st.file_uploader("Upload Photograph:", type=["jpg", "png", "jpeg"])
            submit_en = st.form_submit_button("Run Diagnostic Agent")

    with col2:
        st.subheader("Diagnostic Engine Output")
        if submit_en and en_query:
            with st.spinner("Executing Multi-Agent Graph..."):
                files = {"image": en_image.getvalue()} if en_image else None
                data = {"query": en_query, "language": "en"}

                try:
                    response = requests.post(api_url, data=data, files=files if en_image else None)
                    if response.status_code == 200:
                        res = response.json()

                        st.markdown(
                            f"""
                            <div class="ltr-box">
                                <b>PII Redacted:</b> {res.get('pii_scrubbed')}<br><br>
                                <b>Technical Deliverable:</b><br>{res.get('response_en')}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        with st.expander("🕵️ Live Multi-Agent Execution Trace", expanded=True):
                            for log in res.get("execution_trace", []):
                                st.write(log)
                except Exception as e:
                    st.error(f"Could not connect to FastAPI server: {e}")