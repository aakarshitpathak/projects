import streamlit as st
import pyttsx3
import tempfile
import os

st.title("⚙️ Conversion in Progress")

if "uploaded_file" not in st.session_state:
    st.warning("⚠️ No file uploaded. Please go to Main Page first.")
else:
    file = st.session_state["uploaded_file"]

    progress_text = st.empty()
    progress_bar = st.progress(0)

    # Step 1: Extract text (already stored in session or re-extract)
    progress_text.text("📖 Extracting text...")
    text = st.session_state.get("extracted_text", "")
    progress_bar.progress(40)

    # Step 2: Convert to audio with pyttsx3
    progress_text.text("🎤 Converting to speech (offline)...")
    engine = pyttsx3.init()
    
    # Create temp file (use .wav for better compatibility)
    output_path = os.path.join(tempfile.gettempdir(), "audiobook.wav")
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    progress_bar.progress(90)

    # Step 3: Save & Download
    progress_text.text("💾 Saving file...")
    progress_bar.progress(100)

    st.success("✅ Conversion complete!")
    st.audio(output_path)
    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download Audiobook", f, file_name="audiobook.wav")
       