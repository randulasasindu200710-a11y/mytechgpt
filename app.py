import streamlit as st
from litellm import completion
from duckduckgo_search import DDGS
import os

# 1. Groq API Key එක ලබා ගැනීම
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# UI එක සකස් කිරීම
st.set_page_config(page_title="A/L Tech AI Guru", page_icon="🎓")
st.title("🎓TECH-gpt")
st.write("ET - SFT - IT")

user_input = st.text_input("Your quection?", placeholder="උදා: IP ලිපිනයක් යනු කුමක්ද? නැතහොත් SFT මාන...")

# A/L Exam එකට ගැළපෙන පරිදි විස්තරාත්මක පිළිතුරු සැකසීමට සකස් කළ System Prompt එක
system_prompt = """
You are an expert Sri Lankan A/L Technology Stream (ET, SFT, BST, ICT) teacher and paper evaluator. 

RESPONSE STRUCTURE RULES:
1. ALWAYS provide detailed, comprehensive, and well-explained answers suitable for A/L exam standards.
2. Write in clear, natural Sinhala (සිංහල) with correct technical terms.
3. Structure the explanation logically using Markdown headings and bullet points. Include:
   - 📌 **අර්ථදැක්වීම සහ හඳුන්වාදීම (Definition & Introduction)**
   - 🎯 **ප්‍රධාන කාර්යයන් සහ වැදගත්කම (Key Functions & Importance)**
   - 🔍 **වර්ගීකරණය / ප්‍රධාන වර්ග (Types & Classifications)** (e.g., IPv4 vs IPv6, Static vs Dynamic)
   - 💡 **පැහැදිලි කිරීම සහ උදාහරණ (Examples & Explanation)**
4. NEVER repeat sentences or loop paragraphs.
5. Only refuse if the question is CLEARLY completely unrelated to school or technology (e.g., movies, gossip, cooking recipes). 
   If refusing, say: "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
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

                response = completion(
                    model="groq/llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.3
                )
                
                answer = response.choices[0].message.content
                st.success("විස්තරාත්මක පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
