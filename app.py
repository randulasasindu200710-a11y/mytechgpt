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
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** ප්‍රශ්න අසන්න, නැතහොත් ප්‍රශ්න පත්‍රයේ පින්තූරයක්/PDF එකක් Upload කරන්න:")

# File Uploader
uploaded_file = st.file_uploader("📸 ප්‍රශ්න පත්‍රයේ පින්තූරයක් (JPG/PNG) හෝ අමතර PDF එකක් එකතු කරන්න:", type=["png", "jpg", "jpeg", "pdf"])

with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න (පින්තූරයක් යෙදුවේ නම් එයට අදාළ සටහනක් තබන්න):", placeholder="උදා: ඕල්ඩුවායි වාදය, 5M සංකල්පය, හුක් නියමය...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# ---------------------------------------------------------
# System Prompt (Updated & Fixed Refusal Rules)
# ---------------------------------------------------------
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

SYLLABUS & DOMAIN VALIDATION (CRITICAL):
- G.C.E. A/L Technology subjects (ET, SFT, BST, ICT) cover a vast area including:
  * ET / BST: 5M concept (Man, Machine, Material, Method, Measurement), 5S, Total Quality Management (TQM), ISO standards, Safety, Workshop technology, Management, Economics, Agricultural Machinery, Post-harvest Tech.
  * SFT: Olduvai theory, Energy crisis, Physics, Chemistry, Biology, Environmental Science, Soil science.
  * ICT: Programming, Networking, Hardware, Databases, Logic gates.
- DO NOT REFUSE these technical/management concepts! 5M, 5S, TQM, ISO are 100% VALID A/L TECH TOPICS.
- Refuse ONLY if the topic is 100% non-educational and unrelated to school subjects (e.g., cinema gossip, political news, general entertainment).
  * Refusal message: "කණගාටුයි! මට පිළිතුරු දිය හැක්කේ උසස් පෙළ තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්න සඳහා පමණයි."

IMAGE PROCESSING INSTRUCTION:
- If an image is uploaded, YOUR HIGHEST PRIORITY IS TO READ AND SOLVE THE EXACT QUESTION SHOWN IN THE IMAGE.

ANSWERING RULES:
- Write in accurate examination-standard Sinhala (සිංහල).
- Match official Sri Lankan G.C.E. A/L marking scheme standard.
- Use Markdown Tables (| අංගය | විස්තරය |) when presenting components, differences, or categorized lists.
- Use clear bullet points and bold technical terms.
"""

if submit_button:
    if user_input or uploaded_file:
        with st.spinner("තොරතුරු විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                context_text = ""
                is_image = uploaded_file and uploaded_file.type.startswith("image/")

                # 1. Upload කළ PDF එකක් තිබේ නම්
                if uploaded_file and uploaded_file.type == "application/pdf":
                    try:
                        custom_pdf_reader = PdfReader(uploaded_file)
                        for page in custom_pdf_reader.pages:
                            t = page.extract_text()
                            if t: context_text += t + "\n"
                    except Exception as e:
                        st.error(f"PDF කියවීමේ දෝෂයක්: {e}")

                # 2. Keyword Search (Server PDFs)
                if user_input:
                    stopwords = {"photo", "ekata", "adalawa", "uththara", "denna", "me", "mewa", "prashna", "uthtara", "thiyena"}
                    query_words = [w.lower() for w in user_input.split() if len(w) > 2 and w.lower() not in stopwords]
                    
                    relevant_pages = []
                    if query_words:
                        relevant_pages = [p for p in pdf_pages if any(w in p.lower() for w in query_words)]
                    
                    if relevant_pages:
                        context_text += "\n\n---\n\n" + "\n\n---\n\n".join(relevant_pages)[:10000]

                # Prompt සකස් කිරීම
                if is_image:
                    final_prompt_text = f"CRITICAL TASK: Carefully read the uploaded image and solve the exact questions inside it.\nUser instructions: {user_input if user_input else 'මෙම පින්තූරයේ ඇති ප්‍රශ්නවලට A/L Marking Scheme එකට අනුව පිළිතුරු සපයන්න.'}"
                    if context_text.strip():
                        final_prompt_text += f"\n\nSyllabus Reference Context:\n{context_text}"
                else:
                    final_prompt_text = f"Official Syllabus Context (PDF):\n{context_text}\n\nUser Prompt: {user_input}"

                # Model තේරීම
                if is_image:
                    base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    user_content = [
                        {"type": "text", "text": final_prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{uploaded_file.type};base64,{base64_image}"
                            }
                        }
                    ]
                    
                    if "OPENROUTER_API_KEY" in os.environ:
                        model_name = "openrouter/openai/gpt-4o-mini"
                    else:
                        model_name = "groq/llama-3.2-11b-vision-instruct"
                else:
                    user_content = final_prompt_text
                    if "OPENROUTER_API_KEY" in os.environ:
                        model_name = "openrouter/openai/gpt-4o-mini"
                    else:
                        model_name = "groq/llama-3.3-70b-versatile"

                # API Call
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.2
                )
                
                answer = response.choices[0].message.content
                
                if "කණගාටුයි!" in answer and len(answer) < 150:
                    st.warning(answer)
                else:
                    st.success("විෂය නිර්දේශයට අදාළ නිවැරදි පිළිතුර:")
                    st.markdown(answer)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න හෝ පින්තූරයක් Upload කරන්න.")
