import os
import tempfile
import streamlit as st
import docx
from PyPDF2 import PdfReader
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

# ======================
# Config
# ======================
load_dotenv()
MODEL_NAME = "llama-3.3-70b"
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

def ask_cerebras(prompt: str) -> str:
    try:
        response = client.completions.create(
            model=MODEL_NAME,
            prompt=prompt,
            max_tokens=1500,
            temperature=0.4
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# ======================
# Streamlit UI
# ======================
st.set_page_config(page_title="📝 AI Resume Analyzer", layout="wide")

st.title("📝 AI Resume Analyzer")
st.write("Upload your resume and get instant AI-powered feedback (ATS score, strengths, improvements).")

uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    # Extract text
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_path)
    else:
        resume_text = extract_text_from_docx(file_path)

    st.success("✅ Resume uploaded and processed!")

    # Ask AI for analysis
    if st.button("Analyze Resume"):
        with st.spinner("Analyzing..."):
            prompt = f"""
            You are an expert recruiter and ATS system. Analyze the following resume text and provide:
            1. An ATS score (0–100) based on clarity, keywords, and formatting.
            2. Strengths of the resume.
            3. Weaknesses / missing elements.
            4. Specific suggestions to improve the resume.

            Resume:
            {resume_text}
            """

            result = ask_cerebras(prompt)

        st.markdown("### 📊 Resume Analysis")
        st.write(result)

        with st.expander("📄 Extracted Resume Text"):
            st.write(resume_text)

