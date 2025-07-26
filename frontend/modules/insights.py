import streamlit as st
import requests
from datetime import datetime
from collections import defaultdict
import os
import json

API_BASE = "http://127.0.0.1:8000"  # 🔧 Change if hosted elsewhere


def show_insights():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("📊 Insights")

    try:
        res = requests.get(f"{API_BASE}/insights/")
        if res.status_code == 200:
            data = res.json()
            st.metric("📝 Total Entries", data["total_entries"])
            st.metric("✍️ Avg Word Count", data["average_word_count"])

            st.bar_chart(data["entries_per_day"])
            st.bar_chart(data["entries_per_week"])

            st.subheader("🏷️ Top Tags")
            top_tags = {tag: count for tag, count in data["top_tags"]}
            st.bar_chart(top_tags)

            st.subheader("😶 Mood Distribution")
            mood_dist = {m["mood"]: m["count"] for m in data["mood_distribution"]}
            st.bar_chart(mood_dist)

        else:
            st.error("Failed to load insights.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)