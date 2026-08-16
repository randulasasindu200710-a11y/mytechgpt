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
# 1. PDF කියවා පිටු වශයෙන් ගබඩා කිරීම (Smart Chunking)
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
                # හිස් පිටු මඟ හැරීම
                if text and len(text.strip()) > 50:
                    pages_data.append(text)
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
            
    return pages_data

# App එක පටන් ගනිද්දීම PDF වල පිටු මතකයේ තබාගනී
pdf_pages = load_pdf_pages()

st.title("🎓 TECH gpt - A/L Tech AI Guru 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (ET / SFT / BST / ICT)** විෂයයන්ට අදාළ ඕනෑම ප්‍රශ්නයක් අසන්න:")

with st.form(key="chat_form"):
    user_input = st.text_input("ඔබේ ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="ඔබේ ප්‍රශ්නය මෙහි ටයිප් කරන්න...")
    submit_button = st.form_submit_button(label="පිළිතුර ලබාගන්න")

# ---------------------------------------------------------
# 2. Universal System Prompt (ස්ථිර නීති මාලාව)
# ---------------------------------------------------------
system_prompt = """
You are an expert Sri Lankan G.C.E. A/L Technology stream (ET, SFT, BST, ICT) Master Teacher.

CREATOR IDENTITY RULE:
- If asked who made/created you, reply ONLY: "මාව නිර්මාණය කළේ Randula Sasindu විසිනි."

UNIVERSAL ANSWERING LOGIC (PDF FIRST, AI SECOND):
1. First, deeply analyze the "Official Syllabus Context (PDF)" provided below the user's prompt.
2. If the answer to the user's question can be found in that PDF context, formulate your answer STRICTLY based on those facts. Maintain exact definitions and structures as found in the PDF.
3. If the answer is NOT found in the provided PDF context, DO NOT REFUSE. Instead, fall back to your own expert AI knowledge regarding the Sri Lankan A/L Technology syllabus (ET, SFT, BST, ICT) and provide a highly accurate, syllabus-aligned answer.
4. Refuse ONLY if the user asks something completely outside the Tech Stream domain (e.g., movies, gossip, arts, general life advice). Refusal message: "කණගාටුයි! මට පිළිතුරු දිය හැක්කේ උසස් පෙළ තාක්ෂණවේදය (ET, SFT, BST, ICT) විෂයයන්ට අදාළ ප්‍රශ්න සඳහා පමණයි."

FORMATTING RULES:
- Write in accurate examination-standard Sinhala (සිංහල).
- Always use Markdown Tables (| Column 1 | Column 2 |) when presenting components, differences, lists (like 5M/5S), or source/use pairs.
- Use clear bullet points for explanations. DO NOT output massive unreadable paragraphs.
- Do NOT output raw LaTeX like [ F = k... ]. Format math beautifully using standard text.
"""

if submit_button:
    if user_input:
        with st.spinner("සටහන් විශ්ලේෂණය කර පිළිතුර සකසමින් පවතී..."):
            try:
                # ---------------------------------------------------------
                # 3. Smart Keyword Filtering (අදාළ පිටු පමණක් සෙවීම)
                # ---------------------------------------------------------
                # ප්‍රශ්නයේ ඇති අකුරු 2කට වඩා වැඩි වචන වෙන් කරගැනීම
                query_words = [w for w in user_input.split() if len(w) > 2]
                relevant_pages = []
                
                # ප්‍රශ්නයේ වචන ඇති පිටු පමණක් තෝරා ගැනීම
                for page in pdf_pages:
                    if any(word.lower() in page.lower() for word in query_words):
                        relevant_pages.append(page)
                
                # අදාළ පිටු එකතු කිරීම (උපරිමය අකුරු 30000කට සීමා කර ඇත - Multiple PDFs සඳහා)
                if relevant_pages:
                    context_text = "\n\n---\n\n".join(relevant_pages)[:30000]
                else:
                    # ගැලපෙන වචන නැත්නම් සාමාන්‍ය පරිදි මුල් පිටු ලබාදීම
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
