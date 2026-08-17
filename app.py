import streamlit as st
from litellm import completion
import os
import glob
import base64
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
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** ප්‍රශ්න අසන්න, නැතහොත් ප්‍රශ්න පත්‍රයේ පින්තූරයක් Upload කරන්න:")

# File Uploader
uploaded_file = st.file_uploader("📸 ප්‍රශ්න පත්‍රයේ පින්තූරයක් (JPG/PNG) හෝ PDF එකක් එකතු කරන්න:", type=["png", "jpg", "jpeg", "pdf"])

with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: 5M සංකල්පය, හුක් නියමය හෝ photo එකට අදාළ උපදෙස්...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# ---------------------------------------------------------
# System Prompt
# ---------------------------------------------------------
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

CRITICAL INSTRUCTION FOR IMAGE PROCESSING:
- When an image is provided, READ THE EXACT TEXT AND QUESTIONS INSIDE THE IMAGE.
- Answer ONLY the specific questions visible in the uploaded image.
- Do NOT talk about unrelated topics. Focus entirely on solving the uploaded photo's content matching Sri Lankan A/L marking schemes.

FORMATTING RULES:
- Write in accurate examination-standard Sinhala (සිංහල).
- Use Markdown Tables (| අංගය | විස්තරය |) when presenting components, differences, or lists.
- Use clear bullet points and bold technical terms.
"""

if submit_button:
    if user_input or uploaded_file:
        with st.spinner("විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                is_image = uploaded_file and uploaded_file.type.startswith("image/")

                # ---------------------------------------------------------
                # 1. PHOTO MODE (PDF Context 100% Bypass කරයි)
                # ---------------------------------------------------------
                if is_image:
                    base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    
                    prompt_instruction = user_input if user_input and len(user_input.strip()) > 0 else "මෙම පින්තූරයේ ඇති ප්‍රශ්නවලට A/L Marking Scheme එකට අනුව නිවැරදි උත්තර සපයන්න."
                    
                    user_content = [
                        {
                            "type": "text", 
                            "text": f"IMPORTANT: Read the attached photo carefully and answer the EXACT questions shown inside it.\nUser Instruction: {prompt_instruction}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{uploaded_file.type};base64,{base64_image}"
                            }
                        }
                    ]
                    
                    model_name = "openrouter/openai/gpt-4o-mini" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.2-11b-vision-instruct"

                # ---------------------------------------------------------
                # 2. TEXT / PDF MODE (Photo නොමැති විට පමණක් ක්‍රියාත්මක වේ)
                # ---------------------------------------------------------
                else:
                    context_text = ""
                    
                    # Upload කළ PDF එකක් නම්
                    if uploaded_file and uploaded_file.type == "application/pdf":
                        try:
                            custom_pdf_reader = PdfReader(uploaded_file)
                            for page in custom_pdf_reader.pages:
                                t = page.extract_text()
                                if t: context_text += t + "\n"
                        except Exception as e:
                            st.error(f"PDF කියවීමේ දෝෂයක්: {e}")

                    # Server PDF Search
                    if user_input:
                        query_words = [w.lower() for w in user_input.split() if len(w) > 2]
                        relevant_pages = [p for p in pdf_pages if any(w in p.lower() for w in query_words)]
                        
                        if relevant_pages:
                            context_text += "\n\n---\n\n" + "\n\n---\n\n".join(relevant_pages)[:10000]

                    user_content = f"Official Syllabus Context:\n{context_text}\n\nUser Question: {user_input}"
                    model_name = "openrouter/openai/gpt-4o-mini" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.3-70b-versatile"

                # API Call
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.1
                )
                
                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)

            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න හෝ පින්තූරයක් Upload කරන්න.")
