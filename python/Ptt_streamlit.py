import faiss_sumpy as fs
import streamlit as st
import os
import tiktoken
import warnings
import requests
from dotenv import load_dotenv
import textract
import re
import tempfile
from ocr_summarizer import summarize_paragraph
import concurrent.futures

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')

FASTAPI_URL1 = os.getenv('FASTAPI_URL1')
FASTAPI_URL2 = os.getenv('FASTAPI_URL2')
FASTAPI_URL3 = os.getenv('FASTAPI_URL3')

def merge_short_paragraphs(paragraphs, min_length):
    merged_paragraphs = []
    current_paragraph = ""

    for paragraph in paragraphs:
        if len(paragraph.strip()) < min_length:
            current_paragraph += " " + paragraph.strip()
        else:
            if current_paragraph:
                merged_paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
            merged_paragraphs.append(paragraph.strip())
    
    if current_paragraph:
        merged_paragraphs.append(current_paragraph.strip())

    return merged_paragraphs

def split_long_paragraphs(paragraphs, max_length=1400):
    split_paragraphs = []
    
    for paragraph in paragraphs:
        if len(paragraph) <= max_length:
            split_paragraphs.append(paragraph)
        else:
            words = paragraph.split()
            current_chunk = ""
            
            for word in words:
                if len(current_chunk) + len(word) + 1 <= max_length:  # +1 for the space
                    current_chunk += " " + word
                else:
                    split_paragraphs.append(current_chunk.strip())
                    current_chunk = word
            
            if current_chunk:
                split_paragraphs.append(current_chunk.strip())
    
    return split_paragraphs

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
            # text = texts.decode('utf-8')
            # 2 개 이상의 연속된 공백 문자를 단락 구분자로 사용하여 텍스트를 단락으로 분할
            paragraphs = re.split(r'\n\n', texts)

            # 짧은 단락들을 전 단락과 병합
            merged_paragraphs = merge_short_paragraphs(paragraphs, 500)

            # 긴 단락들을 문장 단위로 분할
            split_paragraphs = split_long_paragraphs(merged_paragraphs)

            # 짧은 단락들을 전 단락과 병합
            merged_paragraphs = merge_short_paragraphs(split_paragraphs, 500)
            
            # 첫 7개 단락만 출력
            paragraphs_to_summarize = merged_paragraphs[:10]
            
            # 결과 출력
            st.write("단락별 텍스트:")
            for i, paragraph in enumerate(paragraphs_to_summarize):
                st.write(f"단락 {i+1}:")
                st.write(paragraph)
                st.write("---")

            summaries = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(summarize_paragraph, paragraph): i for i, paragraph in enumerate(paragraphs_to_summarize)}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        summary = future.result()
                        summaries.append(summary)
                        st.write(f"요약된 단락 {len(summaries)}:")
                        st.write(summary)
                        st.write("---")
                    except Exception as e:
                        st.write(f"Error during summarization: {e}")
        if model == "hf":
            print("HuggingFace 구상 중")
            # documents = fs.data_load(texts)
            # text_summary = fs.summarize(documents)
            # st.write("요약 텍스트: ", text_summary)
        else:
            print("구현중")
    else:
        st.write("PDF 파일를 업로드하세요.")

    # st.write(text_summary)

            

# ------------- 사이드바 화면 구성 -----------------------
st.sidebar.title('Menu')

# ------------- 메인 화면 구성 --------------------------  
st.title('Paragraph Extraction and Summarization from PDF')

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