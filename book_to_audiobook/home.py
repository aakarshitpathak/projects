import streamlit as st
import os, time
from pathlib import Path
import PyPDF2
import pyttsx3

# ---------------- Directories ----------------
APP_DIR = Path(__file__).parent          # base dir (book_to_audiobook)
EBOOK_DIR = APP_DIR / "sample_books"     # input ebooks
OUTPUT_DIR = APP_DIR / "outputs"         # output audio
EBOOK_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------- Utils ----------------
def list_ebooks():
    supported_exts = {".txt", ".pdf"}
    return [p for p in sorted(EBOOK_DIR.iterdir()) if p.is_file() and p.suffix.lower() in supported_exts]

# ---------------- UI ----------------
st.set_page_config(page_title="Audiobook Generator", page_icon="🎧", layout="centered")
st.title("Audiobook Generator 🎧")

# Debug info (to check path & files)
st.write("📂 Looking inside:", EBOOK_DIR.resolve())
st.write("📄 Files in folder:", [f.name for f in EBOOK_DIR.iterdir()])

files = list_ebooks()

if not files:
    st.info("Place .txt or .pdf files in this folder and refresh.")
else:
    file_labels = [f.name for f in files]
    selected_idx = st.selectbox("Select an ebook", range(len(files)), format_func=lambda i: file_labels[i])
    selected_file = files[selected_idx]
    st.success(f"✅ Selected file: {selected_file.name}")
