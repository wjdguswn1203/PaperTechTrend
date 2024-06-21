import streamlit as st
import textract
import re
import tempfile
from ocr_summarizer import summarize_paragraph
import concurrent.futures

st.title('Paragraph Extraction and Summarization from PDF')

# PDF 파일 업로드
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

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

if uploaded_file is not None:
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    # PDF 파일의 내용을 텍스트로 추출
    text = textract.process(temp_file_path)
    text = text.decode('utf-8')  # 바이트 문자열을 유니코드 문자열로 변환

    # 세 개 이상의 연속된 공백 문자를 단락 구분자로 사용하여 텍스트를 단락으로 분할
    paragraphs = re.split(r'\s{2,}', text)

    # 짧은 단락들을 전 단락과 병합
    merged_paragraphs = merge_short_paragraphs(paragraphs, 500)

    # 긴 단락들을 문장 단위로 분할
    split_paragraphs = split_long_paragraphs(merged_paragraphs)

    # 짧은 단락들을 전 단락과 병합
    merged_paragraphs = merge_short_paragraphs(paragraphs, 500)
    
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

    # st.write("요약 텍스트:")
    # for i, summary in enumerate(summaries):
    #     st.write(f"단락 {i+1} 요약:")
    #     st.write(summary)
    #     st.write("---")
