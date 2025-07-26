import streamlit as st
import requests
from datetime import datetime
from collections import defaultdict
import os
import json

API_BASE = "http://127.0.0.1:8000"  # 🔧 Change if hosted elsewhere

def show_entries_by_date():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("📅 Browse Entries by Date")

    try:
        res = requests.get(f"{API_BASE}/entries/")
        if res.status_code == 200:
            raw_entries = res.json()

            # ✅ Group entries by date
            entries_by_date = defaultdict(list)
            for entry in raw_entries:
                entries_by_date[entry["date"]].append(entry)

            # 🗓 Show calendar picker
            all_dates = sorted(entries_by_date.keys(), reverse=True)
            default_date = datetime.strptime(all_dates[0], "%Y-%m-%d") if all_dates else datetime.today()
            date_choice = st.date_input("Pick a date", default_date)
            date_str = date_choice.strftime("%Y-%m-%d")

            # 📘 Show entries for selected date
            if date_str in entries_by_date:
                st.write(f"📝 Entries for {date_str}:")
                for entry in entries_by_date[date_str]:
                    st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); padding: 1rem;
                                    border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
                                    margin-bottom: 1rem; color: #ccc;">
                            <b>ID:</b> {entry["id"]} | <b>Mood:</b> {entry.get("mood_label", "N/A")} | <b>Tags:</b> {entry.get("tags", "")}
                            <div style="margin-top: 0.5rem;">{entry["text"][:400].replace('\n', '<br>')}{"..." if len(entry["text"]) > 400 else ""}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 No entries for this date.")
        else:
            st.error("❌ Failed to fetch entries from backend.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)