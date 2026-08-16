import streamlit as st
from litellm import completion
import os
import glob
from pypdf import PdfReader

# Page Setup
st.set_page_config(page_title="TECH gpt - A/L Guru", page_icon="logo.png")

# API Keys පරීක්ෂාව
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
elif "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# ---------------------------------------------------------
# PDF කියවා පිරිසිදු කරගැනීම
# ---------------------------------------------------------
@st.cache_data
def load_all_pdfs():
    combined_text = ""
    pdf_files = glob.glob("*.pdf") + glob.glob("pdfs/*.pdf")
    
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text and len(text.strip()) > 10:
                    combined_text += text + "\n"
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
            
    return combined_text

pdf_context_data = load_all_pdfs()

st.title("🎓 TECH gpt - A/L Tech AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ඕනෑම ප්‍රශ්නයක් අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ප්‍රාථමික පරිවෘත්තජ, SFT මාන, IP ලිපින...")

system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If the user asks who made/created/developed you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

STRICT REPETITION PREVENT RULE:
- NEVER repeat the exact same sentence or definition under different bullet points.
- Every single bullet point MUST contain unique, distinct, and exam-relevant academic points.

ANSWER STYLE:
- Write accurate A/L examination-standard Sinhala (සිංහල).
- Use embedded PDF context combined with official NIE A/L syllabus principles.
- NEVER show source notes, chapter numbers, or references at the end.

REFUSAL RULE:
- Refuse ONLY non-academic topics like movies, cooking, gossip.
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("විද්‍යාත්මක හා තාක්ෂණික දත්ත විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                final_user_prompt = user_input
                # PDF දත්ත සීමිත ප්‍රමාණයකට එකතු කිරීම (AI එක ඩම්ප් වීම වැළැක්වීමට)
                if pdf_context_data and len(pdf_context_data) > 50:
                    truncated_context = pdf_context_data[:5000]
                    final_user_prompt = f"Syllabus Context:\n{truncated_context}\n\nQuestion: {user_input}"

                model_name = "openrouter/deepseek/deepseek-chat" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.3-70b-versatile"
                
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": final_user_prompt}
                    ],
                    temperature=0.3,
                    frequency_penalty=0.6, # එකම පේළිය නැවත නැවත කීම 100% ක් නතර කරයි
                    presence_penalty=0.4
                )
                
                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
