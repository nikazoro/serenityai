import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

def reset_page():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("🧨 Reset All Data")

    st.warning("⚠️ This will delete all journal entries, embeddings, and reset your app's database.")

    if st.button("🔁 Reset Everything"):
        try:
            res = requests.post(f"{API_BASE}/reset/")
            if res.status_code == 200:
                message = res.json().get("message", "Reset successful.")
                st.success("✅ Reset Successful")
                st.text_area("Response", value=message, height=100, disabled=True)
            else:
                st.error("❌ Reset Failed")
                st.text_area("Error Detail", value=res.text, height=100, disabled=True)
        except Exception as e:
            st.error("⚠️ An error occurred while contacting the backend.")
            st.text_area("Exception", value=str(e), height=100, disabled=True)

    st.markdown("</div>", unsafe_allow_html=True)
