import streamlit as st
import os
import glob
import base64
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
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** ප්‍රශ්න අසන්න, නැතහොත් ප්‍රශ්න පත්‍රයේ පින්තූරයක් Upload කරන්න:")

# File Uploader
uploaded_file = st.file_uploader("📸 ප්‍රශ්න පත්‍රයේ පින්තූරයක් (JPG/PNG) හෝ PDF එකක් එකතු කරන්න:", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file and uploaded_file.type.startswith("image/"):
    st.image(uploaded_file, caption="Upload කරන ලද ප්‍රශ්න පත්‍රය", use_container_width=True)

with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: 5M සංකල්පය හෝ photo එකට අදාළ උපදෙස්...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# System Prompt
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

CRITICAL INSTRUCTION FOR SINHALA IMAGE READING:
1. Carefully read and internally translate/transcribe the exact Sinhala questions visible in the image.
2. Provide precise, short, and accurate exam-standard Sinhala answers based on official Sri Lankan G.C.E. A/L marking schemes.
3. NEVER repeat words, sentences, or phrases in loops.

FORMATTING RULES:
- Answer sub-questions directly using numbers like (i), (ii), (iii), (iv), (v).
- Use accurate examination Sinhala terminology.
"""

if submit_button:
    if user_input or uploaded_file:
        with st.spinner("විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                is_image = uploaded_file is not None and uploaded_file.type.startswith("image/")

                # 1. Image Mode (Using GPT-4o-Mini via OpenRouter with Penalty Controls)
                if is_image:
                    image_bytes = uploaded_file.getvalue()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": "Transcribe the Sinhala questions in this image accurately and write the correct A/L marking scheme answer for each sub-question numbered clearly."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{uploaded_file.type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]

                    # frequency_penalty සහ presence_penalty මගින් Looping වැළැක්වීම
                    response = client.chat.completions.create(
                        model="openai/gpt-4o-mini",
                        messages=messages,
                        temperature=0.1,
                        max_tokens=800,
                        frequency_penalty=0.5,
                        presence_penalty=0.5
                    )

                # 2. Text / PDF Mode
                else:
                    context_text = ""
                    if uploaded_file and uploaded_file.type == "application/pdf":
                        try:
                            custom_pdf_reader = PdfReader(uploaded_file)
                            for page in custom_pdf_reader.pages:
                                t = page.extract_text()
                                if t: context_text += t + "\n"
                        except Exception as e:
                            st.error(f"PDF කියවීමේ දෝෂයක්: {e}")

                    if user_input:
                        query_words = [w.lower() for w in user_input.split() if len(w) > 2]
                        relevant_pages = [p for p in pdf_pages if any(w in p.lower() for w in query_words)]
                        if relevant_pages:
                            context_text += "\n\n---\n\n" + "\n\n---\n\n".join(relevant_pages)[:10000]

                    user_content = f"Official Syllabus Context:\n{context_text}\n\nUser Question: {user_input}"

                    response = client.chat.completions.create(
                        model="deepseek/deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        temperature=0.2,
                        max_tokens=1000
                    )

                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)

            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න හෝ පින්තූරයක් Upload කරන්න.")
