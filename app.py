import streamlit as st
from litellm import completion
import os

# 1. Browser Tab එකේ පමණක් Logo එක පෙන්වීමට page_icon="logo.png" ලබා දී ඇත
st.set_page_config(page_title="A/L Tech AI Guru", page_icon="logo.png")

# API Keys පරීක්ෂාව (OpenRouter හෝ Groq)
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
elif "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.title("🎓TECH-gpt")
st.write("උසස් පෙළ තාක්ෂණවේදය විෂයයන්ට අදාළ ප්‍රශ්න අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ද්විතීයික පරිවෘත්තජ, SFT මාන, IP ලිපින...")

# System Prompt
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If the user asks who made/created/developed you (e.g., "ඔයාව හැදුවේ කවුද?"), reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

CORE INSTRUCTIONS:
1. FLEXIBLE TECH SUBJECT COVERAGE:
   - Accept ALL Sri Lankan A/L Tech stream terms (ET, SFT, BST, ICT).
   - Technical terms like "ද්විතීයික පරිවෘත්තජ" (Secondary Metabolites), electrical safety classes, physics, chemistry, mechanics, agricultural tech, and IT ARE 100% VALID A/L TECH TOPICS.
   - Do NOT be overly strict or defensive. Assume any engineering, scientific, or tech phrase belongs to the A/L Tech syllabus.

2. ANSWER STYLE:
   - Identify which subject (ET, SFT, BST, or ICT) the topic belongs to, and explain it strictly according to that syllabus.
   - Write in clear, accurate, examination-standard Sinhala (සිංහල).
   - Provide direct, structured bullet points with clear explanations.
   - NO sentence repetitions or infinite loops.
   - NEVER show source notes, chapter numbers, citations, or book references at the end.

3. REFUSAL RULE (ONLY FOR COMPLETELY UNRELATED NON-ACADEMIC TOPICS):
   - Refuse ONLY if the prompt is CLEARLY about everyday non-academic topics (e.g., cooking recipes, movies, songs, gossip, video games, love advice).
   - If refusing, reply ONLY:
     "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

if st.button("Enter"):
    if user_input:
        with st.spinner("loading..."):
            try:
                model_name = "openrouter/deepseek/deepseek-chat" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.3-70b-versatile"
                
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.3
                )
                
                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
