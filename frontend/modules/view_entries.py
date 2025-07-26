import streamlit as st
import requests
from collections import defaultdict

API_BASE = "http://127.0.0.1:8000"  # 🔧 Change if hosted elsewhere

def show_view_entries():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("📘 Your Journal Entries")

    try:
        # ✅ Access your FastAPI backend running locally
        res = requests.get("http://127.0.0.1:8000/entries/")

        if res.status_code == 200:
            raw_entries = res.json()

            # 📅 Group by date if flat list
            if isinstance(raw_entries, list):
                entries_by_date = defaultdict(list)
                for entry in raw_entries:
                    entries_by_date[entry["date"]].append(entry)
            elif isinstance(raw_entries, dict):
                entries_by_date = raw_entries
            else:
                st.error("❌ Unknown format from backend.")
                st.stop()

            # 🎨 Mood → Color/Emoji
            mood_map = {
                "joy": ("#FFE066", "😊"),
                "anxious": ("#FF6B6B", "😰"),
                "reflective": ("#6C5CE7", "🧘"),
                "grateful": ("#55EFC4", "🙏"),
                "sad": ("#A29BFE", "😢"),
                "overwhelmed": ("#FAB1A0", "😵‍💫"),
            }

            # 🖼 Source type icons
            source_icons = {
                "text": "📝",
                "audio": "🎤",
                "image": "🖼"
            }

            # 🔁 Loop through entries by date
            for date, entries in sorted(entries_by_date.items(), reverse=True):
                st.markdown(f"<h4 style='color:#00BFFF;'>📅 {date}</h4>", unsafe_allow_html=True)

                for entry in entries:
                    mood = entry.get("mood_label", "").lower()
                    mood_color, mood_emoji = mood_map.get(mood, ("#D3D3D3", "💬"))

                    icon = source_icons.get(entry["source_type"], "📄")

                    st.markdown(f"""
                        <div style="
                            background: rgba(255,255,255,0.07);
                            backdrop-filter: blur(10px);
                            border-radius: 15px;
                            border: 1px solid rgba(255,255,255,0.15);
                            padding: 1.2rem;
                            margin-bottom: 1.2rem;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                        ">
                            <div style="font-size: 0.9rem; color: #ccc;">
                                🆔 ID: {entry['id']} | {icon} {entry['source_type'].capitalize()} | {mood_emoji} 
                                <span style='color:{mood_color}; font-weight:bold'>{entry['mood_label'].capitalize()}</span>
                            </div>
                            <div style="margin-top: 0.5rem; font-size: 1rem; color: #eee;">
                                {entry['text'][:500].replace('\n', '<br>')}{"..." if len(entry['text']) > 500 else ""}
                            </div>
                            <div style="margin-top: 0.6rem; font-size: 0.85rem; color: #bbb;">
                                <b>🏷 Tags:</b> {entry['tags']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("❌ Could not load entries from API.")

    except Exception as e:
        st.error(f"⚠️ Error while connecting: {e}")

    st.markdown("</div>", unsafe_allow_html=True)