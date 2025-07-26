import streamlit as st
import requests
from datetime import datetime
from collections import defaultdict
import os
import json

API_BASE = "http://127.0.0.1:8000"  # 🔧 Change if hosted elsewhere

def show_reflect():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("🪞 Reflect on a Journal Entry")

    # 🧠 Initialize stored reflections
    if "reflections" not in st.session_state:
        st.session_state.reflections = {}

    try:
        entries_res = requests.get(f"{API_BASE}/entries/")
        if entries_res.status_code == 200:
            raw_entries = entries_res.json()

            # ✅ Normalize entries
            if isinstance(raw_entries, dict):
                all_entries = []
                for entry_list in raw_entries.values():
                    all_entries.extend(entry_list)
            else:
                all_entries = raw_entries

            # 🧾 Build dropdown
            entry_map = {
                f"{entry['id']} | {entry['date']} | {entry['text'][:40].replace('\n', ' ')}...": entry
                for entry in all_entries
            }

            selected = st.selectbox("Choose an entry", list(entry_map.keys()))

            if selected:
                entry = entry_map[selected]
                eid = entry["id"]

                # ✍️ Show full journal text
                st.markdown("### 📓 Full Journal Entry")
                st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); padding: 1rem;
                                border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
                                color: #ccc;">
                        {entry['text'].replace('\n', '<br>')}
                    </div>
                """, unsafe_allow_html=True)

                # 🧠 Reflect if not already done
                if eid in st.session_state.reflections:
                    reflection = st.session_state.reflections[eid]
                else:
                    reflect_res = requests.post(f"{API_BASE}/reflect/", json={"entry_id": eid})
                    if reflect_res.status_code == 200:
                        reflection = reflect_res.json().get("reflection", "No reflection found.")
                        st.session_state.reflections[eid] = reflection
                    else:
                        st.error("❌ Failed to generate reflection.")
                        reflection = None

                # 💬 Show reflection
                if reflection:
                    st.markdown("### 🧠 LLM Reflection")
                    st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); padding: 1rem;
                                    border-radius: 10px; border: 1px solid rgba(255,255,255,0.2);
                                    color: #eee;">
                            {reflection}
                        </div>
                    """, unsafe_allow_html=True)

        else:
            st.error("⚠️ Failed to fetch entries.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")

    # 📝 Export reflections
    if st.session_state.reflections:
        if st.button("⬇ Export Reflections"):
            from datetime import datetime
            filename = f"reflections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for eid, reflection in st.session_state.reflections.items():
                    f.write(f"Entry ID: {eid}\nReflection:\n{reflection}\n\n")
            st.success(f"Reflections exported to `{filename}` ✅")

    st.markdown("</div>", unsafe_allow_html=True)