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

# Upload කළ Photo එක Preview පෙන්වීම
if uploaded_file and uploaded_file.type.startswith("image/"):
    st.image(uploaded_file, caption="Upload කරන ලද ප්‍රශ්න පත්‍රය", use_container_width=True)

with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: photo එකේ ප්‍රශ්නයට උත්තර දෙන්න / 5M සංකල්පය...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# System Prompt
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

CRITICAL INSTRUCTION FOR IMAGES:
- Read and transcribe the EXACT questions written in the provided image.
- Solve ONLY those specific questions shown in the image according to official A/L marking schemes.
- Ignore all other external PDF syllabus context if an image is provided.

FORMATTING RULES:
- Write in accurate examination-standard Sinhala (සිංහල).
- Use Markdown Tables (| අංගය | විස්තරය |) when presenting components, differences, or lists.
- Use clear bullet points and bold technical terms.
"""

if submit_button:
    if user_input or uploaded_file:
        with st.spinner("විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                is_image = uploaded_file is not None and uploaded_file.type.startswith("image/")

                if is_image:
                    # getvalue() භාවිතයෙන් රූපයේ සියලු දත්ත නිවැරදිව ලබා ගැනීම
                    image_bytes = uploaded_file.getvalue()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    
                    user_instruction = user_input if user_input.strip() else "මෙම පින්තූරයේ ඇති ප්‍රශ්නයට A/L Marking Scheme එකට අනුව උත්තර සපයන්න."
                    
                    messages_payload = [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": f"Read the attached image and solve the exact question inside it.\nUser Instruction: {user_instruction}"
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
                    
                    model_name = "openrouter/openai/gpt-4o-mini" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.2-11b-vision-instruct"

                    response = completion(
                        model=model_name,
                        messages=messages_payload,
                        temperature=0.1
                    )

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
                    model_name = "openrouter/openai/gpt-4o-mini" if "OPENROUTER_API_KEY" in os.environ else "groq/llama-3.3-70b-versatile"

                    response = completion(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        temperature=0.2
                    )

                answer = response.choices[0].message.content
                st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                st.markdown(answer)

            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න හෝ පින්තූරයක් Upload කරන්න.")
