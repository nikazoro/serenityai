import streamlit as st
import requests
from datetime import datetime
import os
import json

API_BASE = "http://127.0.0.1:8000"
qa_file = "data/qa_history.json"


def show_ask_question():
    # 🧠 Session state init
    if "qa_history" not in st.session_state:
        if os.path.exists(qa_file):
            with open(qa_file, "r", encoding="utf-8") as f:
                st.session_state.qa_history = json.load(f)
        else:
            st.session_state.qa_history = []

    if "latest_qa" not in st.session_state:
        st.session_state.latest_qa = None

    if "qa_submitted" not in st.session_state:
        st.session_state.qa_submitted = False


    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("💬 Ask About Your Journal")

    question_input = st.text_input("What would you like to know?", key="qa_input")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Ask"):
            if question_input.strip():
                try:
                    res = requests.post(f"{API_BASE}/ask/", json={"question": question_input})
                    if res.status_code == 200:
                        answer = res.json().get("answer", "")

                        latest = {
                            "question": question_input,
                            "answer": answer
                        }

                        st.session_state.qa_history.insert(0, latest)
                        with open(qa_file, "w", encoding="utf-8") as f:
                            json.dump(st.session_state.qa_history, f, indent=2, ensure_ascii=False)

                        st.session_state.latest_qa = latest
                        st.session_state.qa_submitted = True

                        if "qa_input" in st.session_state:
                            del st.session_state["qa_input"]

                        st.rerun()
                    else:
                        st.error("❌ Question failed.")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
            else:
                st.warning("Please enter a question.")

    with col2:
        if st.button("🗑 Clear All"):
            st.session_state.qa_history = []
            st.session_state.latest_qa = None
            st.session_state.qa_submitted = False
            if "qa_input" in st.session_state:
                del st.session_state["qa_input"]
            if os.path.exists(qa_file):
                os.remove(qa_file)
            st.success("History cleared.")
            st.rerun()

    # 🔍 Show latest answer inline
    if st.session_state.latest_qa:
        q = st.session_state.latest_qa["question"]
        a = st.session_state.latest_qa["answer"]
        st.markdown(f"""
            <div style="border: 1px solid rgba(255,255,255,0.3); padding: 1rem; border-radius: 10px;
                        background: rgba(255,255,255,0.08); margin-top: 1rem; margin-bottom: 1.5rem;">
                <div style="font-weight: bold; color: #00BFFF;">❓ {q}</div>
                <div style="color: #eee; margin-top: 0.5rem;">💡 {a}</div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.latest_qa = None
        st.session_state.qa_submitted = False

    # 📜 Previous Q&A history
    if st.session_state.qa_history:
        st.subheader("🧾 Previous Answers")
        for item in st.session_state.qa_history:
            st.markdown(f"""
                <div style="border: 1px solid rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;
                            background: rgba(255,255,255,0.04); margin-bottom: 1rem;">
                    <div style="color: #aaa;">❓ {item['question']}</div>
                    <div style="color: #888; margin-top: 0.5rem;">💡 {item['answer']}</div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("⬇ Export Q&A"):
        export_name = f"qa_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        full_log = "\n\n".join([f"❓ {q['question']}\n💡 {q['answer']}" for q in st.session_state.qa_history])
        with open(export_name, "w", encoding="utf-8") as f:
            f.write(full_log)
        st.success(f"Exported to {export_name} ✅")

    st.markdown("</div>", unsafe_allow_html=True)
