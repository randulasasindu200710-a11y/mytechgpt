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
# PDF කියවා පිටු වශයෙන් ගබඩා කිරීම
# ---------------------------------------------------------
@st.cache_data
def load_pdf_pages():
    pages_data = []
    pdf_files = glob.glob("*.pdf") + glob.glob("pdfs/*.pdf")
    
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    pages_data.append(text)
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
            
    return pages_data

pdf_pages = load_pdf_pages()

st.title("🎓 TECH gpt - A/L Tech AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ඕනෑම ප්‍රශ්නයක් අසන්න:")

with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: ඕල්ඩුවායි වාදය, 5M සංකල්පය, හුක් නියමය...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# ---------------------------------------------------------
# Universal System Prompt (අලුත් කරන ලද නීති)
# ---------------------------------------------------------
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

CRITICAL SYLLABUS DOMAIN & REFUSAL LOGIC:
1. SFT, ET, BST include topics that sound like other subjects but ARE VALID. 
   - Example: "ඕල්ඩුවායි වාදය" (Olduvai theory) IS A VALID SFT TOPIC related to energy crises and the decline of industrial civilization. DO NOT treat it as history.
   - Example: 5M, 5S, Economics, Management, ISO standards ARE VALID Tech topics.
2. IF the user's concept is found in the "Official Syllabus Context (PDF)" below, YOU MUST NEVER REFUSE IT. If it's in the PDF, it is automatically part of the syllabus.
3. Refuse ONLY if the topic is 100% outside the Tech Stream domain AND is not mentioned in the provided PDF (e.g., movies, gossip, Sinhala literature). 
   - Refusal message: "කණගාටුයි! මට පිළිතුරු දිය හැක්කේ උසස් පෙළ තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්න සඳහා පමණයි."

ANSWERING LOGIC (PDF FIRST, AI SECOND):
- First, extract the answer strictly from the PDF Context provided. 
- If not found in the PDF context, use your expert AI knowledge of the A/L Technology syllabus to answer accurately.

FORMATTING RULES:
- Write in accurate examination-standard Sinhala (සිංහල).
- Always use Markdown Tables (| අංගය | විස්තරය |) when presenting components, differences, or lists.
- Use clear bullet points.
"""

if submit_button:
    if user_input:
        with st.spinner("සටහන් විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                # ---------------------------------------------------------
                # Smart Keyword Filtering
                # ---------------------------------------------------------
                query_words = [w for w in user_input.split() if len(w) > 2]
                relevant_pages = []
                
                for page in pdf_pages:
                    if any(word.lower() in page.lower() for word in query_words):
                        relevant_pages.append(page)
                
                if relevant_pages:
                    context_text = "\n\n---\n\n".join(relevant_pages)[:30000]
                else:
                    context_text = "\n\n---\n\n".join(pdf_pages)[:30000]

                final_user_prompt = f"Official Syllabus Context (PDF):\n{context_text}\n\nUser Question: {user_input}"

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
                
                if "කණගාටුයි!" in answer:
                    st.warning(answer)
                else:
                    st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                    st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")   
