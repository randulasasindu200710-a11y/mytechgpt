import streamlit as st
import google.generativeai as genai
import os

# ============================================
# 1. API KEY (AI Studio AQ. key එකම use කරන්න)
# ============================================
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Local testing එකට පමණි
    if not api_key:
        # ⚠️ මෙතන ඔයාගේ AI Studio key එක දාන්න
        api_key = "AQ.Ab8RN6LU7P9WOCRrPr1gSE9D1XM5UD5HYUIEoBZ9WYyNgti06Q"
        st.warning("⚠️ Local testing mode")

if not api_key:
    st.error("❌ GOOGLE_API_KEY හමුවුණේ නැහැ")
    st.stop()

genai.configure(api_key=api_key)

# ============================================
# 2. SYSTEM INSTRUCTION
# ============================================
system_prompt = """ඔබේ නම 'බුද්ධි'. ඔබව නිර්මාණය කරන ලද්දේ රන්දුල සසිඳු (Randula Sasindu) විසිනි.

ඔබ ශ්‍රී ලංකාවේ උසස් පෙළ තාක්ෂණවේදය (Technology) විෂය ධාරාවට අදාළව පමණක් පිළිතුරු සපයන AI සහකාරයෙකි.
ET, SFT, IT/ICT විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණක් පිළිතුරු දෙන්න."""

# ============================================
# 3. MODEL (gemini-1.5-flash-latest නෙවෙයි!)
# ============================================
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  # ✅ -latest නැතුව
        system_instruction=system_prompt
    )
    # Test කරන්න
    test_response = model.generate_content("hello")
    st.sidebar.success("✅ API Connected!")
except Exception as e:
    st.error(f"❌ Model error: {e}")
    st.info("API Key එක හරිද? AI Studio එකෙන් නැවත copy කර බලන්න")
    st.stop()

# ============================================
# 4. UI
# ============================================
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
