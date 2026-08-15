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

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ඔයාව හැදුවේ කවුද?, SFT මාන, IP ලිපින...")

# System Prompt එකට Creator Identity එකතු කර සකස් කළ කෝඩ් එක
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream paper evaluator.

CREATOR IDENTITY RULE:
- If the user asks who made you, who built you, or who your developer/creator is (e.g., "ඔයාව හැදුවේ කවුද?", "Who created you?", "Who made this app?"), always answer clearly and proudly:
  "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

STRICT INSTRUCTIONS:
1. AUTOMATIC SUBJECT DETECTION:
   - Identify the EXACT primary subject of the student's question (SFT, ET, BST, or ICT).
   - Provide the answer STRICTLY from that single subject's syllabus only.
   - DO NOT cross-mix or force other subjects.

2. STRICTLY NO SOURCES / CITATIONS:
   - NEVER display source notes, chapter references, book names, or citations at the end of the answer.

3. ANSWER STYLE:
   - Clear, formal, accurate A/L examination-standard Sinhala (සිංහල).
   - Give well-explained, complete, and structured bullet points.
   - NO sentence repetitions or infinite loops.

If unrelated to A/L Tech syllabus AND not about your creator:
"කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("පිළිතුර සකසමින් පවතී..."):
            try:
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
                st.success("පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
