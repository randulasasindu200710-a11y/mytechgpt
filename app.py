import streamlit as st
import requests

# 1. ඔබගේ Google API Key එක
api_key = "AQ.Ab8RN6IGGxhI30kFymQFFo3GPO3U4LvVkmuzlndrJTpDQU_nmQ"

# 2. System Instruction සැකසීම
system_prompt = """ඔබේ නම 'බුද්ධි'. ඔබව නිර්මාණය කරන ලද්දේ රන්දුල සසිඳු (Randula Sasindu) විසිනි. 
කවුරුන් හෝ ඔබගෙන් 'ඔයාව හැදුවේ කවුද?', 'ඔයාගේ නිර්මාණකරු කවුද?' හෝ ඒ හා සමාන ප්‍රශ්නයක් ඇසුවහොත්, 'මාව නිර්මාණය කළේ රන්දුල සසිඳු (Randula Sasindu) විසිනි' ලෙස පැහැදිලිව පිළිතුරු දෙන්න.

ඔබ ශ්‍රී ලංකාවේ උසස් පෙළ තාක්ෂණවේදය (Technology) විෂය ධාරාවට අදාළව පමණක් පිළිතුරු සපයන AI සහකාරයෙකි. 
ඔබ පිළිතුරු ලබා දිය යුත්තේ ඉංජිනේරු තාක්ෂණවේදය (ET), තාක්ෂණවේදය සඳහා විද්‍යාව (SFT) සහ තොරතුරු හා සන්නිවේදන තාක්ෂණය (IT/ICT) යන විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණි. 

ඔබව නිර්මාණය කළ අය ගැන අසන ප්‍රශ්න හැර වෙනත් විෂය බාහිර කිසිදු මාතෘකාවකට පිළිතුරු නොදිය යුතු අතර, එවැනි ප්‍රශ්නයක් ඇසුවහොත් 'සමාවෙන්න, මම පිළිතුරු සපයන්නේ ET, SFT සහ IT යන තාක්ෂණවේදී විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි' ලෙස කාරුණිකව පවසන්න."""

st.title("මගේ තාක්ෂණවේදී AI සහකාරයා (ET/SFT/IT) 🧠🤖")

# 3. පරිශීලකයාගෙන් අලුත් ප්‍රශ්නයක් ලබා ගැනීම
if prompt := st.chat_input("ET, SFT හෝ IT විෂයයන්ට අදාළ ප්‍රශ්නයක් අසන්න..."):
    # පරිශීලකයාගේ ප්‍රශ්නය පෙන්වීම
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI එකෙන් පිළිතුර ලබා ගැනීම (gemini-3.6-flash Model එක භාවිත කර ඇත)
    with st.chat_message("assistant"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ]
            }
            
            # API Request එක යැවීම
            response = requests.post(url, headers=headers, json=payload)
            res_data = response.json()
            
            if response.status_code == 200:
                bot_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                st.markdown(bot_reply)
            else:
                error_msg = res_data.get("error", {}).get("message", "Unknown error")
                st.error(f"දෝෂයක් ඇති විය: {error_msg}")
                
        except Exception as e:
            st.error(f"දෝෂයක් ඇති විය: {e}")
