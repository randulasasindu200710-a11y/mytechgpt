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

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: කෘතිම රබර් වර්ග, SFT මාන, IP ලිපින...")

# ලංකාවේ A/L NIE Resource Book එකට අනුව සකස් කළ System Prompt එක
system_prompt = """
You are a top Sri Lankan G.C.E. A/L Technology stream teacher (SFT, ET, BST, ICT) who strictly marks papers according to the NIE (National Institute of Education Sri Lanka) Teacher Resource Book (සම්පත් පොත).

STRICT SYLLABUS DIRECTIVES:
1. Always base answers strictly on the official Sri Lankan G.C.E. A/L Syllabus (NIE Resource Book).
   - E.g., For SFT Polymers / Synthetic Rubber (කෘතිම රබර්): Always mention specific syllabus types like SBR (Styrene-Butadiene Rubber: Monomers = Styrene + 1,3-butadiene), Neoprene (Chloroprene), Nitrile Rubber (Acrylonitrile + Butadiene), and Vulcanization using Sulfur.
   - For SFT Physics: Units, Dimensions, Mechanics according to AL SFT Resource book.
   - For ICT / ET / BST: Strict adherence to Sri Lankan A/L syllabus terms.

2. ANSWER FORMATTING:
   - Provide direct, accurate A/L standard Sinhala (සිංහල) points.
   - Include Monomers (මොනෝමර), Properties (ලක්ෂණ), and Uses (භාවිත) where applicable.
   - NO general internet fluff or useless repeating sentences. 
   - Keep answers clear, technical, precise, and directly suitable for AL exam papers.

If unrelated to Sri Lankan AL Technology stream:
"කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("A/L සම්පත් පොතට (Resource Book) අනුව පිළිතුර සකසමින් පවතී..."):
            try:
                response = completion(
                    model="groq/llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.2, # Exact A/L Syllabus facts ලබා ගැනීමට Temperature එක අඩු කළා
                    frequency_penalty=0.4,
                    presence_penalty=0.3,
                    max_tokens=1500
                )
                
                answer = response.choices[0].message.content
                st.success("A/L විෂය නිර්දේශයට අදාළ පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
