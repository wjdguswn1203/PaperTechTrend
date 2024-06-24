import warnings
import numpy as np
import faiss
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')

# 요약 모델 및 임베딩 모델 초기화
summarization_pipe = pipeline("summarization", model="facebook/bart-large-cnn")
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def summarize_paragraph(paragraph):
    try:
        summary = summarization_pipe(paragraph, max_length=150, min_length=30, do_sample=False)
        summary_text = summary[0]['summary_text'] if summary else paragraph
        print(f"Summary: {summary_text}\n")
        return summary_text
    except Exception as e:
        print(f"Error summarizing paragraph: {e}")
        return paragraph

def summarize(paragraphs):
    summaries = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(summarize_paragraph, paragraph) for paragraph in paragraphs]
        for future in futures:
            summaries.append(future.result())
    return summaries