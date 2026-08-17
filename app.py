import streamlit as st
import os
import glob
from pypdf import PdfReader
from openai import OpenAI

st.set_page_config(page_title="TECH gpt - A/L Guru", page_icon="logo.png")

# OpenRouter Client Setup
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("කරුණාකර OPENROUTER_API_KEY එක Streamlit Secrets වලට ඇතුළත් කරන්න.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

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
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** ඕනෑම ප්‍රශ්නයක් පහතින් ඇතුළත් කරන්න:")

# Text Input Form
with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: කොහොඹ ශාකයේ විද්‍යාත්මක නාමය, 5M සංකල්පය...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# System Prompt with Strict Scientific Name Verification
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

STRICT SCIENTIFIC ACCURACY RULE:
- You MUST strictly follow standard Sri Lankan A/L Biology / BST / SFT Resource Book facts.
- Do NOT mix up scientific names. (e.g., Kohomba = Azadirachta indica, Kumbuk = Terminalia arjuna).

ANSWER STRUCTURE:
1. Direct Answer (නිවැරදි කෙටි පිළිතුර)
2. Detailed Explanation (විෂය නිර්දේශයට අදාළ පැහැදිලි කිරීම)
3. Key Scientific Terms & Families (විද්‍යාත්මක නාම සහ කුල)
"""

if submit_button:
    if user_input.strip():
        with st.spinner("විශ්ලේෂණය කර නිවැරදි පිළිතුර සකසමින් පවතී..."):
            try:
                # PDF Context search
                query_words = [w.lower() for w in user_input.split() if len(w) > 2]
                relevant_pages = [p for p in pdf_pages if any(w in p.lower() for w in query_words)]
                
                context_text = ""
                if relevant_pages:
                    context_text = "\n\n---\n\n".join(relevant_pages)[:10000]

                user_content = f"Syllabus Context from PDFs:\n{context_text}\n\nUser Question: {user_input}\n\nProvide the exact, highly accurate Sri Lankan A/L exam Sinhala answer."

                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.0,  # 0.0 මගින් Fact errors සම්පූර්ණයෙන්ම වළක්වයි
                    max_tokens=1000
                )

                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)

            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
