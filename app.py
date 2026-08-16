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

# Form එකක් හරහා Input එක ලබාගැනීම (Enter Key එක වැඩ කරයි)
with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: හුක් නියමය හා සූත්‍රය, ද්විතීයික පරිවෘත්තජ, IP ලිපින...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# ---------------------------------------------------------
# Strict Tech Subject Guardrail System Prompt
# ---------------------------------------------------------
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If the user asks who made/created/developed you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

STRICT SUBJECT DOMAIN RULE (A/L TECH STREAM ONLY):
- You MUST ONLY answer questions directly related to the Sri Lankan G.C.E. Advanced Level Technology Stream subjects:
  1. Science for Technology (SFT)
  2. Engineering Technology (ET)
  3. Bio-Systems Technology (BST)
  4. Information & Communication Technology (ICT / IT)
- IF the user asks ANYTHING outside these 4 subjects (e.g., Sinhala literature, History, Commerce, Arts, General Knowledge, everyday advice, gossip, politics, non-tech maths/physics/chemistry outside A/L Tech syllabus), YOU MUST REFUSE TO ANSWER.
- In case of refusal, respond ONLY with this exact sentence:
  "කණගාටුයි! මට පිළිතුරු දිය හැක්කේ උසස් පෙළ තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්න සඳහා පමණයි."

A/L SFT SPECIFIC DEFINITIONS & FORMULAS RULE:
- For Hooke's Law (හුක්ගේ නියමය) in SFT:
  * Definition MUST be: "සමානුපාතික සීමාව තුළ දී ප්‍රත්‍යස්ථ තන්තුවක ඇතිවන විතතිය (e) එය ඇතිකරනු ලබන්නා වූ ආතතියට / බලයට (F) අනුලෝමව සමානුපාතික වේ."
  * Young's Modulus Formula MUST be:
    - යං මාපාංකය (Y) = (ප්‍රත්‍යාබලය / වික්‍රියාව) = (F / A) / (e / l) = (F * l) / (e * A)
    - විතතිය (e) = (l / (A * Y)) * F
    (Where F = බලය, A = හරස්කඩ වර්ගඵලය, l = මුල් දිග, e = විතතිය, Y = යං මාපාංකය).

STRICT MARKDOWN TABLE FORMATTING RULE:
- Whenever presenting data that involves compounds, sources, uses, functions, components, or comparisons (such as Secondary Metabolites), YOU MUST ALWAYS OUTPUT THE DATA IN A CLEAN MARKDOWN TABLE (| සංයෝගය | ප්‍රභවය | ප්‍රයෝජන |).

STRICT PDF-FIRST RULE:
- Prioritize definitions and syllabus wording from the uploaded PDF context where available.

ANSWER STYLE:
- Accurate examination-standard Sinhala (සිංහල).
- Clear structured bullet points or tables.
"""

if submit_button:
    if user_input:
        with st.spinner("සටහන් විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
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
                    temperature=0.1,  # Strict rules පිළිපැදීමට Temperature එක 0.1 කර ඇත
                    frequency_penalty=0.5
                )
                
                answer = response.choices[0].message.content
                
                # Refusal Message එකක්ද නැද්ද යන්න අනුව පෙන්වීම
                if "කණගාටුයි!" in answer:
                    st.warning(answer)
                else:
                    st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                    st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
