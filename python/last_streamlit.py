import streamlit as st
import os
import tiktoken
import warnings
import requests
import textract
import re
import tempfile
from langchain.text_splitter import CharacterTextSplitter
import concurrent.futures

warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')

FASTAPI_URL1 = os.getenv('FASTAPI_URL1')
FASTAPI_URL2 = os.getenv('FASTAPI_URL2')
FASTAPI_URL3 = os.getenv('FASTAPI_URL3')

def summarize_PDF_file(pdf_file, model, input_title):

    if (pdf_file is not None):

        st.write("PDF 문서를 요약 중입니다. 잠시만 기다려 주세요.")

        # PDF 파일을 바이트 스트림으로 읽기
        file_bytes = pdf_file.read()
        url = f"{FASTAPI_URL3}/upload"
        headers = {"Content-Type": "application/pdf", "titles": input_title}
        response = requests.post(url, data=file_bytes, headers=headers)
        print("pdf sended")

        if response.status_code == 200:
            texts = response.json().get("texts", "")
            st.write("파일이 성공적으로 전송되었습니다.")

            # 스플리터 지정
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                separator="\\n\\n",  # 분할 기준
                chunk_size=2000,   # 청크 사이즈
                chunk_overlap=100, # 중첩 사이즈
            )

            split_texts = text_splitter.split_text(texts)
            st.write(len(split_texts), "단락이 있음.")
            
            # # 결과 출력
            # st.write("단락별 텍스트:")
            # for i, paragraph in enumerate(split_texts):
            #     st.write(f"단락 {i+1}:")
            #     st.write(paragraph)
            #     st.write("---")
        if model == "bart":
            url2 = f"{FASTAPI_URL2}/summarize"
            headers2 = {"Content-Type": "application/json", "titles": input_title}
            summaries = requests.post(url2, json={"title": input_title,"texts": split_texts}, headers=headers2)
            sum_list = summaries.json().get("data", "")
            st.write("요약된 단락:")
            for i, summary in enumerate(sum_list):
                st.write(f"{summary}")
                st.write("---")
        elif model == "flan":
            print("구현중")
    else:
        st.write("PDF 파일를 업로드하세요.")
            

# ------------- 사이드바 화면 구성 -----------------------
with st.sidebar:
    st.title('Summarization')
    sum_model = ["flan-t5-3b-summarizer","bart-large-cnn", "의미론적 방법론"]
    selected_sum_model = st.selectbox("Please select the PDF summary model.", sum_model)

    if selected_sum_model == "flan-t5-3b-summarizer":
        st.caption('https://huggingface.co/jordiclive/flan-t5-3b-summarizer')
        st.caption('bart-large-cnn 허깅페이스 모델을 사용하여 텍스트 요약을 수행합니다. \
                   이 모델의 차이점은 모델의 크기가 500MB로 적은 disk로도 요약이 가능합니다. \
                   그러나 모델의 크기가 작은만큼 AI 학습이 효과가 다른 모델에 비해 떨어질 수 있습니다.')

    elif selected_sum_model == "bart-large-cnn":
        st.caption('https://huggingface.co/facebook/bart-large-cnn \
                   bart-large-cnn 허깅페이스 모델을 사용하여 텍스트 요약을 수행합니다. \
                   이 모델의 차이점은 모델의 크기가 500MB로 적은 disk로도 요약이 가능합니다. \
                   그러나 모델의 크기가 작은만큼 AI 학습이 효과가 다른 모델에 비해 떨어질 수 있습니다.')

    elif selected_sum_model == "의미론적 방법론":
        st.header('Summary with 의미론적 방법론')

    chart = ["All", "Time", "Accuracy"]
    selected_chart = st.selectbox("Please select the chart.", chart)

    st.markdown("---")

    st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" \
            alt="Streamlit logo" height="16">&nbsp by',unsafe_allow_html=True)

    st.markdown(
            '<h6> \
            <a href="https://github.com/raminicano">@raminicano</a> \
            <a href="https://github.com/sinzng">@sinzng</a> \
            <a href="https://github.com/wjdguswn1203">@wjdguswn1203</a> \
            <a href="https://github.com/chang558">@chang558</a> \
            </h6>',
            unsafe_allow_html=True,
        )

    st.markdown('<h5></h5>', unsafe_allow_html=True)



# ------------- 메인 화면 구성 --------------------------  

if selected_sum_model == "flan-t5-3b-summarizer":
    st.header('Summary with flan-t5-3b-summarizer')
    model = "flan"
elif selected_sum_model == "bart-large-cnn":
    st.header('Summary with bart-large-cnn')
    model = "bart"
elif selected_sum_model == "의미론적 방법론":
    st.header('Summary with 의미론적 방법론')
    model = "bart"

input_title = st.text_input("논문의 제목을 입력하세요.")

upload_file = st.file_uploader("PDF 파일를 업로드하세요.", type="pdf")

# 컬럼을 사용하여 버튼을 오른쪽에 배치
col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
with col3:
    clicked_sum_model = st.button('PDF 문서 요약')

if clicked_sum_model:
    summarize_PDF_file(upload_file, model, input_title)
