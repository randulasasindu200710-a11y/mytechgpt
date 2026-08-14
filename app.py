import streamlit as st
from litellm import completion
from duckduckgo_search import DDGS
import os

# 1. Groq API Key එක ලබා ගැනීම
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# UI එක සකස් කිරීම
st.set_page_config(page_title="A/L Tech AI Guru", page_icon="🎓")
st.title("TECH-gpt")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ප්‍රශ්න අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: IP ලිපිනයක් යනු කුමක්ද? නැතහොත් SFT මාන...")

# Repetition තහනම් කළ System Prompt එක
system_prompt = """
You are an expert Sri Lankan A/L Technology Stream (ET, SFT, BST, ICT) teacher.

CRITICAL GENERATION RULES:
1. NEVER REPEAT the same sentence, phrase, or line under any circumstances.
2. Once a point or section is written, STOP and move immediately to the next topic.
3. Write in clean, natural Sinhala (සිංහල). Keep it structured and easy to read.

RESPONSE STRUCTURE:
- 📌 **අර්ථදැක්වීම (Definition)**: Brief 2-3 sentence introduction.
- 🎯 **ප්‍රධාන කාර්යය සහ වැදගත්කම (Key Function)**: Main points in bullet form.
- 🔍 **වර්ගීකරණය (Types & Categories)**: Key types with brief descriptions.
- 💡 **උදාහරණ (Examples)**: Real-world AL syllabus examples.

If unrelated to AL Tech:
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
        with st.spinner("A/L විෂය නිර්දේශයට අනුව පිළිතුර සකසමින් පවතී..."):
            try:
                web_info = search_web(user_input)
                
                full_prompt = f"Student Question: {user_input}"
                if web_info:
                    full_prompt += f"\n\nContext:\n{web_info}"

                # Repetition සම්පූර්ණයෙන්ම නැවැත්වූ LLaMA Model Call එක
                response = completion(
                    model="groq/llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.5,
                    frequency_penalty=0.8,  # Repeat වෙන එක නවත්වන ප්‍රධානම දේ
                    presence_penalty=0.6,   # අලුත් වචන භාවිතයට පෙළඹවීම
                    max_tokens=1000         # දිගටම repeat වෙමින් ලිවීම වැළැක්වීම
                )
                
                answer = response.choices[0].message.content
                st.success("විස්තරාත්මක පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
