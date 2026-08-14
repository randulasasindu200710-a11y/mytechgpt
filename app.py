import streamlit as st
from litellm import completion
from duckduckgo_search import DDGS
import os

# 1. Groq API Key එක ලබා ගැනීම
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# UI එක සකස් කිරීම
st.set_page_config(page_title="A/L Tech AI Guru", page_icon="🎓")
st.title("🎓 A/L Technology AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ප්‍රශ්න අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ගින්නක් යනු කුමක්ද? එහි ත්‍රිකෝණය පැහැදිලි කරන්න.")

# A/L Tech Syllabus එකට විතරක් සීමා කළ strict System Prompt එක
system_prompt = """
You are a highly qualified Sri Lankan A/L Technology Stream teacher. 
Your target audience is Sri Lankan G.C.E. A/L Technology stream students (ET, SFT, BST, ICT).

STRICT RULES FOR YOUR ANSWER:
1. Write in natural, accurate, grammatically correct Sinhala (සිංහල) using correct Sri Lankan A/L Tech terminology.
2. NEVER repeat sentences, paragraphs, or bullet points.
3. Be direct, clear, and structured (use bullet points where necessary).
4. ONLY answer topics related to Sri Lankan A/L Technology stream (ET, SFT, BST, ICT).
5. If the question is NOT related to A/L Tech stream, reply ONLY with:
   "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

def search_web(query):
    try:
        results = DDGS().text(f"{query} Sri Lanka AL Technology", max_results=2)
        if not results:
            return ""
        return "\n".join([f"- {r['body']}" for r in results])
    except Exception:
        return ""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("Syllabus එකට අනුව පරීක්ෂා කර පිළිතුර සකසයි..."):
            try:
                # අන්තර්ජාලයෙන් අවශ්‍ය තොරතුරු සෙවීම
                web_info = search_web(user_input)
                
                full_prompt = f"Student Question: {user_input}"
                if web_info:
                    full_prompt += f"\n\nSearch Context (Use if helpful):\n{web_info}"

                # LLaMA 3.3 Call with strictly controlled temperature
                response = completion(
                    model="groq/llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.3 # මේකෙන් AI එක විකාර ලියන එක සහ repeat වෙන එක සම්පූර්ණයෙන්ම නවතිනවා
                )
                
                answer = response.choices[0].message.content
                st.success("පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
