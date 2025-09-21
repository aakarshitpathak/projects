import streamlit as st

st.title("Audiobook Converter")

if st.button("Go to Dashboard"):
    st.switch_page("Pages/audiobook_dashboard.py")

if st.button("⚙️ Conversion Progress"):
    st.switch_page("Pages/conversion_progress.py")
