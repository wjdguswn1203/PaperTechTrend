import faiss_sumpy as fs
import streamlit as st
import os
import tiktoken
import textwrap
import warnings
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')

FASTAPI_URL1 = os.getenv('FASTAPI_URL1')
FASTAPI_URL2 = os.getenv('FASTAPI_URL2')
FASTAPI_URL3 = os.getenv('FASTAPI_URL3')

def summarize_PDF_file(pdf_file, model):

    text_summaries = []

    if (pdf_file is not None):
        st.write("PDF 문서를 요약 중입니다. 잠시만 기다려 주세요.")
        # PDF 파일을 바이트 스트림으로 읽기
        file_bytes = pdf_file.read()
        url = f"{FASTAPI_URL3}/upload"
        headers = {"Content-Type": "application/pdf"}
        response = requests.post(url, data=file_bytes, headers=headers)
        print("pdf sended")
        if response.status_code == 200:
            texts = response.json().get("text", "")
            st.write("파일이 성공적으로 전송되었습니다.")
        if model == "hf":
            documents = fs.data_load(texts)
            text_summary = fs.summarize(documents)
            st.write("요약 텍스트: ", text_summary)
        else:
            print("구현중")
    else:
        st.write("PDF 파일를 업로드하세요.")

    # st.write(text_summary)

            

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

if clicked_sum_model:
    summarize_PDF_file(upload_file, model)