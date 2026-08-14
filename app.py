import streamlit as st
from litellm import completion
import os

# 1. API Key එක ලබා ගැනීම (OpenRouter හෝ Groq)
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
elif "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="A/L Tech AI Guru", page_icon="🎓")
st.title("🎓 A/L Technology AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ප්‍රශ්න අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: එතීන් අණුවක් යනු, SFT මාන, IP ලිපින...")

# A/L NIE Syllabus එකට අනුව හරියටම සකස් කළ System Prompt එක
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream paper evaluator.

STRICT INSTRUCTIONS:
1. AUTOMATIC SUBJECT DETECTION:
   - Identify the EXACT primary subject of the student's question (SFT, ET, BST, or ICT).
   - Provide the answer STRICTLY from that single subject's syllabus only.
   - DO NOT cross-mix or force other subjects (e.g. If the question is SFT Chemistry like 'Ethene', answer ONLY according to SFT chemistry. DO NOT add sections like "ET/ICT සම්බන්ධ අංශ" or "BST සම්බන්ධ අංශ").

2. STRICTLY NO SOURCES / CITATIONS:
   - NEVER display source notes, chapter references, book names, or citations at the end of the answer.
   - DO NOT write things like "(පරිච්ඡේදය: SFT ඒකක 4.2...)" or "සටහන: NIE සම්පත් පොත..." anywhere in the output.

3. ANSWER STYLE:
   - Clear, formal, accurate A/L examination-standard Sinhala (සිංහල).
   - Give well-explained, complete, and structured bullet points.
   - NO sentence repetitions or infinite loops.

If unrelated to A/L Tech syllabus:
"කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("A/L විෂය නිර්දේශයට අනුව පිළිතුර සකසමින් පවතී..."):
            try:
                # OpenRouter හෝ Groq හරහා Call කිරීම
                model_name = "openrouter/deepseek/deepseek-chat" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.3-70b-versatile"
                
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.2
                )
                
                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
