import faiss_sumpy as fs
import streamlit as st
import os
from PyPDF2 import PdfReader
import tiktoken
import textwrap
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')

async def summarize_PDF_file(pdf_file, model):

    text_summaries = []

    if (pdf_file is not None):
        st.write("PDF 문서를 요약 중입니다. 잠시만 기다려 주세요.")
        # reader = await fs.data_load()
        if model == "hf":
            page_text = fs.data_load(pdf_file)
            text_summary = fs.summarize(page_text)
            text_summaries.append(text_summary)
        else:
            print("구현중")
    else:
        st.write("PDF 파일를 업로드하세요.")

    st.write(text_summaries) # <-- text_summaries

            

# ------------- 사이드바 화면 구성 -----------------------
st.sidebar.title('Menu')

# ------------- 메인 화면 구성 --------------------------  
st.title('PaperTrendTech')

st.header("요약 모델 설정 ")

st.write("요약 모델을 선택하세요.")

radio_selected_model = st.radio("PDF 문서 요약 모델", ["OpenAI","HuggingFace"], index=1, horizontal=True)

upload_file = st.file_uploader("PDF 파일를 업로드하세요.", type="pdf")

if radio_selected_model == "HuggingFace":
    model = "hf"
else:
    st.write("OpenAI 구상 중")

clicked_sum_model = st.button('PDF 문서 요약')