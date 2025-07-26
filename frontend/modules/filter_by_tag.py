import streamlit as st
import requests
from datetime import datetime
from collections import defaultdict
import os
import json

API_BASE = "http://127.0.0.1:8000"  # 🔧 Change if hosted elsewhere

def show_filter_by_tag():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("🏷️ Filter Journal Entries by Tag")

    try:
        tags_res = requests.get(f"{API_BASE}/tags")
        if tags_res.status_code == 200:
            tags = tags_res.json()
            selected_tag = st.selectbox("Select a tag", tags)
            if selected_tag:
                filter_res = requests.get(f"{API_BASE}/filter", params={"tag": selected_tag})
                if filter_res.status_code == 200:
                    entries = filter_res.json()
                    for entry in entries:
                        st.markdown(f"- ✍️ `{entry['id']}`: {entry.get('text', '')[:100]}...")
                else:
                    st.warning("No entries found for this tag.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)