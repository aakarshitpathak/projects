import streamlit as st
import streamlit as st

import os

# Page config
st.set_page_config(page_title="📖 Audiobook Generator", page_icon="🎧", layout="wide")

# Title
st.title("📖 Audiobook Generator from eBooks")
st.markdown("### Convert your eBooks or text into natural speech using AI-powered Text-to-Speech.")

# Banner / Image
st.image("assets/images.png",use_container_width=True)

# Sidebar
st.sidebar.title("⚙ Settings")
voice_lang = st.sidebar.selectbox("Select Language", ["en",'hi','fr','de','es'])
speed = st.sidebar.radio("Speech Speed", ["Normal", "Slow"])

st.title("🎙 Introduction: The Rise of AI-Generated Audiobooks")
st.markdown("""In a world where multitasking is the norm and screen fatigue is real, audiobooks have emerged as a powerful alternative to traditional reading. But producing them used to be expensive, time-consuming, and limited to major publishers. Enter AI-powered audiobook generation—a revolutionary approach that transforms any eBook into a professionally narrated audio experience in minutes. Whether you're an indie author, a student, or a lifelong learner, this technology opens up new ways to consume and share stories, knowledge, and ideas.""")

st.title("🧠 Technology Behind Audiobook Generation")
st.subheader("1.Text-to-Speech (TTS) Engines")
st.markdown("""Converts written text into spoken audio.

Uses deep learning to replicate human-like voices.

Examples: Google WaveNet, Amazon Polly, Microsoft Azure TTS.""")

st.subheader("2. Natural Language Processing (NLP)")
st.markdown("""Understands sentence structure, punctuation, and context.

Ensures smooth, expressive narration with proper emphasis.""")

st.subheader("3. Voice Cloning & Synthetic Voices")
st.markdown("""AI can mimic real voices or generate new ones.

Enables personalized narration and multilingual support.""")

st.subheader("4. Generative AI & Machine Learning")
st.markdown("""Trains on massive datasets of human speech.

Adapts tone and style based on genre or audience.""")

st.title("✅ Advantages of AI-Generated Audiobooks")

st.subheader("⚡ Speed")
st.markdown("""Converts entire books in hours, not weeks.""")
st.subheader("💸 Cost-Effective")	
st.markdown("""No need for studios, actors, or editors.""")
st.subheader("🌐 Multilingual ")
st.markdown("""Reach	Narration in dozens of languages and accents.""")
st.subheader("🧠 Customization")
st.markdown(""""Choose voice style, emotion, and pacing.""")
st.subheader("📈 Scalability")	
st.markdown("""Convert entire libraries or niche titles easily.""")

st.title("🎯 Key Uses of Audiobook Generation from eBooks")
st.subheader("1. Accessibility for All")
st.markdown("""Helps visually impaired or dyslexic readers enjoy literature effortlessly.

Supports inclusive education by providing audio formats for students with learning differences.""")

st.subheader("2. Multitasking-Friendly Consumption")
st.markdown("""Lets people “read” while commuting, exercising, or doing chores.

Perfect for busy lifestyles where screen time is limited.""")

st.subheader("3. Global Reach & Language Expansion")
st.markdown("""AI tools can generate audiobooks in multiple languages and accents.

Authors can tap into international markets without hiring multilingual narrators.""")

st.subheader("4. Cost-Effective Publishing")
st.markdown("""AI narration is significantly cheaper than hiring voice actors and studio time.

Ideal for self-published authors or indie publishers with limited budgets.""")

st.subheader("5. Enhanced Storytelling")
st.markdown("""Emotion tags, character voice attribution, and multi-voice narration add drama and immersion.

Revitalizes older eBooks with fresh audio experiences.""")

st.subheader("6. Revenue Diversification")
st.markdown("""Audiobooks offer an additional income stream alongside print and digital formats.

Can be sold on platforms like Audible, Google Play Books, and Apple Books.""")

st.subheader("7. Marketing & Branding")
st.markdown("""Authors can use audiobooks to build their brand and credibility.

Audio snippets can be used for promotional teasers on social media.""")