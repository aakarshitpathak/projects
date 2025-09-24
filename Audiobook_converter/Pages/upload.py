import os, io, time, pathlib
import streamlit as st
from gtts import gTTS
import PyPDF2

# Page settings
st.set_page_config(page_title="Audiobook Generator", page_icon="📖", layout="centered") 
st.title("Audiobook Generator 🎧")

# Sidebar
st.sidebar.title("⚙ Settings")
voice_lang = st.sidebar.selectbox("Select Language", ["en", "hi", "fr", "de", "es"])
speed = st.sidebar.radio("Speech Speed", ["Normal", "Slow"])

# Upload Section
st.header("Upload your eBook/Text File")
uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])

text = ""  # placeholder

if uploaded_file is not None:
    if uploaded_file.name.endswith(".txt"):
        # Handle text files
        content = uploaded_file.read()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

    elif uploaded_file.name.endswith(".pdf"):
        # Handle PDF files
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Avoid None

    if text.strip():  # Only proceed if text is extracted
        st.subheader("Preview of Uploaded Text 📑")
        st.text_area("Text Content", text[:1000] + "..." if len(text) > 1000 else text, height=200)

        if st.button("Generate Audiobook 🎧"):
            tts = gTTS(text=text, lang=voice_lang, slow=True if speed == "Slow" else False)
            output_path = "audiobook.mp3"
            tts.save(output_path)

            st.success("✅ Audiobook generated successfully!")
            audio_file = open(output_path, "rb")
            st.audio(audio_file.read(), format="audio/mp3")
            st.download_button("⬇ Download Audiobook", data=open(output_path, "rb"), file_name="audiobook.mp3")
            st.subheader("Thank you for using our service")
    else:
        st.error("⚠ No readable text found in this file. Please try another file.")

else:
    st.info("Please upload a .txt or .pdf file to start.")
    st.subheader("Thank you for using our service")
