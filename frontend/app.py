import streamlit as st

from modules.upload_journal import show_upload_journal
from modules.add_entry import show_add_entry
from modules.view_entries import show_view_entries
from modules.ask_question import show_ask_question
from modules.reflect import show_reflect
from modules.insights import show_insights
from modules.filter_by_tag import show_filter_by_tag
from modules.entries_by_date import show_entries_by_date
from modules.reset import reset_page

st.set_page_config(page_title="Your Own Personal Therapist AI", layout="wide")
st.title("🧠 Your Own Personal Therapist AI")

page = st.sidebar.selectbox("Navigate", [
    "Upload Journal",
    "Add Entry",
    "View Entries",
    "Ask a Question",
    "Reflect",
    "Insights",
    "Filter by Tag",
    "Entries by Date",
    "Reset All Data"
])

if page == "Upload Journal":
    show_upload_journal()
elif page == "Add Entry":
    show_add_entry()
elif page == "View Entries":
    show_view_entries()
elif page == "Ask a Question":
    show_ask_question()
elif page == "Reflect":
    show_reflect()
elif page == "Insights":
    show_insights()
elif page == "Filter by Tag":
    show_filter_by_tag()
elif page == "Entries by Date":
    show_entries_by_date()
elif page == "Reset All Data":
    reset_page()
