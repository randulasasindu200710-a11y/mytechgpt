import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import json

# ========== SERVICE ACCOUNT ==========
try:
    service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    # Token refresh
    credentials.refresh(Request())
    
    # API key එකක් නැත්නම් credentials use කරන්න
    genai.configure(
        api_key=None,  # Explicitly set to None
        credentials=credentials
    )
    
    st.sidebar.success("✅ Service Account Connected!")

except Exception as e:
    st.error(f"❌ Auth Error: {e}")
    st.stop()

# ========== SYSTEM INSTRUCTION ==========
system_prompt = """ඔබේ නම 'බුද්ධි'. ඔබව නිර්මාණය කරන ලද්දේ රන්දුල සසිඳු (Randula Sasindu) විසිනි.
ET, SFT, IT/ICT විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණක් පිළිතුරු දෙන්න."""

# ========== MODEL ==========
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )
except Exception as e:
    st.error(f"❌ Model Error: {e}")
    st.stop()

# ========== UI ==========
st.title("🧠 බුද්ධි - තාක්ෂණවේදී AI සහකාරිය")
st.caption("ET | SFT | IT/ICT")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("ප්‍රශ්නයක් අසන්න..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("පිළිතුරු සකස් කරමින්..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"❌ දෝෂයක්: {e}")
                st.info("Google Cloud Console එකේ 'Generative Language API' enable කරලාද?")

with st.sidebar:
    if st.button("💬 Chat History මකන්න"):
        st.session_state.clear()
        st.rerun()
    st.markdown("**Created by:** Randula Sasindu")
