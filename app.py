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
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: 5M සංකල්පය, හුක් නියමය හෝ photo එකට අදාළ උපදෙස්...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# System Prompt
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

CRITICAL INSTRUCTION FOR SINHALA IMAGE READING:
- Carefully read and transcribe the exact Sinhala text and question numbers inside the uploaded image.
- Solve ONLY the specific questions visible in the image matching official Sri Lankan G.C.E. A/L marking schemes.
- Do NOT hallucinate or output unrelated general topics.
- Ignore background PDF syllabus context completely when an image is provided.

FORMATTING RULES:
- Write in accurate examination-standard Sinhala (සිංහල).
- Use clear bullet points and bold technical terms.
- Use Markdown Tables (| අංගය | විස්තරය |) ONLY when comparing items or organizing structured data.
"""

if submit_button:
    if user_input or uploaded_file:
        with st.spinner("විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                is_image = uploaded_file is not None and uploaded_file.type.startswith("image/")

                # 1. Image Mode (OpenAI GPT-4o with max_tokens set)
                if is_image:
                    image_bytes = uploaded_file.getvalue()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    
                    user_instruction = user_input.strip() if user_input and user_input.strip() else "මෙම පින්තූරයේ ඇති ප්‍රශ්නවලට A/L Marking Scheme එකට අනුව නිවැරදි උත්තර සපයන්න."

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": f"Read the Sinhala text in this image accurately and solve the exact questions inside it.\nUser Note: {user_instruction}"
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

                    # max_tokens=1000 මගින් Credits වැය වීම පාලනය කරයි
                    response = client.chat.completions.create(
                        model="openai/gpt-4o",
                        messages=messages,
                        temperature=0.1,
                        max_tokens=1000
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
