import streamlit as st
from litellm import completion
from duckduckgo_search import DDGS
import os

# 1. Streamlit Secrets හරහා Groq API Key එක ලබා ගැනීම
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# UI එක සකස් කිරීම
st.set_page_config(page_title="A/L Tech AI Guru", page_icon="🎓")
st.title("🎓 A/L Technology AI Guru (Live Web Search සමඟ) 🧠")
st.write("උසස් පෙළ **තාක්ෂණවේදය (Technology)** විෂය ධාරාවට අදාළ ඕනෑම ප්‍රශ්නයක් අහන්න:")

user_input = st.text_input("ඔබේ විෂය කරුණ / ප්‍රශ්නය ඇතුළත් කරන්න:", placeholder="උදා: SFT වල මාන (Dimensions) යනු කුමක්ද?")

# A/L Tech Syllabus එකට විතරක් සීමා කළ System Prompt එක
system_prompt = """
You are an expert tutor for the Sri Lankan G.C.E. Advanced Level (A/L) Technology Stream (ශ්‍රී ලංකාවේ A/L තාක්ෂණවේදය විෂය ධාරාව).

Your rules:
1. ONLY answer questions related to the Sri Lankan A/L Technology stream subjects:
   - Science for Technology (SFT / තාක්ෂණවේදය සඳහා විද්‍යාව)
   - Engineering Technology (ET / ඉංජිනේරු තාක්ෂණවේදය)
   - Biosystems Technology (BST / ජෛව පද්ධති තාක්ෂණවේදය)
   - Information and Communication Technology (ICT / තොරතුරු හා සන්නිවේදන තාක්ෂණය)

2. ALWAYS respond in clear, natural, and friendly Sinhala language suited for an A/L student. Use bullet points and simple terms where necessary.

3. Use the provided live web search context to make your answers up-to-date and highly accurate.

4. If the user asks ANYTHING outside the Sri Lankan A/L Technology stream (e.g., General knowledge, Maths, Bio, Arts, Commerce, cooking, movies, or general technology not in syllabus), politely refuse in Sinhala by saying:
   "කණගාටුයි, මට පිළිතුරු දිය හැක්කේ ශ්‍රී ලංකාවේ උසස් පෙළ (A/L) තාක්ෂණවේදය (Technology) විෂය ධාරාවට (SFT, ET, BST, ICT) අදාළ ප්‍රශ්න වලට පමණයි."
"""

# Web Search කිරීම සඳහා වන Function එක (කිසිම API Key එකක් නොමැතිව)
def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        search_text = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return search_text
    except Exception:
        return "අන්තර්ජාල සෙවුම් තොරතුරු ලබාගැනීමට නොහැකි විය."

if st.button("පිළිතුර ලබාගන්න"):
    if user_input:
        with st.spinner("අන්තර්ජාලයෙන් තොරතුරු සොයමින් Syllabus එකට අනුව පිළිතුර සකසයි..."):
            try:
                # 1. අන්තර්ජාලයෙන් තොරතුරු සෙවීම
                web_context = search_web(user_input)
                
                # 2. ප්‍රශ්නය සහ සොයාගත් තොරතුරු AI එකට යැවීම
                full_user_prompt = f"User Question: {user_input}\n\nLive Search Context from Web:\n{web_context}"

                response = completion(
                    model="groq/llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_user_prompt}
                    ]
                )
                st.success("පිළිතුර:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"දෝෂයක් ඇති විය: {e}")
    else:
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
