import streamlit as st
from litellm import completion
import os
import glob
from pypdf import PdfReader

st.set_page_config(page_title="TECH gpt - A/L Guru", page_icon="logo.png")

# API Keys
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
elif "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

@st.cache_data
def load_all_pdfs():
    combined_text = ""
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
- If the user asks who made/created/developed you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

STRICT MARKDOWN TABLE FORMATTING RULE:
- Whenever presenting data that involves compounds, sources, uses, functions, components, or comparisons (such as Secondary Metabolites: සංයෝග, ප්‍රභව, ප්‍රයෝජන), YOU MUST ALWAYS OUTPUT THE DATA IN A CLEAN MARKDOWN TABLE (| සංයෝගය | ප්‍රභවය | ප්‍රයෝජන |).
- DO NOT convert tabular PDF data into general text paragraphs or bullet points. Preserve table structures.

STRICT PDF-FIRST RULE:
- Answer strictly using the definitions, tables, and details provided in the uploaded PDF / Syllabus Context.

ANSWER STYLE:
- Accurate examination-standard Sinhala (සිංහල).
- Use Markdown Tables for all structured/tabular data.
- NO sentence repetition loops.
- NEVER display source citations, page numbers, or chapter references at the end.
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("සටහන් විශ්ලේෂණය කර වගු සකසමින් පවතී..."):
            try:
                final_user_prompt = user_input
                if pdf_context_data and len(pdf_context_data.strip()) > 50:
                    truncated_context = pdf_context_data[:8000]
                    final_user_prompt = f"Official Syllabus Context (PDF):\n{truncated_context}\n\nUser Question: {user_input}"

                model_name = "openrouter/deepseek/deepseek-chat" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.3-70b-versatile"
                
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": final_user_prompt}
                    ],
                    temperature=0.2,
                    frequency_penalty=0.5
                )
                
                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
