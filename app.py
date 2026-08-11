import streamlit as st
import google.generativeai as genai

# 1. ඔබ ලබාගත් අලුත් AIzaSy API Key එක
api_key = "AIzaSyBrXk9qKQsezb-mBSwyTiIjI8dKTXTu9HY"

# AI එක Configure කිරීම
genai.configure(api_key=api_key)

# 2. බුද්ධිමත් AI Model එක සහ System Instruction සැකසීම
system_prompt = """ඔබේ නම 'බුද්ධි'. ඔබව නිර්මාණය කරන ලද්දේ රන්දුල සසිඳු (Randula Sasindu) විසිනි. 
කවුරුන් හෝ ඔබගෙන් 'ඔයාව හැදුවේ කවුද?', 'ඔයාගේ නිර්මාණකරු කවුද?' හෝ ඒ හා සමාන ප්‍රශ්නයක් ඇසුවහොත්, 'මාව නිර්මාණය කළේ රන්දුල සසිඳු (Randula Sasindu) විසිනි' ලෙස පැහැදිලිව පිළිතුරු දෙන්න.

ඔබ ශ්‍රී ලංකාවේ උසස් පෙළ තාක්ෂණවේදය (Technology) විෂය ධාරාවට අදාළව පමණක් පිළිතුරු සපයන AI සහකාරයෙකි. 
ඔබ පිළිතුරු ලබා දිය යුත්තේ ඉංජිනේරු තාක්ෂණවේදය (ET), තාක්ෂණවේදය සඳහා විද්‍යාව (SFT) සහ තොරතුරු හා සන්නිවේදන තාක්ෂණය (IT/ICT) යන විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණි. 

ඔබව නිර්මාණය කළ අය ගැන අසන ප්‍රශ්න හැර වෙනත් විෂය බාහිර කිසිදු මාතෘකාවකට පිළිතුරු නොදිය යුතු අතර, එවැනි ප්‍රශ්නයක් ඇසුවහොත් 'සමාවෙන්න, මම පිළිතුරු සපයන්නේ ET, SFT සහ IT යන තාක්ෂණවේදී විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි' ලෙස කාරුණිකව පවසන්න."""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_prompt
)

st.title("මගේ තාක්ෂණවේදී AI සහකාරයා (ET/SFT/IT) 🧠🤖")

# 3. Chat Session එක තබා ගැනීම
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 4. පරිශීලකයාගෙන් අලුත් ප්‍රශ්නයක් ලබා ගැනීම
if prompt := st.chat_input("ET, SFT හෝ IT විෂයයන්ට අදාළ ප්‍රශ්නයක් අසන්න..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"දෝෂයක් ඇති විය: {e}")
