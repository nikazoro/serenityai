import streamlit as st
import requests
from datetime import datetime
import os
import json

API_BASE = "http://127.0.0.1:8000"
DRAFT_FILE = "data/draft_entry.json"

def show_add_entry():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Write a New Journal Entry")

    # Load persisted draft from file
    if "draft_entry" not in st.session_state:
        if os.path.exists(DRAFT_FILE):
            with open(DRAFT_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                st.session_state.draft_entry = {
                    "date": datetime.strptime(raw.get("date", str(datetime.today())), "%Y-%m-%d"),
                    "text": raw.get("text", ""),
                    "tags": raw.get("tags", ""),
                    "mood_label": raw.get("mood_label", "")
                }
        else:
            st.session_state.draft_entry = {
                "date": datetime.today(),
                "text": "",
                "tags": "",
                "mood_label": ""
            }

    # Form values from session
    draft = st.session_state.draft_entry

    entry_date = st.date_input("Date of Entry", value=draft["date"])
    text = st.text_area("Journal Content", value=draft["text"], height=250)
    word_count = len((text or "").strip().split())
    st.caption(f"Word count: {word_count} word{'s' if word_count != 1 else ''}")

    tags = st.text_input("Tags (comma-separated)", value=draft["tags"])
    mood_options = ["", "joy", "anxious", "reflective", "grateful", "sad", "overwhelmed"]
    mood = st.selectbox("Mood", mood_options, index=mood_options.index(draft["mood_label"]) if draft["mood_label"] in mood_options else 0)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Save Draft"):
            draft_data = {
                "date": entry_date.strftime("%Y-%m-%d"),
                "text": text,
                "tags": tags,
                "mood_label": mood
            }
            with open(DRAFT_FILE, "w", encoding="utf-8") as f:
                json.dump(draft_data, f, indent=2)
            st.session_state.draft_entry = {
                "date": entry_date,
                "text": text,
                "tags": tags,
                "mood_label": mood
            }
            st.success("Draft saved and persisted to file.")

    with col2:
        if st.button("Clear Draft"):
            if os.path.exists(DRAFT_FILE):
                os.remove(DRAFT_FILE)
            st.session_state.draft_entry = {
                "date": datetime.today(),
                "text": "",
                "tags": "",
                "mood_label": ""
            }
            st.success("Draft cleared.")
            st.rerun()

    with col3:
        if st.button("Submit Entry"):
            if not (text or "").strip():
                st.warning("Journal content cannot be empty.")
            else:
                payload = {
                    "text": (text or "").strip(),
                    "date": entry_date.strftime("%Y-%m-%d"),
                    "tags": (tags or "").strip() or None,
                    "mood_label": mood or None,
                    "source_type": "text"
                }
                try:
                    res = requests.post(f"{API_BASE}/create_entry/", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("success"):
                            st.success(f"Entry saved successfully! ID: {data.get('entry_id')}")
                            if data.get("tags"):
                                st.info(f"Auto-tags: {data['tags']}")
                            if data.get("mood_label"):
                                st.info(f"Mood: {data['mood_label']}")
                            # Clear file and session after submission
                            if os.path.exists(DRAFT_FILE):
                                os.remove(DRAFT_FILE)
                            st.session_state.draft_entry = {
                                "date": datetime.today(),
                                "text": "",
                                "tags": "",
                                "mood_label": ""
                            }
                        else:
                            st.warning(data.get("message", "Could not save entry."))
                    else:
                        st.error("Backend error.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Draft Preview
    if st.session_state.draft_entry["text"].strip():
        d = st.session_state.draft_entry
        st.markdown("---")
        st.subheader("Saved Draft Preview")
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.04); padding: 1rem; border-radius: 10px;
                        border: 1px solid rgba(255,255,255,0.1); color: #ccc;">
                <b>Date:</b> {d['date'].strftime("%Y-%m-%d")}<br>
                <b>Tags:</b> {d['tags']}<br>
                <b>Mood:</b> {d['mood_label']}<br><br>
                <b>Text:</b><br>{d['text'].replace('\n', '<br>')}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)