import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"  # 🔧 Change if hosted elsewhere

def show_upload_journal():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("📂 Upload Journal File")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "json", "jpg", "png", "mp3", "wav", "m4a"])

    if uploaded_file is not None:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        try:
            res = requests.post(f"{API_BASE}/upload/", files=files)
            if res.status_code == 200:
                st.success(res.json()["message"])
            else:
                st.error("❌ Upload failed.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)