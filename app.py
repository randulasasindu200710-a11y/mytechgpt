import streamlit as st
from litellm import completion
import os

# 1. Streamlit Secrets හරහා OpenRouter API Key එක ලබා ගැනීම
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]

# UI එක සකස් කිරීම
st.set_page_config(page_title="A/L Tech AI Guru", page_icon="🎓")
st.title("🎓 A/L Technology AI Guru (DeepSeek V3) 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ප්‍රශ්න අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: SFT මාන, කෘතිම රබර් වර්ග, IP ලිපින...")

# A/L NIE Syllabus එකට 100% ක් අනුකූල කළ System Prompt එක
system_prompt = """
You are a master teacher for Sri Lankan G.C.E. Advanced Level (A/L) Technology stream (SFT, ET, BST, ICT).
Your core duty is to evaluate and explain concepts strictly based on the official NIE Sri Lanka Teacher Resource Books (සම්පත් පොත).

CRITICAL SYLLABUS GUIDELINES:
1. SUBJECT IDENTIFICATION:
   - SFT (Science for Technology): Units & Dimensions, Physics, Chemistry, Polymers (SBR, Neoprene, Nitrile, Vulcanization).
   - ICT: IP Addressing, Hardware, Software, Networking, Databases.
   - ET: Engineering concepts, Safety, Materials, Tools.
   - BST: Agriculture, Soil science, Bio-systems, Food Tech.

2. ANSWER STRUCTURE & QUALITY:
   - Always respond in natural, grammatically correct, and formal Sinhala (සිංහල).
   - Provide direct, exam-standard points with relevant technical Sinhala terms.
   - DO NOT continuously repeat sentences or loop text.
   - Keep answers detailed enough for A/L exam essay/structured questions.

3. OUT OF SYLLABUS RESTRICTION:
   If the query is unrelated to Sri Lankan A/L Tech Stream, reply ONLY:
   "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("A/L සම්පත් පොතට අනුව පිළිතුර සකසමින් පවතී..."):
            try:
                # OpenRouter හරහා DeepSeek V3 Model එක Call කිරීම
                response = completion(
                    model="openrouter/deepseek/deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.3
                )
                
                answer = response.choices[0].message.content
                st.success("A/L විෂය නිර්දේශයට අදාළ පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
