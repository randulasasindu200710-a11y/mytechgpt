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

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ගින්නක් යනු කුමක්ද? නැතහොත් SFT මාන...")

# A/L Tech Syllabus එකට ගැළපෙන පරිදි සකස් කළ System Prompt එක
system_prompt = """
You are a friendly, highly knowledgeable teacher for Sri Lankan G.C.E. Advanced Level (A/L) Technology Stream (ET, SFT, BST, ICT).

GUIDELINES:
1. ALWAYS respond in clear, grammatically accurate Sinhala (සිංහල).
2. When the user enters a short phrase or term (e.g., "ගින්නක් යනු", "මාන", "CPU", "පස"), ALWAYS view it through the A/L Technology stream context (e.g., Industrial Safety, Fire Triangle, SFT Physics, ICT concepts, BST Agriculture) and explain it according to the A/L syllabus.
3. NEVER repeat paragraphs or sentences. Use neat bullet points.
4. Only refuse if the question is CLEARLY completely unrelated to school or technology (e.g., cooking recipes, movies, gossip, political opinions).
5. If refusing, say: "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
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
        with st.spinner("Syllabus එකට අනුව පිළිතුර සකසයි..."):
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
                st.success("පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
