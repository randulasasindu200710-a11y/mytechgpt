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

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: IP ලිපිනයක් යනු කුමක්ද? නැතහොත් SFT මාන...")

# විස්තරාත්මක පිළිතුරු ලබාදෙන පරිදි සකස් කළ System Prompt එක
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology Stream (ET, SFT, BST, ICT) teacher and exam paper evaluator.

YOUR GOAL:
Provide DETAILED, COMPREHENSIVE, and IN-DEPTH Sinhala explanations suitable for A/L examination standard answers.

RULES FOR ANSWERING:
1. Write in clear, natural, and grammatically accurate Sinhala (සිංහල).
2. DO NOT give 1-2 word brief bullets. Provide detailed explanations (2-3 sentences per point) for every bullet point.
3. Structure your response logically using Markdown:
   - 📌 **අර්ථදැක්වීම සහ හැඳින්වීම (Definition & Introduction)**: Comprehensive, clear explanation of the core concept.
   - 🎯 **ප්‍රධාන කාර්යයන් සහ වැදගත්කම (Key Functions & Importance)**: Explain WHY and HOW it works in detail.
   - 🔍 **වර්ගීකරණය සහ වෙනස්කම් (Types & Classifications)**: Detailed comparison (e.g., IPv4 vs IPv6, Static vs Dynamic, bit lengths, format differences).
   - 💡 **ප්‍රායෝගික උදාහරණ (Examples & Applications)**: Practical real-world examples with explanations.
4. DO NOT repeat exact sentences or continuously loop text.

IF UNRELATED TO A/L TECH:
Say only: "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
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
        with st.spinner("A/L විෂය නිර්දේශයට අනුව විස්තරාත්මක පිළිතුරක් සකසමින් පවතී..."):
            try:
                web_info = search_web(user_input)
                
                full_prompt = f"Student Question: {user_input}"
                if web_info:
                    full_prompt += f"\n\nContext:\n{web_info}"

                # Balanced Parameters for High Detail + No Loops
                response = completion(
                    model="groq/llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.4,
                    frequency_penalty=0.3, # Repeat වීම වළක්වන අතරම විස්තරාත්මකව ලියන්න ඉඩ දෙයි
                    presence_penalty=0.3,
                    max_tokens=2048        # ලොකු විස්තරාත්මක පිළිතුරක් ලියන්න ඉඩ ලබා දේ
                )
                
                answer = response.choices[0].message.content
                st.success("විස්තරාත්මක පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
