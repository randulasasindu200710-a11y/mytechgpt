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

# File Uploader එකතු කිරීම (Images සහ PDFs සඳහා)
uploaded_file = st.file_uploader("📸 ප්‍රශ්න පත්‍රයේ පින්තූරයක් (JPG/PNG) හෝ අමතර PDF එකක් එකතු කරන්න:", type=["png", "jpg", "jpeg", "pdf"])

with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න (පින්තූරයක් යෙදුවේ නම් එයට අදාළ සටහනක් තබන්න):", placeholder="උදා: ඕල්ඩුවායි වාදය, 5M සංකල්පය, හෝ 'මෙම රූපයේ ප්‍රශ්නයට උත්තර දෙන්න'...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# ---------------------------------------------------------
# Universal System Prompt
# ---------------------------------------------------------
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

CRITICAL SYLLABUS DOMAIN & REFUSAL LOGIC:
1. SFT, ET, BST include topics that sound like other subjects but ARE VALID. 
   - Example: "ඕල්ඩුවායි වාදය" (Olduvai theory) IS A VALID SFT TOPIC related to energy crises and the decline of industrial civilization.
   - Example: 5M, 5S, Economics, Management, ISO standards ARE VALID Tech topics.
2. IF the user's concept is found in the provided PDF or uploaded image/file, YOU MUST NEVER REFUSE IT.
3. Refuse ONLY if the topic is 100% outside the Tech Stream domain AND is not mentioned in any provided document/image. 
   - Refusal message: "කණගාටුයි! මට පිළිතුරු දිය හැක්කේ උසස් පෙළ තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්න සඳහා පමණයි."

ANSWERING LOGIC:
- If an image is provided, carefully read the text/diagrams inside the question paper photo.
- Formulate the answer strictly following Sri Lankan G.C.E. A/L examination marking schemes.
- Combine knowledge from the provided syllabus PDFs and your expert AI capabilities.

FORMATTING RULES:
- Write in accurate examination-standard Sinhala (සිංහල).
- Always use Markdown Tables (| අංගය | විස්තරය |) when presenting components, differences, or lists.
- Use clear bullet points and bold key Sri Lankan technical terms.
"""

if submit_button:
    if user_input or uploaded_file:
        with st.spinner("තොරතුරු හා පින්තූර විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                context_text = ""
                
                # 1. පරිශීලකයා අලුතින් PDF එකක් Upload කර තිබේ නම් එයින් Text ලබාගැනීම
                if uploaded_file and uploaded_file.type == "application/pdf":
                    try:
                        custom_pdf_reader = PdfReader(uploaded_file)
                        for page in custom_pdf_reader.pages:
                            t = page.extract_text()
                            if t: context_text += t + "\n"
                    except Exception as e:
                        st.error(f"PDF කියවීමේ දෝෂයක්: {e}")

                # 2. Server එකේ ඇති PDF වලින් Keyword සෙවීම
                if user_input:
                    query_words = [w for w in user_input.split() if len(w) > 2]
                    relevant_pages = [p for p in pdf_pages if any(w.lower() in p.lower() for w in query_words)]
                    if relevant_pages:
                        context_text += "\n\n---\n\n" + "\n\n---\n\n".join(relevant_pages)[:20000]
                    else:
                        context_text += "\n\n---\n\n" + "\n\n---\n\n".join(pdf_pages)[:20000]

                final_prompt_text = f"Official Syllabus Context (PDF):\n{context_text}\n\nUser Prompt: {user_input if user_input else 'කරුණාකර ඇතුළත් කර ඇති පින්තූරයේ/ගොනුවේ ඇති ප්‍රශ්නවලට A/L Marking Scheme එකට අනුව නිවැරදි උත්තර ලබාදෙන්න.'}"

                # 3. Image ද නැතහොත් Text විතරද යන්න මත Model එක තේරීම
                if uploaded_file and uploaded_file.type.startswith("image/"):
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
                        model_name = "openrouter/deepseek/deepseek-chat"
                    else:
                        model_name = "groq/llama-3.3-70b-versatile"

                # LiteLLM API Call
                response = completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
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
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න හෝ පින්තූරයක් Upload කරන්න.")
