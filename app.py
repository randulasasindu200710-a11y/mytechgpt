import streamlit as st
import google.generativeai as genai
import os

# ========== 1. API KEY ==========
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ GOOGLE_API_KEY හමුවුණේ නැහැ. Streamlit Secrets හෝ Environment Variables පරීක්ෂා කරන්න.")
        st.stop()

genai.configure(api_key=api_key)

# ========== 2. System Instruction ==========
system_prompt = """ඔබේ නම 'බුද්ධි'. ඔබව නිර්මාණය කරන ලද්දේ රන්දුල සසිඳු (Randula Sasindu) විසිනි. 
කවුරුන් හෝ ඔබගෙන් 'ඔයාව හැදුවේ කවුද?', 'ඔයාගේ නිර්මාණකරු කවුද?' හෝ ඒ හා සමාන ප්‍රශ්නයක් ඇසුවහොත්, 'මාව නිර්මාණය කළේ රන්දුල සසිඳු (Randula Sasindu) විසිනි' ලෙස පැහැදිලිව පිළිතුරු දෙන්න.

ඔබ ශ්‍රී ලංකාවේ උසස් පෙළ තාක්ෂණවේදය (Technology) විෂය ධාරාවට අදාළව පමණක් පිළිතුරු සපයන AI සහකාරයෙකි. 
ඔබ පිළිතුරු ලබා දිය යුත්තේ ඉංජිනේරු තාක්ෂණවේදය (ET), තාක්ෂණවේදය සඳහා විද්‍යාව (SFT) සහ තොරතුරු හා සන්නිවේදන තාක්ෂණය (IT/ICT) යන විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණි. 

ඔබව නිර්මාණය කළ අය ගැන අසන ප්‍රශ්න හැර වෙනත් විෂය බාහිර කිසිදු මාතෘකාවකට පිළිතුරු නොදිය යුතු අතර, එවැනි ප්‍රශ්නයක් ඇසුවහොත් 'සමාවෙන්න, මම පිළිතුරු සපයන්නේ ET, SFT සහ IT යන තාක්ෂණවේදී විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි' ලෙස කාරුණිකව පවසන්න."""

# ========== 3. Model එක Try කිරීම (Fallback සහිත) ==========
MODEL_NAMES = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001", 
    "gemini-1.5-pro",
    "gemini-pro"
]

model = None
last_error = None

for model_name in MODEL_NAMES:
    try:
        test_model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        # Test කිරීමක්
        test_model.generate_content("hello")
        model = test_model
        st.sidebar.success(f"✅ Model: `{model_name}`")
        break
    except Exception as e:
        last_error = e
        continue

if model is None:
    st.error("❌ කිසිදු Model එකක් initialize කිරීමට නොහැකි විය.")
    st.error(f"Last error: {last_error}")
    st.info("""
    **විසඳුම්:**
    1. `requirements.txt` එකේ `google-generativeai>=0.8.0` දාලා තියෙනවාද?
    2. Streamlit Cloud එකේ **Manage app → Reboot** කරන්න
    3. API Key එක වලංගුද? [Google AI Studio](https://aistudio.google.com/app/apikey) එකෙන් පරීක්ෂා කරන්න
    """)
    st.stop()

# ========== 4. UI ==========
st.title("මගේ තාක්ෂණවේදී AI සහකාරයා (ET/SFT/IT) 🧠🤖")

# Chat session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []

# පැරණි messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# නව ප්‍රශ්නයක්
if prompt := st.chat_input("ET, SFT හෝ IT විෂයයන්ට අදාළ ප්‍රශ්නයක් අසන්න..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("පිළිතුරු සකස් කරමින්..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                answer = response.text
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"❌ දෝෂයක් ඇති විය: {e}")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("💬 Chat History මකන්න"):
        st.session_state.clear()
        st.rerun()
    st.markdown("**Created by:** Randula Sasindu")
    st.markdown("**Subjects:** ET | SFT | IT/ICT")
