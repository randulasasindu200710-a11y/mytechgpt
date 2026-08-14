import streamlit as st
from litellm import completion
import os

# 1. Groq API Key එක ලබා ගැනීම
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# UI එක සකස් කිරීම
st.set_page_config(page_title="A/L Tech AI Guru", page_icon="🎓")
st.title("🎓 A/L Technology AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ප්‍රශ්න අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: SFT වල මාන (Dimensions), Ethernet switch, ගින්නක් යනු...")

# A/L Tech Syllabus එක නිවැරදිව හඳුනාගන්නා System Prompt එක
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (SFT, ET, BST, ICT) Master Teacher.

SUBJECT RECOGNITION RULES:
1. Identify the subject accurately:
   - SFT (Science for Technology): Units & Dimensions (ඒකක හා මාන), Physics, Chemistry, Basic Maths.
   - ICT: Networking, Hardware, Software, Programming, Databases.
   - ET: Engineering concepts, Civil, Mechanical, Electrical, Workshop Safety.
   - BST: Agro Technology, Food Tech, Bio-systems.

2. NEVER confuse SFT concepts with ICT! (e.g. "මාන" / "ඒකක" belongs to SFT, NOT ICT).
3. Handle spelling variations intelligently (e.g., if user writes "එකින් අනුවක්" or "ඒකක හා මාන", recognize it as SFT Units/Dimensions).

RESPONSE RULES:
- Write in clear, grammatically correct, natural Sinhala (සිංහල).
- Provide a clear, detailed A/L exam-standard answer (around 150-250 words).
- Use bullet points where appropriate, but DO NOT force artificial categories.
- ABSOLUTELY NO REPETITION or infinite loops of the same sentence.

IF NOT A/L TECH:
Say only: "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("A/L විෂය නිර්දේශයට අනුව පරීක්ෂා කර පිළිතුර සකසයි..."):
            try:
                response = completion(
                    model="groq/llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.3,
                    frequency_penalty=0.5,
                    presence_penalty=0.3,
                    max_tokens=1500
                )
                
                answer = response.choices[0].message.content
                st.success("විස්තරාත්මක පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
