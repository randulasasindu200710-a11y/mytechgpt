import streamlit as st
import google.generativeai as genai

# 1. ඔබගේ Google API Key එක
api_key = "AQ.Ab8RN6LXebVOJSJay6CVWfz7C9_7OBJaJ6Oy0wrtWpIKtY-NdQ"

# AI එක Configure කිරීම
genai.configure(api_key=api_key)

# 2. බුද්ධිමත් AI Model එක සහ නව System Instruction සැකසීම
system_prompt = """ඔබේ නම 'බුද්ධි'. ඔබ ශ්‍රී ලංකාවේ උසස් පෙළ තාක්ෂණවේදය (Technology) විෂය ධාරාවට අදාළව පමණක් පිළිතුරු සපයන AI සහකාරයෙකි. 
ඔබ පිළිතුරු ලබා දිය යුත්තේ ඉංජිනේරු තාක්ෂණවේදය (ET), තාක්ෂණවේදය සඳහා විද්‍යාව (SFT) සහ තොරතුරු හා සන්නිවේදන තාක්ෂණය (IT/ICT) යන විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණි. 
වෙනත් කිසිදු මාතෘකාවකට හෝ ප්‍රශ්නයකට පිළිතුරු නොදිය යුතු අතර, එවැනි ප්‍රශ්නයක් ඇසුවහොත් 'සමාවෙන්න, මම පිළිතුරු සපයන්නේ ET, SFT සහ IT යන තාක්ෂණවේදී විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි' ලෙස කාරුණිකව පවසන්න."""

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=system_prompt
)

st.title("TECH-gpt 🤖")

# 3. Chat Session එක තබා ගැනීම (කලින් ඇසූ දේවල් AI එකට මතක තබා ගැනීමට)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# කලින් තිබූ "Chat History පෙන්වන Loop එක" මෙතැනින් ඉවත් කර ඇත.
# ඒ නිසා පරණ ප්‍රශ්න තිරයේ නොපෙනී යයි.

# 4. පරිශීලකයාගෙන් අලුත් ප්‍රශ්නයක් ලබා ගැනීම
if prompt := st.chat_input("ET, SFT හෝ IT විෂයයන්ට අදාළ ප්‍රශ්නයක් අසන්න..."):
    # අලුත් ප්‍රශ්නය පමණක් තිරයේ පෙන්වීම
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI එකෙන් පිළිතුර ලබා ගැනීම
    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            # අලුත් පිළිතුර පමණක් තිරයේ පෙන්වීම
            st.markdown(response.text)
        except Exception as e:
            st.error(f"දෝෂයක් ඇති විය: {e}")