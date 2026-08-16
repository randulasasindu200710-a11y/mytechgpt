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

# ---------------------------------------------------------
# PDF කියවීම සහ Sidebar එකේ Status පෙන්වීම
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
                if text:
                    combined_text += text + "\n"
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
            
    return combined_text

pdf_context_data = load_all_pdfs()

# Debug: PDF එකෙන් අකුරු කියවුණාද කියා පරීක්ෂා කිරීම
st.sidebar.header("⚙️ PDF Data Status")
if pdf_context_data and len(pdf_context_data.strip()) > 50:
    st.sidebar.success(f"✅ PDF සටහන් කියවන ලදී! ({len(pdf_context_data)} characters)")
else:
    st.sidebar.warning("⚠️ PDF එකේ සිංහල අකුරු කියවීමට නොහැකි විය (Font Encoding issue). AI එක දැනුමෙන් පමණක් උත්තර දෙයි.")

st.title("🎓 TECH gpt - A/L Tech AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ඕනෑම ප්‍රශ්නයක් අසන්න:")

user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ප්‍රාථමික පරිවෘත්තජ, SFT මාන, IP ලිපින...")

system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If the user asks who made/created/developed you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

STRICT PDF-FIRST RULE:
- IF "Syllabus Context" is provided below, your HIGHEST PRIORITY is to answer STRICTLY using the definitions, bullet points, and examples given in that context.
- Match definitions EXACTLY as presented in the Sri Lankan A/L Teacher Resource Book / Syllabus (e.g. For primary metabolites, emphasize survival, growth, development, reproduction, and examples like sucrose, ethanol, lactic acid if mentioned).

ANSWER STYLE:
- Accurate examination-standard Sinhala (සිංහල).
- Structured bullet points.
- NO sentence repetitions or infinite loops.
- NEVER display source citations or chapter numbers at the end.
"""

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("PDF සටහන් සහ AI දත්ත විශ්ලේෂණය කරමින් පවතී..."):
            try:
                final_user_prompt = user_input
                if pdf_context_data and len(pdf_context_data.strip()) > 50:
                    truncated_context = pdf_context_data[:7000]
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
