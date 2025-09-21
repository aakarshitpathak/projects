import streamlit as st

st.set_page_config(page_title="📚 Audiobook Generator", layout="wide")
st.title("📚 eBook to Audiobook Converter")
st.write("Upload your **PDF** or **EPUB** file to generate an audiobook 🎧")

uploaded_file = st.file_uploader("Upload eBook", type=["pdf", "epub"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully")
    if st.button("Start Conversion"):
        st.session_state["uploaded_file"] = uploaded_file
        st.switch_page("Pages/conversion_progress.py")
