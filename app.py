import streamlit as st
from litellm import completion
import os
import glob
from pypdf import PdfReader

# 1. Browser Tab Config
st.set_page_config(page_title="TECH gpt - A/L Guru", page_icon="logo.png")

# API Keys පරීක්ෂාව
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
elif "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# ---------------------------------------------------------
# Repo එකේ තියෙන සියලුම PDF ස්වයංක්‍රීයව කියවා ගැනීම
# ---------------------------------------------------------
@st.cache_data
def load_all_pdfs():
    combined_text = ""
    # Root folder එකේ සහ pdfs folder එකේ තියෙන සියලුම .pdf සොයා ගැනීම
    pdf_files = glob.glob("*.pdf") + glob.glob("pdfs/*.pdf")
    
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    combined_text += text + "\n"
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
            
    return combined_text

pdf_context_data = load_all_pdfs()

st.title("🎓 TECH gpt - A/L Tech AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ඕනෑම ප්‍රශ්නයක් අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ද්විතීයික පරිවෘත්තජ, SFT මාන, IP ලිපින...")

system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If the user asks who made/created/developed you (e.g., "ඔයාව හැදුවේ කවුද?"), reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

RESOURCE KNOWLEDGE RULE:
- You are provided with embedded A/L notes and Syllabus/Resource Book context from uploaded PDFs.
- Always combine the embedded PDF knowledge with official Sri Lankan A/L Technology syllabus principles to formulate the answer.

CORE INSTRUCTIONS:
1. FLEXIBLE TECH SUBJECT COVERAGE:
   - Accept ALL Sri Lankan A/L Tech stream terms (ET, SFT, BST, ICT).
   - Do NOT be overly strict. Assume any engineering, scientific, or tech phrase belongs to the A/L Tech syllabus.

2. ANSWER STYLE:
   - Write in clear, accurate, examination-standard Sinhala (සිංහල).
   - Provide direct, structured bullet points with clear explanations.
   - NO sentence repetitions or infinite loops.
   - NEVER show source notes, chapter numbers, citations, or book references at the end.

3. REFUSAL RULE (ONLY FOR COMPLETELY UNRELATED TOPICS):
   - Refuse ONLY if the prompt is CLEARLY about everyday non-academic topics (e.g., cooking, movies, gossip).
   - If refusing, reply ONLY:
     "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්නවලට පමණයි."
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("සටහන් සහ AI දත්ත විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                final_user_prompt = user_input
                if pdf_context_data:
                    truncated_context = pdf_context_data[:10000]
                    final_user_prompt = f"Uploaded Syllabus/Resource Context:\n{truncated_context}\n\nStudent Question: {user_input}"

                model_name = "openrouter/deepseek/deepseek-chat" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.3-70b-versatile"
                
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": final_user_prompt}
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
